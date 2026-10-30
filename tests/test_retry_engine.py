"""
tests/test_retry_engine.py
==========================
Unit and integration tests for the Smart Retry Engine.
"""

import pytest
from core.retry_engine import SmartRetryEngine, ExecutionStatus, retryable
from database.db_manager import init_db, fetch_all, fetch_one


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_clean_pass_on_first_attempt():
    engine = SmartRetryEngine(max_retries=2, retry_delay=0.0)
    call_count = 0

    def passing_test():
        nonlocal call_count
        call_count += 1

    result = engine.run(passing_test, test_name="test_clean_pass", module="test_unit")
    assert result.status == ExecutionStatus.PASS
    assert result.attempt_count == 1
    assert not result.retry_success
    assert call_count == 1

    # Check database persistence
    row = fetch_one("SELECT * FROM executions WHERE id = ?", (result.execution_db_id,))
    assert row is not None
    assert row["status"] == "PASS"
    assert row["attempt_count"] == 1


def test_retry_success_flaky():
    engine = SmartRetryEngine(max_retries=3, retry_delay=0.0)
    call_count = 0

    def flaky_test():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Intermittent transient network glitch")

    result = engine.run(flaky_test, test_name="test_flaky_retry", module="test_unit")
    assert result.status == ExecutionStatus.FLAKY
    assert result.attempt_count == 2
    assert result.retry_success is True
    assert call_count == 2

    # Verify attempts in retry_attempts table
    attempts = fetch_all("SELECT * FROM retry_attempts WHERE execution_id = ? ORDER BY attempt_number", (result.execution_db_id,))
    assert len(attempts) == 2
    assert attempts[0]["status"] == "FAIL"
    assert attempts[1]["status"] == "PASS"


def test_hard_failure_exceeding_max_retries():
    engine = SmartRetryEngine(max_retries=2, retry_delay=0.0)
    call_count = 0

    def failing_test():
        nonlocal call_count
        call_count += 1
        raise AssertionError("Element #target never showed up")

    result = engine.run(failing_test, test_name="test_hard_fail", module="test_unit")
    assert result.status == ExecutionStatus.FAIL
    assert result.attempt_count == 3  # 1 initial + 2 retries
    assert result.retry_success is False
    assert call_count == 3
    assert result.exception_type == "AssertionError"
    assert "Element #target" in result.exception_message

    attempts = fetch_all("SELECT * FROM retry_attempts WHERE execution_id = ?", (result.execution_db_id,))
    assert len(attempts) == 3
    assert all(a["status"] == "FAIL" for a in attempts)


def test_retryable_decorator():
    call_count = 0

    @retryable(test_name="test_decorated_fn", module="decorator_test", max_retries=2)
    def my_test_fn():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RuntimeError("Transient error")

    res = my_test_fn()
    assert res.status == ExecutionStatus.FLAKY
    assert res.attempt_count == 2
