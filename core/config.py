"""
Configuration loading from config.json and command-line argument parsing.

Priority (highest to lowest):
    CLI arguments > config.json values > built-in defaults.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict


def load_config(script_dir: str) -> Dict[str, Any]:
    """
    Load settings from config.json located in the given directory.

    Parameters:
        script_dir (str): The directory containing config.json.

    Returns:
        Dict[str, Any]: Parsed configuration dictionary.
            Returns an empty dict if the file is missing or unreadable.

    Side effects:
        Prints a status message indicating success or failure.
    """
    config_path = os.path.join(script_dir, 'config.json')
    if not os.path.isfile(config_path):
        print("WARNING: config.json not found. Using command-line arguments or defaults.")
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ Loaded settings from config.json")
        return config
    except Exception as e:
        print(f"WARNING: Could not read config.json: {e}")
        return {}


def parse_args(config: Dict[str, Any]) -> argparse.Namespace:
    """
    Parse command-line arguments, using config.json values as defaults.

    Parameters:
        config (Dict[str, Any]): Configuration dictionary from load_config().

    Returns:
        argparse.Namespace: Parsed arguments with all settings resolved.
    """
    parser = argparse.ArgumentParser(
        description='Send Arabic event reminder emails to guests from Excel file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python3 send_reminders.py
  python3 send_reminders.py --dry-run
        """
    )

    parser.add_argument('--file', default=config.get('file', 'guests.xlsx'), help='Path to Excel file')
    parser.add_argument('--sheet', default=config.get('sheet'), help='Sheet name (default: first sheet)')
    parser.add_argument('--email-col', default=config.get('email_col'), help='Email column name')
    parser.add_argument('--name-col', default=config.get('name_col'), help='Name column name')
    parser.add_argument('--event-name', default=config.get('event_name'), help='Event name (Arabic)')
    parser.add_argument('--event-date', default=config.get('event_date'), help='Event date (Arabic)')
    parser.add_argument('--subject', default=config.get('subject') or None, help='Custom email subject')
    parser.add_argument('--dry-run', action='store_true', help='Test mode: no emails sent')
    parser.add_argument('--batch-size', type=int, default=config.get('batch_size', 75), help='Emails per batch')
    parser.add_argument('--batch-sleep-seconds', type=int, default=config.get('batch_sleep_seconds', 900), help='Sleep between batches (seconds)')
    parser.add_argument('--min-delay', type=float, default=config.get('min_delay', 2.0), help='Min delay between emails (seconds)')
    parser.add_argument('--max-delay', type=float, default=config.get('max_delay', 4.0), help='Max delay between emails (seconds)')
    parser.add_argument('--from-name', default=config.get('from_name', 'فريق الفعالية'), help='From display name')
    parser.add_argument('--reply-to', default=config.get('reply_to') or None, help='Reply-To email address')
    parser.add_argument('--template', default=config.get('template', 'message_template.txt'), help='Path to message template file')
    parser.add_argument('--logo', default=config.get('logo') or None, help='Logo image to display in email header (HTML mode)')
    parser.add_argument('--embedded-image', default=config.get('embedded_image') or None, help='Image to embed in email body')
    parser.add_argument('--attachments', nargs='*', default=config.get('attachments') or None, help='Files to attach to the email')
    parser.add_argument('--no-html', action='store_true', default=not config.get('html', True), help='Send plain text only (no HTML wrapping)')

    return parser.parse_args()


def get_gmail_credentials() -> tuple:
    """
    Read Gmail credentials from environment variables.

    Returns:
        tuple: (gmail_user, gmail_password) strings.

    Side effects:
        Exits the program if either GMAIL_USER or GMAIL_APP_PASSWORD is not set.
    """
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        print("ERROR: Environment variables GMAIL_USER and GMAIL_APP_PASSWORD must be set.")
        print("\nSetup:")
        print("  export GMAIL_USER='your-email@yourdomain.com'")
        print("  export GMAIL_APP_PASSWORD='your-16-char-app-password'")
        sys.exit(1)

    return gmail_user, gmail_password
