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


def cleanup():
    if os.path.exists("outreach_log.csv"):
        os.remove("outreach_log.csv")


class TestLogger:
    def test_creates_csv_on_first_log(self, contact, email):
        cleanup()
        log_result(contact, email, "sent")
        assert os.path.exists("outreach_log.csv")
        cleanup()

    def test_reads_back_entries(self, contact, email):
        cleanup()
        log_result(contact, email, "sent")
        entries = read_log()
        assert len(entries) == 1
        assert entries[0]["status"] == "sent"
        assert entries[0]["company"] == "TestCo"
        cleanup()

    def test_summary_counts(self, contact, email):
        cleanup()
        log_result(contact, email, "sent")
        log_result(contact, email, "skipped")
        log_result(contact, email, "failed", "Connection error")
        summary = get_log_summary()
        assert summary["sent"] == 1
        assert summary["skipped"] == 1
        assert summary["failed"] == 1
        assert summary["total"] == 3
        cleanup()

    def test_no_header_duplication(self, contact, email):
        cleanup()
        log_result(contact, email, "sent")
        log_result(contact, email, "skipped")
        with open("outreach_log.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
        header_count = sum(1 for l in lines if l.startswith("timestamp"))
        assert header_count == 1
        cleanup()

    def test_empty_log_summary(self):
        cleanup()
        summary = get_log_summary()
        assert summary["total"] == 0
        assert summary["sent"] == 0
        assert summary["skipped"] == 0
        assert summary["failed"] == 0
        cleanup()

    def test_error_message_logged(self, contact, email):
        cleanup()
        log_result(contact, email, "failed", "SMTP connection refused")
        entries = read_log()
        assert entries[0]["error_message"] == "SMTP connection refused"
        cleanup()
