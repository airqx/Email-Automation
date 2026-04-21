"""
Template file loading and placeholder replacement.

All email message content is read exclusively from an external file.
No message text is hardcoded anywhere in this codebase.
"""

import os
import sys


def read_template(name: str, event_name: str, event_date: str, template_file: str) -> str:
    """
    Read the message body from an external template file and replace placeholders.

    The template file must exist and contain the complete email message.
    No fallback or default message is provided by the code.

    Supported placeholders:
        {name}       - Replaced with the recipient's name (empty string if absent).
        {event_name} - Replaced with the event name.
        {event_date} - Replaced with the event date.

    Parameters:
        name (str): The recipient's name.
        event_name (str): The name of the event.
        event_date (str): The date of the event.
        template_file (str): Path to the template text file.

    Returns:
        str: The message body with all placeholders replaced.

    Side effects:
        Exits the program if the template file is missing or unreadable.
    """
    if not template_file or not os.path.isfile(template_file):
        print(f"ERROR: Template file '{template_file}' not found.")
        print("Please create a message_template.txt file with your email message.")
        print("Use {name}, {event_name}, and {event_date} as placeholders.")
        sys.exit(1)

    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"ERROR: Could not read template file '{template_file}': {e}")
        sys.exit(1)

    body = template.replace('{name}', name if name else '')
    body = body.replace('{event_name}', event_name)
    body = body.replace('{event_date}', event_date)
    return body
