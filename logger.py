"""
Logging module for The Closer.
Records every email action to outreach_log.csv for auditability."""

import csv
from datetime import datetime
from pathlib import Path
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

    print(f"  [~] Logged: {entry.status} -> {entry.recipient_email} | {entry.company}")


def read_log() -> list[dict]:
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
        print("\n  [~] No log entries found.")
        return

    summary = get_log_summary()
    print("\n" + "=" * 60)
    print("  [~] Outreach Log -- Proof")
    print("=" * 60)

    for i, entry in enumerate(entries, 1):
        print(f"\n  {i}. {entry['company']} -- {entry['role']}")
        print(f"     To: {entry['recipient_email']}")
        print(f"     Subject: {entry['subject']}")
        print(f"     Status: {entry['status']}")
        print(f"     Time: {entry['timestamp']}")
        if entry["error_message"]:
            print(f"     Error: {entry['error_message']}")

    print("\n  " + "-" * 55)
    print(f"  Summary: {summary['total']} total | "
          f"{summary['sent']} sent | "
          f"{summary['drafted']} drafted | "
          f"{summary['skipped']} skipped | "
          f"{summary['failed']} failed")
    print("=" * 60 + "\n")
