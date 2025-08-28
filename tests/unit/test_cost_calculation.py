import sys
import os
from unittest.mock import patch
import pytest
from src.cost_calculation.cost_calculation import calculate_meeting_cost

def test_calculate_meeting_cost_basic():
    participants = {
        "mak": "developer",
        "crh": "developer",
        "kk": "ceo"
    }
    role_costs = {
        "developer": 2000,
        "ceo": 4000
    }
    duration_hours = 1.5
    expected_cost = 12000.0

    with patch("cost_calculation.get_role_costs", return_value=role_costs):
        actual_cost = calculate_meeting_cost(participants, duration_hours)

    assert actual_cost == expected_cost
