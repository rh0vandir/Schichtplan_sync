#!/bin/bash

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2025-04-12
# Version: 3.0

# Cron script for automatically syncing and processing work schedules
# This script:
# - Syncs the latest code from git
# - Runs the schedule processing
# - Sends email notifications for any errors



# Get the script directory dynamically
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to add timestamp to each line
add_timestamp() {
    while IFS= read -r line; do
        # Get the current date in the format: Jun 04 25 Wed [01:32:32]
        echo "$(date '+%b %d %y %a [%H:%M:%S]'): $line" 
    done
}

# Function to send email notification
send_email_notification() {
    local subject="$1"
    local message="$2"
    local recipient="schichtplan@rhovandir.net"
    
    # Use the Python mail utility script
    if [ -f "$SCRIPT_DIR/venv_schichtplan_sync/bin/python" ]; then
        "$SCRIPT_DIR/venv_schichtplan_sync/bin/python" "$SCRIPT_DIR/utils/mail_utils.py" \
            --to "$recipient" \
            --subject "$subject" \
            --message "$message" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "Email notification sent to $recipient" | add_timestamp | tee -a "$LOG_FILE"
        else
            echo "Warning: Failed to send email notification" | add_timestamp | tee -a "$LOG_FILE"
        fi
    else
        echo "Warning: Python mail utility not available, cannot send notification" | add_timestamp | tee -a "$LOG_FILE"
    fi
}

# Change to the script directory
cd "$SCRIPT_DIR" || exit 1

# Log file for sync operations
LOG_FILE="$SCRIPT_DIR/sync.log"

# Get the repository URL for logging
REPO_URL=$(git remote get-url origin)
echo "Syncing latest changes from repository: $REPO_URL" | add_timestamp | tee -a "$LOG_FILE"

# Check if git sync is available, otherwise use git pull
if git help sync &> /dev/null; then
    GIT_CMD="git sync"
else
    GIT_CMD="git pull"
    echo "Note: git sync not available, using git pull instead" | add_timestamp | tee -a "$LOG_FILE"
fi

# Perform git sync/pull and log the output
$GIT_CMD 2>&1 | add_timestamp | tee -a "$LOG_FILE"
RESULT=${PIPESTATUS[0]}

if [ $RESULT -eq 0 ]; then
    echo "Sync of Schichtplan Sync Script completed successfully" | add_timestamp | tee -a "$LOG_FILE"
else
    echo "Sync of Schichtplan Sync Script failed with error code $RESULT" | add_timestamp | tee -a "$LOG_FILE"
    
    # Check if the error indicates manual intervention is needed
    # Common git error codes that require manual intervention:
    # 1 = General error (often merge conflicts, authentication issues, etc.)
    # 128 = Authentication failed or repository not found
    if [ $RESULT -eq 1 ] || [ $RESULT -eq 128 ]; then
        ERROR_MESSAGE="Git sync failed with error code $RESULT. Manual intervention may be required for repository: $REPO_URL"
        echo "$ERROR_MESSAGE" | add_timestamp | tee -a "$LOG_FILE"
        send_email_notification "Schichtplan Sync - Manual Intervention Required" "$ERROR_MESSAGE"
    fi
fi

# Keep log file size manageable (keep last 1000 lines)
tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

# Run the Python script in its own environment with unbuffered output
PYTHONUNBUFFERED=1 "$SCRIPT_DIR/venv_schichtplan_sync/bin/python" -u "$SCRIPT_DIR/schichtplan_sync.py" 2>&1 | add_timestamp | tee -a "$LOG_FILE"

echo "Sync of Schichtplan completed successfully" | add_timestamp | tee -a "$LOG_FILE"
