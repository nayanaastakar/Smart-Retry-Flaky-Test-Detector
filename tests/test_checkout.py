import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

class TestCheckout:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        self.cart_page = CartPage(driver)
        self.checkout_page = CheckoutPage(driver)
        
    def test_checkout_process(self):
        """Test the complete checkout process"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        self.cart_page.proceed_to_checkout()
        
        self.checkout_page.fill_information("John", "Doe", "12345")
        self.checkout_page.continue_checkout()
        assert self.checkout_page.is_summary_loaded(), "Checkout summary should load"
        
    def test_cancel_checkout(self):
        """Test canceling the checkout process"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        self.cart_page.proceed_to_checkout()
        
        self.checkout_page.cancel_checkout()
        assert self.cart_page.is_cart_loaded(), "Should return to cart after cancel"
        
    def test_complete_checkout(self):
        """Test completing the checkout process"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        self.cart_page.proceed_to_checkout()
        
        self.checkout_page.fill_information("Jane", "Smith", "54321")
        self.checkout_page.continue_checkout()
        self.checkout_page.finish_checkout()
        
        assert self.checkout_page.is_complete_loaded(), "Checkout complete page should load"
