#!/bin/bash

# Function to add timestamp to each line
add_timestamp() {
    while IFS= read -r line; do
        # Get the current date in the format: Jun 04 25 Wed [01:32:32]
        echo "$(date '+%b %d %y %a [%H:%M:%S]'): $line" 
    done
}

# Change to the script directory
cd /root/schichtplan_sync || exit 1

# Log file for sync operations
LOG_FILE="/root/schichtplan_sync/sync.log"

# Get the repository URL for logging
REPO_URL=$(git remote get-url origin)
echo "Pulling latest changes from repository: $REPO_URL" | add_timestamp | tee -a "$LOG_FILE"

# Perform git pull and log the output
git pull 2>&1 | add_timestamp | tee -a "$LOG_FILE"
RESULT=${PIPESTATUS[0]}

if [ $RESULT -eq 0 ]; then
    echo "Pull of Schichtplan Sync Script completed successfully" | add_timestamp | tee -a "$LOG_FILE"
else
    echo "Pull of Schichtplan Sync Script failed with error code $RESULT" | add_timestamp | tee -a "$LOG_FILE"
fi

# Keep log file size manageable (keep last 1000 lines)
tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

# Run the Python script in its own environment
/root/schichtplan_sync/venv_schichtplan_sync/bin/python /root/schichtplan_sync/schichtplan_sync.py --no-mail 2>&1 | add_timestamp | tee -a "$LOG_FILE"

echo "Sync of Schichtplan completed successfully" | add_timestamp | tee -a "$LOG_FILE"
