import pytest
from src.bot.email_server import EmailServer

# Integration test for poll_for_new_emails

def test_poll_for_new_emails_prints_new_emails(capfd):
    server = EmailServer()
    emails = server.poll_for_new_emails()
    assert emails, "No new emails found"
    print("Polled Emails:")
    for email in emails:
        print(email)
    # Capture output and assert at least one email printed (manual test)
    out, _ = capfd.readouterr()
    assert out.strip() != ""
