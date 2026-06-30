import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.screenshot_manager import ScreenshotManager
from core.browser_log_manager import BrowserLogManager
from utils.report_generator import ReportGenerator
from dashboard.history_manager import HistoryManager
from dashboard.execution_history import ExecutionHistory
from models.evidence import Evidence

class TestScreenshotManager:
    @patch('core.screenshot_manager.Config')
    def test_screenshot_capture(self, mock_config):
        mock_config.return_value.ENABLE_SCREENSHOTS = True
        mock_config.return_value.SCREENSHOT_PATH = Path("mock_screenshots")
        
        manager = ScreenshotManager()
        mock_driver = MagicMock()
        mock_driver.save_screenshot.return_value = True
        
        with patch('core.screenshot_manager.datetime') as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "20260630_120000"
            result = manager.capture(mock_driver, "test_example")
            
            assert result == Path("mock_screenshots/test_example_20260630_120000.png")
            mock_driver.save_screenshot.assert_called_once()

    @patch('core.screenshot_manager.Config')
    def test_screenshot_disabled(self, mock_config):
        mock_config.return_value.ENABLE_SCREENSHOTS = False
        manager = ScreenshotManager()
        
        result = manager.capture(MagicMock(), "test_example")
        assert result is None

class TestBrowserLogManager:
    @patch('core.browser_log_manager.Config')
    def test_save_logs(self, mock_config):
        mock_config.return_value.ENABLE_BROWSER_LOGS = True
        mock_config.return_value.LOG_PATH = Path("mock_logs")
        
        manager = BrowserLogManager()
        mock_driver = MagicMock()
        mock_driver.get_log.return_value = [{"level": "SEVERE", "message": "error msg", "timestamp": 123}]
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('core.browser_log_manager.datetime') as mock_dt:
                mock_dt.now.return_value.strftime.return_value = "20260630_120000"
                result = manager.save_logs(mock_driver, "test_example")
                assert result == Path("mock_logs/test_example_20260630_120000.txt")
                mock_open.assert_called_once()

    @patch('core.browser_log_manager.Config')
    def test_save_logs_disabled(self, mock_config):
        mock_config.return_value.ENABLE_BROWSER_LOGS = False
        manager = BrowserLogManager()
        result = manager.save_logs(MagicMock(), "test_example")
        assert result is None


class TestReportGenerator:
    def test_generate_report(self):
        generator = ReportGenerator()
        generator.config.AUTO_GENERATE_REPORT = True
        
        ev1 = Evidence(test_name="t1", status="PASS")
        ev2 = Evidence(test_name="t2", status="FAILURE")
        
        html = generator.generate("saucedemo", [ev1, ev2])
        assert "t1" in html
        assert "t2" in html
        assert "saucedemo" in html.lower()


class TestHistoryManager:
    @patch('dashboard.history_manager.Config')
    def test_save_and_load_history(self, mock_config, tmp_path):
        history_file = tmp_path / "history.json"
        mock_config.return_value.HISTORY_PATH = history_file
        mock_config.return_value.ENABLE_HISTORY = True
        
        manager = HistoryManager()
        
        history_record = ExecutionHistory(
            execution_id="1234",
            total_tests=5,
            passed=3,
            failed=2,
            flaky=0
        )
        
        manager.save_execution(history_record)
        
        records = manager.load_history()
        assert len(records) == 1
        assert records[0].execution_id == "1234"
        assert records[0].total_tests == 5
