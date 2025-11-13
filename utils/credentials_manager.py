#!/usr/bin/env python3

import os
from getpass import getpass
from cryptography.fernet import Fernet
from typing import Tuple

def get_credentials() -> Tuple[str, str]:
    """Get credentials from encrypted file or prompt user"""
    credentials_file = os.path.expanduser('~/.schichtplan_credentials')
    key_file = os.path.expanduser('~/.schichtplan_key')

    # Try to load existing credentials
    if os.path.exists(credentials_file) and os.path.exists(key_file):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            fernet = Fernet(key)

            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            username, password = decrypted_data.decode().split(':')
            return username, password
        except Exception as e:
            print(f"Error reading credentials: {e}")

    # If no credentials file or error, prompt user
    print("Bitte gebe deine Zugangsdaten für den Schichtplan ein:")
    username = input("Nutzername: ")
    password = getpass("Passwort: ")

    # Save credentials
    try:
        # Generate new key if needed
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()

        fernet = Fernet(key)
        data = f"{username}:{password}"
        encrypted_data = fernet.encrypt(data.encode())

        with open(credentials_file, 'wb') as f:
            f.write(encrypted_data)

        # Set secure permissions
        os.chmod(credentials_file, 0o600)
        os.chmod(key_file, 0o600)

    except Exception as e:
        print(f"Warning: Could not save credentials: {e}")

    return username, password

def get_ftp_credentials(force_prompt: bool = False) -> Tuple[str, str, str]:
    """Get FTP credentials from encrypted file or prompt user"""
    credentials_file = os.path.expanduser('~/.schichtplan_ftp_credentials')
    key_file = os.path.expanduser('~/.schichtplan_ftp_key')

    # Try to load existing credentials
    if (not force_prompt and
            os.path.exists(credentials_file) and os.path.exists(key_file)):
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            fernet = Fernet(key)

            with open(credentials_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            host, username, password = decrypted_data.decode().split(':')
            return host, username, password
        except Exception as e:
            print(f"Error reading FTP credentials: {e}")

    # If no credentials file or error, prompt user
    print("Bitte gebe deine FTP Zugangsdaten ein:")
    host = input("FTP Host: ")
    username = input("Nutzername: ")
    password = getpass("Passwort: ")

    # Save credentials
    try:
        # Generate new key if needed
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()

        fernet = Fernet(key)
        data = f"{host}:{username}:{password}"
        encrypted_data = fernet.encrypt(data.encode())

        with open(credentials_file, 'wb') as f:
            f.write(encrypted_data)

        # Set secure permissions
        os.chmod(credentials_file, 0o600)
        os.chmod(key_file, 0o600)

    except Exception as e:
        print(f"Warning: Could not save FTP credentials: {e}")

    return host, username, password
