"""
SMTP connection management, retry logic, and batch email sending.
"""

import smtplib
import time
from typing import List, Optional, Tuple

from core.template_loader import read_template
from core.email_builder import build_message
from core.attachments import normalize_attachment_path


def connect_smtp(gmail_user: str, gmail_password: str) -> smtplib.SMTP:
    """
    Establish an authenticated SMTP connection to Gmail with TLS.

    Parameters:
        gmail_user (str): Gmail email address.
        gmail_password (str): Gmail App Password.

    Returns:
        smtplib.SMTP: An authenticated, ready-to-send SMTP connection.

    Raises:
        Exception: If connection or authentication fails.
    """
    print("\n🔌 Connecting to Gmail SMTP...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_user, gmail_password)
    print("✓ Connected and authenticated")
    return server


def send_single_email(
    smtp_server: smtplib.SMTP,
    from_email: str,
    from_name: str,
    reply_to: str,
    to_email: str,
    name: str,
    subject: str,
    event_name: str,
    event_date: str,
    template_file: str,
    embedded_image: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    max_retries: int = 3,
    plain_text_only: bool = False,
    logo_path: Optional[str] = None,
    gmail_user: Optional[str] = None,
    gmail_password: Optional[str] = None,
) -> Tuple[bool, smtplib.SMTP, str]:
    """
    Send an email to a single recipient with automatic retry on transient errors.

    Reads the template, builds the MIME message (with optional image/attachments),
    and sends it. On transient SMTP errors, retries up to max_retries times
    with exponential backoff (2s, 4s, 8s). Reconnects to SMTP if connection is lost.

    Parameters:
        smtp_server (smtplib.SMTP): An authenticated SMTP connection.
        from_email (str): Sender email address.
        from_name (str): Sender display name.
        reply_to (str): Reply-To address.
        to_email (str): Recipient email address.
        name (str): Recipient name (for template personalization).
        subject (str): Email subject line.
        event_name (str): Event name (for template placeholder).
        event_date (str): Event date (for template placeholder).
        template_file (str): Path to the message template file.
        embedded_image (Optional[str]): Path to image to embed inline.
        attachments (Optional[List[str]]): Paths to files to attach for this specific email.
        max_retries (int): Max retry attempts for transient errors.
        plain_text_only (bool): If True, send plain text only (no HTML).
        logo_path (Optional[str]): Path to logo image for the email header.
        gmail_user (Optional[str]): Gmail user for reconnection if needed.
        gmail_password (Optional[str]): Gmail password for reconnection if needed.

    Returns:
        Tuple[bool, smtplib.SMTP, str]: (success, smtp_server, error_message).
    """
    normalized_attachments: List[str] = []
    if attachments:
        normalized_attachments = [
            normalize_attachment_path(path)
            for path in attachments
            if path and str(path).strip()
        ]

    for attempt in range(1, max_retries + 1):
        try:
            text_body = read_template(name, event_name, event_date, template_file)

            msg = build_message(
                from_email=from_email,
                from_name=from_name,
                reply_to=reply_to,
                to_email=to_email,
                subject=subject,
                text_body=text_body,
                embedded_image_path=embedded_image,
                attachment_paths=normalized_attachments,
                plain_text_only=plain_text_only,
                logo_path=logo_path,
            )

            smtp_server.send_message(msg)
            return True, smtp_server, ""

        except (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            smtplib.SMTPHeloError,
            ConnectionError
        ) as e:
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(
                    f"  ⚠️  Connection error for {to_email}, reconnecting in {wait_time}s... "
                    f"(attempt {attempt}/{max_retries})"
                )
                time.sleep(wait_time)

                if gmail_user and gmail_password:
                    try:
                        smtp_server.quit()
                    except Exception:
                        pass

                    try:
                        print("  🔄 Reconnecting to SMTP...")
                        smtp_server = connect_smtp(gmail_user, gmail_password)
                    except Exception as reconnect_error:
                        if attempt == max_retries:
                            return False, smtp_server, f"Failed to reconnect: {str(reconnect_error)}"
                continue
            else:
                return False, smtp_server, f"Failed after {max_retries} retries: {str(e)}"

        except Exception as e:
            return False, smtp_server, str(e)

    return False, smtp_server, "Unknown error"