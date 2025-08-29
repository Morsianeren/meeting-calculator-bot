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
        #while True:
        meetings = self.parse_meeting_details()
        for details in meetings:
            cost, explanation = self.calculate_meeting_cost(details)
            
            # Add cost to the meeting details
            details['cost'] = cost
            
            # Save meeting in database
            self.db.add_meeting(details)
            
            # Send email notification
            self.email_server.send_email(details['from'], f"{details['subject']} [ID: {details['meeting_id']}] - Meeting Cost Summary", f"Cost: {cost}\n\n{explanation}")
            print(f"Processed meeting '{details['subject']}'[ID: {details['meeting_id']}] with cost {cost} to {details['from']}")
        
        #time.sleep(60) # Poll every minute

    def extract_usernames_from_fields(self, fields):
        """
        Extracts usernames from email addresses matching <XXX@deif.com> pattern
        Only accepts usernames between 2-4 characters
        """
        all_emails = set()
        for field in fields:
            # Find all matches with 2-4 letter usernames
            email_matches = re.findall(r'<(\w{2,4})@deif\.com>', field)
            all_emails.update(email_matches)
        # Convert all usernames to lowercase
        all_emails = {email.lower() for email in all_emails}
        return sorted(all_emails)

    def extract_teams_meeting_id(self, body: str) -> str:
        """
        Extracts the Teams meeting ID from email body.
        Returns empty string if not found.
        """
        meeting_id_match = re.search(r'Meeting ID:[\s]*([0-9\s]+)', body)
        if meeting_id_match:
            # Remove spaces from meeting ID
            return re.sub(r'\s+', '', meeting_id_match.group(1))
        return ""

    def parse_meeting_details(self) -> list:
        """
        Parses email data and extracts meeting details
        """
        emails_dict = self.email_server.poll_for_new_emails()
        meetings = []
        for eid, mail in emails_dict.items():
            # Extract email address from "from" field using regex
            from_email = ""
            from_match = re.search(r'[\w\.-]+@[\w\.-]+', mail.get('from', ''))
            if from_match:
                from_email = from_match.group(0)
                
            fields = [mail.get('from', ''), mail.get('body', '')]
            participants = self.extract_usernames_from_fields(fields)
            body = mail.get('body', '')
            duration = self.extract_duration_from_body(body)
            meeting_id = self.extract_teams_meeting_id(body)
            
            # Format date to match expected format in DB.add_meeting
            date_str = mail.get('date', '')
            try:
                from datetime import datetime
                # Parse email date format
                parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                # Convert to expected format
                formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_date = date_str  # Keep original if parsing fails
                
            meetings.append({
                'participants': participants,
                'organizer': mail.get('from', ''),
                'from': from_email,
                'subject': mail.get('subject', ''),
                'date': formatted_date,
                'body': body,
                'duration': duration,
                'meeting_id': meeting_id,
            })
        return meetings

    def calculate_meeting_cost(self, details: dict) -> tuple:
        """
        Calculate the total meeting cost and return explanation.
        
        Args:
            details: Dict with meeting information
            
        Returns:
            Tuple of (cost, explanation)
        """
        duration_min = details.get('duration')
        if duration_min is None or duration_min <= 0:
            duration_hr = 1.0  # Default to 1 hour 
            duration_str = "1 hour (default)"
        else:
            duration_hr = duration_min / 60.0
            duration_str = f"{duration_min} minutes ({duration_hr:.2f} hours)"
        
        total_cost = 0.0
        cost_breakdown = []
        
        for username in details.get('participants', []):
            wage = username_to_wage(username)
            participant_cost = wage * duration_hr
            total_cost += participant_cost
            cost_breakdown.append(f"{username}: {wage}/hr * {duration_hr:.2f}hr = {participant_cost:.2f}")
        
        explanation = f"Meeting cost: {total_cost:.2f} for {duration_str}\nBreakdown:\n" + "\n".join(cost_breakdown)
        return total_cost, explanation

    def extract_duration_from_body(self, body: str) -> int | None:
        """
        Extracts meeting duration in minutes from the 'When:' line in the email body.
        Example line: 'When: 29 August 2025 21:00-21:30.'
        Returns duration in minutes, or None if not found.
        """
        match = re.search(r'When:.*?(\d{2}:\d{2})-(\d{2}:\d{2})', body)
        if match:
            start = match.group(1)
            end = match.group(2)
            h1, m1 = map(int, start.split(':'))
            h2, m2 = map(int, end.split(':'))
            return (h2 * 60 + m2) - (h1 * 60 + m1)
        return None

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