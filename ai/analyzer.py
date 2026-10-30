"""
ai/analyzer.py
================
Module 6: AI Failure Analysis.

Orchestrates: pull execution + retry history from the DB -> build prompt ->
call Ollama -> validate/normalize the response -> persist to `ai_analyses` ->
link back to the execution row.
"""

from __future__ import annotations

import logging

from ai.ollama_client import OllamaClient, OllamaUnavailableError
from ai.prompts import SYSTEM_PROMPT, build_failure_analysis_prompt
from config import settings
from database.db_manager import execute, fetch_all, fetch_one

logger = logging.getLogger("smart_retry.ai_analyzer")

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class AIAnalysisError(RuntimeError):
    pass


class AIFailureAnalyzer:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def analyze_execution(self, execution_id: int) -> dict:
        from services.settings_service import get_runtime_settings

        if not get_runtime_settings()["ai_enabled"]:
            raise AIAnalysisError("AI analysis is disabled in settings.")

        execution = fetch_one("SELECT * FROM executions WHERE id = ?", (execution_id,))
        if not execution:
            raise AIAnalysisError(f"Execution {execution_id} not found.")

        if execution["status"] not in ("FAIL", "FLAKY"):
            raise AIAnalysisError("AI analysis only applies to FAIL or FLAKY executions.")

        retry_rows = fetch_all(
            "SELECT attempt_number, status, duration_ms, error_message FROM retry_attempts "
            "WHERE execution_id = ? ORDER BY attempt_number ASC",
            (execution_id,),
        )
        retry_history = [dict(r) for r in retry_rows]

        prompt = build_failure_analysis_prompt(
            test_name=execution["test_name"],
            module=execution["module"] or "general",
            exception_type=execution["exception_type"],
            exception_message=execution["exception_message"],
            stack_trace=execution["stack_trace"],
            console_logs=execution["console_logs"],
            retry_history=retry_history,
            screenshot_path=execution["screenshot_path"],
        )

        try:
            result = self.client.generate_json(prompt, system=SYSTEM_PROMPT)
        except OllamaUnavailableError as exc:
            logger.warning("AI analysis unavailable: %s", exc)
            raise AIAnalysisError(str(exc)) from exc

        normalized = self._normalize(result)
        analysis_id = self._persist(execution_id, normalized)
        execute("UPDATE executions SET ai_analysis_id = ? WHERE id = ?", (analysis_id, execution_id))
        normalized["id"] = analysis_id
        return normalized

    def analyze_execution_with_fallback(self, execution_id: int) -> dict:
        """Try real AI analysis via Ollama; if unreachable, fall back to a
        deterministic heuristic based on exception type so the feature is
        still usable without a local model running. The fallback result is
        clearly labeled (model_name='heuristic-fallback') so it is never
        confused with a genuine model output.
        """
        try:
            return self.analyze_execution(execution_id)
        except AIAnalysisError as exc:
            if "not found" in str(exc) or "only applies to" in str(exc) or "disabled" in str(exc):
                raise
            logger.info("Falling back to heuristic analysis for execution %s: %s", execution_id, exc)
            return self._heuristic_fallback(execution_id)

    def _heuristic_fallback(self, execution_id: int) -> dict:
        execution = fetch_one("SELECT * FROM executions WHERE id = ?", (execution_id,))
        exc_type = (execution["exception_type"] or "").lower()

        rules = {
            "timeoutexception": {
                "root_cause": "The test waited for an element/condition that did not appear within the configured timeout.",
                "possible_reason": "Page load latency, an async UI update, or a wait condition targeting the wrong element.",
                "recommended_fix": "Replace fixed waits with an explicit WebDriverWait on the specific condition, and confirm the locator matches the element that actually becomes interactable.",
                "prevention": "Add explicit waits keyed to visible network/UI signals rather than arbitrary sleep values; monitor page load time trends.",
                "suggested_code": "from selenium.webdriver.support.ui import WebDriverWait\nfrom selenium.webdriver.support import expected_conditions as EC\n\nWebDriverWait(driver, 15).until(\n    EC.element_to_be_clickable((By.CSS_SELECTOR, 'YOUR_LOCATOR'))\n)",
                "severity": "MEDIUM",
            },
            "nosuchelementexception": {
                "root_cause": "The locator used did not match any element in the current DOM at the time of the call.",
                "possible_reason": "The locator is stale relative to a recent UI change, or the element renders inside an iframe/shadow DOM that was not switched into.",
                "recommended_fix": "Verify the locator against the current DOM, add an explicit wait for presence, and confirm iframe context if applicable.",
                "prevention": "Prefer stable data-testid attributes over brittle CSS/XPath, and add DOM-change detection to the page object.",
                "suggested_code": "WebDriverWait(driver, 10).until(\n    EC.presence_of_element_located((By.CSS_SELECTOR, 'YOUR_LOCATOR'))\n)",
                "severity": "MEDIUM",
            },
            "elementclickinterceptedexception": {
                "root_cause": "Another element (overlay, modal, sticky header) was intercepting the click at the target coordinates.",
                "possible_reason": "A loading spinner, cookie banner, or animation was still visible/overlapping when the click was attempted.",
                "recommended_fix": "Wait for the intercepting element to disappear, or scroll the target into view before clicking; consider a JS-click as a last resort.",
                "prevention": "Add a standard 'dismiss overlays' step in page object setup, and wait for animations to complete before interacting.",
                "suggested_code": "WebDriverWait(driver, 10).until(\n    EC.invisibility_of_element_located((By.CSS_SELECTOR, '.overlay'))\n)\nelement.click()",
                "severity": "LOW",
            },
            "staleelementreferenceexception": {
                "root_cause": "The element reference was captured before the DOM re-rendered, invalidating the handle.",
                "possible_reason": "A page re-render (React/Vue state update, AJAX refresh) replaced the element after it was located but before it was used.",
                "recommended_fix": "Re-locate the element immediately before interacting with it rather than caching the reference, or wrap the interaction in a retry-on-stale helper.",
                "prevention": "Avoid holding element references across waits; re-query inside explicit-wait lambdas.",
                "suggested_code": "def click_fresh(driver, locator):\n    WebDriverWait(driver, 10).until(\n        EC.element_to_be_clickable(locator)\n    ).click()",
                "severity": "MEDIUM",
            },
        }

        rule = rules.get(exc_type, {
            "root_cause": "Failure pattern does not match a known heuristic category; manual triage recommended.",
            "possible_reason": "Insufficient signal to classify automatically without a language model.",
            "recommended_fix": "Review the stack trace and screenshot manually, or enable the Ollama-backed AI analysis for deeper reasoning.",
            "prevention": "Add more specific exception handling/logging around this test step to improve future auto-classification.",
            "suggested_code": "# Add targeted logging around the failing step to capture more context next run.",
            "severity": "LOW",
        })

        analysis = {
            "root_cause": rule["root_cause"],
            "severity": rule["severity"],
            "possible_reason": rule["possible_reason"],
            "recommended_fix": rule["recommended_fix"],
            "prevention": rule["prevention"],
            "confidence_score": 0.55,
            "suggested_code": rule["suggested_code"],
            "raw_model_output": "(heuristic fallback - Ollama unreachable, no model was called)",
        }
        analysis_id = execute(
            """INSERT INTO ai_analyses
               (execution_id, root_cause, severity, possible_reason, recommended_fix,
                prevention, confidence_score, suggested_code, raw_model_output, model_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                execution_id, analysis["root_cause"], analysis["severity"], analysis["possible_reason"],
                analysis["recommended_fix"], analysis["prevention"], analysis["confidence_score"],
                analysis["suggested_code"], analysis["raw_model_output"], "heuristic-fallback",
            ),
        )
        execute("UPDATE executions SET ai_analysis_id = ? WHERE id = ?", (analysis_id, execution_id))
        analysis["id"] = analysis_id
        analysis["model_name"] = "heuristic-fallback"
        return analysis

    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize(result: dict) -> dict:
        severity = str(result.get("severity", "MEDIUM")).upper()
        if severity not in VALID_SEVERITIES:
            severity = "MEDIUM"

        try:
            confidence = float(result.get("confidence_score", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        return {
            "root_cause": str(result.get("root_cause", "Unable to determine root cause."))[:2000],
            "severity": severity,
            "possible_reason": str(result.get("possible_reason", ""))[:2000],
            "recommended_fix": str(result.get("recommended_fix", ""))[:2000],
            "prevention": str(result.get("prevention", ""))[:2000],
            "confidence_score": confidence,
            "suggested_code": str(result.get("suggested_code", ""))[:4000],
            "raw_model_output": result.get("_raw_model_output", ""),
        }

    def _persist(self, execution_id: int, analysis: dict) -> int:
        return execute(
            """INSERT INTO ai_analyses
               (execution_id, root_cause, severity, possible_reason, recommended_fix,
                prevention, confidence_score, suggested_code, raw_model_output, model_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                execution_id,
                analysis["root_cause"],
                analysis["severity"],
                analysis["possible_reason"],
                analysis["recommended_fix"],
                analysis["prevention"],
                analysis["confidence_score"],
                analysis["suggested_code"],
                analysis["raw_model_output"],
                self.client.model,
            ),
        )
