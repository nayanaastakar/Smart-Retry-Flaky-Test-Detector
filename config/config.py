"""
Configuration Module for Smart Retry & Flaky Test Detector - Updated for Module 4

Adds:
- Screenshot configuration
- Browser log configuration
- Log format settings for TestLogger
- SCRIPT_TIMEOUT for driver compatibility
"""

import os
import json
from pathlib import Path


class Config:
    """
    Configuration class for the Smart Retry & Flaky Test Detector framework.

    This class centralizes all configuration parameters to ensure easy maintenance
    and modification of framework settings.
    """

    # Project Root Directory
    PROJECT_ROOT = Path(__file__).parent.parent

    # Browser Configuration
    BROWSER: str = "chrome"
    HEADLESS_MODE: bool = False
    BROWSER_WINDOW_SIZE: str = "1920,1080"

    # Timeout Configurations (in seconds)
    IMPLICIT_WAIT: int = 5
    EXPLICIT_WAIT: int = 5
    PAGE_LOAD_TIMEOUT: int = 15
    SCRIPT_TIMEOUT: int = 15

    # Base URL for SauceDemo
    SAUCE_DEMO_URL: str = "https://www.saucedemo.com"

    # SauceDemo Login Credentials
    SAUCE_DEMO_USERNAME: str = "standard_user"
    SAUCE_DEMO_PASSWORD: str = "secret_sauce"

    # Retry Engine Configuration - Module 2
    MAX_RETRIES: int = 2
    RETRY_DELAY: float = 1.0
    MAX_RETRY_COUNT: int = 2

    # Flaky Detection Configuration - Module 3
    ENABLE_FLAKY_DETECTION: bool = True
    CONFIDENCE_THRESHOLD: int = 80

    # ─── Module 4: Screenshot & Browser Log Configuration ────────────────────
    ENABLE_SCREENSHOTS: bool = True
    ENABLE_BROWSER_LOGS: bool = True
    SCREENSHOT_FOLDER: str = "screenshots"
    LOG_FOLDER: str = "logs"

    # ─── Module 5: Report Configuration ──────────────────────────────────────
    REPORT_FOLDER: str = "reports"
    AUTO_GENERATE_REPORT: bool = True
    OPEN_REPORT_AFTER_EXECUTION: bool = False

    # ─── Module 6: AI Analysis Configuration (Ollama / OpenAI) ────────────────────────
    ENABLE_AI: bool = True
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OPENAI_API_KEY: str = ""
    AI_TIMEOUT: int = 15

    # ─── Module 7: Analytics & Execution History ─────────────────────────────
    ENABLE_HISTORY: bool = True
    ENABLE_ANALYTICS: bool = True
    HISTORY_FILE: str = "history/execution_history.json"
    AUTO_REFRESH: bool = False  # Disabled – was causing browser to keep refreshing
    THEME: str = "dark"
    
    # Path helpers (resolved to absolute paths)
    SCREENSHOT_PATH: Path = PROJECT_ROOT / SCREENSHOT_FOLDER
    LOG_PATH: Path = PROJECT_ROOT / LOG_FOLDER
    REPORT_PATH: Path = PROJECT_ROOT / REPORT_FOLDER

    # Logging format used by TestLogger
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s [%(levelname)8s] %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_NAME: str = "test_execution.log"

    def __init__(self):
        self.SETTINGS_JSON_PATH = self.PROJECT_ROOT / "config" / "settings.json"
        self.HISTORY_PATH = self.PROJECT_ROOT / self.HISTORY_FILE
        
        # Ensure directories exist at runtime
        self.SCREENSHOT_PATH.mkdir(parents=True, exist_ok=True)
        self.LOG_PATH.mkdir(parents=True, exist_ok=True)
        self.REPORT_PATH.mkdir(parents=True, exist_ok=True)
        self.HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Load persistent settings
        self.load_settings()

    def load_settings(self) -> None:
        """Loads user settings from config/settings.json if it exists."""
        if self.SETTINGS_JSON_PATH.exists():
            try:
                with open(self.SETTINGS_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.MAX_RETRIES = int(data.get("retry_count", self.MAX_RETRIES))
                    self.MAX_RETRY_COUNT = self.MAX_RETRIES
                    self.HEADLESS_MODE = bool(data.get("headless_mode", self.HEADLESS_MODE))
                    self.ENABLE_AI = bool(data.get("ai_enabled", self.ENABLE_AI))
                    self.BROWSER = str(data.get("browser", self.BROWSER))
                    self.THEME = str(data.get("theme", "dark"))
            except Exception as e:
                print(f"Error loading settings.json: {e}")
        else:
            self.THEME = "dark"
            self.save_settings()

    def save_settings(self) -> None:
        """Saves current user settings to config/settings.json."""
        data = {
            "retry_count": self.MAX_RETRIES,
            "headless_mode": self.HEADLESS_MODE,
            "ai_enabled": self.ENABLE_AI,
            "browser": self.BROWSER,
            "theme": getattr(self, "THEME", "dark")
        }
        try:
            with open(self.SETTINGS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings.json: {e}")

    def validate_configuration(self) -> list:
        """
        Validates settings and configurations before starting test runs.
        Returns a list of error strings if any are found.
        """
        errors = []
        if not isinstance(self.MAX_RETRIES, int) or self.MAX_RETRIES < 1 or self.MAX_RETRIES > 40:
            errors.append("Retry Count must be an integer between 1 and 40.")
        if self.BROWSER.lower() not in ["chrome", "firefox", "edge"]:
            errors.append(f"Browser '{self.BROWSER}' is not supported. Supported browsers: chrome, firefox, edge.")
        if not self.SCREENSHOT_PATH.parent.exists():
            errors.append(f"Project directory is invalid; parent of SCREENSHOT_PATH does not exist: {self.SCREENSHOT_PATH.parent}")
        return errors

    def get_screenshot_path(self, test_name: str) -> Path:
        """Return timestamped screenshot path for a test."""
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.SCREENSHOT_PATH / f"{test_name}_{ts}.png"

    def get_log_path(self, test_name: str) -> Path:
        """Return timestamped log path for a test."""
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.LOG_PATH / f"{test_name}_{ts}.log"

