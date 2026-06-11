"""
The Closer -- Cold Email Writer + Send Bot
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
from models import Email as EmptyEmail
from preview import preview_email
from logger import log_result, show_proof
from sender import send_email
from opt_out import is_opted_out
from preview import edit_email


def print_banner() -> None:
    """Print application banner."""
    print()
    print("=" * 48)
    print("  The Closer -- Cold Email Writer + Send Bot")
    print("=" * 48)
    print()


def print_summary(results: list[tuple]) -> None:
    """Print final summary of all actions."""
    print("\n" + "=" * 55)
    print("  Run Summary")
    print("=" * 55)

    total = len(results)
    sent = sum(1 for _, s in results if s == "sent")
    drafted = sum(1 for _, s in results if "draft" in s)
    skipped = sum(1 for _, s in results if s == "skipped")
    failed = sum(1 for _, s in results if s == "failed")

    print(f"\n  Total contacts processed: {total}")
    if sent:
        print(f"  [+] Sent: {sent}")
    if drafted:
        print(f"  [~] Drafted: {drafted}")
    if skipped:
        print(f"  [-] Skipped: {skipped}")
    if failed:
        print(f"  [!] Failed: {failed}")

    print(f"\n  [~] Log saved to: outreach_log.csv")
    print("=" * 55 + "\n")


def main() -> None:
    """Main orchestrator."""
    print_banner()

    # --- Handle --log flag ----------------------------
    cli_args = parse_cli_args()
    if cli_args.get("log"):
        show_proof()
        return

    # --- Load config ---------------------------------
    config = load_config()

    # Apply CLI overrides
    if cli_args.get("file"):
        config.data_source = cli_args["file"]
    if cli_args.get("dry_run") is not None:
        config.dry_run = cli_args["dry_run"]

    # Validate config
    errors = validate_config(config)
    if errors:
        print("  [!] Configuration errors:")
        for err in errors:
            print(f"     - {err}")
        sys.exit(1)

    # Show mode
    mode = "DRY RUN" if config.dry_run else "LIVE SEND"
    print(f"  Mode: {mode}")
    if config.dry_run:
        print(f"  No emails will be sent. Set DRY_RUN=false to send.")
    print()

    # --- Load contacts --------------------------------
    try:
        contacts = load_contacts(config.data_source)
    except FileNotFoundError as e:
        print(f"  [!] {e}")
        sys.exit(1)

    # Limit to max_emails_per_run
    contacts = contacts[: config.max_emails_per_run]
    print(f"  Loaded {len(contacts)} outreach target(s)\n")

    # --- Process each contact -------------------------
    results = []

    for i, contact in enumerate(contacts, 1):
        print(f"  {'-' * 50}")
        print(f"  Processing ({i}/{len(contacts)}): {contact.company} -- {contact.role}")
        print(f"  {'-' * 50}")

        # Generate email
        try:
            email = generate_email(contact)
            print(f"  [+] Email generated ({email.word_count} words)")
        except Exception as e:
            print(f"  [!] Generation failed: {e}")
            log_result(contact, EmptyEmail("", "", 0, contact), "failed", str(e))
            results.append((contact, "failed"))
            continue

        # Check opt-out
        if is_opted_out(contact.recipient_email):
            print(f"  [OFF] {contact.recipient_email} has opted out. Skipping.")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            continue

        # Preview and confirm
        action = preview_email(contact, email, i, len(contacts))

        if action == "quit":
            print("\n  [STOP] Quitting...")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            break

        if action == "edit":
            email = edit_email(email)
            # Re-display the updated preview so the user sees their changes
            action = preview_email(contact, email, i, len(contacts))
            if action == "quit":
                print("\n  [STOP] Quitting...")
                log_result(contact, email, "skipped")
                results.append((contact, "skipped"))
                break

        if action == "skip":
            print("  [-] Skipped.")
            log_result(contact, email, "skipped")
            results.append((contact, "skipped"))
            continue

        # Safety confirmation for real sends
        if not config.dry_run:
            confirm = input("\n  [!] Really send this email? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("  [-] Skipped.")
                log_result(contact, email, "skipped")
                results.append((contact, "skipped"))
                continue

        # Send or dry-run
        if config.dry_run:
            status = "drafted (dry_run)"
        else:
            print(f"  Sending to {contact.recipient_email}...")
            result = send_email(contact, email, config)
            status = result.status
            if result.error:
                log_result(contact, email, status, result.error)
                results.append((contact, status))
                continue

        log_result(contact, email, status)
        results.append((contact, status))

    # --- Summary --------------------------------------
    print_summary(results)

    # Show log file location
    if Path("outreach_log.csv").exists():
        print(f"  Tip: Run 'python main.py --log' to view the full outreach log.")


if __name__ == "__main__":
    main()
