"""
Ollama Client - Module 6

Provides a client to communicate with a local Ollama instance for AI analysis.
"""

import json
import urllib.request
import urllib.error
import logging
from typing import Optional, Dict, Any

from config.config import Config


class OllamaClient:
    """
    Client for interacting with Ollama API.
    
    Methods:
        connect()
        generate()
        is_running()
        available_models()
    """

    def __init__(self):
        self.config = Config()
        self.base_url = self.config.OLLAMA_URL
        self.model = self.config.OLLAMA_MODEL
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_running_cache = None  # Cache connectivity check

    def is_running(self) -> bool:
        """Check if the Ollama server is running (cached after first check)."""
        if self._is_running_cache is not None:
            return self._is_running_cache
        try:
            req = urllib.request.Request(self.base_url)
            with urllib.request.urlopen(req, timeout=2) as response:
                self._is_running_cache = response.status == 200
                return self._is_running_cache
        except Exception as e:
            self.logger.warning(f"Ollama server is not running: {str(e)}")
            self._is_running_cache = False
            return False

    def connect(self) -> bool:
        """Alias for is_running()."""
        return self.is_running()

    def available_models(self) -> list:
        """Return a list of available models on the Ollama server."""
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return [m.get('name') for m in data.get('models', [])]
            return []
        except Exception as e:
            self.logger.warning(f"Failed to fetch available models: {str(e)}")
            return []

    def generate(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to Ollama and return the generated text.
        Returns JSON string if prompt requests it, else plain text.
        """
        if not self.is_running():
            print("Ollama not available")
            return None

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # Ensure we get JSON back
        }
        
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=self.config.AI_TIMEOUT) as response:
                if response.status == 200:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    return resp_data.get('response')
                else:
                    self.logger.error(f"Ollama returned status {response.status}")
                    return None
        except urllib.error.URLError as e:
            self.logger.error(f"Failed to generate AI response: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during AI generation: {str(e)}")
            return None
