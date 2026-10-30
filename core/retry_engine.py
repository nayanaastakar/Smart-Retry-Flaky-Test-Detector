"""
core/retry_engine.py
=====================
The Smart Retry Engine.

Wraps arbitrary test callables (Selenium-driven PyTest tests, in practice)
with configurable retry-with-backoff behaviour, records every attempt to the
database, and reports whether the eventual result was a clean pass, a
"retry save" (failed once/more, then passed), or a hard failure.

Design notes
------------
- Retry policy is intentionally decoupled from *how* a test runs. This engine
  does not know about Selenium; it is handed a zero-arg callable and a
  context object, and it does not care what's inside.
- Every attempt (not just the final result) is persisted to `retry_attempts`
  so the dashboard can show real retry statistics, not just pass/fail totals.
- Backoff is exponential: delay * (multiplier ** attempt_index), which is
  more forgiving of load-related flakiness (server warming up, resource
  contention) than a fixed delay.
"""

from __future__ import annotations

import logging
import platform
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Optional

from config import settings
from database.db_manager import execute, fetch_one

logger = logging.getLogger("smart_retry.retry_engine")


class ExecutionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    FLAKY = "FLAKY"       # failed >=1 time then eventually passed within the retry budget
    RUNNING = "RUNNING"
    SKIPPED = "SKIPPED"


@dataclass
class AttemptResult:
    attempt_number: int
    status: ExecutionStatus
    duration_ms: int
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    exception_type: Optional[str] = None


@dataclass
class ExecutionResult:
    """Final, aggregated outcome of a (possibly retried) test execution."""

    run_id: str
    test_name: str
    module: str
    status: ExecutionStatus
    attempt_count: int
    max_retries: int
    retry_success: bool
    duration_ms: int
    attempts: list[AttemptResult] = field(default_factory=list)
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    stack_trace: Optional[str] = None
    execution_db_id: Optional[int] = None


class SmartRetryEngine:
    """Executes a test callable with retry-with-backoff, persisting history."""

    def __init__(
        self,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        backoff_multiplier: float | None = None,
    ) -> None:
        from services.settings_service import get_runtime_settings

        runtime = get_runtime_settings()
        self.max_retries = max_retries if max_retries is not None else runtime["retry_count"]
        self.retry_delay = retry_delay if retry_delay is not None else runtime["retry_delay"]
        self.backoff_multiplier = (
            backoff_multiplier if backoff_multiplier is not None else settings.RETRY_BACKOFF_MULTIPLIER
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(
        self,
        test_fn: Callable[[], None],
        test_name: str,
        module: str = "general",
        website_profile: str | None = None,
        browser: str = "chrome",
        os_name: str = "unknown",
        evidence_collector: Optional[Callable[[Exception | None], dict]] = None,
        on_event: Optional[Callable[[str, str], None]] = None,
    ) -> ExecutionResult:
        """
        Execute `test_fn` up to (1 + max_retries) times.

        `evidence_collector`, if provided, is called after every attempt with
        the exception (or None on success) and must return a dict that may
        contain: screenshot_path, console_logs, stack_trace override.
        """
        run_id = uuid.uuid4().hex[:12]
        if not os_name or os_name == "unknown":
            os_name = f"{platform.system()} {platform.release()}"
        attempts: list[AttemptResult] = []
        overall_start = time.perf_counter()

        last_exception: Exception | None = None
        final_status = ExecutionStatus.FAIL
        evidence: dict = {}

        # Create the execution row up-front (status RUNNING) so every retry
        # attempt has a real, non-null execution_id to attach to. This row
        # is updated in place once the final outcome is known, rather than
        # inserted fresh at the end.
        execution_db_id = execute(
            """INSERT INTO executions (run_id, test_name, module, website_profile, status,
               max_retries, browser, os_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, test_name, module, website_profile, ExecutionStatus.RUNNING.value,
             self.max_retries, browser, os_name),
        )

        for attempt_index in range(self.max_retries + 1):
            attempt_number = attempt_index + 1
            attempt_start = time.perf_counter()
            try:
                test_fn()
                duration_ms = int((time.perf_counter() - attempt_start) * 1000)
                attempts.append(
                    AttemptResult(attempt_number=attempt_number, status=ExecutionStatus.PASS, duration_ms=duration_ms)
                )
                self._record_attempt(execution_db_id, attempt_number, ExecutionStatus.PASS, duration_ms, None)
                final_status = ExecutionStatus.FLAKY if attempt_index > 0 else ExecutionStatus.PASS
                last_exception = None
                if evidence_collector:
                    evidence = evidence_collector(None) or {}
                break
            except Exception as exc:  # noqa: BLE001 - intentionally broad, this is a test harness
                duration_ms = int((time.perf_counter() - attempt_start) * 1000)
                last_exception = exc
                tb = traceback.format_exc()
                attempts.append(
                    AttemptResult(
                        attempt_number=attempt_number,
                        status=ExecutionStatus.FAIL,
                        duration_ms=duration_ms,
                        error_message=str(exc),
                        stack_trace=tb,
                        exception_type=type(exc).__name__,
                    )
                )
                self._record_attempt(execution_db_id, attempt_number, ExecutionStatus.FAIL, duration_ms, str(exc))
                if evidence_collector:
                    evidence = evidence_collector(exc) or {}

                logger.warning(
                    "Attempt %s/%s failed for %s: %s",
                    attempt_number,
                    self.max_retries + 1,
                    test_name,
                    exc,
                )

                if attempt_index < self.max_retries:
                    delay = self.retry_delay * (self.backoff_multiplier ** attempt_index)
                    if on_event:
                        on_event("warn", f"{test_name}: attempt {attempt_number} failed, retrying in {delay:.1f}s ({exc})")
                    time.sleep(delay)
                else:
                    final_status = ExecutionStatus.FAIL

        total_duration_ms = int((time.perf_counter() - overall_start) * 1000)
        retry_success = final_status == ExecutionStatus.FLAKY

        result = ExecutionResult(
            run_id=run_id,
            test_name=test_name,
            module=module,
            status=final_status,
            attempt_count=len(attempts),
            max_retries=self.max_retries,
            retry_success=retry_success,
            duration_ms=total_duration_ms,
            attempts=attempts,
            exception_type=type(last_exception).__name__ if last_exception else None,
            exception_message=str(last_exception) if last_exception else None,
            stack_trace=attempts[-1].stack_trace if (last_exception and attempts) else None,
        )

        result.execution_db_id = execution_db_id
        self._finalize_execution(execution_db_id, result, evidence)
        if on_event:
            level = {"PASS": "success", "FLAKY": "warn", "FAIL": "error"}.get(final_status.value, "info")
            on_event(level, f"{test_name}: {final_status.value} after {len(attempts)} attempt(s)")
        return result

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _record_attempt(
        execution_id: int, attempt_number: int, status: ExecutionStatus, duration_ms: int, error_message: str | None
    ) -> None:
        execute(
            """INSERT INTO retry_attempts (execution_id, attempt_number, status, duration_ms, error_message)
               VALUES (?, ?, ?, ?, ?)""",
            (execution_id, attempt_number, status.value, duration_ms, error_message),
        )

    @staticmethod
    def _finalize_execution(execution_id: int, result: ExecutionResult, evidence: dict) -> None:
        """Update the pre-created execution row with the final outcome."""
        execute(
            """UPDATE executions SET
                   status = ?, attempt_count = ?, retry_success = ?, duration_ms = ?,
                   exception_type = ?, exception_message = ?, stack_trace = ?,
                   console_logs = ?, screenshot_path = ?, finished_at = ?, browser_version = ?
               WHERE id = ?""",
            (
                result.status.value,
                result.attempt_count,
                int(result.retry_success),
                result.duration_ms,
                result.exception_type,
                result.exception_message,
                result.stack_trace,
                evidence.get("console_logs"),
                evidence.get("screenshot_path"),
                datetime.now(timezone.utc).isoformat(),
                evidence.get("browser_version"),
                execution_id,
            ),
        )


def retryable(
    test_name: str,
    module: str = "general",
    max_retries: int | None = None,
    website_profile: str | None = None,
):
    """Decorator form for PyTest test functions.

    Usage:
        @retryable(test_name="Login - Valid Credentials", module="login")
        def test_login(driver):
            ...
    """

    def decorator(fn: Callable[..., None]):
        def wrapper(*args, **kwargs):
            engine = SmartRetryEngine(max_retries=max_retries)
            return engine.run(
                lambda: fn(*args, **kwargs),
                test_name=test_name,
                module=module,
                website_profile=website_profile,
            )

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator
