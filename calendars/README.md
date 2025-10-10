# Calendars Directory

This directory contains all the generated ICS (iCalendar) files for the Schichtplan Sync project.

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

### Features
- **Schedule Extension**: Calendars can be automatically extended using configurable patterns
- **Year Boundary Handling**: Proper handling of schedules that cross year boundaries
- **Change Detection**: Automatic comparison with previous versions for notifications
- **Multi-User Support**: Separate calendar files for each configured user

### Management
- Files are automatically created by the main script (`schichtplan_sync.py`)
- Old files are automatically updated after successful FTP uploads
- Files are automatically cleaned up and recreated on each run
- Schedule extension can be controlled via command line options

### Integration
- Used by `schichtplan_sync.py` for calendar generation and comparison
- Used by FTP upload functionality (`utils/ftp_uploader.py`)
- Used by email notification system for change detection
- Used by schedule extension system (`utils/shift_continuation.py`)

### Configuration
- Schedule extension patterns are defined in `config.json`
- Default continuation length is configurable via `default_continuation_days` in the config
- Custom extension periods can be specified via `--extend-days` option
- Extension can be disabled with `--no-extend` flag

## Security
- Files contain personal schedule information
- Should be protected with appropriate file permissions
- Considered temporary working files (not long-term storage)
- Excluded from the repo as they hold sensitive info
- Files are automatically cleaned up after processing
- To prevent bots from scraping Calendars, restrict access to the Domain with a precise .htaccess

## File Format
- Standard iCalendar (.ics) format
- Compatible with Google Calendar, Apple Calendar, Outlook, and other calendar applications
- Events include proper start/end times, descriptions, and shift information
- Timezone-aware scheduling
- Support for recurring patterns and extended schedules
