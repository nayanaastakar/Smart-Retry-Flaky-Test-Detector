"""
core/evidence_collector.py
===========================
Captures forensic evidence for a test attempt: screenshot, browser console
logs, stack trace, browser version, OS details, and timestamp. Everything is
written to disk under /screenshots and /logs, organized by run_id, so a
report can later embed or link to it.
"""

from __future__ import annotations

import json
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import settings


class EvidenceCollector:
    """Wraps a Selenium `driver` instance to capture evidence on demand.

    This class is deliberately defensive: if the driver is None (e.g. unit
    tests, or a non-UI test) it degrades gracefully instead of raising.
    """

    def __init__(self, driver: Any | None, run_id: str, test_name: str) -> None:
        self.driver = driver
        self.run_id = run_id
        self.test_name = test_name
        self.safe_name = "".join(c if c.isalnum() else "_" for c in test_name)[:60]
        self.safe_run_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(run_id))[:60]

    def capture(self, exception: Optional[Exception] = None, attempt_number: int = 1) -> dict:
        """Capture all available evidence and return a dict of results."""
        evidence: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "os_name": f"{platform.system()} {platform.release()}",
            "python_version": platform.python_version(),
        }

        evidence["screenshot_path"] = self._capture_screenshot(attempt_number)
        evidence["console_logs"] = self._capture_console_logs()
        evidence["browser_version"] = self._capture_browser_version()

        if exception is not None:
            evidence["stack_trace"] = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )
            evidence["exception_type"] = type(exception).__name__
            evidence["exception_message"] = str(exception)

        return evidence

    # ------------------------------------------------------------------ #
    def _capture_screenshot(self, attempt_number: int) -> Optional[str]:
        if self.driver is None:
            return None
        try:
            folder = settings.SCREENSHOTS_DIR / self.safe_run_id
            folder.mkdir(parents=True, exist_ok=True)
            filename = f"{self.safe_name}_attempt{attempt_number}.png"
            path = folder / filename
            self.driver.save_screenshot(str(path))
            return str(path.relative_to(settings.BASE_DIR))
        except Exception:
            return None

    def _capture_console_logs(self) -> Optional[str]:
        if self.driver is None:
            return None
        try:
            logs = self.driver.get_log("browser")
            folder = settings.LOGS_DIR / self.safe_run_id
            folder.mkdir(parents=True, exist_ok=True)
            log_path = folder / f"{self.safe_name}_console.json"
            log_path.write_text(json.dumps(logs, indent=2, default=str))
            return str(log_path.relative_to(settings.BASE_DIR))
        except Exception:
            return None

    def _capture_browser_version(self) -> Optional[str]:
        if self.driver is None:
            return None
        try:
            caps = getattr(self.driver, "capabilities", {})
            browser_name = caps.get("browserName", "unknown")
            browser_version = caps.get("browserVersion") or caps.get("version", "unknown")
            return f"{browser_name} {browser_version}"
        except Exception:
            return None
