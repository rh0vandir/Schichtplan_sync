# Calendars Directory

This directory will contain all the generated ICS (iCalendar) files for the Schichtplan Sync project.

## Contents

### Current Calendar Files
- `schichtplan_[Name].ics` - Current calendar files for each user
- `old_schichtplan_[Name].ics` - Previous versions for change detection

### File Naming Convention
- Current files: `schichtplan_[Name].ics`
- Old files: `old_schichtplan_[Name].ics`
- Names are sanitized (spaces replaced with underscores)

### Purpose
- **Current files**: Active calendar files that are uploaded to FTP servers
- **Old files**: Used for change detection to determine if email notifications should be sent

### Management
- Files are automatically created by the main script
- Old files are automatically updated after successful FTP uploads
- Files are automatically cleaned up and recreated on each run

### Integration
- Used by `schichtplan_sync.py` for calendar generation and comparison
- Used by FTP upload functionality
- Used by email notification system for change detection

## Security
- Files contain personal schedule information
- Should be protected with appropriate file permissions
- Considered temporary working files (not long-term storage) 
- excluded from the repo as they hold sensitive info