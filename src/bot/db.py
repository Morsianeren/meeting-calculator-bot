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
        
    def add_meeting(self, meeting_details: Dict[str, Any]) -> Optional[int]:
        """
        Adds a meeting to the database based on the output from parse_meeting_details
        
        Args:
            meeting_details: Dictionary containing meeting details from parse_meeting_details
            
        Returns:
            The ID of the newly created meeting
            
        Example input:
        {
            'participants': ['mdh', 'crh'],
            'organizer': 'John Smith <mdh@deif.com>',
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
        
        # Parse start and end times from date and duration
        start_time = datetime.strptime(meeting_details.get('date', ''), '%Y-%m-%d %H:%M:%S')
        duration = meeting_details.get('duration', 60)  # Default to 60 minutes if not specified
        end_time = start_time + timedelta(minutes=duration)
        
        # Generate a unique token for meeting feedback
        feedback_token = str(uuid.uuid4())
        
        # Insert meeting record
        cursor.execute('''
        INSERT INTO MEETING (
            meeting_uid, organizer_email, subject, start_time, end_time, 
            duration_minutes, total_cost, feedback_sent, feedback_token
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            meeting_details.get('meeting_id', ''),
            meeting_details.get('from', ''),
            meeting_details.get('subject', 'Untitled Meeting'),
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S'),
            duration,
            meeting_details.get('cost', 0.0),
            False,
            feedback_token
        ))
        
        meeting_id = cursor.lastrowid
        
        # Add participants
        for participant in meeting_details.get('participants', []):
            # Use the username_to_wage function from bot.py to get participant's role and hourly cost
            # For testing, this can be imported or re-implemented here
            from src.bot.bot import username_to_wage
            hourly_cost = username_to_wage(participant)
            
            # Generate unique token for this participant's feedback
            participant_token = str(uuid.uuid4())
            
            # Extract role from initials or provide default
            role = "Unknown"  # Default role
            role_lookup_path = os.path.join(os.path.dirname(__file__), '../../config/initials_role_lookup.csv')
            if os.path.exists(role_lookup_path):
                with open(role_lookup_path, newline='') as f:
                    for row in csv.reader(f):
                        if len(row) == 2 and row[0].strip().lower() == participant.lower():
                            role = row[1].strip()
                            break
            
            # Construct email from initials if missing
            email = f"{participant}@deif.com"
            
            cursor.execute('''
            INSERT INTO PARTICIPANT (
                meeting_id, email, initials, role, hourly_cost, 
                feedback_requested, feedback_token
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                meeting_id,
                email,
                participant,
                role,
                hourly_cost,
                True,  # Default to requesting feedback
                participant_token
            ))
        
        conn.commit()
        conn.close()
        
        return meeting_id
