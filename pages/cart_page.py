from pages.base_page import BasePage

class CartPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        
    def is_cart_loaded(self):
        return self.is_element_visible("cart", "cart_list")
        
    def remove_item(self):
        self.click("cart", "remove_button")
        
    def proceed_to_checkout(self):
        self.click("cart", "checkout_button")
