#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from .config_loader import get_default_pattern
from .year_tracker import YearTracker

def extend_shift_schedule(dates: List[str], shifts: List[str], 
                         extension_days: int = 365, pdf_title: str = "") -> Tuple[List[str], List[str], Dict[str, int]]:
    """
    Extend the shift schedule using the default pattern, continuing from where the PDF ends
    
    Args:
        dates: List of dates in DD.MM format
        shifts: List of shift codes corresponding to dates
        extension_days: Number of days to extend the schedule by (default: 365 for a year)
        pdf_title: Title of the PDF for year extraction
    
    Returns:
        Tuple of (extended_dates, extended_shifts, year_mapping)
    """
    if not dates or not shifts:
        return dates, shifts
    
    # Get the default pattern from configuration
    default_pattern = get_default_pattern()
    if not default_pattern:
        print("Warning: No default pattern found in configuration, cannot extend schedule")
        return dates, shifts
    
    # Initialize year tracker
    year_tracker = YearTracker()
    
    # Note: We don't rely on PDF title year as it may not indicate the start year
    # For example, "Schichtplan 2026" might start in December 2025
    if pdf_title:
        pdf_year = year_tracker.extract_year_from_pdf_title(pdf_title)
        if pdf_year:
            print(f"PDF title shows: {pdf_title} (year: {pdf_year})")
            print("Note: PDF title year may not indicate the start year of the schedule")
    
    # Map existing dates to years based on chronological sequence and current context
    year_mapping = year_tracker.map_dates_to_years(dates)
    
    # Show summary instead of full mapping
    years_covered = sorted(set(year_mapping.values()))
    date_range = f"{dates[0]} to {dates[-1]}"
    print(f"Existing dates: {date_range} → Years: {years_covered}")
    
    # Validate year consistency
    warnings = year_tracker.validate_year_consistency(dates)
    if warnings:
        print("Year consistency warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Find the last date in the current schedule
    last_date_str = dates[-1]
    try:
        # Use the year from our mapping
        if last_date_str in year_mapping:
            last_year = year_mapping[last_date_str]
            last_date = datetime.strptime(f"{last_date_str}.{last_year}", '%d.%m.%Y')
        else:
            # Fallback to current year
            last_date = datetime.strptime(last_date_str, '%d.%m')
            last_date = last_date.replace(year=datetime.now().year)
    except ValueError:
        print(f"Warning: Could not parse last date '{last_date_str}', cannot extend schedule")
        return dates, shifts
    
    # Always extend by the specified number of days
    days_to_add = extension_days
    print(f"Extending schedule by {days_to_add} days using default pattern")
    
    # Find where in the 28-day rhythm the PDF schedule ends
    last_shift = shifts[-1]
    pattern_length = len(default_pattern)
    
    # Find the position in the pattern where we should continue
    rhythm_position = find_rhythm_position(shifts, default_pattern)
    
    if rhythm_position is None:
        print("Warning: Could not determine rhythm position, starting from beginning of pattern")
        rhythm_position = 0
    
    # Check if we're near the end of the pattern and need to wrap around
    # If we're within 7 positions of the end, it's better to start from the beginning
    if rhythm_position >= pattern_length - 7:
        print(f"Note: PDF ends near pattern end (position {rhythm_position}), wrapping to beginning for clean week alignment")
        rhythm_position = -1  # This will make the next position 0
    
    print(f"Extending schedule: PDF ends at rhythm position {rhythm_position}, continuing from position {rhythm_position}")
    
    # Extend the schedule
    extended_dates = dates.copy()
    extended_shifts = shifts.copy()
    
    current_date = last_date + timedelta(days=1)
    today = datetime.now()
    
    for i in range(days_to_add):
        # Get the shift from the pattern, continuing from where we left off
        pattern_index = (rhythm_position + i) % pattern_length
        shift = default_pattern[pattern_index]
        
        # Format the date with proper year handling
        date_str = current_date.strftime('%d.%m.%Y')
        
        extended_dates.append(date_str)
        extended_shifts.append(shift)
        
        # Move to next day
        current_date += timedelta(days=1)
    
    # Update year mapping for extended dates
    extended_year_mapping = year_tracker.extend_years_for_future_dates(extended_dates, extension_days)
    
    # Get year transition information
    transition_info = year_tracker.get_year_transition_info()
    if transition_info.get('has_year_transition'):
        print(f"Year transition detected: {transition_info['year_range'][0]} → {transition_info['year_range'][1]}")
    else:
        print(f"All dates in year: {transition_info.get('year_range', [0])[0]}")
    
    # Validate the extended schedule follows the correct pattern
    validate_extended_schedule(extended_shifts, default_pattern, rhythm_position)
    
    print(f"Schedule extended: {len(dates)} → {len(extended_dates)} days")
    
    return extended_dates, extended_shifts, year_mapping

def validate_extended_schedule(extended_shifts: List[str], pattern: List[str], start_position: int):
    """
    Validate that the extended schedule correctly follows the 28-day pattern
    
    Args:
        extended_shifts: The complete extended schedule
        pattern: The 28-day default pattern
        start_position: Where in the pattern the extension started
    """
    pattern_length = len(pattern)
    
    # Get the expected first week pattern from the config
    expected_first_week = pattern[:7]
    
    # Get the actual first week of the extension
    actual_first_week = []
    for i in range(7):
        pos = (start_position + i) % pattern_length
        actual_first_week.append(pattern[pos])
    
    # Validate all shift types in the first week
    shift_validation = {}
    has_errors = False
    
    for shift_type in set(expected_first_week):  # Get unique shift types from expected first week
        expected_count = expected_first_week.count(shift_type)
        actual_count = actual_first_week.count(shift_type)
        if expected_count != actual_count:
            has_errors = True
        shift_validation[shift_type] = {
            'expected': expected_count,
            'actual': actual_count,
            'status': '✓' if expected_count == actual_count else '✗'
        }
    
    # Only show validation results if there are errors
    if has_errors:
        print(f"⚠ Extension validation - Pattern mismatch detected:")
        print(f"  Expected: {expected_first_week}")
        print(f"  Actual:   {actual_first_week}")
        print(f"  Starting from pattern position: {start_position}")
        
        for shift_type, counts in shift_validation.items():
            if counts['expected'] > 0 and counts['actual'] != counts['expected']:
                print(f"    ✗ {shift_type}: {counts['actual']}/{counts['expected']} (MISSING {counts['expected'] - counts['actual']})")
    
    # Check for errors in subsequent weeks
    weeks_to_check = min(4, (len(extended_shifts) - len(pattern)) // 7)  # Check up to 4 weeks
    week_errors = []
    
    for week in range(weeks_to_check):
        week_start = start_position + (week * 7)
        week_shifts = []
        for i in range(7):
            pos = (week_start + i) % pattern_length
            week_shifts.append(pattern[pos])
        
        # Get expected pattern for this week
        expected_week = pattern[week*7:(week+1)*7]
        
        # Count all shift types for this week
        week_validation = {}
        week_has_errors = False
        
        for shift_type in set(expected_week):
            expected_count = expected_week.count(shift_type)
            actual_count = week_shifts.count(shift_type)
            if expected_count != actual_count:
                week_has_errors = True
            week_validation[shift_type] = {
                'expected': expected_count,
                'actual': actual_count,
                'status': '✓' if expected_count == actual_count else '✗'
            }
        
        if week_has_errors:
            total_week_expected = sum(counts['expected'] for counts in week_validation.values())
            total_week_actual = sum(counts['actual'] for counts in week_validation.values())
            week_errors.append({
                'week': week + 1,
                'expected': total_week_expected,
                'actual': total_week_actual,
                'details': week_validation
            })
    
    # Only show week validation if there are errors
    if week_errors:
        print(f"⚠ Pattern continuation errors:")
        for week_error in week_errors:
            print(f"  Week {week_error['week']}: {week_error['actual']}/{week_error['expected']} shifts correct")
            for shift_type, counts in week_error['details'].items():
                if counts['expected'] > 0 and counts['actual'] != counts['expected']:
                    print(f"    {shift_type}: {counts['actual']}/{counts['expected']} (MISSING {counts['expected'] - counts['actual']})")
    
    # Only show success message if there were no errors
    if not has_errors and not week_errors:
        print(f"✓ Extension validation: Pattern correctly aligned")

def find_rhythm_position(shifts: List[str], pattern: List[str]) -> Optional[int]:
    """
    Find where in the 28-day rhythm the PDF schedule ends
    
    Args:
        shifts: List of shifts from the PDF
        pattern: The 28-day default pattern
    
    Returns:
        Position in the pattern (0-27) where the PDF ends, or None if can't determine
    """
    if not shifts or not pattern:
        return 0
    
    # Filter out any empty or invalid shifts
    valid_shifts = [shift for shift in shifts if shift and shift.strip()]
    if not valid_shifts:
        print("Warning: No valid shifts found in PDF data")
        return 0
    
    if len(valid_shifts) != len(shifts):
        print(f"Filtered out {len(shifts) - len(valid_shifts)} empty/invalid shifts")
        shifts = valid_shifts
    
    pattern_length = len(pattern)
    
    # If PDF is shorter than pattern, we need to find the best match
    if len(shifts) < pattern_length:
        return find_best_pattern_match(shifts, pattern)
    
    # If PDF is longer than pattern, find the last complete pattern cycle
    # and determine where we are in the current incomplete cycle
    complete_cycles = len(shifts) // pattern_length
    remaining_shifts = len(shifts) % pattern_length
    
    if remaining_shifts == 0:
        # We end exactly at the end of a complete cycle
        return 0
    
    # We have some remaining shifts that form a partial cycle
    # Find where this partial cycle starts in the pattern
    partial_cycle_start = find_partial_cycle_start(shifts[-remaining_shifts:], pattern)
    
    if partial_cycle_start is not None:
        # Calculate where we end in the pattern
        end_position = (partial_cycle_start + remaining_shifts) % pattern_length
        return end_position
    
    # Fallback to best pattern match for the remaining shifts
    return find_best_pattern_match(shifts[-remaining_shifts:], pattern)

def find_partial_cycle_start(partial_shifts: List[str], pattern: List[str]) -> Optional[int]:
    """
    Find where a partial cycle of shifts starts in the pattern
    
    Args:
        partial_shifts: List of shifts that form a partial cycle
        pattern: The complete pattern
    
    Returns:
        Position in the pattern where the partial cycle starts, or None if can't determine
    """
    if not partial_shifts or not pattern:
        return None
    
    pattern_length = len(pattern)
    partial_length = len(partial_shifts)
    
    # Try each possible starting position in the pattern
    for start_pos in range(pattern_length):
        # Check if the partial shifts match the pattern starting from this position
        matches = 0
        for i, shift in enumerate(partial_shifts):
            pattern_pos = (start_pos + i) % pattern_length
            if shift == pattern[pattern_pos]:
                matches += 1
        
        # If we have a good match (at least 80% of shifts match)
        if matches >= partial_length * 0.8:
            return start_pos
    
    return None

def find_best_pattern_match(shifts: List[str], pattern: List[str]) -> Optional[int]:
    """
    Find the best match between shifts and pattern to determine rhythm position
    
    Args:
        shifts: List of shifts from the PDF
        pattern: The 28-day default pattern
    
    Returns:
        Best matching position in the pattern
    """
    if not shifts or not pattern:
        return 0
    
    pattern_length = len(pattern)
    best_match = 0
    best_score = 0
    
    # Try each possible starting position in the pattern
    for start_pos in range(pattern_length):
        score = 0
        for i, shift in enumerate(shifts):
            pattern_pos = (start_pos + i) % pattern_length
            if shift == pattern[pattern_pos]:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = start_pos
    
    # Calculate where we end in the pattern
    end_position = (best_match + len(shifts)) % pattern_length
    
    # Additional validation: check if the transition makes sense
    if len(shifts) > 0:
        last_shift = shifts[-1]
        expected_next = pattern[end_position]
        
        # If we have a good match, verify the transition point
        if best_score >= len(shifts) * 0.8:  # 80% match threshold
            print(f"Pattern match: {best_score}/{len(shifts)} shifts match, continuing from position {end_position}")
        else:
            print(f"Warning: Low pattern match score ({best_score}/{len(shifts)}), rhythm continuation may not be perfect")
    
    return end_position

def get_shift_continuation_info() -> Dict[str, str]:
    """
    Get information about the shift continuation feature
    
    Returns:
        Dictionary with continuation information
    """
    default_pattern = get_default_pattern()
    if not default_pattern:
        return {
            "enabled": False,
            "pattern_length": 0,
            "message": "No default pattern configured"
        }
    
    return {
        "enabled": True,
        "pattern_length": len(default_pattern),
        "pattern": default_pattern,
        "message": f"Default pattern with {len(default_pattern)} shifts configured"
    }
