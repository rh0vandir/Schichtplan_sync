# Mail Utility for Schichtplan Sync

This document describes the new mail utility functionality that has been extracted from the main `schichtplan_sync.py` script.

## Overview

The `utils/mail_utils.py` script provides a standalone email notification system that can be used by:
- The main `schichtplan_sync.py` script for schedule change notifications
- The `cron_schichtplan.sh` script for system notifications
- Any other script that needs to send email notifications

## Features

- **Encrypted SMTP credentials**: Credentials are stored securely using Fernet encryption
- **Flexible email types**: Supports both schedule updates and custom notifications
- **Command-line interface**: Can be used directly from the command line
- **Python module**: Can be imported and used in other Python scripts
- **Error handling**: Comprehensive error handling with detailed logging

## Usage

### As a Python Module

```python
from mail_utils import send_mail, send_notification_email

# Send a schedule update email
success = send_mail(
    recipient_email="user@example.com",
    user_name="John Doe",
    changes=["New shift added: F 08-16 on 2024-12-25"],
    subject="Schedule Update"
)

# Send a simple notification email
success = send_notification_email(
    recipient_email="admin@example.com",
    subject="System Alert",
    message="The system has encountered an error."
)
```

### From Command Line

```bash
# Send a schedule update email
python3 utils/mail_utils.py --to user@example.com --name "John Doe" \
    --changes "New shift added: F 08-16 on 2024-12-25" \
    --subject "Schedule Update"

# Send a custom notification email
python3 utils/mail_utils.py --to admin@example.com \
    --subject "System Alert" \
    --message "The system has encountered an error."
```

### In Shell Scripts

```bash
# Send notification from cron script
/root/schichtplan_sync/venv_schichtplan_sync/bin/python /root/schichtplan_sync/utils/mail_utils.py \
    --to "admin@example.com" \
    --subject "Cron Job Failed" \
    --message "The scheduled job has failed."
```

## Configuration

### First-time Setup

When you first use the mail utility, it will prompt you for SMTP credentials:

1. **SMTP Host**: Your SMTP server address (e.g., `smtp.gmail.com`)
2. **SMTP Port**: SMTP port (usually 587 for TLS or 465 for SSL)
3. **SMTP Username**: Your email username
4. **SMTP Password**: Your email password

The credentials are encrypted and stored in:
- `~/.schichtplan_smtp_credentials` (encrypted credentials)
- `~/.schichtplan_smtp_key` (encryption key)

### Security

- Credentials are encrypted using Fernet (symmetric encryption)
- Files have restricted permissions (600)
- No credentials are stored in plain text

## Functions

### `send_mail(recipient_email, user_name, changes=None, subject=None, custom_body=None)`

Sends an email notification about schedule changes.

**Parameters:**
- `recipient_email` (str): Email address of the recipient
- `user_name` (str): Name of the user (for personalization)
- `changes` (list, optional): List of schedule changes
- `subject` (str, optional): Email subject (default: "Schichtplan Update")
- `custom_body` (str, optional): Custom message body (overrides default format)

**Returns:**
- `bool`: True if email was sent successfully, False otherwise

### `send_notification_email(recipient_email, subject, message)`

Sends a simple notification email.

**Parameters:**
- `recipient_email` (str): Email address of the recipient
- `subject` (str): Email subject
- `message` (str): Email message body

**Returns:**
- `bool`: True if email was sent successfully, False otherwise

### `get_smtp_credentials()`

Gets SMTP credentials from encrypted storage or prompts user.

**Returns:**
- `tuple`: (host, port, username, password) or (None, None, None, None) if failed

## Integration with Existing Scripts

### Main Script (`schichtplan_sync.py`)

The main script now imports the mail utility:

```python
from mail_utils import send_mail
```

The existing mail functionality remains the same, but now uses the external module.

### Cron Script (`cron_schichtplan.sh`)

The cron script now uses the Python mail utility instead of the system `mail` command:

```bash
/root/schichtplan_sync/venv_schichtplan_sync/bin/python /root/schichtplan_sync/mail_utils.py \
    --to "$recipient" \
    --subject "$subject" \
    --message "$message"
```

## Error Handling

The mail utility includes comprehensive error handling:

- **SMTP errors**: Connection, authentication, and sending errors
- **SSL errors**: TLS/SSL configuration issues
- **Timeout errors**: Network timeout issues
- **Credential errors**: Missing or invalid credentials
- **File permission errors**: Issues with credential storage

All errors are logged with descriptive messages to help with troubleshooting.

## Testing

Use the `test_mail.py` script to test the mail utility functionality:

```bash
python3 utils/test_mail.py
```

Note: Tests will fail without valid SMTP credentials and email addresses.

## Dependencies

The mail utility requires the following Python packages:
- `cryptography` (for credential encryption)
- Standard library modules: `smtplib`, `ssl`, `email`, `os`, `argparse`

These are already included in the main project's virtual environment. 