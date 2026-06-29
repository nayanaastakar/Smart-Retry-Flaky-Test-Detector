"""
Login Test Module for Saucedemo

This module contains test cases for login functionality including:
- Successful login
- Locked out user (intentional failure)
- Performance glitch user (intentional flaky scenario)
- Invalid credentials
"""

import pytest
import time
from selenium.common.exceptions import TimeoutException

from core.driver import get_driver_manager
from core.logger import get_logger
from core.retry_engine import execute_test_with_retry
from core.screenshot import capture_on_failure
from core.console_logs import capture_console_logs
from pages.login_page import LoginPage
from config.config import Config


class TestLogin:
    """
    Test class for login functionality.
    
    Tests include normal login, failure scenarios, and flaky test detection.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Setup and teardown for each test.
        
        Initializes driver manager and navigates to login page.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("TestLogin")
        self.config = Config()
        self.login_page = LoginPage()
        
        # Navigate to login page
        self.login_page.navigate_to_login_page(self.config.SAUCE_DEMO_URL)
        
        yield
        
        # Cleanup
        self.driver_manager.quit_driver()
    
    def test_successful_login(self):
        """
        Test successful login with valid credentials.
        
        This test should pass on first attempt.
        """
        def _test_login():
            self.login_page.login_with_standard_user()
            assert self.login_page.is_login_successful(), "Login should be successful"
        
        result = execute_test_with_retry(
            _test_login,
            "test_successful_login",
            max_retries=3,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_locked_out_user(self):
        """
        Test login with locked out user (intentional failure).
        
        This test should fail consistently and be classified as a genuine failure.
        """
        def _test_locked_login():
            self.login_page.login_with_locked_user()
            # This should fail - locked out user cannot login
            assert self.login_page.is_login_successful(), "Locked out user should not be able to login"
        
        result = execute_test_with_retry(
            _test_locked_login,
            "test_locked_out_user",
            max_retries=2,
            retry_delay=1.0
        )
        
        # Capture screenshot and logs on failure
        if result.status.value == "FAILURE":
            driver = self.driver_manager.get_driver()
            capture_on_failure(driver, "test_locked_out_user")
            capture_console_logs(driver, "test_locked_out_user")
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "FAILURE", "Test should fail for locked out user"
    
    def test_performance_glitch_user(self):
        """
        Test login with performance glitch user (intentional flaky scenario).
        
        This test may fail on first attempt due to performance issues but should pass on retry.
        This simulates a flaky test scenario.
        """
        def _test_glitch_login():
            # Add a small delay to simulate performance issues
            time.sleep(0.5)
            self.login_page.login_with_performance_glitch_user()
            assert self.login_page.is_login_successful(), "Performance glitch user should eventually login"
        
        result = execute_test_with_retry(
            _test_glitch_login,
            "test_performance_glitch_user",
            max_retries=3,
            retry_delay=2.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        # This test might be flaky - could be PASS or FLAKY
        assert result.status.value in ["PASS", "FLAKY"], "Test should pass or be flaky"
    
    def test_invalid_credentials(self):
        """
        Test login with invalid credentials.
        
        This test should fail consistently.
        """
        def _test_invalid_login():
            self.login_page.login("invalid_user", "invalid_password")
            assert self.login_page.is_login_successful(), "Invalid credentials should not login"
        
        result = execute_test_with_retry(
            _test_invalid_login,
            "test_invalid_credentials",
            max_retries=2,
            retry_delay=1.0
        )
        
        # Capture screenshot and logs on failure
        if result.status.value == "FAILURE":
            driver = self.driver_manager.get_driver()
            capture_on_failure(driver, "test_invalid_credentials")
            capture_console_logs(driver, "test_invalid_credentials")
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "FAILURE", "Test should fail for invalid credentials"
    
    def test_empty_credentials(self):
        """
        Test login with empty credentials.
        
        This test should fail consistently.
        """
        def _test_empty_login():
            self.login_page.login("", "")
            assert self.login_page.is_login_successful(), "Empty credentials should not login"
        
        result = execute_test_with_retry(
            _test_empty_login,
            "test_empty_credentials",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "FAILURE", "Test should fail for empty credentials"
    
    def test_page_load_verification(self):
        """
        Test that login page loads correctly.
        
        This test should pass on first attempt.
        """
        def _test_page_load():
            assert self.login_page.is_page_loaded(), "Login page should be loaded"
            assert "Swag Labs" in self.login_page.get_page_title(), "Page title should be correct"
        
        result = execute_test_with_retry(
            _test_page_load,
            "test_page_load_verification",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
