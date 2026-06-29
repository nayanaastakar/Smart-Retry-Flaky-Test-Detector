"""
Logger Module for Smart Retry & Flaky Test Detector

This module provides centralized logging functionality with:
- Timestamped log entries
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console logging
- Test-specific log files
- Structured log format
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

from config.config import Config


class TestLogger:
    """
    Custom logger for test execution tracking.
    
    This class provides methods to log various test events including:
    - Test start/finish
    - Retry attempts
    - Failures and successes
    - Exceptions
    - AI analysis events
    """
    
    def __init__(self, test_name: Optional[str] = None):
        """
        Initialize the TestLogger.
        
        Args:
            test_name: Name of the test case (optional)
        """
        self.config = Config()
        self.test_name = test_name or "general"
        self.logger = self._setup_logger()
        self.test_start_time: Optional[datetime] = None
        self.test_end_time: Optional[datetime] = None
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger with file and console handlers.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logger
        logger = logging.getLogger(f"{self.__class__.__name__}.{self.test_name}")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatter
        formatter = logging.Formatter(
            self.config.LOG_FORMAT,
            datefmt=self.config.LOG_DATE_FORMAT
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for general log
        general_log_path = self.config.LOG_PATH / self.config.LOG_FILE_NAME
        file_handler = logging.FileHandler(general_log_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Test-specific file handler
        test_log_path = self.config.get_log_path(self.test_name)
        test_file_handler = logging.FileHandler(test_log_path, mode='w')
        test_file_handler.setLevel(logging.DEBUG)
        test_file_handler.setFormatter(formatter)
        logger.addHandler(test_file_handler)
        
        return logger
    
    def log_test_start(self, test_name: str) -> None:
        """
        Log the start of a test execution.
        
        Args:
            test_name: Name of the test being started
        """
        self.test_start_time = datetime.now()
        self.logger.info("=" * 80)
        self.logger.info(f"TEST STARTED: {test_name}")
        self.logger.info(f"Timestamp: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
    
    def log_test_finish(self, test_name: str, status: str) -> None:
        """
        Log the completion of a test execution.
        
        Args:
            test_name: Name of the test being finished
            status: Final status of the test (PASS, FAIL, FLAKY)
        """
        self.test_end_time = datetime.now()
        duration = (self.test_end_time - self.test_start_time).total_seconds() if self.test_start_time else 0
        
        self.logger.info("=" * 80)
        self.logger.info(f"TEST FINISHED: {test_name}")
        self.logger.info(f"Status: {status}")
        self.logger.info(f"Timestamp: {self.test_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info("=" * 80)
    
    def log_retry(self, test_name: str, retry_count: int, max_retries: int) -> None:
        """
        Log a retry attempt.
        
        Args:
            test_name: Name of the test being retried
            retry_count: Current retry attempt number
            max_retries: Maximum number of retry attempts
        """
        self.logger.warning(f"RETRY ATTEMPT {retry_count}/{max_retries} for test: {test_name}")
    
    def log_failure(self, test_name: str, exception: Exception) -> None:
        """
        Log a test failure with exception details.
        
        Args:
            test_name: Name of the test that failed
            exception: Exception that caused the failure
        """
        self.logger.error(f"TEST FAILED: {test_name}")
        self.logger.error(f"Exception Type: {type(exception).__name__}")
        self.logger.error(f"Exception Message: {str(exception)}")
        self.logger.error(f"Stack Trace:", exc_info=True)
    
    def log_success(self, test_name: str) -> None:
        """
        Log a successful test execution.
        
        Args:
            test_name: Name of the test that passed
        """
        self.logger.info(f"TEST PASSED: {test_name}")
    
    def log_flaky_detected(self, test_name: str, retry_count: int) -> None:
        """
        Log detection of a flaky test.
        
        Args:
            test_name: Name of the flaky test
            retry_count: Number of retries before success
        """
        self.logger.warning(f"FLAKY TEST DETECTED: {test_name}")
        self.logger.warning(f"Test passed after {retry_count} retry attempts")
    
    def log_screenshot_saved(self, test_name: str, screenshot_path: Path) -> None:
        """
        Log that a screenshot was saved.
        
        Args:
            test_name: Name of the test
            screenshot_path: Path where screenshot was saved
        """
        self.logger.info(f"Screenshot saved for test '{test_name}': {screenshot_path}")
    
    def log_console_logs_saved(self, test_name: str, log_path: Path) -> None:
        """
        Log that browser console logs were saved.
        
        Args:
            test_name: Name of the test
            log_path: Path where console logs were saved
        """
        self.logger.info(f"Console logs saved for test '{test_name}': {log_path}")
    
    def log_ai_analysis_start(self, test_name: str) -> None:
        """
        Log the start of AI analysis.
        
        Args:
            test_name: Name of the test being analyzed
        """
        self.logger.info(f"AI Analysis started for test: {test_name}")
    
    def log_ai_analysis_finish(self, test_name: str, result: dict) -> None:
        """
        Log the completion of AI analysis.
        
        Args:
            test_name: Name of the test analyzed
            result: AI analysis result dictionary
        """
        self.logger.info(f"AI Analysis completed for test: {test_name}")
        self.logger.info(f"Classification: {result.get('classification', 'N/A')}")
        self.logger.info(f"Root Cause: {result.get('root_cause', 'N/A')}")
        self.logger.info(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
    
    def log_exception(self, exception: Exception, context: str = "") -> None:
        """
        Log an exception with optional context.
        
        Args:
            exception: Exception to log
            context: Additional context information
        """
        self.logger.error(f"Exception occurred: {context}")
        self.logger.error(f"Exception Type: {type(exception).__name__}")
        self.logger.error(f"Exception Message: {str(exception)}")
        self.logger.error(f"Stack Trace:", exc_info=True)
    
    def log_info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: Message to log
        """
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Warning message to log
        """
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Error message to log
        """
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Debug message to log
        """
        self.logger.debug(message)
    
    def log_custom(self, level: str, message: str) -> None:
        """
        Log a message at a custom level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Message to log
        """
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(message)
    
    def get_test_duration(self) -> float:
        """
        Get the duration of the test execution.
        
        Returns:
            float: Duration in seconds
        """
        if self.test_start_time and self.test_end_time:
            return (self.test_end_time - self.test_start_time).total_seconds()
        return 0.0
    
    def save_log_summary(self, summary: dict) -> Path:
        """
        Save a summary of test execution as JSON.
        
        Args:
            summary: Dictionary containing test summary
            
        Returns:
            Path: Path to the saved summary file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = self.config.LOG_PATH / f"summary_{timestamp}.json"
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Test summary saved to: {summary_path}")
        return summary_path


class LogManager:
    """
    Manager for handling multiple test loggers.
    
    This class provides centralized management of loggers for different tests.
    """
    
    _loggers: dict = {}
    
    @classmethod
    def get_logger(cls, test_name: str) -> TestLogger:
        """
        Get or create a logger for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            TestLogger: Logger instance for the test
        """
        if test_name not in cls._loggers:
            cls._loggers[test_name] = TestLogger(test_name)
        return cls._loggers[test_name]
    
    @classmethod
    def remove_logger(cls, test_name: str) -> None:
        """
        Remove a logger from the manager.
        
        Args:
            test_name: Name of the test logger to remove
        """
        if test_name in cls._loggers:
            del cls._loggers[test_name]
    
    @classmethod
    def clear_all_loggers(cls) -> None:
        """
        Clear all loggers from the manager.
        """
        cls._loggers.clear()
    
    @classmethod
    def get_all_logger_names(cls) -> list:
        """
        Get names of all active loggers.
        
        Returns:
            list: List of logger names
        """
        return list(cls._loggers.keys())


def get_logger(test_name: str = "general") -> TestLogger:
    """
    Convenience function to get a logger instance.
    
    Args:
        test_name: Name of the test (default: "general")
        
    Returns:
        TestLogger: Logger instance
    """
    return LogManager.get_logger(test_name)
