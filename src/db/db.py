import sqlite3
import os
from datetime import datetime

def get_db_path(meeting_id=None):
    return 'main_meetings.db'

def store_meeting(record, meeting_id=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS meetings (
        organizer TEXT, participants TEXT, start_time TEXT, end_time TEXT, feedback_sent BOOLEAN
    )''')
    c.execute('''INSERT INTO meetings VALUES (?, ?, ?, ?, ?)''', (
        record['organizer'], ','.join(record['participants']), record['start_time'], record['end_time'], record.get('feedback_sent', False)))
    conn.commit()
    conn.close()

def get_meeting(organizer, meeting_id=None):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT * FROM meetings WHERE organizer=?''', (organizer,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'organizer': row[0],
            'participants': row[1].split(','),
            'start_time': row[2],
            'end_time': row[3],
            'feedback_sent': bool(row[4])
        }
    return None
