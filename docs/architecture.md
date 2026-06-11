# The Closer — Architecture Document

> **Cold Email Writer + Send Bot** | Sprint 3 Architecture

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Module Design](#4-module-design)
5. [Data Flow](#5-data-flow)
6. [Data Models & Contracts](#6-data-models--contracts)
7. [Email Generation Engine](#7-email-generation-engine)
8. [Email Sending Architecture](#8-email-sending-architecture)
9. [Security & Safety Architecture](#9-security--safety-architecture)
10. [Configuration & Environment](#10-configuration--environment)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Testing Strategy](#12-testing-strategy)
13. [Demo Flow Architecture](#13-demo-flow-architecture)
14. [Stretch Goal Paths](#14-stretch-goal-paths)

---

## 1. System Overview

### What We're Building

**The Closer** is a CLI-based cold email generator and sender that helps job seekers create personalized outreach emails at scale. It takes job/contact information, generates structured cold emails following proven outreach patterns, previews them for human review, and sends or drafts them via the user's email account.

### Primary Goal

```text
Job Listing / Contact Info
        ↓
Personalization Extraction
        ↓
Cold Email Generation
        ↓
Human Review (Preview + Confirm)
        ↓
Send or Draft Email
        ↓
Proof in Sent Folder + Local Log
```

### Target User

A job seeker who wants to reach out to recruiters, hiring managers, founders, or employees about relevant roles — without writing every email from scratch.

---

## 2. Architecture Principles

| Principle | Description |
|-----------|-------------|
| **Safety First** | Human review is mandatory before every send. DRY_RUN is the default. |
| **Simplicity** | The stack should be explainable in a live demo. No over-engineering. |
| **Modularity** | Each concern (generation, sending, logging) is a separate module. |
| **Configuration over hardcoding** | Secrets, templates, and thresholds live in env vars or config files. |
| **Progressive enhancement** | Start with deterministic templates; layer on LLM capabilities later. |
| **Auditability** | Every email action is logged with timestamp, status, and error info. |
| **Low volume by design** | The system is built for thoughtful, personalized outreach — not spam. |

---

## 3. High-Level Architecture

### 3.1 Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         main.py (Orchestrator)                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Data Loader  │  │   Preview    │  │   Logger     │           │
│  │  (FR1)        │  │   Manager    │  │   (FR5)      │           │
│  │               │  │   (FR3)      │  │              │           │
│  │  Loads from   │  │  Displays    │  │  Writes to   │           │
│  │  JSON/CSV/    │  │  email &     │  │  outreach_   │           │
│  │  dict         │  │  asks confirm │  │  log.csv     │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│  ┌──────────────────────────────────────────────────┐            │
│  │              Email Generator (FR2)                │            │
│  │  - Template-based generation                     │            │
│  │  - Optional: LLM rewriting                       │            │
│  │  - Optional: Spam-risk check                     │            │
│  └──────────────────────┬───────────────────────────┘            │
│                         │                                         │
│                         ▼                                         │
│  ┌──────────────────────────────────────────────────┐            │
│  │              Email Sender (FR4)                   │            │
│  │  - SMTP via smtplib (MVP)                        │            │
│  │  - Gmail API OAuth2 (stretch)                    │            │
│  │  - DRY_RUN mode (default)                        │            │
│  └──────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Module Dependency Graph

```
contacts.json/jobs.csv
        │
        ▼
┌──────────────┐
│  Data Loader  │
│  (loader.py)  │
└──────┬───────┘
       │ List[Contact]
       ▼
┌──────────────┐     ┌──────────────┐
│  Email Gen.   │────▶│  Templates   │
│  (generator)  │     │  (templates) │
└──────┬───────┘     └──────────────┘
       │ Email(subject, body)
       ▼
┌──────────────┐
│  Preview      │
│  (preview)    │
└──────┬───────┘
       │ User confirms (yes/no)
       ▼
┌──────────────┐     ┌──────────────┐
│  Email Sender │────▶│  SMTP/Gmail  │
│  (sender)     │     │  API         │
└──────┬───────┘     └──────────────┘
       │ Status (sent/drafted/failed)
       ▼
┌──────────────┐
│  Logger      │
│  (logger)    │
└──────────────┘
       │
       ▼
 outreach_log.csv
```

---

## 4. Module Design

### 4.1 Module Overview

| Module | File | Responsibility |
|--------|------|----------------|
| **Orchestrator** | `main.py` | Entry point; loads data, loops through contacts, orchestrates the pipeline |
| **Data Loader** | `loader.py` | Reads contacts from JSON, CSV, or hardcoded list; validates required fields |
| **Email Generator** | `generator.py` | Produces subject + body from a contact record using templates |
| **Email Sender** | `sender.py` | Sends or drafts email via SMTP or Gmail API; respects DRY_RUN |
| **Preview Manager** | `preview.py` | Displays formatted email preview; handles user confirmation input |
| **Logger** | `logger.py` | Appends structured log entries to `outreach_log.csv` |
| **Config** | `config.py` | Loads and validates environment variables from `.env` |
| **Models** | `models.py` | Data classes / type definitions for Contacts, Email, LogEntry |

### 4.2 Detailed Module Specifications

#### 4.2.1 Orchestrator (`main.py`)

```
Purpose:         Entry point that runs the full pipeline
Responsibilities:
                 - Load configuration
                 - Load contacts from data source
                 - For each contact:
                     1. Generate email
                     2. Preview email
                     3. Ask for confirmation
                     4. Send/draft or skip
                     5. Log result
                 - Print summary at end
Input:           CLI arguments (optional: --file, --dry-run, --send-mode)
Output:          Terminal output + outreach_log.csv
```

**Pseudocode:**

```python
def main():
    config = load_config()
    contacts = load_contacts(config.data_source)
    
    results = []
    for contact in contacts:
        email = generate_email(contact)

        if not preview_email(contact, email):
            log_result(contact, email, "skipped")
            results.append("skipped")
            continue

        if config.dry_run:
            status = "drafted (dry_run)"
        else:
            status = send_email(contact, email, config)

        log_result(contact, email, status)
        results.append(status)
    
    print_summary(results)
```

#### 4.2.2 Data Loader (`loader.py`)

```
Purpose:         Load and validate outreach target records
Responsibilities:
                 - Detect input format (JSON, CSV, inline list)
                 - Parse records into Contact data class
                 - Validate required fields are present
                 - Return List[Contact]
Supported Sources:
                 - Hardcoded Python list (MVP / live demo)
                 - contacts.json
                 - jobs.csv
Validation Rules:
                 - Required: recipient_email, company, role,
                             candidate_name, candidate_background
                 - Email format validation (basic regex)
                 - Skip records missing required fields (with warning)
```

**Interface:**

```python
def load_contacts(source: str | None = None) -> List[Contact]:
    """Load contacts from file or return default demo contacts."""
    ...

def load_from_json(path: str) -> List[Contact]:
    """Parse contacts.json into Contact objects."""
    ...

def load_from_csv(path: str) -> List[Contact]:
    """Parse jobs.csv into Contact objects."""
    ...

def get_demo_contacts() -> List[Contact]:
    """Return 3-5 hardcoded demo contacts for live demo."""
    ...
```

#### 4.2.3 Email Generator (`generator.py`)

```
Purpose:         Generate personalized cold email from a contact record
Responsibilities:
                 - Apply template with contact variables
                 - Ensure all cold email anatomy requirements are met
                 - Keep output under 150 words
                 - Support multiple template variations (optional)
                 - Support LLM rewriting (optional)
Output:          Email(subject: str, body: str, word_count: int)
```

**Template System Architecture:**

The template system uses Python f-strings with named variables. Templates are stored in a `templates/` directory or defined as constants.

```
Template Anatomy:
                 1. Subject Line: Short, specific, role/company related
                 2. Personalization Hook: "I noticed {company} is hiring..."
                 3. Introduction: Who the sender is
                 4. Value/Fit Statement: Background → role connection
                 5. Clear Ask: Request for chat, referral, or review
                 6. Sign-Off: Name + optional portfolio/linkedin link
```

**Interface:**

```python
@dataclass
class Email:
    subject: str
    body: str
    word_count: int
    contact: Contact

def generate_email(contact: Contact, template_name: str = "default") -> Email:
    """Generate a personalized cold email."""
    ...

def render_template(template: str, contact: Contact) -> str:
    """Fill template variables from contact record."""
    ...

def count_words(text: str) -> int:
    """Count words in email body (enforce 150-word limit)."""
    ...
```

**Default Template (Conceptual):**

```
Subject: Quick note on the {role} role at {company}

Hi {recipient_name},

I noticed {company} is hiring for {role}. {personalization_note}

I'm {candidate_name}, and I've been building projects around
{candidate_background}. The role stood out because it connects closely
with my interest in practical automation and product-focused engineering.

Would you be open to a quick look at my profile or pointing me
to the right person?

Best,
{candidate_name}
{portfolio_url}
```

**Template Validation Rules:**

| Rule | Enforcement |
|------|-------------|
| Max 150 words | `word_count` field; warn if exceeded |
| Has personalization | Must use at least 2 contact-specific fields |
| Has clear ask | Template must include an ask sentence |
| No fake claims | No variable for fabricated experience |
| Professional sign-off | Template must include name + optional link |

#### 4.2.4 Preview Manager (`preview.py`)

```
Purpose:         Display email preview and handle user confirmation
Responsibilities:
                 - Format email for terminal display with clear separation
                 - Show metadata (to, subject, word count)
                 - Prompt user for action: send / draft / skip / quit
Input:           Contact + Email
Output:          User decision (bool + action type)
```

**Confirmation Flow:**

```text
═══════════════════════════════════════════════════════
📧 Email Preview (1 of 5)

  To:      priya@example.com
  Company: Acme AI
  Role:    Backend Engineering Intern

  Subject: Quick note on the Backend Engineering Intern role

  ─────────────────────────────────────────────────────
  Hi Priya,

  I noticed Acme AI is hiring for a Backend Engineering
  Intern role. I was especially interested to hear about
  your recent AI workflow automation product launch.

  I'm Alex Chen, and I've been building projects around
  Python automation and AI agents. This role connects
  closely with my background in building practical,
  product-focused automation tools.

  Would you be open to a 10-minute chat about the role?

  Best,
  Alex Chen
  https://github.com/alexchen
  ─────────────────────────────────────────────────────

  📊 Word count: 98/150

  ┌─ Actions ──────────────────────────────────────┐
  │  [s] Send        [d] Draft only                │
  │  [k] Skip        [q] Quit                      │
  │  [e] Edit email                                │
  └────────────────────────────────────────────────┘

  Your choice (s/d/k/q/e):
```

**Interface:**

```python
def preview_email(contact: Contact, email: Email, index: int, total: int) -> str:
    """Display preview and return user action: 'send', 'draft', 'skip', 'quit', 'edit'."""
    ...

def get_user_action() -> str:
    """Get normalized user input (s/d/k/q/e)."""
    ...
```

#### 4.2.5 Email Sender (`sender.py`)

```
Purpose:         Send or draft email using configured provider
Responsibilities:
                 - Connect to SMTP or Gmail API
                 - Send email with proper headers (From, To, Subject)
                 - Support DRY_RUN mode (log only, no send)
                 - Return status (sent/drafted/failed + error)
                 - Handle connection errors gracefully
Supported Modes:
                 - DRY_RUN (default): Log what would be sent
                 - SMTP: Send via smtplib with app password
                 - Gmail API: Create draft (optional stretch)
```

**Sender Strategy Pattern:**

```python
from abc import ABC, abstractmethod

class EmailSenderStrategy(ABC):
    @abstractmethod
    def send(self, contact: Contact, email: Email) -> SendResult: ...

    @abstractmethod
    def draft(self, contact: Contact, email: Email) -> SendResult: ...

class DryRunSender(EmailSenderStrategy):
    """Logs intent without sending."""

class SmtpSender(EmailSenderStrategy):
    """Sends via SMTP (smtplib)."""

class GmailApiSender(EmailSenderStrategy):
    """Creates Gmail drafts via Gmail API."""

def get_sender(config: Config) -> EmailSenderStrategy:
    """Factory: returns appropriate sender based on config."""
    if config.dry_run:
        return DryRunSender()
    elif config.send_method == "smtp":
        return SmtpSender(...)
    elif config.send_method == "gmail":
        return GmailApiSender(...)
```

**SMTP Implementation Details:**

```python
def send_via_smtp(contact: Contact, email: Email, config: Config) -> SendResult:
    """Send email via SMTP with proper MIME formatting."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{config.sender_name} <{config.smtp_user}>"
        msg["To"] = contact.recipient_email
        msg["Subject"] = email.subject
        msg.attach(MIMEText(email.body, "plain"))

        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)

        return SendResult(status="sent")
    except Exception as e:
        return SendResult(status="failed", error=str(e))
```

**Gmail API Draft Implementation (Conceptual):**

```python
def create_gmail_draft(contact: Contact, email: Email, service) -> SendResult:
    """Create a Gmail draft using the Gmail API."""
    message = create_rfc822_message(contact, email)
    draft = {"message": {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}}
    created = service.users().drafts().create(userId="me", body=draft).execute()
    return SendResult(status="drafted", draft_id=created["id"])
```

#### 4.2.6 Logger (`logger.py`)

```
Purpose:         Record every email action for auditability
Responsibilities:
                 - Append structured entries to outreach_log.csv
                 - Include all required fields
                 - Handle concurrent append safely
                 - Provide summary statistics
                 - Support reading log for proof
```

**Log Schema (CSV):**

```csv
timestamp,recipient_email,company,role,subject,status,error_message
2025-06-11T10:30:00,priya@example.com,Acme AI,Backend Engineering Intern,"Quick note on the Backend Engineering Intern role",sent,
2025-06-11T10:31:00,john@startup.io,StartupXYZ,Frontend Developer,"Excited about the Frontend role at StartupXYZ",skipped,
2025-06-11T10:32:00,sarah@bigcorp.com,BigCorp,Data Scientist,"",failed,Connection refused
```

**Interface:**

```python
@dataclass
class LogEntry:
    timestamp: datetime
    recipient_email: str
    company: str
    role: str
    subject: str
    status: str  # generated, drafted, sent, skipped, failed
    error_message: str = ""

def log_result(contact: Contact, email: Email, status: str, error: str = "") -> None:
    """Append a log entry to outreach_log.csv."""
    ...

def get_log_summary() -> dict:
    """Return summary stats: total, sent, drafted, skipped, failed."""
    ...

def show_proof() -> None:
    """Display or open the log file for proof of sent/drafted emails."""
    ...
```

#### 4.2.7 Config (`config.py`)

```
Purpose:         Centralized configuration management
Responsibilities:
                 - Load .env file using python-dotenv
                 - Validate required variables are present
                 - Provide typed access to config values
                 - Support defaults for optional variables
```

**Interface:**

```python
@dataclass
class Config:
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Sender
    sender_name: str = ""
    dry_run: bool = True
    send_method: str = "smtp"  # smtp, gmail

    # Data source
    data_source: str = ""  # path to JSON/CSV, or empty for demo

    # Limits
    max_emails_per_run: int = 10
    max_words_per_email: int = 150

def load_config(env_file: str = ".env") -> Config:
    """Load and validate configuration from environment."""
    ...

def validate_config(config: Config) -> list[str]:
    """Return list of validation errors (empty if valid)."""
    ...
```

### 4.3 Folder Structure (Extended)

```
the-closer/
│
├── main.py                  # Entry point / orchestrator
├── loader.py                # Data loading (JSON, CSV, demo)
├── generator.py             # Email generation engine
├── sender.py                # Email sending (SMTP, Gmail API, dry-run)
├── preview.py               # Preview display & user confirmation
├── logger.py                # CSV logging
├── config.py                # Configuration & env vars
├── models.py                # Data classes (Contact, Email, LogEntry, etc.)
│
├── templates/               # Email templates directory
│   ├── default.txt          # Default cold email template
│   └── technical.txt        # Tech-focused variant (optional)
│
├── contacts.json            # Sample outreach targets
├── contacts_demo.json       # Built-in demo contacts
├── outreach_log.csv         # Generated log file
│
├── .env                     # Local secrets (gitignored)
├── .env.example             # Template for env vars
├── requirements.txt         # Python dependencies
├── README.md                # Documentation
│
├── tests/                   # Test suite
│   ├── test_loader.py
│   ├── test_generator.py
│   ├── test_sender.py
│   ├── test_logger.py
│   └── test_config.py
│
└── docs/                    # Documentation
    ├── problemStatement.md
    └── architecture.md
```

---

## 5. Data Flow

### 5.1 End-to-End Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Load     │────▶│ Generate │────▶│ Preview  │────▶│  Send     │────▶│  Log     │
│  Contacts │     │  Email   │     │  + Confirm│     │  or Draft │     │  Result  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │                │
     ▼                ▼                ▼                ▼                ▼
 Contact        Email(subject,   User sees        SMTP/Gmail       outreach_
 objects         body, wc)       email +          sends or         log.csv
                                 decides          drafts           appended
```

### 5.2 Per-Contact State Machine

```
                    ┌─────────┐
                    │  LOADED  │
                    └────┬────┘
                         │
                         ▼
                    ┌──────────┐
              ┌────▶│ GENERATED│◀────┐
              │     └─────┬────┘     │
              │           │          │
              │           ▼          │
              │     ┌──────────┐     │
              │     │ PREVIEWED│     │
              │     └─────┬────┘     │
              │           │          │
              │      ┌────┴────┐     │
              │      │         │     │
              │      ▼         ▼     │
              │  ┌──────┐ ┌───────┐  │
              │  │SEND  │ │ SKIP  │  │
              │  │/DRAFT│ │       │  │
              │  └──┬───┘ └───┬───┘  │
              │     │         │      │
              │     ▼         │      │
              │  ┌──────┐     │      │
              │  │DONE  │◀────┘      │
              │  └──────┘            │
              │                      │
              └──────────────────────┘
                 (RETRY on failure)
```

---

## 6. Data Models & Contracts

### 6.1 Contact (Input Record)

```python
@dataclass
class Contact:
    """A single outreach target."""
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
```

**Validation Rules:**

| Field | Rule |
|-------|------|
| `recipient_email` | Must be valid email format; required |
| `company` | Non-empty string; required |
| `role` | Non-empty string; required |
| `candidate_name` | Non-empty string; required |
| `candidate_background` | Non-empty string; required |
| `recipient_name` | If empty, fall back to "there" or infer from email |

### 6.2 Email (Generated Output)

```python
@dataclass
class Email:
    """A generated cold email."""
    subject: str
    body: str
    word_count: int
    contact: Contact  # Reference back to source
```

**Validation Rules:**

| Rule | Threshold | Action |
|------|-----------|--------|
| Max word count | 150 words | Warn but allow override |
| Has subject | Non-empty | Block if empty |
| Has personalization | Uses ≥2 unique contact fields | Warn if under-personalized |

### 6.3 SendResult

```python
@dataclass
class SendResult:
    """Result of a send/draft attempt."""
    status: str           # "sent", "drafted", "skipped", "failed"
    error: str = ""       # Error message if failed
    draft_id: str = ""    # Gmail draft ID if applicable
    timestamp: datetime = field(default_factory=datetime.now)
```

### 6.4 LogEntry

```python
@dataclass
class LogEntry:
    """Persistent log of an email action."""
    timestamp: str
    recipient_email: str
    company: str
    role: str
    subject: str
    status: str           # generated, drafted, sent, skipped, failed
    error_message: str = ""
```

---

## 7. Email Generation Engine

### 7.1 Template Anatomy

Every generated email follows this structured anatomy:

```
┌─────────────────────────────────────────────────────┐
│ 1. Subject Line                                      │
│    → Short, specific, related to role/company        │
│    → e.g., "Quick note on the Backend Intern role"   │
├─────────────────────────────────────────────────────┤
│ 2. Personalization Hook                              │
│    → One sentence showing company/role knowledge      │
│    → e.g., "I noticed Acme AI recently launched..."  │
├─────────────────────────────────────────────────────┤
│ 3. Relevant Introduction                             │
│    → Who the sender is + why relevant                │
│    → e.g., "I'm Alex, building projects in Python"   │
├─────────────────────────────────────────────────────┤
│ 4. Value / Fit Statement                             │
│    → 1-2 lines connecting background to role         │
│    → e.g., "My experience with automation aligns..." │
├─────────────────────────────────────────────────────┤
│ 5. One Clear Ask                                     │
│    → Quick chat, referral, or direction              │
│    → e.g., "Would you be open to a 10-minute chat?"  │
├─────────────────────────────────────────────────────┤
│ 6. Simple Sign-Off                                   │
│    → Name + portfolio/linkedin link                  │
└─────────────────────────────────────────────────────┘
```

### 7.2 Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{recipient_name}` | `contact.recipient_name` | "Priya Sharma" |
| `{company}` | `contact.company` | "Acme AI" |
| `{role}` | `contact.role` | "Backend Engineering Intern" |
| `{candidate_name}` | `contact.candidate_name` | "Alex Chen" |
| `{candidate_background}` | `contact.candidate_background` | "Python developer interested in automation" |
| `{personalization_note}` | `contact.personalization_note` | "Company recently launched an AI workflow automation product" |
| `{portfolio_url}` | `contact.portfolio_url` | "https://github.com/alexchen" |
| `{job_url}` | `contact.job_url` | "https://example.com/job" |
| `{linkedin_url}` | `contact.linkedin_url` | "https://linkedin.com/in/alexchen" |

### 7.3 Template Variations (Stretch)

```python
TEMPLATES = {
    "default": """...""",
    "technical": """...""",
    "referral_request": """...""",
    "startup_focus": """...""",
}
```

| Template | Best For | Key Difference |
|----------|----------|----------------|
| `default` | General outreach | Balanced structure |
| `technical` | Engineering roles | Emphasizes projects & skills |
| `referral_request` | Warm introductions | Asks for referral, not chat |
| `startup_focus` | Startup/early-stage | Shorter, more direct |

### 7.4 LLM Enhancement Layer (Stretch)

Uses [Groq](https://groq.com) — a high-performance, ultra-low-latency inference API for open-source LLMs. Groq offers OpenAI-compatible endpoints, so the Python `openai` SDK can also be used via `base_url` override, but the recommended approach is the official `groq` Python SDK.

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def enhance_with_llm(email: Email) -> Email:
    """Use Groq-hosted LLM to improve tone and naturalness while preserving facts."""
    prompt = f"""
    Improve the following cold email's tone to be more natural and professional.
    Keep all facts, names, and URLs exactly the same.
    Keep it under 150 words.
    Do not add fake experience, referrals, or relationships.

    Original:
    Subject: {email.subject}
    Body: {email.body}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",  # Fast open-source model via Groq
    )
    
    rewritten_body = chat_completion.choices[0].message.content
    # Validate: ensure no facts were changed
    ...
```

**Why Groq over OpenAI / Claude:**

| Factor | Groq | OpenAI / Claude |
|--------|------|----------------|
| **Speed** | Ultra-low latency (LPU architecture) | Variable, often slower |
| **Cost** | Free tier available; very competitive | Pay-per-token, more expensive |
| **Models** | llama-3.3-70b, mixtral-8x7b, gemma2-9b | GPT-4o, Claude 3.5 Sonnet |
| **OpenAI-compatible** | Yes (via base_url override) | Native |
| **API Key** | `GROQ_API_KEY` | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` |
| **SDK** | `groq` Python package | `openai` / `anthropic` |

---

## 8. Email Sending Architecture

### 8.1 Sending Strategy Decision Tree

```
                    ┌─────────────────────┐
                    │  User Config         │
                    │  send_method +       │
                    │  dry_run flag        │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
               dry_run=True          dry_run=False
                    │                     │
                    ▼                     ▼
            ┌──────────────┐    ┌──────────────────┐
            │  DryRunSender │    │  RealSender       │
            │  (log only)   │    │  (choose method)  │
            └──────────────┘    └────────┬─────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          │                              │
                    send_method="smtp"           send_method="gmail"
                          │                              │
                          ▼                              ▼
                  ┌──────────────┐            ┌──────────────────┐
                  │  SmtpSender   │            │  GmailApiSender   │
                  │  (smtplib)   │            │  (Google API)     │
                  └──────────────┘            └──────────────────┘
```

### 8.2 SMTP Sender (MVP)

**Technical Requirements:**

- Python `smtplib` + `email.mime` from standard library
- Gmail App Password for authentication
- STARTTLS for encryption
- Proper MIME formatting with From, To, Subject headers
- Error handling for connection failures, auth failures, send failures

**Gmail SMTP Settings:**

| Setting | Value |
|---------|-------|
| Host | `smtp.gmail.com` |
| Port | `587` |
| Encryption | `STARTTLS` |
| Auth | App Password (requires 2FA enabled) |

**Send Flow:**

```python
def send(contact, email, config):
    1. Create MIMEMultipart message
    2. Set From / To / Subject headers
    3. Attach plain-text body
    4. Connect to SMTP server with STARTTLS
    5. Authenticate with app password
    6. Send message
    7. Close connection
    8. Return SendResult(status="sent")
```

### 8.3 Gmail API Draft Sender (Stretch)

**Technical Requirements:**

- `google-api-python-client` and `google-auth-oauthlib` packages
- OAuth 2.0 credentials from Google Cloud Console
- Gmail API enabled in GCP project
- Scopes: `https://www.googleapis.com/auth/gmail.compose`

**OAuth Flow:**

```python
1. Load client_secret.json (downloaded from GCP)
2. Open browser for user authorization
3. Receive authorization code → exchange for access token
4. Use token to create authenticated Gmail API service
5. Call service.users().drafts().create() for each email
```

---

## 9. Security & Safety Architecture

### 9.1 Guardrails

| Guardrail | Implementation | Enforced At |
|-----------|---------------|-------------|
| Human review required | Preview step blocks send without confirmation | `preview.py` |
| Low-volume default | Config limit: `max_emails_per_run=10` | `config.py` |
| Personalization required | Validates ≥2 custom fields used | `generator.py` |
| No deceptive identity | Sender name/email from config, not generated | `sender.py` |
| No fake claims | Template system prevents fabricated variables | `generator.py` |
| DRY_RUN by default | `DRY_RUN=true` unless explicitly changed | `config.py` |

### 9.2 Sensitive Data Handling

| Data Type | Handling |
|-----------|----------|
| SMTP credentials | Stored in `.env` (gitignored) only |
| App passwords | Never hardcoded; never committed |
| Gmail OAuth tokens | Stored in `token.json` (gitignored) |
| Contact data | Stored in local files only |
| Logged emails | CSV format, local only |

### 9.3 `.gitignore` Rules

```gitignore
.env
token.json
*.log
outreach_log.csv
__pycache__/
*.pyc
```

### 9.4 Opt-Out Mechanism

```python
# opt_out.txt — one email per line
# priya@example.com
# ...

def is_opted_out(recipient_email: str) -> bool:
    """Check if recipient has opted out of contact."""
    ...

def add_opt_out(recipient_email: str) -> None:
    """Add recipient to opt-out list."""
    ...
```

---

## 10. Configuration & Environment

### 10.1 Environment Variables

```env
# ─── SMTP Configuration ───────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# ─── Sender Identity ─────────────────────────────
SENDER_NAME=Your Name

# ─── Mode ────────────────────────────────────────
DRY_RUN=true                          # true = log only, false = actually send
SEND_METHOD=smtp                       # smtp | gmail

# ─── Data Source ─────────────────────────────────
DATA_SOURCE=contacts.json              # path or empty for demo contacts

# ─── Limits ──────────────────────────────────────
MAX_EMAILS_PER_RUN=10
MAX_WORDS_PER_EMAIL=150
```

### 10.2 `.env.example` (Committed)

The example file committed to the repository should have placeholder values and clear instructions for each variable.

---

## 11. Implementation Roadmap

### Phase 1: Foundation (MVP)

```
Goal: Working CLI pipeline with demo data and dry-run mode
Time: 1-2 sessions
Files: main.py, models.py, config.py, loader.py, generator.py,
       preview.py, logger.py, .env.example, requirements.txt
```

| Step | Task | Deliverable |
|------|------|-------------|
| 1.1 | Create project structure and `models.py` | Data classes defined |
| 1.2 | Implement `config.py` with `.env` loading | Config loads correctly |
| 1.3 | Implement `loader.py` with demo contacts | 3-5 sample contacts loadable |
| 1.4 | Implement `generator.py` with default template | Emails generated from contacts |
| 1.5 | Implement `preview.py` with confirmation UI | Preview + yes/no works |
| 1.6 | Implement `logger.py` with CSV output | Log file created |
| 1.7 | Implement `main.py` orchestrator | Full pipeline runs end-to-end |
| 1.8 | Test with `DRY_RUN=true` | Verified all 5 contacts processed |

### Phase 2: Real Sending

```
Goal: Actually send or draft emails via SMTP
```

| Step | Task | Deliverable |
|------|------|-------------|
| 2.1 | Implement `sender.py` with SMTP support | Email sends via SMTP |
| 2.2 | Add Gmail App Password instructions to README | User can set up credentials |
| 2.3 | Test with own email as recipient | Verified delivery |
| 2.4 | Add error handling and retry logic | Graceful failure handling |

### Phase 3: Polish

```
Goal: Production-ready safety, documentation, and testing
```

| Step | Task | Deliverable |
|------|------|-------------|
| 3.1 | Add opt-out mechanism | Respects opt-out list |
| 3.2 | Add validation tests for all modules | Test suite passes |
| 3.3 | Write README with setup & usage instructions | README complete |
| 3.4 | Add CSV import support | Loads from `contacts.json` and `jobs.csv` |
| 3.5 | Add email editing during preview | User can edit before send |

### Phase 4: Stretch Goals

```
Goal: LLM enhancement, UI, and advanced features
```

| Step | Task | Deliverable |
|------|------|-------------|
| 4.1 | Gmail API draft creation | Gmail drafts created |
| 4.2 | LLM-powered rewriting | Improved email tone |
| 4.3 | Multiple template variations | User can choose template style |
| 4.4 | Spam-risk checker | Flags potentially problematic emails |
| 4.5 | Streamlit frontend | Web UI for non-technical users |
| 4.6 | Follow-up email generator | Sequential follow-up series |

---

## 12. Testing Strategy

### 12.1 Unit Tests

| Module | Test Cases |
|--------|------------|
| `loader.py` | Loads JSON correctly; loads CSV correctly; handles missing fields; returns demo contacts when no source; rejects invalid emails |
| `generator.py` | Generates email with all fields; enforces 150-word limit; uses personalization variables; handles missing optional fields |
| `preview.py` | Displays correctly formatted output; accepts valid inputs; rejects invalid inputs |
| `sender.py` | DryRunSender logs without sending; SmtpSender formats MIME correctly; handles SMTP connection errors |
| `logger.py` | Appends to CSV; handles missing file; reads back entries; summary stats correct |
| `config.py` | Loads env vars; applies defaults; validates required fields |

### 12.2 Integration Tests

- Full pipeline with dry run: 5 contacts → generated → previewed → logged
- Full pipeline with actual SMTP send (to test email)
- CSV file input → full pipeline
- JSON file input → full pipeline

### 12.3 Test Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_generator.py -v

# Run integration test
python -m pytest tests/test_integration.py -v

# Manual end-to-end test
python main.py --dry-run
```

---

## 13. Demo Flow Architecture

### 13.1 Live Demo Sequence (For Teaching)

```
Step 1: Create Sample Data
─────────────────────────
Action: loader.py returns 3 hardcoded contacts
Output: "Loaded 3 outreach targets"
Visual: Print contacts nicely formatted

Step 2: Build the Generator
───────────────────────────
Action: generator.py processes each contact
Output: "Generated: Quick note on the {role} role at {company}"
Visual: Show subject + body in terminal

Step 3: Add Preview
───────────────────
Action: preview.py displays formatted email
Output: Formatted email with To, Subject, Body, Word Count
Visual: Clear terminal output with dividers

Step 4: Add Confirmation
─────────────────────────
Action: preview.py prompts user
Prompt: "Send this email? (yes/no): "
Visual: Inline prompt with colored options

Step 5: Add Email Sending
─────────────────────────
Action: sender.py with DRY_RUN=true
Output: "[DRY RUN] Would send to priya@example.com"
Visual: Status line per contact

Step 6: Add Logging
───────────────────
Action: logger.py appends to CSV
Output: "outreach_log.csv updated"
Visual: Show log file contents

Step 7: Turn Off Dry Run
─────────────────────────
Action: Set DRY_RUN=false in .env
Output: "Email sent to yourname@gmail.com"
Visual: Check Gmail Sent folder

Step 8: Show Proof
──────────────────
Action: logger.show_proof()
Output: Formatted log table showing 3 sent/drafted emails
Visual: Screenshot of Sent folder or Drafts folder
```

### 13.2 CLI Command Interface

```bash
# Run with demo contacts (dry run)
python main.py

# Run with custom data file
python main.py --file contacts.json

# Run with CSV input
python main.py --file jobs.csv

# Run with explicit dry-run mode
python main.py --dry-run

# Run to actually send
python main.py --send

# Run with specific send method
python main.py --send --method smtp

# Show log file
python main.py --log

# Show help
python main.py --help
```

---

## 14. Stretch Goal Paths

### 14.1 Gmail API Integration

```text
Requirements:
  - google-api-python-client
  - google-auth-oauthlib
  - GCP project with Gmail API enabled
  - OAuth 2.0 Desktop credentials

Implementation:
  - Add GmailApiSender class to sender.py
  - Add OAuth flow in config.py (or separate auth.py)
  - Store token in token.json
  - Create drafts vs. send based on config
  - Add scope: https://www.googleapis.com/auth/gmail.compose
```

### 14.2 Streamlit Frontend

```text
Architecture:
  - Streamlit app (app.py) wraps the core pipeline
  - File upload for contacts (CSV/JSON)
  - Side-by-side preview
  - Send button with confirmation dialog
  - Log viewer in sidebar

Components:
  - File uploader widget
  - Contact table view
  - Email preview panel
  - Send/Draft/Skip buttons
  - Log panel with export
```

### 14.3 LLM Enhancement

```text
Integration Points:
  - Post-generation: Rewrite email for natural tone
  - Pre-generation: Generate personalization from job URL
  - Template selection: LLM picks best template variant

Guardrails:
  - Fact preservation: LLM cannot change names, companies, URLs
  - Length enforcement: Enforce 150-word limit after rewrite
  - Hallucination check: Verify no fabricated claims added

Supported Providers:
  - **Groq API** (recommended) — llama-3.3-70b-versatile, mixtral-8x7b-32768
  - OpenAI API (via Groq's compatible endpoint or directly)
  - Local model (Ollama) for offline use
```

### 14.4 Spam-Risk Checker

```text
Heuristics:
  - Exclamation mark count > 3 → flag
  - ALL CAPS words > 2 → flag
  - Link density > 1 per 50 words → flag
  - Spam trigger words present → flag
  - Personalization score < 2 → flag

Output: Risk score (0-100) + flagged reasons
```

---

## Appendix A: Dependency Table

| Package | Version | Purpose | Required For |
|---------|---------|---------|--------------|
| `python-dotenv` | ≥1.0 | Load `.env` files | MVP |
| `pytest` | ≥7.0 | Testing | Testing |
| `google-api-python-client` | ≥2.0 | Gmail API | Stretch |
| `google-auth-oauthlib` | ≥1.0 | Gmail OAuth | Stretch |
| `groq` | ≥0.10 | LLM enhancement via Groq API | Stretch |
| `openai` | ≥1.0 | Alternative LLM (via Groq base_url) | Stretch |
| `streamlit` | ≥1.28 | Web UI | Stretch |

## Appendix B: Error Handling Strategy

| Error Type | Handling | User Message |
|-----------|----------|-------------|
| Missing env var | Validate at startup, exit with guidance | "Missing SMTP_USER. Add to .env" |
| SMTP connection failure | Retry once, then log as failed | "Connection failed: {error}" |
| SMTP auth failure | Log as failed, don't retry | "Authentication failed. Check your app password." |
| Invalid contact data | Skip record with warning | "Skipping invalid record: missing recipient_email" |
| File not found | Fall back to demo contacts | "contacts.json not found. Using demo contacts." |
| Template rendering error | Use fallback template | "Template error. Using fallback." |

## Appendix C: Cold Email Best Practices Summary

Based on 2024-2025 research:

1. **Subject Line**: 5-8 words, specific, no clickbait
2. **Length**: 80-120 words ideal; 150 max
3. **Personalization**: Must reference company or role specifically
4. **CTA**: One clear ask only (10-min chat, referral, or guidance)
5. **Tone**: Professional but natural — not overly formal or salesy
6. **Timing**: Send Tue-Thu, 10-11am or 2-3pm
7. **Follow-up**: Plan for 2-3 follow-ups at 3-5 day intervals
8. **Proof**: Always include portfolio/GitHub/LinkedIn
