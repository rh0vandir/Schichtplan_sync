# Changelog

All notable changes to the Schichtplan Sync project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and core functionality
- PDF processing with OCR support using Tesseract
- Calendar integration with iCal format generation
- Email notification system
- FTP upload functionality
- Encrypted credential storage using Fernet encryption
- Command-line interface with various options
- Configuration system with JSON-based settings
- Virtual environment setup script
- Cron job automation script

### Changed
- Project structure simplified and optimized
- Enhanced logging configuration
- Improved error handling and user feedback

### Fixed
- Various bug fixes and stability improvements

## [4.20.0] - 2025-01-XX

### Added
- Enhanced email notification system with utility module
- Comprehensive README documentation for calendars directory
- Dynamic path handling in cron scripts
- Improved logging throughout the application

### Changed
- Refactored email notification system for better modularity
- Updated cron script paths for dynamic execution
- Enhanced script structure and organization
- Cleaned up .gitignore with comprehensive exclusions

### Fixed
- Improved error handling in email notifications
- Better logging configuration and message formatting

## [4.19.0] - 2025-01-XX

### Added
- Initial calendar creation message in ICS comparison
- Enhanced logging configuration for better debugging

### Changed
- Updated version numbering system
- Improved logging output and formatting

## [4.18.0] - 2025-01-XX

### Added
- Initial project setup with core functionality
- PDF download and parsing capabilities
- iCal file generation for calendar integration
- Basic authentication system
- Configuration file support

### Changed
- Project structure established
- Core functionality implemented

## Features Overview

### Core Features
- **PDF Processing**: Downloads and parses PDF schedules using OCR (Tesseract)
- **Calendar Integration**: Generates iCal files compatible with Google Calendar, Apple Calendar, Outlook, etc.
- **Email Notifications**: Sends notifications when schedules change
- **FTP Upload**: Automatically uploads generated iCal files to FTP server
- **Encrypted Credentials**: Securely stores login credentials using Fernet encryption
- **Flexible Configuration**: Supports custom shift definitions and user configurations

### Command Line Options
- `--name`: Override configuration and process schedule for specific name
- `--family`: Include first name in event summary (only with --name)
- `--local`: Use a local PDF file for testing
- `--no-ftp`: Skip FTP upload
- `--mail`: Enable email notifications (default)
- `--no-mail`: Disable email notifications

### Security Features
- Credentials are encrypted using Fernet encryption
- Credential files are stored with secure permissions (600)
- No sensitive data is logged

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

## Requirements

- Python 3.6+
- Tesseract OCR
- Internet connection for PDF download
- FTP server (optional)

## License

MIT License - Copyright (c) 2025 Andras Gerendas

---

## Contributing

This project follows standard Git workflow practices. Please ensure all commits follow conventional commit message format for automatic changelog generation.

## Version History

- **4.20.0**: Enhanced email system, improved logging, better project structure
- **4.19.0**: Enhanced logging configuration and ICS comparison improvements
- **4.18.0**: Initial release with core functionality

For detailed commit history, see the Git log or repository history. 