"""
AI Prompts Module for Smart Retry & Flaky Test Detector

This module contains prompt templates for AI analysis of Selenium test failures.
Prompts are designed to extract structured insights about test failures including:
- Classification of failure type
- Root cause analysis
- Suggested fixes
- Best practices
- Confidence scoring
"""


def get_failure_analysis_prompt() -> str:
    """
    Get the main prompt for Selenium failure analysis.
    
    This prompt instructs the AI to analyze a Selenium test failure and provide
    structured insights about the exception, its cause, and potential fixes.
    
    Returns:
        str: Formatted prompt for AI analysis
    """
    prompt = """
Analyze this Selenium test failure and provide a structured analysis in JSON format with the following fields:

{
    "classification": "One of: Timeout, Element Not Found, Stale Element, Element Not Interactable, Network Issue, Application Bug, Flaky Test, Other",
    "root_cause": "Brief explanation of what caused the failure",
    "why_it_happened": "Detailed explanation of why this failure occurred",
    "suggested_fix": "Specific actionable steps to fix the issue",
    "severity": "One of: Critical, High, Medium, Low",
    "confidence_score": "Float between 0.0 and 1.0 indicating confidence in this analysis",
    "best_practices": ["List of 3-5 best practices to prevent similar failures"],
    "is_flaky": "Boolean indicating if this appears to be a flaky test",
    "retry_recommendation": "Whether retrying this test is likely to succeed (Boolean)"
}

Focus on:
1. Identifying whether this is a genuine application bug or a test infrastructure issue
2. Distinguishing between flaky tests (timing, network, dynamic content) and permanent failures
3. Providing specific, actionable fixes rather than generic advice
4. Considering Selenium-specific issues (waits, locators, browser state)
5. Recommending best practices for stable test automation

"""
    return prompt


def get_flaky_test_detection_prompt() -> str:
    """
    Get the prompt for flaky test detection analysis.
    
    This prompt focuses specifically on identifying whether a test failure
    is due to flakiness or a genuine application bug.
    
    Returns:
        str: Formatted prompt for flaky test detection
    """
    prompt = """
Analyze this test failure to determine if it's a flaky test or a genuine failure.

Provide analysis in JSON format:
{
    "is_flaky": "Boolean - true if this appears to be a flaky test",
    "flaky_probability": "Float between 0.0 and 1.0 indicating likelihood of flakiness",
    "flaky_indicators": ["List of specific indicators that suggest flakiness"],
    "classification": "One of: Definitely Flaky, Likely Flaky, Possibly Flaky, Not Flaky, Cannot Determine",
    "root_cause": "Explanation of what makes this flaky (if applicable)",
    "retry_success_probability": "Float between 0.0 and 1.0 indicating likelihood of success on retry",
    "recommended_action": "One of: Retry with Wait, Increase Timeout, Add Explicit Wait, Fix Application Bug, Improve Test Stability, Other"
}

Flaky test indicators to consider:
- Timeout exceptions (element loaded slowly)
- NoSuchElementException (dynamic loading issues)
- StaleElementReferenceException (DOM updates)
- ElementClickInterceptedException (animations, overlays)
- Network-related failures
- Inconsistent behavior across runs
- Timing-dependent failures
"""
    return prompt


def get_exception_classification_prompt() -> str:
    """
    Get the prompt for exception type classification.
    
    This prompt focuses on classifying the type of Selenium exception
    and providing specific guidance for each type.
    
    Returns:
        str: Formatted prompt for exception classification
    """
    prompt = """
Classify this Selenium exception and provide specific guidance.

Provide analysis in JSON format:
{
    "exception_type": "The specific Selenium exception type",
    "exception_category": "One of: Timeout, Element Not Found, Element Interaction, Stale Element, Network, WebDriver, Other",
    "common_causes": ["List of common causes for this exception type"],
    "immediate_fix": "Immediate action to resolve this specific occurrence",
    "long_term_fix": "Long-term solution to prevent this exception",
    "wait_strategy": "Recommended wait strategy (Explicit Wait, Fluent Wait, Sleep, etc.)",
    "locator_improvement": "Suggestions for improving element locators if relevant"
}

Consider these exception types and their typical solutions:
- TimeoutException: Increase timeout, use explicit waits, check page load
- NoSuchElementException: Wait for element presence, verify locator, check for iframes
- StaleElementReferenceException: Re-find element, use stable locators, check for DOM updates
- ElementClickInterceptedException: Wait for element to be clickable, check for overlays
- ElementNotInteractableException: Wait for element state, check if disabled/hidden
- WebDriverException: Check browser compatibility, driver version, network connectivity
"""
    return prompt


def get_best_practices_prompt() -> str:
    """
    Get the prompt for generating best practices recommendations.
    
    This prompt focuses on providing best practices for stable
    Selenium test automation based on the observed failure.
    
    Returns:
        str: Formatted prompt for best practices generation
    """
    prompt = """
Based on this test failure, provide best practices for stable Selenium automation.

Provide recommendations in JSON format:
{
    "wait_strategies": ["List of recommended wait strategies for this scenario"],
    "locator_strategies": ["List of recommended locator strategies"],
    "test_design_principles": ["List of test design principles to apply"],
    "page_object_recommendations": ["Suggestions for Page Object Model improvements"],
    "error_handling": ["Recommended error handling approaches"],
    "retry_strategies": ["Recommended retry strategies if applicable"],
    "general_best_practices": ["List of general Selenium best practices"]
}

Focus on:
- Explicit waits over implicit waits
- Stable, unique locators (CSS selectors, XPath)
- Page Object Model implementation
- Proper test isolation and cleanup
- Handling dynamic content and asynchronous operations
- Network resilience and timeout management
- Browser compatibility considerations
"""
    return prompt


def get_code_generation_prompt() -> str:
    """
    Get the prompt for generating Python code fixes.
    
    This prompt instructs the AI to generate Python code to fix
    the observed test failure.
    
    Returns:
        str: Formatted prompt for code generation
    """
    prompt = """
Generate Python code to fix this Selenium test failure.

Provide the solution in JSON format:
{
    "original_code_snippet": "The problematic code section (if identifiable)",
    "fixed_code_snippet": "The corrected code with proper waits and error handling",
    "explanation": "Explanation of what was changed and why",
    "imports_needed": ["List of any additional imports required"],
    "additional_changes": ["List of any other changes needed in the test"]
}

Code should include:
- Proper explicit waits (WebDriverWait with expected_conditions)
- Error handling with try-except blocks
- Logging for debugging
- Comments explaining the fix
- Follow PEP 8 style guidelines
- Use Page Object Model pattern where applicable
"""
    return prompt


def get_summary_report_prompt() -> str:
    """
    Get the prompt for generating a summary report of test execution.
    
    This prompt focuses on generating a human-readable summary
    of test execution results and AI analysis.
    
    Returns:
        str: Formatted prompt for summary report generation
    """
    prompt = """
Generate a summary report of the test execution and AI analysis.

Provide the summary in JSON format:
{
    "executive_summary": "Brief high-level summary of test results",
    "key_findings": ["List of key findings from the test execution"],
    "flaky_tests": ["List of tests identified as flaky"],
    "genuine_failures": ["List of tests with genuine failures"],
    "critical_issues": ["List of critical issues requiring immediate attention"],
    "recommendations": ["List of prioritized recommendations"],
    "overall_health": "Assessment of overall test suite health (Excellent, Good, Fair, Poor)",
    "next_steps": ["List of recommended next steps"]
}

Focus on:
- Actionable insights for improving test stability
- Prioritization of issues based on severity and impact
- Clear, concise language suitable for stakeholders
- Quantitative metrics where available
- Specific, achievable recommendations
"""
    return prompt


def get_custom_prompt(template: str, **kwargs) -> str:
    """
    Generate a custom prompt by substituting variables into a template.
    
    Args:
        template: Prompt template string with {variable} placeholders
        **kwargs: Variable substitutions
        
    Returns:
        str: Formatted prompt with substitutions applied
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required variable in template: {e}")


# Predefined prompt templates for common scenarios
PROMPT_TEMPLATES = {
    "failure_analysis": get_failure_analysis_prompt,
    "flaky_detection": get_flaky_test_detection_prompt,
    "exception_classification": get_exception_classification_prompt,
    "best_practices": get_best_practices_prompt,
    "code_generation": get_code_generation_prompt,
    "summary_report": get_summary_report_prompt
}


def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a prompt by type with optional variable substitutions.
    
    Args:
        prompt_type: Type of prompt to retrieve
        **kwargs: Variable substitutions for the prompt template
        
    Returns:
        str: Formatted prompt
        
    Raises:
        ValueError: If prompt_type is not found
    """
    if prompt_type not in PROMPT_TEMPLATES:
        available = ", ".join(PROMPT_TEMPLATES.keys())
        raise ValueError(f"Unknown prompt type: {prompt_type}. Available types: {available}")
    
    prompt = PROMPT_TEMPLATES[prompt_type]()
    
    if kwargs:
        prompt = get_custom_prompt(prompt, **kwargs)
    
    return prompt
