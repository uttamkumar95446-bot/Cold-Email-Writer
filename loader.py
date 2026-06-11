"""
Data loader for The Closer.
Loads outreach targets from JSON, CSV, or hardcoded demo contacts."""

import csv
import json
from pathlib import Path
from typing import List, Optional

from models import Contact


# ─── Demo Contacts ────────────────────────────────────

def get_demo_contacts() -> List[Contact]:
    """
    Return 5 hardcoded demo contacts for live demo / testing.
    These showcase different personalization scenarios."""
    return [
        Contact(
            recipient_email="priya@example.com",
            recipient_name="Priya Sharma",
            company="Acme AI",
            role="Backend Engineering Intern",
            job_url="https://example.com/jobs/acme-backend",
            personalization_note="I was excited to see Acme AI's recent launch of their workflow automation platform — it's impressive.",
            candidate_name="Alex Chen",
            candidate_background="Python developer with experience building automation tools and AI agents",
            portfolio_url="https://github.com/alexchen",
        ),
        Contact(
            recipient_email="james@startup.co",
            recipient_name="James Wilson",
            company="NeuralPath",
            role="ML Engineering Intern",
            job_url="https://example.com/jobs/neuralpath-ml",
            personalization_note="I read about NeuralPath's work on efficient transformers — that's exactly the kind of work I want to contribute to.",
            candidate_name="Alex Chen",
            candidate_background="Machine learning student with projects in NLP and model optimization",
            portfolio_url="https://github.com/alexchen",
            linkedin_url="https://linkedin.com/in/alexchen",
        ),
        Contact(
            recipient_email="sarah@greenenergy.io",
            recipient_name="Sarah Kim",
            company="GreenGrid",
            role="Software Engineering Intern",
            job_url="https://example.com/jobs/greengrid-swe",
            personalization_note="GreenGrid's mission to make renewable energy accessible through smart grids really resonates with me.",
            candidate_name="Alex Chen",
            candidate_background="Full-stack developer with experience in React, Python, and building data pipelines",
            portfolio_url="https://github.com/alexchen",
            resume_link="https://alexchen.dev/resume.pdf",
        ),
        Contact(
            recipient_email="marcus@fintech.com",
            recipient_name="Marcus Johnson",
            company="QuickLedger",
            role="Product Management Intern",
            personalization_note="I've been following QuickLedger's growth in the SMB accounting space — your API-first approach stands out.",
            candidate_name="Alex Chen",
            candidate_background="Computer science student with product sense and experience building user-facing features",
            portfolio_url="https://github.com/alexchen",
        ),
        Contact(
            recipient_email="hello@datavista.io",
            company="DataVista",
            role="Data Engineering Intern",
            personalization_note="DataVista's recent blog post about real-time data pipelines at scale was incredibly insightful.",
            candidate_name="Alex Chen",
            candidate_background="Data engineer with experience in ETL pipelines, SQL, and Python data processing",
            portfolio_url="https://github.com/alexchen",
            linkedin_url="https://linkedin.com/in/alexchen",
        ),
    ]


# ─── File Loaders ─────────────────────────────────────

def load_from_json(path: str) -> List[Contact]:
    """
    Load contacts from a JSON file.
    
    Expected format: array of objects with Contact fields.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of contact objects")

    contacts = []
    errors = []
    for i, item in enumerate(data):
        try:
            contact = Contact(**item)
            contacts.append(contact)
        except (ValueError, TypeError) as e:
            errors.append(f"  Row {i}: {e}")

    if errors:
        print(f"  [!] {len(errors)} contact(s) had validation errors:")
        for err in errors:
            print(f"     {err}")

    return contacts


def load_from_csv(path: str) -> List[Contact]:
    """
    Load contacts from a CSV file.
    
    Expected columns: recipient_email, company, role, candidate_name, 
                      candidate_background, and optional fields.
    """
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    contacts = []
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                # Strip whitespace from keys and values
                cleaned = {k.strip(): v.strip() for k, v in row.items() if k}
                contact = Contact(**cleaned)
                contacts.append(contact)
            except (ValueError, TypeError) as e:
                errors.append(f"  Row {i + 1}: {e}")

    if errors:
        print(f"  [!] {len(errors)} contact(s) had validation errors:")
        for err in errors:
            print(f"     {err}")

    return contacts


def load_contacts(source: Optional[str] = None) -> List[Contact]:
    """
    Main entry point: load contacts from file or return demo contacts.
    
    Args:
        source: Path to JSON or CSV file, or None for demo contacts.
    
    Returns:
        List of validated Contact objects.
    """
    if not source:
        print("  [~] No data source specified. Using demo contacts.")
        return get_demo_contacts()

    path_str = str(source)

    if path_str.endswith(".json"):
        print(f"  [~] Loading contacts from JSON: {path_str}")
        return load_from_json(path_str)
    elif path_str.endswith(".csv"):
        print(f"  [~] Loading contacts from CSV: {path_str}")
        return load_from_csv(path_str)
    else:
        raise ValueError(f"Unsupported file format: {path_str}. Use .json or .csv")
