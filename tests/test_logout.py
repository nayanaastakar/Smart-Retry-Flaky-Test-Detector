import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

class TestLogout:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        
    def test_logout(self):
        """Test logout functionality"""
        self.login_page.navigate()
        self.login_page.login_with_default_credentials()
        assert self.login_page.is_login_successful(), "Login should be successful"
        
        self.inventory_page.logout()
        assert not self.login_page.is_login_successful(), "User should be logged out"
        assert self.login_page.is_page_loaded(), "Should return to login page"
