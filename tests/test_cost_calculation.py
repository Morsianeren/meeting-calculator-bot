import pytest
from src import cost_calculator

# Mock data for initials to role and role to cost
INITIALS_ROLES = {'mak': 'developer', 'crh': 'developer', 'kk': 'ceo'}
ROLE_COSTS = {'developer': 2000, 'ceo': 4000}

@pytest.fixture
def sample_meeting():
    return {
        'participants': ['mak@deif.com', 'crh@deif.com', 'kk@deif.com'],
        'duration_hours': 2
    }

@pytest.fixture
def missing_initials_meeting():
    return {
        'participants': ['mak@deif.com', 'xyz@deif.com'],
        'duration_hours': 1
    }

def test_cost_calculation(sample_meeting):
    cost = cost_calculator.calculate_meeting_cost(
        sample_meeting['participants'],
        sample_meeting['duration_hours'],
        INITIALS_ROLES,
        ROLE_COSTS
    )
    assert cost == (2000 + 2000 + 4000) * 2

def test_missing_initials(missing_initials_meeting):
    cost, warnings = cost_calculator.calculate_meeting_cost_with_warnings(
        missing_initials_meeting['participants'],
        missing_initials_meeting['duration_hours'],
        INITIALS_ROLES,
        ROLE_COSTS
    )
    assert 'xyz' in warnings
    assert cost == (2000 + 0) * 1  # 0 for undefined role


# Negative test: zero duration
def test_zero_duration(sample_meeting):
    cost = cost_calculator.calculate_meeting_cost(
        sample_meeting['participants'],
        0,
        INITIALS_ROLES,
        ROLE_COSTS
    )
    assert cost == 0

# Negative test: invalid participant email
def test_invalid_email():
    with pytest.raises(Exception):
        cost_calculator.calculate_meeting_cost(['notanemail'], 1, INITIALS_ROLES, ROLE_COSTS)
