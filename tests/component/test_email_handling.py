import pytest
from unittest.mock import patch
from src.email.email_handler import *
import src.email.email_handler as email_handler

@patch('smtplib.SMTP_SSL')
def test_send_email(mock_smtp):
    # Set up the mock SMTP server
    mock_server = mock_smtp.return_value.__enter__.return_value
    
    # Call the function
    send_email('test@deif.com', 'Subject', 'Body')
    
    # Assert the server was used correctly
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()


# Negative test: send_email raises exception
@patch('src.email.email_handler.send_email')
def test_send_email_failure(mock_send):
    mock_send.side_effect = Exception("SMTP error")
    with pytest.raises(Exception) as excinfo:
        email_handler.send_email('test@deif.com', 'Subject', 'Body')
    assert "SMTP error" in str(excinfo.value)

@patch('src.email.email_handler.fetch_emails')
def test_fetch_emails(mock_fetch):
    mock_fetch.return_value = ['email1', 'email2']
    emails = email_handler.fetch_emails()
    assert emails == ['email1', 'email2']


# Negative test: fetch_emails returns empty list
@patch('src.email.email_handler.fetch_emails')
def test_fetch_emails_empty(mock_fetch):
    mock_fetch.return_value = []
    emails = email_handler.fetch_emails()
    assert emails == []

# Negative test: fetch_emails raises exception
@patch('src.email.email_handler.fetch_emails')
def test_fetch_emails_failure(mock_fetch):
    mock_fetch.side_effect = Exception("IMAP error")
    with pytest.raises(Exception) as excinfo:
        email_handler.fetch_emails()
    assert "IMAP error" in str(excinfo.value)
