"""Test DB initialization matches the database-structure diagram"""
import os
import pytest
import sqlite3
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