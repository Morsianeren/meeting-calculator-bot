"""Test DB initialization matches the database-structure diagram"""
import os
import pytest
import sqlite3
from unittest.mock import patch
from src.bot.db import DB

@pytest.fixture
def test_db():
    """Fixture to create test DB instance with temp path"""
    db = DB()
    # Override path for testing
    db.db_path = os.path.join(os.path.dirname(__file__), '../data/test_meetings.db')
    os.makedirs(os.path.dirname(db.db_path), exist_ok=True)
    db._initialize_db()
    yield db
    # Cleanup after test
    if os.path.exists(db.db_path):
        os.remove(db.db_path)

def test_db_structure_matches_diagram(test_db):
    """Test database structure matches the specification in database-structure.md"""
    conn = sqlite3.connect(test_db.db_path)
    cursor = conn.cursor()
    
    # Check tables exist as per diagram
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
    
    # Add assertions based on database-structure.md
    expected_tables = ["MEETING", "PARTICIPANT", "FEEDBACK"]
    for table in expected_tables:
        assert table in tables, f"Table {table} missing from database"
    
    # Check MEETING table structure
    cursor.execute("PRAGMA table_info(MEETING)")
    columns = {row[1] for row in cursor.fetchall()}
    meeting_fields = {"id", "meeting_uid", "organizer_email", "subject", "start_time", 
                      "end_time", "duration_minutes", "total_cost", "feedback_sent", 
                      "feedback_token"}
    for field in meeting_fields:
        assert field in columns, f"Field {field} missing from MEETING table"
    
    # Check PARTICIPANT table structure
    cursor.execute("PRAGMA table_info(PARTICIPANT)")
    columns = {row[1] for row in cursor.fetchall()}
    participant_fields = {"id", "meeting_id", "email", "initials", "role", 
                          "hourly_cost", "feedback_requested", "feedback_token"}
    for field in participant_fields:
        assert field in columns, f"Field {field} missing from PARTICIPANT table"
        
    # Check FEEDBACK table structure
    cursor.execute("PRAGMA table_info(FEEDBACK)")
    columns = {row[1] for row in cursor.fetchall()}
    feedback_fields = {"id", "meeting_id", "participant_token", "useful",
                       "improvement_text", "submitted_at", "anonymized"}
    for field in feedback_fields:
        assert field in columns, f"Field {field} missing from FEEDBACK table"

def test_add_meeting(test_db):
    """Test adding a meeting to the database"""
    # Mock the username_to_wage function to return a fixed value
    def mock_username_to_wage(username):
        wages = {'mdh': 100.0, 'crh': 85.0}
        return wages.get(username, 0.0)
    
    # Apply the patch for username_to_wage function
    with patch('src.bot.bot.username_to_wage', side_effect=mock_username_to_wage):
        
        # Sample meeting data matching the example
        sample_meeting = {
            'participants': ['mdh', 'crh'],
            'organizer': 'mdh@deif.com',
            'from': 'mdh@deif.com',
            'subject': 'Weekly Planning Meeting',
            'date': '2025-08-29 14:30:00',
            'body': '...',
            'duration': 60,
            'meeting_id': '354457537935',
            'cost': 185.0  # Total cost (100.0 + 85.0)
        }
        
        # Add the meeting to the database
        meeting_id = test_db.add_meeting(sample_meeting)
        
        # Verify meeting was added correctly
        assert meeting_id is not None, "Meeting ID should not be None"
        
        conn = sqlite3.connect(test_db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check meeting record
        cursor.execute("SELECT * FROM MEETING WHERE id = ?", (meeting_id,))
        meeting = cursor.fetchone()
        assert meeting is not None, "Meeting record not found"
        assert meeting['meeting_uid'] == sample_meeting['meeting_id']
        assert meeting['organizer_email'] == sample_meeting['from']
        assert meeting['subject'] == sample_meeting['subject']
        assert meeting['duration_minutes'] == sample_meeting['duration']
        assert float(meeting['total_cost']) == sample_meeting['cost']
        assert meeting['feedback_sent'] == 0
        assert len(meeting['feedback_token']) > 0
        
        # Check participant records
        cursor.execute("SELECT * FROM PARTICIPANT WHERE meeting_id = ?", (meeting_id,))
        participants = cursor.fetchall()
        
        assert len(participants) == 2, "Should have 2 participant records"
        
        # Check for each participant
        participant_initials = [p['initials'] for p in participants]
        assert 'mdh' in participant_initials
        assert 'crh' in participant_initials
        
        # Check details of one specific participant
        for participant in participants:
            if participant['initials'] == 'mdh':
                assert participant['email'] == 'mdh@deif.com'
                assert float(participant['hourly_cost']) == 100.0
                assert participant['feedback_requested'] == 1
                assert len(participant['feedback_token']) > 0
            elif participant['initials'] == 'crh':
                assert participant['email'] == 'crh@deif.com'
                assert float(participant['hourly_cost']) == 85.0
        
        conn.close()