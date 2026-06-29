"""
Search Page Object Model for Saucedemo

This module implements the Page Object Model for the inventory/search page of Saucedemo.
It provides methods to interact with product listing and search functionality.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional

from core.driver import get_driver_manager
from core.logger import get_logger


class SearchPage:
    """
    Page Object Model for the Saucedemo Inventory/Search Page.
    
    This class encapsulates all interactions with the product inventory page including:
    - Locating product elements
    - Searching/filtering products
    - Adding products to cart
    - Verifying product details
    """
    
    # Page Locators
    PRODUCT_LIST = (By.CLASS_NAME, "inventory_item")
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_item_name")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "[data-test^='add-to-cart']")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "[data-test^='remove']")
    CART_ICON = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    FILTER_NAME_AZ = (By.CSS_SELECTOR, "[value='az']")
    FILTER_NAME_ZA = (By.CSS_SELECTOR, "[value='za']")
    FILTER_PRICE_LOW_HIGH = (By.CSS_SELECTOR, "[value='lohi']")
    FILTER_PRICE_HIGH_LOW = (By.CSS_SELECTOR, "[value='hilo']")
    
    def __init__(self):
        """
        Initialize the SearchPage.
        
        Sets up driver manager and logger instances.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("SearchPage")
        self.driver = self.driver_manager.get_driver()
    
    def is_page_loaded(self) -> bool:
        """
        Check if the inventory page is fully loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            products = self.driver_manager.wait_for_elements_visible(self.PRODUCT_LIST, timeout=10)
            return len(products) > 0
        except Exception:
            return False
    
    def get_all_products(self) -> List[dict]:
        """
        Get all products displayed on the page.
        
        Returns:
            List[dict]: List of product information dictionaries
        """
        try:
            products = []
            product_elements = self.driver.find_elements(*self.PRODUCT_LIST)
            
            for product_element in product_elements:
                try:
                    name = product_element.find_element(*self.PRODUCT_NAME).text
                    price = product_element.find_element(*self.PRODUCT_PRICE).text
                    products.append({
                        "name": name,
                        "price": price
                    })
                except Exception as e:
                    self.logger.log_warning(f"Failed to extract product info: {str(e)}")
                    continue
            
            self.logger.log_info(f"Found {len(products)} products")
            return products
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to get products")
            return []
    
    def find_product_by_name(self, product_name: str) -> Optional[dict]:
        """
        Find a specific product by name.
        
        Args:
            product_name: Name of the product to find
            
        Returns:
            Optional[dict]: Product information if found, None otherwise
        """
        try:
            products = self.get_all_products()
            for product in products:
                if product_name.lower() in product["name"].lower():
                    self.logger.log_info(f"Found product: {product_name}")
                    return product
            
            self.logger.log_warning(f"Product not found: {product_name}")
            return None
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to find product: {product_name}")
            return None
    
    def add_product_to_cart(self, product_name: str) -> bool:
        """
        Add a specific product to the cart.
        
        Args:
            product_name: Name of the product to add
            
        Returns:
            bool: True if product added successfully, False otherwise
        """
        try:
            product_elements = self.driver.find_elements(*self.PRODUCT_LIST)
            
            for product_element in product_elements:
                try:
                    name_element = product_element.find_element(*self.PRODUCT_NAME)
                    if product_name.lower() in name_element.text.lower():
                        add_button = product_element.find_element(*self.ADD_TO_CART_BUTTON)
                        add_button.click()
                        self.logger.log_info(f"Added product to cart: {product_name}")
                        return True
                except Exception:
                    continue
            
            self.logger.log_warning(f"Could not add product to cart: {product_name}")
            return False
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to add product to cart: {product_name}")
            return False
    
    def add_first_product_to_cart(self) -> bool:
        """
        Add the first available product to the cart.
        
        Returns:
            bool: True if product added successfully, False otherwise
        """
        try:
            add_buttons = self.driver.find_elements(*self.ADD_TO_CART_BUTTON)
            if add_buttons:
                add_buttons[0].click()
                self.logger.log_info("Added first product to cart")
                return True
            
            self.logger.log_warning("No products available to add")
            return False
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to add first product to cart")
            return False
    
    def get_cart_count(self) -> int:
        """
        Get the number of items in the cart.
        
        Returns:
            int: Number of items in cart
        """
        try:
            cart_badge = self.driver.find_element(*self.CART_BADGE)
            count = int(cart_badge.text)
            self.logger.log_info(f"Cart count: {count}")
            return count
        except Exception:
            self.logger.log_info("Cart is empty")
            return 0
    
    def click_cart_icon(self) -> None:
        """
        Click the cart icon to navigate to cart page.
        """
        try:
            cart_icon = self.driver_manager.wait_for_element_clickable(self.CART_ICON)
            cart_icon.click()
            self.logger.log_info("Clicked cart icon")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click cart icon")
            raise
    
    def sort_products_by_name_az(self) -> None:
        """
        Sort products by name (A-Z).
        """
        try:
            self._sort_products(self.FILTER_NAME_AZ)
            self.logger.log_info("Sorted products by name (A-Z)")
        except Exception as e:
            self.logger.log_exception(e, "Failed to sort products by name (A-Z)")
            raise
    
    def sort_products_by_name_za(self) -> None:
        """
        Sort products by name (Z-A).
        """
        try:
            self._sort_products(self.FILTER_NAME_ZA)
            self.logger.log_info("Sorted products by name (Z-A)")
        except Exception as e:
            self.logger.log_exception(e, "Failed to sort products by name (Z-A)")
            raise
    
    def sort_products_by_price_low_high(self) -> None:
        """
        Sort products by price (low to high).
        """
        try:
            self._sort_products(self.FILTER_PRICE_LOW_HIGH)
            self.logger.log_info("Sorted products by price (low to high)")
        except Exception as e:
            self.logger.log_exception(e, "Failed to sort products by price (low to high)")
            raise
    
    def sort_products_by_price_high_low(self) -> None:
        """
        Sort products by price (high to low).
        """
        try:
            self._sort_products(self.FILTER_PRICE_HIGH_LOW)
            self.logger.log_info("Sorted products by price (high to low)")
        except Exception as e:
            self.logger.log_exception(e, "Failed to sort products by price (high to low)")
            raise
    
    def _sort_products(self, filter_locator: tuple) -> None:
        """
        Internal method to sort products using a specific filter.
        
        Args:
            filter_locator: Locator tuple for the sort filter
        """
        try:
            dropdown = self.driver_manager.wait_for_element_clickable(self.SORT_DROPDOWN)
            dropdown.click()
            
            filter_option = self.driver_manager.wait_for_element_clickable(filter_locator)
            filter_option.click()
        except Exception as e:
            self.logger.log_exception(e, "Failed to apply sort filter")
            raise
    
    def get_product_count(self) -> int:
        """
        Get the total number of products on the page.
        
        Returns:
            int: Number of products
        """
        try:
            products = self.driver.find_elements(*self.PRODUCT_LIST)
            count = len(products)
            self.logger.log_info(f"Product count: {count}")
            return count
        except Exception as e:
            self.logger.log_exception(e, "Failed to get product count")
            return 0
    
    def is_product_available(self, product_name: str) -> bool:
        """
        Check if a specific product is available on the page.
        
        Args:
            product_name: Name of the product to check
            
        Returns:
            bool: True if product is available, False otherwise
        """
        product = self.find_product_by_name(product_name)
        return product is not None
