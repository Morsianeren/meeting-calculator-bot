"""
Implements the main bot logic for the Meeting Calculator Bot.
"""
import time
import email
from email.header import decode_header
import re
import csv
import os

if __name__ == "__main__":
    from email_server import EmailServer
    from db import DB
else:
    from src.bot.email_server import EmailServer
    from src.bot.db import DB


class Bot:
    def __init__(self, email_server: EmailServer, db: DB):
        self.email_server = email_server
        self.db = db
    def run(self):
        while True:
            meetings = self.parse_meeting_details()
            for details in meetings:
                wages = self.db.lookup_roles_and_wages(details['participants'])
                cost = self.calculate_meeting_cost(details, wages)
                self.email_server.send_email(details['organizer'], "Meeting Cost Summary", f"Cost: {cost}")
            time.sleep(60) # Poll every minute

    def extract_usernames_from_fields(self, fields):
        all_emails = set()
        for field in fields:
            usernames = re.findall(r'([\w\.-]+)@', field)
            all_emails.update(usernames)
        return sorted(all_emails)

    def parse_meeting_details(self) -> list:
        emails_dict = self.email_server.poll_for_new_emails()
        meetings = []
        for eid, mail in emails_dict.items():
            fields = [mail.get('from', ''), mail.get('body', '')]
            participants = self.extract_usernames_from_fields(fields)
            meetings.append({
                'participants': participants,
                'organizer': mail.get('from', ''),
                'subject': mail.get('subject', ''),
                'date': mail.get('date', ''),
                'body': mail.get('body', ''),
            })
        return meetings

    def calculate_meeting_cost(self, details: dict, wages: dict) -> int:
        # Dummy: Replace with cost calculation logic
        return sum(wages.values())

def username_to_wage(user: str) -> float:
    role_lookup_path = os.path.join(os.path.dirname(__file__), '../../config/initials_role_lookup.csv')
    wage_lookup_path = os.path.join(os.path.dirname(__file__), '../../config/role_wage_lookup.csv')

    # Load role lookup
    roles = {}
    if os.path.exists(role_lookup_path):
        with open(role_lookup_path, newline='') as f:
            for row in csv.reader(f):
                if len(row) == 2:
                    roles[row[0].strip()] = row[1].strip()

    # If user not found, add to role lookup as 'undefined'
    if user not in roles:
        with open(role_lookup_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([user, 'undefined'])
        roles[user] = 'undefined'

    # Load wage lookup
    wages = {}
    if os.path.exists(wage_lookup_path):
        with open(wage_lookup_path, newline='') as f:
            for row in csv.reader(f):
                if len(row) == 2:
                    wages[row[0].strip()] = float(row[1].strip())

    role = roles.get(user, 'undefined')

    return wages.get(role, 0.0)

if __name__ == "__main__":
    print("Username to wage test")
    print(username_to_wage("crh"))
    print(username_to_wage("mdh"))
    
    print("Get meeting test")
    bot = Bot(EmailServer(), DB())
    meetings = bot.parse_meeting_details()
    
    if not meetings:
        print("No new meetings found.")
    
    else:
        print("Meetings found:")
        for details in meetings:
            print(details)

    print("Calculate meeting costs")
    for details in meetings:
        total_cost = 0.0
        for name in details['participants']:
            total_cost += username_to_wage(name)
        print(f"Meeting '{details['subject']}' cost: {total_cost}, participants: {len(details['participants'])}")