import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from core.config_loader import ConfigLoader

class TestInventory:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        
    def test_verify_inventory_page(self):
        """Test that inventory page loads correctly after login"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        assert self.inventory_page.is_loaded(), "Inventory page should be loaded"
        
    def test_verify_product_details(self):
        """Test that product details are displayed correctly"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        products = self.inventory_page.get_products()
        assert len(products) > 0, "Products should be available"
        assert all('name' in product and 'price' in product for product in products), "Each product should have name and price"
        
    def test_add_product_to_cart(self):
        """Test adding a product to cart"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        initial_count = self.inventory_page.get_cart_count()
        self.inventory_page.add_first_item_to_cart()
        final_count = self.inventory_page.get_cart_count()
        assert final_count == initial_count + 1, "Cart count should increase by 1"
        
    def test_remove_product_from_cart(self):
        """Test removing a product from cart"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        self.inventory_page.add_first_item_to_cart()
        initial_count = self.inventory_page.get_cart_count()
        self.inventory_page.remove_first_item_from_cart()
        final_count = self.inventory_page.get_cart_count()
        assert final_count == initial_count - 1, "Cart count should decrease by 1"
