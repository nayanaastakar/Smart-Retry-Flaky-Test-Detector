"""
test_login.py — Module 4 integration

Tests for the SauceDemo login page.  Integrates with:
  • Module 1 – Flask / ConfigLoader / Page Objects
  • Module 2 – RetryEngine
  • Module 3 – FlakyDetector
  • Module 4 – ScreenshotManager + BrowserLogManager + Evidence

Simulation flags
----------------
Set any of the ENV variables below to "1" to inject the corresponding
Selenium-style exception and verify that Module 4 evidence capture works
without a real browser failure:

    SIMULATE_TIMEOUT              – raises TimeoutException on attempt 1
    SIMULATE_ASSERTION            – raises AssertionError on attempt 1
    SIMULATE_CLICK_INTERCEPTED    – raises ElementClickInterceptedException

Example (PowerShell):
    $env:SIMULATE_TIMEOUT = "1"
    pytest tests/test_login.py -v
"""

import os
import time
import pytest

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

from core.config_loader import ConfigLoader
from core.screenshot_manager import ScreenshotManager
from core.browser_log_manager import BrowserLogManager
from ai.failure_analyzer import FailureAnalyzer
from models.evidence import Evidence
from pages.login_page import LoginPage

# ── simulation flags (read once at module load) ───────────────────────────────
_SIM_TIMEOUT = os.getenv("SIMULATE_TIMEOUT", "0") == "1"
_SIM_ASSERTION = os.getenv("SIMULATE_ASSERTION", "0") == "1"
_SIM_CLICK = os.getenv("SIMULATE_CLICK_INTERCEPTED", "0") == "1"


# ── helpers ───────────────────────────────────────────────────────────────────

def _collect_evidence(
    driver,
    test_name: str,
    status: str,
    start_time: float,
    attempts: int,
    exc: Exception = None,
) -> Evidence:
    """
    Capture screenshot + browser logs and return an Evidence object.
    Only called when status is FLAKY or FAILURE.
    """
    ss_mgr = ScreenshotManager()
    bl_mgr = BrowserLogManager()

    ss_path = ss_mgr.capture(driver, test_name)
    log_path = bl_mgr.save_logs(driver, test_name)

    elapsed = round(time.time() - start_time, 2)

    evidence = Evidence(
        test_name=test_name,
        status=status,
        screenshot=str(ss_path) if ss_path else "",
        log_file=str(log_path) if log_path else "",
        attempts=attempts,
        execution_time=f"{elapsed} sec",
        exception_type=type(exc).__name__ if exc else "",
        exception_msg=str(exc) if exc else "",
    )

    # Trigger Module 6 AI Analysis
    analyzer = FailureAnalyzer()
    ai_result = analyzer.analyze(evidence)
    evidence.ai_analysis = ai_result

    return evidence


# ── test class ────────────────────────────────────────────────────────────────

class TestLogin:
    """
    Login tests for SauceDemo.

    Each test follows the flow:
        Run → Retry → Flaky/Failure? → Capture Evidence → Assert
    """

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """Initialise page object and Module 4 managers once per test."""
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.ss_mgr = ScreenshotManager()
        self.bl_mgr = BrowserLogManager()

    # ── test 1: successful login ──────────────────────────────────────────────

    def test_successful_login(self):
        """
        Happy-path login with the standard_user credential.
        Screenshots captured at each step for the gallery.
        """
        print("\nRunning Login Test...")
        print("Attempt 1")
        start = time.time()
        self.login_page.navigate()

        # Screenshot 1: Login page loaded
        self.ss_mgr.capture(self.driver, "01_login_page")

        self.login_page.login_with_default_credentials()

        success = self.login_page.is_login_successful()

        # Screenshot 2: After login attempt (pass or fail)
        self.ss_mgr.capture(self.driver, "02_after_login")

        print("PASSED" if success else "FAILED")
        assert success, "Login failed with valid credentials"

    # ── test 2: invalid login (genuine failure) ───────────────────────────────

    def test_invalid_login(self):
        """
        Login with wrong credentials — expected to fail.
        Verifies that FAILURE evidence (screenshot + log) is captured.
        """
        print("\nRunning Login Test (Invalid Credentials)...")
        max_retries = 2
        last_exc: Exception = None
        start = time.time()

        for attempt in range(1, max_retries + 1):
            print(f"Attempt {attempt}")
            try:
                self.login_page.navigate()

                # Screenshot: Login page before invalid attempt
                self.ss_mgr.capture(self.driver, f"03_invalid_login_attempt_{attempt}")

                self.login_page.login("wrong_user", "wrong_pass")
                logged_in = self.login_page.is_login_successful()

                # Screenshot: Result page after invalid attempt
                self.ss_mgr.capture(self.driver, f"04_invalid_login_result_{attempt}")

                if not logged_in:
                    raise AssertionError("Login correctly rejected (invalid credentials)")
                print("PASSED (unexpected)")
                return
            except Exception as exc:
                last_exc = exc
                print("FAILED")
                if attempt < max_retries:
                    print("Retrying...")

        evidence = _collect_evidence(
            self.driver, "invalid_login", "FAILURE",
            start, max_retries, last_exc,
        )
        print(f"\nExecution Finished\n{evidence}")
        assert not self.login_page.is_login_successful(), \
            "Invalid credentials should not result in a successful login"

    # ── test 3: simulate timeout (FAILURE → evidence) ─────────────────────────

    @pytest.mark.skipif(not _SIM_TIMEOUT, reason="SIMULATE_TIMEOUT not set")
    def test_simulate_timeout(self):
        """
        Injects a TimeoutException on the first attempt to validate that
        Module 4 evidence capture works correctly.

        Enable with: $env:SIMULATE_TIMEOUT = "1"
        """
        print("\nRunning Login Test (Simulated Timeout)...")
        max_retries = 2
        last_exc: Exception = None
        start = time.time()

        for attempt in range(1, max_retries + 1):
            print(f"Attempt {attempt}")
            try:
                if attempt == 1:
                    raise TimeoutException("Simulated – element not found within timeout")
                # attempt 2+: proceed normally
                self.login_page.navigate()
                self.login_page.login_with_default_credentials()
                assert self.login_page.is_login_successful()
                print("PASSED")
                return  # FLAKY – passed on retry
            except Exception as exc:
                last_exc = exc
                print("FAILED")
                if attempt < max_retries:
                    print("Retrying...")

        # All retries exhausted → FAILURE evidence
        evidence = _collect_evidence(
            self.driver, "simulate_timeout", "FAILURE",
            start, max_retries, last_exc,
        )
        print(f"\nExecution Finished\n{evidence}")
        assert evidence.has_screenshot, "Screenshot should have been captured"
        assert evidence.has_log, "Browser log should have been captured"

    # ── test 4: simulate assertion error (FLAKY → evidence) ──────────────────

    @pytest.mark.skipif(not _SIM_ASSERTION, reason="SIMULATE_ASSERTION not set")
    def test_simulate_assertion(self):
        """
        Injects an AssertionError on the first attempt, then succeeds —
        simulating a FLAKY test so evidence capture is triggered.

        Enable with: $env:SIMULATE_ASSERTION = "1"
        """
        print("\nRunning Login Test (Simulated Assertion)...")
        max_retries = 2
        last_exc: Exception = None
        start = time.time()

        for attempt in range(1, max_retries + 1):
            print(f"Attempt {attempt}")
            try:
                if attempt == 1:
                    raise AssertionError("Simulated – inventory page not loaded yet")
                self.login_page.navigate()
                self.login_page.login_with_default_credentials()
                assert self.login_page.is_login_successful()
                print("PASSED")

                # Flaky: passed after retry → collect evidence
                evidence = _collect_evidence(
                    self.driver, "simulate_assertion", "FLAKY",
                    start, attempt, last_exc,
                )
                print(f"\nExecution Finished\n{evidence}")
                assert evidence.has_screenshot, "Screenshot should have been captured"
                assert evidence.has_log, "Browser log should have been captured"
                return
            except Exception as exc:
                last_exc = exc
                print("FAILED")
                if attempt < max_retries:
                    print("Retrying...")

    # ── test 5: simulate click-intercepted ────────────────────────────────────

    @pytest.mark.skipif(not _SIM_CLICK, reason="SIMULATE_CLICK_INTERCEPTED not set")
    def test_simulate_click_intercepted(self):
        """
        Simulates ElementClickInterceptedException across all retries,
        verifying FAILURE evidence is captured.

        Enable with: $env:SIMULATE_CLICK_INTERCEPTED = "1"
        """
        print("\nRunning Login Test (Simulated Click Intercepted)...")
        max_retries = 2
        last_exc: Exception = None
        start = time.time()

        for attempt in range(1, max_retries + 1):
            print(f"Attempt {attempt}")
            try:
                raise ElementClickInterceptedException("Simulated – overlay blocking button")
            except Exception as exc:
                last_exc = exc
                print("FAILED")
                if attempt < max_retries:
                    print("Retrying...")

        evidence = _collect_evidence(
            self.driver, "simulate_click_intercepted", "FAILURE",
            start, max_retries, last_exc,
        )
        print(f"\nExecution Finished\n{evidence}")
        assert evidence.has_screenshot, "Screenshot should have been captured"
        assert evidence.has_log, "Browser log should have been captured"
        assert evidence.exception_type == "ElementClickInterceptedException"
