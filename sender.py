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
        print(f"  [DRY RUN] Would send to {contact.recipient_email}")
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
            print(f"  Connecting to {config.smtp_host}:{config.smtp_port}...")
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                server.starttls()
                print(f"  Authenticating as {config.smtp_user}...")
                server.login(config.smtp_user, config.smtp_password)
                server.send_message(msg)

            print(f"  [+] Email sent to {contact.recipient_email}")
            return SendResult(status="sent")

        except smtplib.SMTPAuthenticationError:
            error_msg = "Authentication failed. Check your SMTP username and app password."
            print(f"  [!] {error_msg}")
            return SendResult(status="failed", error=error_msg)

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            print(f"  [!] {error_msg}")
            return SendResult(status="failed", error=error_msg)

        except Exception as e:
            error_msg = f"Connection failed: {e}"
            print(f"  [!] {error_msg}")
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
