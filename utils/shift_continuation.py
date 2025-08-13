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
    
    print(f"PDF schedule ends at rhythm position {rhythm_position} (shift: {last_shift})")
    print(f"Continuing rhythm from position {rhythm_position + 1}")
    
    # Extend the schedule
    extended_dates = dates.copy()
    extended_shifts = shifts.copy()
    
    current_date = last_date + timedelta(days=1)
    today = datetime.now()
    
    for i in range(days_to_add):
        # Get the shift from the pattern, continuing from where we left off
        pattern_index = (rhythm_position + 1 + i) % pattern_length
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
    
    print(f"Extended schedule from {len(dates)} to {len(extended_dates)} days")
    print(f"Pattern continues from position {rhythm_position + 1} and repeats {(days_to_add // pattern_length) + 1} times")
    
    return extended_dates, extended_shifts, year_mapping

def find_rhythm_position(shifts: List[str], pattern: List[str]) -> Optional[int]:
    """
    Find where in the 28-day rhythm the PDF schedule ends
    
    Args:
        shifts: List of shifts from the PDF
        pattern: The 28-day default pattern
    
    Returns:
        Position in the pattern (0-27) where the PDF ends, or None if can't determine
    """
    if len(shifts) < len(pattern):
        # If PDF is shorter than pattern, we can't reliably determine position
        # In this case, we'll try to find the best match
        return find_best_pattern_match(shifts, pattern)
    
    # If PDF is longer than pattern, find the last complete pattern cycle
    pattern_length = len(pattern)
    last_complete_cycle = len(shifts) // pattern_length
    
    if last_complete_cycle > 0:
        # Check if the last complete cycle matches the pattern
        start_idx = (last_complete_cycle - 1) * pattern_length
        end_idx = last_complete_cycle * pattern_length
        
        if shifts[start_idx:end_idx] == pattern:
            # We found a complete cycle, so we're at position 0
            return 0
        
        # Check if we're in the middle of a pattern
        remaining_shifts = shifts[start_idx:]
        return find_best_pattern_match(remaining_shifts, pattern)
    
    # PDF is shorter than pattern, find best match
    return find_best_pattern_match(shifts, pattern)

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
    
    print(f"Best pattern match: starts at position {best_match}, ends at position {end_position}")
    print(f"Match score: {best_score}/{len(shifts)} shifts match the pattern")
    
    # Additional validation: check if the transition makes sense
    if len(shifts) > 0:
        last_shift = shifts[-1]
        expected_next = pattern[end_position]
        print(f"Last shift in PDF: {last_shift}")
        print(f"Expected next shift in rhythm: {expected_next}")
        
        # If we have a good match, verify the transition point
        if best_score >= len(shifts) * 0.8:  # 80% match threshold
            print(f"✓ Good rhythm match confirmed, continuing from position {end_position}")
        else:
            print(f"⚠ Lower match score, rhythm continuation may not be perfect")
    
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
