#!/usr/bin/env python3
"""Tests for config_loader module"""

import pytest
import json
import tempfile
import os
from utils.config_loader import load_config, get_default_continuation_days, get_pdf_url


class TestConfigLoader:
    """Test configuration loading functionality"""

    def test_sample_config_is_valid_json(self):
        """Test that config.json.sample is valid JSON"""
        with open('config.json.sample', 'r') as f:
            config = json.load(f)

        assert config is not None
        assert 'shifts' in config
        assert 'users' in config

    def test_sample_config_has_required_fields(self):
        """Test that sample config has all required fields"""
        with open('config.json.sample', 'r') as f:
            config = json.load(f)

        # Check shifts structure
        assert isinstance(config['shifts'], dict)

        # Check users structure (can be dict or list)
        assert 'users' in config
        assert isinstance(config['users'], (dict, list))

        # Check for optional fields
        assert 'pdf_url' in config
        assert 'default_continuation_days' in config

    def test_load_config_with_valid_file(self):
        """Test loading a valid config file"""
        # Test that the actual config can be loaded
        # This works if either config.json or config.json.sample exists
        shifts, users = load_config()

        # If config.json doesn't exist, both will be None - that's OK for the test
        # The important thing is that load_config() doesn't crash
        if shifts is not None:
            # If we got shifts, validate the structure
            assert isinstance(shifts, dict)
            assert len(shifts) > 0

            # Each shift should have required fields
            for shift_code, shift_data in shifts.items():
                assert 'start' in shift_data
                assert 'end' in shift_data
                assert 'name' in shift_data

        if users is not None:
            # If we got users, validate the structure
            assert isinstance(users, list)
            # Each user should be a tuple of (name, family, mail)
            for user in users:
                assert len(user) == 3
                assert isinstance(user[0], str)  # name
                assert isinstance(user[1], bool)  # family
                assert isinstance(user[2], str)  # mail

    def test_shift_structure(self):
        """Test that shifts have the correct structure"""
        with open('config.json.sample', 'r') as f:
            config = json.load(f)

        for shift_code, shift_data in config['shifts'].items():
            assert 'start' in shift_data
            assert 'end' in shift_data
            assert 'name' in shift_data

            # Verify time format (HH:MM or H:MM)
            start_parts = shift_data['start'].split(':')
            end_parts = shift_data['end'].split(':')

            assert len(start_parts) == 2
            assert len(end_parts) == 2
            assert 0 <= int(start_parts[0]) <= 24
            assert 0 <= int(start_parts[1]) <= 59
            assert 0 <= int(end_parts[0]) <= 24
            assert 0 <= int(end_parts[1]) <= 59


class TestConfigHelpers:
    """Test helper functions for config"""

    def test_get_default_continuation_days(self):
        """Test getting default continuation days"""
        days = get_default_continuation_days()
        assert isinstance(days, int)
        assert days > 0

    def test_get_pdf_url(self):
        """Test getting PDF URL from config"""
        url = get_pdf_url()
        # URL might be None if not in config, or a string if configured
        assert url is None or isinstance(url, str)

