# The Closer -- Cold Email Writer + Send Bot

A CLI tool for job seekers to generate and send personalized cold outreach emails.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment config
cp .env.example .env

# 3. Run with demo contacts (dry run -- safe)
python main.py
```

## Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password:** https://myaccount.google.com/apppasswords
3. **Fill in `.env`:**
   - `SMTP_USER`: your Gmail address
   - `SMTP_PASSWORD`: the 16-character app password
   - `SENDER_NAME`: your name

## Usage

```bash
# Run with demo contacts (dry run -- safe)
python main.py

# Load contacts from a JSON file
python main.py --file contacts.json

# Load from CSV
python main.py --file jobs.csv

# Actually send emails (set up .env first!)
python main.py --send

# View the outreach log
python main.py --log
```

### Interactive Actions

During the email preview, you can choose:

- **`[s] Send / Draft`** -- Proceed with sending (or logging in dry-run mode)
- **`[k] Skip`** -- Skip this contact and move to the next
- **`[e] Edit email`** -- Edit the subject and body before sending
- **`[q] Quit`** -- Stop processing and show summary

When sending for real (not dry-run), you will be asked to confirm with `yes/no`.

## Features

- Load contacts from JSON, CSV, or built-in demo contacts
- Generate personalized cold emails using templates
- Preview emails before sending with word count display
- Edit emails before sending (subject + body)
- Send via SMTP (Gmail App Passwords)
- Dry-run mode (safe by default -- no emails actually sent)
- Safety confirmation for real sends
- Opt-out management (respect recipient preferences)
- Detailed CSV logging with summary view
- 59 automated tests with pytest

## Project Structure

```
├── main.py          # Entry point / orchestrator
├── models.py        # Data classes (Contact, Email, etc.)
├── config.py        # Configuration & env vars
├── loader.py        # Contact loading (JSON, CSV, demo)
├── generator.py     # Email generation with templates
├── preview.py       # Preview, confirmation, email editing
├── sender.py        # Email sending (SMTP strategy pattern)
├── logger.py        # CSV logging
├── opt_out.py       # Opt-out management
├── templates/       # Email template files
│   └── default.txt  # Default cold email template
├── contacts.json    # Sample contacts file for demo
├── .env.example     # Environment variable template
├── requirements.txt # Python dependencies
├── docs/            # Documentation
└── tests/           # Test suite
    ├── test_models.py
    ├── test_config.py
    ├── test_loader.py
    ├── test_generator.py
    ├── test_logger.py
    ├── test_sender.py
    └── test_integration.py
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_generator.py -v

# Run with coverage report
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

## Architecture

See `docs/` for detailed documentation:

- `docs/problemStatement.md` -- Original problem statement
- `docs/implementation-plan.md` -- Phase-by-phase implementation plan

The application follows a simple pipeline architecture:

```
Load Contacts -> Generate Emails -> Preview -> Confirm -> Send (or Dry-Run) -> Log
```

Each phase is implemented as an independent module with its own test file.
