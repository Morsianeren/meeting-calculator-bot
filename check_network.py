#!/usr/bin/env python
"""
Simple network connectivity check for email servers
"""

import socket
import ssl
import sys

def check_connection(host, port, use_ssl=False, timeout=10):
    print(f"Checking connection to {host}:{port}...")
    try:
        # First try basic socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        
        print(f"- Resolving hostname {host}...")
        try:
            ip_address = socket.gethostbyname(host)
            print(f"- Resolved to IP: {ip_address}")
        except socket.gaierror as e:
            print(f"- Failed to resolve hostname: {e}")
            return False
            
        print(f"- Connecting to {host}:{port} ({ip_address}:{port})...")
        s.connect((host, port))
        
        if use_ssl:
            print(f"- Establishing SSL connection...")
            context = ssl.create_default_context()
            ss = context.wrap_socket(s, server_hostname=host)
            ss.do_handshake()
            print(f"- SSL connection established")
            cert = ss.getpeercert()
            print(f"- Server certificate subject: {cert['subject']}")
            ss.close()
        else:
            print(f"- TCP connection established")
            
        s.close()
        print(f"✅ Connection to {host}:{port} successful")
        return True
        
    except socket.timeout:
        print(f"❌ Connection to {host}:{port} timed out")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection to {host}:{port} refused - service might not be running")
        return False
    except ssl.SSLError as e:
        print(f"❌ SSL error connecting to {host}:{port}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to {host}:{port}: {e}")
        return False

def main():
    print("=== Testing Connection to Common Email Servers ===")
    
    # Test common email services for comparison
    check_connection("gmail.com", 443, use_ssl=True)
    print("\n")
    check_connection("outlook.com", 443, use_ssl=True)
    print("\n")
    
    # Test GMX servers
    print("=== Testing Connection to GMX Servers ===")
    check_connection("gmx.com", 80)
    print("\n")
    check_connection("gmx.com", 443, use_ssl=True)
    print("\n")
    check_connection("smtp.gmx.com", 465, use_ssl=True)
    print("\n")
    check_connection("imap.gmx.com", 993, use_ssl=True)

if __name__ == "__main__":
    main()
