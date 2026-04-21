"""
MIME message construction and HTML wrapping.

Builds multipart email messages with plain text and styled HTML versions.
Integrates embedded images and file attachments from their respective modules.
"""

import os
import re
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from core.template_loader import read_template
from core.embedded_image import create_embedded_image_part
from core.attachments import create_attachment_part, attachment_exists, normalize_attachment_path


def wrap_in_html(
    plain_text: str,
    has_embedded_image: bool = False,
    has_logo: bool = False
) -> str:
    """
    Convert plain text content into a styled, RTL-compatible HTML email.
    """

    lines = plain_text.strip().split('\n')
    html_body = ''

    if has_embedded_image:
        html_body += (
            '<div style="text-align: center; margin-bottom: 20px;">'
            '<img src="cid:embedded_image" style="max-width: 100%; height: auto; border-radius: 8px;">'
            '</div>'
        )

    for line in lines:
        stripped = line.strip()

        if stripped == '':
            html_body += '<br>\n'

        elif stripped == '---':
            html_body += '<hr style="border:none;border-top:1px solid #2a7d6b;opacity:0.3;margin:20px 0;">\n'

        else:
            formatted_line = re.sub(r'\*([^*]+)\*', r'<strong>\1</strong>', line)
            html_body += f'<p style="margin:5px 0;">{formatted_line}</p>\n'

    if has_logo:
        logo_html = '<img src="cid:logo_image" style="width:100%;height:auto;display:block;">'
    else:
        logo_html = '<span style="font-size:22px;font-weight:bold;">وحدة العمل التطوعي</span>'

    return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="font-family:'Segoe UI',Tahoma,Verdana;direction:rtl;text-align:right;background:#e8f5f1;margin:0;padding:0;">

<div style="max-width:600px;margin:20px auto;background:white;border-radius:10px;box-shadow:0 2px 12px rgba(26,107,90,0.15);overflow:hidden;">

<div style="text-align:center;line-height:0;">
{logo_html}
</div>

<div style="border-top:4px solid #c8a951;padding:30px 25px;line-height:1.9;color:#2c3e2e;font-size:15px;">
{html_body}
</div>

<div style="background:#f0f9f6;padding:15px 25px;text-align:center;border-top:1px solid #d4ece5;">
<p style="margin:0;font-size:12px;color:#5a8a7d;">وحدة العمل التطوعي • Voluntary Work Unit</p>
</div>

</div>
</body>
</html>
"""


def _create_logo_part(logo_path: str) -> Optional[MIMEImage]:

    import mimetypes

    if not logo_path:
        return None

    normalized_logo_path = normalize_attachment_path(logo_path)

    if not os.path.isfile(normalized_logo_path):
        return None

    with open(normalized_logo_path, 'rb') as f:
        img_data = f.read()

    img_type = mimetypes.guess_type(normalized_logo_path)[0] or 'image/png'
    img_subtype = img_type.split('/')[1]

    part = MIMEImage(img_data, _subtype=img_subtype)
    part.add_header('Content-ID', '<logo_image>')
    part.add_header('Content-Disposition', 'inline', filename=os.path.basename(normalized_logo_path))

    return part


def build_message(
    from_email: str,
    from_name: str,
    reply_to: str,
    to_email: str,
    subject: str,
    text_body: str,
    embedded_image_path: Optional[str] = None,
    attachment_paths: Optional[List[str]] = None,
    plain_text_only: bool = False,
    logo_path: Optional[str] = None,
) -> MIMEMultipart:

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = to_email
    msg['Reply-To'] = reply_to

    valid_attachment_paths: List[str] = []

    if attachment_paths:
        for file_path in attachment_paths:

            if not file_path:
                continue

            normalized_path = normalize_attachment_path(file_path)

            if attachment_exists(normalized_path):
                valid_attachment_paths.append(normalized_path)

    if plain_text_only:

        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))

    else:

        logo_part = _create_logo_part(logo_path) if logo_path else None
        has_logo = logo_part is not None

        embedded_img_part = None
        has_embedded = False

        if embedded_image_path:
            embedded_img_part = create_embedded_image_part(embedded_image_path)
            has_embedded = embedded_img_part is not None

        html_body = wrap_in_html(
            text_body,
            has_embedded_image=has_embedded,
            has_logo=has_logo
        )

        if has_logo or has_embedded:

            msg_related = MIMEMultipart('related')

            msg_alt = MIMEMultipart('alternative')
            msg_alt.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg_alt.attach(MIMEText(html_body, 'html', 'utf-8'))

            msg_related.attach(msg_alt)

            if logo_part:
                msg_related.attach(logo_part)

            if embedded_img_part:
                msg_related.attach(embedded_img_part)

            msg.attach(msg_related)

        else:

            msg_alt = MIMEMultipart('alternative')
            msg_alt.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg_alt.attach(MIMEText(html_body, 'html', 'utf-8'))

            msg.attach(msg_alt)

    if valid_attachment_paths:

        for file_path in valid_attachment_paths:

            att_part = create_attachment_part(file_path)

            if att_part:
                msg.attach(att_part)

    return msg