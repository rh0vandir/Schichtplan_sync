#!/usr/bin/env python3

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2024-03-19
# Version: 4.19

import pdfplumber
import logging
import argparse
from pathlib import Path
import re
import os
import requests
from cryptography.fernet import Fernet
from getpass import getpass
import io
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Component
import pytz
from ftplib import FTP
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib

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

def get_credentials():
    """Get credentials from encrypted file or prompt user"""
    credentials_file = os.path.expanduser('~/.schichtplan_credentials')
    key_file = os.path.expanduser('~/.schichtplan_key')
    
    # Try to load existing credentials
    if os.path.exists(credentials_file) and os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            fernet = Fernet(key)
            
            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            username, password = decrypted_data.decode().split(':')
            return username, password
        except Exception as e:
            print(f"Error reading credentials: {e}")
    
    # If no credentials file or error, prompt user
    print("Bitte gebe deine Zugangsdaten für den Schichtplan ein:")
    username = input("Nutzername: ")
    password = getpass("Passwort: ")
    
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
        data = f"{username}:{password}"
        encrypted_data = fernet.encrypt(data.encode())
        
        with open(credentials_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Set secure permissions
        os.chmod(credentials_file, 0o600)
        os.chmod(key_file, 0o600)
        
    except Exception as e:
        print(f"Warning: Could not save credentials: {e}")
    
    return username, password

def download_pdf(url, username, password):
    """Download PDF with basic auth"""
    try:
        print(f"Downloading PDF from {url} with given credentials")
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return None

def parse_shift_time(shift_code):
    """Parse shift code to extract shift letter and calculate time range"""
    if not shift_code:
        return '', None
    # Check for two-letter shift codes first (WF, WS)
    if len(shift_code) >= 2 and shift_code[:2] in ['WF', 'WS']:
        shift_letter = shift_code[:2]
        # Try to find time range in the format "WF8-16" or similar
        time_match = re.search(r'(\d{1,2})-(\d{1,2})', shift_code[2:])
    else:
        # Single letter shift code
        shift_letter = shift_code[0]
        # Try to find time range in the format "N20-7" or similar
        time_match = re.search(r'(\d{1,2})-(\d{1,2})', shift_code[1:])
    
    if time_match:
        start_hour = int(time_match.group(1))
        end_hour = int(time_match.group(2))
        
        # Format hours to two digits
        start_time = f"{start_hour:02d}:00"
        end_time = f"{end_hour:02d}:00"
        
        return shift_letter, f"{start_time}-{end_time}"
    
    return shift_letter, None

# Shift mapping with times and names
def get_shift_info(shift):
    """Get the time and name for a given shift code"""
    # First try to parse the shift code for custom time ranges
    shift_letter, custom_time = parse_shift_time(shift)
    
    # Get base shift info
    base_info = SHIFTS.get(shift_letter, {'start': '', 'end': '', 'name': ''})
    
    # If we found a custom time range, use it instead of the default
    if custom_time:
        start_time, end_time = custom_time.split('-')
        return {
            'start': start_time,
            'end': end_time,
            'name': base_info['name']
        }
    
    return base_info

def create_ical_file(dates, shifts, name, family=False):
    """Create an iCal file from the shift data"""
    cal = Calendar()
    cal.add('prodid', '-//Schichtplan Sync//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', f'Schichtplan {name}')
    cal.add('x-wr-timezone', 'Europe/Berlin')
    cal.add('x-wr-caldesc', f'Schichtplan für {name}')
    cal.add('refresh-interval', 'PT15M')  # Refresh every 15 minutes
    cal.add('x-published-ttl', 'PT15M')   # Time to live for published calendar
    cal.add('charset', 'UTF-8')
    
    # Add VTIMEZONE component
    tz = pytz.timezone('Europe/Berlin')
    vtimezone = Component()
    vtimezone.add('tzid', 'Europe/Berlin')
    vtimezone.name = 'VTIMEZONE'
    
    # Add standard time info
    standard = Component()
    standard.name = 'STANDARD'
    standard.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
    standard.add('rrule', {'freq': 'yearly', 'byday': '-1SU', 'bymonth': 10})
    standard.add('tzoffsetfrom', timedelta(hours=2))
    standard.add('tzoffsetto', timedelta(hours=1))
    standard.add('tzname', 'CET')
    vtimezone.add_component(standard)
    
    # Add daylight saving time info
    daylight = Component()
    daylight.name = 'DAYLIGHT'
    daylight.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
    daylight.add('rrule', {'freq': 'yearly', 'byday': '-1SU', 'bymonth': 3})
    daylight.add('tzoffsetfrom', timedelta(hours=1))
    daylight.add('tzoffsetto', timedelta(hours=2))
    daylight.add('tzname', 'CEST')
    vtimezone.add_component(daylight)
    
    cal.add_component(vtimezone)
    
    # Generate a unique base ID using timestamp and name
    base_uid = f"{int(datetime.now().timestamp())}_{name.replace(' ', '_')}"
    
    for idx, (date, shift) in enumerate(zip(dates, shifts)):
        if shift and shift != 'K':
            shift_info = get_shift_info(shift)
            if shift_info['start'] and shift_info['end']:
                
                # Parse date and times
                event_date = datetime.strptime(date, '%d.%m')
                event_date = event_date.replace(year=datetime.now().year)
                
                # Parse start time
                start_hour, start_minute = map(int, shift_info['start'].split(':'))
                start_dt = datetime.combine(event_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
                
                # Parse end time, handling 24:00 case
                end_hour, end_minute = map(int, shift_info['end'].split(':'))
                if end_hour == 24:
                    end_dt = datetime.combine(event_date + timedelta(days=1), datetime.min.time().replace(hour=0, minute=end_minute))
                else:
                    end_dt = datetime.combine(event_date, datetime.min.time().replace(hour=end_hour, minute=end_minute))
                
                # Handle overnight shifts
                if end_dt < start_dt and end_hour != 24:
                    end_dt += timedelta(days=1)
                
                # Localize to timezone
                start_dt = tz.localize(start_dt)
                end_dt = tz.localize(end_dt)
                
                # Create event
                event = Event()
                # Create consistent UID based on name and date only
                event.add('uid', f"schichtplan_{name.replace(' ', '_')}_{date.replace('.', '')}")
                
                # Create summary based on family flag
                first_name = name.split()[0] if family else ''
                prefix = f"{first_name} " if family else ""
                if shift in ['F', 'K', 'X', 'U']:
                    summary = f"{prefix}{shift}"
                else:
                    # Extract just the hour part from the time
                    start_hour = shift_info['start'].split(':')[0]
                    end_hour = shift_info['end'].split(':')[0]
                    # Remove numbers and "HO" from shift letter
                    shift_letter = ''.join(c for c in shift if not c.isdigit()).replace('HO', '')
                    summary = f"{prefix}{shift_letter} {start_hour}-{end_hour}"
                event.add('summary', summary)
                
                # Create description with Homeoffice info if present
                description = f'Schicht: {shift}\nName: {name}'
                if 'HO' in shift:
                    description += '\nHomeoffice'
                event.add('description', description)
                
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('dtstamp', datetime.now(tz))
                event.add('created', datetime.now(tz))
                event.add('last-modified', datetime.now(tz))
                event.add('sequence', '1')  # Start with sequence 1
                event.add('status', 'CONFIRMED')
                event.add('transp', 'OPAQUE')
                event.add('class', 'PUBLIC')
                event.add('all-day', False)
                
                cal.add_component(event)
    
    # Save calendar to file with proper line endings
    ical_file = f"schichtplan_{name.replace(' ', '_')}.ics"
    ical_content = cal.to_ical().decode('utf-8').replace('\r\n', '\n').replace('\n', '\r\n')
    with open(ical_file, 'wb') as f:
        f.write(ical_content.encode('utf-8'))
    
    print(f"iCal file created: {ical_file}")
    return ical_file

def extract_and_create_ical(pdf_content, name, family=False):
    """Extract data from PDF and directly create iCal file"""
    try:
        # Convert PDF content to file-like object
        pdf_file = io.BytesIO(pdf_content)
        
        # Store dates and shifts
        dates = []
        shifts = []
        
        # Process PDF and extract data
        with pdfplumber.open(pdf_file) as pdf:
            # Process each page
            for page in pdf.pages:
                # print(f"Processing page {page.page_number}")
                tables = page.extract_tables()
                
                if tables:
                    # Process each table
                    for table in tables:
                        # Store relevant rows
                        all_rows = []
                        
                        # Process each row
                        for row in table:
                            # Clean up the row data
                            cleaned_row = [cell.strip() if cell else '' for cell in row]
                            
                            # Check if any cell in the row matches our criteria
                            has_match = False
                            for cell in cleaned_row:
                                if (cell.startswith(name) or 
                                    (len(cell) >= 4 and cell[:4].isdigit() and cell[:2] == "20")):
                                    has_match = True
                                    break
                            
                            # Only keep rows that match our criteria
                            if has_match:
                                filtered_row = []
                                for cell in cleaned_row:
                                    if not (cell.startswith(name) or 
                                           (len(cell) >= 4 and cell[:4].isdigit() and cell[:2] == "20")):
                                        filtered_row.append(cell)
                                if filtered_row:
                                    all_rows.append(filtered_row)
                        
                        # Process rows to extract dates and shifts
                        for row_idx in range(len(all_rows) - 1):
                            current_row = all_rows[row_idx]
                            next_row = all_rows[row_idx + 1]
                            
                            for col_idx, cell in enumerate(current_row):
                                date_match = re.search(r'\d{2}\.\d{2}', cell)
                                if date_match:
                                    date = date_match.group(0)
                                    dates.append(date)
                                    if col_idx < len(next_row):
                                        shifts.append(next_row[col_idx])
                                    else:
                                        shifts.append('')
        
        # Create iCal file directly from extracted data
        return create_ical_file(dates, shifts, name, family)
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

# Add FTP credentials handling
def get_ftp_credentials():
    """Get FTP credentials from encrypted file or prompt user"""
    credentials_file = os.path.expanduser('~/.schichtplan_ftp_credentials')
    key_file = os.path.expanduser('~/.schichtplan_ftp_key')
    
    # Try to load existing credentials
    if os.path.exists(credentials_file) and os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            fernet = Fernet(key)
            
            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            host, username, password = decrypted_data.decode().split(':')
            return host, username, password
        except Exception as e:
            print(f"Error reading FTP credentials: {e}")
    
    # If no credentials file or error, prompt user
    print("Bitte gebe deine FTP Zugangsdaten ein:")
    host = input("FTP Host: ")
    username = input("Nutzername: ")
    password = getpass("Passwort: ")
    
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
        data = f"{host}:{username}:{password}"
        encrypted_data = fernet.encrypt(data.encode())
        
        with open(credentials_file, 'wb') as f:
            f.write(encrypted_data)
        
        # Set secure permissions
        os.chmod(credentials_file, 0o600)
        os.chmod(key_file, 0o600)
        
    except Exception as e:
        print(f"Warning: Could not save FTP credentials: {e}")
    
    return host, username, password

def compare_ics_files(new_file, old_file):
    """Compare two ICS files and return a list of changes"""
    changes = []
    if not os.path.exists(old_file):
        changes.append("Initial calendar creation - all shifts added")
        return changes, True  # If no old file exists, consider it changed
        
    # Read both files
    with open(new_file, 'rb') as f:
        new_content = f.read()
    with open(old_file, 'rb') as f:
        old_content = f.read()
    
    # Parse both files
    new_cal = Calendar.from_ical(new_content)
    old_cal = Calendar.from_ical(old_content)
    
    # Compare basic calendar properties
    if new_cal.get('x-wr-calname') != old_cal.get('x-wr-calname'):
        changes.append(f"Calendar name changed from {old_cal.get('x-wr-calname')} to {new_cal.get('x-wr-calname')}")
    
    # Compare events
    new_events = {event.get('uid'): event for event in new_cal.walk('VEVENT')}
    old_events = {event.get('uid'): event for event in old_cal.walk('VEVENT')}
    
    # Check for removed events
    for uid, old_event in old_events.items():
        if uid not in new_events:
            date = old_event.get('dtstart').dt.strftime('%Y-%m-%d')
            changes.append(f"Shift removed: {old_event.get('summary')} on {date}")
    
    # Check for added events
    for uid, new_event in new_events.items():
        if uid not in old_events:
            date = new_event.get('dtstart').dt.strftime('%Y-%m-%d')
            changes.append(f"New shift added: {new_event.get('summary')} on {date}")
        else:
            old_event = old_events[uid]
            # Compare relevant properties
            if new_event.get('summary') != old_event.get('summary'):
                date = new_event.get('dtstart').dt.strftime('%Y-%m-%d')
                changes.append(f"Shift changed on {date}: {old_event.get('summary')} → {new_event.get('summary')}")
            elif (new_event.get('dtstart').dt != old_event.get('dtstart').dt or
                  new_event.get('dtend').dt != old_event.get('dtend').dt):
                date = new_event.get('dtstart').dt.strftime('%Y-%m-%d')
                old_start = old_event.get('dtstart').dt.strftime('%H:%M')
                old_end = old_event.get('dtend').dt.strftime('%H:%M')
                new_start = new_event.get('dtstart').dt.strftime('%H:%M')
                new_end = new_event.get('dtend').dt.strftime('%H:%M')
                changes.append(f"Shift time changed on {date}: {old_start}-{old_end} → {new_start}-{new_end}")
    
    return changes, len(changes) > 0

def upload_to_ftp(ical_file):
    """Upload ICS file to FTP server if it has changed"""
    try:
        host, username, password = get_ftp_credentials()
        
        # Compare with local file
        old_file = os.path.join(os.path.dirname(ical_file), f"old_{os.path.basename(ical_file)}")
        changes, has_changes = compare_ics_files(ical_file, old_file)
        if not has_changes:
            print(f"No changes detected in {ical_file}, skipping upload")
            return True
        
        print(f"Changes detected in {ical_file}, uploading to FTP server {host}")
        with FTP(host) as ftp:
            ftp.login(username, password)
            
            with open(ical_file, 'rb') as f:
                ftp.storbinary(f'STOR {os.path.basename(ical_file)}', f)
            
            # Save the current file as the old file for next comparison
            with open(old_file, 'wb') as f:
                with open(ical_file, 'rb') as src:
                    f.write(src.read())
            
            print(f"Successfully uploaded {ical_file} to FTP server")
            return True
            
    except Exception as e:
        print(f"Error uploading to FTP: {e}")
        return False

# Remove the hardcoded SHIFTS dictionary and add config loading
def load_config():
    """Load configuration from schichtplan_sync.json"""
    config_file = Path(__file__).parent / 'schichtplan_sync.json'
    
    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_file}")
        return None, None
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Parse shifts
        shifts = config['shifts']
            
        # Parse users
        users = []
        for user_id, user_data in config['users'].items():
            if user_id.startswith('user'):  # Skip non-user entries
                users.append((user_data['name'], user_data['family'], user_data['mail']))
                
        return shifts, users
        
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return None, None

# Replace the hardcoded SHIFTS with config loading
SHIFTS = None
USERS = None

def send_mail(recipient_email, user_name, changes=None):
    """Send email notification about schedule changes"""
    try:
        # Get SMTP credentials from encrypted file or prompt user
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
            except Exception as e:
                print(f"Error reading SMTP credentials: {e}")
                return False
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
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = "Schichtplan Update"
        
        # Create email body with changes
        body = f"Hallo {user_name},\n\nDein Schichtplan wurde aktualisiert."
        if changes:
            body += "\n\nFolgende Änderungen wurden vorgenommen:\n"
            for change in changes:
                body += f"- {change}\n"
        body += "\nDie Änderungen werden demnächst in deinen Kalender übernommen."
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Configure SSL context
        import ssl
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

def compare_pdf_content(new_pdf_content):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert PDF schedule to iCal')
    parser.add_argument('--name', help='Name to search for in the schedule (optional, if not provided will read from config)')
    parser.add_argument('--local', help='Path to a local PDF file for testing (optional)')
    parser.add_argument('--family', action='store_true', help='Include first name in event summary')
    parser.add_argument('--no-ftp', action='store_true', help='Skip FTP upload')
    parser.add_argument('--mail', action='store_true', help='Enable email notifications (default)')
    parser.add_argument('--no-mail', action='store_true', help='Disable email notifications')
    parser.add_argument('--force', action='store_true', help='Force processing even if PDF has not changed')
    
    args = parser.parse_args()
    
    # Handle mail arguments
    if args.no_mail:
        args.mail = False
    else:
        args.mail = True
    
    # Load configuration
    SHIFTS, USERS = load_config()
    if not SHIFTS:
        print("Failed to load configuration")
        exit(1)
    
    if args.local:
        try:
            print(f"Using local PDF file: {args.local}")
            with open(args.local, 'rb') as f:
                pdf_content = f.read()
        except Exception as e:
            print(f"Error reading local PDF file: {e}")
            exit(1)
    else:
        username, password = get_credentials()
        pdf_url = "https://example.com/path/to/schichtplan.pdf"
        pdf_content = download_pdf(pdf_url, username, password)
        if not pdf_content:
            print("Failed to download PDF")
            exit(1)
    
    # Check if PDF has changed, unless force flag is set
    if not args.force and not compare_pdf_content(pdf_content):
        print("Skipping processing as PDF has not changed")
        exit(0)
    
    if args.name:
        # Single name processing
        name = args.name.strip()
        print(f"Processing schedule for: {name} {'(with family mode)' if args.family else ''}")
        ical_file = extract_and_create_ical(pdf_content, name, args.family)
        if ical_file and not args.no_ftp:
            old_file = os.path.join(os.path.dirname(ical_file), f"old_{os.path.basename(ical_file)}")
            changes, has_changes = compare_ics_files(ical_file, old_file)
            if has_changes:
                if changes:
                    logging.info(f"Changes for {name}:")
                    for change in changes:
                        logging.info(f"  {change}")
                if upload_to_ftp(ical_file) and USERS[0][2] and args.mail:
                    send_mail(USERS[0][2], name, changes)
    else:
        # Process all users from config
        if not USERS:
            print("No users found in configuration")
            exit(1)
            
        print(f"Found {len(USERS)} users in configuration")
        for name, use_family, mail in USERS:
            print(f"\nProcessing schedule for: {name} {'(with family mode)' if use_family else ''}")
            ical_file = extract_and_create_ical(pdf_content, name, use_family)
            if ical_file and not args.no_ftp:
                old_file = os.path.join(os.path.dirname(ical_file), f"old_{os.path.basename(ical_file)}")
                changes, has_changes = compare_ics_files(ical_file, old_file)
                if has_changes:
                    if changes:
                        logging.info(f"Changes for {name}:")
                        for change in changes:
                            logging.info(f"  {change}")
                    if upload_to_ftp(ical_file) and mail and args.mail:
                        send_mail(mail, name, changes)
        
        print(f"Sync complete for {len(USERS) if USERS else 0} users")