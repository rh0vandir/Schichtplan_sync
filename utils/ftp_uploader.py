#!/usr/bin/env python3

import os
from ftplib import FTP
from icalendar import Calendar
from typing import List, Tuple
from .credentials_manager import get_ftp_credentials

def compare_ics_files(new_file: str, old_file: str) -> Tuple[List[str], bool]:
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

def upload_to_ftp(ical_file: str) -> bool:
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
