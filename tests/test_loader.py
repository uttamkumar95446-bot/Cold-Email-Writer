"""Tests for loader.py"""

import pytest
import json
import csv
import tempfile
import os
from loader import load_contacts, load_from_json, load_from_csv, get_demo_contacts


class TestDemoContacts:
    def test_returns_5_contacts(self):
        contacts = get_demo_contacts()
        assert len(contacts) == 5

    def test_all_contacts_valid(self):
        contacts = get_demo_contacts()
        for c in contacts:
            assert c.recipient_email
            assert c.company
            assert c.role

    def test_demo_contacts_have_varied_companies(self):
        contacts = get_demo_contacts()
        companies = [c.company for c in contacts]
        assert len(set(companies)) == 5

    def test_demo_contacts_have_varied_roles(self):
        contacts = get_demo_contacts()
        roles = [c.role for c in contacts]
        assert len(set(roles)) == 5

    def test_some_have_linkedin_some_dont(self):
        contacts = get_demo_contacts()
        with_linkedin = sum(1 for c in contacts if c.linkedin_url)
        without_linkedin = sum(1 for c in contacts if not c.linkedin_url)
        assert with_linkedin > 0
        assert without_linkedin > 0


class TestJsonLoader:
    def test_loads_valid_json(self):
        data = [
            {
                "recipient_email": "test@example.com",
                "company": "TestCo",
                "role": "Intern",
                "candidate_name": "Tester",
                "candidate_background": "Python dev",
            }
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name

        try:
            contacts = load_from_json(path)
            assert len(contacts) == 1
            assert contacts[0].company == "TestCo"
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_from_json("nonexistent.json")

    def test_invalid_json_structure(self):
        """Should raise ValueError if JSON is not an array."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"not": "an array"}, f)
            path = f.name

        try:
            with pytest.raises(ValueError):
                load_from_json(path)
        finally:
            os.unlink(path)


class TestLoadContacts:
    def test_no_source_returns_demo(self):
        contacts = load_contacts(None)
        assert len(contacts) == 5


class TestCsvLoader:
    def test_loads_valid_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["recipient_email", "company", "role", "candidate_name", "candidate_background"])
            writer.writerow(["test@example.com", "TestCo", "Intern", "Tester", "Python dev"])
            path = f.name

        try:
            contacts = load_from_csv(path)
            assert len(contacts) == 1
            assert contacts[0].company == "TestCo"
        finally:
            os.unlink(path)

    def test_csv_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_from_csv("nonexistent.csv")
