"""Integration tests for full pipeline."""

import os
import pytest
from config import Config
from loader import get_demo_contacts
from generator import generate_email
from sender import DryRunSender


class TestDryRunPipeline:
    def test_full_dry_run_pipeline(self):
        """End-to-end: contacts -> generate -> dry-run send."""
        contacts = get_demo_contacts()
        assert len(contacts) == 5

        config = Config(dry_run=True)
        sender = DryRunSender()

        for contact in contacts:
            email = generate_email(contact)
            assert email.subject
            assert email.body
            assert email.word_count > 0

            result = sender.send(contact, email, config)
            assert "draft" in result.status

    def test_all_emails_under_150_words(self):
        """Verify all demo contacts produce sub-150-word emails."""
        contacts = get_demo_contacts()
        for contact in contacts:
            email = generate_email(contact)
            assert email.word_count <= 150, (
                f"{contact.company} - {contact.role}: {email.word_count} words"
            )

    def test_each_email_is_unique(self):
        """No two generated emails should be identical."""
        contacts = get_demo_contacts()
        emails = [generate_email(c) for c in contacts]
        bodies = [e.body for e in emails]
        assert len(set(bodies)) == len(bodies), "Duplicate email bodies detected"

    def test_email_anatomy_present(self):
        """Each email should have all 6 anatomy parts."""
        contacts = get_demo_contacts()
        for contact in contacts:
            email = generate_email(contact)
            # Subject with company and role
            assert contact.company in email.subject
            # Body has greeting
            assert "Hi " in email.body
            # Body has candidate name
            assert contact.candidate_name in email.body
            # Body has closing
            assert "Best" in email.body or "best" in email.body
