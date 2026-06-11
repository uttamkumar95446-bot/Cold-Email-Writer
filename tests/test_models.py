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

    def test_partial_optional_fields(self):
        """Should succeed with some optional fields missing."""
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Engineer",
            candidate_name="Alex",
            candidate_background="Developer",
            portfolio_url="https://github.com/alex",
        )
        assert c.portfolio_url == "https://github.com/alex"
        assert c.linkedin_url == ""
        assert c.job_url == ""


class TestEmail:
    def test_valid_email(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        e = Email(subject="Test Subject", body="Hello world", word_count=2, contact=c)
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

    def test_short_subject_warning(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        e = Email(subject="Hi", body="Hello world", word_count=2, contact=c)
        warnings = e.warnings()
        assert any("short" in w.lower() for w in warnings)

    def test_empty_subject_invalid(self):
        c = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Intern",
            candidate_name="Tester",
            candidate_background="Python dev",
        )
        e = Email(subject="", body="Hello world", word_count=2, contact=c)
        assert not e.is_valid()
