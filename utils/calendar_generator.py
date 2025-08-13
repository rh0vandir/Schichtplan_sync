#!/usr/bin/env python3

import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event, Component
import pytz
import os
from typing import List, Dict
from .year_tracker import YearTracker

def get_shift_info(shift: str, shifts_config: Dict) -> Dict[str, str]:
    """Get the time and name for a given shift code"""
    # First try to parse the shift code for custom time ranges
    shift_letter, custom_time = parse_shift_time(shift)
    
    # Get base shift info
    base_info = shifts_config.get(shift_letter, {'start': '', 'end': '', 'name': ''})
    
    # If we found a custom time range, use it instead of the default
    if custom_time:
        start_time, end_time = custom_time.split('-')
        return {
            'start': start_time,
            'end': end_time,
            'name': base_info['name']
        }
    
    return base_info

def parse_shift_time(shift_code: str) -> tuple:
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

def create_ical_file(dates: List[str], shifts: List[str], name: str, 
                    shifts_config: Dict, family: bool = False, 
                    year_mapping: Dict[str, int] = None) -> str:
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
    
    for idx, (date, shift) in enumerate(zip(dates, shifts)):
        if shift and shift != 'K':
            shift_info = get_shift_info(shift, shifts_config)
            if shift_info['start'] and shift_info['end']:
                
                # Parse date and times - handle both DD.MM and DD.MM.YYYY formats
                try:
                    if len(date.split('.')) == 3:
                        # DD.MM.YYYY format
                        event_date = datetime.strptime(date, '%d.%m.%Y')
                    else:
                        # DD.MM format - use provided year mapping or fallback
                        if year_mapping and date in year_mapping:
                            year = year_mapping[date]
                            event_date = datetime.strptime(f"{date}.{year}", '%d.%m.%Y')
                        else:
                            # Fallback to current year if no year mapping available
                            event_date = datetime.strptime(date, '%d.%m')
                            event_date = event_date.replace(year=datetime.now().year)
                except ValueError:
                    print(f"Warning: Could not parse date '{date}', skipping event")
                    continue
                
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
    calendars_dir = "calendars"
    os.makedirs(calendars_dir, exist_ok=True)
    ical_file = os.path.join(calendars_dir, f"schichtplan_{name.replace(' ', '_')}.ics")
    ical_content = cal.to_ical().decode('utf-8').replace('\r\n', '\n').replace('\n', '\r\n')
    with open(ical_file, 'wb') as f:
        f.write(ical_content.encode('utf-8'))
    
    print(f"iCal file created: {ical_file}")
    return ical_file
