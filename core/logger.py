"""
CSV logging utilities for recording email send results.
"""

import csv
import os

# Path to the CSV log file (relative to the working directory).
LOG_FILE = "send_log.csv"


def log_result(timestamp: str, email: str, name: str, status: str, error_message: str = "") -> None:
    """
    Append a single send result to the CSV log file.

    Creates the file with headers if it does not already exist.

    Parameters:
        timestamp (str): ISO-format timestamp of the operation.
        email (str): The recipient's email address.
        name (str): The recipient's name.
        status (str): Result status: "SENT", "FAILED", "SKIPPED_INVALID", "SKIPPED_DUPLICATE".
        error_message (str): Error description if any (default: empty string).

    Side effects:
        Creates or appends to LOG_FILE.
    """
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'name', 'status', 'error_message'])
        writer.writerow([timestamp, email, name, status, error_message])
