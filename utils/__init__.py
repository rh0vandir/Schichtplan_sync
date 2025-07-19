# Utils package for Schichtplan Sync
# Contains utility modules for email notifications and other helper functions

from .mail_utils import send_mail, send_notification_email, get_smtp_credentials

__all__ = ['send_mail', 'send_notification_email', 'get_smtp_credentials'] 