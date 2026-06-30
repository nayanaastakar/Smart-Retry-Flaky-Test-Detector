"""
AI Analyzer Module for Smart Retry & Flaky Test Detector

This module provides AI-powered analysis of Selenium test failures using:
- OpenAI API for intelligent error analysis
- Strategy pattern for multiple AI providers
- Exception classification and root cause analysis
- Suggested fixes and best practices
- Confidence scoring
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import json
import traceback

from config.config import Config
from core.logger import get_logger


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    This class defines the interface for AI analysis providers,
    allowing for multiple implementations (OpenAI, Ollama, etc.).
    """
    
    @abstractmethod
    def analyze_failure(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str] = None,
        console_logs: Optional[str] = None
    ) -> Dict:
        """
        Analyze a test failure using AI.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot (optional)
            console_logs: Browser console logs (optional)
            
        Returns:
            Dict: Analysis results including classification, root cause, and suggestions
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI provider is available.
        
        Returns:
            bool: True if provider is available, False otherwise
        """
        pass


class OpenAIProvider(AIProvider):
    """
    OpenAI-based AI provider for test failure analysis.
    
    This class uses the OpenAI API to analyze Selenium exceptions
    and provide intelligent insights about test failures.
    """
    
    def __init__(self):
        """
        Initialize the OpenAI provider.
        
        Sets up configuration and logger instance.
        """
        self.config = Config()
        self.logger = get_logger("OpenAIProvider")
        self.client = None
        
        # Initialize OpenAI client if API key is available
        if self.config.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
                self.logger.log_info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.log_exception(e, "Failed to initialize OpenAI client")
                self.client = None
        else:
            self.logger.log_warning("OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """
        Check if OpenAI provider is available.
        
        Returns:
            bool: True if OpenAI client is available, False otherwise
        """
        return self.client is not None
    
    def analyze_failure(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str] = None,
        console_logs: Optional[str] = None
    ) -> Dict:
        """
        Analyze a test failure using OpenAI.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot (optional)
            console_logs: Browser console logs (optional)
            
        Returns:
            Dict: Analysis results from OpenAI
        """
        if not self.is_available():
            return self._get_unavailable_response()
        
        try:
            # Prepare the analysis prompt
            prompt = self._prepare_analysis_prompt(
                exception,
                test_name,
                screenshot_path,
                console_logs
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert QA automation engineer specializing in Selenium test failure analysis. Provide concise, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.OPENAI_TEMPERATURE,
                max_tokens=self.config.OPENAI_MAX_TOKENS
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis = self._parse_analysis_response(analysis_text)
            
            self.logger.log_info(f"OpenAI analysis completed for test: {test_name}")
            return analysis
            
        except Exception as e:
            self.logger.log_exception(e, "OpenAI analysis failed")
            return self._get_error_response(str(e))
    
    def _prepare_analysis_prompt(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str],
        console_logs: Optional[str]
    ) -> str:
        """
        Prepare the analysis prompt for OpenAI.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot
            console_logs: Browser console logs
            
        Returns:
            str: Formatted prompt for OpenAI
        """
        from ai.prompts import get_failure_analysis_prompt
        
        # Get base prompt
        prompt = get_failure_analysis_prompt()
        
        # Add exception details
        exception_info = f"""
Test Name: {test_name}
Exception Type: {type(exception).__name__}
Exception Message: {str(exception)}
Stack Trace:
{traceback.format_exc()}
"""
        
        # Add console logs if available
        if console_logs:
            exception_info += f"\nConsole Logs:\n{console_logs}"
        
        # Add screenshot info if available
        if screenshot_path:
            exception_info += f"\nScreenshot Path: {screenshot_path}"
        
        return prompt + exception_info
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """
        Parse the OpenAI response into a structured dictionary.
        
        Args:
            response_text: Raw response text from OpenAI
            
        Returns:
            Dict: Structured analysis results
        """
        # Try to parse as JSON first
        try:
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # If not JSON, parse text response
        analysis = {
            "classification": "Unknown",
            "root_cause": response_text,
            "why_it_happened": "See root cause",
            "suggested_fix": "Review the analysis",
            "severity": "Medium",
            "confidence_score": 0.7,
            "best_practices": [],
            "raw_response": response_text
        }
        
        # Try to extract key information from text
        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'classification:' in line_lower or 'type:' in line_lower:
                analysis["classification"] = line.split(':', 1)[1].strip()
            elif 'root cause:' in line_lower:
                analysis["root_cause"] = line.split(':', 1)[1].strip()
            elif 'fix:' in line_lower or 'suggestion:' in line_lower:
                analysis["suggested_fix"] = line.split(':', 1)[1].strip()
            elif 'severity:' in line_lower:
                analysis["severity"] = line.split(':', 1)[1].strip()
        
        return analysis
    
    def _get_unavailable_response(self) -> Dict:
        """
        Get response when OpenAI is not available.
        
        Returns:
            Dict: Unavailable response
        """
        return {
            "classification": "Unknown",
            "root_cause": "OpenAI provider not available - API key not configured",
            "why_it_happened": "N/A",
            "suggested_fix": "Configure OPENAI_API_KEY environment variable",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": "OpenAI provider unavailable"
        }
    
    def _get_error_response(self, error_message: str) -> Dict:
        """
        Get response when OpenAI analysis fails.
        
        Args:
            error_message: Error message from the failure
            
        Returns:
            Dict: Error response
        """
        return {
            "classification": "Unknown",
            "root_cause": f"OpenAI analysis failed: {error_message}",
            "why_it_happened": "N/A",
            "suggested_fix": "Check OpenAI API configuration and connectivity",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": error_message
        }


class AIAnalyzer:
    """
    Main AI Analyzer class that manages AI providers.
    
    This class provides a unified interface for AI analysis,
    supporting multiple AI providers through the strategy pattern.
    """
    
    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize the AI Analyzer.
        
        Args:
            provider: AI provider to use (defaults to OpenAI if available)
        """
        self.config = Config()
        self.logger = get_logger("AIAnalyzer")
        
        # Use provided provider or default to OpenAI
        if provider:
            self.provider = provider
        else:
            self.provider = OpenAIProvider()
        
        self.logger.log_info(f"AI Analyzer initialized with provider: {type(self.provider).__name__}")
    
    def analyze_failure(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str] = None,
        console_logs: Optional[str] = None
    ) -> Dict:
        """
        Analyze a test failure using AI.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot (optional)
            console_logs: Browser console logs (optional)
            
        Returns:
            Dict: Analysis results including classification, root cause, and suggestions
        """
        try:
            self.logger.log_ai_analysis_start(test_name)
            
            # Check if AI analysis is enabled
            if not self.config.ENABLE_AI:
                self.logger.log_warning("AI analysis is disabled in configuration")
                return self._get_disabled_response()
            
            # Perform analysis
            analysis = self.provider.analyze_failure(
                exception,
                test_name,
                screenshot_path,
                console_logs
            )
            
            self.logger.log_ai_analysis_finish(test_name, analysis)
            return analysis
            
        except Exception as e:
            self.logger.log_exception(e, "AI analysis failed")
            return self._get_error_response(str(e))
    
    def _get_disabled_response(self) -> Dict:
        """
        Get response when AI analysis is disabled.
        
        Returns:
            Dict: Disabled response
        """
        return {
            "classification": "Skipped",
            "root_cause": "AI analysis is disabled in configuration",
            "why_it_happened": "N/A",
            "suggested_fix": "Enable AI_ANALYSIS_ENABLED in config",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": "AI analysis disabled"
        }
    
    def _get_error_response(self, error_message: str) -> Dict:
        """
        Get response when analysis fails.
        
        Args:
            error_message: Error message from the failure
            
        Returns:
            Dict: Error response
        """
        return {
            "classification": "Error",
            "root_cause": f"AI analysis error: {error_message}",
            "why_it_happened": "N/A",
            "suggested_fix": "Check logs for details",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": error_message
        }
    
    def set_provider(self, provider: AIProvider) -> None:
        """
        Set a different AI provider.
        
        Args:
            provider: AI provider to use
        """
        self.provider = provider
        self.logger.log_info(f"AI provider changed to: {type(provider).__name__}")
    
    def is_available(self) -> bool:
        """
        Check if AI analysis is available.
        
        Returns:
            bool: True if AI provider is available, False otherwise
        """
        return self.provider.is_available()


def analyze_test_failure(
    exception: Exception,
    test_name: str,
    screenshot_path: Optional[str] = None,
    console_logs: Optional[str] = None
) -> Dict:
    """
    Convenience function to analyze a test failure.
    
    Args:
        exception: The exception that caused the failure
        test_name: Name of the test that failed
        screenshot_path: Path to failure screenshot (optional)
        console_logs: Browser console logs (optional)
        
    Returns:
        Dict: Analysis results
    """
    analyzer = AIAnalyzer()
    return analyzer.analyze_failure(exception, test_name, screenshot_path, console_logs)
