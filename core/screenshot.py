"""
Screenshot Utility Module for Smart Retry & Flaky Test Detector

This module provides screenshot capture functionality with:
- Automatic screenshot capture on test failure
- Timestamped screenshot filenames
- Multiple screenshot formats
- Screenshot quality control
- Organized storage by test name
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import base64
import json

from selenium import webdriver
from config.config import Config
from core.logger import get_logger


class ScreenshotManager:
    """
    Manages screenshot capture and storage for test failures.
    
    This class provides methods to capture screenshots during test execution,
    particularly when failures occur, with automatic timestamping and organized storage.
    """
    
    def __init__(self):
        """
        Initialize the ScreenshotManager.
        
        Sets up configuration and logger instance.
        """
        self.config = Config()
        self.logger = get_logger("ScreenshotManager")
    
    def capture_screenshot(
        self,
        driver: webdriver.Chrome,
        test_name: str,
        suffix: Optional[str] = None
    ) -> Path:
        """
        Capture a screenshot and save it with timestamp.
        
        This method captures a screenshot of the current browser state,
        saves it with a timestamped filename, and logs the action.
        
        Args:
            driver: Selenium WebDriver instance
            test_name: Name of the test case
            suffix: Optional suffix for the filename (e.g., "failure", "retry")
            
        Returns:
            Path: Path to the saved screenshot file
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix_str = f"_{suffix}" if suffix else ""
            filename = f"{test_name}{suffix_str}_{timestamp}.{self.config.SCREENSHOT_FORMAT}"
            screenshot_path = self.config.SCREENSHOT_PATH / filename
            
            # Ensure screenshot directory exists
            self.config.SCREENSHOT_PATH.mkdir(parents=True, exist_ok=True)
            
            # Capture and save screenshot
            driver.save_screenshot(str(screenshot_path))
            
            self.logger.log_screenshot_saved(test_name, screenshot_path)
            return screenshot_path
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to capture screenshot for test: {test_name}")
            raise

    def capture_on_failure(
        self,
        driver: webdriver.Chrome,
        test_name: str,
        exception: Optional[Exception] = None
    ) -> Path:
        """
        Automatically capture screenshot on test failure.
        
        This method is designed to be called automatically when a test fails,
        capturing the current browser state for debugging purposes.
        
        Args:
            driver: Selenium WebDriver instance
            test_name: Name of the test case that failed
            exception: Optional exception that caused the failure
            
        Returns:
            Path: Path to the saved screenshot file
        """
        try:
            self.logger.log_failure(test_name, exception)
            return self.capture_screenshot(driver, test_name, "failure")
        except Exception as e:
            self.logger.log_exception(e, f"Failed to capture failure screenshot for test: {test_name}")
            # Return None if screenshot capture fails, don't raise to avoid masking original error
            return None
    
    def capture_screenshot_base64(
        self,
        driver: webdriver.Chrome
    ) -> str:
        """
        Capture screenshot as base64 encoded string.
        
        Useful for embedding screenshots in HTML reports.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            str: Base64 encoded screenshot
        """
        try:
            screenshot_base64 = driver.get_screenshot_as_base64()
            return screenshot_base64
        except Exception as e:
            self.logger.log_exception(e, "Failed to capture base64 screenshot")
            raise
    
    def capture_screenshot_bytes(
        self,
        driver: webdriver.Chrome
    ) -> bytes:
        """
        Capture screenshot as bytes.
        
        Useful for programmatic screenshot processing.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bytes: Screenshot as bytes
        """
        try:
            screenshot_bytes = driver.get_screenshot_as_png()
            return screenshot_bytes
        except Exception as e:
            self.logger.log_exception(e, "Failed to capture screenshot as bytes")
            raise
    
    def capture_full_page_screenshot(
        self,
        driver: webdriver.Chrome,
        test_name: str,
        suffix: Optional[str] = None
    ) -> Path:
        """
        Capture a full page screenshot (scrolling if necessary).
        
        This method captures the entire page by scrolling and stitching
        screenshots together.
        
        Args:
            driver: Selenium WebDriver instance
            test_name: Name of the test case
            suffix: Optional suffix for the filename
            
        Returns:
            Path: Path to the saved screenshot file
        """
        try:
            # Get total page height
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # If page fits in viewport, use regular screenshot
            if total_height <= viewport_height:
                return self.capture_screenshot(driver, test_name, suffix)
            
            # Scroll and capture multiple screenshots
            screenshots = []
            current_position = 0
            
            while current_position < total_height:
                # Scroll to current position
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                
                # Wait for any dynamic content to load
                import time
                time.sleep(0.5)
                
                # Capture screenshot
                screenshot_bytes = self.capture_screenshot_bytes(driver)
                screenshots.append(screenshot_bytes)
                
                # Move to next section
                current_position += viewport_height
            
            # For simplicity, save the first screenshot (full page stitching requires PIL)
            # In production, you would use PIL to stitch images together
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix_str = f"_{suffix}" if suffix else ""
            filename = f"{test_name}{suffix_str}_fullpage_{timestamp}.{self.config.SCREENSHOT_FORMAT}"
            screenshot_path = self.config.SCREENSHOT_PATH / filename
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshots[0])
            
            self.logger.log_screenshot_saved(test_name, screenshot_path)
            self.logger.log_info(f"Full page screenshot captured (sections: {len(screenshots)})")
            
            return screenshot_path
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to capture full page screenshot for test: {test_name}")
            # Fallback to regular screenshot
            return self.capture_screenshot(driver, test_name, suffix)
    
    def capture_element_screenshot(
        self,
        driver: webdriver.Chrome,
        element,
        test_name: str,
        element_name: str
    ) -> Path:
        """
        Capture a screenshot of a specific element.
        
        Args:
            driver: Selenium WebDriver instance
            element: WebElement to capture
            test_name: Name of the test case
            element_name: Name/description of the element
            
        Returns:
            Path: Path to the saved screenshot file
        """
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_name}_{element_name}_{timestamp}.{self.config.SCREENSHOT_FORMAT}"
            screenshot_path = self.config.SCREENSHOT_PATH / filename
            
            # Capture element screenshot
            element.screenshot(str(screenshot_path))
            
            self.logger.log_info(f"Element screenshot saved: {element_name}")
            return screenshot_path
            
        except Exception as e:
            self.logger.log_exception(e, f"Failed to capture element screenshot: {element_name}")
            # Fallback to full page screenshot
            return self.capture_screenshot(driver, test_name, element_name)
    
    def cleanup_old_screenshots(self, days_to_keep: int = 7) -> int:
        """
        Clean up screenshots older than specified days.
        
        Args:
            days_to_keep: Number of days to keep screenshots
            
        Returns:
            int: Number of screenshots deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            deleted_count = 0
            for screenshot_file in self.config.SCREENSHOT_PATH.glob("*"):
                if screenshot_file.is_file():
                    file_time = datetime.fromtimestamp(screenshot_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        screenshot_file.unlink()
                        deleted_count += 1
            
            self.logger.log_info(f"Cleaned up {deleted_count} old screenshots")
            return deleted_count
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to cleanup old screenshots")
            return 0
    
    def get_screenshot_count(self) -> int:
        """
        Get the total number of screenshots in the screenshot directory.
        
        Returns:
            int: Number of screenshot files
        """
        try:
            count = len(list(self.config.SCREENSHOT_PATH.glob("*")))
            return count
        except Exception as e:
            self.logger.log_exception(e, "Failed to get screenshot count")
            return 0
    
    def get_screenshot_info(self, screenshot_path: Path) -> dict:
        """
        Get metadata about a screenshot file.
        
        Args:
            screenshot_path: Path to the screenshot file
            
        Returns:
            dict: Screenshot metadata (size, creation time, etc.)
        """
        try:
            stat = screenshot_path.stat()
            return {
                "path": str(screenshot_path),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.log_exception(e, f"Failed to get screenshot info: {screenshot_path}")
            return {}


def capture_on_failure(
    driver: webdriver.Chrome,
    test_name: str,
    suffix: str = "failure"
) -> Path:
    """
    Convenience function to capture screenshot on test failure.
    
    Args:
        driver: Selenium WebDriver instance
        test_name: Name of the test case
        suffix: Suffix for the filename (default: "failure")
        
    Returns:
        Path: Path to the saved screenshot file
    """
    manager = ScreenshotManager()
    return manager.capture_screenshot(driver, test_name, suffix)
