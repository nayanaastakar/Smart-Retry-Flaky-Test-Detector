"""
Retry Result Module - Module 2

This module defines the RetryResult class for storing test execution results
including status, attempts, execution time, and exception details.
"""

from typing import Optional
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """
    Enumeration for test execution statuses.
    """
    PASS = "PASS"
    FLAKY = "FLAKY"
    FAILURE = "FAILURE"


class RetryResult:
    """
    Stores the result of a test execution with retry logic.
    
    This class captures:
    - Test name
    - Final status (PASS, FLAKY, FAILURE)
    - Number of attempts made
    - Total execution time
    - Exception details if failed
    """
    
    def __init__(
        self,
        test_name: str,
        status: TestStatus,
        attempts: int,
        execution_time: float,
        exception: Optional[str] = None
    ):
        """
        Initialize the RetryResult.
        
        Args:
            test_name: Name of the test executed
            status: Final test status (PASS, FLAKY, FAILURE)
            attempts: Number of execution attempts made
            execution_time: Total execution time in seconds
            exception: Exception message if test failed
        """
        self.test_name = test_name
        self.status = status
        self.attempts = attempts
        self.execution_time = execution_time
        self.exception = exception
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convert the RetryResult to a dictionary.
        
        Returns:
            dict: Dictionary representation of the result
        """
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "attempts": self.attempts,
            "execution_time": f"{self.execution_time:.2f} sec",
            "exception": self.exception
        }
    
    def __str__(self) -> str:
        """
        String representation of the result.
        
        Returns:
            str: Formatted string with result details
        """
        result_str = (
            f"Test: {self.test_name}\n"
            f"Status: {self.status.value}\n"
            f"Attempts: {self.attempts}\n"
            f"Execution Time: {self.execution_time:.2f} sec"
        )
        if self.exception:
            result_str += f"\nException: {self.exception}"
        return result_str
