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
                    year_mapping: Dict[str, int] = None,
                    pdf_dates: List[str] = None) -> str:
    """
    Create an iCal file from the shift data
    
    Args:
        dates: List of dates in DD.MM or DD.MM.YYYY format
        shifts: List of shift codes corresponding to dates
        name: Name for the calendar
        shifts_config: Configuration dictionary for shift definitions
        family: Whether to include first name in event summary
        year_mapping: Dictionary mapping dates to years
        pdf_dates: List of dates that originated from the PDF (for X-FOO:bar comments)
    """
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
    
    # Count events for reporting
    skipped_events = 0  # Free days (F)
    created_events = 0  # Work shifts and PT (U)
    
    # Separate PDF dates and continuation dates
    pdf_events = []
    continuation_events = []
    
    for idx, (date, shift) in enumerate(zip(dates, shifts)):
        # Skip creating events for free days (F)
        # This keeps the calendar clean by only showing actual work shifts and holidays
        if shift and shift != 'F':
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
                
                # Handle different shift types
                if shift == 'U':
                    # PTO - use the shift name from config
                    summary = f"{prefix}{shift_info['name']}"
                else:
                    # Work shift - show time range
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
                
                # Categorize events by source
                if pdf_dates and date in pdf_dates:
                    pdf_events.append(event)
                else:
                    continuation_events.append(event)
                
                created_events += 1
        else:
            if shift == 'F':
                skipped_events += 1
    
    # Save calendar to file with proper line endings and section structure
    calendars_dir = "calendars"
    os.makedirs(calendars_dir, exist_ok=True)
    ical_file = os.path.join(calendars_dir, f"schichtplan_{name.replace(' ', '_')}.ics")
    
    # Manually construct the iCal file to place X-FOO:bar properties between events
    with open(ical_file, 'w', encoding='utf-8') as f:
        # Write calendar header
        f.write("BEGIN:VCALENDAR\r\n")
        f.write("VERSION:2.0\r\n")
        f.write("PRODID:-//Schichtplan Sync//\r\n")
        f.write("CALSCALE:GREGORIAN\r\n")
        f.write("METHOD:PUBLISH\r\n")
        f.write(f"X-WR-CALNAME:Schichtplan {name}\r\n")
        f.write("X-WR-TIMEZONE:Europe/Berlin\r\n")
        f.write(f"X-WR-CALDESC:Schichtplan für {name}\r\n")
        f.write("REFRESH-INTERVAL:PT15M\r\n")
        f.write("X-PUBLISHED-TTL:PT15M\r\n")
        f.write("CHARSET:UTF-8\r\n")
        
        # Write VTIMEZONE component
        f.write("BEGIN:VTIMEZONE\r\n")
        f.write("TZID:Europe/Berlin\r\n")
        f.write("BEGIN:STANDARD\r\n")
        f.write("DTSTART:19701025T030000\r\n")
        f.write("RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10\r\n")
        f.write("TZOFFSETFROM:+0200\r\n")
        f.write("TZOFFSETTO:+0100\r\n")
        f.write("TZNAME:CET\r\n")
        f.write("END:STANDARD\r\n")
        f.write("BEGIN:DAYLIGHT\r\n")
        f.write("DTSTART:19700329T020000\r\n")
        f.write("RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3\r\n")
        f.write("TZOFFSETFROM:+0100\r\n")
        f.write("TZOFFSETTO:+0200\r\n")
        f.write("TZNAME:CEST\r\n")
        f.write("END:DAYLIGHT\r\n")
        f.write("END:VTIMEZONE\r\n")
        
        # Add PDF section with events
        if pdf_events:
            # Extract year from first PDF date for the comment
            pdf_year = None
            if pdf_dates and len(pdf_dates[0].split('.')) == 3:
                pdf_year = pdf_dates[0].split('.')[-1]
            elif year_mapping and pdf_dates[0] in year_mapping:
                pdf_year = str(year_mapping[pdf_dates[0]])
            else:
                pdf_year = str(datetime.now().year)
            
            # Add PDF section start marker
            f.write(f"X-SHIFT-PDF-{pdf_year}:START\r\n")
            
            # Add all PDF events
            for event in pdf_events:
                f.write("BEGIN:VEVENT\r\n")
                f.write(f"UID:{event.get('uid')}\r\n")
                f.write(f"SUMMARY:{event.get('summary')}\r\n")
                f.write(f"DESCRIPTION:{event.get('description')}\r\n")
                f.write(f"X-SHIFT-SOURCE:PDF-{pdf_year}\r\n")
                f.write(f"DTSTART:{event.get('dtstart').to_ical().decode()}\r\n")
                f.write(f"DTEND:{event.get('dtend').to_ical().decode()}\r\n")
                f.write(f"DTSTAMP:{event.get('dtstamp').to_ical().decode()}\r\n")
                f.write(f"CREATED:{event.get('created').to_ical().decode()}\r\n")
                f.write(f"LAST-MODIFIED:{event.get('last-modified').to_ical().decode()}\r\n")
                f.write(f"SEQUENCE:{event.get('sequence')}\r\n")
                f.write(f"STATUS:{event.get('status')}\r\n")
                f.write(f"TRANSP:{event.get('transp')}\r\n")
                f.write(f"CLASS:{event.get('class')}\r\n")
                f.write(f"ALL-DAY:{event.get('all-day')}\r\n")
                f.write("END:VEVENT\r\n")
            
            # Add PDF section end marker
            f.write(f"X-SHIFT-PDF-{pdf_year}:END\r\n")
        
        # Add continuation section with events
        if continuation_events:
            # Calculate continuation days
            continuation_days = len(dates) - len(pdf_dates) if pdf_dates else len(dates)
            
            # Add continuation section start marker
            f.write(f"X-CONTINUATION-{continuation_days}:START\r\n")
            
            # Add all continuation events
            for event in continuation_events:
                f.write("BEGIN:VEVENT\r\n")
                f.write(f"UID:{event.get('uid')}\r\n")
                f.write(f"SUMMARY:{event.get('summary')}\r\n")
                f.write(f"DESCRIPTION:{event.get('description')}\r\n")
                f.write(f"X-SHIFT-SOURCE:CONTINUATION\r\n")
                f.write(f"DTSTART:{event.get('dtstart').to_ical().decode()}\r\n")
                f.write(f"DTEND:{event.get('dtend').to_ical().decode()}\r\n")
                f.write(f"DTSTAMP:{event.get('dtstamp').to_ical().decode()}\r\n")
                f.write(f"CREATED:{event.get('created').to_ical().decode()}\r\n")
                f.write(f"LAST-MODIFIED:{event.get('last-modified').to_ical().decode()}\r\n")
                f.write(f"SEQUENCE:{event.get('sequence')}\r\n")
                f.write(f"STATUS:{event.get('status')}\r\n")
                f.write(f"TRANSP:{event.get('transp')}\r\n")
                f.write(f"CLASS:{event.get('class')}\r\n")
                f.write(f"ALL-DAY:{event.get('all-day')}\r\n")
                f.write("END:VEVENT\r\n")
            
            # Add continuation section end marker
            f.write(f"X-CONTINUATION-{continuation_days}:END\r\n")
        
        # Write calendar footer
        f.write("END:VCALENDAR\r\n")
    
    # Report on what was created and what was skipped
    if skipped_events > 0:
        print(f"Calendar created: {created_events} work shifts and PT, skipped {skipped_events} free days")
    else:
        print(f"Calendar created: {created_events} work shifts and PT")
    
    print(f"iCal file created: {ical_file}")
    return ical_file
