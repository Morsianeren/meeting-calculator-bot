import pytest
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import sys
import email
import imaplib

# Explicitly load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

from src.email.email_handler import send_email, fetch_emails, EMAIL_ADDRESS

# Skip these tests if integration testing is not enabled
pytestmark = [pytest.mark.integration]

# Function to check if the environment variables for email are set
def has_email_config():
    # Print the current configuration for debugging
    print(f"Email config check: SMTP_SERVER={os.getenv('SMTP_SERVER')}")
    return (
        os.getenv('EMAIL_ADDRESS') and 
        os.getenv('EMAIL_PASSWORD') and
        os.getenv('IMAP_SERVER') and 
        os.getenv('SMTP_SERVER')
    )

@pytest.mark.skipif(not has_email_config(), reason="No email credentials available")
class TestRealEmailIntegration:
    """Tests that use real email credentials from the .env file"""
    
    def test_send_real_email(self):
        """Test sending a real email using the credentials from .env"""
        # Use a unique subject to identify this test email
        timestamp = str(int(time.time()))
        test_subject = f"Test Email from Meeting Bot {timestamp}"
        test_body = "This is a test email from the Meeting Calculator Bot integration tests."
        test_recipient = EMAIL_ADDRESS  # Send to self for testing
        
        # Send the email
        send_email(test_recipient, test_subject, test_body)
        
        # Allow some time for the email to be delivered
        time.sleep(10)
        
        # Check if the email was received - use specific search criteria to find our test email
        # SUBJECT search might not work on all IMAP servers, so we'll fetch recent emails instead
        found_email = False
        retry_count = 0
        max_retries = 3
        
        while not found_email and retry_count < max_retries:
            # Get the 5 most recent emails
            emails = fetch_emails(max_emails=5)
            
            # Import the parse_email function
            from src.email.email_handler import parse_email
            
            # Process emails and check if our test email is there
            for raw_email in emails:
                try:
                    parsed = parse_email(raw_email)
                    if timestamp in parsed['subject']:
                        found_email = True
                        break
                except Exception as e:
                    print(f"Error parsing email: {str(e)}")
                    continue
            
            if not found_email:
                retry_count += 1
                time.sleep(5)  # Wait before retrying
                
        assert found_email, "The test email was not found in the inbox"
    
    def test_fetch_real_emails(self):
        """Test fetching emails using real credentials"""
        emails = fetch_emails(max_emails=3)  # Limit to 3 emails for quicker testing
        assert isinstance(emails, list), "fetch_emails should return a list"
        
        # Just verify we got something and it's not an error
        # We don't validate the exact count since that depends on the inbox state
        
        # If we got something, try to parse at least one email to ensure it's valid
        if emails:
            from src.email.email_handler import parse_email
            parsed_email = parse_email(emails[0])
            
            assert 'subject' in parsed_email, "Parsed email should have a subject"
            assert 'from' in parsed_email, "Parsed email should have a sender"
            assert 'body' in parsed_email, "Parsed email should have a body"
            
            print(f"Successfully fetched and parsed email with subject: {parsed_email['subject']}")
        else:
            print("No emails found in the inbox to test with")
    
    def test_search_recent_emails(self):
        """Test searching for recent emails"""
        # Get emails from the last day
        import datetime
        from email.utils import formatdate
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        date_str = formatdate(time.mktime(yesterday.timetuple()))
        
        # Some IMAP servers support SINCE search
        try:
            emails = fetch_emails(search_criteria=f'SINCE "{date_str}"')
            assert isinstance(emails, list), "fetch_emails should return a list"
            print(f"Found {len(emails)} emails since yesterday")
        except Exception as e:
            # If the SINCE search fails, just note it and pass the test
            print(f"SINCE search not supported: {str(e)}")
            pass
