# Shared pytest fixtures for MeetingBot tests
import pytest
import os

# Set mock environment variables for tests
os.environ['EMAIL_ADDRESS'] = 'test@example.com'
os.environ['EMAIL_PASSWORD'] = 'test_password'
os.environ['IMAP_SERVER'] = 'localhost'
os.environ['SMTP_SERVER'] = 'localhost'

@pytest.fixture
def sample_participants():
    return ['mak@deif.com', 'crh@deif.com', 'kk@deif.com']

@pytest.fixture
def sample_roles():
    return {'mak': 'developer', 'crh': 'developer', 'kk': 'ceo'}

@pytest.fixture
def sample_costs():
    return {'developer': 2000, 'ceo': 4000}
