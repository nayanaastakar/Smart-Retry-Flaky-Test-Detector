"""
Failure Analyzer - Module 6

Coordinates the building of prompts and communicating with Ollama Client to parse AI Analysis.
"""

import json
import time
import logging
from typing import Optional

from models.evidence import Evidence
from models.ai_analysis import AIAnalysis
from ai.ollama_client import OllamaClient
from ai.prompt_builder import PromptBuilder
from config.config import Config


class FailureAnalyzer:
    """
    Analyzes test failures using AI.
    
    Methods:
        analyze(evidence)
        parse_response(response_text)
        validate_response(parsed_json)
    """

    def __init__(self):
        self.config = Config()
        self.client = OllamaClient()
        self.prompt_builder = PromptBuilder()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Cache identical failures by exception signature to avoid duplicate AI requests
        self._analysis_cache = {}

    def analyze(self, evidence: Evidence) -> AIAnalysis:
        """
        Analyze the failure evidence using Ollama.
        
        Returns:
            AIAnalysis model containing the analysis or default values if AI fails.
        """
        # Default fallback
        fallback = AIAnalysis(
            test_name=evidence.test_name,
            status=evidence.status,
            model_name=self.config.OLLAMA_MODEL
        )

        if not self.config.ENABLE_AI:
            return fallback

        if not evidence.is_failure:
            self.logger.debug("Test passed, skipping AI analysis.")
            return fallback

        # Simple caching mechanism based on test name and exception
        cache_key = f"{evidence.test_name}_{evidence.exception_type}_{evidence.exception_msg}"
        if cache_key in self._analysis_cache:
            self.logger.info(f"Using cached AI analysis for {evidence.test_name}")
            return self._analysis_cache[cache_key]

        print(f"Sending Failure To AI... ({evidence.test_name})")
        print("Waiting...")
        
        # Read browser logs if available
        browser_logs = ""
        if evidence.has_log:
            try:
                with open(evidence.log_file, 'r', encoding='utf-8') as f:
                    browser_logs = f.read()
            except Exception as e:
                self.logger.warning(f"Failed to read browser logs for AI analysis: {str(e)}")

        prompt = self.prompt_builder.build_prompt(evidence, browser_logs)
        
        start_time = time.time()
        response_text = self.client.generate(prompt)
        duration = round(time.time() - start_time, 2)
        
        if not response_text:
            self.logger.warning("AI failed to generate a response. Returning fallback.")
            fallback.response_time = f"{duration} sec"
            return fallback

        parsed_data = self.parse_response(response_text)
        validated_data = self.validate_response(parsed_data)
        
        # Build final analysis object
        analysis = AIAnalysis(
            test_name=evidence.test_name,
            status=evidence.status,
            classification=validated_data.get('classification', fallback.classification),
            root_cause=validated_data.get('root_cause', fallback.root_cause),
            reason=validated_data.get('reason', fallback.reason),
            recommendation=validated_data.get('recommendation', fallback.recommendation),
            prevention=validated_data.get('prevention', fallback.prevention),
            confidence=validated_data.get('confidence', fallback.confidence),
            response_time=f"{duration} sec",
            model_name=self.config.OLLAMA_MODEL
        )
        
        print(f"AI Analysis Completed (Model: {analysis.model_name}, Confidence: {analysis.confidence}%)")
        
        # Store in cache
        self._analysis_cache[cache_key] = analysis
        return analysis

    def parse_response(self, response_text: str) -> dict:
        """Parse JSON response from Ollama safely."""
        try:
            # Strip markdown block quotes if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
                
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from AI response: {str(e)}\nRaw Response: {response_text}")
            return {}

    def validate_response(self, parsed_json: dict) -> dict:
        """Validate the fields returned by AI and enforce types."""
        if not parsed_json:
            return {}
            
        validated = {}
        # Ensure strings
        for field in ['classification', 'root_cause', 'reason', 'recommendation', 'prevention']:
            val = parsed_json.get(field, "")
            validated[field] = str(val) if val else "Not provided"
            
        # Ensure confidence is int
        try:
            validated['confidence'] = int(parsed_json.get('confidence', 0))
        except (ValueError, TypeError):
            validated['confidence'] = 0
            
        return validated
