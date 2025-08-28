import pytest
from src import feedback

@pytest.fixture
def feedback_data():
    return [
        {'useful': True, 'improvements': 'None'},
        {'useful': False, 'improvements': 'Shorter meeting'}
    ]

def test_aggregate_feedback(feedback_data):
    result = feedback.aggregate_feedback(feedback_data)
    assert 'useful_count' in result
    assert 'improvements' in result


# Negative test: empty feedback list
def test_aggregate_feedback_empty():
    result = feedback.aggregate_feedback([])
    assert result['useful_count'] == 0
    assert result['improvements'] == []

# Negative test: invalid feedback data
def test_aggregate_feedback_invalid():
    with pytest.raises(Exception):
        feedback.aggregate_feedback([None])
