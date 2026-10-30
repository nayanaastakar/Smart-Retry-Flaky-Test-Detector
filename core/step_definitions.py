"""
core/step_definitions.py
==========================
Plain-data metadata describing every step type the Test Builder can offer.
Deliberately has zero dependency on Selenium so the builder UI (which just
needs to render a dropdown of actions and show/hide the right input fields)
works even in environments where Selenium isn't installed yet. Actual
execution logic lives in core/step_executor.py, which imports Selenium and
is only touched when a test is actually run.
"""

from __future__ import annotations

STEP_ACTIONS: list[dict] = [
    {"key": "open_url", "label": "Open URL", "needs_locator": False, "needs_input": True,
     "input_label": "URL (leave blank to use project URL)", "needs_timeout": False},
    {"key": "click", "label": "Click", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "double_click", "label": "Double Click", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "right_click", "label": "Right Click", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "type_text", "label": "Type Text", "needs_locator": True, "needs_input": True,
     "input_label": "Text to type", "needs_timeout": True},
    {"key": "clear", "label": "Clear Field", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "select_dropdown", "label": "Select Dropdown Option", "needs_locator": True, "needs_input": True,
     "input_label": "Option text", "needs_timeout": True},
    {"key": "check_checkbox", "label": "Check Checkbox", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "wait", "label": "Wait", "needs_locator": False, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "scroll_to", "label": "Scroll To Element", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "hover", "label": "Mouse Hover", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "press_keys", "label": "Press Key", "needs_locator": False, "needs_input": True,
     "input_label": "Key (ENTER, TAB, ESCAPE, ...)", "needs_timeout": False},
    {"key": "switch_frame", "label": "Switch Frame", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": False},
    {"key": "switch_window", "label": "Switch Window", "needs_locator": False, "needs_input": True,
     "input_label": "Window index (blank = latest)", "needs_timeout": False},
    {"key": "screenshot", "label": "Take Screenshot (checkpoint)", "needs_locator": False, "needs_input": False,
     "input_label": None, "needs_timeout": False},
    {"key": "assert_url_contains", "label": "Assert: URL Contains", "needs_locator": False, "needs_input": True,
     "input_label": "Expected substring", "needs_timeout": False},
    {"key": "assert_title_contains", "label": "Assert: Title Contains", "needs_locator": False, "needs_input": True,
     "input_label": "Expected substring", "needs_timeout": False},
    {"key": "assert_text_present", "label": "Assert: Page Text Contains", "needs_locator": False, "needs_input": True,
     "input_label": "Expected text", "needs_timeout": False},
    {"key": "assert_element_visible", "label": "Assert: Element Visible", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "assert_element_exists", "label": "Assert: Element Exists", "needs_locator": True, "needs_input": False,
     "input_label": None, "needs_timeout": True},
    {"key": "assert_attribute", "label": "Assert: Attribute Equals", "needs_locator": True, "needs_input": True,
     "input_label": "attribute=expected_value", "needs_timeout": True},
    {"key": "custom_js", "label": "Custom JavaScript", "needs_locator": False, "needs_input": True,
     "input_label": "JavaScript to execute", "needs_timeout": False},
]

LOCATOR_TYPES = ["css", "xpath", "id", "name", "link_text", "partial_link_text", "class_name", "tag_name"]

STEP_ACTION_KEYS = {a["key"] for a in STEP_ACTIONS}
