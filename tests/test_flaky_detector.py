"""
tests/test_flaky_detector.py
============================
Tests for the Flaky Test Detection Engine.
"""

import pytest
from core.flaky_detector import FlakyDetector
from database.db_manager import init_db, execute


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_stable_classification_all_passes():
    test_name = "test_stable_flow"
    module = "test_mod"
    # Seed 5 consecutive passes
    for _ in range(5):
        execute(
            """INSERT INTO executions (run_id, test_name, module, status, attempt_count, retry_success)
               VALUES ('run1', ?, ?, 'PASS', 1, 0)""",
            (test_name, module),
        )

    detector = FlakyDetector(window_size=10, threshold_pct=20.0)
    report = detector.evaluate_test(test_name, module=module)
    assert report.classification == "STABLE"
    assert report.total_runs == 5
    assert report.pass_count == 5
    assert report.fail_count == 0
    assert report.flip_count == 0
    assert report.flaky_score == 0.0


def test_flaky_classification_alternating_flips():
    test_name = "test_flip_flop"
    module = "test_mod"
    # Seed alternating PASS, FAIL, PASS, FAIL
    statuses = ["PASS", "FAIL", "PASS", "FAIL"]
    for s in statuses:
        execute(
            """INSERT INTO executions (run_id, test_name, module, status, attempt_count, retry_success)
               VALUES ('run1', ?, ?, ?, 1, 0)""",
            (test_name, module, s),
        )

    detector = FlakyDetector(window_size=10, threshold_pct=20.0)
    report = detector.evaluate_test(test_name, module=module)
    assert report.classification == "FLAKY"
    assert report.flip_count == 3
    assert report.flaky_score > 50.0


def test_chronic_failure_classification():
    test_name = "test_chronic_failure"
    module = "test_mod"
    # 4 consecutive failures
    for _ in range(4):
        execute(
            """INSERT INTO executions (run_id, test_name, module, status, attempt_count, retry_success)
               VALUES ('run1', ?, ?, 'FAIL', 3, 0)""",
            (test_name, module),
        )

    detector = FlakyDetector(window_size=10, threshold_pct=20.0)
    report = detector.evaluate_test(test_name, module=module)
    assert report.classification == "CHRONIC_FAILURE"
    assert report.fail_count == 4
    assert report.pass_count == 0


def test_retry_save_elevates_flaky_score():
    test_name = "test_retry_saved_test"
    module = "test_mod"
    # Passed, but needed a retry (FLAKY status, retry_success=1)
    for _ in range(5):
        execute(
            """INSERT INTO executions (run_id, test_name, module, status, attempt_count, retry_success)
               VALUES ('run1', ?, ?, 'FLAKY', 2, 1)""",
            (test_name, module),
        )

    detector = FlakyDetector(window_size=10, threshold_pct=20.0)
    report = detector.evaluate_test(test_name, module=module)
    assert report.classification == "FLAKY"
    assert report.flaky_score == 30.0  # 30% from retry saves
