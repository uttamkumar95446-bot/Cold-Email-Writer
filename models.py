"""
Data models for The Closer cold email system.
All data classes with field validation."""
from dataclasses import dataclass, field
from datetime import datetime
import re
@dataclass
class Contact:
    """A single outreach target (job listing or contact)."""
    # Required fields
    recipient_email: str
    company: str
    role: str
    candidate_name: str
    candidate_background: str

    # Optional fields
    recipient_name: str = ""
    job_url: str = ""
    personalization_note: str = ""
    portfolio_url: str = ""
    linkedin_url: str = ""
    resume_link: str = ""

    def __post_init__(self):
        """Validate required fields after initialization."""
        errors = []

        if not self.recipient_email or not self._is_valid_email(self.recipient_email):
            errors.append(f"Invalid or missing recipient_email: {self.recipient_email}")
        if not self.company:
            errors.append("company is required")
        if not self.role:
            errors.append("role is required")
        if not self.candidate_name:
            errors.append("candidate_name is required")
        if not self.candidate_background:
            errors.append("candidate_background is required")

        if errors:
            raise ValueError(f"Contact validation failed: {'; '.join(errors)}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def get_recipient_name_or_fallback(self) -> str:
        """Return recipient_name or infer a fallback from email."""
        if self.recipient_name:
            return self.recipient_name
        # Fallback: extract name from email prefix
        name_part = self.recipient_email.split("@")[0]
        # Convert underscores/dots to spaces and capitalize
        return name_part.replace(".", " ").replace("_", " ").title()


@dataclass
class Email:
    """A generated cold email."""
    subject: str
    body: str
    word_count: int
    contact: Contact  # Reference back to source contact

    def is_valid(self) -> bool:
        """Check if email meets basic quality standards."""
        if not self.subject or not self.body:
            return False
        if self.word_count > 150:
            # Allow override but flag it
            return True  # Just a warning, not a blocker
        return True

    def warnings(self) -> list[str]:
        """Return list of quality warnings."""
        warnings_list = []
        if self.word_count > 150:
            warnings_list.append(f"Word count ({self.word_count}) exceeds 150 limit")
        if len(self.subject) < 5:
            warnings_list.append("Subject line is very short")
        return warnings_list


@dataclass
class SendResult:
    """Result of a send/draft attempt."""
    status: str  # "sent", "drafted", "skipped", "failed"
    error: str = ""
    draft_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LogEntry:
    """Persistent log entry for an email action."""
    timestamp: str
    recipient_email: str
    company: str
    role: str
    subject: str
    status: str  # generated, drafted, sent, skipped, failed
    error_message: str = ""
