#!/usr/bin/env python
"""
Email Connection Diagnostics Script

This script tests connectivity to email servers using credentials from the .env file.
It provides detailed error information to help troubleshoot connection issues.
"""

import os
import sys
import socket
import smtplib
import imaplib
import ssl
from dotenv import load_dotenv
import time

def print_header(message):
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80)

def print_result(success, message):
    if success:
        print("✅ " + message)
    else:
        print("❌ " + message)

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = os.path.join(os.path.dirname(__file__), 'config/.env')
    
    print_header("CHECKING ENVIRONMENT VARIABLES")
    
    # Check if .env file exists
    if not os.path.exists(env_path):
        print_result(False, f".env file not found at {env_path}")
        return False
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check required variables
    required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'SMTP_SERVER', 'IMAP_SERVER']
    all_vars_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print_result(False, f"{var} is missing or empty")
            all_vars_present = False
        else:
            masked_value = value[:3] + "*" * (len(value) - 3) if var == 'EMAIL_PASSWORD' else value
            print_result(True, f"{var} = {masked_value}")
    
    return all_vars_present

def check_network_connectivity():
    """Check general network connectivity"""
    print_header("CHECKING NETWORK CONNECTIVITY")
    
    targets = [
        ("google.com", 443),
        (os.getenv('SMTP_SERVER'), 465),
        (os.getenv('IMAP_SERVER'), 993)
    ]
    
    all_connections_ok = True
    
    for host, port in targets:
        try:
            start_time = time.time()
            sock = socket.create_connection((host, port), timeout=10)
            duration = time.time() - start_time
            sock.close()
            print_result(True, f"Connected to {host}:{port} in {duration:.2f} seconds")
        except socket.error as e:
            print_result(False, f"Failed to connect to {host}:{port} - {str(e)}")
            all_connections_ok = False
    
    return all_connections_ok

def test_smtp_connection():
    """Test SMTP server connection"""
    print_header("TESTING SMTP CONNECTION")
    
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    
    try:
        # Try connection only
        print("Connecting to SMTP server...")
        start_time = time.time()
        server = smtplib.SMTP_SSL(smtp_server)
        connection_time = time.time() - start_time
        print_result(True, f"Connected to {smtp_server} in {connection_time:.2f} seconds")
        
        # Try login
        print("Attempting login...")
        start_time = time.time()
        server.login(email, password)
        login_time = time.time() - start_time
        print_result(True, f"Login successful in {login_time:.2f} seconds")
        
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print_result(False, f"Authentication failed: {str(e)}")
        print("This likely means your username or password is incorrect.")
        print("Some email providers may require an app-specific password instead of your regular password.")
        return False
    except ssl.SSLError as e:
        print_result(False, f"SSL error: {str(e)}")
        print("This could indicate an SSL/TLS issue with the connection.")
        return False
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        return False

def test_imap_connection():
    """Test IMAP server connection"""
    print_header("TESTING IMAP CONNECTION")
    
    email = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    imap_server = os.getenv('IMAP_SERVER')
    
    try:
        # Try connection only
        print("Connecting to IMAP server...")
        start_time = time.time()
        mail = imaplib.IMAP4_SSL(imap_server)
        connection_time = time.time() - start_time
        print_result(True, f"Connected to {imap_server} in {connection_time:.2f} seconds")
        
        # Try login
        print("Attempting login...")
        start_time = time.time()
        mail.login(email, password)
        login_time = time.time() - start_time
        print_result(True, f"Login successful in {login_time:.2f} seconds")
        
        # List mailboxes
        print("Listing mailboxes...")
        result, mailboxes = mail.list()
        if result == 'OK':
            print_result(True, f"Found {len(mailboxes)} mailboxes")
            print("Available mailboxes:")
            for mailbox in mailboxes[:5]:  # Show only first 5 to avoid clutter
                print(f"  - {mailbox.decode()}")
            if len(mailboxes) > 5:
                print(f"  ... and {len(mailboxes) - 5} more")
        
        # Check inbox
        print("Selecting inbox...")
        mail.select('inbox')
        result, data = mail.search(None, 'ALL')
        
        if result == 'OK':
            ids = data[0].split()
            print_result(True, f"Found {len(ids)} emails in inbox")
        else:
            print_result(False, "Failed to search inbox")
        
        mail.logout()
        return True
    except imaplib.IMAP4.error as e:
        print_result(False, f"IMAP error: {str(e)}")
        return False
    except ssl.SSLError as e:
        print_result(False, f"SSL error: {str(e)}")
        print("This could indicate an SSL/TLS issue with the connection.")
        return False
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        return False

def run_diagnostics():
    """Run all diagnostics and provide a summary"""
    results = {}
    
    # Step 1: Check environment variables
    results["env_check"] = check_env_file()
    if not results["env_check"]:
        print("\n⚠️ Environment variable issues detected. Please fix before proceeding.")
        return
    
    # Step 2: Check network connectivity
    results["network_check"] = check_network_connectivity()
    if not results["network_check"]:
        print("\n⚠️ Network connectivity issues detected. This might affect email communication.")
    
    # Step 3: Test SMTP
    results["smtp_check"] = test_smtp_connection()
    
    # Step 4: Test IMAP
    results["imap_check"] = test_imap_connection()
    
    # Print summary
    print_header("DIAGNOSIS SUMMARY")
    
    if all(results.values()):
        print("🎉 All checks passed! Your email configuration appears to be working correctly.")
        print("You should be able to send and receive emails with the current settings.")
    else:
        print("⚠️ Some checks failed. Here's a summary of what needs attention:")
        
        if not results.get("env_check", True):
            print("- Environment variables are missing or incorrect.")
            print("  Please check your config/.env file and ensure all required variables are set.")
        
        if not results.get("network_check", True):
            print("- Network connectivity issues were detected.")
            print("  Check your internet connection and firewall settings.")
        
        if not results.get("smtp_check", True):
            print("- SMTP connection failed.")
            print("  Check your email address, password, and SMTP server settings.")
        
        if not results.get("imap_check", True):
            print("- IMAP connection failed.")
            print("  Check your email address, password, and IMAP server settings.")
        
        print("\nCommon issues and solutions:")
        print("1. Incorrect password: Double-check your password in the .env file")
        print("2. App-specific password needed: Some providers like Google require app-specific passwords")
        print("3. Less secure app access: Some providers require enabling this setting")
        print("4. Firewall blocking: Your network might be blocking email ports")
        print("5. Incorrect server settings: Verify SMTP and IMAP server addresses and ports")

if __name__ == "__main__":
    run_diagnostics()
