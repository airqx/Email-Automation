# Email Reminder Script for Arabic Events

Production-ready Python script for sending event reminder emails with Arabic content to guests using Gmail.

## Project Structure

```
email/
├── send_reminders.py          # Entry point - run this file
├── config.json                # Your settings (event name, date, etc.)
├── message_template.txt       # Your email message (edit this!)
├── files/
│   └── guests.xlsx            # Your guest list (Excel file)
├── requirements.txt           # Python dependencies
├── send_log.csv               # Auto-generated log after sending
├── README.md                  # This file
└── core/                      # Internal modules (do not edit unless you know what you're doing)
    ├── __init__.py             # Package definition
    ├── config.py               # Config loading and CLI argument parsing
    ├── validators.py           # Email validation and file checks
    ├── data_loader.py          # Excel file reading and column detection
    ├── template_loader.py      # Template file reading and placeholder replacement
    ├── email_builder.py        # MIME message construction and HTML wrapping
    ├── attachments.py          # File attachment handling
    ├── embedded_image.py       # Inline image embedding (CID)
    ├── sender.py               # SMTP connection, retry logic, email sending
    └── logger.py               # CSV send-log utilities
```

**What you need to edit:**
- `config.json` - Your event settings
- `message_template.txt` - Your email message
- `files/guests.xlsx` - Your guest list

**What you run:**
- `python3 send_reminders.py` - Sends emails
- `python3 send_reminders.py --dry-run` - Test without sending

## Quick Start (Step by Step)

Follow these steps in order. If you're new, don't skip any step.

### Step 1: Install Python

Make sure Python 3 is installed on your Mac. Open **Terminal** and run:

```bash
python3 --version
```

If you see a version number (e.g., `Python 3.11.5`), you're good. If not, install it from https://www.python.org/downloads/

### Step 2: Open the Project Folder

Open **Terminal** and navigate to the project folder:

```bash
cd "/path/to/email"
```

Replace `/path/to/email` with the actual path to this project folder.

### Step 3: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated:

```bash
python3 -m venv .venv
```

### Step 4: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of your terminal line. This means the virtual environment is active.

**Important:** You need to activate the virtual environment every time you open a new terminal to run this script.

To deactivate later (when you're done):

```bash
deactivate
```

### Step 5: Install Dependencies

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

### Step 6: Create a Google App Password

You need a special App Password (NOT your regular Gmail password) to send emails.

1. **Enable 2-Step Verification** (required first):
   - Go to https://myaccount.google.com/
   - Click **Security** (left sidebar)
   - Find **2-Step Verification** and turn it ON
   - Follow Google's steps to set it up

2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Sign in if asked
   - Enter a name like "Email Script"
   - Click **Create**
   - Google will show you a 16-character password like: `xwzb evuw lwan ipiz`
   - **Copy this password** - you won't see it again!

### Step 7: Set Environment Variables

Environment variables store your Gmail credentials securely outside the code.

**For macOS/Linux (zsh or bash):**

Run these commands in Terminal (replace with your actual email and app password):

```bash
echo 'export GMAIL_USER="your-email@gmail.com"' >> ~/.zshrc
echo 'export GMAIL_APP_PASSWORD="xwzb evuw lwan ipiz"' >> ~/.zshrc
source ~/.zshrc
```

**Verify they are set:**

```bash
echo $GMAIL_USER
echo $GMAIL_APP_PASSWORD
```

Both should print your email and password. If they are empty, try closing and reopening Terminal.

**Important notes:**
- Replace `your-email@gmail.com` with your actual Gmail address
- Replace the password with your actual App Password from Step 6
- The App Password can include spaces (as Google provides it)
- You only need to do this ONCE - it persists across terminal sessions
- If using bash instead of zsh, replace `~/.zshrc` with `~/.bash_profile`

### Step 8: Edit config.json (Your Event Settings)

Open `config.json` and fill in your event details:

```json
{
   "file": "files/guests.xlsx",
    "event_name": "ورشة العمل",
    "event_date": "15 فبراير 2026",
    "from_name": "فريق الفعالية",
    "reply_to": "",
    "subject": "",
    "template": "message_template.txt",
    "html": false,
    "embedded_image": "",
    "attachments": [],
    "batch_size": 25,
    "batch_sleep_seconds": 1800,
    "min_delay": 8.0,
    "max_delay": 15.0
}
```

**What each setting does:**

| Setting | What it does | Example |
|---------|-------------|---------|
| `file` | Path to your guest list Excel file | `"files/guests.xlsx"` |
| `event_name` | Your event's name (Arabic) | `"ورشة العمل"` |
| `event_date` | Your event's date (Arabic) | `"15 فبراير 2026"` |
| `from_name` | Sender name shown in the email | `"فريق الفعالية"` |
| `reply_to` | Reply-to address (empty = your Gmail) | `""` or `"team@example.com"` |
| `subject` | Custom subject (empty = auto-generated) | `""` or `"دعوة لحضور..."` |
| `template` | Path to your message template file | `"message_template.txt"` |
| `html` | Email format: `true` = styled HTML, `false` = plain text | `false` |
| `embedded_image` | Image to show inside the email body (HTML mode only) | `""` or `"poster.jpg"` |
| `attachments` | Files to attach to the email (downloadable) | `[]` or `["flyer.pdf"]` |
| `batch_size` | How many emails per batch | `25` |
| `batch_sleep_seconds` | Pause between batches (in seconds) | `1800` (30 min) |
| `min_delay` | Minimum wait between emails (seconds) | `8.0` |
| `max_delay` | Maximum wait between emails (seconds) | `15.0` |

### Step 9: Prepare Your Guest List (Excel File)

Create or edit `files/guests.xlsx` with at least two columns:

| Email | name |
|-------|------|
| guest1@gmail.com | Ahmed |
| guest2@gmail.com | Sara |

**Column naming rules:**
- The script auto-detects columns named: `email`, `e-mail`, `mail`, `البريد`, `البريد الإلكتروني`
- For names: `name`, `full name`, `first name`, `الاسم`, `اسم`
- If your columns have different names, the script will ask you to select them

### Step 10: Write Your Email Message

Edit `message_template.txt` with the message you want to send. This is the **only** place where the email content is defined - nothing is hardcoded in the code.

Example:
```
مرحبًا {name}،

نذكركم بموعد الفعالية القادمة:

📅 {event_name}
🗓️ التاريخ: {event_date}

نتطلع لرؤيتكم معنا!

تحياتنا،
فريق التنظيم

---
إذا رغبت بعدم استلام هذه الرسائل، يرجى الرد بكلمة (إيقاف).
```

**Available placeholders:**
- `{name}` - Gets replaced with each guest's name
- `{event_name}` - Gets replaced with the event name from config.json
- `{event_date}` - Gets replaced with the event date from config.json

The script automatically wraps your text in a styled HTML email with a purple gradient header and RTL layout.

### Step 11: Test with Dry Run

**Always test first!** A dry run shows you what would be sent without actually sending anything:

```bash
source .venv/bin/activate
python3 send_reminders.py --dry-run
```

Check the output to make sure:
- The correct recipients are listed
- The email body looks right
- The event name and date are correct

### Step 12: Send Emails for Real

When you're ready to send:

```bash
source .venv/bin/activate
python3 send_reminders.py
```

The script will:
1. Show you a summary of what will be sent
2. Ask you to type `SEND` to confirm
3. Send emails one by one with progress updates
4. Show a final summary when done

## Email Format: Plain Text vs HTML

You can choose between two email formats using the `"html"` setting in `config.json`:

### Plain text (`"html": false`)

The email is sent as simple plain text - exactly what you wrote in `message_template.txt`, with no styling or formatting. The recipient sees the raw text in their inbox.

- No colors, no gradient header, no special layout
- The embedded image will **not** appear inside the email body (it is ignored)
- File attachments still work normally (recipients can download them)

### HTML (`"html": true`)

The email is wrapped in a styled HTML template with:

- A purple gradient header at the top
- White card layout with rounded corners
- Right-to-left (RTL) Arabic text direction
- Professional font and spacing

When HTML is enabled and you set an `embedded_image`, the image appears **at the top of the email body**, centered above your message text. The recipient sees the image inline (not as a download) - it is displayed directly inside the email like a banner or poster.

### Switching between formats

In `config.json`:
```json
"html": false
```
Change to `true` or `false` as needed.

Or via command line (overrides config.json):
```bash
python3 send_reminders.py --no-html
```

## Adding Images and Attachments

### Embedded Image (displayed inside the email body - HTML mode only)

The embedded image appears **at the top of the email**, centered above your message text. It is shown inline as part of the email content - the recipient sees it directly without needing to download anything. Think of it like a banner or event poster at the top of the email.

**Important:** Embedded images only work when `"html"` is set to `true`. In plain text mode, the embedded image is ignored.

To use it:

1. Set `"html": true` in `config.json`
2. Set the image path in `config.json`:
   ```json
   "html": true,
   "embedded_image": "poster.jpg"
   ```

You can use a full path or a relative path:
```json
"embedded_image": "/Users/you/Desktop/event_poster.png"
```

Supported formats: PNG, JPG, GIF, and other standard image types.

### File Attachments (downloadable files)

Attachments are files that the recipient can **download** from the email. They appear as downloadable files at the bottom of the email (like when you attach a file in Gmail). Attachments work in both plain text and HTML modes.

To use them:

1. Set them in `config.json`:
   ```json
   "attachments": ["schedule.pdf", "map.png"]
   ```

### Using both together

You can use an embedded image AND file attachments at the same time (requires HTML mode):
```json
"html": true,
"embedded_image": "event_banner.jpg",
"attachments": ["schedule.pdf", "directions.pdf"]
```

The recipient will see:
1. The banner image at the top of the email (inline)
2. Your message text below it
3. The PDF files as downloadable attachments

## Command-Line Overrides

All settings from `config.json` can be overridden with command-line arguments:

```bash
# Override event name and date
python3 send_reminders.py --event-name "المؤتمر السنوي" --event-date "20 مارس"

# Use a different guest file
python3 send_reminders.py --file files/other_guests.xlsx

# Use a different template
python3 send_reminders.py --template my_other_message.txt

# Add attachments via command line
python3 send_reminders.py --attachments flyer.pdf schedule.pdf
```

**Full argument list:**

| Argument | Description | Default |
|----------|-------------|---------|
| `--file` | Path to Excel file | `From config.json (default: files/guests.xlsx)` |
| `--sheet` | Sheet name in Excel | First sheet |
| `--email-col` | Email column name | Auto-detected |
| `--name-col` | Name column name | Auto-detected |
| `--event-name` | Event name (Arabic) | From config.json |
| `--event-date` | Event date (Arabic) | From config.json |
| `--subject` | Custom email subject | Auto-generated |
| `--from-name` | Sender display name | From config.json |
| `--reply-to` | Reply-to email address | Same as GMAIL_USER |
| `--template` | Path to message template file | `message_template.txt` |
| `--embedded-image` | Image to show inside the email (HTML only) | None |
| `--attachments` | Files to attach to the email | None |
| `--no-html` | Send plain text only (no HTML wrapping) | From config.json |
| `--dry-run` | Test mode (no emails sent) | Off |
| `--batch-size` | Emails per batch | From config.json |
| `--batch-sleep-seconds` | Pause between batches (seconds) | From config.json |
| `--min-delay` | Min delay between emails (seconds) | From config.json |
| `--max-delay` | Max delay between emails (seconds) | From config.json |

## Features

- Reads guest data from Excel (.xlsx) files
- Auto-detects email and name columns (Arabic and English)
- Validates and deduplicates email addresses
- External template file with placeholders - no hardcoded messages
- Two email formats: plain text only, or styled HTML with RTL support
- Embedded images displayed inline at the top of the email (HTML mode)
- File attachments (downloadable) in both plain text and HTML modes
- Rate limiting with batches and random delays to avoid spam flags
- Retry logic for transient errors (3 retries with exponential backoff)
- CSV logging for all operations (`send_log.csv`)
- Dry-run mode for testing
- Confirmation prompt before sending (must type "SEND")
- Clean modular codebase split into separate files by responsibility

## Logging

After sending, a `send_log.csv` file is created with details:

| timestamp | email | name | status | error_message |
|-----------|-------|------|--------|---------------|
| 2026-01-30T10:30:00 | guest@example.com | Ahmed | SENT | |
| 2026-01-30T10:30:05 | bad-email | | SKIPPED_INVALID | Invalid email format |
| 2026-01-30T10:30:10 | guest@example.com | Ahmed | SKIPPED_DUPLICATE | Duplicate email |

**Status values:**
- `SENT` - Email sent successfully
- `FAILED` - Failed to send after retries
- `SKIPPED_INVALID` - Invalid email format
- `SKIPPED_DUPLICATE` - Duplicate email address

## Troubleshooting

### "Environment variables GMAIL_USER and GMAIL_APP_PASSWORD must be set"

You haven't set your credentials. Go back to **Step 7** and set the environment variables. Make sure to run `source ~/.zshrc` after setting them, or open a new terminal.

### "Username and Password not accepted"

Your email or App Password is wrong. Check:
1. Is the email address correct? (check for typos like `gamil.com` instead of `gmail.com`)
2. Did you use an **App Password** (not your regular Gmail password)?
3. Is **2-Step Verification** turned ON in your Google account?
4. Generate a new App Password and try again (Step 6)

### "Connection unexpectedly closed: timed out"

The script can't reach Gmail's server. Check:
1. Is your internet connection working?
2. Are you behind a VPN or firewall blocking port 587?
3. Try a different network (e.g., phone hotspot)

### "openpyxl is not installed" or "ModuleNotFoundError"

You forgot to activate the virtual environment or install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Could not auto-detect email column"

Your Excel column names don't match the expected keywords. Either:
1. Rename your columns to `Email` and `name`
2. Or specify them manually: `--email-col "your column" --name-col "your column"`

### "Template file not found"

Make sure:
1. `message_template.txt` exists in the same folder as `send_reminders.py`
2. The file name in `config.json` matches the actual file name
3. The file uses UTF-8 encoding
4. Placeholders are exactly: `{name}`, `{event_name}`, `{event_date}`

## Rate Limiting & Gmail Limits

To avoid spam filters:
- **Gmail daily limit**: ~500 emails/day (personal) or ~2000 (Workspace)
- **Default batch size**: 25 emails per batch
- **Batch delay**: 30 minutes between batches
- **Email delay**: Random 8-15 seconds between individual emails

You can adjust these in `config.json`:

```json
"batch_size": 25,
"batch_sleep_seconds": 1800,
"min_delay": 8.0,
"max_delay": 15.0
```

Or via command line:

```bash
# Safer (slower)
python3 send_reminders.py --batch-size 15 --batch-sleep-seconds 2400

# Faster (riskier)
python3 send_reminders.py --batch-size 50 --batch-sleep-seconds 900
```

## Security Notes

- **NEVER** put your App Password in code files or share it
- **NEVER** commit `~/.zshrc` or `.env` files to Git
- Store credentials only in environment variables
- Regularly rotate your App Passwords at https://myaccount.google.com/apppasswords
- Delete unused App Passwords from your Google account
- The `send_log.csv` contains email addresses - keep it secure
