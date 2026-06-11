# The Closer — Phase-Wise Implementation Plan

> **Cold Email Writer + Send Bot** | Sprint 3 Implementation Guide
> Based on: `docs/problemStatement.md` + `docs/architecture.md`

---

## Table of Contents

1. [Overview & Dependency Map](#1-overview--dependency-map)
2. [Phase 0: Project Scaffolding](#2-phase-0-project-scaffolding)
3. [Phase 1: Core Data Layer](#3-phase-1-core-data-layer)
4. [Phase 2: Email Generator](#4-phase-2-email-generator)
5. [Phase 3: Preview & User Confirmation](#5-phase-3-preview--user-confirmation)
6. [Phase 4: Logger](#6-phase-4-logger)
7. [Phase 5: Orchestrator & Dry-Run Pipeline](#7-phase-5-orchestrator--dry-run-pipeline)
8. [Phase 6: Real Email Sending (SMTP)](#8-phase-6-real-email-sending-smtp)
9. [Phase 7: Polish & Safety](#9-phase-7-polish--safety)
10. [Phase 8: Testing Suite](#10-phase-8-testing-suite)
11. [Phase 9: Documentation & Demo Prep](#11-phase-9-documentation--demo-prep)
12. [Phase X: Stretch Goals](#12-phase-x-stretch-goals)
13. [Appendix: Dependency Installation Order](#appendix-dependency-installation-order)

---

## 1. Overview & Dependency Map

### 1.1 Phase Dependency Graph

```
Phase 0: Scaffolding
    │
    ▼
Phase 1: Models + Config + Loader
    │
    ▼
Phase 2: Generator ──────────────────────┐
    │                                     │
    ▼                                     │
Phase 3: Preview Manager ────────────────┤
    │                                     │
    ▼                                     │
Phase 4: Logger ─────────────────────────┤
    │                                     │
    ▼                                     │
Phase 5: Orchestrator & Dry-Run Pipeline ◄┘
    │
    ▼
Phase 6: Real Email Sending (SMTP)
    │
    ▼
Phase 7: Polish & Safety
    │
    ├── Phase 8: Testing Suite (parallel)
    └── Phase 9: Documentation & Demo Prep
```

### 1.2 File Creation Order

Each phase lists exactly which files to create. Files are never revisited across phases — they are completed in the phase they appear.

| Phase | Files Created | Files Modified |
|-------|---------------|----------------|
| 0 | `.env.example`, `.gitignore`, `requirements.txt` | — |
| 1 | `models.py`, `config.py`, `loader.py` | — |
| 2 | `generator.py`, `templates/default.txt` | — |
| 3 | `preview.py` | — |
| 4 | `logger.py` | — |
| 5 | `main.py` | `config.py` (add CLI arg parsing) |
| 6 | `sender.py` | `main.py`, `.env.example` |
| 7 | `opt_out.py` (optional) | `main.py`, `preview.py` |
| 8 | `tests/test_*.py` | — |
| 9 | `README.md` | — |
| X | stretch feature files | varies |

### 1.3 How to Use This Plan

Each phase is designed to be **independently implementable and testable**. Follow this pattern for every phase:

1. **Read** the phase specification below
2. **Implement** the files listed
3. **Test** the phase (manual + automated if tests exist)
4. **Verify** against the phase's Acceptance Criteria
5. **Commit** before moving to the next phase

---

## 2. Phase 0: Project Scaffolding

> **Goal**: Create the project directory structure and foundational config files.
> **Time estimate**: 15 minutes
> **Live demo value**: Sets up the workspace; quick win.

### 2.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 0.1 | Create directory structure | — | `mkdir -p templates tests docs` |
| 0.2 | Create `.env.example` | `.env.example` | All env vars with placeholder values + comments |
| 0.3 | Create `.gitignore` | `.gitignore` | Secrets, logs, cache files |
| 0.4 | Create `requirements.txt` | `requirements.txt` | Only MVP dependencies initially: `python-dotenv` |

### 2.2 File Specifications

#### `.env.example`

```env
# ─── SMTP Configuration ───────────────────────────
# For Gmail: use an App Password (requires 2FA enabled)
# Generate at: https://myaccount.google.com/apppasswords
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# ─── Sender Identity ─────────────────────────────
SENDER_NAME=Your Full Name

# ─── LLM Configuration (Stretch) ────────────────
# Groq API key for LLM-powered email rewriting
# Get one at: https://console.groq.com/keys
# GROQ_API_KEY=gsk_your_api_key_here

# ─── Mode ────────────────────────────────────────
# Set to "true" to log only (safe). Set to "false" to actually send.
DRY_RUN=true

# ─── Data Source ─────────────────────────────────
# Path to contacts file. Leave empty to use built-in demo contacts.
DATA_SOURCE=
```

#### `.gitignore`

```gitignore
# Environment
.env
token.json

# Logs
outreach_log.csv
*.log

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

#### `requirements.txt`

```txt
# Core
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0

# Stretch — uncomment when needed
# groq>=0.10.0
# google-api-python-client>=2.0.0
# google-auth-oauthlib>=1.0.0
# openai>=1.0.0  # Alternative: use OpenAI SDK with Groq base_url
# streamlit>=1.28.0
```

### 2.3 Acceptance Criteria

- [ ] `the-closer/` directory exists with all subdirectories
- [ ] `.env.example` contains all env vars from architecture doc
- [ ] `.gitignore` covers secrets, logs, and cache files
- [ ] `requirements.txt` installs with `pip install -r requirements.txt`
- [ ] `python-dotenv` imports successfully

### 2.4 Demo Script

```bash
# Create project
mkdir -p templates tests docs

# Create files... (copy contents above)

# Install dependencies
pip install -r requirements.txt

# Verify
python -c "from dotenv import load_dotenv; print('dotenv ready')"
```

---

## 3. Phase 1: Core Data Layer

> **Goal**: Define data models, configuration loader, and data loader.
> **Time estimate**: 45 minutes
> **Files**: `models.py`, `config.py`, `loader.py`
> **Dependencies**: Phase 0 (scaffolding)

### 3.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 1.1 | Define data classes | `models.py` | `Contact`, `Email`, `SendResult`, `LogEntry` with field validation |
| 1.2 | Implement config loader | `config.py` | Load `.env`, parse types, validate required fields |
| 1.3 | Implement data loader | `loader.py` | Load from JSON, CSV, or return demo contacts |

### 3.2 File Specifications

#### `models.py` — Complete Content

```python
"""
Data models for The Closer cold email system.
All data classes with field validation."""
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Optional


@dataclass
class Contact:
    """A single outreach target (job listing or contact)."""
    # Required fields
    recipient_email: str
    company: str
    role: str
    candidate_name: str
    candidate_background: str

    # Optional fields
    recipient_name: str = ""
    job_url: str = ""
    personalization_note: str = ""
    portfolio_url: str = ""
    linkedin_url: str = ""
    resume_link: str = ""

    def __post_init__(self):
        """Validate required fields after initialization."""
        errors = []

        if not self.recipient_email or not self._is_valid_email(self.recipient_email):
            errors.append(f"Invalid or missing recipient_email: {self.recipient_email}")
        if not self.company:
            errors.append("company is required")
        if not self.role:
            errors.append("role is required")
        if not self.candidate_name:
            errors.append("candidate_name is required")
        if not self.candidate_background:
            errors.append("candidate_background is required")

        if errors:
            raise ValueError(f"Contact validation failed: {'; '.join(errors)}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def get_recipient_name_or_fallback(self) -> str:
        """Return recipient_name or infer a fallback from email."""
        if self.recipient_name:
            return self.recipient_name
        # Fallback: extract name from email prefix
        name_part = self.recipient_email.split("@")[0]
        # Convert underscores/dots to spaces and capitalize
        return name_part.replace(".", " ").replace("_", " ").title()


@dataclass
class Email:
    """A generated cold email."""
    subject: str
    body: str
    word_count: int
    contact: Contact  # Reference back to source contact

    def is_valid(self) -> bool:
        """Check if email meets basic quality standards."""
        if not self.subject or not self.body:
            return False
        if self.word_count > 150:
            # Allow override but flag it
            return True  # Just a warning, not a blocker
        return True

    def warnings(self) -> list[str]:
        """Return list of quality warnings."""
        warnings_list = []
        if self.word_count > 150:
            warnings_list.append(f"Word count ({self.word_count}) exceeds 150 limit")
        if len(self.subject) < 5:
            warnings_list.append("Subject line is very short")
        return warnings_list


@dataclass
class SendResult:
    """Result of a send/draft attempt."""
    status: str  # "sent", "drafted", "skipped", "failed"
    error: str = ""
    draft_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LogEntry:
    """Persistent log entry for an email action."""
    timestamp: str
    recipient_email: str
    company: str
    role: str
    subject: str
    status: str  # generated, drafted, sent, skipped, failed
    error_message: str = ""
```

#### `config.py` — Complete Content

```python
"""
Configuration management for The Closer.
Loads and validates environment variables from .env file."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os


@dataclass
class Config:
    """Application configuration loaded from environment."""
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Sender
    sender_name: str = ""
    dry_run: bool = True
    send_method: str = "smtp"

    # Data source
    data_source: str = ""

    # Limits
    max_emails_per_run: int = 10
    max_words_per_email: int = 150


def load_config(env_file: str = ".env") -> Config:
    """
    Load configuration from .env file.
    
    Args:
        env_file: Path to .env file (default: ".env")
    
    Returns:
        Config object with loaded values
    
    Raises:
        FileNotFoundError: If .env file doesn't exist (warning only)
        ValueError: If required config values are missing
    """
    env_path = Path(env_file)

    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"  ⚠  .env file not found at {env_file}. Using defaults (DRY_RUN mode).")
        print(f"     Copy .env.example to .env and fill in your settings.")

    config = Config(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        sender_name=os.getenv("SENDER_NAME", ""),
        dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
        send_method=os.getenv("SEND_METHOD", "smtp"),
        data_source=os.getenv("DATA_SOURCE", ""),
        max_emails_per_run=int(os.getenv("MAX_EMAILS_PER_RUN", "10")),
        max_words_per_email=int(os.getenv("MAX_WORDS_PER_EMAIL", "150")),
    )

    return config


def validate_config(config: Config) -> list[str]:
    """
    Validate configuration and return list of errors.
    
    Returns:
        List of error messages (empty if config is valid)
    """
    errors = []

    if config.send_method == "smtp" and not config.dry_run:
        if not config.smtp_user:
            errors.append("SMTP_USER is required when dry_run=false")
        if not config.smtp_password:
            errors.append("SMTP_PASSWORD is required when dry_run=false")
        if not config.sender_name:
            errors.append("SENDER_NAME is required when dry_run=false")

    if config.smtp_port not in (25, 465, 587, 2525):
        errors.append(f"Unusual SMTP port: {config.smtp_port}. Expected 25, 465, 587, or 2525.")

    if config.send_method not in ("smtp", "gmail"):
        errors.append(f"Unknown send_method: {config.send_method}. Expected 'smtp' or 'gmail'.")

    return errors
```

#### `loader.py` — Complete Content

```python
"""
Data loader for The Closer.
Loads outreach targets from JSON, CSV, or hardcoded demo contacts."""

import csv
import json
from pathlib import Path
from typing import List, Optional

from models import Contact


# ─── Demo Contacts ────────────────────────────────────

def get_demo_contacts() -> List[Contact]:
    """
    Return 5 hardcoded demo contacts for live demo / testing.
    These showcase different personalization scenarios."""
    return [
        Contact(
            recipient_email="priya@example.com",
            recipient_name="Priya Sharma",
            company="Acme AI",
            role="Backend Engineering Intern",
            job_url="https://example.com/jobs/acme-backend",
            personalization_note="I was excited to see Acme AI's recent launch of their workflow automation platform — it's impressive.",
            candidate_name="Alex Chen",
            candidate_background="Python developer with experience building automation tools and AI agents",
            portfolio_url="https://github.com/alexchen",
        ),
        Contact(
            recipient_email="james@startup.co",
            recipient_name="James Wilson",
            company="NeuralPath",
            role="ML Engineering Intern",
            job_url="https://example.com/jobs/neuralpath-ml",
            personalization_note="I read about NeuralPath's work on efficient transformers — that's exactly the kind of work I want to contribute to.",
            candidate_name="Alex Chen",
            candidate_background="Machine learning student with projects in NLP and model optimization",
            portfolio_url="https://github.com/alexchen",
            linkedin_url="https://linkedin.com/in/alexchen",
        ),
        Contact(
            recipient_email="sarah@greenenergy.io",
            recipient_name="Sarah Kim",
            company="GreenGrid",
            role="Software Engineering Intern",
            job_url="https://example.com/jobs/greengrid-swe",
            personalization_note="GreenGrid's mission to make renewable energy accessible through smart grids really resonates with me.",
            candidate_name="Alex Chen",
            candidate_background="Full-stack developer with experience in React, Python, and building data pipelines",
            portfolio_url="https://github.com/alexchen",
            resume_link="https://alexchen.dev/resume.pdf",
        ),
        Contact(
            recipient_email="marcus@fintech.com",
            recipient_name="Marcus Johnson",
            company="QuickLedger",
            role="Product Management Intern",
            personalization_note="I've been following QuickLedger's growth in the SMB accounting space — your API-first approach stands out.",
            candidate_name="Alex Chen",
            candidate_background="Computer science student with product sense and experience building user-facing features",
            portfolio_url="https://github.com/alexchen",
        ),
        Contact(
            recipient_email="hello@datavista.io",
            company="DataVista",
            role="Data Engineering Intern",
            personalization_note="DataVista's recent blog post about real-time data pipelines at scale was incredibly insightful.",
            candidate_name="Alex Chen",
            candidate_background="Data engineer with experience in ETL pipelines, SQL, and Python data processing",
            portfolio_url="https://github.com/alexchen",
            linkedin_url="https://linkedin.com/in/alexchen",
        ),
    ]


# ─── File Loaders ─────────────────────────────────────

def load_from_json(path: str) -> List[Contact]:
    """
    Load contacts from a JSON file.
    
    Expected format: array of objects with Contact fields.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of contact objects")

    contacts = []
    errors = []
    for i, item in enumerate(data):
        try:
            contact = Contact(**item)
            contacts.append(contact)
        except (ValueError, TypeError) as e:
            errors.append(f"  Row {i}: {e}")

    if errors:
        print(f"  ⚠  {len(errors)} contact(s) had validation errors:")
        for err in errors:
            print(f"     {err}")

    return contacts


def load_from_csv(path: str) -> List[Contact]:
    """
    Load contacts from a CSV file.
    
    Expected columns: recipient_email, company, role, candidate_name, 
                      candidate_background, and optional fields.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    contacts = []
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                # Strip whitespace from keys and values
                cleaned = {k.strip(): v.strip() for k, v in row.items() if k}
                contact = Contact(**cleaned)
                contacts.append(contact)
            except (ValueError, TypeError) as e:
                errors.append(f"  Row {i + 1}: {e}")

    if errors:
        print(f"  ⚠  {len(errors)} contact(s) had validation errors:")
        for err in errors:
            print(f"     {err}")

    return contacts


def load_contacts(source: Optional[str] = None) -> List[Contact]:
    """
    Main entry point: load contacts from file or return demo contacts.
    
    Args:
        source: Path to JSON or CSV file, or None for demo contacts.
    
    Returns:
        List of validated Contact objects.
    """
    if not source:
        print("  📋 No data source specified. Using demo contacts.")
        return get_demo_contacts()

    path_str = str(source)

    if path_str.endswith(".json"):
        print(f"  📋 Loading contacts from JSON: {path_str}")
        return load_from_json(path_str)
    elif path_str.endswith(".csv"):
        print(f"  📋 Loading contacts from CSV: {path_str}")
        return load_from_csv(path_str)
    else:
        raise ValueError(f"Unsupported file format: {path_str}. Use .json or .csv")
```

### 3.3 Acceptance Criteria

- [ ] `models.py`: Can create a `Contact`, `Email`, `SendResult`, `LogEntry`
- [ ] `models.py`: Contact validation rejects missing required fields
- [ ] `models.py`: Contact validation rejects invalid emails
- [ ] `config.py`: Loads config from `.env` when file exists
- [ ] `config.py`: Returns defaults when `.env` doesn't exist
- [ ] `config.py`: `validate_config()` catches missing SMTP credentials when dry_run=false
- [ ] `loader.py`: `get_demo_contacts()` returns 5 valid contacts
- [ ] `loader.py`: `load_from_json()` parses valid JSON array
- [ ] `loader.py`: `load_from_csv()` parses CSV with DictReader
- [ ] `loader.py`: `load_contacts(None)` returns demo contacts
- [ ] All three files import without errors

### 3.4 Quick Test Snippet

```python
# Save as test_phase1.py and run: python test_phase1.py
from models import Contact, Email
from config import load_config, validate_config
from loader import load_contacts

# Test Contact creation
c = Contact(
    recipient_email="test@example.com",
    company="TestCo",
    role="Intern",
    candidate_name="Tester",
    candidate_background="Python dev",
)
print(f"✅ Contact created: {c.company} - {c.role}")

# Test validation
try:
    Contact(recipient_email="", company="", role="", candidate_name="", candidate_background="")
except ValueError as e:
    print(f"✅ Validation works: {e}")

# Test config
config = load_config()
print(f"✅ Config loaded: dry_run={config.dry_run}")

# Test demo contacts
contacts = load_contacts(None)
print(f"✅ Loaded {len(contacts)} demo contacts")

print("\n✅ Phase 1 tests passed!")
```

---

## 4. Phase 2: Email Generator

> **Goal**: Generate personalized cold emails from contact records using templates.
> **Time estimate**: 45 minutes
> **Files**: `generator.py`, `templates/default.txt`
> **Dependencies**: Phase 1 (`models.py`)

### 4.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 2.1 | Create default template | `templates/default.txt` | Jinja-like placeholders with 6-part email anatomy |
| 2.2 | Implement generator | `generator.py` | Template rendering, variable substitution, word counting |

### 4.2 File Specifications

#### `templates/default.txt`

```text
Subject: Quick note on the {role} role at {company}

Hi {recipient_name_or_fallback},

{personalization_note}

I'm {candidate_name}, and I've been building projects around {candidate_background}. The {role} role at {company} stood out because it connects closely with my background and interests.

Would you be open to a quick chat about how my experience could contribute to your team?

Best,
{candidate_name}
{portfolio_or_linkedin}
```

> **Note**: `{portfolio_or_linkedin}` is a computed variable that uses `portfolio_url` if available, otherwise `linkedin_url`, otherwise empty.

#### `generator.py` — Complete Content

```python
"""
Email generation engine for The Closer.
Generates personalized cold emails from contact records using templates."""

from pathlib import Path
from typing import Optional

from models import Contact, Email


# ─── Default Template (inline fallback) ──────────────

DEFAULT_TEMPLATE = """\
Subject: Quick note on the {role} role at {company}

Hi {recipient_name_or_fallback},

{personalization_note}

I'm {candidate_name}, and I've been building projects around {candidate_background}. The {role} role at {company} stood out because it connects closely with my background and interests.

Would you be open to a quick chat about how my experience could contribute to your team?

Best,
{candidate_name}
{portfolio_or_linkedin}"""


# ─── Template Loading ─────────────────────────────────

def load_template(template_name: str = "default") -> str:
    """
    Load a template file from the templates/ directory.
    
    Args:
        template_name: Name without extension (e.g., "default")
    
    Returns:
        Template string with {placeholders}.
    """
    template_path = Path(__file__).parent / "templates" / f"{template_name}.txt"

    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fall back to inline default
    if template_name == "default":
        return DEFAULT_TEMPLATE

    raise FileNotFoundError(f"Template not found: {template_name}")


# ─── Variable Preparation ─────────────────────────────

def prepare_variables(contact: Contact) -> dict:
    """
    Prepare template variables from contact record.
    Computes derived fields (e.g., portfolio_or_linkedin, recipient_name_or_fallback)."""
    return {
        "recipient_name": contact.recipient_name,
        "recipient_name_or_fallback": contact.get_recipient_name_or_fallback(),
        "company": contact.company,
        "role": contact.role,
        "candidate_name": contact.candidate_name,
        "candidate_background": contact.candidate_background,
        "personalization_note": contact.personalization_note or (
            f"I noticed {contact.company} is hiring for a {contact.role} role "
            f"and wanted to reach out."
        ),
        "portfolio_url": contact.portfolio_url or "",
        "linkedin_url": contact.linkedin_url or "",
        "portfolio_or_linkedin": contact.portfolio_url or contact.linkedin_url or "",
        "job_url": contact.job_url or "",
        "resume_link": contact.resume_link or "",
    }


# ─── Rendering ────────────────────────────────────────

def render_template(template: str, variables: dict) -> tuple[str, str]:
    """
    Render template with variables.
    
    Returns:
        Tuple of (subject_line, email_body)
    """
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))

    # Split subject from body
    lines = rendered.strip().split("\n", 1)
    subject_line = lines[0].replace("Subject: ", "").strip()
    body = lines[1].strip() if len(lines) > 1 else ""

    return subject_line, body


# ─── Word Counting ────────────────────────────────────

def count_words(text: str) -> int:
    """Count words in text, excluding URLs."""
    # Split on whitespace, exclude URLs from count
    words = [w for w in text.split() if not w.startswith("http")]
    return len(words)


# ─── Main Generation Function ─────────────────────────

def generate_email(
    contact: Contact,
    template_name: str = "default",
) -> Email:
    """
    Generate a personalized cold email from a contact record.
    
    Args:
        contact: Outreach target with personalization fields
        template_name: Name of template to use
    
    Returns:
        Email object with subject, body, and word count
    """
    template = load_template(template_name)
    variables = prepare_variables(contact)
    subject, body = render_template(template, variables)
    word_count = count_words(body)

    return Email(
        subject=subject,
        body=body,
        word_count=word_count,
        contact=contact,
    )


def generate_all(
    contacts: list[Contact],
    template_name: str = "default",
) -> list[Email]:
    """Generate emails for all contacts."""
    return [generate_email(c, template_name) for c in contacts]
```

### 4.3 Acceptance Criteria

- [ ] `generator.generate_email(contact)` returns an `Email` with subject + body
- [ ] Subject line includes company and role
- [ ] Body includes recipient name, personalization, candidate intro, value statement, ask, sign-off
- [ ] `word_count` is ≤ 150 words
- [ ] Missing optional fields (portfolio_url, personalization_note) don't cause errors
- [ ] Template with all variables renders cleanly (no `{...}` left in output)
- [ ] `load_template("nonexistent")` raises `FileNotFoundError`

### 4.4 Quick Test Snippet

```python
# Save as test_phase2.py and run: python test_phase2.py
from models import Contact
from generator import generate_email

contact = Contact(
    recipient_email="priya@example.com",
    recipient_name="Priya Sharma",
    company="Acme AI",
    role="Backend Engineering Intern",
    candidate_name="Alex Chen",
    candidate_background="Python developer building automation tools",
    personalization_note="I was excited to see Acme AI's recent launch.",
    portfolio_url="https://github.com/alexchen",
)

email = generate_email(contact)

print(f"Subject: {email.subject}")
print(f"Body:\n{email.body}")
print(f"\nWord count: {email.word_count}")

assert email.subject, "Subject must not be empty"
assert email.body, "Body must not be empty"
assert email.word_count <= 150, f"Too many words: {email.word_count}"
assert "{company}" not in email.body, "Unrendered template variable"
print("\n✅ Phase 2 tests passed!")
```

---

## 5. Phase 3: Preview & User Confirmation

> **Goal**: Display generated email in a clear terminal preview and handle user confirmation.
> **Time estimate**: 30 minutes
> **Files**: `preview.py`
> **Dependencies**: Phase 1 (`models.py`), Phase 2 (`generator.py`)

### 5.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 3.1 | Build preview display | `preview.py` | Formatted terminal output with To, Subject, Body, Word Count |
| 3.2 | Build confirmation prompt | `preview.py` | Actions: send/skip/quit — handles invalid input gracefully |

### 5.2 File Specification

#### `preview.py` — Complete Content

```python
"""
Preview and confirmation manager for The Closer.
Displays generated emails and handles user action input."""

from models import Contact, Email


def preview_email(
    contact: Contact,
    email: Email,
    index: int = 1,
    total: int = 1,
) -> str:
    """
    Display email preview and prompt for user action.
    
    Args:
        contact: The original contact record
        email: The generated email
        index: Current email index (1-based)
        total: Total number of emails
    
    Returns:
        User action string: "send", "skip", "quit"
    """
    _display_email(contact, email, index, total)
    return _get_user_action()


def _display_email(contact: Contact, email: Email, index: int, total: int) -> None:
    """Format and print email preview to terminal."""
    separator = "═" * 55

    print(f"\n{separator}")
    print(f"  📧 Email Preview ({index} of {total})")
    print(f"{separator}")
    print(f"\n  To:      {contact.recipient_email}")
    print(f"  Company: {contact.company}")
    print(f"  Role:    {contact.role}")
    print(f"\n  Subject: {email.subject}")
    print(f"\n  ─{'─' * 50}")
    print(f"\n{email.body}")
    print(f"\n  ─{'─' * 50}")
    print(f"\n  📊 Word count: {email.word_count}/150")

    # Show warnings if any
    warnings = email.warnings()
    if warnings:
        print(f"\n  ⚠  Warnings:")
        for w in warnings:
            print(f"     • {w}")

    print(f"{separator}\n")


def _get_user_action() -> str:
    """Get normalized user action input."""
    print("  ┌─ Actions ───────────────────────────────────┐")
    print("  │  [s] Send / Draft    [k] Skip               │")
    print("  │  [q] Quit                                    │")
    print("  └──────────────────────────────────────────────┘")

    while True:
        choice = input("  Your choice (s/k/q): ").strip().lower()

        if choice in ("s", "send"):
            return "send"
        elif choice in ("k", "skip"):
            return "skip"
        elif choice in ("q", "quit"):
            return "quit"
        else:
            print("  ❓ Invalid choice. Please enter s, k, or q.")
```

### 5.3 Acceptance Criteria

- [ ] `preview_email()` displays To, Company, Role, Subject, Body, Word Count
- [ ] Word count is clearly shown with `/150` limit
- [ ] Warnings (e.g., word count exceeded) are shown
- [ ] User can type `s` or `send` to proceed
- [ ] User can type `k` or `skip` to skip
- [ ] User can type `q` or `quit` to exit
- [ ] Invalid input shows error and re-prompts
- [ ] Valid action string is returned

### 5.4 Manual Test

```bash
python -c "
from models import Contact
from generator import generate_email
from preview import preview_email

c = Contact(
    recipient_email='test@example.com',
    company='TestCo',
    role='Intern',
    candidate_name='Tester',
    candidate_background='Python dev',
)
email = generate_email(c)
action = preview_email(c, email, 1, 3)
print(f'User chose: {action}')
"
```

---

## 6. Phase 4: Logger

> **Goal**: Log every email action to a CSV file for auditability and proof.
> **Time estimate**: 20 minutes
> **Files**: `logger.py`
> **Dependencies**: Phase 1 (`models.py`)

### 6.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 4.1 | Implement logger | `logger.py` | Append entries to CSV, get summary stats, show proof |

### 6.2 File Specification

#### `logger.py` — Complete Content

```python
"""
Logging module for The Closer.
Records every email action to outreach_log.csv for auditability."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from models import Contact, Email, LogEntry


LOG_FILE = "outreach_log.csv"
LOG_HEADERS = [
    "timestamp",
    "recipient_email",
    "company",
    "role",
    "subject",
    "status",
    "error_message",
]


def log_result(
    contact: Contact,
    email: Email,
    status: str,
    error: str = "",
) -> None:
    """
    Append a log entry to outreach_log.csv.
    
    Args:
        contact: The original contact record
        email: The generated email
        status: One of: generated, drafted, sent, skipped, failed
        error: Error message if status is "failed"
    """
    entry = LogEntry(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        recipient_email=contact.recipient_email,
        company=contact.company,
        role=contact.role,
        subject=email.subject,
        status=status,
        error_message=error,
    )

    file_exists = Path(LOG_FILE).exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": entry.timestamp,
            "recipient_email": entry.recipient_email,
            "company": entry.company,
            "role": entry.role,
            "subject": entry.subject,
            "status": entry.status,
            "error_message": entry.error_message,
        })

    print(f"  📝 Logged: {entry.status} → {entry.recipient_email} | {entry.company}")


def read_log() -> List[dict]:
    """Read all entries from outreach_log.csv."""
    if not Path(LOG_FILE).exists():
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_log_summary() -> dict:
    """Return summary statistics from the log file."""
    entries = read_log()
    total = len(entries)

    if total == 0:
        return {
            "total": 0,
            "sent": 0,
            "drafted": 0,
            "skipped": 0,
            "failed": 0,
            "generated": 0,
        }

    statuses = [e["status"] for e in entries]
    return {
        "total": total,
        "sent": statuses.count("sent"),
        "drafted": statuses.count("drafted"),
        "skipped": statuses.count("skipped"),
        "failed": statuses.count("failed"),
        "generated": statuses.count("generated"),
    }


def show_proof() -> None:
    """Display formatted log table for proof."""
    entries = read_log()

    if not entries:
        print("\n  📭 No log entries found.")
        return

    summary = get_log_summary()
    print("\n" + "═" * 60)
    print("  📋 Outreach Log — Proof")
    print("═" * 60)

    for i, entry in enumerate(entries, 1):
        print(f"\n  {i}. {entry['company']} — {entry['role']}")
        print(f"     To: {entry['recipient_email']}")
        print(f"     Subject: {entry['subject']}")
        print(f"     Status: {entry['status']}")
        print(f"     Time: {entry['timestamp']}")
        if entry["error_message"]:
            print(f"     Error: {entry['error_message']}")

    print("\n  ─" + "─" * 55)
    print(f"  Summary: {summary['total']} total | "
          f"{summary['sent']} sent | "
          f"{summary['drafted']} drafted | "
          f"{summary['skipped']} skipped | "
          f"{summary['failed']} failed")
    print("═" * 60 + "\n")
```

### 6.3 Acceptance Criteria

- [ ] `log_result()` creates `outreach_log.csv` if it doesn't exist
- [ ] `log_result()` appends a new row with all fields
- [ ] CSV file has header row with correct columns
- [ ] `read_log()` returns list of dicts from existing CSV
- [ ] `get_log_summary()` returns correct counts
- [ ] `show_proof()` prints formatted log table
- [ ] Multiple calls to `log_result()` append correctly (no header duplication)

### 6.4 Quick Test Snippet

```python
# Save as test_phase4.py and run: python test_phase4.py
from models import Contact, Email
from logger import log_result, read_log, get_log_summary, show_proof
import os

c = Contact(
    recipient_email="test@example.com",
    company="TestCo",
    role="Intern",
    candidate_name="Tester",
    candidate_background="Python dev",
)
email = Email(subject="Test", body="Hello", word_count=2, contact=c)

# Clean up before test
if os.path.exists("outreach_log.csv"):
    os.remove("outreach_log.csv")

log_result(c, email, "sent")
log_result(c, email, "skipped")

entries = read_log()
print(f"Entries: {len(entries)}")
assert len(entries) == 2, "Should have 2 entries"

summary = get_log_summary()
print(f"Summary: {summary}")
assert summary["sent"] == 1
assert summary["skipped"] == 1

print("\n✅ Phase 4 tests passed!")
```

---

## 7. Phase 5: Orchestrator & Dry-Run Pipeline

> **Goal**: Wire all modules together into a working CLI pipeline with dry-run mode.
> **Time estimate**: 45 minutes
> **Files**: `main.py`, minor update to `config.py`
> **Dependencies**: Phases 1-4 (models, config, loader, generator, preview, logger)

### 7.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 5.1 | Add CLI argument parsing | `config.py` | Add `parse_cli_args()` function |
| 5.2 | Build orchestrator | `main.py` | Full pipeline: load → generate → preview → dry-run → log |
| 5.3 | End-to-end dry-run test | — | Run `python main.py` with demo contacts |

### 7.2 File Specifications

#### Add to `config.py` (new function)

```python
import argparse


def parse_cli_args() -> dict:
    """
    Parse command-line arguments.
    Override .env values where provided.
    
    Returns:
        Dictionary of CLI overrides.
    """
    parser = argparse.ArgumentParser(
        description="The Closer — Cold Email Writer + Send Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with demo contacts (dry run)
  python main.py --file contacts.json     # Load from JSON file
  python main.py --send                   # Actually send emails
  python main.py --file jobs.csv --send   # CSV input + real sending
        """,
    )

    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to contacts JSON or CSV file (default: use demo contacts)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Enable dry-run mode (log only, no sending)",
    )
    parser.add_argument(
        "--send",
        action="store_false",
        dest="dry_run",
        default=None,
        help="Disable dry-run mode and actually send emails",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Show outreach log and exit",
    )

    args = parser.parse_args()
    return {k: v for k, v in vars(args).items() if v is not None}
```

#### `main.py` — Complete Content

```python
"""
The Closer — Cold Email Writer + Send Bot
Main entry point and orchestrator.

Usage:
    python main.py                      # Demo contacts, dry run
    python main.py --file contacts.json # Custom contacts file
    python main.py --send               # Actually send emails
    python main.py --log                # Show outreach log
"""

import sys
from pathlib import Path

from config import load_config, validate_config, parse_cli_args
from loader import load_contacts
from generator import generate_email
from preview import preview_email
from logger import log_result, show_proof, get_log_summary


def print_banner() -> None:
    """Print application banner."""
    print()
    print("╔═══════════════════════════════════════════╗")
    print("║        The Closer — Cold Email Bot        ║")
    print("║        Sprint 3 — The Outreach Operator   ║")
    print("╚═══════════════════════════════════════════╝")
    print()


def print_summary(results: list[tuple]) -> None:
    """Print final summary of all actions."""
    print("\n" + "═" * 55)
    print("  📊 Run Summary")
    print("═" * 55)

    total = len(results)
    sent = sum(1 for _, s in results if s == "sent")
    drafted = sum(1 for _, s in results if "draft" in s)
    skipped = sum(1 for _, s in results if s == "skipped")
    failed = sum(1 for _, s in results if s == "failed")

    print(f"\n  Total contacts processed: {total}")
    if sent:
        print(f"  ✅ Sent: {sent}")
    if drafted:
        print(f"  📝 Drafted: {drafted}")
    if skipped:
        print(f"  ⏭  Skipped: {skipped}")
    if failed:
        print(f"  ❌ Failed: {failed}")

    print(f"\n  📋 Log saved to: outreach_log.csv")
    print("═" * 55 + "\n")


def main() -> None:
    """Main orchestrator."""
    print_banner()

    # ─── Handle --log flag ─────────────────────────
    cli_args = parse_cli_args()
    if cli_args.get("log"):
        show_proof()
        return

    # ─── Load config ──────────────────────────────
    config = load_config()

    # Apply CLI overrides
    if cli_args.get("file"):
        config.data_source = cli_args["file"]
    if cli_args.get("dry_run") is not None:
        config.dry_run = cli_args["dry_run"]

    # Validate config
    errors = validate_config(config)
    if errors:
        print("  ❌ Configuration errors:")
        for err in errors:
            print(f"     • {err}")
        sys.exit(1)

    # Show mode
    mode = "🔒 DRY RUN" if config.dry_run else "📤 LIVE SEND"
    print(f"  Mode: {mode}")
    if config.dry_run:
        print(f"  No emails will be sent. Set DRY_RUN=false to send.\n")
    print()

    # ─── Load contacts ────────────────────────────
    try:
        contacts = load_contacts(config.data_source)
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    # Limit to max_emails_per_run
    contacts = contacts[: config.max_emails_per_run]
    print(f"  Loaded {len(contacts)} outreach target(s)\n")

    # ─── Process each contact ─────────────────────
    results = []

    for i, contact in enumerate(contacts, 1):
        print(f"  ─{'─' * 50}")
        print(f"  Processing ({i}/{len(contacts)}): {contact.company} — {contact.role}")
        print(f"  ─{'─' * 50}")

        # Generate email
        try:
            email = generate_email(contact)
            print(f"  ✅ Email generated ({email.word_count} words)")
        except Exception as e:
            print(f"  ❌ Generation failed: {e}")
            log_result(contact, Email("", "", 0, contact), "failed", str(e))
            results.append((contact, "failed"))
            continue

        # Preview and confirm
        action = preview_email(contact, email, i, len(contacts))

        if action == "quit":
            print("\n  🛑 Quitting...")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            break

        if action == "skip":
            print("  ⏭  Skipped.")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            continue

        # Send or dry-run
        if config.dry_run:
            print(f"  🔒 [DRY RUN] Would send to {contact.recipient_email}")
            status = "drafted (dry_run)"
        else:
            # Real sending will be connected in Phase 6
            print(f"  📤 Sending to {contact.recipient_email}...")
            status = "sent (placeholder)"

        log_result(contact, email, status)
        results.append((contact, status))

    # ─── Summary ──────────────────────────────────
    print_summary(results)

    # Show log file location
    if Path("outreach_log.csv").exists():
        print(f"  💡 Run 'python main.py --log' to view the full outreach log.")


if __name__ == "__main__":
    main()
```

### 7.3 Acceptance Criteria

- [ ] `python main.py` runs end-to-end with 5 demo contacts
- [ ] Each contact generates a unique, personalized email
- [ ] Each email is previewed with confirmation prompt
- [ ] User actions work: `s` (proceed), `k` (skip), `q` (quit mid-pipeline)
- [ ] `outreach_log.csv` is created with entries for each contact
- [ ] Final summary shows correct count of processed/skipped entries
- [ ] `python main.py --log` displays the log without running the pipeline
- [ ] `python main.py --send` shows "LIVE SEND" mode
- [ ] `python main.py --file nonexistent.json` shows a clear error

---

## 8. Phase 6: Real Email Sending (SMTP)

> **Goal**: Connect the pipeline to SMTP to actually send emails or create drafts.
> **Time estimate**: 45 minutes
> **Files**: `sender.py`, update `main.py`, update `.env.example`
> **Dependencies**: Phase 5 (working dry-run pipeline), Gmail App Password setup

### 8.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 6.1 | Implement SMTP sender | `sender.py` | `DryRunSender`, `SmtpSender` with strategy pattern |
| 6.2 | Connect to orchestrator | `main.py` | Replace dry-run placeholder with real sender |
| 6.3 | Add config validation | `config.py` | Already done — ensure SMTP fields validated |
| 6.4 | Test send to self | — | Real send test to own email |

### 8.2 File Specification

#### `sender.py` — Complete Content

```python
"""
Email sender for The Closer.
Supports dry-run (log only) and SMTP (real send) modes."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from abc import ABC, abstractmethod

from models import Contact, Email, SendResult
from config import Config


class EmailSenderStrategy(ABC):
    """Abstract base for email sending strategies."""

    @abstractmethod
    def send(self, contact: Contact, email: Email, config: Config) -> SendResult:
        """Send or log an email. Returns result with status."""
        ...


class DryRunSender(EmailSenderStrategy):
    """Logs intent without actually sending."""

    def send(self, contact: Contact, email: Email, config: Config) -> SendResult:
        print(f"  🔒 [DRY RUN] Would send to {contact.recipient_email}")
        print(f"     Subject: {email.subject}")
        return SendResult(status="drafted (dry_run)")


class SmtpSender(EmailSenderStrategy):
    """Sends email via SMTP using smtplib."""

    def send(self, contact: Contact, email: Email, config: Config) -> SendResult:
        """
        Send email via SMTP with proper MIME formatting.
        
        Args:
            contact: Recipient information
            email: Generated email content
            config: SMTP configuration
        
        Returns:
            SendResult with status and optional error
        """
        try:
            # Build MIME message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{config.sender_name} <{config.smtp_user}>"
            msg["To"] = contact.recipient_email
            msg["Subject"] = email.subject
            msg.attach(MIMEText(email.body, "plain"))

            # Connect and send
            print(f"  📤 Connecting to {config.smtp_host}:{config.smtp_port}...")
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                server.starttls()
                print(f"  🔐 Authenticating as {config.smtp_user}...")
                server.login(config.smtp_user, config.smtp_password)
                server.send_message(msg)

            print(f"  ✅ Email sent to {contact.recipient_email}")
            return SendResult(status="sent")

        except smtplib.SMTPAuthenticationError:
            error_msg = "Authentication failed. Check your SMTP username and app password."
            print(f"  ❌ {error_msg}")
            return SendResult(status="failed", error=error_msg)

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            print(f"  ❌ {error_msg}")
            return SendResult(status="failed", error=error_msg)

        except Exception as e:
            error_msg = f"Connection failed: {e}"
            print(f"  ❌ {error_msg}")
            return SendResult(status="failed", error=error_msg)


def get_sender(config: Config) -> EmailSenderStrategy:
    """
    Factory: returns appropriate sender based on config.
    
    Args:
        config: Application configuration
    
    Returns:
        EmailSenderStrategy implementation
    """
    if config.dry_run:
        return DryRunSender()
    elif config.send_method == "smtp":
        return SmtpSender()
    elif config.send_method == "gmail":
        # Stretch: Gmail API sender
        raise NotImplementedError("Gmail API sender not yet implemented")
    else:
        raise ValueError(f"Unknown send_method: {config.send_method}")


def send_email(contact: Contact, email: Email, config: Config) -> SendResult:
    """
    High-level send function: delegates to the appropriate strategy.
    
    Args:
        contact: Recipient information
        email: Generated email content
        config: Application configuration
    
    Returns:
        SendResult with status and optional error
    """
    sender = get_sender(config)
    return sender.send(contact, email, config)
```

#### Update `main.py` — Replace the dry-run placeholder

In the `main()` function, replace the comment placeholder section:

```python
# In main(), find this section and replace:

        # Send or dry-run
        if config.dry_run:
            print(f"  🔒 [DRY RUN] Would send to {contact.recipient_email}")
            status = "drafted (dry_run)"
        else:
            # Real sending will be connected in Phase 6
            print(f"  📤 Sending to {contact.recipient_email}...")
            status = "sent (placeholder)"

# With:

        # Send or dry-run
        if config.dry_run:
            status = "drafted (dry_run)"
        else:
            print(f"  📤 Sending to {contact.recipient_email}...")
            result = send_email(contact, email, config)
            status = result.status
            if result.error:
                log_result(contact, email, status, result.error)
                results.append((contact, status))
                continue
```

And add the import at the top of `main.py`:

```python
from sender import send_email
```

### 8.3 User Setup Instructions

For the user to send real emails, they must:

1. **Enable 2-Factor Authentication** on their Google account
2. **Generate an App Password** at https://myaccount.google.com/apppasswords
3. **Copy the app password** into `.env` as `SMTP_PASSWORD=`
4. **Fill in their email** as `SMTP_USER=yourname@gmail.com`
5. **Set their name** as `SENDER_NAME=Your Full Name`
6. **Set `DRY_RUN=false`** in `.env` or use `--send` flag
7. **Test by sending to their own email first**

### 8.4 Acceptance Criteria

- [ ] `DryRunSender` logs intent without connecting to SMTP
- [ ] `SmtpSender` builds proper MIME message with From, To, Subject
- [ ] `SmtpSender` handles authentication errors gracefully
- [ ] `SmtpSender` handles connection errors gracefully
- [ ] `get_sender()` returns correct strategy based on config
- [ ] `send_email()` is a clean public API
- [ ] Pipeline runs with `DRY_RUN=false` and actually sends email
- [ ] Successful sends are logged as "sent"

---

## 9. Phase 7: Polish & Safety

> **Goal**: Add safety guardrails, opt-out mechanism, email editing, and final polish.
> **Time estimate**: 30 minutes
> **Files**: `opt_out.py` (new), updates to `preview.py`, `main.py`
> **Dependencies**: Phase 6

### 9.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 7.1 | Implement opt-out | `opt_out.py` | Check + add recipients to opt-out list |
| 7.2 | Add opt-out check to pipeline | `main.py` | Skip opted-out recipients silently |
| 7.3 | Add email editing in preview | `preview.py` | Allow user to edit subject/body before sending |
| 7.4 | Add safety confirmation | `main.py` | "Are you sure?" prompt when not in dry-run |

### 9.2 File Specifications

#### `opt_out.py`

```python
"""
Opt-out management for The Closer.
Respects recipient preferences by maintaining an opt-out list."""

from pathlib import Path
from typing import List


OPT_OUT_FILE = "opt_out.txt"


def load_opt_outs() -> List[str]:
    """Load list of opted-out email addresses."""
    if not Path(OPT_OUT_FILE).exists():
        return []
    with open(OPT_OUT_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]


def is_opted_out(recipient_email: str) -> bool:
    """Check if a recipient has opted out."""
    return recipient_email.lower() in load_opt_outs()


def add_opt_out(recipient_email: str) -> None:
    """Add a recipient to the opt-out list."""
    email_lower = recipient_email.lower()
    current = load_opt_outs()

    if email_lower not in current:
        with open(OPT_OUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{email_lower}\n")
        print(f"  🚫 Added {recipient_email} to opt-out list.")
```

#### Update `preview.py` — Add `edit_email()` function

```python
def edit_email(email: Email) -> Email:
    """
    Allow user to edit subject and body before sending.
    Returns updated Email with recalculated word count."""
    print("\n  📝 Edit mode — press Enter to keep current value.\n")

    new_subject = input(f"  Subject [{email.subject}]: ").strip()
    if new_subject:
        email.subject = new_subject

    print(f"\n  Current body:\n{email.body}\n")
    print("  Enter new body (Ctrl+D or Enter newline + '.' + Enter to finish):")
    lines = []
    while True:
        try:
            line = input()
            if line == ".":
                break
            lines.append(line)
        except EOFError:
            break
    if lines:
        new_body = "\n".join(lines)
        email.body = new_body
        email.word_count = len([w for w in new_body.split() if not w.startswith("http")])

    print(f"  ✅ Email updated ({email.word_count} words)")
    return email
```

#### Update `preview.py` — Add edit action

In `_get_user_action()`, add `e` to the options:

```python
def _get_user_action() -> str:
    """Get normalized user action input."""
    print("  ┌─ Actions ───────────────────────────────────┐")
    print("  │  [s] Send / Draft    [k] Skip               │")
    print("  │  [e] Edit email      [q] Quit               │")
    print("  └──────────────────────────────────────────────┘")

    while True:
        choice = input("  Your choice (s/k/e/q): ").strip().lower()

        if choice in ("s", "send"):
            return "send"
        elif choice in ("k", "skip"):
            return "skip"
        elif choice in ("e", "edit"):
            return "edit"
        elif choice in ("q", "quit"):
            return "quit"
        else:
            print("  ❓ Invalid choice. Please enter s, k, e, or q.")
```

#### Update `main.py` — Add opt-out check + safety confirmation + edit flow

In the main processing loop, after generating email:

```python
        # Check opt-out
        if is_opted_out(contact.recipient_email):
            print(f"  🚫 {contact.recipient_email} has opted out. Skipping.")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            continue
```

Replace the action handler to support editing:

```python
        # Preview and confirm
        action = preview_email(contact, email, i, len(contacts))

        if action == "quit":
            print("\n  🛑 Quitting...")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            break

        if action == "edit":
            email = edit_email(email)
            # Re-display the updated preview so the user sees their changes
            action = preview_email(contact, email, i, len(contacts))
            if action == "quit":
                print("\n  🛑 Quitting...")
                log_result(contact, email, "skipped")
                results.append((contact, "skipped"))
                break

        if action == "skip":
            print("  ⏭  Skipped.")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            continue
```

Add safety confirmation before sending:

```python
        # Safety confirmation for real sends
        if not config.dry_run:
            confirm = input("\n  ⚠  Really send this email? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("  ⏭  Skipped.")
                log_result(contact, email, "skipped")
                results.append((contact, "skipped"))
                continue

        # Send
        ...
```

Add imports to `main.py`:

```python
from opt_out import is_opted_out, add_opt_out
from preview import edit_email
```

### 9.3 Acceptance Criteria

- [ ] Opt-out file is respected: opted-out recipients are skipped
- [ ] Opt-out file is automatically created on first addition
- [ ] Email editing works: user can change subject and body
- [ ] Word count is recalculated after editing
- [ ] Safety confirmation appears when `dry_run=false`
- [ ] User can abort send during safety confirmation

---

## 10. Phase 8: Testing Suite

> **Goal**: Comprehensive test suite covering all modules.
> **Time estimate**: 45 minutes
> **Files**: `tests/test_models.py`, `tests/test_config.py`, `tests/test_loader.py`, `tests/test_generator.py`, `tests/test_logger.py`, `tests/test_sender.py`, `tests/test_integration.py`
> **Dependencies**: Phases 1-6

### 10.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 8.1 | Test models | `tests/test_models.py` | Contact validation, Email warnings, edge cases |
| 8.2 | Test config | `tests/test_config.py` | Env loading, validation errors |
| 8.3 | Test loader | `tests/test_loader.py` | JSON, CSV, demo contacts, error handling |
| 8.4 | Test generator | `tests/test_generator.py` | Template rendering, word count, edge cases |
| 8.5 | Test logger | `tests/test_logger.py` | CSV append, read, summary, proof |
| 8.6 | Test sender | `tests/test_sender.py` | DryRunSender, SmtpSender (mocked) |
| 8.7 | Integration test | `tests/test_integration.py` | Full dry-run pipeline |

### 10.2 Test Environment Isolation

> ⚠ Tests must not depend on a real `.env` file. Use fixtures to isolate environment.

```python
# test_config.py example fixture:
@pytest.fixture
def isolated_env(tmp_path):
    """Create a temporary .env for testing."""
    env_file = tmp_path / ".env.test"
    env_file.write_text("DRY_RUN=true\n")
    return str(env_file)
```

### 10.3 Test File Specifications

#### `tests/test_models.py`

```python
"""Tests for models.py"""
import pytest
from models import Contact, Email


class TestContact:
    def test_valid_contact(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        assert c.company == "TestCo"

    def test_missing_required_fields(self):
        with pytest.raises(ValueError):
            Contact(
                recipient_email="",
                company="",
                role="",
                candidate_name="",
                candidate_background="",
            )

    def test_invalid_email(self):
        with pytest.raises(ValueError):
            Contact(
                recipient_email="not-an-email",
                company="TestCo",
                role="Intern",
                candidate_name="Tester",
                candidate_background="Python dev",
            )

    def test_recipient_name_fallback(self):
        c = Contact(
            recipient_email="john.doe@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        assert c.get_recipient_name_or_fallback() == "John Doe"


class TestEmail:
    def test_valid_email(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        e = Email(subject="Test", body="Hello world", word_count=2, contact=c)
        assert e.is_valid()
        assert e.warnings() == []

    def test_long_email_warning(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        e = Email(subject="Test", body="word " * 151, word_count=151, contact=c)
        warnings = e.warnings()
        assert any("150" in w for w in warnings)
```

#### `tests/test_generator.py`

```python
"""Tests for generator.py"""
import pytest
from models import Contact
from generator import generate_email, count_words, load_template


class TestGenerator:
    @pytest.fixture
    def contact(self):
        return Contact(
            recipient_email="test@example.com",
            recipient_name="Test User",
            company="TestCo",
            role="Engineer",
            candidate_name="Alex",
            candidate_background="Python developer",
            personalization_note="Love your product.",
            portfolio_url="https://github.com/alex",
        )

    def test_generates_email(self, contact):
        email = generate_email(contact)
        assert email.subject
        assert email.body
        assert email.word_count > 0

    def test_subject_contains_company_and_role(self, contact):
        email = generate_email(contact)
        assert "TestCo" in email.subject
        assert "Engineer" in email.subject

    def test_body_contains_personalization(self, contact):
        email = generate_email(contact)
        assert "Love your product." in email.body or "Alex" in email.body

    def test_word_count_limit(self, contact):
        email = generate_email(contact)
        assert email.word_count <= 150, f"Word count: {email.word_count}"

    def test_no_unrendered_variables(self, contact):
        email = generate_email(contact)
        assert "{" not in email.body.replace("{email}", "")

    def test_missing_optional_fields(self):
        minimal = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Engineer",
            candidate_name="Alex",
            candidate_background="Python dev",
        )
        email = generate_email(minimal)
        assert email.subject
        assert email.body

    def test_count_words(self):
        assert count_words("Hello world") == 2
        assert count_words("Check https://example.com") == 1  # URL excluded
        assert count_words("") == 0
```

#### `tests/test_loader.py`

```python
"""Tests for loader.py"""
import pytest
import json
import tempfile
import os
from loader import load_contacts, load_from_json, load_from_csv, get_demo_contacts


class TestDemoContacts:
    def test_returns_5_contacts(self):
        contacts = get_demo_contacts()
        assert len(contacts) == 5

    def test_all_contacts_valid(self):
        contacts = get_demo_contacts()
        for c in contacts:
            assert c.recipient_email
            assert c.company
            assert c.role

    def test_demo_contacts_have_varied_companies(self):
        contacts = get_demo_contacts()
        companies = [c.company for c in contacts]
        assert len(set(companies)) == 5


class TestJsonLoader:
    def test_loads_valid_json(self):
        data = [
            {
                "recipient_email": "test@example.com",
                "company": "TestCo",
                "role": "Intern",
                "candidate_name": "Tester",
                "candidate_background": "Python dev",
            }
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name

        try:
            contacts = load_from_json(path)
            assert len(contacts) == 1
            assert contacts[0].company == "TestCo"
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_from_json("nonexistent.json")


class TestLoadContacts:
    def test_no_source_returns_demo(self):
        contacts = load_contacts(None)
        assert len(contacts) == 5


class TestCsvLoader:
    def test_loads_valid_csv(self):
        import csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["recipient_email", "company", "role", "candidate_name", "candidate_background"])
            writer.writerow(["test@example.com", "TestCo", "Intern", "Tester", "Python dev"])
            path = f.name

        try:
            contacts = load_from_csv(path)
            assert len(contacts) == 1
            assert contacts[0].company == "TestCo"
        finally:
            os.unlink(path)

    def test_csv_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_from_csv("nonexistent.csv")
```

#### `tests/test_config.py`

```python
"""Tests for config.py"""
import os
import pytest
from config import Config, validate_config


class TestValidateConfig:
    def test_dry_run_requires_no_credentials(self):
        config = Config(dry_run=True)
        errors = validate_config(config)
        assert len(errors) == 0

    def test_smtp_send_requires_credentials(self):
        config = Config(dry_run=False, send_method="smtp")
        errors = validate_config(config)
        assert any("SMTP_USER" in e for e in errors)
        assert any("SMTP_PASSWORD" in e for e in errors)

    def test_unknown_send_method(self):
        config = Config(send_method="unknown")
        errors = validate_config(config)
        assert any("unknown" in e.lower() for e in errors)

    def test_unusual_port_warning(self):
        config = Config(smtp_port=1234)
        errors = validate_config(config)
        assert any("Unusual" in e for e in errors)
```

#### `tests/test_logger.py`

```python
"""Tests for logger.py"""
import os
import pytest
from models import Contact, Email
from logger import log_result, read_log, get_log_summary


@pytest.fixture
def contact():
    return Contact(
        recipient_email="test@example.com",
        company="TestCo",
        role="Intern",
        candidate_name="Tester",
        candidate_background="Python dev",
    )


@pytest.fixture
def email(contact):
    return Email(subject="Test", body="Hello world", word_count=2, contact=contact)


class TestLogger:
    def test_creates_csv_on_first_log(self, contact, email):
        if os.path.exists("outreach_log.csv"):
            os.remove("outreach_log.csv")
        log_result(contact, email, "sent")
        assert os.path.exists("outreach_log.csv")
        os.remove("outreach_log.csv")

    def test_reads_back_entries(self, contact, email):
        if os.path.exists("outreach_log.csv"):
            os.remove("outreach_log.csv")
        log_result(contact, email, "sent")
        entries = read_log()
        assert len(entries) == 1
        assert entries[0]["status"] == "sent"
        assert entries[0]["company"] == "TestCo"
        os.remove("outreach_log.csv")

    def test_summary_counts(self, contact, email):
        if os.path.exists("outreach_log.csv"):
            os.remove("outreach_log.csv")
        log_result(contact, email, "sent")
        log_result(contact, email, "skipped")
        log_result(contact, email, "failed", "Connection error")
        summary = get_log_summary()
        assert summary["sent"] == 1
        assert summary["skipped"] == 1
        assert summary["failed"] == 1
        assert summary["total"] == 3
        os.remove("outreach_log.csv")
```

#### `tests/test_sender.py`

```python
"""Tests for sender.py"""
import pytest
from models import Contact, Email
from config import Config
from sender import DryRunSender, get_sender


@pytest.fixture
def contact():
    return Contact(
        recipient_email="test@example.com",
        company="TestCo",
        role="Intern",
        candidate_name="Tester",
        candidate_background="Python dev",
    )


@pytest.fixture
def email(contact):
    return Email(subject="Test", body="Hello world", word_count=2, contact=contact)


class TestDryRunSender:
    def test_returns_drafted_status(self, contact, email):
        config = Config(dry_run=True)
        sender = DryRunSender()
        result = sender.send(contact, email, config)
        assert result.status == "drafted (dry_run)"
        assert result.error == ""


class TestGetSender:
    def test_dry_run_returns_dry_run_sender(self):
        config = Config(dry_run=True)
        sender = get_sender(config)
        assert isinstance(sender, DryRunSender)

    def test_smtp_returns_smtp_sender(self):
        config = Config(dry_run=False, send_method="smtp")
        sender = get_sender(config)
        from sender import SmtpSender
        assert isinstance(sender, SmtpSender)

    def test_gmail_not_implemented(self):
        config = Config(dry_run=False, send_method="gmail")
        with pytest.raises(NotImplementedError):
            get_sender(config)
```

#### `tests/test_integration.py`

```python
"""Integration tests for full pipeline."""
import os
import pytest
from config import Config, load_config
from loader import get_demo_contacts
from generator import generate_email
from sender import DryRunSender


class TestDryRunPipeline:
    def test_full_dry_run_pipeline(self):
        """End-to-end: contacts → generate → dry-run send → log."""
        contacts = get_demo_contacts()
        assert len(contacts) == 5

        config = Config(dry_run=True)
        sender = DryRunSender()

        for contact in contacts:
            email = generate_email(contact)
            assert email.subject
            assert email.body
            assert email.word_count > 0

            result = sender.send(contact, email, config)
            assert "draft" in result.status

    def test_all_emails_under_150_words(self):
        """Verify all demo contacts produce sub-150-word emails."""
        contacts = get_demo_contacts()
        for contact in contacts:
            email = generate_email(contact)
            assert email.word_count <= 150, (
                f"{contact.company} - {contact.role}: {email.word_count} words"
            )

    def test_each_email_is_unique(self):
        """No two generated emails should be identical."""
        contacts = get_demo_contacts()
        emails = [generate_email(c) for c in contacts]
        bodies = [e.body for e in emails]
        assert len(set(bodies)) == len(bodies), "Duplicate email bodies detected"
```

### 10.4 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_generator.py -v

# Run with coverage (if pytest-cov installed)
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

### 10.5 Acceptance Criteria

- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Each module has ≥1 test file
- [ ] Edge cases covered: missing fields, invalid emails, file not found
- [ ] Integration test runs full dry-run pipeline
- [ ] Tests are isolated (use temp files, clean up after)

---

## 11. Phase 9: Documentation & Demo Prep

> **Goal**: Complete project documentation and prepare for live demo.
> **Time estimate**: 30 minutes
> **Files**: `README.md`, demo slides/notes
> **Dependencies**: All prior phases (must have working code)

### 11.1 Tasks

| # | Task | File | Details |
|---|------|------|---------|
| 9.1 | Write README | `README.md` | Setup, usage, architecture, demo flow |
| 9.2 | Create `contacts.json` sample | `contacts.json` | 5 sample contacts for file-based demo |
| 9.3 | Final end-to-end test | — | Verify full pipeline with all features |

### 11.2 File Specifications

#### `README.md`

```markdown
# The Closer — Cold Email Writer + Send Bot

A CLI tool for job seekers to generate and send personalized cold outreach emails.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment config
cp .env.example .env

# 3. Run with demo contacts (dry run — safe)
python main.py
```

## Setup

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Fill in `.env`:
   - `SMTP_USER`: your Gmail address
   - `SMTP_PASSWORD`: the 16-character app password
   - `SENDER_NAME`: your name

## Usage

```bash
# Run with demo contacts (dry run — safe)
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

## Features

- ✅ Load contacts from JSON, CSV, or built-in demo
- ✅ Generate personalized cold emails using templates
- ✅ Preview emails before sending with word count
- ✅ Edit emails before sending
- ✅ Send via SMTP (Gmail App Passwords)
- ✅ Dry-run mode (safe by default)
- ✅ Safety confirmation for real sends
- ✅ Opt-out management
- ✅ Detailed CSV logging

## Project Structure

```
├── main.py          # Entry point / orchestrator
├── models.py        # Data classes
├── config.py        # Configuration & env vars
├── loader.py        # Contact loading
├── generator.py     # Email generation
├── preview.py       # Preview & confirmation
├── sender.py        # Email sending (SMTP)
├── logger.py        # CSV logging
├── opt_out.py       # Opt-out management
├── templates/       # Email templates
├── contacts.json    # Sample contacts
├── .env.example     # Environment template
└── tests/           # Test suite
```

## Architecture

See `docs/architecture.md` for full architecture documentation.
See `docs/implementation-plan.md` for the detailed phase-by-phase plan.
```

#### `contacts.json`

```json
[
  {
    "recipient_email": "alice@techcorp.com",
    "recipient_name": "Alice Wang",
    "company": "TechCorp",
    "role": "Software Engineering Intern",
    "job_url": "https://techcorp.com/careers/swe-intern",
    "personalization_note": "I was impressed by TechCorp's open-source contributions to the React ecosystem.",
    "candidate_name": "Your Name",
    "candidate_background": "Full-stack developer with React and Python experience",
    "portfolio_url": "https://github.com/yourname"
  },
  {
    "recipient_email": "bob@healthai.io",
    "recipient_name": "Bob Chen",
    "company": "HealthAI",
    "role": "ML Research Intern",
    "personalization_note": "HealthAI's work on medical image segmentation is exactly the kind of impactful ML I want to work on.",
    "candidate_name": "Your Name",
    "candidate_background": "ML engineer with projects in computer vision and healthcare",
    "linkedin_url": "https://linkedin.com/in/yourname"
  },
  {
    "recipient_email": "carol@finstartup.com",
    "recipient_name": "Carol Martinez",
    "company": "FinStartup",
    "role": "Backend Intern",
    "personalization_note": "I've been following FinStartup's growth — your API-first approach to personal finance is innovative.",
    "candidate_name": "Your Name",
    "candidate_background": "Backend developer with experience in Python, PostgreSQL, and distributed systems",
    "portfolio_url": "https://github.com/yourname"
  },
  {
    "recipient_email": "dave@greentech.org",
    "recipient_name": "Dave Park",
    "company": "GreenTech",
    "role": "Data Engineering Intern",
    "personalization_note": "GreenTech's mission to use data for environmental monitoring really aligns with my values.",
    "candidate_name": "Your Name",
    "candidate_background": "Data engineer skilled in ETL pipelines, SQL, and data visualization",
    "portfolio_url": "https://github.com/yourname"
  },
  {
    "recipient_email": "eva@sociapp.com",
    "recipient_name": "Eva Thompson",
    "company": "Sociapp",
    "role": "Product Management Intern",
    "personalization_note": "I love Sociapp's focus on community-driven features — your recent launch is inspiring.",
    "candidate_name": "Your Name",
    "candidate_background": "CS student with product thinking and experience building user-facing features",
    "linkedin_url": "https://linkedin.com/in/yourname"
  }
]
```

### 11.3 Acceptance Criteria

- [ ] `README.md` is complete with setup, usage, architecture, and feature list
- [ ] `contacts.json` has 5 valid sample contacts for file-based demo
- [ ] `python main.py --file contacts.json` works end-to-end with the sample file
- [ ] All doc files are consistent: `docs/architecture.md`, `docs/implementation-plan.md`
- [ ] Final end-to-end test: all 5 contacts processed through full pipeline
- [ ] Dry run outputs match expected format from problem statement examples (§6)
- [ ] User can follow README from zero to running demo without assistance

---

## 12. Phase X: Stretch Goals

> **Goal**: Optional advanced features for after the MVP is complete.
> **Each stretch goal is independent** — implement in any order.

### 12.1 Stretch: Gmail API Draft Creation

**PREREQ**: `google-api-python-client`, `google-auth-oauthlib`

**Files**: Add `auth.py` for OAuth flow, extend `sender.py` with `GmailApiSender`

**Tasks**:
1. Set up Google Cloud Project + enable Gmail API
2. Create OAuth 2.0 Desktop credentials → download `client_secret.json`
3. Implement `auth.py`: OAuth flow with local server
4. Implement `GmailApiSender` in `sender.py`
5. Create drafts via `users().drafts().create()`
6. Update `main.py` to support `--method gmail`
7. Token stored in `token.json` (gitignored)

**Testing**:
- Verify Gmail draft appears in Gmail Drafts folder
- Draft shows correct To, Subject, and body

### 12.2 Stretch: LLM Email Rewriting (via Groq)

**PREREQ**: `groq` package + GROQ_API_KEY

**Files**: Add `llm_enhancer.py`, update `generator.py`

**Tasks**:
1. Implement `enhance_with_llm(email: Email) -> Email` using the `groq` SDK
2. Add safety guardrails: fact preservation, length enforcement
3. Use `llama-3.3-70b-versatile` model (fast, open-source, via Groq LPU)
4. Update `generator.py` to accept `use_llm=True` parameter
5. Cache LLM results to avoid repeated API calls

**Why Groq**:
- Ultra-low latency inference for real-time email rewriting
- Free tier available — no upfront cost for development
- OpenAI-compatible endpoint allows fallback if needed
- Models: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`, `gemma2-9b-it`

**Python Implementation (conceptual):**

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def enhance_with_llm(email: Email) -> Email:
    """Improve email tone via Groq-hosted LLM."""
    prompt = f"""
    Improve the following cold outreach email's tone to be more
    natural and professional. DO NOT change: names, company names,
    URLs, or facts. Keep it under 150 words. DO NOT add fake
    experience, referrals, or relationships.

    Original:
    {email.body}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    
    rewritten = chat_completion.choices[0].message.content
    email.body = rewritten
    email.word_count = count_words(rewritten)
    return email
```

**Prompt Template**:

```
You are improving a cold outreach email for a job application.
Improve the tone to be more natural and professional.
DO NOT change: names, company names, URLs, or facts.
Keep it under 150 words.
DO NOT add fake experience, referrals, or relationships.

Original email:
{email_body}
```

### 12.3 Stretch: Streamlit Web UI

**PREREQ**: `streamlit`

**Files**: Add `app.py`

**Tasks**:
1. File upload for JSON/CSV contacts
2. Contact table viewer (editable)
3. Email preview panel with word count
4. Send / Draft / Skip buttons per contact
5. Log viewer in sidebar
6. Progress bar for batch processing

### 12.4 Stretch: Spam-Risk Checker

**PREREQ**: None (pure Python)

**Files**: Add `spam_checker.py`, update `generator.py`

**Heuristics**:

| Check | Threshold | Score Impact |
|-------|-----------|--------------|
| Exclamation marks | > 3 | +20 points |
| ALL CAPS words | > 2 | +15 points |
| Link density | > 1 per 50 words | +10 points |
| Spam trigger words | present | +25 points |
| Personalization score | < 2 fields used | +30 points |
| Subject line length | < 5 chars | +5 points |

**Scoring**: 0-40 = Safe, 41-70 = Caution, 71+ = High Risk

### 12.5 Stretch: Follow-Up Email Generator

**Files**: Add `followup.py`, new templates `templates/followup1.txt`, `templates/followup2.txt`

**Tasks**:
1. Generate follow-up emails referencing the original
2. Track follow-up sequence in log
3. Recommend send timing (3-5 days after initial)

---

## Appendix: Dependency Installation Order

### MVP Dependencies

```bash
# Phase 0: Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Phase 0: Install core dependencies
pip install python-dotenv

# Phase 8: Install testing dependencies
pip install pytest
```

### Stretch Dependencies

```bash
# Gmail API
pip install google-api-python-client google-auth-oauthlib

# LLM Enhancement via Groq (recommended)
pip install groq

# Alternative: OpenAI SDK (compatible with Groq's base_url)
pip install openai

# Streamlit UI
pip install streamlit
```

### Full Install Command

```bash
pip install -r requirements.txt
```

---

## Quick Reference: File-by-File Implementation Order

| Order | File | Phase | Lines (est.) |
|-------|------|-------|-------------|
| 1 | `.env.example` | 0 | 15 |
| 2 | `.gitignore` | 0 | 20 |
| 3 | `requirements.txt` | 0 | 5 |
| 4 | `models.py` | 1 | 90 |
| 5 | `config.py` | 1 | 120 |
| 6 | `loader.py` | 1 | 130 |
| 7 | `templates/default.txt` | 2 | 15 |
| 8 | `generator.py` | 2 | 120 |
| 9 | `preview.py` | 3 | 90 |
| 10 | `logger.py` | 4 | 100 |
| 11 | `main.py` | 5 | 150 |
| 12 | `sender.py` | 6 | 120 |
| 13 | `opt_out.py` | 7 | 35 |
| 14 | `tests/test_models.py` | 8 | 70 |
| 15 | `tests/test_generator.py` | 8 | 55 |
| 16 | `tests/test_loader.py` | 8 | 65 |
| 17 | `tests/test_config.py` | 8 | 40 |
| 18 | `tests/test_logger.py` | 8 | 45 |
| 19 | `tests/test_sender.py` | 8 | 50 |
| 20 | `tests/test_integration.py` | 8 | 60 |
| 21 | `README.md` | 9 | 100 |
| 22 | `contacts.json` | 9 | 55 |

Total: ~1,550 lines of scaffolded, production-ready code.
