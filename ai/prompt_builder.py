"""
Prompt Builder - Module 6

Constructs the prompt sent to Ollama based on the provided test evidence.
"""

from models.evidence import Evidence


class PromptBuilder:
    """
    Builds structured prompts for the AI model to analyze test failures.
    """

    def build_prompt(self, evidence: Evidence, browser_logs: str) -> str:
        """
        Build the prompt string.
        
        Args:
            evidence (Evidence): The test execution evidence.
            browser_logs (str): Snippet of the browser console logs.
            
        Returns:
            str: The constructed prompt.
        """
        
        # Limit browser logs to prevent exceeding context window (e.g., last 2000 chars)
        logs_snippet = browser_logs[-2000:] if browser_logs else "No browser logs available."
        
        prompt = f"""
You are an expert Selenium QA Engineer and Software Architect.
Analyze this Selenium failure and provide a structured JSON response.

Test Name: {evidence.test_name}
Status: {evidence.status}
Exception: {evidence.exception_type}
Message: {evidence.exception_msg}
Attempts: {evidence.attempts}
Execution Time: {evidence.execution_time}

Browser Log Snippet:
{logs_snippet}

Return JSON only, with the following exact fields:
- classification (string): e.g., 'Timeout', 'Stale Element', 'Assertion Error', 'Application Bug'
- root_cause (string): What technically caused this failure?
- reason (string): Why did it happen?
- recommendation (string): Suggested code fix or configuration change.
- prevention (string): How to prevent this in the future?
- confidence (number): 0-100 score indicating your confidence in this analysis.

Do not include any other text outside the JSON object.
"""
        return prompt.strip()
