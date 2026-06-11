"""Tests for sender.py"""

import pytest
from models import Contact, Email
from config import Config
from sender import DryRunSender, SmtpSender, get_sender


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


class TestSmtpSender:
    def test_graceful_connection_failure(self, contact, email):
        """SmtpSender should fail gracefully when no SMTP server available."""
        config = Config(
            dry_run=False,
            send_method="smtp",
            smtp_host="localhost",
            smtp_port=1,
            smtp_user="x",
            smtp_password="y",
            sender_name="Tester",
        )
        sender = SmtpSender()
        result = sender.send(contact, email, config)
        assert result.status == "failed"
        assert result.error


class TestGetSender:
    def test_dry_run_returns_dry_run_sender(self):
        config = Config(dry_run=True)
        sender = get_sender(config)
        assert isinstance(sender, DryRunSender)

    def test_smtp_returns_smtp_sender(self):
        config = Config(dry_run=False, send_method="smtp")
        sender = get_sender(config)
        assert isinstance(sender, SmtpSender)

    def test_gmail_not_implemented(self):
        config = Config(dry_run=False, send_method="gmail")
        with pytest.raises(NotImplementedError):
            get_sender(config)

    def test_unknown_method_raises_value_error(self):
        config = Config(dry_run=False, send_method="fax")
        with pytest.raises(ValueError):
            get_sender(config)
