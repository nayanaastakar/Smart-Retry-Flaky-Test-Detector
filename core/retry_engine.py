"""
Retry Engine Module - Module 2

This module provides the Smart Retry Engine with:
- Automatic test retry on failure
- Configurable retry count and delay
- Test status classification (PASS, FLAKY, FAILURE)
- Retry tracking without logging
"""

import time
from typing import Callable, Any
from functools import wraps

from config.config import Config
from utils.retry_result import RetryResult, TestStatus


class RetryEngine:
    """
    Smart Retry Engine for test execution.
    
    This class implements retry logic for Selenium tests:
    - Executes test functions with automatic retry on failure
    - Classifies tests as PASS, FLAKY, or FAILURE
    - Tracks number of attempts and execution time
    - Returns RetryResult with complete execution details
    """
    
    def __init__(self):
        """
        Initialize the RetryEngine.
        
        Loads configuration for retry settings.
        """
        self.config = Config()
        self.max_retries = self.config.MAX_RETRIES
        self.retry_delay = self.config.RETRY_DELAY
    
    def execute(self, test_func: Callable, test_name: str) -> RetryResult:
        """
        Execute a test function with retry logic.
        
        Args:
            test_func: The test function to execute
            test_name: Name of the test for reporting
        
        Returns:
            RetryResult: Result containing status, attempts, and execution time
        """
        start_time = time.time()
        attempts = 0
        last_exception = None
        first_passed = False
        
        print(f"Running {test_name}...")
        
        # First attempt
        attempts += 1
        print(f"Attempt {attempts}")
        
        try:
            result = test_func()
            first_passed = True
            print("PASSED")
            
            # Test passed on first attempt
            execution_time = time.time() - start_time
            return RetryResult(
                test_name=test_name,
                status=TestStatus.PASS,
                attempts=attempts,
                execution_time=execution_time,
                exception=None
            )
        except Exception as e:
            last_exception = str(e)
            print(f"FAILED: {last_exception}")
        
        # Retry attempts
        for attempt in range(1, self.max_retries + 1):
            attempts += 1
            print("Retrying...")
            print(f"Attempt {attempts}")
            
            # Wait before retry
            time.sleep(self.retry_delay)
            
            try:
                result = test_func()
                print("PASSED")
                
                # Test passed after retry - FLAKY
                execution_time = time.time() - start_time
                return RetryResult(
                    test_name=test_name,
                    status=TestStatus.FLAKY,
                    attempts=attempts,
                    execution_time=execution_time,
                    exception=last_exception
                )
            except Exception as e:
                last_exception = str(e)
                print(f"FAILED: {last_exception}")
        
        # All retries failed - FAILURE
        execution_time = time.time() - start_time
        return RetryResult(
            test_name=test_name,
            status=TestStatus.FAILURE,
            attempts=attempts,
            execution_time=execution_time,
            exception=last_exception
        )
    
    def reset(self) -> None:
        """
        Reset the retry engine state.
        
        This method can be used to clear any internal state
        before running a new test sequence.
        """
        pass
    
    def retry(self, test_func: Callable) -> Callable:
        """
        Decorator to add retry functionality to any test function.
        
        Args:
            test_func: The test function to wrap with retry logic
        
        Returns:
            Callable: Wrapped function with retry logic
        """
        @wraps(test_func)
        def wrapper(*args, **kwargs) -> RetryResult:
            return self.execute(test_func, test_func.__name__)
        return wrapper
