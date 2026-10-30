"""
core/step_executor.py
=======================
The engine behind the visual Test Builder. A "test case" is no longer a
hand-written Selenium script tied to one site -- it's an ordered list of
JSON step dictionaries, and this module knows how to execute *any* of them
against *any* driver/site. This is what makes the platform fully dynamic:
add a project, describe steps in plain data, run them anywhere.

Step shape (each item in a test case's steps_json list):
{
    "action": "click",                 # one of ACTION_HANDLERS keys
    "locator_type": "css",             # id | name | xpath | css | link_text |
                                        # partial_link_text | class_name | tag_name
    "locator_value": "#submit-btn",
    "input_value": "hello@example.com",
    "timeout": 10,
    "description": "Submit the login form"
}

Not every action needs every field -- e.g. `wait` only needs `timeout`,
`open_url` only needs `input_value`. Unused fields can be omitted/None.

Security note: there is deliberately no "run arbitrary Python" step type.
`custom_js` executes JavaScript inside the browser sandbox (standard
Selenium capability, no different from what any Selenium script can already
do), but arbitrary host-side Python execution from user-submitted step data
would be a remote-code-execution hole and is intentionally not implemented.
"""

from __future__ import annotations

import time
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

LOCATOR_MAP = {
    "id": By.ID,
    "name": By.NAME,
    "xpath": By.XPATH,
    "css": By.CSS_SELECTOR,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "class_name": By.CLASS_NAME,
    "tag_name": By.TAG_NAME,
}

KEY_ALIASES = {
    "ENTER": Keys.ENTER, "RETURN": Keys.RETURN, "TAB": Keys.TAB, "ESCAPE": Keys.ESCAPE, "ESC": Keys.ESCAPE,
    "BACKSPACE": Keys.BACKSPACE, "DELETE": Keys.DELETE, "SPACE": Keys.SPACE,
    "ARROW_DOWN": Keys.ARROW_DOWN, "ARROW_UP": Keys.ARROW_UP, "ARROW_LEFT": Keys.ARROW_LEFT, "ARROW_RIGHT": Keys.ARROW_RIGHT,
    "PAGE_UP": Keys.PAGE_UP, "PAGE_DOWN": Keys.PAGE_DOWN,
}


class StepExecutionError(AssertionError):
    """Raised when a step fails; subclasses AssertionError so it reads
    naturally as a test failure to the retry engine and reports."""


def _by(step: dict):
    locator_type = (step.get("locator_type") or "css").lower()
    by = LOCATOR_MAP.get(locator_type)
    if by is None:
        raise StepExecutionError(f"Unknown locator_type '{locator_type}'.")
    return by


def _find(driver, step: dict, timeout: int):
    locator_value = step.get("locator_value")
    if not locator_value:
        raise StepExecutionError(f"Step '{step.get('action')}' requires a locator_value.")
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((_by(step), locator_value))
    )


def _find_clickable(driver, step: dict, timeout: int):
    locator_value = step.get("locator_value")
    if not locator_value:
        raise StepExecutionError(f"Step '{step.get('action')}' requires a locator_value.")
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((_by(step), locator_value))
    )


def _act_open_url(driver, step, project_url):
    url = step.get("input_value") or project_url
    if not url:
        raise StepExecutionError("open_url step has no URL and no project URL to fall back to.")
    if url.startswith("/") and project_url:
        from urllib.parse import urljoin
        url = urljoin(project_url, url)
    driver.get(url)


def _act_click(driver, step, project_url):
    timeout = step.get("timeout") or 10
    _find_clickable(driver, step, timeout).click()


def _act_double_click(driver, step, project_url):
    from selenium.webdriver.common.action_chains import ActionChains
    timeout = step.get("timeout") or 10
    element = _find_clickable(driver, step, timeout)
    ActionChains(driver).double_click(element).perform()


def _act_right_click(driver, step, project_url):
    from selenium.webdriver.common.action_chains import ActionChains
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    ActionChains(driver).context_click(element).perform()


def _act_type_text(driver, step, project_url):
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    element.send_keys(step.get("input_value") or "")


def _act_clear(driver, step, project_url):
    timeout = step.get("timeout") or 10
    _find(driver, step, timeout).clear()


def _act_select_dropdown(driver, step, project_url):
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    Select(element).select_by_visible_text(step.get("input_value") or "")


def _act_check_checkbox(driver, step, project_url):
    timeout = step.get("timeout") or 10
    element = _find_clickable(driver, step, timeout)
    if not element.is_selected():
        element.click()


def _act_wait(driver, step, project_url):
    time.sleep(float(step.get("timeout") or 1))


def _act_scroll_to(driver, step, project_url):
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)


def _act_hover(driver, step, project_url):
    from selenium.webdriver.common.action_chains import ActionChains
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    ActionChains(driver).move_to_element(element).perform()


def _act_press_keys(driver, step, project_url):
    key_name = (step.get("input_value") or "ENTER").upper()
    key = KEY_ALIASES.get(key_name)
    if key is None:
        raise StepExecutionError(f"Unknown key '{key_name}'. Supported: {', '.join(KEY_ALIASES)}")
    driver.switch_to.active_element.send_keys(key)


def _act_switch_frame(driver, step, project_url):
    value = step.get("locator_value") or step.get("input_value")
    if value is None:
        driver.switch_to.default_content()
        return
    try:
        index = int(value)
        driver.switch_to.frame(index)
    except ValueError:
        driver.switch_to.frame(value)


def _act_switch_window(driver, step, project_url):
    handles = driver.window_handles
    if not handles:
        raise StepExecutionError("No window handles available.")
    index_raw = step.get("input_value")
    try:
        index = int(index_raw) if index_raw not in (None, "") else -1
        driver.switch_to.window(handles[index])
    except (IndexError, ValueError) as exc:
        raise StepExecutionError(f"Invalid window index '{index_raw}': {exc}") from exc


def _act_screenshot(driver, step, project_url):
    try:
        from config import settings
        folder = settings.SCREENSHOTS_DIR / "checkpoints"
        folder.mkdir(parents=True, exist_ok=True)
        ts = int(time.time() * 1000)
        name = step.get("input_value") or f"checkpoint_{ts}"
        safe_name = "".join(c if c.isalnum() else "_" for c in name)[:50]
        driver.save_screenshot(str(folder / f"{safe_name}_{ts}.png"))
    except Exception:
        pass


def _act_assert_url_contains(driver, step, project_url):
    expected = step.get("input_value") or ""
    if expected not in driver.current_url:
        raise StepExecutionError(f"Expected URL to contain '{expected}', got '{driver.current_url}'.")


def _act_assert_title_contains(driver, step, project_url):
    expected = step.get("input_value") or ""
    if expected not in (driver.title or ""):
        raise StepExecutionError(f"Expected title to contain '{expected}', got '{driver.title}'.")


def _act_assert_text_present(driver, step, project_url):
    expected = step.get("input_value") or ""
    body_text = driver.find_element(By.TAG_NAME, "body").text
    if expected not in body_text:
        raise StepExecutionError(f"Expected page text to contain '{expected}'.")


def _act_assert_element_visible(driver, step, project_url):
    timeout = step.get("timeout") or 10
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((_by(step), step.get("locator_value"))))
    except Exception as exc:
        raise StepExecutionError(f"Element not visible: {step.get('locator_value')}") from exc


def _act_assert_element_exists(driver, step, project_url):
    timeout = step.get("timeout") or 10
    try:
        _find(driver, step, timeout)
    except Exception as exc:
        raise StepExecutionError(f"Element does not exist: {step.get('locator_value')}") from exc


def _act_assert_attribute(driver, step, project_url):
    timeout = step.get("timeout") or 10
    element = _find(driver, step, timeout)
    attr_name, _, expected_value = (step.get("input_value") or "").partition("=")
    actual = element.get_attribute(attr_name.strip())
    if actual != expected_value.strip():
        raise StepExecutionError(f"Attribute '{attr_name}' expected '{expected_value}', got '{actual}'.")


def _act_custom_js(driver, step, project_url):
    script = step.get("input_value") or ""
    driver.execute_script(script)


ACTION_HANDLERS: dict[str, Callable] = {
    "open_url": _act_open_url,
    "click": _act_click,
    "double_click": _act_double_click,
    "right_click": _act_right_click,
    "type_text": _act_type_text,
    "clear": _act_clear,
    "select_dropdown": _act_select_dropdown,
    "check_checkbox": _act_check_checkbox,
    "wait": _act_wait,
    "scroll_to": _act_scroll_to,
    "hover": _act_hover,
    "press_keys": _act_press_keys,
    "switch_frame": _act_switch_frame,
    "switch_window": _act_switch_window,
    "screenshot": _act_screenshot,
    "assert_url_contains": _act_assert_url_contains,
    "assert_title_contains": _act_assert_title_contains,
    "assert_text_present": _act_assert_text_present,
    "assert_element_visible": _act_assert_element_visible,
    "assert_element_exists": _act_assert_element_exists,
    "assert_attribute": _act_assert_attribute,
    "custom_js": _act_custom_js,
}

STEP_ACTION_CHOICES = list(ACTION_HANDLERS.keys())


def execute_steps(driver, steps: list[dict], project_url: str | None = None) -> None:
    """Run an ordered list of steps against `driver`. Raises StepExecutionError
    (or lets the underlying Selenium exception propagate) on the first
    failing step -- the retry engine treats either as a normal test failure.
    """
    if not steps:
        raise StepExecutionError("This test case has no steps defined.")

    for index, step in enumerate(steps, start=1):
        action = step.get("action")
        handler = ACTION_HANDLERS.get(action)
        if handler is None:
            raise StepExecutionError(f"Step {index}: unknown action '{action}'.")
        try:
            handler(driver, step, project_url)
        except StepExecutionError:
            raise
        except Exception as exc:  # noqa: BLE001
            desc = step.get("description") or action
            raise StepExecutionError(f"Step {index} ({desc}) failed: {exc}") from exc
