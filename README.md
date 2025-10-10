# Schichtplan Sync

A Python-based tool for automatically downloading, parsing, and syncing work schedules from PDF files to calendar applications via iCal format.

## Features

- **PDF Processing**: Downloads and parses PDF schedules using OCR (Tesseract)
- **Calendar Integration**: Generates iCal files compatible with Google Calendar, Apple Calendar, Outlook, etc.
- **Email Notifications**: Sends notifications when schedules change
- **FTP Upload**: Automatically uploads generated iCal files to FTP server
- **Encrypted Credentials**: Securely stores login credentials using Fernet encryption
- **Flexible Configuration**: Supports custom shift definitions and user configurations
- **Schedule Extension**: Automatically extends schedules using configurable patterns
- **Change Detection**: Compares PDF content to avoid unnecessary processing
- **Modular Architecture**: Organized into utility modules for maintainability

## Requirements

- Python 3.6+
- Tesseract OCR
- Internet connection for PDF download
- FTP server (optional)

## Installation

1. **Clone the repository:**
   ```bash
   git clone git@code.rhovandir.net:all-inkl/schichtplan_sync.git
   cd schichtplan_sync
   ```

2. **Run the setup script:**
   ```bash
   ./setup_schichtplan_sync.sh
   ```

The setup script will:
- Check for required dependencies (Python 3, pip3, Tesseract)
- Create a virtual environment
- Install required Python packages from requirements.txt
- Create a default configuration file

## Configuration

Edit `config.json` to configure:

### Shift Definitions
```json
{
    "shifts": {
        "A": {"start": "07:00", "end": "14:00", "name": "Frühschicht"},
        "B": {"start": "14:00", "end": "24:00", "name": "Spätschicht"},
        "N": {"start": "00:00", "end": "07:00", "name": "Nachtschicht"},
        "WF": {"start": "00:00", "end": "12:00", "name": "Wochenende Frühschicht"},
        "WS": {"start": "12:00", "end": "24:00", "name": "Wochenende Spätschicht"},
        "K": {"start": "0:00", "end": "24:00", "name": "Krank"},
        "U": {"start": "0:00", "end": "24:00", "name": "Urlaub"},
        "F": {"start": "0:00", "end": "24:00", "name": "Frei"},

    }
}
```

### Default Pattern for Schedule Extension
```json
{
    "default_pattern": [
        "N", "N", "N", "N", "N", "WF", "WF",
        "A", "A", "A", "A", "A", "F", "F",
        "B", "B", "B", "B", "B", "WS", "WS",
        "F", "F", "F", "F", "F", "F", "F"
    ]
}
```

### Default Continuation Length
```json
{
    "default_continuation_days": 365
}
```
This setting controls how many days the schedule is extended beyond the PDF data using the default pattern. The value represents the total number of days for continuation events.

### User Configurations
```json
{
    "users": {
        "user1": {
            "name": "John Doe",
            "family": false,
            "mail": "john@example.com"
        }
    }
}
```

## Usage

### Basic Usage
```bash
# Activate virtual environment
source venv_schichtplan_sync/bin/activate

# Run the script
python3 schichtplan_sync.py
```

### Advanced Options
```bash
# Process schedule for specific user
python3 schichtplan_sync.py --name "John Doe" --family

# Use local PDF file for testing
python3 schichtplan_sync.py --local

# Skip FTP upload
python3 schichtplan_sync.py --no-ftp

# Disable email notifications
python3 schichtplan_sync.py --no-mail

# Force processing even if PDF hasn't changed
python3 schichtplan_sync.py --force

# Customize schedule extension
python3 schichtplan_sync.py --extend-days 180

# Disable schedule extension
python3 schichtplan_sync.py --no-extend
```

## Command Line Options

- `--name`: Override configuration and process schedule for specific name
- `--family`: Include first name in event summary (only with --name)
- `--local`: Use a local PDF file for testing
- `--no-ftp`: Skip FTP upload
- `--mail`: Enable email notifications (default)
- `--no-mail`: Disable email notifications
- `--force`: Force processing even if PDF has not changed
- `--extend`: Enable schedule extension using default pattern (default)
- `--no-extend`: Disable schedule extension
- `--extend-days`: Number of days to extend schedule (if not specified, uses config default_continuation_days value)

## Calendar Integration

The script generates iCal files that can be imported into:

- **Google Calendar**: Click the '+' next to 'Other calendars' > 'Import'
- **Apple Calendar**: File > Import
- **Outlook**: File > Open & Export > Import/Export > Import an iCalendar file

## Automation

### Cron Job Setup
The repository includes `cron_schichtplan.sh` for automated execution:

```bash
# Add to crontab (run every 4 hours)
0 */4 * * * /path/to/schichtplan_sync/cron_schichtplan.sh
```

The cron script will:
- Sync the latest code from git
- Run the schedule processing
- Send email notifications for any errors

### Mail Utility
The `utils/mail_utils.py` module provides standalone email functionality:

```bash
# Send custom notification
python3 utils/mail_utils.py --to user@example.com --subject "Alert" --message "Message"
```

## Project Structure

```
schichtplan_sync/
├── schichtplan_sync.py          # Main script
├── setup_schichtplan_sync.sh    # Setup script
├── cron_schichtplan.sh          # Cron automation script
├── config.json                   # Configuration file
├── requirements.txt              # Python dependencies
├── calendars/                    # Generated iCal files
├── utils/                        # Utility modules
│   ├── mail_utils.py            # Email functionality
│   ├── pdf_processor.py         # PDF processing
│   ├── calendar_generator.py    # iCal generation
│   ├── ftp_uploader.py          # FTP upload
│   ├── credentials_manager.py   # Credential management
│   ├── config_loader.py         # Configuration loading
│   ├── shift_continuation.py    # Schedule extension
│   └── year_tracker.py          # Year boundary handling
└── venv_schichtplan_sync/       # Virtual environment
```

## Security

- Credentials are encrypted using Fernet encryption
- Credential files are stored with secure permissions (600)
- No sensitive data is logged
- PDF content is hashed for change detection

### Securing FTP Hosted iCal Files

When hosting iCal files on a web server via FTP, it's recommended to add security restrictions using `.htaccess`:

1. **Copy the sample .htaccess file to your FTP server:**
   ```bash
   cp .htaccess.sample /path/to/your/ftp/directory/.htaccess
   ```

2. **Customize for your environment:**
   - Add your IP address(es) to the allowed list
   - Add calendar application user agents (Google Calendar, Apple Calendar, etc.)
   - Optionally add password protection
   - Test access from your calendar applications

3. **The sample .htaccess includes (production-tested configuration):**
   - **Block all non-.ics files** with 403 Forbidden
   - **Allow Google Calendar** user agent
   - **IP-based access control** for specific addresses
   - **Default deny-all policy** with explicit allow list
   - Optional HTTP Basic Authentication
   - MIME type configuration
   - Protection for hidden files

4. **Common User-Agent strings for calendar apps:**
   - Google Calendar: `.*Google-Calendar*`
   - Apple Calendar: `.*CalendarAgent.*`
   - Outlook: `.*Microsoft.*`
   - Mozilla Lightning: `.*Lightning.*`

**Note:** The `.htaccess.sample` file is based on real-world production usage and provides a secure starting point. Adjust based on your server configuration and security requirements.

## License

MIT License - Copyright (c) 2025 Andras Gerendas

## Version

Current Version: 2.12.0 