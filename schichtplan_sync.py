#!/usr/bin/env python3

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2024-03-19
# Version: 2.12.0

import logging
import argparse
import os
import requests
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from utils.mail_utils import send_mail, verify_smtp_credentials
from utils.pdf_processor import extract_and_create_ical
from utils.ftp_uploader import upload_to_ftp, compare_ics_files, verify_ftp_credentials
from utils.config_loader import load_config, get_default_continuation_days, get_pdf_url
from utils.credentials_manager import get_credentials

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Configure logging to suppress warnings
logging.getLogger('pdfplumber').setLevel(logging.ERROR)
logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('pdfminer.psparser').setLevel(logging.ERROR)
logging.getLogger('pdfminer.pdfdocument').setLevel(logging.ERROR)
logging.getLogger('pdfminer.pdfpage').setLevel(logging.ERROR)
logging.getLogger('pdfminer.pdfinterp').setLevel(logging.ERROR)
logging.getLogger('pdfminer.converter').setLevel(logging.ERROR)
logging.getLogger('pdfminer.cmapdb').setLevel(logging.ERROR)

def download_pdf(url: str, username: str, password: str) -> bytes:
    """Download PDF with basic auth"""
    try:
        print(f"Downloading PDF from {url} with given credentials")
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return None

def compare_pdf_content(new_pdf_content: bytes) -> bool:
    """Compare new PDF content with previous PDF content using hash"""
    hash_file = os.path.expanduser('~/.schichtplan_pdf_hash')

    # Calculate hash of new PDF content
    new_hash = hashlib.sha256(new_pdf_content).hexdigest()

    # Try to read previous hash
    try:
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                old_hash = f.read().strip()
            if old_hash == new_hash:
                print("PDF content has not changed since last execution")
                return False
    except Exception as e:
        print(f"Error reading previous PDF hash: {e}")

    # Save new hash
    try:
        with open(hash_file, 'w') as f:
            f.write(new_hash)
        os.chmod(hash_file, 0o600)  # Set secure permissions
    except Exception as e:
        print(f"Warning: Could not save PDF hash: {e}")

    return True

def verify_http_credentials(pdf_url: str):
    """Verify HTTP basic authentication credentials for the configured PDF URL."""
    username, password = get_credentials()
    response = None
    try:
        response = requests.get(pdf_url, auth=(username, password), stream=True, timeout=30)
        response.raise_for_status()
        print("HTTP authentication credentials verified successfully")
        return username, password
    except requests.exceptions.RequestException as e:
        print(f"Error verifying HTTP credentials: {e}")
        return None, None
    finally:
        if response is not None:
            response.close()

def main():
    parser = argparse.ArgumentParser(
        description='Convert PDF schedule to iCal with shift continuation')
    parser.add_argument('--name', metavar='STR',
                        help='Name to search for in the schedule '
                             '(optional, if not provided will read from config)')
    parser.add_argument('--local', metavar='FILE',
                        help='Path to a local PDF file for testing (optional)')
    parser.add_argument('--family', action='store_true', help='Include first name in event summary')
    parser.add_argument('--no-ftp', action='store_true', help='Skip FTP upload')
    parser.add_argument('--mail', action='store_true', help='Enable email notifications (default)')
    parser.add_argument('--no-mail', action='store_true', help='Disable email notifications')
    parser.add_argument('--force', action='store_true', help='Force processing even if PDF has not changed')
    parser.add_argument('--extend', action='store_true', help='Extend schedule using default pattern (default)')
    parser.add_argument('--no-extend', action='store_true', help='Disable schedule extension')
    parser.add_argument('--extend-days', metavar='INT', type=int, default=None,
                        help='Number of days to extend schedule '
                             '(if not specified, uses config default_continuation_days value)')
    parser.add_argument('--setup-ftp', action='store_true',
                        help='Prompt for and verify FTP credentials, then exit')
    parser.add_argument('--setup-smtp', action='store_true',
                        help='Prompt for and verify SMTP credentials, then exit')
    parser.add_argument('--setup-auth', action='store_true',
                        help='Prompt for and verify HTTP basic authentication credentials, then exit')

    args = parser.parse_args()

    # Handle mail arguments
    if args.no_mail:
        args.mail = False
    else:
        args.mail = True

    # Handle extend arguments
    if args.no_extend:
        args.extend = False
    else:
        args.extend = True

    # Load configuration
    SHIFTS, USERS = load_config()
    if not SHIFTS:
        print("Failed to load configuration")
        exit(1)

    # Handle extend_days parameter - use config default if None
    if args.extend_days is None:
        args.extend_days = get_default_continuation_days()

    setup_requested = args.setup_ftp or args.setup_smtp or args.setup_auth

    pdf_url = None
    parsed_url = None
    http_credentials = None

    if args.setup_auth:
        pdf_url = get_pdf_url()
        if not pdf_url:
            print("Error: PDF URL not configured in config.json")
            exit(1)
        parsed_url = urlparse(pdf_url)
        if parsed_url.scheme not in ('http', 'https'):
            print("HTTP basic authentication setup requested, but configured PDF URL is not HTTP(S)")
            exit(1)
        http_credentials = verify_http_credentials(pdf_url)
        if not all(http_credentials):
            exit(1)

    if args.setup_ftp:
        if not verify_ftp_credentials():
            exit(1)

    if args.setup_smtp:
        if not verify_smtp_credentials():
            exit(1)

    if setup_requested:
        print("Credential setup completed successfully.")
        exit(0)

    if not args.local:
        if not pdf_url:
            pdf_url = get_pdf_url()
            if not pdf_url:
                print("Error: PDF URL not configured in config.json")
                exit(1)
        if not parsed_url:
            parsed_url = urlparse(pdf_url)

        if parsed_url.scheme in ('http', 'https'):
            if not http_credentials:
                http_credentials = verify_http_credentials(pdf_url)
                if not all(http_credentials):
                    exit(1)
        else:
            http_credentials = (None, None)

    if not args.no_ftp:
        if not verify_ftp_credentials():
            exit(1)

    if args.mail:
        if not verify_smtp_credentials():
            exit(1)

    pdf_content = None

    if args.local:
        try:
            print(f"Using local PDF file: {args.local}")
            with open(args.local, 'rb') as f:
                pdf_content = f.read()
        except Exception as e:
            print(f"Error reading local PDF file: {e}")
            exit(1)
    else:
        if not parsed_url:
            print("Error: PDF URL not configured in config.json")
            exit(1)

        if parsed_url.scheme in ('http', 'https'):
            username, password = http_credentials
            pdf_content = download_pdf(pdf_url, username, password)
        else:
            local_path_str = parsed_url.path if parsed_url.scheme == 'file' else pdf_url
            if parsed_url.scheme == 'file' and parsed_url.netloc:
                local_path_str = f"//{parsed_url.netloc}{parsed_url.path}"
            local_path = Path(local_path_str).expanduser()

            if not local_path.is_file():
                print(f"Error: Local PDF file not found at {local_path}")
                exit(1)

            try:
                print(f"Using local PDF file from config: {local_path}")
                with open(local_path, 'rb') as f:
                    pdf_content = f.read()
            except Exception as e:
                print(f"Error reading local PDF file from config: {e}")
                exit(1)

        if pdf_content is None:
            print("Failed to obtain PDF content")
            exit(1)

    # Check if PDF has changed, unless force flag is set
    if not args.force and not compare_pdf_content(pdf_content):
        print("Skipping processing as PDF has not changed")
        exit(0)

    if args.name:
        # Single name processing
        name = args.name.strip()
        print(f"Processing schedule for: {name} {'(with family mode)' if args.family else ''}")

        # Find the user's email from config
        user_email = None
        for user_name, family, mail in USERS:
            if user_name == name:
                user_email = mail
                break

        ical_file = extract_and_create_ical(
            pdf_content,
            name,
            SHIFTS,
            args.family,
            args.extend,
            args.extend_days
        )

        if ical_file and not args.no_ftp:
            # Get changes for email notification BEFORE FTP upload
            old_file = os.path.join(os.path.dirname(ical_file), f"old_{os.path.basename(ical_file)}")
            changes, has_changes = compare_ics_files(ical_file, old_file)

            if upload_to_ftp(ical_file) and user_email and args.mail:
                if has_changes and changes:
                    send_mail(user_email, name, changes)
    else:
        # Process all users from config
        if not USERS:
            print("No users found in configuration")
            exit(1)

        print(f"Found {len(USERS)} users in configuration")
        for name, use_family, mail in USERS:
            print(f"\nProcessing schedule for: {name} {'(with family mode)' if use_family else ''}")
            ical_file = extract_and_create_ical(
                pdf_content,
                name,
                SHIFTS,
                use_family,
                args.extend,
                args.extend_days
            )

            if ical_file and not args.no_ftp:
                # Get changes for email notification BEFORE FTP upload
                old_file = os.path.join(os.path.dirname(ical_file), f"old_{os.path.basename(ical_file)}")
                changes, has_changes = compare_ics_files(ical_file, old_file)

                if upload_to_ftp(ical_file) and mail and args.mail:
                    if has_changes and changes:
                        send_mail(mail, name, changes)

        print(f"Sync complete for {len(USERS) if USERS else 0} users")

if __name__ == "__main__":
    main()