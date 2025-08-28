# Shared pytest fixtures for MeetingBot tests
import pytest
import os
from dotenv import load_dotenv

# Only set mock environment variables if we're not running integration tests
def pytest_configure(config):
    markers = config.getoption("-m", "")
    
    # Only set mock values for regular tests, not for integration tests
    if not any(marker in markers for marker in ["integration", "email"]):
        print("Setting mock email environment for unit tests")
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
