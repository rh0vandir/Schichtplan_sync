# Schichtplan Sync

A Python-based tool for automatically downloading, parsing, and syncing work schedules from PDF files to calendar applications via iCal format.

## Features

- **PDF Processing**: Downloads and parses PDF schedules using OCR (Tesseract)
- **Calendar Integration**: Generates iCal files compatible with Google Calendar, Apple Calendar, Outlook, etc.
- **Email Notifications**: Sends notifications when schedules change
- **FTP Upload**: Automatically uploads generated iCal files to FTP server
- **Encrypted Credentials**: Securely stores login credentials using Fernet encryption
- **Flexible Configuration**: Supports custom shift definitions and user configurations

## Requirements

- Python 3.6+
- Tesseract OCR
- Internet connection for PDF download
- FTP server (optional)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-gitlab-repo-url>
   cd schichtplan_sync
   ```

2. **Run the setup script:**
   ```bash
   ./setup_schichtplan_sync.sh
   ```

The setup script will:
- Check for required dependencies (Python 3, pip3, Tesseract)
- Create a virtual environment
- Install required Python packages
- Create a default configuration file
- Generate a requirements.txt file

## Configuration

Edit `schichtplan_sync.json` to configure:

### Shift Definitions
```json
{
    "shifts": {
        "A": {"start": "07:00", "end": "14:00", "name": "Frühschicht"},
        "B": {"start": "14:00", "end": "24:00", "name": "Spätschicht"},
        "N": {"start": "00:00", "end": "07:00", "name": "Nachtschicht"}
    }
}
```

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
```

## Command Line Options

- `--name`: Override configuration and process schedule for specific name
- `--family`: Include first name in event summary (only with --name)
- `--local`: Use a local PDF file for testing
- `--no-ftp`: Skip FTP upload
- `--mail`: Enable email notifications (default)
- `--no-mail`: Disable email notifications

## Calendar Integration

The script generates iCal files that can be imported into:

- **Google Calendar**: Click the '+' next to 'Other calendars' > 'Import'
- **Apple Calendar**: File > Import
- **Outlook**: File > Open & Export > Import/Export > Import an iCalendar file

## Security

- Credentials are encrypted using Fernet encryption
- Credential files are stored with secure permissions (600)
- No sensitive data is logged

## License

MIT License - Copyright (c) 2025 Andras Gerendas

## Version

Current Version: 4.18 