"""
ai/prompts.py
==============
Prompt construction for the AI Failure Analysis module. Kept separate from
the client/analyzer so prompt wording can be iterated on without touching
HTTP or persistence logic.
"""

from __future__ import annotations

SYSTEM_PROMPT = """You are a senior Selenium/QA automation engineer performing root-cause \
analysis on a failed or flaky automated test. You are precise, concise, and never invent \
information that isn't supported by the evidence given. You always respond with valid JSON \
matching exactly the schema you are given, and nothing else."""

RESPONSE_SCHEMA_DESCRIPTION = """Respond with a single JSON object with exactly these keys:
{
  "root_cause": "one or two sentences on the most likely underlying cause",
  "severity": "one of: LOW, MEDIUM, HIGH, CRITICAL",
  "possible_reason": "brief technical explanation of why this exception/pattern occurs",
  "recommended_fix": "concrete, actionable fix for this specific test",
  "prevention": "how to prevent this class of failure going forward",
  "confidence_score": "a float between 0.0 and 1.0",
  "suggested_code": "a short Selenium code snippet (Python) implementing the recommended fix"
}"""


def build_failure_analysis_prompt(
    test_name: str,
    module: str,
    exception_type: str | None,
    exception_message: str | None,
    stack_trace: str | None,
    console_logs: str | None,
    retry_history: list[dict],
    screenshot_path: str | None,
) -> str:
    retry_summary = "\n".join(
        f"  - Attempt {r.get('attempt_number')}: {r.get('status')} "
        f"({r.get('duration_ms', 0)}ms){' - ' + r['error_message'] if r.get('error_message') else ''}"
        for r in retry_history
    ) or "  (no retry history available)"

    return f"""Analyze this Selenium test failure and produce a structured root-cause report.

TEST NAME: {test_name}
MODULE: {module}
EXCEPTION TYPE: {exception_type or 'unknown'}
EXCEPTION MESSAGE: {exception_message or 'none captured'}

STACK TRACE:
{(stack_trace or 'none captured')[:2000]}

BROWSER CONSOLE LOGS:
{(console_logs or 'none captured')[:1000]}

RETRY HISTORY:
{retry_summary}

SCREENSHOT AVAILABLE: {"yes, at " + screenshot_path if screenshot_path else "no"}

{RESPONSE_SCHEMA_DESCRIPTION}
"""
