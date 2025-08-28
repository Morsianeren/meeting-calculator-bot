import os
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))

# Set default values for testing environment or use environment variables
# This helps prevent tests from hanging when environment variables aren't set
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'test@example.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'test_password')
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmx.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmx.com')

# Send email using HTML template
def send_email(to, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    msg['Subject'] = subject
    with open(os.path.join(os.path.dirname(__file__), '../../config/templates/email_template.html')) as f:
        html = f.read().replace('{{ body }}', body)
    msg.attach(MIMEText(html, 'html'))
    with smtplib.SMTP_SSL(SMTP_SERVER) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

# Fetch emails from IMAP
def fetch_emails(max_emails=None, search_criteria='ALL'):
    with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')
        typ, data = mail.search(None, search_criteria)
        emails = []
        
        # If no emails found
        if not data[0]:
            return emails
            
        email_ids = data[0].split()
        
        # Limit the number of emails if specified
        if max_emails:
            email_ids = email_ids[-max_emails:]
            
        for num in email_ids:
            typ, msg_data = mail.fetch(num, '(RFC822)')
            if msg_data and msg_data[0]:
                emails.append(msg_data[0][1])
        return emails

# Parse email message into a more usable format
def parse_email(raw_email):
    import email
    from email.header import decode_header
    
    message = email.message_from_bytes(raw_email)
    
    subject = message.get('Subject', '')
    from_email = message.get('From', '')
    date = message.get('Date', '')
    
    body = ""
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" or content_type == "text/html":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = message.get_payload(decode=True).decode()
        
    return {
        'subject': subject,
        'from': from_email,
        'date': date,
        'body': body,
        'raw': message
    }
