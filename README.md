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
   git clone git@github.com:rh0vandir/Schichtplan_sync.git
   cd schichtplan_sync
   ```

2. **Run the setup script:**
   ```bash
   ./setup_schichtplan_sync.sh
   ```
3. **Set up Configuration in `config.json`**
4. **Execute the Script manually once to set up credentials**
   
The setup script will:
- Check for required dependencies (Python 3, pip3, Tesseract)
- Create a virtual environment
- Install required Python packages from requirements.txt
- Create a default configuration file

## Configuration

Edit `config.json` to configure the application. The configuration file is created automatically during setup with default values.

### Mandatory Configuration

These settings **must** be configured before the application can function properly:

#### `pdf_url` (string)
The URL from which the PDF schedule is downloaded. Update this to point to your organization's schedule PDF.

**Example:**
```json
"pdf_url": "https://example.com/path/to/schedule.pdf"
```

#### `users` (object)
Define one or more users whose schedules should be processed. Each user entry requires:

- **`name`** (string, required): Full name exactly as it appears in the PDF schedule. This is critical for accurate schedule extraction.
- **`family`** (boolean, required): Whether to include the first name in calendar event summaries. Set to `true` if multiple people with the same last name share calendars.
- **`mail`** (string, required): Email address for notifications. Use an empty string `""` to disable email notifications for this user.

**Example:**
```json
"users": {
    "user1": {
        "name": "John Doe",
        "family": false,
        "mail": "john@example.com"
    },
    "user2": {
        "name": "Jane Doe",
        "family": true,
        "mail": "jane@example.com"
    }
}
```

### Optional Configuration

These settings have sensible defaults but can be customized to match your needs:

#### `shifts` (object)
Defines shift codes, times, and display names. Modify these to match your organization's shift definitions. Each shift requires:
- **`start`** (string): Start time in 24-hour format (HH:MM)
- **`end`** (string): End time in 24-hour format (HH:MM, use "24:00" for midnight)
- **`name`** (string): Display name for the shift in calendar events

**Default shifts include:** A (Frühschicht), B (Spätschicht), N (Nachtschicht), WF (Wochenende Frühschicht), WS (Wochenende Spätschicht), K (Krank), U (Urlaub), F (Frei)

**Note:** Only modify if your schedule uses different shift codes or times.

#### `default_pattern` (array)
A 28-day pattern used to extend schedules beyond the PDF data. The pattern repeats cyclically for the continuation period. Modify this array to match your organization's typical rotation schedule.

**Default:** A 4-week rotation pattern (5 days N, 2 days WF, 5 days A, 2 days F, 5 days B, 2 days WS, 7 days F)

**Note:** Can be overridden at runtime with `--no-extend` to disable schedule extension.

#### `default_continuation_days` (integer)
Number of days to extend the schedule beyond the PDF data using the default pattern. Useful when the PDF only contains the current month but you want year-round calendar entries.

**Default:** `365` (one year)

**Note:** Can be overridden at runtime with `--extend-days <number>`.

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
