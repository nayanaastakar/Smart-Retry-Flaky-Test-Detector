"""
tests/test_evidence_and_reports.py
==================================
Tests for EvidenceCollector and ReportService (HTML, JSON, CSV).
"""

from unittest.mock import MagicMock
import pytest
from app import app
from core.evidence_collector import EvidenceCollector
from services.report_service import ReportService
from database.db_manager import init_db, execute
from config import settings


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_evidence_collector_graceful_degrade_without_driver():
    collector = EvidenceCollector(driver=None, run_id="run_test", test_name="No Driver Test")
    evidence = collector.capture(exception=ValueError("Sample error"))
    assert evidence["screenshot_path"] is None
    assert evidence["console_logs"] is None
    assert evidence["browser_version"] is None
    assert evidence["exception_type"] == "ValueError"
    assert "Sample error" in evidence["exception_message"]


def test_evidence_collector_with_mock_driver(tmp_path):
    mock_driver = MagicMock()
    mock_driver.capabilities = {"browserName": "chrome", "browserVersion": "125.0.6422.60"}
    mock_driver.get_log.return_value = [{"level": "INFO", "message": "Console log test"}]

    collector = EvidenceCollector(driver=mock_driver, run_id="run_123", test_name="Sample UI Test")
    evidence = collector.capture()
    assert evidence["browser_version"] == "chrome 125.0.6422.60"
    mock_driver.save_screenshot.assert_called_once()


def test_report_service_generation():
    # Insert test execution
    execute(
        """INSERT INTO executions (run_id, test_name, module, status, attempt_count, duration_ms, started_at)
           VALUES ('report_batch', 'Test Report Case', 'reporting', 'PASS', 1, 1500, CURRENT_TIMESTAMP)"""
    )

    service = ReportService()

    # Generate JSON
    json_result = service.generate("json", run_id="report_batch")
    assert json_result["summary"]["total"] == 1
    assert json_result["summary"]["passed"] == 1

    # Generate CSV
    csv_result = service.generate("csv", run_id="report_batch")
    assert csv_result["summary"]["total"] == 1

    # Generate HTML within app context
    with app.app_context():
        html_result = service.generate("html", run_id="report_batch")
        assert html_result["summary"]["total"] == 1
