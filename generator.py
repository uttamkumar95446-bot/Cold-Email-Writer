"""
Email generation engine for The Closer.
Generates personalized cold emails from contact records using templates."""

from pathlib import Path
from models import Contact, Email


# ─── Default Template (inline fallback) ──────────────

DEFAULT_TEMPLATE = """\
Subject: Quick note on the {role} role at {company}

Hi {recipient_name_or_fallback},

{personalization_note}

I'm {candidate_name}, and I've been building projects around {candidate_background}. The {role} role at {company} stood out because it connects closely with my background and interests.

Would you be open to a quick chat about how my experience could contribute to your team?

Best,
{candidate_name}
{portfolio_or_linkedin}"""


# ─── Template Loading ─────────────────────────────────

def load_template(template_name: str = "default") -> str:
    """
    Load a template file from the templates/ directory.
    
    Args:
        template_name: Name without extension (e.g., "default")
    
    Returns:
        Template string with {placeholders}.
    """
    template_path = Path(__file__).parent / "templates" / f"{template_name}.txt"

    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fall back to inline default
    if template_name == "default":
        return DEFAULT_TEMPLATE

    raise FileNotFoundError(f"Template not found: {template_name}")


# ─── Variable Preparation ─────────────────────────────

def prepare_variables(contact: Contact) -> dict:
    """
    Prepare template variables from contact record.
    Computes derived fields (e.g., portfolio_or_linkedin, recipient_name_or_fallback)."""
    return {
        "recipient_name": contact.recipient_name,
        "recipient_name_or_fallback": contact.get_recipient_name_or_fallback(),
        "company": contact.company,
        "role": contact.role,
        "candidate_name": contact.candidate_name,
        "candidate_background": contact.candidate_background,
        "personalization_note": contact.personalization_note or (
            f"I noticed {contact.company} is hiring for a {contact.role} role "
            f"and wanted to reach out."
        ),
        "portfolio_url": contact.portfolio_url or "",
        "linkedin_url": contact.linkedin_url or "",
        "portfolio_or_linkedin": contact.portfolio_url or contact.linkedin_url or "",
        "job_url": contact.job_url or "",
        "resume_link": contact.resume_link or "",
    }


# ─── Rendering ────────────────────────────────────────

def render_template(template: str, variables: dict) -> tuple[str, str]:
    """
    Render template with variables.
    
    Returns:
        Tuple of (subject_line, email_body)
    """
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))

    # Split subject from body
    lines = rendered.strip().split("\n", 1)
    subject_line = lines[0].replace("Subject: ", "").strip()
    body = lines[1].strip() if len(lines) > 1 else ""

    return subject_line, body


# ─── Word Counting ────────────────────────────────────

def count_words(text: str) -> int:
    """Count words in text, excluding URLs."""
    # Split on whitespace, exclude URLs from count
    words = [w for w in text.split() if not w.startswith("http")]
    return len(words)


# ─── Main Generation Function ─────────────────────────

def generate_email(
    contact: Contact,
    template_name: str = "default",
) -> Email:
    """
    Generate a personalized cold email from a contact record.
    
    Args:
        contact: Outreach target with personalization fields
        template_name: Name of template to use
    
    Returns:
        Email object with subject, body, and word count
    """
    template = load_template(template_name)
    variables = prepare_variables(contact)
    subject, body = render_template(template, variables)
    word_count = count_words(body)

    return Email(
        subject=subject,
        body=body,
        word_count=word_count,
        contact=contact,
    )


def generate_all(
    contacts: list[Contact],
    template_name: str = "default",
) -> list[Email]:
    """Generate emails for all contacts."""
    return [generate_email(c, template_name) for c in contacts]
