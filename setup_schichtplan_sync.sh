#!/usr/bin/env bash

# MIT License
# Copyright (c) 2025 Andras Gerendas
# Created: 2024-03-19
# Version: 1.1

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
if [ -d "venv_schichtplan_sync" ]; then
    echo -e "${YELLOW}Virtual environment found. Checking requirements...${NC}"
    source venv_schichtplan_sync/bin/activate
    
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
        rm -rf venv_schichtplan_sync
    fi
fi

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv_schichtplan_sync

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv_schichtplan_sync/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install pdfplumber requests cryptography icalendar pytz

# Create requirements.txt
echo -e "${YELLOW}Creating requirements.txt...${NC}"
pip freeze > requirements.txt

# Check for configuration file
if [ ! -f "schichtplan_sync.json" ]; then
    echo -e "${YELLOW}Creating default configuration file...${NC}"
    cat > schichtplan_sync.json << 'EOL'
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
echo -e "To activate the virtual environment, run: ${BOLD}source venv_schichtplan_sync/bin/activate${NORMAL}"
echo -e "To run the script: ${BOLD}python3 schichtplan_sync.py${NORMAL}"

echo -e "\n${BLACK_ON_YELLOW}Configuration:${NC}"
echo -e "1. Edit ${BOLD}schichtplan_sync.json${NORMAL} to configure:"
echo -e "   - Shift definitions (start/end times and names)"
echo -e "   - User configurations (name, family mode, and email)"
echo -e "2. Run the script to process the schedule"

echo -e "\n${BLACK_ON_YELLOW}Calendar Integration:${NC}"
echo -e "The script will generate an iCal file (${BOLD}.ics${NORMAL}) that you can import into any calendar application:"
echo -e "1. The script will create an iCal file for each configured user"
echo -e "2. Import the iCal file into your calendar application:"
echo -e "   - Google Calendar: Click the '+' next to 'Other calendars' > 'Import'"
echo -e "   - Apple Calendar: File > Import"
echo -e "   - Outlook: File > Open & Export > Import/Export > Import an iCalendar file"
echo -e "3. The calendar events will be created with proper start and end times"

echo -e "\n${BLACK_ON_YELLOW}Email Notifications:${NC}"
echo -e "The script can send email notifications when the schedule changes:"
echo -e "1. Configure your SMTP server credentials when prompted"
echo -e "2. Add email addresses to user configurations in schichtplan_sync.json"
echo -e "3. Notifications will be sent only when the schedule actually changes"

echo -e "\n${BLACK_ON_YELLOW}Additional Options:${NC}"
echo -e "  --name: Override configuration and process schedule for specific name"
echo -e "  --family: Include first name in event summary (only with --name)"
echo -e "  --local: Use a local PDF file for testing"
echo -e "  --no-ftp: Skip FTP upload"
echo -e "  --mail: Enable email notifications (default)"
echo -e "  --no-mail: Disable email notifications"

echo -e "\n${BLACK_ON_YELLOW}Example Usage:${NC}"
echo -e "  ${BOLD}python3 schichtplan_sync.py --name 'John Doe' --family --local${NORMAL} (process schedule for John Doe with family mode and use local PDF file)"
echo -e "  ${BOLD}python3 schichtplan_sync.py --no-mail${NORMAL} (process schedule of configured users without email notifications)"