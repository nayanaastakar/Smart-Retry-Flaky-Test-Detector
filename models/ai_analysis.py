"""
AI Analysis Model - Module 6

Data model for holding the results of AI-driven test failure analysis.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AIAnalysis:
    """
    Holds the AI's analysis of a failed or flaky test.
    
    Attributes:
        test_name (str): Name of the test analyzed.
        status (str): Status of the test (FLAKY or FAILURE).
        classification (str): Category of failure (e.g., Timeout, Locator Issue).
        root_cause (str): Detailed root cause of the failure.
        reason (str): Why the failure occurred.
        recommendation (str): Suggested fix for the issue.
        prevention (str): Tips to prevent this failure in the future.
        confidence (int): AI's confidence score (0-100) in its analysis.
        response_time (str): Time taken by the model to generate response.
        model_name (str): Name of the Ollama model used.
    """
    test_name: str = ""
    status: str = ""
    classification: str = "Unknown"
    root_cause: str = "Analysis not available"
    reason: str = "Analysis not available"
    recommendation: str = "Manual investigation required"
    prevention: str = "No prevention tips available"
    confidence: int = 0
    response_time: str = "0 sec"
    model_name: str = "unknown"

    def to_dict(self) -> dict:
        """Convert the analysis to a dictionary for JSON serialization."""
        return {
            "test_name": self.test_name,
            "status": self.status,
            "classification": self.classification,
            "root_cause": self.root_cause,
            "reason": self.reason,
            "recommendation": self.recommendation,
            "prevention": self.prevention,
            "confidence": self.confidence,
            "response_time": self.response_time,
            "model_name": self.model_name
        }
