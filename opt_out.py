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
        print(f"  [OFF] Added {recipient_email} to opt-out list.")
