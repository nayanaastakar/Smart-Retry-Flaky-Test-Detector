"""
tests/test_app_routes.py
========================
Integration tests for the Flask web application and API endpoints.
"""

import pytest
from app import app as flask_app
from database.db_manager import init_db
from database.seed import seed_admin_user, seed_default_settings


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            init_db()
            seed_admin_user()
            seed_default_settings()
        yield client


def login(client, username="admin", password="Admin@123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_unauthenticated_redirect_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_success(client):
    res = login(client)
    assert res.status_code == 200
    assert b"Execution Overview" in res.data


def test_login_failure(client):
    res = client.post("/login", data={"username": "admin", "password": "WrongPassword"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid username or password" in res.data


def test_api_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "smart-retry-framework"


def test_api_analytics_summary(client):
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_executions" in data
    assert "pass_rate" in data


def test_project_crud(client):
    login(client)

    # Create project
    create_res = client.post(
        "/projects/create",
        data={"name": "Test Project", "url": "https://example.org", "browser": "chrome", "tags": "smoke, api", "notes": "E2E testing"},
        follow_redirects=True,
    )
    assert create_res.status_code == 200
    assert b"Test Project" in create_res.data

    from database.db_manager import fetch_one
    p = fetch_one("SELECT id FROM projects WHERE name = 'Test Project'")
    assert p is not None
    project_id = p["id"]

    # Create test case inside project
    tc_res = client.post(
        f"/projects/{project_id}/tests/create",
        data={
            "name": "Verify Login Flow",
            "description": "Check valid login",
            "group_name": "auth",
            "tags": "login",
            "steps_json": '[{"action": "open_url", "input_value": "/login"}]',
        },
        follow_redirects=True,
    )
    assert tc_res.status_code == 200
    assert b"Verify Login Flow" in tc_res.data


def test_settings_update(client):
    login(client)
    res = client.post(
        "/settings/",
        data={
            "browser": "firefox",
            "retry_count": "5",
            "retry_delay": "3.5",
            "execution_timeout": "90",
            "headless": "false",
            "theme": "light",
            "ai_enabled": "true",
        },
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Settings saved successfully" in res.data
