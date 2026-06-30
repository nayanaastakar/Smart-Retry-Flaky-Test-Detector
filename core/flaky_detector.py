"""
Flaky Test Detector Module - Module 3

This module provides intelligent flaky test detection with:
- Classification of flaky vs genuine failures based on retry behavior
- Selenium exception type analysis
- Confidence score generation
- Root cause analysis
- Automated fix recommendations
"""

from typing import Optional
from enum import Enum

from models.flaky_result import FlakyResult, TestStatus
from utils.retry_result import RetryResult


class FlakyDetector:
    """
    Detector for identifying flaky tests vs genuine failures.
    
    This class analyzes test execution results and exceptions to classify
    whether a test failure is due to flakiness or a genuine application bug.
    It provides confidence scores, root cause analysis, and recommendations.
    """
    
    def __init__(self):
        """
        Initialize the FlakyDetector.
        """
        # Exception confidence scores
        self.exception_confidence = {
            "TimeoutException": 95,
            "StaleElementReferenceException": 90,
            "ElementClickInterceptedException": 88,
            "ElementNotInteractableException": 85,
            "WebDriverException": 70,
            "NoSuchElementException": 40,
            "AssertionError": 10,
            "Exception": 50
        }
        
        # Root cause mappings
        self.root_causes = {
            "TimeoutException": "Slow page loading",
            "StaleElementReferenceException": "DOM refreshed",
            "ElementClickInterceptedException": "Popup blocked click",
            "ElementNotInteractableException": "Element not ready",
            "WebDriverException": "Browser/network issue",
            "NoSuchElementException": "Locator missing",
            "AssertionError": "Application returned unexpected result",
            "Exception": "Unknown issue"
        }
        
        # Recommendation mappings
        self.recommendations = {
            "TimeoutException": "Increase Explicit Wait",
            "StaleElementReferenceException": "Locate element again",
            "ElementClickInterceptedException": "Wait until clickable",
            "ElementNotInteractableException": "Wait for element state",
            "WebDriverException": "Check browser/network",
            "NoSuchElementException": "Verify locator",
            "AssertionError": "Check application logic",
            "Exception": "Review test and application"
        }
    
    def analyze(self, retry_result: RetryResult, test_name: str) -> FlakyResult:
        """
        Analyze a retry result to determine flaky status.
        
        This method examines the retry result, exception types, and
        execution patterns to classify the test failure.
        
        Args:
            retry_result: Result from retry engine execution
            test_name: Name of the test
            
        Returns:
            FlakyResult: Analysis result with confidence, root cause, and recommendation
        """
        print("Analyzing Result...")
        
        # Extract exception type
        exception_type = self._extract_exception_type(retry_result.exception)
        print(f"Exception: {exception_type}")
        
        # Classify based on retry behavior
        status = self._classify(retry_result)
        print(f"Classification: {status.value}")
        
        # Calculate confidence score
        confidence = self._calculate_confidence(exception_type, retry_result)
        print(f"Confidence: {confidence}%")
        
        # Determine root cause
        root_cause = self._determine_root_cause(exception_type)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(exception_type)
        print(f"Recommendation: {recommendation}")
        
        print("Execution Completed")
        
        return FlakyResult(
            test_name=test_name,
            status=status,
            exception_type=exception_type,
            attempts=retry_result.attempts,
            confidence=confidence,
            root_cause=root_cause,
            recommendation=recommendation,
            execution_time=retry_result.execution_time
        )
    
    def _extract_exception_type(self, exception_msg: Optional[str]) -> str:
        """
        Extract the exception type from the exception message.
        
        Args:
            exception_msg: Exception message string
            
        Returns:
            str: Exception type name
        """
        if not exception_msg:
            return None
        
        # Check for common Selenium exceptions
        for exc_type in self.exception_confidence.keys():
            if exc_type in exception_msg:
                return exc_type
        
        return "Exception"
    
    def _classify(self, retry_result: RetryResult) -> TestStatus:
        """
        Classify the test based on retry behavior.
        
        Args:
            retry_result: Result from retry engine execution
            
        Returns:
            TestStatus: PASS, FLAKY, or FAILURE
        """
        # Use the status from retry result
        return retry_result.status
    
    def _calculate_confidence(self, exception_type: Optional[str], retry_result: RetryResult) -> int:
        """
        Calculate confidence score for the classification.
        
        Args:
            exception_type: Type of exception encountered
            retry_result: Result from retry engine execution
            
        Returns:
            int: Confidence score (0-100)
        """
        # If test passed on first attempt, high confidence it's not flaky
        if retry_result.status == TestStatus.PASS:
            return 100
        
        # If test passed after retry, high confidence it's flaky
        if retry_result.status == TestStatus.FLAKY:
            base_confidence = self.exception_confidence.get(exception_type, 80)
            return min(base_confidence, 95)
        
        # If test failed all retries, confidence depends on exception type
        if retry_result.status == TestStatus.FAILURE:
            return self.exception_confidence.get(exception_type, 50)
        
        return 50
    
    def _determine_root_cause(self, exception_type: Optional[str]) -> str:
        """
        Determine the root cause of the failure.
        
        Args:
            exception_type: Type of exception encountered
            
        Returns:
            str: Root cause description
        """
        return self.root_causes.get(exception_type, "Unknown issue")
    
    def _generate_recommendation(self, exception_type: Optional[str]) -> str:
        """
        Generate a recommendation for fixing the issue.
        
        Args:
            exception_type: Type of exception encountered
            
        Returns:
            str: Recommended fix
        """
        return self.recommendations.get(exception_type, "Review test implementation")
    
    def is_flaky(self, retry_result: RetryResult) -> bool:
        """
        Determine if a test result indicates flakiness.
        
        Args:
            retry_result: Result from retry engine execution
            
        Returns:
            bool: True if test is flaky, False otherwise
        """
        return retry_result.status == TestStatus.FLAKY
    
    def should_retry(self, exception_type: Optional[str]) -> bool:
        """
        Determine if an exception should trigger a retry.
        
        Args:
            exception_type: Type of exception encountered
            
        Returns:
            bool: True if exception is retryable
        """
        # Most Selenium exceptions are retryable except AssertionError
        if exception_type == "AssertionError":
            return False
        return True
