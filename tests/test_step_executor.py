"""
tests/test_step_executor.py
===========================
Tests for step definitions and the step executor engine.
"""

from unittest.mock import MagicMock
import pytest
from core.step_definitions import STEP_ACTIONS, STEP_ACTION_KEYS, LOCATOR_TYPES
from core.step_executor import ACTION_HANDLERS, execute_steps, StepExecutionError


def test_step_definitions_consistency():
    """Verify that every step action in STEP_ACTIONS has a corresponding execution handler."""
    for action in STEP_ACTIONS:
        key = action["key"]
        assert key in ACTION_HANDLERS, f"Action '{key}' is declared in STEP_ACTIONS but missing from ACTION_HANDLERS"
    assert len(STEP_ACTION_KEYS) == len(ACTION_HANDLERS)


def test_execute_empty_steps_raises():
    mock_driver = MagicMock()
    with pytest.raises(StepExecutionError, match="no steps defined"):
        execute_steps(mock_driver, [])


def test_execute_unknown_action_raises():
    mock_driver = MagicMock()
    with pytest.raises(StepExecutionError, match="unknown action"):
        execute_steps(mock_driver, [{"action": "nonexistent_action"}])


def test_open_url_absolute_and_relative():
    mock_driver = MagicMock()

    # Absolute URL
    execute_steps(mock_driver, [{"action": "open_url", "input_value": "https://example.com/login"}], project_url="https://example.com")
    mock_driver.get.assert_called_with("https://example.com/login")

    # Relative URL with project URL
    execute_steps(mock_driver, [{"action": "open_url", "input_value": "/dashboard"}], project_url="https://example.com")
    mock_driver.get.assert_called_with("https://example.com/dashboard")


def test_custom_js_execution():
    mock_driver = MagicMock()
    execute_steps(mock_driver, [{"action": "custom_js", "input_value": "console.log('test');"}])
    mock_driver.execute_script.assert_called_with("console.log('test');")


def test_assert_url_contains():
    mock_driver = MagicMock()
    mock_driver.current_url = "https://example.com/dashboard?user=admin"

    # Should pass
    execute_steps(mock_driver, [{"action": "assert_url_contains", "input_value": "/dashboard"}])

    # Should fail
    with pytest.raises(StepExecutionError, match="Expected URL to contain"):
        execute_steps(mock_driver, [{"action": "assert_url_contains", "input_value": "/login"}])


def test_assert_title_contains():
    mock_driver = MagicMock()
    mock_driver.title = "Welcome to Portal"

    # Should pass
    execute_steps(mock_driver, [{"action": "assert_title_contains", "input_value": "Portal"}])

    # Should fail
    with pytest.raises(StepExecutionError, match="Expected title to contain"):
        execute_steps(mock_driver, [{"action": "assert_title_contains", "input_value": "Dashboard"}])
