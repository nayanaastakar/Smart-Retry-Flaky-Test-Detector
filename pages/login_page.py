"""
Login Page Object Model - Module 1

This module implements the Page Object Model for the SauceDemo login page.
It encapsulates all interactions with the login page elements.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

from config.config import Config


class LoginPage:
    """
    Page Object for SauceDemo Login Page - Module 1.
    
    This class provides methods to interact with the login page elements
    including navigation, login form submission, and login verification.
    """
    
    # Locators for SauceDemo login page
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    
    def __init__(self, driver):
        """
        Initialize the LoginPage with a WebDriver instance.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.config = Config()
        self.wait = WebDriverWait(driver, self.config.EXPLICIT_WAIT)
    
    def navigate(self) -> None:
        """
        Navigate to the SauceDemo login page.
        """
        try:
            self.driver.get(self.config.SAUCE_DEMO_URL)
            self.wait.until(EC.presence_of_element_located(self.USERNAME_FIELD))
        except Exception as e:
            raise Exception(f"Failed to navigate to login page: {str(e)}")
    
    def enter_username(self, username: str) -> None:
        """
        Enter username in the username field.
        
        Args:
            username: Username to enter
        """
        try:
            username_field = self.wait.until(
                EC.presence_of_element_located(self.USERNAME_FIELD)
            )
            username_field.clear()
            username_field.send_keys(username)
        except Exception as e:
            raise Exception(f"Failed to enter username: {str(e)}")
    
    def enter_password(self, password: str) -> None:
        """
        Enter password in the password field.
        
        Args:
            password: Password to enter
        """
        try:
            password_field = self.wait.until(
                EC.presence_of_element_located(self.PASSWORD_FIELD)
            )
            password_field.clear()
            password_field.send_keys(password)
        except Exception as e:
            raise Exception(f"Failed to enter password: {str(e)}")
    
    def click_login_button(self) -> None:
        """
        Click the login button.
        """
        try:
            login_button = self.wait.until(
                EC.element_to_be_clickable(self.LOGIN_BUTTON)
            )
            login_button.click()
        except Exception as e:
            raise Exception(f"Failed to click login button: {str(e)}")
    
    def login(self, username: str, password: str) -> None:
        """
        Perform login with given credentials.
        
        Args:
            username: Username for login
            password: Password for login
        """
        try:
            self.enter_username(username)
            self.enter_password(password)
            self.click_login_button()
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def login_with_default_credentials(self) -> None:
        """
        Perform login using default credentials from config.
        """
        self.login(self.config.SAUCE_DEMO_USERNAME, self.config.SAUCE_DEMO_PASSWORD)
    
    def is_login_successful(self) -> bool:
        """
        Verify if login was successful by checking for inventory container.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            self.wait.until(EC.presence_of_element_located(self.INVENTORY_CONTAINER))
            return True
        except:
            return False
    
    def get_error_message(self) -> Optional[str]:
        """
        Get error message if login failed.
        
        Returns:
            Optional[str]: Error message text if present, None otherwise
        """
        try:
            error_element = self.driver.find_element(*self.ERROR_MESSAGE)
            return error_element.text
        except:
            return None
