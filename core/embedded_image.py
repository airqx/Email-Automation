"""
Embedded (inline) image handling for email messages.

Creates MIME image parts with Content-ID headers so they can be
referenced in HTML via cid:embedded_image.
"""

import mimetypes
import os
from email.mime.image import MIMEImage
from typing import Optional


def create_embedded_image_part(image_path: str) -> Optional[MIMEImage]:
    """
    Create a MIME image part for inline embedding in an HTML email.

    The image is assigned Content-ID '<embedded_image>' so it can be
    referenced in HTML as: <img src="cid:embedded_image">

    Parameters:
        image_path (str): Path to the image file (PNG, JPG, GIF, etc.).

    Returns:
        Optional[MIMEImage]: The MIME image part with CID header set,
            or None if the file does not exist.
    """
    if not image_path or not os.path.isfile(image_path):
        return None

    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()

    img_type = mimetypes.guess_type(image_path)[0] or 'image/png'
    img_subtype = img_type.split('/')[1]

    part = MIMEImage(img_data, _subtype=img_subtype)
    part.add_header('Content-ID', '<embedded_image>')
    part.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
    return part
