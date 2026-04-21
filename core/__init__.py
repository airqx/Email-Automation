"""
Core modules for the email reminder script.

This package contains all business logic split by responsibility:
    config          - Configuration loading (config.json + CLI args)
    validators      - Email format and file existence validation
    data_loader     - Excel file reading and column detection
    template_loader - Template file reading and placeholder replacement
    email_builder   - MIME message construction and HTML wrapping
    attachments     - File attachment MIME part creation
    embedded_image  - Inline image embedding via CID
    sender          - SMTP connection, retry logic, and batch sending
    logger          - CSV send-log utilities
"""
