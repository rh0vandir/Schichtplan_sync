#!/usr/bin/env python3

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional, Any
import re
from .config_loader import get_default_continuation_days

class YearTracker:
    """
    Utility class to track and manage years for shift schedules,
    especially handling year transitions between December and January
    """
    
    def __init__(self, base_year: Optional[int] = None):
        """
        Initialize the year tracker
        
        Args:
            base_year: Base year to start with (defaults to current year)
        """
        self.base_year = base_year or datetime.now().year
        self.year_mapping: Dict[str, int] = {}
        self._initialize_year_mapping()
    
    def _initialize_year_mapping(self):
        """Initialize the year mapping for the current schedule period"""
        current_date = datetime.now()
        current_year = current_date.year
        
        # If we're in December, we need to consider next year for January dates
        if current_date.month == 12:
            self.base_year = current_year
            self.next_year = current_year + 1
        else:
            self.base_year = current_year
            self.next_year = current_year + 1
    
    def extract_year_from_pdf_title(self, pdf_title: str) -> Optional[int]:
        """
        Extract the year from PDF title (e.g., "Schichtplan 2025")
        
        Args:
            pdf_title: Title of the PDF
            
        Returns:
            Year found in title, or None if not found
        """
        year_match = re.search(r'(\d{4})', pdf_title)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def determine_year_for_date(self, date_str: str, month: int, day: int, 
                              context_month: Optional[int] = None) -> int:
        """
        Determine the correct year for a given date
        
        Args:
            date_str: Date string in DD.MM format
            month: Month number (1-12)
            day: Day number (1-31)
            context_month: Month from context (e.g., if we know we're in December)
            
        Returns:
            Correct year for the date
        """
        # If we have a specific year mapping for this date, use it
        if date_str in self.year_mapping:
            return self.year_mapping[date_str]
        
        # Handle year transitions
        if month == 1 and context_month == 12:
            # We're going from December to January, so January should be next year
            return self.base_year + 1
        elif month == 12 and context_month == 1:
            # We're going from January to December, so December should be previous year
            return self.base_year - 1
        elif month == 12:
            # December dates in the current year
            return self.base_year
        elif month == 1:
            # January dates - check if we're extending into next year
            current_date = datetime.now()
            if current_date.month == 12:
                # We're in December, so January dates should be next year
                return self.base_year + 1
            else:
                # We're not in December, so January dates are current year
                return self.base_year
        else:
            # All other months use the base year
            return self.base_year
    
    def map_dates_to_years(self, dates: List[str], pdf_title: str = "") -> Dict[str, int]:
        """
        Map all dates to their correct years using PDF title as base year
        with Dec->Jan transition logic
        
        Args:
            dates: List of dates in DD.MM format
            pdf_title: PDF title to extract base year from
            
        Returns:
            Dictionary mapping dates to their correct years
        """
        if not dates:
            return {}
        
        year_mapping = {}
        
        # Extract base year from PDF title (e.g., "Schichtplan 2025" -> 2025)
        base_year = None
        if pdf_title:
            year_match = re.search(r'(\d{4})', pdf_title)
            if year_match:
                base_year = int(year_match.group(1))
        
        # Fallback to current year if no title year found
        if not base_year:
            base_year = datetime.now().year
        
        # Using PDF title year as base
        
        # Start with base year from title
        current_year = base_year
        previous_month = None
        transition_count = 0
        
        for date_str in dates:
            try:
                day, month = map(int, date_str.split('.'))
                
                # Detect December -> January transitions
                if previous_month == 12 and month == 1:
                    transition_count += 1
                    
                    if transition_count == 1:
                        # First transition: December (base-1) -> January (base)
                        # We were in December of previous year, now entering base year
                        current_year = base_year
                        print(f"Dec->Jan transition detected at {date_str}")
                    else:
                        # Subsequent transitions: December (base) -> January (base+1) 
                        current_year += 1
                        print(f"Dec->Jan transition #{transition_count} at {date_str}")
                
                # Special handling for December dates at the start
                elif month == 12 and previous_month is None:
                    # First date is December - it should be from year before base year
                    current_year = base_year - 1
                    # December dates assigned to previous year
                
                year_mapping[date_str] = current_year
                previous_month = month
                
            except (ValueError, IndexError):
                print(f"Warning: Could not parse date '{date_str}'")
                continue
        
        # Report the results
        years_covered = sorted(set(year_mapping.values()))
        print(f"Year mapping: {len(dates)} dates across {len(years_covered)} years")
        # Transition count tracked
        
        # Show key dates for verification
        key_dates = [(date, year) for date, year in year_mapping.items() 
                    if date in ["30.12", "31.12", "01.01", "25.01"]]
        if key_dates:
            # Key dates processed
            for date, year in sorted(key_dates, key=lambda x: (x[1], x[0])):
                pass  # Date assignment logged
        
        self.year_mapping = year_mapping
        return year_mapping
    def get_date_with_year(self, date_str: str) -> str:
        """
        Get a date string with the correct year
        
        Args:
            date_str: Date in DD.MM format
            
        Returns:
            Date in DD.MM.YYYY format
        """
        if date_str in self.year_mapping:
            year = self.year_mapping[date_str]
            return f"{date_str}.{year}"
        
        # Fallback: try to determine year
        try:
            day, month = map(int, date_str.split('.'))
            year = self.determine_year_for_date(date_str, month, day)
            return f"{date_str}.{year}"
        except (ValueError, IndexError):
            return date_str
    
    def extend_years_for_future_dates(self, dates: List[str], 
                                    extension_days: int = get_default_continuation_days()) -> Dict[str, int]:
        """
        Extend year mapping for future dates when extending the schedule
        
        Args:
            dates: List of dates in DD.MM format
            extension_days: Number of days to extend by (uses config default)
            
        Returns:
            Extended year mapping
        """
        
        if not dates:
            return {}
        
        # Get the last date and its year
        last_date_str = dates[-1]
        if last_date_str not in self.year_mapping:
            # If we don't have a year for the last date, we can't extend
            return self.year_mapping
        
        last_year = self.year_mapping[last_date_str]
        last_date = datetime.strptime(f"{last_date_str}.{last_year}", "%d.%m.%Y")
        
        # Extend year mapping for future dates
        current_date = last_date + timedelta(days=1)
        
        for i in range(extension_days):
            date_str = current_date.strftime("%d.%m")
            year = current_date.year
            
            if date_str not in self.year_mapping:
                self.year_mapping[date_str] = year
            
            current_date += timedelta(days=1)
        
        return self.year_mapping
    
    def get_year_transition_info(self) -> Dict[str, any]:
        """
        Get information about year transitions in the schedule
        
        Returns:
            Dictionary with year transition information
        """
        if not self.year_mapping:
            return {"message": "No year mapping available"}
        
        years = set(self.year_mapping.values())
        min_year = min(years)
        max_year = max(years)
        
        # Check for December to January transitions
        december_dates = [date for date, year in self.year_mapping.items() 
                         if date.endswith('.12')]
        january_dates = [date for date, year in self.year_mapping.items() 
                        if date.endswith('.01')]
        
        return {
            "year_range": (min_year, max_year),
            "years_covered": sorted(years),
            "december_dates": december_dates,
            "january_dates": january_dates,
            "has_year_transition": max_year > min_year,
            "base_year": self.base_year,
            "next_year": self.next_year
        }
    
    def validate_year_consistency(self, dates: List[str]) -> List[str]:
        """
        Validate that year assignments are consistent and logical
        
        Args:
            dates: List of dates to validate
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        if not dates:
            return warnings
        
        # Check for logical month progression
        previous_date = None
        previous_year = None
        
        for date_str in dates:
            if date_str not in self.year_mapping:
                warnings.append(f"Date {date_str} has no year assigned")
                continue
            
            try:
                day, month = map(int, date_str.split('.'))
                year = self.year_mapping[date_str]
                
                if previous_date and previous_year:
                    # Check for logical year progression
                    if month == 1 and previous_date.month == 12:
                        if year != previous_year + 1:
                            warnings.append(f"Year transition from {previous_date.strftime('%d.%m.%Y')} to {date_str}.{year} may be incorrect")
                    elif month == 12 and previous_date.month == 1:
                        if year != previous_year - 1:
                            warnings.append(f"Year transition from {previous_date.strftime('%d.%m.%Y')} to {date_str}.{year} may be incorrect")
                
                previous_date = datetime(year, month, day)
                previous_year = year
                
            except (ValueError, IndexError):
                warnings.append(f"Could not parse date {date_str}")
                continue
        
        return warnings
