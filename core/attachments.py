"""
File attachment handling for email messages.

Creates MIME parts for files to be attached to emails.
Validates file existence and determines MIME type automatically.
"""

import mimetypes
import os
from email import encoders
from email.mime.base import MIMEBase
from typing import Optional


def normalize_attachment_path(file_path: str) -> str:
    """
    Normalize an attachment path.

    Expands user home shortcuts and returns a normalized path string.

    Parameters:
        file_path (str): Raw file path.

    Returns:
        str: Normalized file path.
    """
    return os.path.normpath(os.path.expanduser(file_path.strip()))


def attachment_exists(file_path: str) -> bool:
    """
    Check whether an attachment file exists on disk.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        bool: True if the file exists and is a regular file, otherwise False.
    """
    if not file_path:
        return False

    normalized_path = normalize_attachment_path(file_path)
    return os.path.isfile(normalized_path)


def create_attachment_part(file_path: str) -> Optional[MIMEBase]:
    """
    Create a MIME attachment part from a file on disk.

    Reads the file, determines its MIME type, encodes it in base64,
    and sets the Content-Disposition header for download.

    Parameters:
        file_path (str): Path to the file to attach.

    Returns:
        Optional[MIMEBase]: The MIME part ready to attach to a message,
            or None if the file does not exist.
    """
    if not file_path:
        return None

    normalized_path = normalize_attachment_path(file_path)

    if not os.path.isfile(normalized_path):
        return None

    mime_type = mimetypes.guess_type(normalized_path)[0] or 'application/octet-stream'
    main_type, sub_type = mime_type.split('/', 1)

    with open(normalized_path, 'rb') as f:
        file_data = f.read()

    part = MIMEBase(main_type, sub_type)
    part.set_payload(file_data)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        'attachment',
        filename=os.path.basename(normalized_path)
    )
    return part