"""
Login Page Object Model for Saucedemo

This module implements the Page Object Model for the login page of Saucedemo.
It provides methods to interact with login page elements and perform login operations.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

from core.driver import get_driver_manager
from core.logger import get_logger


class LoginPage:
    """
    Page Object Model for the Saucedemo Login Page.
    
    This class encapsulates all interactions with the login page including:
    - Locating page elements
    - Entering credentials
    - Clicking login button
    - Verifying login success/failure
    """
    
    # Page Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    LOGO = (By.CLASS_NAME, "login_logo")
    
    # Valid credentials for Saucedemo
    STANDARD_USER = "standard_user"
    LOCKED_OUT_USER = "locked_out_user"
    PROBLEM_USER = "problem_user"
    PERFORMANCE_GLITCH_USER = "performance_glitch_user"
    VALID_PASSWORD = "secret_sauce"
    
    def __init__(self):
        """
        Initialize the LoginPage.
        
        Sets up driver manager and logger instances.
        """
        self.driver_manager = get_driver_manager()
        self.logger = get_logger("LoginPage")
        self.driver = self.driver_manager.get_driver()
    
    def navigate_to_login_page(self, url: str) -> None:
        """
        Navigate to the login page.
        
        Args:
            url: URL of the login page
        """
        try:
            self.driver_manager.navigate_to(url)
            self.logger.log_info(f"Navigated to login page: {url}")
        except Exception as e:
            self.logger.log_exception(e, "Failed to navigate to login page")
            raise
    
    def enter_username(self, username: str) -> None:
        """
        Enter username in the username field.
        
        Args:
            username: Username to enter
        """
        try:
            username_field = self.driver_manager.wait_for_element_visible(self.USERNAME_INPUT)
            username_field.clear()
            username_field.send_keys(username)
            self.logger.log_info(f"Entered username: {username}")
        except Exception as e:
            self.logger.log_exception(e, "Failed to enter username")
            raise
    
    def enter_password(self, password: str) -> None:
        """
        Enter password in the password field.
        
        Args:
            password: Password to enter
        """
        try:
            password_field = self.driver_manager.wait_for_element_visible(self.PASSWORD_INPUT)
            password_field.clear()
            password_field.send_keys(password)
            self.logger.log_info("Entered password")
        except Exception as e:
            self.logger.log_exception(e, "Failed to enter password")
            raise
    
    def click_login_button(self) -> None:
        """
        Click the login button.
        """
        try:
            login_button = self.driver_manager.wait_for_element_clickable(self.LOGIN_BUTTON)
            login_button.click()
            self.logger.log_info("Clicked login button")
        except Exception as e:
            self.logger.log_exception(e, "Failed to click login button")
            raise
    
    def login(self, username: str, password: str) -> None:
        """
        Perform complete login operation.
        
        Args:
            username: Username to login with
            password: Password to login with
        """
        try:
            self.enter_username(username)
            self.enter_password(password)
            self.click_login_button()
            self.logger.log_info(f"Login attempt with username: {username}")
        except Exception as e:
            self.logger.log_exception(e, "Login operation failed")
            raise
    
    def login_with_standard_user(self) -> None:
        """
        Login with standard user credentials.
        """
        self.login(self.STANDARD_USER, self.VALID_PASSWORD)
    
    def login_with_locked_user(self) -> None:
        """
        Login with locked out user credentials (intentional failure).
        """
        self.login(self.LOCKED_OUT_USER, self.VALID_PASSWORD)
    
    def login_with_problem_user(self) -> None:
        """
        Login with problem user credentials.
        """
        self.login(self.PROBLEM_USER, self.VALID_PASSWORD)
    
    def login_with_performance_glitch_user(self) -> None:
        """
        Login with performance glitch user credentials (intentional flaky scenario).
        """
        self.login(self.PERFORMANCE_GLITCH_USER, self.VALID_PASSWORD)
    
    def get_error_message(self) -> Optional[str]:
        """
        Get the error message displayed on login failure.
        
        Returns:
            Optional[str]: Error message text if present, None otherwise
        """
        try:
            error_element = self.driver_manager.wait_for_element_visible(self.ERROR_MESSAGE, timeout=5)
            error_text = error_element.text
            self.logger.log_info(f"Error message: {error_text}")
            return error_text
        except Exception:
            self.logger.log_info("No error message found")
            return None
    
    def is_login_successful(self) -> bool:
        """
        Check if login was successful by verifying URL change.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # After successful login, URL should contain /inventory.html
            current_url = self.driver_manager.get_current_url()
            is_successful = "inventory.html" in current_url
            self.logger.log_info(f"Login successful: {is_successful}")
            return is_successful
        except Exception as e:
            self.logger.log_exception(e, "Failed to check login status")
            return False
    
    def is_page_loaded(self) -> bool:
        """
        Check if the login page is fully loaded.
        
        Returns:
            bool: True if page loaded, False otherwise
        """
        try:
            logo = self.driver_manager.wait_for_element_visible(self.LOGO, timeout=10)
            return logo is not None
        except Exception:
            return False
    
    def get_page_title(self) -> str:
        """
        Get the page title.
        
        Returns:
            str: Page title
        """
        return self.driver_manager.get_page_title()
    
    def clear_credentials(self) -> None:
        """
        Clear username and password fields.
        """
        try:
            username_field = self.driver_manager.wait_for_element_visible(self.USERNAME_INPUT)
            password_field = self.driver_manager.wait_for_element_visible(self.PASSWORD_INPUT)
            username_field.clear()
            password_field.clear()
            self.logger.log_info("Cleared credentials")
        except Exception as e:
            self.logger.log_exception(e, "Failed to clear credentials")
