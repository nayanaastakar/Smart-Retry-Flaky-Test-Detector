"""
Browser Log Manager — Module 4

Collects Chrome DevTools console logs (JavaScript errors, warnings,
network errors, console errors) from the active WebDriver session and
persists them to a structured text file inside logs/.

File-naming convention:
    <test_name>_YYYYMMDD_HHMMSS.txt
    e.g. login_test_20260630_101525.txt

Captured log levels: SEVERE (errors), WARNING, INFO
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config.config import Config


class BrowserLogManager:
    """
    Manages browser console log capture, persistence and retrieval.

    Public API
    ----------
    capture_logs(driver)                       → List[dict]
    save_logs(driver, test_name)               → Path | None
    read_logs(log_path)                        → str
    """

    _LOG_CATEGORIES = {
        "SEVERE":  "JavaScript / Network Errors",
        "WARNING": "Warnings",
        "INFO":    "Info / Console Logs",
    }

    def __init__(self) -> None:
        self._config = Config()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._config.LOG_PATH.mkdir(parents=True, exist_ok=True)

    # ── public methods ────────────────────────────────────────────────────────

    def capture_logs(self, driver) -> List[dict]:
        """
        Retrieve raw browser console log entries from ChromeDriver.

        Parameters
        ----------
        driver : Active selenium.webdriver instance

        Returns
        -------
        List of dicts with keys: level, message, timestamp
        """
        try:
            raw = driver.get_log("browser")
            self._logger.debug("Captured %d browser log entries.", len(raw))
            return raw
        except Exception as exc:
            self._logger.warning("Could not retrieve browser logs: %s", exc)
            return []

    def save_logs(self, driver, test_name: str) -> Optional[Path]:
        """
        Capture Chrome console logs and write them to a .txt file.

        Parameters
        ----------
        driver    : Active selenium.webdriver instance
        test_name : Identifier used in the filename

        Returns
        -------
        Path to the saved file, or None if disabled / capture failed.
        """
        if not self._config.ENABLE_BROWSER_LOGS:
            self._logger.info("Browser logs disabled – skipping for '%s'.", test_name)
            return None

        entries = self.capture_logs(driver)
        safe_name = self._safe_name(test_name)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{ts}.txt"
        dest = self._config.LOG_PATH / filename

        try:
            print(f"\nCollecting Browser Logs...")
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write("=" * 70 + "\n")
                fh.write(f"BROWSER CONSOLE LOGS — {test_name}\n")
                fh.write(f"Captured : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                fh.write(f"Entries  : {len(entries)}\n")
                fh.write("=" * 70 + "\n\n")

                if not entries:
                    fh.write("No browser console log entries found.\n")
                else:
                    for idx, entry in enumerate(entries, 1):
                        level = entry.get("level", "UNKNOWN")
                        message = entry.get("message", "")
                        raw_ts = entry.get("timestamp", "")
                        fh.write(f"[{idx:03d}] Level   : {level}\n")
                        fh.write(f"       Timestamp: {raw_ts}\n")
                        fh.write(f"       Message  : {message}\n")
                        fh.write("-" * 50 + "\n")

            print(f"Browser Logs Saved → {dest}")
            self._logger.info("Browser logs saved: %s", dest)
            return dest

        except Exception as exc:
            self._logger.error("Failed to save browser logs for '%s': %s", test_name, exc)
            return None

    def read_logs(self, log_path: Path) -> str:
        """
        Read the contents of a saved browser-log file.

        Parameters
        ----------
        log_path : Path returned by save_logs()

        Returns
        -------
        Full text content of the log file, or an empty string on error.
        """
        try:
            return Path(log_path).read_text(encoding="utf-8")
        except Exception as exc:
            self._logger.warning("Cannot read log file '%s': %s", log_path, exc)
            return ""

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _safe_name(test_name: str) -> str:
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
