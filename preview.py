"""
Preview and confirmation manager for The Closer.
Displays generated emails and handles user action input."""

from models import Contact, Email


def edit_email(email: Email) -> Email:
    """
    Allow user to edit subject and body before sending.
    Returns updated Email with recalculated word count."""
    print("\n  [~] Edit mode -- press Enter to keep current value.\n")

    new_subject = input(f"  Subject [{email.subject}]: ").strip()
    if new_subject:
        email.subject = new_subject

    print(f"\n  Current body:\n{email.body}\n")
    print("  Enter new body (Enter newline + '.' + Enter to finish):")
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

    print(f"  [+] Email updated ({email.word_count} words)")
    return email


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
        User action string: "send", "skip", "edit", "quit"
    """
    _display_email(contact, email, index, total)
    return _get_user_action()


def _display_email(contact: Contact, email: Email, index: int, total: int) -> None:
    """Format and print email preview to terminal."""
    separator = "=" * 55

    print(f"\n{separator}")
    print(f"  Email Preview ({index} of {total})")
    print(f"{separator}")
    print(f"\n  To:      {contact.recipient_email}")
    print(f"  Company: {contact.company}")
    print(f"  Role:    {contact.role}")
    print(f"\n  Subject: {email.subject}")
    print(f"\n  {'-' * 50}")
    print(f"\n{email.body}")
    print(f"\n  {'-' * 50}")
    print(f"\n  Word count: {email.word_count}/150")

    # Show warnings if any
    warnings = email.warnings()
    if warnings:
        print(f"\n  Warnings:")
        for w in warnings:
            print(f"     - {w}")

    print(f"{separator}\n")


def _get_user_action() -> str:
    """Get normalized user action input."""
    print("  Actions:")
    print("  [s] Send / Draft    [k] Skip")
    print("  [e] Edit email      [q] Quit")

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
            print("  Invalid choice. Please enter s, k, e, or q.")
