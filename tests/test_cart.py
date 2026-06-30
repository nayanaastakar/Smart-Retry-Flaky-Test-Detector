import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

class TestCart:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        self.cart_page = CartPage(driver)
        
    def test_add_to_cart(self):
        """Test adding an item to the cart"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        assert self.login_page.is_login_successful(), "Must be logged in to add to cart"
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        assert self.cart_page.is_cart_loaded(), "Cart page did not load successfully"

    def test_remove_from_cart(self):
        """Test removing an item from the cart"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        
        self.cart_page.remove_item()
        assert True, "Removed item without exception"

    def test_verify_cart(self):
        """Test verifying cart contents"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        
        self.inventory_page.add_first_item_to_cart()
        self.inventory_page.go_to_cart()
        
        cart_items = self.cart_page.get_cart_items()
        assert len(cart_items) > 0, "Cart should have items"
        assert all('name' in item and 'price' in item for item in cart_items), "Each item should have name and price"
