#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Tuple, Dict, List, Optional

def load_config():
    """Load configuration from schichtplan_sync.json"""
    config_file = Path(__file__).parent.parent / 'schichtplan_sync.json'
    
    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_file}")
        return None, None
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Parse shifts
        shifts = config['shifts']
            
        # Parse users
        users = []
        for user_id, user_data in config['users'].items():
            if user_id.startswith('user'):  # Skip non-user entries
                users.append((user_data['name'], user_data['family'], user_data['mail']))
                
        return shifts, users
        
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return None, None

def get_default_pattern() -> Optional[List[str]]:
    """Get the default shift pattern from configuration"""
    config_file = Path(__file__).parent.parent / 'schichtplan_sync.json'
    
    if not config_file.exists():
        return None
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config.get('default_pattern', [])
        
    except Exception as e:
        print(f"Error reading default pattern: {e}")
        return None

def get_default_continuation_days() -> int:
    """Get the default continuation days from configuration"""
    config_file = Path(__file__).parent.parent / 'schichtplan_sync.json'
    
    if not config_file.exists():
        return 365  # Default fallback
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config.get('default_continuation_days', 365)
        
    except Exception as e:
        print(f"Error reading default continuation days: {e}")
        return 365  # Default fallback
