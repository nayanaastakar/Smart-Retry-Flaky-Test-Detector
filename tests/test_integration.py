import pytest
from app import app
import json
from dashboard.history_manager import HistoryManager

@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_full_execution_pipeline(client, monkeypatch):
    """
    Test the full integration pipeline from triggering a test run via API,
    generating reports, and saving execution history.
    """
    # Mock subprocess.run to avoid running actual pytest Selenium in CI/headless without setup
    class MockProcess:
        stdout = "Test executed successfully"
        stderr = ""
        returncode = 0
    
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: MockProcess())
    
    # Trigger run_tests API
    response = client.post("/api/run_tests", json={
        "website_id": "saucedemo",
        "retry_count": 1,
        "ai_enabled": False,
        "headless": True
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data["status"] == "success"
    assert "report_url" in data
    assert "result_url" in data
    assert "evidence" in data
    
    # Verify execution history was saved
    mgr = HistoryManager()
    records = mgr.load_history()
    
    assert len(records) > 0
    latest_run = records[0]
    
    # Assert fields are filled
    assert latest_run.execution_id is not None
    assert latest_run.total_tests >= 1
    
def test_dashboard_routes(client):
    """Verify all dashboard routes return 200."""
    routes = ["/", "/run", "/analytics", "/history", "/settings"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
