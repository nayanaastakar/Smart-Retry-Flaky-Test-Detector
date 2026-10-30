"""
tests/conftest.py
=================
Pytest fixtures and configuration for Smart Retry Framework tests.
"""

import os
import pytest
from config import settings
from database.db_manager import init_db

# Ensure testing settings
os.environ["FLASK_ENV"] = "testing"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    settings.ensure_directories()
    init_db()
