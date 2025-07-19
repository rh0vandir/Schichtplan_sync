#!/usr/bin/env bash

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2025-04-11
# Version: 1.3.0

# Get the script directory dynamically
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'
BLACK_ON_YELLOW='\033[7;33m'
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi

# Check if tesseract-ocr is installed
if ! command -v tesseract &> /dev/null; then
    echo -e "${RED}Error: tesseract-ocr is not installed${NC}"
    echo -e "Please install it using your package manager:"
    echo -e "  Ubuntu/Debian: ${BOLD}sudo apt-get install tesseract-ocr${NORMAL}"
    echo -e "  Fedora: ${BOLD}sudo dnf install tesseract${NORMAL}"
    echo -e "  Arch Linux: ${BOLD}sudo pacman -S tesseract${NORMAL}"
    exit 1
fi

# Check if virtual environment exists and is properly set up
if [ -d "$SCRIPT_DIR/venv_schichtplan_sync" ]; then
    echo -e "${YELLOW}Virtual environment found. Checking requirements...${NC}"
    source "$SCRIPT_DIR/venv_schichtplan_sync/bin/activate"
    
    # Check if all required packages are installed
    if pip freeze | grep -q "pdfplumber" && \
       pip freeze | grep -q "requests" && \
       pip freeze | grep -q "cryptography" && \
       pip freeze | grep -q "icalendar" && \
       pip freeze | grep -q "pytz"; then
        echo -e "${GREEN}Virtual environment is properly set up with all required packages.${NC}"
        echo -e "To activate the virtual environment, run: ${BOLD}source venv_schichtplan_sync/bin/activate${NORMAL}"
        exit 0
    else
        echo -e "${YELLOW}Virtual environment exists but is missing some packages. Reinstalling...${NC}"
        deactivate
        rm -rf "$SCRIPT_DIR/venv_schichtplan_sync"
    fi
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv "$SCRIPT_DIR/venv_schichtplan_sync"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv_schichtplan_sync/bin/activate"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install pdfplumber requests cryptography icalendar pytz

# Create requirements.txt
echo -e "${YELLOW}Creating requirements.txt...${NC}"
pip freeze > "$SCRIPT_DIR/requirements.txt"

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p "$SCRIPT_DIR/calendars"
mkdir -p "$SCRIPT_DIR/utils"

# Check for configuration file
if [ ! -f "$SCRIPT_DIR/schichtplan_sync.json" ]; then
    echo -e "${YELLOW}Creating default configuration file...${NC}"
    cat > "$SCRIPT_DIR/schichtplan_sync.json" << 'EOL'
{
    "shifts": {
        "A": {"start": "07:00", "end": "14:00", "name": "Frühschicht"},
        "B": {"start": "14:00", "end": "24:00", "name": "Spätschicht"},
        "N": {"start": "00:00", "end": "07:00", "name": "Nachtschicht"},
        "WF": {"start": "00:00", "end": "12:00", "name": "Wochenende Frühschicht"},
        "WS": {"start": "12:00", "end": "24:00", "name": "Wochenende Spätschicht"}
    },
    "users": {
        "user1": {
            "name": "Some Name",
            "family": false,
            "mail": "some@email.com"
        },
        "user2": {
            "name": "Some Other Name",
            "family": true,
            "mail": "someother@email.com"
        }
    }
}
EOL
    echo -e "${GREEN}Default configuration file created. Please edit schichtplan_sync.json to add your users and shift configurations.${NC}"
fi

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "To activate the virtual environment, run: ${BOLD}source \"$SCRIPT_DIR/venv_schichtplan_sync/bin/activate\"${NORMAL}"
echo -e "To run the script: ${BOLD}\"$SCRIPT_DIR/venv_schichtplan_sync/bin/python\" \"$SCRIPT_DIR/schichtplan_sync.py\"${NORMAL}"

echo -e "\n${BLACK_ON_YELLOW}Configuration:${NC}"
echo -e "1. Edit ${BOLD}$SCRIPT_DIR/schichtplan_sync.json${NORMAL} to configure:"
echo -e "   - Shift definitions (start/end times and names)"
echo -e "   - User configurations (name, family mode, and email)"
echo -e "2. Run the script to process the schedule"

echo -e "\n${BLACK_ON_YELLOW}Calendar Integration:${NC}"
echo -e "The script will generate iCal files (${BOLD}.ics${NORMAL}) in the ${BOLD}$SCRIPT_DIR/calendars/${NORMAL} directory that you can import into any calendar application:"
echo -e "1. The script will create an iCal file for each configured user in ${BOLD}$SCRIPT_DIR/calendars/${NORMAL}"
echo -e "2. Import the iCal file into your calendar application:"
echo -e "   - Google Calendar: Click the '+' next to 'Other calendars' > 'Import'"
echo -e "   - Apple Calendar: File > Import"
echo -e "   - Outlook: File > Open & Export > Import/Export > Import an iCalendar file"
echo -e "3. The calendar events will be created with proper start and end times"
echo -e "4. Old calendar files are kept for change detection and email notifications"

echo -e "\n${BLACK_ON_YELLOW}Email Notifications:${NC}"
echo -e "The script can send email notifications when the schedule changes:"
echo -e "1. Configure your SMTP server credentials when prompted (stored securely in ${BOLD}~/.schichtplan_smtp_credentials${NORMAL})"
echo -e "2. Add email addresses to user configurations in $SCRIPT_DIR/schichtplan_sync.json"
echo -e "3. Notifications will be sent only when the schedule actually changes"
echo -e "4. The mail utility (${BOLD}$SCRIPT_DIR/utils/mail_utils.py${NORMAL}) can be used independently for custom notifications"

echo -e "\n${BLACK_ON_YELLOW}Directory Structure:${NC}"
echo -e "  ${BOLD}$SCRIPT_DIR/calendars/${NORMAL}: Contains all generated ICS calendar files"
echo -e "  ${BOLD}$SCRIPT_DIR/utils/${NORMAL}: Contains utility modules (mail notifications, etc.)"
echo -e "  ${BOLD}$SCRIPT_DIR/schichtplan_sync.json${NORMAL}: Configuration file for shifts and users"
echo -e "  ${BOLD}$SCRIPT_DIR/venv_schichtplan_sync/${NORMAL}: Python virtual environment"

echo -e "\n${BLACK_ON_YELLOW}Additional Options:${NC}"
echo -e "  --name: Override configuration and process schedule for specific name"
echo -e "  --family: Include first name in event summary (only with --name)"
echo -e "  --local: Use a local PDF file for testing"
echo -e "  --no-ftp: Skip FTP upload"
echo -e "  --mail: Enable email notifications (default)"
echo -e "  --no-mail: Disable email notifications"
echo -e "  --force: Force processing even if PDF has not changed"

echo -e "\n${BLACK_ON_YELLOW}Example Usage:${NC}"
echo -e "  ${BOLD}\"$SCRIPT_DIR/venv_schichtplan_sync/bin/python\" \"$SCRIPT_DIR/schichtplan_sync.py\" --name 'John Doe' --family --local${NORMAL} (process schedule for John Doe with family mode and use local PDF file)"
echo -e "  ${BOLD}\"$SCRIPT_DIR/venv_schichtplan_sync/bin/python\" \"$SCRIPT_DIR/schichtplan_sync.py\" --no-mail${NORMAL} (process schedule of configured users without email notifications)"
echo -e "  ${BOLD}\"$SCRIPT_DIR/venv_schichtplan_sync/bin/python\" \"$SCRIPT_DIR/schichtplan_sync.py\" --force${NORMAL} (force processing even if PDF hasn't changed)"
echo -e "  ${BOLD}\"$SCRIPT_DIR/venv_schichtplan_sync/bin/python\" \"$SCRIPT_DIR/utils/mail_utils.py\" --to 'user@example.com' --subject 'Test' --message 'Hello'${NORMAL} (send custom email notification)"

echo -e "\n${BLACK_ON_YELLOW}Cron Job Setup:${NC}"
echo -e "To set up automated execution, add to your crontab:"
echo -e "  ${BOLD}crontab -e${NORMAL}"
echo -e "  ${BOLD}0 */4 * * * \"$SCRIPT_DIR/cron_schichtplan.sh\"${NORMAL} (run every 4 hours)"
echo -e "The cron script will:"
echo -e "  - Sync the latest code from git"
echo -e "  - Run the schedule processing"
echo -e "  - Send email notifications for any errors"