"""
Checkout Test Module for Saucedemo

This module contains test cases for checkout functionality including:
- Cart review
- Checkout information form
- Order completion
- Intentional flaky scenarios
"""

import pytest
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from core.driver import get_driver_manager
from core.logger import get_logger
from core.retry_engine import execute_test_with_retry
from core.screenshot import capture_on_failure
from core.console_logs import capture_console_logs
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.checkout_page import CheckoutPage
from config.config import Config


class TestCheckout:
    """
    Test class for checkout functionality.
    
    Tests include cart operations, checkout process, and flaky scenarios.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Setup and teardown for each test.
        
        Initializes driver manager, logs in, adds product to cart, and navigates to cart.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("TestCheckout")
        self.config = Config()
        self.login_page = LoginPage()
        self.search_page = SearchPage()
        self.checkout_page = CheckoutPage()
        
        # Navigate to login page and login
        self.login_page.navigate_to_login_page(self.config.SAUCE_DEMO_URL)
        self.login_page.login_with_standard_user()
        time.sleep(1)
        
        # Add a product to cart
        self.search_page.add_first_product_to_cart()
        time.sleep(1)
        
        # Navigate to cart
        self.search_page.click_cart_icon()
        time.sleep(1)
        
        yield
        
        # Cleanup
        self.driver_manager.quit_driver()
    
    def test_cart_page_load(self):
        """
        Test that cart page loads correctly.
        
        This test should pass on first attempt.
        """
        def _test_cart_load():
            assert self.checkout_page.is_cart_page_loaded(), "Cart page should be loaded"
            assert self.checkout_page.get_cart_item_count() > 0, "Cart should have items"
        
        result = execute_test_with_retry(
            _test_cart_load,
            "test_cart_page_load",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_get_cart_items(self):
        """
        Test retrieving items from cart.
        
        This test should pass on first attempt.
        """
        def _test_get_items():
            items = self.checkout_page.get_cart_items()
            assert len(items) > 0, "Cart should have items"
            assert all("name" in item and "price" in item for item in items), "Each item should have name and price"
        
        result = execute_test_with_retry(
            _test_get_items,
            "test_get_cart_items",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_click_checkout_button(self):
        """
        Test clicking checkout button to proceed to checkout.
        
        This test should pass on first attempt.
        """
        def _test_checkout_click():
            self.checkout_page.click_checkout_button()
            assert self.checkout_page.is_checkout_info_page_loaded(), "Checkout info page should load"
        
        result = execute_test_with_retry(
            _test_checkout_click,
            "test_click_checkout_button",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_fill_checkout_information(self):
        """
        Test filling checkout information form.
        
        This test should pass on first attempt.
        """
        def _test_fill_info():
            # First click checkout button
            self.checkout_page.click_checkout_button()
            time.sleep(0.5)
            
            # Fill information
            self.checkout_page.fill_checkout_information("John", "Doe", "12345")
            
            # Verify we can click continue
            self.checkout_page.click_continue_button()
            assert self.checkout_page.is_checkout_summary_page_loaded(), "Checkout summary should load"
        
        result = execute_test_with_retry(
            _test_fill_info,
            "test_fill_checkout_information",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_complete_checkout(self):
        """
        Test completing the entire checkout process.
        
        This test should pass on first attempt.
        """
        def _test_complete_checkout():
            success = self.checkout_page.complete_checkout("John", "Doe", "12345")
            assert success, "Checkout should complete successfully"
            assert self.checkout_page.is_checkout_complete_page_loaded(), "Complete page should load"
        
        result = execute_test_with_retry(
            _test_complete_checkout,
            "test_complete_checkout",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_get_order_summary(self):
        """
        Test getting order summary information.
        
        This test should pass on first attempt.
        """
        def _test_summary():
            # Navigate to checkout summary
            self.checkout_page.click_checkout_button()
            time.sleep(0.5)
            self.checkout_page.fill_checkout_information("John", "Doe", "12345")
            self.checkout_page.click_continue_button()
            time.sleep(0.5)
            
            # Get summary
            subtotal = self.checkout_page.get_subtotal()
            tax = self.checkout_page.get_tax()
            total = self.checkout_page.get_total()
            
            assert subtotal is not None, "Should have subtotal"
            assert tax is not None, "Should have tax"
            assert total is not None, "Should have total"
        
        result = execute_test_with_retry(
            _test_summary,
            "test_get_order_summary",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_empty_checkout_information(self):
        """
        Test checkout with empty information (intentional failure).
        
        This test should fail consistently.
        """
        def _test_empty_info():
            # Navigate to checkout info page
            self.checkout_page.click_checkout_button()
            time.sleep(0.5)
            
            # Try to continue without filling information
            self.checkout_page.click_continue_button()
            # This should fail - form validation should prevent continuation
            assert False, "Should not be able to continue without filling information"
        
        result = execute_test_with_retry(
            _test_empty_info,
            "test_empty_checkout_information",
            max_retries=2,
            retry_delay=1.0
        )
        
        # Capture screenshot and logs on failure
        if result.status.value == "FAILURE":
            driver = self.driver_manager.get_driver()
            capture_on_failure(driver, "test_empty_checkout_information")
            capture_console_logs(driver, "test_empty_checkout_information")
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "FAILURE", "Test should fail for empty information"
    
    def test_flaky_checkout_navigation(self):
        """
        Test with intentional flaky scenario - checkout navigation with timing issues.
        
        This test simulates a flaky scenario where page navigation might be slow.
        """
        def _test_flaky_nav():
            # Add small delay to simulate timing issue
            time.sleep(0.3)
            self.checkout_page.click_checkout_button()
            time.sleep(0.3)
            
            # Fill information with potential timing issues
            self.checkout_page.enter_first_name("John")
            time.sleep(0.2)
            self.checkout_page.enter_last_name("Doe")
            time.sleep(0.2)
            self.checkout_page.enter_postal_code("12345")
            
            self.checkout_page.click_continue_button()
            assert self.checkout_page.is_checkout_summary_page_loaded(), "Summary should load"
        
        result = execute_test_with_retry(
            _test_flaky_nav,
            "test_flaky_checkout_navigation",
            max_retries=3,
            retry_delay=1.5
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        # This test might be flaky
        assert result.status.value in ["PASS", "FLAKY"], "Test should pass or be flaky"
    
    def test_get_completion_message(self):
        """
        Test getting order completion message.
        
        This test should pass on first attempt.
        """
        def _test_completion():
            # Complete checkout
            self.checkout_page.complete_checkout("John", "Doe", "12345")
            time.sleep(0.5)
            
            # Get completion message
            message = self.checkout_page.get_completion_message()
            text = self.checkout_page.get_completion_text()
            
            assert message is not None, "Should have completion message"
            assert text is not None, "Should have completion text"
            assert "THANK YOU" in message.upper(), "Message should contain THANK YOU"
        
        result = execute_test_with_retry(
            _test_completion,
            "test_get_completion_message",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_back_home_after_checkout(self):
        """
        Test navigating back to home after checkout completion.
        
        This test should pass on first attempt.
        """
        def _test_back_home():
            # Complete checkout
            self.checkout_page.complete_checkout("John", "Doe", "12345")
            time.sleep(0.5)
            
            # Click back home
            self.checkout_page.click_back_home_button()
            time.sleep(0.5)
            
            # Verify back on inventory page
            current_url = self.driver_manager.get_current_url()
            assert "inventory.html" in current_url, "Should be back on inventory page"
        
        result = execute_test_with_retry(
            _test_back_home,
            "test_back_home_after_checkout",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
