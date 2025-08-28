# Shared pytest fixtures for MeetingBot tests
import pytest

@pytest.fixture
def sample_participants():
    return ['mak@deif.com', 'crh@deif.com', 'kk@deif.com']

@pytest.fixture
def sample_roles():
    return {'mak': 'developer', 'crh': 'developer', 'kk': 'ceo'}

@pytest.fixture
def sample_costs():
    return {'developer': 2000, 'ceo': 4000}
