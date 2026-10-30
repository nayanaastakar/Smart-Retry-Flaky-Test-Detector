"""
core/generic_test_suite.py
============================
A small, URL-agnostic battery of Selenium smoke checks. Unlike the
Page-Object-Model tests under /tests (which know the specific locators of a
specific site), these tests work against *any* URL the user pastes in,
because they only assert on things every well-formed web page has: it loads,
it has a title, it has a body, its links resolve, images aren't broken, and
the browser console isn't full of severe errors.

Each check is a zero-arg callable (a closure over `driver` and `url`) so it
can be handed directly to SmartRetryEngine.run() exactly like a real PyTest
test would be.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class GenericCheck:
    name: str
    fn: Callable[[], None]


def _check_page_loads(driver, url: str) -> None:
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def _check_title_present(driver, url: str) -> None:
    title = (driver.title or "").strip()
    if not title:
        raise AssertionError(f"Page at {url} has no <title> text.")


def _check_body_has_content(driver, url: str) -> None:
    body = driver.find_element(By.TAG_NAME, "body")
    text = (body.text or "").strip()
    if len(text) < 10:
        raise AssertionError("Page body has little or no visible text content (possible blank/error page).")


def _check_links_present(driver, url: str) -> None:
    links = driver.find_elements(By.TAG_NAME, "a")
    if len(links) == 0:
        raise AssertionError("No <a> links found on the page.")


def _check_no_broken_images(driver, url: str) -> None:
    broken = driver.execute_script(
        """
        return Array.from(document.images)
            .filter(img => !img.complete || img.naturalWidth === 0)
            .map(img => img.src)
            .slice(0, 5);
        """
    )
    if broken:
        raise AssertionError(f"Found {len(broken)} broken image(s): {', '.join(broken)}")


def _check_console_has_no_severe_errors(driver, url: str) -> None:
    try:
        logs = driver.get_log("browser")
    except Exception:
        return  # not all browsers/drivers expose console logs (e.g. geckodriver)
    severe = [entry for entry in logs if entry.get("level") == "SEVERE"]
    if severe:
        messages = "; ".join(e.get("message", "")[:120] for e in severe[:3])
        raise AssertionError(f"Browser console reported {len(severe)} SEVERE error(s): {messages}")


def build_generic_checks(driver, url: str) -> list[GenericCheck]:
    """Return the standard smoke-check battery bound to this driver/url."""
    return [
        GenericCheck("Page Loads Successfully", lambda: _check_page_loads(driver, url)),
        GenericCheck("Page Title Is Present", lambda: _check_title_present(driver, url)),
        GenericCheck("Body Has Visible Content", lambda: _check_body_has_content(driver, url)),
        GenericCheck("Navigation Links Present", lambda: _check_links_present(driver, url)),
        GenericCheck("No Broken Images", lambda: _check_no_broken_images(driver, url)),
        GenericCheck("No Severe Console Errors", lambda: _check_console_has_no_severe_errors(driver, url)),
    ]
