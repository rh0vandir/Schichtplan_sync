#!/usr/bin/env python3

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2024-03-19
# Version: 1.0

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from getpass import getpass
import argparse

def get_smtp_credentials():
    """Get SMTP credentials from encrypted file or prompt user"""
    credentials_file = os.path.expanduser('~/.schichtplan_smtp_credentials')
    key_file = os.path.expanduser('~/.schichtplan_smtp_key')
    
    # Try to load existing credentials
    if os.path.exists(credentials_file) and os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            fernet = Fernet(key)
            
            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            smtp_host, smtp_port, smtp_user, smtp_pass = decrypted_data.decode().split(':')
            return smtp_host, smtp_port, smtp_user, smtp_pass
        except Exception as e:
            print(f"Error reading SMTP credentials: {e}")
            return None, None, None, None
    else:
        # If no credentials file or error, prompt user
        print("Bitte gebe deine SMTP Zugangsdaten ein:")
        smtp_host = input("SMTP Host: ")
        smtp_port = input("SMTP Port: ")
        smtp_user = input("SMTP Nutzername: ")
        smtp_pass = getpass("SMTP Passwort: ")
        
        # Save credentials
        try:
            # Generate new key if needed
            if not os.path.exists(key_file):
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
            else:
                with open(key_file, 'rb') as f:
                    key = f.read()
            
            fernet = Fernet(key)
            data = f"{smtp_host}:{smtp_port}:{smtp_user}:{smtp_pass}"
            encrypted_data = fernet.encrypt(data.encode())
            
            with open(credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            os.chmod(credentials_file, 0o600)
            os.chmod(key_file, 0o600)
            
        except Exception as e:
            print(f"Warning: Could not save SMTP credentials: {e}")
        
        return smtp_host, smtp_port, smtp_user, smtp_pass

def send_mail(recipient_email, user_name, changes=None, subject=None, custom_body=None):
    """Send email notification about schedule changes or custom message"""
    try:
        # Get SMTP credentials
        smtp_host, smtp_port, smtp_user, smtp_pass = get_smtp_credentials()
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            print("Failed to get SMTP credentials")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        
        # Use custom subject or default
        if subject:
            msg['Subject'] = subject
        else:
            msg['Subject'] = "Schichtplan Update"
        
        # Create email body
        if custom_body:
            body = custom_body
        else:
            body = f"Hallo {user_name},\n\nDein Schichtplan wurde aktualisiert."
            if changes:
                body += "\n\nFolgende Änderungen wurden vorgenommen:\n"
                for change in changes:
                    body += f"- {change}\n"
                body += "\nDie Änderungen werden demnächst in deinen Kalender übernommen."
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Configure SSL context
        context = ssl.create_default_context()
        
        # Send email with timeout
        try:
            with smtplib.SMTP(smtp_host, int(smtp_port), timeout=30) as server:
                server.set_debuglevel(0)  # disable debug output
                server.starttls(context=context)
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                
            print(f"Email notification sent to {recipient_email}")
            return True
            
        except smtplib.SMTPException as e:
            print(f"SMTP error: {e}")
            return False
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            return False
        except TimeoutError as e:
            print(f"Connection timeout: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
        
    except Exception as e:
        print(f"Error in send_mail: {e}")
        return False

def send_notification_email(recipient_email, subject, message):
    """Send a simple notification email"""
    return send_mail(recipient_email, "User", custom_body=message, subject=subject)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send email notifications')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', help='Email subject (default: Schichtplan Update)')
    parser.add_argument('--message', help='Custom message body')
    parser.add_argument('--name', help='Recipient name (for personalized messages)')
    parser.add_argument('--changes', nargs='*', help='List of changes to include in the email')
    
    args = parser.parse_args()
    
    if args.message:
        # Send custom message
        success = send_notification_email(args.to, args.subject or "Notification", args.message)
    else:
        # Send schedule update
        success = send_mail(args.to, args.name or "User", args.changes, args.subject)
    
    exit(0 if success else 1) 