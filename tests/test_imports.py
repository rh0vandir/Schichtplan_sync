#!/usr/bin/env python3
"""Test that all modules can be imported without errors"""

import pytest


class TestImports:
    """Test module imports"""
    
    def test_main_script_import(self):
        """Test that main script can be imported"""
        import schichtplan_sync
        assert schichtplan_sync is not None
    
    def test_utils_imports(self):
        """Test that all utility modules can be imported"""
        from utils import config_loader
        from utils import pdf_processor
        from utils import calendar_generator
        from utils import ftp_uploader
        from utils import mail_utils
        from utils import credentials_manager
        from utils import shift_continuation
        from utils import year_tracker
        
        assert config_loader is not None
        assert pdf_processor is not None
        assert calendar_generator is not None
        assert ftp_uploader is not None
        assert mail_utils is not None
        assert credentials_manager is not None
        assert shift_continuation is not None
        assert year_tracker is not None
    
    def test_critical_functions_exist(self):
        """Test that critical functions exist in modules"""
        from utils.config_loader import load_config
        from utils.pdf_processor import extract_and_create_ical
        from utils.ftp_uploader import upload_to_ftp
        from utils.mail_utils import send_mail
        
        assert callable(load_config)
        assert callable(extract_and_create_ical)
        assert callable(upload_to_ftp)
        assert callable(send_mail)


class TestDependencies:
    """Test that required dependencies are available"""
    
    def test_required_packages(self):
        """Test that all required packages can be imported"""
        import requests
        import icalendar
        import pdfplumber
        import pytesseract
        from datetime import datetime
        from dateutil import parser
        
        assert requests is not None
        assert icalendar is not None
        assert pdfplumber is not None
        assert pytesseract is not None
        assert datetime is not None
        assert parser is not None

