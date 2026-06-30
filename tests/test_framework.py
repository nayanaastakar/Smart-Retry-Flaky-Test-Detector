"""
Unit Tests for Smart Retry & Flaky Test Detector Framework

This module contains unit tests for core framework components:
- Retry Engine
- Flaky Detector
- Logger
- AI Analyzer
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from selenium.common.exceptions import TimeoutException

from core.retry_engine import RetryEngine, RetryResult, TestStatus
from core.flaky_detector import FlakyDetector
from core.logger import TestLogger, LogManager
from ai.ai_analyzer import AIAnalyzer
from config.config import Config


class TestRetryEngine:
    """
    Unit tests for the Retry Engine.
    """
    
    def setup_method(self):
        """Setup for each test method."""
        self.retry_engine = RetryEngine()
    
    def test_successful_execution_no_retry(self):
        """Test that a passing test is executed once without retries."""
        def successful_func():
            return "success"
        
        result = self.retry_engine.execute(successful_func, "test_success")
        
        assert result.status == TestStatus.PASS
        assert result.attempts == 1
    
    def test_failure_all_retries(self):
        """Test that a failing test exhausts all retries."""
        def failing_func():
            raise ValueError("Test failure")
        
        result = self.retry_engine.execute(failing_func, "test_failure")
        
        assert result.status == TestStatus.FAILURE
        assert result.attempts == 3  # 1 initial + 2 retries
        # len(exceptions) checking removed since it uses singular exception now
    
    def test_flaky_detection_pass_after_retry(self):
        """Test flaky detection when a test passes after initial failure."""
        call_count = [0]
        
        def flaky_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("First attempt fails")
            return "success"
        
        result = self.retry_engine.execute(flaky_func, "test_flaky")
        
        assert result.status == TestStatus.FLAKY
        assert result.attempts == 2
    
    def test_retry_delay(self):
        """Test that engine respects retry delay."""
        def failing_func():
            raise ValueError("Failure")
        
        import time
        start_time = time.time()
        result = self.retry_engine.execute(failing_func, "test_delay")
        end_time = time.time()
        
        # With 2 retries and 0.1s delay, should take at least 0.2s
        assert (end_time - start_time) >= 0.2
    
    def test_result_to_dict(self):
        """Test conversion of result to dictionary."""
        result = RetryResult(
            test_name="test_login",
            status=TestStatus.PASS,
            attempts=1,
            execution_time=1.5,
            exception=None
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] == "PASS"
        assert result_dict["attempts"] == 1
        assert result_dict["execution_time"] == "1.50 sec"


class TestLogger:
    """
    Unit tests for the Logger.
    """
    
    def setup_method(self):
        """Setup for each test method."""
        self.logger = LogManager.get_logger("test_logger")
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        assert self.logger.test_name == "test_logger"
        assert self.logger.logger is not None
    
    def test_log_info(self):
        """Test info logging."""
        # This should not raise an exception
        self.logger.log_info("Test info message")
    
    def test_log_error(self):
        """Test error logging."""
        # This should not raise an exception
        self.logger.log_error("Test error message")
    
    def test_log_exception(self):
        """Test exception logging."""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            # This should not raise an exception
            self.logger.log_exception(e, "Test context")
    
    def test_log_manager(self):
        """Test LogManager functionality."""
        logger1 = LogManager.get_logger("test1")
        logger2 = LogManager.get_logger("test1")
        
        # Should return the same instance
        assert logger1 is logger2
        
        LogManager.remove_logger("test1")
        
        # Should create new instance after removal
        logger3 = LogManager.get_logger("test1")
        assert logger3 is not logger1


class TestAIAnalyzer:
    """
    Unit tests for the AI Analyzer.
    """
    
    def setup_method(self):
        """Setup for each test method."""
        self.config = Config()
        self.analyzer = AIAnalyzer()
        self.analyzer.config = self.config
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        assert self.analyzer is not None
        assert self.analyzer.provider is not None
    
    def test_analyze_failure_disabled(self):
        """Test analysis when AI is disabled."""
        self.analyzer.config.ENABLE_AI = False
        analysis = self.analyzer.analyze_failure(ValueError("Test error"), "test_name")
        assert analysis["classification"] == "Skipped"
        assert "disabled" in analysis["root_cause"].lower()
    
    def test_set_provider(self):
        """Test setting a different AI provider."""
        from ai.ai_analyzer import AIProvider
        
        class MockProvider(AIProvider):
            def analyze_failure(self, exception, test_name, screenshot_path=None, console_logs=None):
                return {"mock": True}
            
            def is_available(self):
                return True
        
        mock_provider = MockProvider()
        self.analyzer.set_provider(mock_provider)
        
        assert self.analyzer.provider is mock_provider


class TestConfig:
    """
    Unit tests for Configuration.
    """
    
    def test_config_initialization(self):
        """Test that config initializes with correct defaults or env vars."""
        config = Config()
        
        assert config.BROWSER == "chrome"
        assert config.MAX_RETRY_COUNT == 2
        assert config.IMPLICIT_WAIT == 10
    
    def test_directory_creation(self):
        """Test directory creation."""
        config = Config()
        
        assert config.SCREENSHOT_PATH.exists()
        assert config.LOG_PATH.exists()
        assert config.REPORT_PATH.exists()
    
    def test_screenshot_path_generation(self):
        """Test screenshot path generation."""
        config = Config()
        
        path = config.get_screenshot_path("test_name")
        
        assert path.parent == config.SCREENSHOT_PATH
        assert "test_name" in path.name
        assert path.suffix == ".png"
    
    def test_log_path_generation(self):
        """Test log path generation."""
        config = Config()
        
        path = config.get_log_path("test_name")
        
        assert path.parent == config.LOG_PATH
        assert "test_name" in path.name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
