"""
Search Test Module for Saucedemo

This module contains test cases for product search and inventory functionality including:
- Product listing
- Product search
- Adding products to cart
- Sorting products
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
from config.config import Config


class TestSearch:
    """
    Test class for product search and inventory functionality.
    
    Tests include product listing, search, cart operations, and flaky scenarios.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Setup and teardown for each test.
        
        Initializes driver manager, logs in, and navigates to inventory page.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("TestSearch")
        self.config = Config()
        self.login_page = LoginPage()
        self.search_page = SearchPage()
        
        # Navigate to login page and login
        self.login_page.navigate_to_login_page(self.config.SAUCE_DEMO_URL)
        self.login_page.login_with_standard_user()
        
        # Wait for inventory page to load
        time.sleep(1)
        
        yield
        
        # Cleanup
        self.driver_manager.quit_driver()
    
    def test_inventory_page_load(self):
        """
        Test that inventory page loads correctly.
        
        This test should pass on first attempt.
        """
        def _test_page_load():
            assert self.search_page.is_page_loaded(), "Inventory page should be loaded"
            assert self.search_page.get_product_count() > 0, "Products should be displayed"
        
        result = execute_test_with_retry(
            _test_page_load,
            "test_inventory_page_load",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_get_all_products(self):
        """
        Test retrieving all products from inventory.
        
        This test should pass on first attempt.
        """
        def _test_get_products():
            products = self.search_page.get_all_products()
            assert len(products) > 0, "Should retrieve products"
            assert all("name" in p and "price" in p for p in products), "Each product should have name and price"
        
        result = execute_test_with_retry(
            _test_get_products,
            "test_get_all_products",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_find_product_by_name(self):
        """
        Test finding a specific product by name.
        
        This test should pass on first attempt.
        """
        def _test_find_product():
            product = self.search_page.find_product_by_name("Sauce Labs Backpack")
            assert product is not None, "Should find the product"
            assert "Backpack" in product["name"], "Product name should match"
        
        result = execute_test_with_retry(
            _test_find_product,
            "test_find_product_by_name",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_add_product_to_cart(self):
        """
        Test adding a product to cart.
        
        This test should pass on first attempt.
        """
        def _test_add_to_cart():
            initial_count = self.search_page.get_cart_count()
            success = self.search_page.add_product_to_cart("Sauce Labs Backpack")
            assert success, "Should successfully add product to cart"
            final_count = self.search_page.get_cart_count()
            assert final_count == initial_count + 1, "Cart count should increase by 1"
        
        result = execute_test_with_retry(
            _test_add_to_cart,
            "test_add_product_to_cart",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_add_first_product_to_cart(self):
        """
        Test adding the first available product to cart.
        
        This test should pass on first attempt.
        """
        def _test_add_first():
            initial_count = self.search_page.get_cart_count()
            success = self.search_page.add_first_product_to_cart()
            assert success, "Should successfully add first product to cart"
            final_count = self.search_page.get_cart_count()
            assert final_count == initial_count + 1, "Cart count should increase by 1"
        
        result = execute_test_with_retry(
            _test_add_first,
            "test_add_first_product_to_cart",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_sort_products_by_name_az(self):
        """
        Test sorting products by name (A-Z).
        
        This test should pass on first attempt.
        """
        def _test_sort_az():
            self.search_page.sort_products_by_name_az()
            products = self.search_page.get_all_products()
            assert len(products) > 0, "Should have products after sorting"
            # Verify sorting
            names = [p["name"] for p in products]
            assert names == sorted(names), "Products should be sorted A-Z"
        
        result = execute_test_with_retry(
            _test_sort_az,
            "test_sort_products_by_name_az",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_sort_products_by_price_low_high(self):
        """
        Test sorting products by price (low to high).
        
        This test should pass on first attempt.
        """
        def _test_sort_price():
            self.search_page.sort_products_by_price_low_high()
            products = self.search_page.get_all_products()
            assert len(products) > 0, "Should have products after sorting"
        
        result = execute_test_with_retry(
            _test_sort_price,
            "test_sort_products_by_price_low_high",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_flaky_product_search(self):
        """
        Test with intentional flaky scenario - searching for non-existent product.
        
        This test simulates a flaky scenario where element might not be found initially.
        """
        def _test_flaky_search():
            # Small delay to simulate timing issue
            time.sleep(0.3)
            product = self.search_page.find_product_by_name("NonExistentProduct123")
            # This should return None (product not found)
            assert product is None, "Non-existent product should not be found"
        
        result = execute_test_with_retry(
            _test_flaky_search,
            "test_flaky_product_search",
            max_retries=3,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        # This test should pass (product not found is expected behavior)
        assert result.status.value == "PASS", "Test should pass"
    
    def test_click_cart_icon(self):
        """
        Test clicking cart icon to navigate to cart.
        
        This test should pass on first attempt.
        """
        def _test_cart_click():
            self.search_page.click_cart_icon()
            # Verify navigation - URL should contain cart.html
            current_url = self.driver_manager.get_current_url()
            assert "cart.html" in current_url, "Should navigate to cart page"
        
        result = execute_test_with_retry(
            _test_cart_click,
            "test_click_cart_icon",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
    
    def test_product_availability(self):
        """
        Test checking if a specific product is available.
        
        This test should pass on first attempt.
        """
        def _test_availability():
            is_available = self.search_page.is_product_available("Sauce Labs Backpack")
            assert is_available, "Product should be available"
            
            not_available = self.search_page.is_product_available("NonExistentProduct")
            assert not not_available, "Non-existent product should not be available"
        
        result = execute_test_with_retry(
            _test_availability,
            "test_product_availability",
            max_retries=2,
            retry_delay=1.0
        )
        
        self.logger.log_info(f"Test result: {result.status.value}")
        assert result.status.value == "PASS", "Test should pass on first attempt"
