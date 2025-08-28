from src.email import email_handler
from src.db import db
from src.feedback import feedback
from src.utils import cost_calculator
import os
import csv

# Load CSVs
INITIALS_ROLES = {}
ROLE_COSTS = {}
with open('config/initials_roles.csv') as f:
    for row in csv.reader(f):
        if row:
            INITIALS_ROLES[row[0]] = row[1]
with open('config/role_costs.csv') as f:
    for row in csv.reader(f):
        if row:
            ROLE_COSTS[row[0]] = int(row[1])

def process_meeting_invite(email):
    # Dummy parser for demonstration
    organizer = 'mak@deif.com'
    participants = ['mak@deif.com', 'crh@deif.com', 'kk@deif.com']
    duration_hours = 2
    cost, warnings = cost_calculator.calculate_meeting_cost_with_warnings(
        participants, duration_hours, INITIALS_ROLES, ROLE_COSTS)
    if warnings:
        body = f"Meeting cost: {cost}. Warning: Missing roles for {', '.join(warnings)}."
    else:
        body = f"Meeting cost: {cost}."
    email_handler.send_email(organizer, 'Meeting Cost Estimate', body)
    db.store_meeting({
        'organizer': organizer,
        'participants': participants,
        'start_time': '2025-08-28T10:00:00',
        'end_time': '2025-08-28T12:00:00',
        'feedback_sent': False
    })

if __name__ == '__main__':
    emails = email_handler.fetch_emails()
    for email in emails:
        process_meeting_invite(email)
