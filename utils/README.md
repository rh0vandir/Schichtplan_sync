# Utils Package for Schichtplan Sync

This document describes the utility modules that provide modular functionality for the Schichtplan Sync project.

## Overview

The `utils/` package contains specialized modules that handle different aspects of the schedule synchronization process:

- **Mail Utilities**: Email notification system with encrypted credentials
- **PDF Processing**: PDF download, parsing, and text extraction
- **Calendar Generation**: iCal file creation and management
- **FTP Operations**: File upload and comparison functionality
- **Credential Management**: Secure storage and retrieval of login credentials
- **Configuration Loading**: JSON configuration parsing and validation
- **Schedule Extension**: Automatic schedule continuation using patterns
- **Year Tracking**: Proper handling of year boundary transitions

## Module Overview

### `mail_utils.py`
Provides a standalone email notification system that can be used by:
- The main `schichtplan_sync.py` script for schedule change notifications
- The `cron_schichtplan.sh` script for system notifications
- Any other script that needs to send email notifications

**Features:**
- Encrypted SMTP credentials using Fernet encryption
- Flexible email types (schedule updates and custom notifications)
- Command-line interface and Python module usage
- Comprehensive error handling with detailed logging

### `pdf_processor.py`
Handles PDF download, processing, and text extraction:
- Downloads PDFs from configured URLs with authentication
- Extracts text content using OCR (Tesseract)
- Processes extracted text to identify shift patterns
- Integrates with calendar generation system

### `calendar_generator.py`
Creates and manages iCalendar files:
- Generates standard iCal format files
- Handles shift definitions and time calculations
- Supports schedule extension and pattern repetition
- Manages event creation and calendar structure

### `ftp_uploader.py`
Manages FTP server operations:
- Uploads generated iCal files to configured FTP servers
- Compares current and previous files for change detection
- Handles FTP authentication and error management
- Supports secure FTP connections

### `credentials_manager.py`
Securely manages login credentials:
- Encrypts and stores credentials using Fernet
- Manages both web login and FTP credentials
- Provides secure credential retrieval
- Handles credential file permissions and security

### `config_loader.py`
Loads and validates configuration:
- Parses JSON configuration files
- Validates shift definitions and user configurations
- Provides default values and error handling
- Manages configuration file loading and validation

### `shift_continuation.py`
Handles schedule extension functionality:
- Extends schedules using configurable patterns
- Manages pattern repetition and continuation
- Handles year boundary transitions
- Supports custom extension periods

### `year_tracker.py`
Manages year boundary transitions:
- Handles schedules that cross year boundaries
- Manages date calculations and transitions
- Ensures proper calendar continuity
- Supports leap year handling

## Usage

### As Python Modules

```python
from utils.mail_utils import send_mail, send_notification_email
from utils.pdf_processor import extract_and_create_ical
from utils.ftp_uploader import upload_to_ftp, compare_ics_files
from utils.config_loader import load_config
from utils.credentials_manager import get_credentials

# Load configuration
SHIFTS, USERS = load_config()

# Process PDF and create calendar
ical_file = extract_and_create_ical(pdf_content, name, SHIFTS, family_mode, extend, extend_days)

# Upload to FTP and check for changes
if upload_to_ftp(ical_file):
    changes, has_changes = compare_ics_files(ical_file, old_file)
    if has_changes and changes:
        send_mail(user_email, name, changes)
```

### From Command Line

```bash
# Send email notification
python3 utils/mail_utils.py --to user@example.com --name "John Doe" \
    --changes "New shift added: F 08-16 on 2024-12-25" \
    --subject "Schedule Update"

# Test mail functionality
python3 utils/test_mail.py
```

## Configuration

### First-time Setup

When you first use modules that require credentials:

1. **Web Login Credentials**: Stored in `~/.schichtplan_credentials`
2. **FTP Credentials**: Stored in `~/.schichtplan_ftp_credentials`
3. **SMTP Credentials**: Stored in `~/.schichtplan_smtp_credentials`

All credential files are encrypted using Fernet encryption with keys stored in:
- `~/.schichtplan_key` (main encryption key)
- `~/.schichtplan_ftp_key` (FTP encryption key)
- `~/.schichtplan_smtp_key` (SMTP encryption key)

### Security

- All credentials are encrypted using Fernet (symmetric encryption)
- Files have restricted permissions (600)
- No credentials are stored in plain text
- Encryption keys are stored separately from encrypted data

## Integration

### Main Script (`schichtplan_sync.py`)

The main script imports and uses all utility modules:

```python
from utils.mail_utils import send_mail
from utils.pdf_processor import extract_and_create_ical
from utils.ftp_uploader import upload_to_ftp, compare_ics_files
from utils.config_loader import load_config
from utils.credentials_manager import get_credentials
```

### Cron Script (`cron_schichtplan.sh`)

The cron script uses the Python mail utility for notifications:

```bash
"$SCRIPT_DIR/venv_schichtplan_sync/bin/python" "$SCRIPT_DIR/utils/mail_utils.py" \
    --to "$recipient" \
    --subject "$subject" \
    --message "$message"
```

## Error Handling

All utility modules include comprehensive error handling:

- **Network errors**: Connection, timeout, and authentication issues
- **File errors**: Permission, path, and I/O problems
- **Configuration errors**: Missing or invalid configuration data
- **Credential errors**: Missing or invalid credentials
- **Processing errors**: PDF parsing and calendar generation issues

All errors are logged with descriptive messages to help with troubleshooting.

## Dependencies

The utility modules require the following Python packages:
- `cryptography` (for credential encryption)
- `requests` (for HTTP operations)
- `pdfplumber` (for PDF processing)
- `icalendar` (for calendar generation)
- `pytz` (for timezone handling)
- Standard library modules: `smtplib`, `ssl`, `email`, `os`, `argparse`, `json`

These are already included in the main project's virtual environment and requirements.txt.

## Testing

Use the `test_mail.py` script to test the mail utility functionality:

```bash
python3 utils/test_mail.py
```

Note: Tests will fail without valid SMTP credentials and email addresses.

## Module Dependencies

```
utils/
├── __init__.py              # Package initialization and exports
├── mail_utils.py            # Email functionality (standalone)
├── pdf_processor.py         # PDF processing (depends on config_loader)
├── calendar_generator.py    # Calendar generation (depends on config_loader)
├── ftp_uploader.py          # FTP operations (depends on credentials_manager)
├── credentials_manager.py   # Credential management (standalone)
├── config_loader.py         # Configuration loading (standalone)
├── shift_continuation.py    # Schedule extension (depends on config_loader)
├── year_tracker.py          # Year handling (standalone)
└── test_mail.py             # Mail utility testing
```

Each module is designed to be as independent as possible while providing clear interfaces for integration. 