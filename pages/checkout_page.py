"""
Checkout Page Object Model for Saucedemo

This module implements the Page Object Model for the checkout page of Saucedemo.
It provides methods to interact with checkout process including cart review and checkout form.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

from core.driver import get_driver_manager
from core.logger import get_logger


class CheckoutPage:
    """
    Page Object Model for the Saucedemo Checkout Page.
    
    This class encapsulates all interactions with the checkout process including:
    - Cart review
    - Checkout information form
    - Order confirmation
    - Order completion
    """
    
    # Cart Page Locators
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    CART_ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")
    
    # Checkout Information Page Locators
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CANCEL_BUTTON = (By.ID, "cancel")
    CONTINUE_BUTTON = (By.ID, "continue")
    
    # Checkout Summary Page Locators
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON_SUMMARY = (By.ID, "cancel")
    SUBTOTAL_LABEL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX_LABEL = (By.CLASS_NAME, "summary_tax_label")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")
    
    # Checkout Complete Page Locators
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT = (By.CLASS_NAME, "complete-text")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")
    
    def __init__(self):
        """
        Initialize the CheckoutPage.
        
        Sets up driver manager and logger instances.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("CheckoutPage")
        self.driver = self.driver_manager.get_driver()
    
    def is_cart_page_loaded(self) -> bool:
        """
        Check if the cart page is fully loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            checkout_button = self.driver_manager.wait_for_element_visible(self.CHECKOUT_BUTTON, timeout=10)
            return checkout_button is not None
        except Exception:
            return False
    
    def get_cart_items(self) -> list:
        """
        Get all items in the cart.
        
        Returns:
            list: List of cart item information
        """
        try:
            items = []
            cart_items = self.driver.find_elements(*self.CART_ITEMS)
            
            for item in cart_items:
                try:
                    name = item.find_element(*self.CART_ITEM_NAME).text
                    price = item.find_element(*self.CART_ITEM_PRICE).text
                    items.append({
                        "name": name,
                        "price": price
                    })
                except Exception as e:
                    self.logger.log_warning(f"Failed to extract cart item: {str(e)}")
                    continue
            
            self.logger.log_info(f"Found {len(items)} items in cart")
            return items
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to get cart items")
            return []
    
    def get_cart_item_count(self) -> int:
        """
        Get the number of items in the cart.
        
        Returns:
            int: Number of items in cart
        """
        try:
            cart_items = self.driver.find_elements(*self.CART_ITEMS)
            count = len(cart_items)
            self.logger.log_info(f"Cart item count: {count}")
            return count
        except Exception as e:
            self.logger.log_exception(e, "Failed to get cart item count")
            return 0
    
    def click_checkout_button(self) -> None:
        """
        Click the checkout button to proceed to checkout.
        """
        try:
            checkout_button = self.driver_manager.wait_for_element_clickable(self.CHECKOUT_BUTTON)
            checkout_button.click()
            self.logger.log_info("Clicked checkout button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click checkout button")
            raise
    
    def click_continue_shopping(self) -> None:
        """
        Click continue shopping to return to inventory.
        """
        try:
            continue_button = self.driver_manager.wait_for_element_clickable(self.CONTINUE_SHOPPING_BUTTON)
            continue_button.click()
            self.logger.log_info("Clicked continue shopping")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click continue shopping")
            raise
    
    def is_checkout_info_page_loaded(self) -> bool:
        """
        Check if the checkout information page is loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            continue_button = self.driver_manager.wait_for_element_visible(self.CONTINUE_BUTTON, timeout=10)
            return continue_button is not None
        except Exception:
            return False
    
    def enter_first_name(self, first_name: str) -> None:
        """
        Enter first name in the checkout form.
        
        Args:
            first_name: First name to enter
        """
        try:
            first_name_field = self.driver_manager.wait_for_element_visible(self.FIRST_NAME_INPUT)
            first_name_field.clear()
            first_name_field.send_keys(first_name)
            self.logger.log_info(f"Entered first name: {first_name}")
        except Exception as e:
            self.logger.log_exception(e, "Failed to enter first name")
            raise
    
    def enter_last_name(self, last_name: str) -> None:
        """
        Enter last name in the checkout form.
        
        Args:
            last_name: Last name to enter
        """
        try:
            last_name_field = self.driver_manager.wait_for_element_visible(self.LAST_NAME_INPUT)
            last_name_field.clear()
            last_name_field.send_keys(last_name)
            self.logger.log_info(f"Entered last name: {last_name}")
        except Exception as e:
            self.logger.log_exception(e, "Failed to enter last name")
            raise
    
    def enter_postal_code(self, postal_code: str) -> None:
        """
        Enter postal code in the checkout form.
        
        Args:
            postal_code: Postal code to enter
        """
        try:
            postal_code_field = self.driver_manager.wait_for_element_visible(self.POSTAL_CODE_INPUT)
            postal_code_field.clear()
            postal_code_field.send_keys(postal_code)
            self.logger.log_info(f"Entered postal code: {postal_code}")
        except Exception as e:
            self.logger.log_exception(e, "Failed to enter postal code")
            raise
    
    def fill_checkout_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        """
        Fill all checkout information fields.
        
        Args:
            first_name: First name
            last_name: Last name
            postal_code: Postal code
        """
        try:
            self.enter_first_name(first_name)
            self.enter_last_name(last_name)
            self.enter_postal_code(postal_code)
            self.logger.log_info("Filled checkout information")
        except Exception as e:
            self.logger.log_exception(e, "Failed to fill checkout information")
            raise
    
    def click_continue_button(self) -> None:
        """
        Click continue button to proceed to checkout summary.
        """
        try:
            continue_button = self.driver_manager.wait_for_element_clickable(self.CONTINUE_BUTTON)
            continue_button.click()
            self.logger.log_info("Clicked continue button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click continue button")
            raise
    
    def click_cancel_button(self) -> None:
        """
        Click cancel button to cancel checkout.
        """
        try:
            cancel_button = self.driver_manager.wait_for_element_clickable(self.CANCEL_BUTTON)
            cancel_button.click()
            self.logger.log_info("Clicked cancel button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click cancel button")
            raise
    
    def is_checkout_summary_page_loaded(self) -> bool:
        """
        Check if the checkout summary page is loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            finish_button = self.driver_manager.wait_for_element_visible(self.FINISH_BUTTON, timeout=10)
            return finish_button is not None
        except Exception:
            return False
    
    def get_subtotal(self) -> Optional[str]:
        """
        Get the subtotal amount.
        
        Returns:
            Optional[str]: Subtotal text if found, None otherwise
        """
        try:
            subtotal_label = self.driver.find_element(*self.SUBTOTAL_LABEL)
            subtotal = subtotal_label.text
            self.logger.log_info(f"Subtotal: {subtotal}")
            return subtotal
        except Exception:
            self.logger.log_warning("Could not get subtotal")
            return None
    
    def get_tax(self) -> Optional[str]:
        """
        Get the tax amount.
        
        Returns:
            Optional[str]: Tax text if found, None otherwise
        """
        try:
            tax_label = self.driver.find_element(*self.TAX_LABEL)
            tax = tax_label.text
            self.logger.log_info(f"Tax: {tax}")
            return tax
        except Exception:
            self.logger.log_warning("Could not get tax")
            return None
    
    def get_total(self) -> Optional[str]:
        """
        Get the total amount.
        
        Returns:
            Optional[str]: Total text if found, None otherwise
        """
        try:
            total_label = self.driver.find_element(*self.TOTAL_LABEL)
            total = total_label.text
            self.logger.log_info(f"Total: {total}")
            return total
        except Exception:
            self.logger.log_warning("Could not get total")
            return None
    
    def click_finish_button(self) -> None:
        """
        Click finish button to complete the order.
        """
        try:
            finish_button = self.driver_manager.wait_for_element_clickable(self.FINISH_BUTTON)
            finish_button.click()
            self.logger.log_info("Clicked finish button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click finish button")
            raise
    
    def is_checkout_complete_page_loaded(self) -> bool:
        """
        Check if the checkout complete page is loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            complete_header = self.driver_manager.wait_for_element_visible(self.COMPLETE_HEADER, timeout=10)
            return complete_header is not None
        except Exception:
            return False
    
    def get_completion_message(self) -> Optional[str]:
        """
        Get the order completion message.
        
        Returns:
            Optional[str]: Completion message if found, None otherwise
        """
        try:
            header = self.driver.find_element(*self.COMPLETE_HEADER)
            header_text = header.text
            self.logger.log_info(f"Completion message: {header_text}")
            return header_text
        except Exception:
            self.logger.log_warning("Could not get completion message")
            return None
    
    def get_completion_text(self) -> Optional[str]:
        """
        Get the completion description text.
        
        Returns:
            Optional[str]: Completion text if found, None otherwise
        """
        try:
            text = self.driver.find_element(*self.COMPLETE_TEXT)
            text_content = text.text
            self.logger.log_info(f"Completion text: {text_content}")
            return text_content
        except Exception:
            self.logger.log_warning("Could not get completion text")
            return None
    
    def click_back_home_button(self) -> None:
        """
        Click back home button to return to inventory.
        """
        try:
            back_home_button = self.driver_manager.wait_for_element_clickable(self.BACK_HOME_BUTTON)
            back_home_button.click()
            self.logger.log_info("Clicked back home button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click back home button")
            raise
    
    def complete_checkout(
        self,
        first_name: str = "John",
        last_name: str = "Doe",
        postal_code: str = "12345"
    ) -> bool:
        """
        Complete the entire checkout process.
        
        Args:
            first_name: First name for checkout
            last_name: Last name for checkout
            postal_code: Postal code for checkout
            
        Returns:
            bool: True if checkout completed successfully, False otherwise
        """
        try:
            # Proceed to checkout
            self.click_checkout_button()
            
            # Fill checkout information
            self.fill_checkout_information(first_name, last_name, postal_code)
            self.click_continue_button()
            
            # Complete order
            self.click_finish_button()
            
            # Verify completion
            if self.is_checkout_complete_page_loaded():
                self.logger.log_info("Checkout completed successfully")
                return True
            
            return False
            
        except Exception as e:
            self.logger.log_exception(e, "Checkout process failed")
            return False
