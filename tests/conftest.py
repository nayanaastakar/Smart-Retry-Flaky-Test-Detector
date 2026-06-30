import pytest
from core.driver import DriverManager
from core.config_loader import ConfigLoader


def pytest_configure(config):
    """Load active website config before any tests run."""
    ConfigLoader.load_config()


@pytest.fixture(scope="session")
def driver():
    """Single WebDriver instance shared across the whole test session."""
    mgr = DriverManager()
    driver_instance = mgr.initialize_driver()
    yield driver_instance
    mgr.quit_driver()
