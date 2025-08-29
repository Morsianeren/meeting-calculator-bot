"""
Handles database operations for the Meeting Calculator Bot.
"""
from typing import List, Dict, Any, Optional
import sqlite3
import os
import uuid
from datetime import datetime

class DB:
    def __init__(self):
        # Database path
        self.db_path = os.path.join(os.path.dirname(__file__), '../../data/meetings.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database if it doesn't exist
        self._initialize_db()
    
    def _initialize_db(self):
        """
        Creates database tables if they don't exist according to the schema defined in 
        database-structure.md
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create MEETING table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MEETING (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_uid VARCHAR(255) NOT NULL,
            organizer_email VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            duration_minutes INTEGER NOT NULL,
            total_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            feedback_sent BOOLEAN NOT NULL DEFAULT 0,
            feedback_token VARCHAR(64) NOT NULL
        )
        ''')
        
        # Create PARTICIPANT table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS PARTICIPANT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            email VARCHAR(255) NOT NULL,
            initials VARCHAR(10) NOT NULL,
            role VARCHAR(100) NOT NULL,
            hourly_cost DECIMAL(10,2) NOT NULL,
            feedback_requested BOOLEAN NOT NULL DEFAULT 0,
            feedback_token VARCHAR(64) NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES MEETING(id)
        )
        ''')
        
        # Create FEEDBACK table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FEEDBACK (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            participant_token VARCHAR(64) NOT NULL,
            useful BOOLEAN,
            improvement_text TEXT,
            submitted_at DATETIME,
            anonymized BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (meeting_id) REFERENCES MEETING(id)
        )
        ''')
        
        # Create indices for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_uid ON MEETING(meeting_uid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_token ON MEETING(feedback_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participant_token ON PARTICIPANT(feedback_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_participant ON PARTICIPANT(meeting_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_feedback ON FEEDBACK(meeting_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participant_feedback ON FEEDBACK(participant_token)')
        
        conn.commit()
        conn.close()
        
    def _get_connection(self) -> sqlite3.Connection:
        """
        Returns a connection to the SQLite database
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
