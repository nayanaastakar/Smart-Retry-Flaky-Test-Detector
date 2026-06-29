"""
Flaky Test Detector Module for Smart Retry & Flaky Test Detector

This module provides flaky test detection with:
- Classification of flaky vs genuine failures
- Detection of common flaky patterns
- Exception type analysis
- Network issue detection
- Dynamic loading detection
- Animation delay detection
"""

from typing import Dict, List, Optional
from enum import Enum
import traceback

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException
)

from config.config import Config
from core.logger import get_logger
from core.retry_engine import RetryResult, TestStatus


class FlakyClassification(Enum):
    """
    Enumeration of flaky test classifications.
    
    - TIMEOUT: Test failed due to timeout (likely timing issue)
    - ELEMENT_NOT_FOUND: Element not found (dynamic loading)
    - STALE_ELEMENT: Stale element reference (DOM update)
    - ELEMENT_NOT_INTERACTABLE: Element not interactable (animation/overlay)
    - NETWORK_ISSUE: Network-related failure
    - TEMPORARY_FAILURE: Temporary failure that resolved on retry
    - GENUINE_FAILURE: Genuine application bug
    - UNKNOWN: Unknown cause
    """
    TIMEOUT = "Timeout Issue"
    ELEMENT_NOT_FOUND = "Element Not Found"
    STALE_ELEMENT = "Stale Element Reference"
    ELEMENT_NOT_INTERACTABLE = "Element Not Interactable"
    NETWORK_ISSUE = "Network Issue"
    TEMPORARY_FAILURE = "Temporary Failure"
    GENUINE_FAILURE = "Genuine Failure"
    UNKNOWN = "Unknown Cause"


class FlakyTestDetector:
    """
    Detector for identifying flaky tests vs genuine failures.
    
    This class analyzes test execution results and exceptions to classify
    whether a test failure is due to flakiness or a genuine application bug.
    """
    
    def __init__(self):
        """
        Initialize the FlakyTestDetector.
        
        Sets up configuration and logger instance.
        """
        self.config = Config()
        self.logger = get_logger("FlakyTestDetector")
    
    def analyze_test_result(self, retry_result: RetryResult) -> Dict:
        """
        Analyze a test result to determine if it's flaky.
        
        This method examines the retry result, exception types, and
        execution patterns to classify the test failure.
        
        Args:
            retry_result: Result from retry engine execution
            
        Returns:
            Dict: Analysis results including classification and confidence
        """
        analysis = {
            "test_status": retry_result.status.value,
            "is_flaky": retry_result.status == TestStatus.FLAKY,
            "classification": None,
            "root_cause": None,
            "confidence_score": 0.0,
            "suggested_fix": None,
            "exception_types": [type(e).__name__ for e in retry_result.exceptions],
            "retry_count": retry_result.attempts - 1
        }
        
        # If test passed on first attempt, it's not flaky
        if retry_result.status == TestStatus.PASS:
            analysis["classification"] = FlakyClassification.GENUINE_FAILURE.value
            analysis["root_cause"] = "Test passed on first attempt - no flakiness detected"
            analysis["confidence_score"] = 1.0
            return analysis
        
        # If test failed after all retries, analyze exceptions
        if retry_result.status == TestStatus.FAILURE:
            analysis["classification"] = self._classify_failure(retry_result.exceptions)
            analysis["root_cause"] = self._determine_root_cause(retry_result.exceptions)
            analysis["confidence_score"] = self._calculate_confidence(retry_result)
            analysis["suggested_fix"] = self._suggest_fix(analysis["classification"])
            return analysis
        
        # If test passed after retry, it's flaky
        if retry_result.status == TestStatus.FLAKY:
            analysis["classification"] = self._classify_flaky(retry_result.exceptions)
            analysis["root_cause"] = self._determine_flaky_root_cause(retry_result.exceptions)
            analysis["confidence_score"] = 0.9  # High confidence for flaky tests
            analysis["suggested_fix"] = self._suggest_fix(analysis["classification"])
            return analysis
        
        return analysis
    
    def _classify_flaky(self, exceptions: List[Exception]) -> str:
        """
        Classify a flaky test based on exception types.
        
        Args:
            exceptions: List of exceptions encountered
            
        Returns:
            str: Classification of the flaky behavior
        """
        if not exceptions:
            return FlakyClassification.TEMPORARY_FAILURE.value
        
        # Analyze exception types
        exception_types = [type(e).__name__ for e in exceptions]
        
        # Check for timeout exceptions
        if any(exc in self.config.TIMEOUT_EXCEPTIONS for exc in exception_types):
            return FlakyClassification.TIMEOUT.value
        
        # Check for element not found exceptions
        if any(exc in self.config.ELEMENT_NOT_FOUND_EXCEPTIONS for exc in exception_types):
            return FlakyClassification.ELEMENT_NOT_FOUND.value
        
        # Check for stale element exceptions
        if any(exc in self.config.STALE_ELEMENT_EXCEPTIONS for exc in exception_types):
            return FlakyClassification.STALE_ELEMENT.value
        
        # Check for element interaction exceptions
        if any(exc in self.config.ELEMENT_INTERACTION_EXCEPTIONS for exc in exception_types):
            return FlakyClassification.ELEMENT_NOT_INTERACTABLE.value
        
        # Check for network exceptions
        if any(exc in self.config.NETWORK_EXCEPTIONS for exc in exception_types):
            return FlakyClassification.NETWORK_ISSUE.value
        
        # Default to temporary failure
        return FlakyClassification.TEMPORARY_FAILURE.value
    
    def _classify_failure(self, exceptions: List[Exception]) -> str:
        """
        Classify a genuine failure based on exception types.
        
        Args:
            exceptions: List of exceptions encountered
            
        Returns:
            str: Classification of the failure
        """
        if not exceptions:
            return FlakyClassification.GENUINE_FAILURE.value
        
        exception_types = [type(e).__name__ for e in exceptions]
        
        # If the same exception occurs consistently, it's likely a genuine failure
        if len(set(exception_types)) == 1:
            return FlakyClassification.GENUINE_FAILURE.value
        
        # If different exceptions occur, it might be environmental
        if len(set(exception_types)) > 1:
            return FlakyClassification.NETWORK_ISSUE.value
        
        return FlakyClassification.GENUINE_FAILURE.value
    
    def _determine_root_cause(self, exceptions: List[Exception]) -> str:
        """
        Determine the root cause of a failure.
        
        Args:
            exceptions: List of exceptions encountered
            
        Returns:
            str: Root cause description
        """
        if not exceptions:
            return "No exceptions captured"
        
        # Get the most recent exception
        latest_exception = exceptions[-1]
        exception_type = type(latest_exception).__name__
        exception_message = str(latest_exception)
        
        root_causes = {
            "TimeoutException": "Element or operation took longer than expected to complete",
            "NoSuchElementException": "Element could not be found in the DOM",
            "StaleElementReferenceException": "Element is no longer attached to the DOM",
            "ElementClickInterceptedException": "Element is obscured by another element",
            "ElementNotInteractableException": "Element is not in a state to be interacted with",
            "WebDriverException": "General WebDriver error occurred"
        }
        
        return root_causes.get(exception_type, f"{exception_type}: {exception_message}")
    
    def _determine_flaky_root_cause(self, exceptions: List[Exception]) -> str:
        """
        Determine the root cause of a flaky test.
        
        Args:
            exceptions: List of exceptions encountered
            
        Returns:
            str: Root cause description
        """
        if not exceptions:
            return "Temporary issue that resolved on retry"
        
        exception_types = [type(e).__name__ for e in exceptions]
        
        causes = {
            "TimeoutException": "Timing issue - element loaded slowly on first attempt",
            "NoSuchElementException": "Dynamic loading - element not immediately available",
            "StaleElementReferenceException": "DOM updated between test execution and retry",
            "ElementClickInterceptedException": "Animation or overlay blocked interaction temporarily",
            "ElementNotInteractableException": "Element state changed temporarily (e.g., disabled)",
            "WebDriverException": "Temporary network or browser issue"
        }
        
        for exc_type in exception_types:
            if exc_type in causes:
                return causes[exc_type]
        
        return "Temporary issue that resolved on retry"
    
    def _calculate_confidence(self, retry_result: RetryResult) -> float:
        """
        Calculate confidence score for the classification.
        
        Args:
            retry_result: Result from retry engine execution
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # If test passed after retry, high confidence it's flaky
        if retry_result.status == TestStatus.FLAKY:
            return 0.9
        
        # If test failed consistently, high confidence it's genuine
        if retry_result.status == TestStatus.FAILURE:
            # Check if same exception occurred
            exception_types = [type(e).__name__ for e in retry_result.exceptions]
            if len(set(exception_types)) == 1:
                return 0.85
            else:
                return 0.6
        
        # If test passed on first attempt, it's not flaky
        if retry_result.status == TestStatus.PASS:
            return 1.0
        
        return 0.5
    
    def _suggest_fix(self, classification: str) -> str:
        """
        Suggest a fix based on classification.
        
        Args:
            classification: Classification of the issue
            
        Returns:
            str: Suggested fix
        """
        fixes = {
            FlakyClassification.TIMEOUT.value: "Increase explicit wait timeout or use WebDriverWait with expected conditions",
            FlakyClassification.ELEMENT_NOT_FOUND.value: "Add explicit wait for element presence or use dynamic locators",
            FlakyClassification.STALE_ELEMENT.value: "Re-find element before interaction or use stable locators",
            FlakyClassification.ELEMENT_NOT_INTERACTABLE.value: "Wait for element to be clickable or check for overlays",
            FlakyClassification.NETWORK_ISSUE.value: "Add retry logic for network operations or check network stability",
            FlakyClassification.TEMPORARY_FAILURE.value: "Implement retry mechanism or add appropriate waits",
            FlakyClassification.GENUINE_FAILURE.value: "Fix the application bug or update test expectations"
        }
        
        return fixes.get(classification, "Review test implementation and application state")
    
    def detect_flaky_patterns(self, exceptions: List[Exception]) -> List[str]:
        """
        Detect common flaky test patterns from exceptions.
        
        Args:
            exceptions: List of exceptions encountered
            
        Returns:
            List[str]: List of detected flaky patterns
        """
        patterns = []
        
        if not exceptions:
            return patterns
        
        exception_types = [type(e).__name__ for e in exceptions]
        
        # Pattern: Element not interactable
        if any(exc in self.config.ELEMENT_INTERACTION_EXCEPTIONS for exc in exception_types):
            patterns.append("Element interaction blocked (animation/overlay)")
        
        # Pattern: Timeout
        if any(exc in self.config.TIMEOUT_EXCEPTIONS for exc in exception_types):
            patterns.append("Timeout occurred (slow loading)")
        
        # Pattern: Element not found
        if any(exc in self.config.ELEMENT_NOT_FOUND_EXCEPTIONS for exc in exception_types):
            patterns.append("Element not found (dynamic loading)")
        
        # Pattern: Stale element
        if any(exc in self.config.STALE_ELEMENT_EXCEPTIONS for exc in exception_types):
            patterns.append("Stale element reference (DOM update)")
        
        # Pattern: Network issue
        if any(exc in self.config.NETWORK_EXCEPTIONS for exc in exception_types):
            patterns.append("Network issue (temporary connectivity)")
        
        # Pattern: Multiple different exceptions
        if len(set(exception_types)) > 1:
            patterns.append("Multiple exception types (environmental instability)")
        
        return patterns
    
    def get_flaky_statistics(self, test_results: List[Dict]) -> Dict:
        """
        Calculate flaky test statistics across multiple test results.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            Dict: Flaky test statistics
        """
        total_tests = len(test_results)
        flaky_tests = sum(1 for r in test_results if r.get("is_flaky", False))
        failed_tests = sum(1 for r in test_results if r.get("test_status") == TestStatus.FAILURE.value)
        passed_tests = sum(1 for r in test_results if r.get("test_status") == TestStatus.PASS.value)
        
        return {
            "total_tests": total_tests,
            "flaky_tests": flaky_tests,
            "failed_tests": failed_tests,
            "passed_tests": passed_tests,
            "flaky_percentage": round((flaky_tests / total_tests * 100) if total_tests > 0 else 0, 2),
            "pass_percentage": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
            "fail_percentage": round((failed_tests / total_tests * 100) if total_tests > 0 else 0, 2)
        }


def analyze_flakiness(retry_result: RetryResult) -> Dict:
    """
    Convenience function to analyze test flakiness.
    
    Args:
        retry_result: Result from retry engine execution
        
    Returns:
        Dict: Analysis results
    """
    detector = FlakyTestDetector()
    return detector.analyze_test_result(retry_result)
