from pages.base_page import BasePage

class InventoryPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        
    def add_first_item_to_cart(self):
        self.click("inventory", "first_add_to_cart")
        
    def go_to_cart(self):
        self.click("inventory", "cart_icon")
        
    def logout(self):
        self.click("inventory", "menu_btn")
        self.click("inventory", "logout_link")
