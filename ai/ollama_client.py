"""
ai/ollama_client.py
=====================
Thin HTTP client for a local Ollama server. Deliberately dependency-light
(just `requests`) and defensive: if Ollama isn't running, every method
raises `OllamaUnavailableError` with a clear message instead of a raw
connection-refused traceback, so the calling code can degrade gracefully.
"""

from __future__ import annotations

import json
import logging

import requests

from config import settings

logger = logging.getLogger("smart_retry.ollama")


class OllamaUnavailableError(RuntimeError):
    """Raised when the local Ollama server cannot be reached or errors out."""


class OllamaClient:
    def __init__(self, host: str | None = None, model: str | None = None, timeout: int | None = None) -> None:
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.AI_REQUEST_TIMEOUT

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        """Call /api/generate with format=json and return the parsed dict.

        Ollama's JSON mode still returns the model's raw text in the `response`
        field; we parse that ourselves and raise a clear error if the model
        didn't produce valid JSON (rare with format="json" but not impossible).
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        if system:
            payload["system"] = system

        try:
            resp = requests.post(f"{self.host}/api/generate", json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.ConnectionError as exc:
            raise OllamaUnavailableError(
                f"Could not reach Ollama at {self.host}. Is `ollama serve` running "
                f"and has `{self.model}` been pulled? (ollama pull {self.model})"
            ) from exc
        except requests.Timeout as exc:
            raise OllamaUnavailableError(f"Ollama request timed out after {self.timeout}s") from exc
        except requests.HTTPError as exc:
            raise OllamaUnavailableError(f"Ollama returned an error: {exc}") from exc

        data = resp.json()
        raw_text = data.get("response", "")
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.warning("Ollama did not return valid JSON: %s", raw_text[:400])
            raise OllamaUnavailableError("The model did not return valid JSON output.") from exc

        parsed["_raw_model_output"] = raw_text
        return parsed
