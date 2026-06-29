"""
Configuration Module for Smart Retry & Flaky Test Detector

This module contains all configuration settings for the framework including:
- Browser settings
- Timeout configurations
- Retry settings
- Base URLs
- File paths
- AI API configurations
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Configuration class for the Smart Retry & Flaky Test Detector framework.
    
    This class centralizes all configuration parameters to ensure easy maintenance
    and modification of framework settings.
    """
    
    # Project Root Directory
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # Browser Configuration
    BROWSER: str = "chrome"
    HEADLESS_MODE: bool = False
    BROWSER_WINDOW_SIZE: str = "1920,1080"
    
    # Timeout Configurations (in seconds)
    IMPLICIT_WAIT: int = 10
    EXPLICIT_WAIT: int = 20
    PAGE_LOAD_TIMEOUT: int = 30
    SCRIPT_TIMEOUT: int = 30
    
    # Retry Configuration
    MAX_RETRY_COUNT: int = 3
    RETRY_DELAY: float = 2.0  # Delay between retries in seconds
    
    # Base URLs for Test Applications
    BASE_URL: str = "https://www.saucedemo.com"
    SAUCE_DEMO_URL: str = "https://www.saucedemo.com"
    AUTOMATION_EXERCISE_URL: str = "https://automationexercise.com"
    HEROKUAPP_URL: str = "https://the-internet.herokuapp.com"
    
    # File Paths
    SCREENSHOT_PATH: Path = PROJECT_ROOT / "screenshots"
    LOG_PATH: Path = PROJECT_ROOT / "logs"
    REPORT_PATH: Path = PROJECT_ROOT / "reports"
    CONFIG_PATH: Path = PROJECT_ROOT / "config"
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 1000
    
    # Ollama Configuration (for local AI)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TEMPERATURE: float = 0.3
    
    # AI Analysis Settings
    AI_ANALYSIS_ENABLED: bool = True
    AI_ANALYSIS_TIMEOUT: int = 30  # seconds
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_NAME: str = "test_execution.log"
    
    # Screenshot Configuration
    SCREENSHOT_FORMAT: str = "png"
    SCREENSHOT_QUALITY: int = 90
    
    # Console Logs Configuration
    CAPTURE_CONSOLE_LOGS: bool = True
    CONSOLE_LOG_TYPES: list = ["log", "error", "warning", "info"]
    
    # Report Configuration
    REPORT_TITLE: str = "Smart Retry & Flaky Test Detector Report"
    REPORT_TEMPLATE: str = "default"
    INCLUDE_SCREENSHOTS: bool = True
    INCLUDE_CONSOLE_LOGS: bool = True
    INCLUDE_AI_ANALYSIS: bool = True
    
    # Test Configuration
    TEST_PARALLEL_EXECUTION: bool = False
    TEST_WORKERS: int = 2
    
    # Flaky Test Detection Thresholds
    FLAKY_DETECTION_ENABLED: bool = True
    FLAKY_THRESHOLD: int = 2  # Number of retries to consider as flaky
    
    # Exception Classification Patterns
    TIMEOUT_EXCEPTIONS: list = [
        "TimeoutException",
        "TimeoutError"
    ]
    
    ELEMENT_NOT_FOUND_EXCEPTIONS: list = [
        "NoSuchElementException",
        "NoSuchFrameException"
    ]
    
    STALE_ELEMENT_EXCEPTIONS: list = [
        "StaleElementReferenceException"
    ]
    
    ELEMENT_INTERACTION_EXCEPTIONS: list = [
        "ElementClickInterceptedException",
        "ElementNotInteractableException",
        "ElementNotSelectableException"
    ]
    
    NETWORK_EXCEPTIONS: list = [
        "WebDriverException",
        "ConnectionError"
    ]
    
    @classmethod
    def create_directories(cls) -> None:
        """
        Create all necessary directories if they don't exist.
        
        This method ensures that all required directories for storing
        screenshots, logs, and reports are created before test execution.
        """
        directories = [
            cls.SCREENSHOT_PATH,
            cls.LOG_PATH,
            cls.REPORT_PATH
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_screenshot_path(cls, test_name: str) -> Path:
        """
        Generate a unique screenshot path for a given test.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Path object for the screenshot file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.{cls.SCREENSHOT_FORMAT}"
        return cls.SCREENSHOT_PATH / filename
    
    @classmethod
    def get_log_path(cls, test_name: str) -> Path:
        """
        Generate a unique log path for a given test.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Path object for the log file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.log"
        return cls.LOG_PATH / filename
    
    @classmethod
    def get_console_log_path(cls, test_name: str) -> Path:
        """
        Generate a unique console log path for a given test.
        
        Args:
            test_name: Name of the test case
            
        Returns:
            Path object for the console log file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_console_{timestamp}.txt"
        return cls.LOG_PATH / filename
    
    @classmethod
    def get_report_path(cls) -> Path:
        """
        Generate a report path with timestamp.
        
        Returns:
            Path object for the HTML report file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.html"
        return cls.REPORT_PATH / filename
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate the configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Check if AI analysis is enabled but API key is missing
        if cls.AI_ANALYSIS_ENABLED and not cls.OPENAI_API_KEY:
            print("Warning: AI Analysis is enabled but OPENAI_API_KEY is not set.")
            print("Set OPENAI_API_KEY environment variable or disable AI analysis.")
            return False
        
        return True


# Initialize configuration and create directories
Config.create_directories()
