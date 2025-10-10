#!/usr/bin/env python3
"""Basic functionality tests for the main script"""

import pytest
import hashlib
import tempfile
import os


class TestPDFComparison:
    """Test PDF comparison functionality"""
    
    def test_compare_pdf_content_with_new_pdf(self):
        """Test that new PDF content returns True"""
        from schichtplan_sync import compare_pdf_content
        
        # Create test PDF content
        test_content = b"Test PDF content %d" % hash(os.urandom(16))
        
        # Use a temporary hash file
        with tempfile.NamedTemporaryFile(delete=False, suffix='_test_hash') as f:
            temp_hash_file = f.name
        
        try:
            # Mock the hash file location
            import schichtplan_sync
            original_expanduser = os.path.expanduser
            
            def mock_expanduser(path):
                if '.schichtplan_pdf_hash' in path:
                    return temp_hash_file
                return original_expanduser(path)
            
            os.path.expanduser = mock_expanduser
            
            # First run should return True (new content)
            result = compare_pdf_content(test_content)
            assert result is True
            
            # Second run with same content should return False
            result = compare_pdf_content(test_content)
            assert result is False
            
            # Restore original function
            os.path.expanduser = original_expanduser
        finally:
            if os.path.exists(temp_hash_file):
                os.unlink(temp_hash_file)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_download_pdf_with_invalid_url(self):
        """Test that invalid URL handling works"""
        from schichtplan_sync import download_pdf
        
        result = download_pdf("http://invalid.test.url.that.does.not.exist.com/file.pdf", 
                             "user", "pass")
        assert result is None
    
    def test_hash_calculation(self):
        """Test that PDF hash calculation is consistent"""
        test_data = b"Test PDF content"
        hash1 = hashlib.sha256(test_data).hexdigest()
        hash2 = hashlib.sha256(test_data).hexdigest()
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest length

