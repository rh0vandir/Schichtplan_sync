#!/usr/bin/env python3

import pdfplumber
import io
import re
from typing import List, Tuple, Optional
from .calendar_generator import create_ical_file
from .shift_continuation import extend_shift_schedule

def extract_and_create_ical(pdf_content: bytes, name: str, shifts_config: dict, 
                          family: bool = False, extend_schedule: bool = True, 
                          extension_days: int = 365) -> Optional[str]:
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
                                    
                                    # Get the corresponding shift
                                    shift = ''
                                    if col_idx < len(next_row):
                                        shift = next_row[col_idx].strip()
                                    
                                    # Always add the date, treat empty shifts as free days
                                    dates.append(date)
                                    if shift and shift.strip():
                                        shifts.append(shift.strip())
                                    else:
                                        shifts.append('F')  # Empty shift becomes free day
        
        # Final cleanup: ensure all shifts are valid (should be rare now)
        cleaned_dates = []
        cleaned_shifts = []
        invalid_shift_count = 0
        for date, shift in zip(dates, shifts):
            if shift and shift.strip() and shift != 'F':
                # Valid shift found
                cleaned_dates.append(date)
                cleaned_shifts.append(shift.strip())
            elif shift == 'F':
                # Free day - keep as is
                cleaned_dates.append(date)
                cleaned_shifts.append('F')
            else:
                # Fallback: treat as free day
                cleaned_dates.append(date)
                cleaned_shifts.append('F')
                invalid_shift_count += 1
        
        if invalid_shift_count > 0:
            print(f"Converted {invalid_shift_count} invalid shifts to free days")
        
        dates, shifts = cleaned_dates, cleaned_shifts
        
        print(f"Extracted {len(dates)} valid date/shift pairs from PDF")
        
        # Create year mapping for the extracted dates
        year_mapping = {}
        if dates:
            from .year_tracker import YearTracker
            year_tracker = YearTracker()
            year_mapping = year_tracker.map_dates_to_years(dates)
            
            # Show summary instead of full mapping
            years_covered = sorted(set(year_mapping.values()))
            date_range = f"{dates[0]} to {dates[-1]}"
            print(f"PDF dates: {date_range} → Years: {years_covered}")
        
        # Extend schedule if requested
        if extend_schedule:
            # Get PDF title for year extraction
            pdf_title = ""
            try:
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    pdf_title = pdf.metadata.get('Title', '')
                if not pdf_title:
                    # Try to extract title from first page text
                    first_page_text = pdf.pages[0].extract_text()
                    if first_page_text:
                        # Look for "Schichtplan YYYY" pattern
                        title_match = re.search(r'Schichtplan\s+\d{4}', first_page_text)
                        if title_match:
                            pdf_title = title_match.group(0)
            except Exception as e:
                print(f"Warning: Could not extract PDF title: {e}")
            
            extended_dates, extended_shifts, extended_year_mapping = extend_shift_schedule(dates, shifts, extension_days, pdf_title)
            
            # Update year mapping for extended dates
            if extended_dates:
                year_mapping.update(extended_year_mapping)
                
                # Show summary of extended dates
                extended_years = sorted(set(extended_year_mapping.values()))
                extended_range = f"{extended_dates[0]} to {extended_dates[-1]}"
                print(f"Extended dates: {extended_range} → Years: {extended_years}")
            
            dates, shifts = extended_dates, extended_shifts
        
        # Create iCal file directly from extracted data with year mapping
        return create_ical_file(dates, shifts, name, shifts_config, family, year_mapping)
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
