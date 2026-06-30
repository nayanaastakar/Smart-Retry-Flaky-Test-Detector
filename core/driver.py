"""
Selenium WebDriver Manager Module - Module 1

This module provides basic WebDriver management with:
- Automatic ChromeDriver download and management using webdriver-manager
- Configurable browser options
- Headless mode support
- Browser lifecycle management
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from typing import Optional

from config.config import Config


class DriverManager:
    """
    Manages Selenium WebDriver lifecycle and configuration - Module 1.
    
    This class provides methods to initialize, configure, and manage
    the Chrome WebDriver with automatic driver management using webdriver-manager.
    """
    
    def __init__(self):
        """
        Initialize the DriverManager.
        
        Sets up the driver instance and configuration parameters.
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.config = Config()
    
    def initialize_driver(self) -> webdriver.Chrome:
        """
        Initialize and configure the Chrome WebDriver.
        
        This method:
        - Downloads the appropriate ChromeDriver version automatically using webdriver-manager
        - Configures browser options (headless mode, window size, etc.)
        - Sets up timeouts (implicit, page load)
        - Returns the configured driver instance
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        try:
            # Configure Chrome options
            chrome_options = Options()
            
            # Set headless mode if configured
            if self.config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            
            # Set window size
            chrome_options.add_argument(f"--window-size={self.config.BROWSER_WINDOW_SIZE}")
            
            # Add additional options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--ignore-certificate-errors")
            
            # Enable browser console log capture (Module 4)
            chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

            # Use Selenium 4's built-in Selenium Manager (no webdriver-manager needed)
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.set_script_timeout(self.config.SCRIPT_TIMEOUT)

            return self.driver
            
        except Exception as e:
            raise Exception(f"Failed to initialize WebDriver: {str(e)}")
    
    def quit_driver(self) -> None:
        """
        Quit the WebDriver instance and release resources.
        
        This method safely closes the browser and releases all resources
        associated with the WebDriver instance.
        """
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                print(f"Error quitting driver: {str(e)}")
    
    def get_driver(self) -> webdriver.Chrome:
        """
        Get the current WebDriver instance.
        
        Returns:
            webdriver.Chrome: Current WebDriver instance
            
        Raises:
            Exception: If driver is not initialized
        """
        if self.driver is None:
            raise Exception("Driver not initialized. Call initialize_driver() first.")
        return self.driver
