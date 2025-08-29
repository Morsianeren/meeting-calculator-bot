"""
Handles polling and sending emails for the Meeting Calculator Bot.
"""
from email.header import decode_header
import email
import imaplib
import os
import smtplib
from email.mime.text import MIMEText

class EmailServer:

    
    def poll_for_new_emails(self) -> dict:
        """
        Connect to the IMAP server and fetch unread emails.

        Returns:
            dict: A dictionary of unread emails where each key is the email ID (string),
                and the value is another dict containing:
                    - subject (str)
                    - from (str)
                    - date (str)
                    - body (str, plain text if available)

        Example:
            {'10': 
                {'subject': 'FW: Testmøde - Ignorer', 
                 'from': 'Magnus Blach Klokker <mak@deif.com>', 
                 'date': 'Fri, 29 Aug 2025 07:05:03 +0000', 
                 'body': '________________________________\r\nFrom: Magnus Blach Klokker <mak@deif.com>\r\nSent: 26 August 2025 20:35:20 (UTC+01:00) Brussels, Copenhagen, Madrid, Paris\r\nTo: Christian Raun Hornebo <crh@deif.com>\r\nCc: morsianeren@gmail.com <morsianeren@gmail.com>; meeting-bot@gmx.com <meeting-bot@gmx.com>; meetingbott@gmx.com <meetingbott@gmx.com>\r\nSubject: Testmde - Ignorer\r\nWhen: 29 August 2025 21:00-21:30.\r\nWhere: Deif Placering\r\n\r\n\r\ntestbeskrivelse'}}
        """
        IMAP_SERVER = os.getenv('IMAP_HOST', 'imap.gmx.com')
        EMAIL_ACCOUNT = os.getenv('IMAP_USER', 'meetingbott@gmx.com')
        PASSWORD = os.getenv('IMAP_PASS', 'QWERTa123!')
        MAILBOX = os.getenv('IMAP_MAILBOX', 'INBOX')
        FETCH_LIMIT = 10
        
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        mail.select(MAILBOX)

        # Search emails (latest first)
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        latest_emails = email_ids[-FETCH_LIMIT:]

        emails_dict = {}

        for eid in reversed(latest_emails):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject = clean_text(msg.get("Subject"))
                    from_ = clean_text(msg.get("From"))
                    date = msg.get("Date")

                    # Extract email body (prefer plain text)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                                try:
                                    body = part.get_payload(decode=True).decode(errors="ignore").strip()
                                except Exception:
                                    body = ""
                                break
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode(errors="ignore").strip()
                        except Exception:
                            body = ""

                    # Add to dictionary
                    emails_dict[eid.decode()] = {
                        "subject": subject,
                        "from": from_,
                        "date": date,
                        "body": body
                    }

        mail.logout()
        return emails_dict
    
    def send_email(self, recipient: str, subject: str, body: str):
        SMTP_SERVER = os.getenv('SMTP_HOST', 'smtp.gmx.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        EMAIL_ACCOUNT = os.getenv('SMTP_USER', 'meetingbott@gmx.com')
        PASSWORD = os.getenv('SMTP_PASS', 'QWERTa123!')

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ACCOUNT
        msg['To'] = recipient

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ACCOUNT, PASSWORD)
            server.sendmail(EMAIL_ACCOUNT, [recipient], msg.as_string())

def clean_text(text):
    """Decode and clean email headers."""
    if not text:
        return ""
    text, encoding = decode_header(text)[0]
    if isinstance(text, bytes):
        return text.decode(encoding or "utf-8", errors="ignore")
    return text

if __name__ == "__main__":
    server = EmailServer()
    emails = server.poll_for_new_emails()
    if not emails:
        print("No emails!")
    else:
        print(emails)
    for email in emails:
        print(email)
        #print(email["body"])