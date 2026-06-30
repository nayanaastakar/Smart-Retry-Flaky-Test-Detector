"""
Screenshot Manager — Module 4

Captures a PNG screenshot from the active WebDriver session whenever a
test enters FAILURE or FLAKY state.  Screenshots are NEVER taken for
passing tests.

File-naming convention:
    <test_name>_YYYYMMDD_HHMMSS.png
    e.g. login_test_20260630_101525.png

Files are stored in the folder defined by Config.SCREENSHOT_PATH.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.config import Config


class ScreenshotManager:
    """
    Manages screenshot capture, retrieval and cleanup for test evidence.

    Public API
    ----------
    capture(driver, test_name)  → Path | None
    get_latest(test_name)       → Path | None
    delete_old(days)            → int   (number of files deleted)
    """

    def __init__(self) -> None:
        self._config = Config()
        self._logger = logging.getLogger(self.__class__.__name__)
        # Guarantee the screenshots folder exists
        self._config.SCREENSHOT_PATH.mkdir(parents=True, exist_ok=True)

    # ── public methods ────────────────────────────────────────────────────────

    def capture(self, driver, test_name: str) -> Optional[Path]:
        """
        Take a full-page PNG screenshot and save it to screenshots/.

        Parameters
        ----------
        driver    : Active selenium.webdriver instance
        test_name : Identifier used in the filename

        Returns
        -------
        Path to the saved PNG, or None if capture failed.
        """
        if not self._config.ENABLE_SCREENSHOTS:
            self._logger.info("Screenshots disabled – skipping capture for '%s'.", test_name)
            return None

        # Sanitise test name for use in a filename
        safe_name = self._safe_name(test_name)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{ts}.png"
        dest = self._config.SCREENSHOT_PATH / filename

        try:
            print(f"\nCapturing Screenshot...")
            driver.save_screenshot(str(dest))
            print(f"Screenshot Saved → {dest}")
            self._logger.info("Screenshot saved: %s", dest)
            return dest
        except Exception as exc:
            self._logger.error("Failed to capture screenshot for '%s': %s", test_name, exc)
            return None

    def get_latest(self, test_name: str) -> Optional[Path]:
        """
        Return the most recently created screenshot for a given test name.

        Parameters
        ----------
        test_name : Test identifier to search for

        Returns
        -------
        Path to the latest PNG, or None if none found.
        """
        safe_name = self._safe_name(test_name)
        matches = sorted(
            self._config.SCREENSHOT_PATH.glob(f"{safe_name}_*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return matches[0] if matches else None

    def delete_old(self, days: int = 7) -> int:
        """
        Delete screenshots older than *days* days.

        Parameters
        ----------
        days : Age threshold in days (default 7)

        Returns
        -------
        Number of files deleted.
        """
        import time

        cutoff = time.time() - days * 86_400
        deleted = 0
        for png in self._config.SCREENSHOT_PATH.glob("*.png"):
            if png.stat().st_mtime < cutoff:
                try:
                    png.unlink()
                    deleted += 1
                except OSError as exc:
                    self._logger.warning("Could not delete %s: %s", png, exc)

        self._logger.info("delete_old(%d days): removed %d file(s).", days, deleted)
        return deleted

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _safe_name(test_name: str) -> str:
        """Replace characters that are illegal in filenames."""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
