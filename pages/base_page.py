"""
Base Page Module — dynamic locator helper for all Page Objects.

Every page class inherits from BasePage. Locators are fetched from
the active JSON configuration via ConfigLoader, so no locator is
ever hardcoded inside Python source files.
"""

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.config_loader import ConfigLoader


class BasePage:
    """Universal base for all Page Object classes."""

    def __init__(self, driver):
        self.driver = driver
        # Use the standard Python logger so there is no dependency on
        # TestLogger at construction time (avoids the 'get_logger' error).
        self.logger = logging.getLogger(self.__class__.__name__)
        settings = ConfigLoader.get_settings()
        self.timeout = settings.get("timeout", 15)
        self.wait = WebDriverWait(self.driver, self.timeout)

    # ── element lookup ──────────────────────────────────────────────────────

    def find_element(self, page_name: str, element_name: str):
        """Return element after waiting for presence (dynamic locator)."""
        locator = ConfigLoader.get_locator(page_name, element_name)
        self.logger.debug("Finding element: %s.%s → %s", page_name, element_name, locator)
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable_element(self, page_name: str, element_name: str):
        """Return element after waiting for it to be clickable."""
        locator = ConfigLoader.get_locator(page_name, element_name)
        return self.wait.until(EC.element_to_be_clickable(locator))

    # ── actions ─────────────────────────────────────────────────────────────

    def click(self, page_name: str, element_name: str):
        """Click a dynamically-located element."""
        element = self.find_clickable_element(page_name, element_name)
        element.click()
        self.logger.debug("Clicked: %s.%s", page_name, element_name)

    def input_text(self, page_name: str, element_name: str, text: str):
        """Clear and type text into a dynamically-located element."""
        element = self.find_element(page_name, element_name)
        element.clear()
        element.send_keys(text)
        self.logger.debug("Typed into %s.%s", page_name, element_name)

    def is_element_visible(self, page_name: str, element_name: str) -> bool:
        """Return True if the element is visible within the timeout."""
        try:
            locator = ConfigLoader.get_locator(page_name, element_name)
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False
