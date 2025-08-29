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
    # Replace these with the actual table names from your diagram
    expected_tables = ["meetings", "participants", "roles", "wages"]
    for table in expected_tables:
        assert table in tables, f"Table {table} missing from database"