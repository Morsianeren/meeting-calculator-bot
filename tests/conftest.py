# Shared pytest fixtures for MeetingBot tests
import pytest
import os
from dotenv import load_dotenv

def is_integration_test(config):
    """Determine if the current test is an integration test."""
    # Check if the marker is explicitly used
    markers = config.getoption("-m", "")
    if any(marker in markers for marker in ["integration", "email"]):
        return True
    
    # Check if we're running tests from the integration directory
    test_paths = [arg for arg in config.args if 'test' in arg]
    return any('integration' in path for path in test_paths)

def pytest_configure(config):
    if not is_integration_test(config):
        print("Setting mock email environment for component tests")
        os.environ['EMAIL_ADDRESS'] = 'test@example.com'
        os.environ['EMAIL_PASSWORD'] = 'test_password'
        os.environ['IMAP_SERVER'] = 'localhost'
        os.environ['SMTP_SERVER'] = 'localhost'
    else:
        # For integration tests, ensure we load from .env
        print("Loading real email credentials for integration tests")
        load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

@pytest.fixture
def sample_participants():
    return ['mak@deif.com', 'crh@deif.com', 'kk@deif.com']

@pytest.fixture
def sample_roles():
    return {'mak': 'developer', 'crh': 'developer', 'kk': 'ceo'}

@pytest.fixture
def sample_costs():
    return {'developer': 2000, 'ceo': 4000}
