"""
Configuration management for The Closer.
Loads and validates environment variables from .env file."""

import argparse
from dataclasses import dataclass
from pathlib import Path
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
        print(f"  [!] .env file not found at {env_file}. Using defaults (DRY_RUN mode).")
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


def parse_cli_args() -> dict:
    """
    Parse command-line arguments.
    Override .env values where provided.

    Returns:
        Dictionary of CLI overrides.
    """
    parser = argparse.ArgumentParser(
        description="The Closer -- Cold Email Writer + Send Bot",
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
        default=None,
        help="Show outreach log and exit",
    )

    args = parser.parse_args()
    return {k: v for k, v in vars(args).items() if v is not None}
