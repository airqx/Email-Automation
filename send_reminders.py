#!/usr/bin/env python3
"""
Entry point for the email reminder script.

All email message content is loaded exclusively from an external template file
(message_template.txt). No message text is hardcoded in this script.
"""

import os
import sys
import time
from datetime import datetime
from random import uniform

from core.config import load_config, parse_args, get_gmail_credentials
from core.validators import validate_email, validate_file_exists, validate_attachments
from core.data_loader import (
    read_data_file, detect_column, get_column_interactive,
    EMAIL_KEYWORDS, NAME_KEYWORDS, ATTACHMENT_PATH_KEYWORDS
)
from core.template_loader import read_template
from core.sender import connect_smtp, send_single_email
from core.logger import log_result


def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config(script_dir)
    args = parse_args(config)

    if not args.event_name or not args.event_date:
        print("ERROR: event_name and event_date are required.")
        sys.exit(1)

    gmail_user, gmail_password = get_gmail_credentials()

    validate_file_exists(args.template, "Template file")

    if args.logo:
        validate_file_exists(args.logo, "Logo image file")

    if args.embedded_image:
        validate_file_exists(args.embedded_image, "Embedded image file")

    validate_attachments(args.attachments)

    reply_to = args.reply_to or gmail_user
    subject = args.subject if args.subject else f" {args.event_name} – {args.event_date}"

    print("=" * 70)
    print("📧 Email Reminder Script")
    print("=" * 70)
    print(f"File: {args.file}")
    print(f"Event: {args.event_name}")
    print(f"Date: {args.event_date}")
    print(f"Subject: {subject}")
    print("=" * 70)

    print("\n📂 Reading data file...")
    headers, data = read_data_file(args.file, args.sheet)
    print(f"✓ Found {len(data)} rows")

    # EMAIL COLUMN
    email_col = detect_column(headers, EMAIL_KEYWORDS)
    if not email_col:
        print("⚠️ Could not auto detect email column")
        email_col = get_column_interactive(headers, "EMAIL")

    # NAME COLUMN
    name_col = detect_column(headers, NAME_KEYWORDS)
    if not name_col:
        print("⚠️ Could not auto detect name column")
        name_col = get_column_interactive(headers, "NAME")

    # ATTACHMENT COLUMN (NEW)
    attachment_col = detect_column(headers, ATTACHMENT_PATH_KEYWORDS)

    print("\n✓ Using columns:")
    print(f"Email: {email_col}")
    print(f"Name: {name_col}")
    if attachment_col:
        print(f"Attachment: {attachment_col}")
    else:
        print("Attachment: (none detected, using global attachments only)")

    print("\n🔍 Processing recipients...")

    recipients = []
    seen_emails = set()

    skipped_invalid = 0
    skipped_duplicate = 0

    for row in data:

        email = row.get(email_col, "").strip().lower()
        name = row.get(name_col, "").strip()

        if not email:
            continue

        if not validate_email(email):
            skipped_invalid += 1
            continue

        if email in seen_emails:
            skipped_duplicate += 1
            continue

        seen_emails.add(email)

        attachment_paths = []

         # PER EMAIL ATTACHMENT
        if attachment_col:
            row_attachment = row.get(attachment_col, "").strip()
            if row_attachment:
                attachment_paths = [p.strip() for p in row_attachment.split(";") if p.strip()]

        # FALLBACK GLOBAL ATTACHMENTS
        if not attachment_paths and args.attachments:
            attachment_paths = args.attachments

        recipients.append({
            "email": email,
            "name": name,
            "attachments": attachment_paths
        })

    print(f"✓ Valid recipients: {len(recipients)}")

    if len(recipients) == 0:
        print("No valid recipients found")
        sys.exit(0)

    if args.dry_run:

        print("\nDRY RUN PREVIEW\n")

        for r in recipients[:5]:
            print(r["email"], r["attachments"])

        sys.exit(0)

    num_batches = (len(recipients) + args.batch_size - 1) // args.batch_size

    print("\nStarting send process...\n")

    sent_count = 0
    failed_count = 0

    try:

        smtp_server = connect_smtp(gmail_user, gmail_password)

        for batch_num in range(num_batches):

            batch_start = batch_num * args.batch_size
            batch_end = min(batch_start + args.batch_size, len(recipients))

            batch = recipients[batch_start:batch_end]

            print(f"\nBatch {batch_num + 1}/{num_batches}")

            for i, recipient in enumerate(batch, 1):

                email = recipient["email"]
                name = recipient["name"]
                attachments = recipient["attachments"]

                success, smtp_server, error_msg = send_single_email(

                    smtp_server,
                    gmail_user,
                    args.from_name,
                    reply_to,
                    email,
                    name,
                    subject,
                    args.event_name,
                    args.event_date,
                    args.template,
                    args.embedded_image,
                    attachments,
                    plain_text_only=args.no_html,
                    logo_path=args.logo,
                    gmail_user=gmail_user,
                    gmail_password=gmail_password,
                )

                timestamp = datetime.now().isoformat()

                if success:
                    sent_count += 1
                    print(f"✓ {email}")
                    log_result(timestamp, email, name, "SENT")
                else:
                    failed_count += 1
                    print(f"✗ {email} ERROR: {error_msg}")
                    log_result(timestamp, email, name, "FAILED", error_msg)

                delay = uniform(args.min_delay, args.max_delay)
                time.sleep(delay)

            if batch_num < num_batches - 1:
                time.sleep(args.batch_sleep_seconds)

        smtp_server.quit()

    except Exception as e:

        print("CRITICAL ERROR:", e)
        sys.exit(1)

    print("\nFINAL SUMMARY")
    print(f"Sent: {sent_count}")
    print(f"Failed: {failed_count}")
    print("Done.")


if __name__ == "__main__":
    main()