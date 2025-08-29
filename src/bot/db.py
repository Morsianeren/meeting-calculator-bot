"""
Handles database operations for the Meeting Calculator Bot.
"""
from typing import List, Dict, Any, Optional
import sqlite3
import os
import uuid
import csv
from datetime import datetime
from datetime import timedelta


class DB:
    def __init__(self):
        # Database path
        self.db_path = os.path.join(os.path.dirname(__file__), '../../data/meetings.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database if it doesn't exist
        self._initialize_db()
    
    def _initialize_db(self):
        """
        Creates database tables if they don't exist according to schema in database-structure.md
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create MEETING table with meeting_uid as PK
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MEETING (
            meeting_uid VARCHAR(255) PRIMARY KEY,
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
            meeting_uid VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            initials VARCHAR(10) NOT NULL,
            role VARCHAR(100) NOT NULL,
            hourly_cost DECIMAL(10,2) NOT NULL,
            feedback_requested BOOLEAN NOT NULL DEFAULT 0,
            feedback_token VARCHAR(64) NOT NULL,
            FOREIGN KEY (meeting_uid) REFERENCES MEETING(meeting_uid)
        )
        ''')
        
        # Create FEEDBACK table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS FEEDBACK (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_uid VARCHAR(255) NOT NULL,
            participant_token VARCHAR(64) NOT NULL,
            useful BOOLEAN,
            improvement_text TEXT,
            submitted_at DATETIME,
            anonymized BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (meeting_uid) REFERENCES MEETING(meeting_uid)
        )
        ''')
        
        # Create indices for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_token ON MEETING(feedback_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_participant_token ON PARTICIPANT(feedback_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_participant ON PARTICIPANT(meeting_uid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_feedback ON FEEDBACK(meeting_uid)')
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
        
    def add_meeting(self, meeting_details: Dict[str, Any]) -> None:
        """
        Adds meeting to database based on parse_meeting_details output.
        Skips if meeting already exists (based on meeting_uid).
        
        Args:
            meeting_details: Meeting details dictionary
            
        Returns:
            meeting_uid of the created/existing meeting
            
        Example input:
        {
            'participants': ['mdh', 'crh'],
            'organizer': 'mdh@deif.com',
            'from': 'mdh@deif.com',
            'subject': 'Weekly Planning Meeting',
            'date': '2025-08-29 14:30:00',
            'body': '...',
            'duration': 60,
            'meeting_id': '354457537935'
        }
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if meeting already exists to avoid duplicates
        meeting_uid = meeting_details.get('meeting_id', '')
        cursor.execute("SELECT meeting_uid FROM MEETING WHERE meeting_uid = ?", (meeting_uid,))
        existing = cursor.fetchone()
        
        if existing:
            # No mames, this meeting already exists pendejo!
            conn.close()
            return meeting_uid
        
        # Parse times
        start_time = datetime.strptime(meeting_details.get('date', ''), '%Y-%m-%d %H:%M:%S')
        duration = meeting_details.get('duration', 60)
        if duration is None:
            duration = 60  # Fallback for None
        end_time = start_time + timedelta(minutes=duration)
        
        # Generate token
        feedback_token = str(uuid.uuid4())
        
        # Insert meeting record
        cursor.execute('''
        INSERT INTO MEETING (
            meeting_uid, organizer_email, subject, start_time, end_time, 
            duration_minutes, total_cost, feedback_sent, feedback_token
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meeting_uid,
            meeting_details.get('from', ''),
            meeting_details.get('subject', 'Untitled Meeting'),
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S'),
            duration,
            meeting_details.get('cost', 0.0),
            False,
            feedback_token
        ))
        
        # Add participants
        for participant in meeting_details.get('participants', []):
            # Get wage
            from src.bot.bot import username_to_wage
            hourly_cost = username_to_wage(participant)
            
            # Generate token
            participant_token = str(uuid.uuid4())
            
            # Get role 
            role = "Unknown"
            role_lookup_path = os.path.join(os.path.dirname(__file__), '../../config/initials_role_lookup.csv')
            if os.path.exists(role_lookup_path):
                with open(role_lookup_path, newline='') as f:
                    for row in csv.reader(f):
                        if len(row) == 2 and row[0].strip().lower() == participant.lower():
                            role = row[1].strip()
                            break
        
            # Construct email
            email = f"{participant}@deif.com"
            
            cursor.execute('''
            INSERT INTO PARTICIPANT (
                meeting_uid, email, initials, role, hourly_cost, 
                feedback_requested, feedback_token
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting_uid,
                email,
                participant,
                role,
                hourly_cost,
                True,
                participant_token
            ))
    
        conn.commit()
        conn.close()
        
        return
