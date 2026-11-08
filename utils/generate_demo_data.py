"""
utils/generate_demo_data.py
============================
Populates the database with realistic (simulated) execution history so the
dashboard, history, and flaky-detection views are meaningful immediately
after setup -- without requiring a live Selenium/browser run first.

This does NOT touch a real browser; it drives the SmartRetryEngine with fake
test callables that pass/fail according to a per-test probability profile,
which is exactly the kind of harness-level testing the retry engine is
built to support.

Run:  python -m utils.generate_demo_data
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from database.db_manager import execute, init_db
from database.seed import run_all as seed_all
from core.retry_engine import SmartRetryEngine
from core.flaky_detector import FlakyDetector

random.seed(42)

# (test_name, module, pass_probability) - lower probability => more failures/flakiness
TEST_PROFILES = [
    ("Login - Valid Credentials", "login", 0.95),
    ("Login - Invalid Password", "login", 0.97),
    ("Logout - Session Cleared", "login", 0.93),
    ("Search - Product Keyword", "search", 0.80),
    ("Add To Cart - Single Item", "cart", 0.65),   # flaky
    ("Add To Cart - Multiple Items", "cart", 0.60),  # flaky
    ("Checkout - Valid Payment", "checkout", 0.55),  # flaky
    ("Checkout - Empty Cart Blocked", "checkout", 0.92),
    ("Navigation - Menu Links", "navigation", 0.90),
    ("Product Verification - Details Page", "products", 0.88),
    ("Profile - Update Info", "profile", 0.30),      # chronic failure
    ("Negative - SQL Injection Attempt", "negative", 0.97),
]


class FakeException(Exception):
    pass


# Map each test to a realistic Selenium exception type for meaningful AI triage
_EXCEPTION_POOL = [
    ("TimeoutException", "TimeoutException: element not visible after 10s wait"),
    ("NoSuchElementException", "NoSuchElementException: locator did not match any elements"),
    ("ElementClickInterceptedException", "ElementClickInterceptedException: element not clickable at point"),
    ("StaleElementReferenceException", "StaleElementReferenceException: element is no longer attached to DOM"),
]


def _simulated_test(pass_probability: float, exc_index: int = 0):
    exc_type, exc_msg = _EXCEPTION_POOL[exc_index % len(_EXCEPTION_POOL)]

    def _run():
        if random.random() > pass_probability:
            raise FakeException(exc_msg)
    return _run, exc_type, exc_msg


def generate(num_runs_per_test: int = 15) -> None:
    init_db()
    seed_all()
    engine = SmartRetryEngine(max_retries=2, retry_delay=0.0)  # no real sleep for demo speed

    for idx, (test_name, module, prob) in enumerate(TEST_PROFILES):
        test_fn, exc_type, exc_msg = _simulated_test(prob, exc_index=idx)
        for i in range(num_runs_per_test):
            result = engine.run(
                test_fn,
                test_name=test_name,
                module=module,
                browser=random.choice(["chrome", "chrome", "firefox", "edge"]),
                os_name=random.choice(["Windows 11", "macOS 14", "Ubuntu 22.04"]),
            )
            # Store the realistic Selenium exception type on FAIL/FLAKY executions
            if result.status.value in ("FAIL", "FLAKY"):
                execute(
                    "UPDATE executions SET exception_type = ?, exception_message = ? WHERE id = ?",
                    (exc_type, exc_msg, result.execution_db_id),
                )
            # Backdate the execution timestamp so the trend charts have spread
            days_ago = random.randint(0, 13)
            backdated = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            execute(
                "UPDATE executions SET started_at = ? WHERE id = ?",
                (backdated, result.execution_db_id),
            )

    detector = FlakyDetector()
    reports = detector.evaluate_all()

    print(f"[demo-data] Generated {len(TEST_PROFILES) * num_runs_per_test} executions across {len(TEST_PROFILES)} tests.")
    for r in reports:
        if r.classification != "STABLE":
            print(f"  - {r.test_name}: {r.classification} (score {r.flaky_score})")


if __name__ == "__main__":
    generate()
