"""
Validation utilities for email addresses and file paths.
"""

import os
import re
import sys
from typing import List, Optional

# Regex pattern for validating email address format (RFC 5322 simplified).
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def validate_email(email: str) -> bool:
    """
    Check whether an email address matches a valid format.

    Parameters:
        email (str): The email address string to validate.

    Returns:
        bool: True if the email matches the expected pattern, False otherwise.
    """
    return bool(EMAIL_PATTERN.match(email))


def validate_file_exists(file_path: str, label: str) -> None:
    """
    Verify that a file exists at the given path. Exit with an error if not.

    Parameters:
        file_path (str): The path to check.
        label (str): A human-readable label for the file (used in the error message).

    Side effects:
        Exits the program (sys.exit(1)) if the file does not exist.
    """
    if not os.path.isfile(file_path):
        print(f"ERROR: {label} '{file_path}' not found.")
        sys.exit(1)


def validate_attachments(attachments: Optional[List[str]]) -> None:
    """
    Verify that all attachment file paths exist. Exit with an error on first missing file.

    Parameters:
        attachments (Optional[List[str]]): List of file paths to validate, or None.

    Side effects:
        Exits the program (sys.exit(1)) if any attachment file does not exist.
    """
    if not attachments:
        return
    for att_path in attachments:
        if not os.path.isfile(att_path):
            print(f"ERROR: Attachment file '{att_path}' not found.")
            sys.exit(1)
