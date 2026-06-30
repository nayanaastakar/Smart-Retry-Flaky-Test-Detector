"""
Flaky Result Model - Module 3

This module defines the FlakyResult class for storing flaky test analysis results
including confidence score, root cause, and recommendation.
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


class FlakyResult:
    """
    Stores the result of flaky test analysis.
    
    This class captures:
    - Test name
    - Final status (PASS, FLAKY, FAILURE)
    - Exception type
    - Number of attempts made
    - Confidence score (0-100)
    - Root cause analysis
    - Recommended fix
    - Total execution time
    """
    
    def __init__(
        self,
        test_name: str,
        status: TestStatus,
        exception_type: Optional[str],
        attempts: int,
        confidence: int,
        root_cause: str,
        recommendation: str,
        execution_time: float
    ):
        """
        Initialize the FlakyResult.
        
        Args:
            test_name: Name of the test executed
            status: Final test status (PASS, FLAKY, FAILURE)
            exception_type: Type of Selenium exception encountered
            attempts: Number of execution attempts made
            confidence: Confidence score (0-100) for flaky classification
            root_cause: Root cause analysis of the failure
            recommendation: Suggested fix for the issue
            execution_time: Total execution time in seconds
        """
        self.test_name = test_name
        self.status = status
        self.exception_type = exception_type
        self.attempts = attempts
        self.confidence = confidence
        self.root_cause = root_cause
        self.recommendation = recommendation
        self.execution_time = execution_time
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convert the FlakyResult to a dictionary.
        
        Returns:
            dict: Dictionary representation of the result
        """
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "exception_type": self.exception_type,
            "attempts": self.attempts,
            "confidence": self.confidence,
            "root_cause": self.root_cause,
            "recommendation": self.recommendation,
            "execution_time": f"{self.execution_time:.2f} sec"
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
        if self.exception_type:
            result_str += f"\nException: {self.exception_type}"
        if self.confidence > 0:
            result_str += f"\nConfidence: {self.confidence}%"
        if self.root_cause:
            result_str += f"\nRoot Cause: {self.root_cause}"
        if self.recommendation:
            result_str += f"\nRecommendation: {self.recommendation}"
        return result_str
