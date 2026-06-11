"""Tests for generator.py"""

import pytest
from models import Contact
from generator import generate_email, count_words, load_template


class TestGenerator:
    @pytest.fixture
    def contact(self):
        return Contact(
            recipient_email="test@example.com",
            recipient_name="Test User",
            company="TestCo",
            role="Engineer",
            candidate_name="Alex",
            candidate_background="Python developer",
            personalization_note="Love your product.",
            portfolio_url="https://github.com/alex",
        )

    def test_generates_email(self, contact):
        email = generate_email(contact)
        assert email.subject
        assert email.body
        assert email.word_count > 0

    def test_subject_contains_company_and_role(self, contact):
        email = generate_email(contact)
        assert "TestCo" in email.subject
        assert "Engineer" in email.subject

    def test_body_contains_personalization(self, contact):
        email = generate_email(contact)
        assert "Love your product." in email.body or "Alex" in email.body

    def test_word_count_limit(self, contact):
        email = generate_email(contact)
        assert email.word_count <= 150, f"Word count: {email.word_count}"

    def test_no_unrendered_variables(self, contact):
        email = generate_email(contact)
        assert "{" not in email.body.replace("{email}", "")

    def test_missing_optional_fields(self):
        minimal = Contact(
            recipient_email="test@example.com",
            company="TestCo",
            role="Engineer",
            candidate_name="Alex",
            candidate_background="Python dev",
        )
        email = generate_email(minimal)
        assert email.subject
        assert email.body

    def test_generate_all(self, contact):
        """Test batch generation."""
        from generator import generate_all
        contacts = [contact]
        emails = generate_all(contacts)
        assert len(emails) == 1
        assert emails[0].subject
        assert emails[0].body
        assert emails[0].word_count > 0

    def test_load_template_fallback(self):
        """Should load inline default when file not found."""
        template = load_template("default")
        assert "Subject:" in template
        assert "{role}" in template
        assert "{company}" in template

    def test_load_template_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            load_template("nonexistent_template")


class TestCountWords:
    def test_simple_text(self):
        assert count_words("Hello world") == 2

    def test_url_excluded(self):
        assert count_words("Check https://example.com") == 1

    def test_multiple_urls_excluded(self):
        assert count_words("See https://a.com and https://b.com") == 2

    def test_empty_string(self):
        assert count_words("") == 0

    def test_newlines_handled(self):
        assert count_words("Hello\nworld\nagain") == 3
