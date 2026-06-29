"""
Selenium WebDriver Manager Module

This module provides a centralized WebDriver management system with:
- Automatic ChromeDriver download and management
- Configurable browser options
- Headless mode support
- Implicit and explicit wait helpers
- Browser lifecycle management
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, List
import logging

from config.config import Config


class DriverManager:
    """
    Manages Selenium WebDriver lifecycle and configuration.
    
    This class provides methods to initialize, configure, and manage
    the Chrome WebDriver with automatic driver management.
    """
    
    def __init__(self):
        """
        Initialize the DriverManager.
        
        Sets up the driver instance and configuration parameters.
        """
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = logging.getLogger(__name__)
        self.config = Config()
    
    def initialize_driver(self) -> webdriver.Chrome:
        """
        Initialize and configure the Chrome WebDriver.
        
        This method:
        - Downloads the appropriate ChromeDriver version automatically
        - Configures browser options (headless mode, window size, etc.)
        - Sets up timeouts (implicit, page load, script)
        - Enables browser logging for console logs
        
        Returns:
            webdriver.Chrome: Configured WebDriver instance
        """
        try:
            # Configure Chrome options
            chrome_options = Options()
            
            # Headless mode configuration
            if self.config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                self.logger.info("Headless mode enabled")
            
            # Window size configuration
            chrome_options.add_argument(f"--window-size={self.config.BROWSER_WINDOW_SIZE}")
            
            # Additional browser options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Enable browser logging for console logs
            chrome_options.set_capability("goog:loggingPrefs", {
                "browser": "ALL"
            })
            
            # Initialize ChromeDriver Service with error handling
            try:
                service = Service(ChromeDriverManager().install())
                # Initialize WebDriver
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_error:
                # Fallback: Try without webdriver-manager if it fails
                self.logger.warning(f"ChromeDriverManager failed: {str(driver_error)}")
                self.logger.info("Attempting to use system ChromeDriver...")
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as system_error:
                    self.logger.error(f"System ChromeDriver also failed: {str(system_error)}")
                    raise Exception(f"Failed to initialize ChromeDriver: {str(driver_error)}")
            
            # Set timeouts
            self.driver.implicitly_wait(self.config.IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(self.config.PAGE_LOAD_TIMEOUT)
            self.driver.set_script_timeout(self.config.SCRIPT_TIMEOUT)
            
            self.logger.info("WebDriver initialized successfully")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def get_driver(self) -> webdriver.Chrome:
        """
        Get the current WebDriver instance.
        
        Initializes the driver if it doesn't exist.
        
        Returns:
            webdriver.Chrome: Current WebDriver instance
        """
        if self.driver is None:
            return self.initialize_driver()
        return self.driver
    
    def quit_driver(self) -> None:
        """
        Quit the WebDriver and clean up resources.
        
        This method safely closes the browser and releases resources.
        """
        if self.driver is not None:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
    
    def navigate_to(self, url: str) -> None:
        """
        Navigate to a specific URL.
        
        Args:
            url: The URL to navigate to
        """
        try:
            self.get_driver().get(url)
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise
    
    def get_current_url(self) -> str:
        """
        Get the current URL of the browser.
        
        Returns:
            str: Current URL
        """
        return self.get_driver().current_url
    
    def get_page_title(self) -> str:
        """
        Get the title of the current page.
        
        Returns:
            str: Page title
        """
        return self.get_driver().title
    
    def refresh_page(self) -> None:
        """
        Refresh the current page.
        """
        try:
            self.get_driver().refresh()
            self.logger.info("Page refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            raise
    
    def go_back(self) -> None:
        """
        Navigate back in browser history.
        """
        try:
            self.get_driver().back()
            self.logger.info("Navigated back")
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {str(e)}")
            raise
    
    def go_forward(self) -> None:
        """
        Navigate forward in browser history.
        """
        try:
            self.get_driver().forward()
            self.logger.info("Navigated forward")
        except Exception as e:
            self.logger.error(f"Failed to navigate forward: {str(e)}")
            raise
    
    def maximize_window(self) -> None:
        """
        Maximize the browser window.
        """
        try:
            self.get_driver().maximize_window()
            self.logger.info("Browser window maximized")
        except Exception as e:
            self.logger.error(f"Failed to maximize window: {str(e)}")
            raise
    
    def minimize_window(self) -> None:
        """
        Minimize the browser window.
        """
        try:
            self.get_driver().minimize_window()
            self.logger.info("Browser window minimized")
        except Exception as e:
            self.logger.error(f"Failed to minimize window: {str(e)}")
            raise
    
    def execute_script(self, script: str, *args) -> any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of the script execution
        """
        try:
            return self.get_driver().execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Failed to execute script: {str(e)}")
            raise
    
    def wait_for_element(self, locator: tuple, timeout: Optional[int] = None) -> any:
        """
        Wait for an element to be present on the page.
        
        Args:
            locator: Tuple of (By, locator_value)
            timeout: Custom timeout in seconds (uses config default if not provided)
            
        Returns:
            WebElement: The found element
        """
        try:
            wait_time = timeout or self.config.EXPLICIT_WAIT
            wait = WebDriverWait(self.get_driver(), wait_time)
            element = wait.until(EC.presence_of_element_located(locator))
            self.logger.info(f"Element found: {locator}")
            return element
        except Exception as e:
            self.logger.error(f"Element not found: {locator} - {str(e)}")
            raise
    
    def wait_for_element_visible(self, locator: tuple, timeout: Optional[int] = None) -> any:
        """
        Wait for an element to be visible on the page.
        
        Args:
            locator: Tuple of (By, locator_value)
            timeout: Custom timeout in seconds (uses config default if not provided)
            
        Returns:
            WebElement: The visible element
        """
        try:
            wait_time = timeout or self.config.EXPLICIT_WAIT
            wait = WebDriverWait(self.get_driver(), wait_time)
            element = wait.until(EC.visibility_of_element_located(locator))
            self.logger.info(f"Element visible: {locator}")
            return element
        except Exception as e:
            self.logger.error(f"Element not visible: {locator} - {str(e)}")
            raise
    
    def wait_for_element_clickable(self, locator: tuple, timeout: Optional[int] = None) -> any:
        """
        Wait for an element to be clickable.
        
        Args:
            locator: Tuple of (By, locator_value)
            timeout: Custom timeout in seconds (uses config default if not provided)
            
        Returns:
            WebElement: The clickable element
        """
        try:
            wait_time = timeout or self.config.EXPLICIT_WAIT
            wait = WebDriverWait(self.get_driver(), wait_time)
            element = wait.until(EC.element_to_be_clickable(locator))
            self.logger.info(f"Element clickable: {locator}")
            return element
        except Exception as e:
            self.logger.error(f"Element not clickable: {locator} - {str(e)}")
            raise
    
    def wait_for_title_contains(self, title: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for the page title to contain specific text.
        
        Args:
            title: Text to search for in the title
            timeout: Custom timeout in seconds (uses config default if not provided)
            
        Returns:
            bool: True if title contains the text
        """
        try:
            wait_time = timeout or self.config.EXPLICIT_WAIT
            wait = WebDriverWait(self.get_driver(), wait_time)
            wait.until(EC.title_contains(title))
            self.logger.info(f"Title contains: {title}")
            return True
        except Exception as e:
            self.logger.error(f"Title does not contain '{title}': {str(e)}")
            return False
    
    def wait_for_url_contains(self, url: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for the URL to contain specific text.
        
        Args:
            url: Text to search for in the URL
            timeout: Custom timeout in seconds (uses config default if not provided)
            
        Returns:
            bool: True if URL contains the text
        """
        try:
            wait_time = timeout or self.config.EXPLICIT_WAIT
            wait = WebDriverWait(self.get_driver(), wait_time)
            wait.until(EC.url_contains(url))
            self.logger.info(f"URL contains: {url}")
            return True
        except Exception as e:
            self.logger.error(f"URL does not contain '{url}': {str(e)}")
            return False
    
    def get_browser_logs(self) -> List[dict]:
        """
        Retrieve browser console logs.
        
        Returns:
            List[dict]: List of log entries from the browser console
        """
        try:
            logs = self.get_driver().get_log('browser')
            self.logger.info(f"Retrieved {len(logs)} browser log entries")
            return logs
        except Exception as e:
            self.logger.error(f"Failed to retrieve browser logs: {str(e)}")
            return []
    
    def switch_to_frame(self, frame_reference: any) -> None:
        """
        Switch to a specific iframe.
        
        Args:
            frame_reference: Frame identifier (name, ID, index, or WebElement)
        """
        try:
            self.get_driver().switch_to.frame(frame_reference)
            self.logger.info(f"Switched to frame: {frame_reference}")
        except Exception as e:
            self.logger.error(f"Failed to switch to frame: {str(e)}")
            raise
    
    def switch_to_default_content(self) -> None:
        """
        Switch back to the main document from an iframe.
        """
        try:
            self.get_driver().switch_to.default_content()
            self.logger.info("Switched to default content")
        except Exception as e:
            self.logger.error(f"Failed to switch to default content: {str(e)}")
            raise
    
    def switch_to_window(self, window_handle: str) -> None:
        """
        Switch to a specific browser window/tab.
        
        Args:
            window_handle: Window handle to switch to
        """
        try:
            self.get_driver().switch_to.window(window_handle)
            self.logger.info(f"Switched to window: {window_handle}")
        except Exception as e:
            self.logger.error(f"Failed to switch to window: {str(e)}")
            raise
    
    def get_window_handles(self) -> List[str]:
        """
        Get all window handles.
        
        Returns:
            List[str]: List of window handles
        """
        return self.get_driver().window_handles
    
    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            DriverManager: Self instance
        """
        self.initialize_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        
        Ensures driver is closed when exiting context.
        """
        self.quit_driver()


# Global driver instance for use across the framework
_driver_manager: Optional[DriverManager] = None


def get_driver_manager() -> DriverManager:
    """
    Get the global DriverManager instance.
    
    Creates a new instance if one doesn't exist.
    
    Returns:
        DriverManager: Global driver manager instance
    """
    global _driver_manager
    if _driver_manager is None:
        _driver_manager = DriverManager()
    return _driver_manager


def close_driver_manager() -> None:
    """
    Close the global DriverManager instance.
    
    Cleans up resources and resets the global instance.
    """
    global _driver_manager
    if _driver_manager is not None:
        _driver_manager.quit_driver()
        _driver_manager = None
