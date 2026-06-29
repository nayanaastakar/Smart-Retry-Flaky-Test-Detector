"""
Retry Engine Module for Smart Retry & Flaky Test Detector

This module provides intelligent retry functionality with:
- Automatic test retry on failure
- Configurable retry count and delay
- Test status classification (PASS, FLAKY, FAILURE)
- Retry tracking and logging
- Integration with flaky detector
"""

import time
from typing import Callable, Any, Optional, Dict
from enum import Enum
from functools import wraps

from config.config import Config
from core.logger import get_logger


class TestStatus(Enum):
    """
    Enumeration of possible test statuses.
    
    - PASS: Test passed on first attempt
    - FLAKY: Test failed initially but passed after retry
    - FAILURE: Test failed after all retry attempts
    """
    PASS = "PASS"
    FLAKY = "FLAKY"
    FAILURE = "FAILURE"


class RetryResult:
    """
    Data class to store retry execution results.
    
    Attributes:
        status: Final test status (PASS, FLAKY, FAILURE)
        attempts: Number of execution attempts
        first_attempt_passed: Whether first attempt passed
        final_attempt_passed: Whether final attempt passed
        exceptions: List of exceptions encountered
        execution_time: Total execution time in seconds
    """
    
    def __init__(
        self,
        status: TestStatus,
        attempts: int,
        first_attempt_passed: bool,
        final_attempt_passed: bool,
        exceptions: list,
        execution_time: float
    ):
        self.status = status
        self.attempts = attempts
        self.first_attempt_passed = first_attempt_passed
        self.final_attempt_passed = final_attempt_passed
        self.exceptions = exceptions
        self.execution_time = execution_time
    
    def to_dict(self) -> Dict:
        """
        Convert retry result to dictionary.
        
        Returns:
            Dict: Dictionary representation of the result
        """
        return {
            "status": self.status.value,
            "attempts": self.attempts,
            "first_attempt_passed": self.first_attempt_passed,
            "final_attempt_passed": self.final_attempt_passed,
            "exceptions": [str(e) for e in self.exceptions],
            "execution_time": self.execution_time
        }


class RetryEngine:
    """
    Intelligent retry engine for test execution.
    
    This class implements the retry logic:
    1. Run test
    2. If pass → status = PASS
    3. If fail → retry
    4. If pass after retry → status = FLAKY
    5. If fail after all retries → status = FAILURE
    """
    
    def __init__(self, max_retries: Optional[int] = None, retry_delay: Optional[float] = None):
        """
        Initialize the RetryEngine.
        
        Args:
            max_retries: Maximum number of retry attempts (uses config if not provided)
            retry_delay: Delay between retries in seconds (uses config if not provided)
        """
        self.config = Config()
        self.max_retries = max_retries or self.config.MAX_RETRY_COUNT
        self.retry_delay = retry_delay or self.config.RETRY_DELAY
        self.logger = get_logger("RetryEngine")
    
    def execute_with_retry(
        self,
        test_func: Callable,
        test_name: str,
        *args,
        **kwargs
    ) -> RetryResult:
        """
        Execute a test function with retry logic.
        
        This method implements the core retry algorithm:
        - Execute the test function
        - If it fails, retry up to max_retries times
        - Classify the test based on retry behavior
        - Track all exceptions and execution time
        
        Args:
            test_func: The test function to execute
            test_name: Name of the test case
            *args: Positional arguments to pass to test_func
            **kwargs: Keyword arguments to pass to test_func
            
        Returns:
            RetryResult: Result object with status and metadata
        """
        import time
        start_time = time.time()
        exceptions = []
        attempts = 0
        first_attempt_passed = False
        final_attempt_passed = False
        
        self.logger.log_test_start(test_name)
        
        # First attempt
        attempts += 1
        try:
            self.logger.log_info(f"Attempt 1/{self.max_retries + 1} for test: {test_name}")
            result = test_func(*args, **kwargs)
            first_attempt_passed = True
            final_attempt_passed = True
            
            execution_time = time.time() - start_time
            self.logger.log_success(test_name)
            self.logger.log_test_finish(test_name, TestStatus.PASS.value)
            
            return RetryResult(
                status=TestStatus.PASS,
                attempts=attempts,
                first_attempt_passed=first_attempt_passed,
                final_attempt_passed=final_attempt_passed,
                exceptions=exceptions,
                execution_time=execution_time
            )
            
        except Exception as e:
            exceptions.append(e)
            self.logger.log_failure(test_name, e)
            self.logger.log_info(f"First attempt failed for test: {test_name}")
        
        # Retry attempts
        for retry_count in range(1, self.max_retries + 1):
            attempts += 1
            
            # Log retry attempt
            self.logger.log_retry(test_name, retry_count, self.max_retries)
            
            # Wait before retry
            if self.retry_delay > 0:
                self.logger.log_debug(f"Waiting {self.retry_delay} seconds before retry...")
                time.sleep(self.retry_delay)
            
            # Execute retry
            try:
                self.logger.log_info(f"Retry attempt {retry_count}/{self.max_retries} for test: {test_name}")
                result = test_func(*args, **kwargs)
                final_attempt_passed = True
                
                execution_time = time.time() - start_time
                self.logger.log_success(test_name)
                self.logger.log_flaky_detected(test_name, retry_count)
                self.logger.log_test_finish(test_name, TestStatus.FLAKY.value)
                
                return RetryResult(
                    status=TestStatus.FLAKY,
                    attempts=attempts,
                    first_attempt_passed=first_attempt_passed,
                    final_attempt_passed=final_attempt_passed,
                    exceptions=exceptions,
                    execution_time=execution_time
                )
                
            except Exception as e:
                exceptions.append(e)
                self.logger.log_failure(test_name, e)
                self.logger.log_info(f"Retry attempt {retry_count} failed for test: {test_name}")
        
        # All retries failed
        execution_time = time.time() - start_time
        self.logger.log_test_finish(test_name, TestStatus.FAILURE.value)
        
        return RetryResult(
            status=TestStatus.FAILURE,
            attempts=attempts,
            first_attempt_passed=first_attempt_passed,
            final_attempt_passed=final_attempt_passed,
            exceptions=exceptions,
            execution_time=execution_time
        )
    
    def execute_with_retry_decorator(
        self,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None
    ) -> Callable:
        """
        Decorator for automatic retry functionality.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Callable: Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Use provided values or fall back to instance values
                actual_max_retries = max_retries or self.max_retries
                actual_retry_delay = retry_delay or self.retry_delay
                
                # Create a temporary retry engine with custom settings
                temp_engine = RetryEngine(actual_max_retries, actual_retry_delay)
                
                # Execute with retry
                test_name = func.__name__
                return temp_engine.execute_with_retry(func, test_name, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry.
        
        This method can be extended to include custom logic for
        deciding which exceptions are retryable.
        
        Args:
            exception: The exception to evaluate
            
        Returns:
            bool: True if the exception should trigger a retry
        """
        # By default, retry all exceptions
        # This can be customized based on specific requirements
        return True
    
    def get_retry_statistics(self) -> Dict:
        """
        Get statistics about retry behavior.
        
        Returns:
            Dict: Retry statistics
        """
        # This would be implemented to track statistics across multiple tests
        # For now, return a placeholder
        return {
            "total_tests": 0,
            "passed": 0,
            "flaky": 0,
            "failed": 0,
            "total_retries": 0,
            "average_retries": 0
        }


def retry_on_failure(
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Callable:
    """
    Convenience decorator for automatic retry on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Callable: Decorator function
        
    Example:
        @retry_on_failure(max_retries=3, retry_delay=1.0)
        def test_login():
            # Test implementation
            pass
    """
    engine = RetryEngine(max_retries, retry_delay)
    return engine.execute_with_retry_decorator(max_retries, retry_delay)


def execute_test_with_retry(
    test_func: Callable,
    test_name: str,
    max_retries: Optional[int] = None,
    retry_delay: Optional[float] = None,
    *args,
    **kwargs
) -> RetryResult:
    """
    Convenience function to execute a test with retry logic.
    
    Args:
        test_func: The test function to execute
        test_name: Name of the test case
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        *args: Positional arguments to pass to test_func
        **kwargs: Keyword arguments to pass to test_func
        
    Returns:
        RetryResult: Result object with status and metadata
    """
    engine = RetryEngine(max_retries, retry_delay)
    return engine.execute_with_retry(test_func, test_name, *args, **kwargs)
