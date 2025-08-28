import pytest
from src import db

@pytest.fixture
def meeting_record():
    return {
        'organizer': 'mak@deif.com',
        'participants': ['mak@deif.com', 'crh@deif.com'],
        'start_time': '2025-08-28T10:00:00',
        'end_time': '2025-08-28T11:00:00'
    }

def test_store_meeting(meeting_record):
    db.store_meeting(meeting_record)
    stored = db.get_meeting(meeting_record['organizer'])
    assert stored is not None
    assert stored['organizer'] == 'mak@deif.com'


# Negative test: get non-existent meeting
def test_get_missing_meeting():
    stored = db.get_meeting('unknown@deif.com')
    assert stored is None

# Negative test: store invalid meeting record
def test_store_invalid_meeting():
    with pytest.raises(Exception):
        db.store_meeting({'organizer': None})
