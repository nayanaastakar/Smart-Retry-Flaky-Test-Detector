"""
Ollama AI Provider Module for Smart Retry & Flaky Test Detector

This module provides an alternative AI implementation using Ollama for local execution:
- Local AI inference without API keys
- Strategy pattern implementation
- Compatible with the AI Analyzer interface
- Supports various Ollama models (llama3, mistral, etc.)
"""

import requests
import json
from typing import Dict, Optional
import traceback

from config.config import Config
from core.logger import get_logger
from ai.ai_analyzer import AIProvider


class OllamaProvider(AIProvider):
    """
    Ollama-based AI provider for local test failure analysis.
    
    This class uses the Ollama API for local AI inference without requiring
    external API keys or cloud services. It implements the AIProvider interface
    for seamless integration with the AI Analyzer.
    """
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API (uses config default if not provided)
            model: Model name to use (uses config default if not provided)
        """
        self.config = Config()
        self.logger = get_logger("OllamaProvider")
        
        self.base_url = base_url or self.config.OLLAMA_BASE_URL
        self.model = model or self.config.OLLAMA_MODEL
        
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
        self.logger.log_info(f"Ollama provider initialized with model: {self.model}")
        self.logger.log_info(f"Ollama API endpoint: {self.chat_endpoint}")
    
    def is_available(self) -> bool:
        """
        Check if Ollama provider is available.
        
        Returns:
            bool: True if Ollama is available, False otherwise
        """
        try:
            # Try to connect to Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            is_available = response.status_code == 200
            
            if is_available:
                self.logger.log_info("Ollama is available")
            else:
                self.logger.log_warning("Ollama is not available")
            
            return is_available
            
        except Exception as e:
            self.logger.log_warning(f"Ollama availability check failed: {str(e)}")
            return False
    
    def analyze_failure(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str] = None,
        console_logs: Optional[str] = None
    ) -> Dict:
        """
        Analyze a test failure using Ollama.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot (optional)
            console_logs: Browser console logs (optional)
            
        Returns:
            Dict: Analysis results from Ollama
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
            
            # Call Ollama API
            response = requests.post(
                self.chat_endpoint,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert QA automation engineer specializing in Selenium test failure analysis. Provide concise, actionable insights in JSON format."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "options": {
                        "temperature": self.config.OLLAMA_TEMPERATURE,
                        "num_predict": 1000
                    }
                },
                timeout=self.config.AI_ANALYSIS_TIMEOUT
            )
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            analysis_text = response_data.get("message", {}).get("content", "")
            analysis = self._parse_analysis_response(analysis_text)
            
            self.logger.log_info(f"Ollama analysis completed for test: {test_name}")
            return analysis
            
        except requests.exceptions.Timeout:
            self.logger.log_error("Ollama API request timed out")
            return self._get_timeout_response()
        except requests.exceptions.ConnectionError:
            self.logger.log_error("Failed to connect to Ollama API")
            return self._get_connection_error_response()
        except Exception as e:
            self.logger.log_exception(e, "Ollama analysis failed")
            return self._get_error_response(str(e))
    
    def _prepare_analysis_prompt(
        self,
        exception: Exception,
        test_name: str,
        screenshot_path: Optional[str],
        console_logs: Optional[str]
    ) -> str:
        """
        Prepare the analysis prompt for Ollama.
        
        Args:
            exception: The exception that caused the failure
            test_name: Name of the test that failed
            screenshot_path: Path to failure screenshot
            console_logs: Browser console logs
            
        Returns:
            str: Formatted prompt for Ollama
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
        Parse the Ollama response into a structured dictionary.
        
        Args:
            response_text: Raw response text from Ollama
            
        Returns:
            Dict: Structured analysis results
        """
        # Try to parse as JSON first
        try:
            # Find JSON in the response (Ollama might include extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
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
        Get response when Ollama is not available.
        
        Returns:
            Dict: Unavailable response
        """
        return {
            "classification": "Unknown",
            "root_cause": "Ollama provider not available - ensure Ollama is running locally",
            "why_it_happened": "N/A",
            "suggested_fix": "Start Ollama server: 'ollama serve' and ensure model is downloaded",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": "Ollama provider unavailable"
        }
    
    def _get_timeout_response(self) -> Dict:
        """
        Get response when Ollama request times out.
        
        Returns:
            Dict: Timeout response
        """
        return {
            "classification": "Unknown",
            "root_cause": "Ollama API request timed out",
            "why_it_happened": "N/A",
            "suggested_fix": "Increase AI_ANALYSIS_TIMEOUT in config or check Ollama server performance",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": "Request timeout"
        }
    
    def _get_connection_error_response(self) -> Dict:
        """
        Get response when connection to Ollama fails.
        
        Returns:
            Dict: Connection error response
        """
        return {
            "classification": "Unknown",
            "root_cause": "Failed to connect to Ollama API",
            "why_it_happened": "N/A",
            "suggested_fix": "Ensure Ollama is running at the configured base URL",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": "Connection error"
        }
    
    def _get_error_response(self, error_message: str) -> Dict:
        """
        Get response when Ollama analysis fails.
        
        Args:
            error_message: Error message from the failure
            
        Returns:
            Dict: Error response
        """
        return {
            "classification": "Unknown",
            "root_cause": f"Ollama analysis failed: {error_message}",
            "why_it_happened": "N/A",
            "suggested_fix": "Check Ollama server logs and configuration",
            "severity": "Low",
            "confidence_score": 0.0,
            "best_practices": [],
            "error": error_message
        }
    
    def list_available_models(self) -> list:
        """
        List available models in Ollama.
        
        Returns:
            list: List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            
            self.logger.log_info(f"Available Ollama models: {models}")
            return models
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to list Ollama models")
            return []
    
    def set_model(self, model: str) -> None:
        """
        Set the model to use for analysis.
        
        Args:
            model: Model name to use
        """
        self.model = model
        self.logger.log_info(f"Ollama model changed to: {model}")
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model.
        
        Returns:
            Dict: Model information
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model},
                timeout=5
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.log_exception(e, "Failed to get model info")
            return {}


def create_ollama_provider(
    base_url: Optional[str] = None,
    model: Optional[str] = None
) -> OllamaProvider:
    """
    Factory function to create an Ollama provider.
    
    Args:
        base_url: Base URL for Ollama API
        model: Model name to use
        
    Returns:
        OllamaProvider: Configured Ollama provider instance
    """
    return OllamaProvider(base_url, model)
