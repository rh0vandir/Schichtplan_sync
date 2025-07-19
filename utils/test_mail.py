#!/usr/bin/env python3

"""
Test script to demonstrate the mail utility functionality
"""

from mail_utils import send_mail, send_notification_email

def test_schedule_update():
    """Test sending a schedule update email"""
    print("Testing schedule update email...")
    
    # Example changes
    changes = [
        "New shift added: F 08-16 on 2024-12-25",
        "Shift changed on 2024-12-26: N 20-07 → F 08-16",
        "Shift removed: K on 2024-12-27"
    ]
    
    success = send_mail(
        recipient_email="test@example.com",
        user_name="Test User",
        changes=changes,
        subject="Test Schedule Update"
    )
    
    print(f"Schedule update email result: {'Success' if success else 'Failed'}")

def test_notification_email():
    """Test sending a simple notification email"""
    print("Testing notification email...")
    
    success = send_notification_email(
        recipient_email="test@example.com",
        subject="Test Notification",
        message="This is a test notification email from the mail utility."
    )
    
    print(f"Notification email result: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    print("Mail Utility Test Script")
    print("=" * 30)
    
    # Note: These tests will fail unless you have valid SMTP credentials configured
    # and a valid email address. This is just to demonstrate the API.
    
    test_schedule_update()
    print()
    test_notification_email()
    
    print("\nNote: Tests will fail without valid SMTP credentials and email addresses.")
    print("Configure your SMTP settings first by running the main script.") 