"""
core/driver_factory.py
========================
Centralized Selenium WebDriver creation. Every test/page-object should get
its driver instance from here rather than constructing one inline, so
headless mode, browser choice, timeouts and driver-manager caching stay
consistent across the whole suite.
"""

from __future__ import annotations

import logging
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config import settings

logger = logging.getLogger("smart_retry.driver_factory")


def _enable_browser_logging_capabilities() -> dict:
    return {"goog:loggingPrefs": {"browser": "ALL"}}


def create_driver(browser: str | None = None, headless: bool | None = None) -> Any:
    """Create and return a configured Selenium WebDriver instance.

    :param browser: 'chrome' | 'edge' | 'firefox'. Defaults to settings.DEFAULT_BROWSER.
    :param headless: overrides settings.HEADLESS if provided.
    """
    from services.settings_service import get_runtime_settings

    runtime = get_runtime_settings()
    browser = (browser or runtime["browser"]).lower()
    headless = runtime["headless"] if headless is None else headless

    logger.info("Creating %s driver (headless=%s)", browser, headless)

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        try:
            driver_path = ChromeDriverManager().install()
            # If webdriver-manager returns non-exe metadata file on Windows
            if driver_path and not driver_path.endswith(".exe"):
                from pathlib import Path
                p = Path(driver_path)
                exe = p.parent / "chromedriver.exe"
                if exe.exists():
                    driver_path = str(exe)
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as exc:
            logger.warning("ChromeDriverManager failed (%s), falling back to Selenium Manager", exc)
            driver = webdriver.Chrome(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        try:
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
        except Exception as exc:
            logger.warning("EdgeChromiumDriverManager failed (%s), falling back to Selenium Manager", exc)
            driver = webdriver.Edge(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
        except Exception as exc:
            logger.warning("GeckoDriverManager failed (%s), falling back to Selenium Manager", exc)
            driver = webdriver.Firefox(options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver.implicitly_wait(settings.IMPLICIT_WAIT)
    driver.set_page_load_timeout(runtime["execution_timeout"])
    return driver


def quit_driver(driver: Any | None) -> None:
    if driver is None:
        return
    try:
        driver.quit()
    except Exception:
        logger.exception("Error while quitting driver")
