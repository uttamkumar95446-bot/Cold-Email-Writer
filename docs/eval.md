# Evaluation — The Closer

> **Cold Email Writer + Send Bot** | Phase-by-Phase AI Build Evaluation
> Each phase is evaluated on: functionality, code quality, test coverage, safety, and documentation

---

## How to Use This Document

Each phase below defines:

1. **Evaluation criteria** — What an AI builder must achieve
2. **Pass/fail checklist** — Binary checks for automated verification
3. **Scoring rubric** — 0–10 scale per dimension
4. **Review prompts** — What a code reviewer should inspect

AI builders should run the eval script after completing each phase:

```bash
# After Phase N, run:
python -m eval.phase_N
```

---

## Table of Contents

- [Phase 0: Scaffolding Evaluation](#phase-0-scaffolding-evaluation)
- [Phase 1: Core Data Layer Evaluation](#phase-1-core-data-layer-evaluation)
- [Phase 2: Email Generator Evaluation](#phase-2-email-generator-evaluation)
- [Phase 3: Preview & Confirmation Evaluation](#phase-3-preview--confirmation-evaluation)
- [Phase 4: Logger Evaluation](#phase-4-logger-evaluation)
- [Phase 5: Orchestrator & Dry-Run Evaluation](#phase-5-orchestrator--dry-run-evaluation)
- [Phase 6: SMTP Sender Evaluation](#phase-6-smtp-sender-evaluation)
- [Phase 7: Safety & Polish Evaluation](#phase-7-safety--polish-evaluation)
- [Phase 8: Testing Suite Evaluation](#phase-8-testing-suite-evaluation)
- [Phase 9: Documentation & Demo Evaluation](#phase-9-documentation--demo-evaluation)
- [Phase X: Stretch Goals Evaluation](#phase-x-stretch-goals-evaluation)
- [Appendix: Aggregated Scoring Sheet](#appendix-aggregated-scoring-sheet)

---

## Phase 0: Scaffolding Evaluation

### Pass/Fail Checklist

- [ ] `.env.example` exists with all required variables
- [ ] `.env.example` has `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- [ ] `.env.example` has `SENDER_NAME`, `DRY_RUN`, `DATA_SOURCE`
- [ ] `.gitignore` covers `.env`, `token.json`, `*.log`, `__pycache__/`
- [ ] `requirements.txt` includes `python-dotenv` and `pytest`
- [ ] `pip install -r requirements.txt` succeeds

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Completeness | 40% | Missing 3+ files | All files present, 1-2 minor gaps | All files with thorough comments |
| Correctness | 30% | Typo in env var names | All names correct | No errors, validated |
| Safety | 30% | No `.gitignore` | `.gitignore` present | Covers secrets, logs, OS files |

**Pass threshold**: ≥ 6.0 average

### Review Prompts

```
Are all required env vars from the architecture doc present in .env.example?
Are there any secrets or real credentials in the committed files?
Does .gitignore cover .env, token.json, __pycache__, *.log, and OS files?
```

---

## Phase 1: Core Data Layer Evaluation

### Pass/Fail Checklist

- [ ] `models.py` defines `Contact`, `Email`, `SendResult`, `LogEntry` dataclasses
- [ ] `Contact.__post_init__` validates 5 required fields
- [ ] `Contact.__post_init__` rejects invalid emails
- [ ] `Contact.get_recipient_name_or_fallback()` works with and without `recipient_name`
- [ ] `Email.warnings()` flags word count > 150 and short subjects
- [ ] `config.py` loads `.env` via `python-dotenv`
- [ ] `config.py` defaults to `DRY_RUN=true`
- [ ] `config.py` `validate_config()` catches missing SMTP creds when `dry_run=false`
- [ ] `loader.py` `get_demo_contacts()` returns 5 valid contacts
- [ ] `loader.py` `load_from_json()` parses valid JSON array
- [ ] `loader.py` `load_from_csv()` parses CSV with DictReader
- [ ] `loader.py` `load_contacts(None)` returns demo contacts
- [ ] All 3 files import without errors: `python -c "from models import *; from config import *; from loader import *"`

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Functionality | 40% | >3 checklist items fail | All checklist items pass | All pass + handles edge cases |
| Code Quality | 25% | No docstrings, messy | Clear docstrings, type hints | Comprehensive docs, clean code |
| Error Handling | 20% | Bare excepts | Specific exceptions | Helpful error messages for each case |
| Safety | 15% | No input validation | Basic validation | Full validation + fallbacks |

**Pass threshold**: ≥ 6.5 average

### Review Prompts

```
Does Contact.__post_init__ validate all 5 required fields correctly?
Are error messages clear and actionable for the user?
Does load_from_csv handle BOM characters and whitespace in headers?
Can load_from_json accept a file with extra unknown fields?
```

---

## Phase 2: Email Generator Evaluation

### Pass/Fail Checklist

- [ ] `generate_email(contact)` returns `Email` with non-empty subject and body
- [ ] Subject line contains company name and role title
- [ ] Body contains 6-part anatomy: subject, hook, intro, value, ask, sign-off
- [ ] `word_count` ≤ 150 for all demo contacts
- [ ] Missing optional fields (portfolio_url, personalization_note) don't cause errors
- [ ] Template renders with no unsubstituted `{...}` placeholders
- [ ] `load_template("nonexistent")` raises `FileNotFoundError`
- [ ] `render_template` handles shared-prefix variables correctly (sorted by length)

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Output Quality | 35% | Missing anatomy parts | All 6 parts present | Natural, varied, effective |
| Robustness | 30% | Crashes on missing fields | Handles missing fields | Handles edge cases gracefully |
| Template System | 20% | No fallback template | Inline fallback works | File + inline + custom templates |
| Word Limit | 15% | No enforcement | Warns on exceed | Enforces + auto-trims |

**Pass threshold**: ≥ 6.5 average

### Review Prompts

```
Does every generated email follow the 6-part cold email anatomy?
What happens when all optional fields are missing — does it still produce a reasonable email?
Are there any {variables} left unrendered in the output?
Does render_template sort keys by length to avoid prefix collision issues?
```

---

## Phase 3: Preview & Confirmation Evaluation

### Pass/Fail Checklist

- [ ] `preview_email()` displays To, Company, Role, Subject, Body, Word Count
- [ ] Word count shown with `/150` limit indicator
- [ ] Warnings (word count > 150, short subject) are displayed
- [ ] `s` or `send` returns "send"
- [ ] `k` or `skip` returns "skip"
- [ ] `q` or `quit` returns "quit"
- [ ] Invalid input shows error and re-prompts (infinite loop protection: max 5 attempts)
- [ ] `Ctrl+C` is caught gracefully (doesn't trigger traceback)

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| UX | 40% | Hard to read preview | Clear, formatted preview | Beautiful terminal display |
| Interaction | 35% | Single option only | Send/skip/quit | Send/skip/edit/quit + safety |
| Robustness | 25% | Crashes on Ctrl+C | Handles invalid input | Handles Ctrl+C, EOFError, all inputs |

**Pass threshold**: ≥ 6.0 average

### Review Prompts

```
Does the preview clearly separate the email metadata from the body?
What happens if the user presses Ctrl+C during confirmation?
Are there too many prompts for a batch of 5 contacts? (shouldn't be tedious)
```

---

## Phase 4: Logger Evaluation

### Pass/Fail Checklist

- [ ] `log_result()` creates `outreach_log.csv` if it doesn't exist
- [ ] `log_result()` appends a new row with all 7 columns
- [ ] CSV file has header row: `timestamp,recipient_email,company,role,subject,status,error_message`
- [ ] No duplicate header when logging multiple times
- [ ] `read_log()` returns list of dicts from existing CSV
- [ ] `get_log_summary()` returns correct counts per status
- [ ] `show_proof()` prints formatted log table

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Correctness | 40% | Missing columns | All columns written | Correct headers, no duplication |
| Format | 25% | Unparseable CSV | Valid CSV | RFC 4180 compliant CSV |
| Readability | 20% | No summary function | Raw entries only | Summary stats + pretty-print |
| Safety | 15% | No file-exists check | Checks file exists | Atomic writes, lock-safe |

**Pass threshold**: ≥ 6.0 average

### Review Prompts

```
Does the CSV get a header row only once (file creation)?
What happens if outreach_log.csv is read-only?
Does get_log_summary correctly count all status types?
```

---

## Phase 5: Orchestrator & Dry-Run Evaluation

### Pass/Fail Checklist

- [ ] `python main.py` runs end-to-end without errors
- [ ] Processes all 5 demo contacts through generate → preview
- [ ] User actions work: `s` (proceed), `k` (skip), `q` (quit mid-pipeline)
- [ ] `outreach_log.csv` created with entries for each contact
- [ ] Final summary shows accurate counts
- [ ] `python main.py --log` shows log without running pipeline
- [ ] `python main.py --send` shows "LIVE SEND" mode in banner
- [ ] `python main.py --file nonexistent.json` shows clear error and exits
- [ ] `--dry-run` overrides `.env` value
- [ ] `--file` overrides `DATA_SOURCE` env var

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Pipeline Integrity | 35% | Crashes mid-pipeline | Full pipeline runs | Graceful error handling per contact |
| CLI UX | 30% | Confusing output | Clear terminal output | Beautiful banner + progress + summary |
| Config | 20% | CLI args ignored | Basic args work | All args + env var overrides |
| Error Handling | 15% | Unhandled exceptions | Basic error handling | Granular error per phase |

**Pass threshold**: ≥ 6.5 average

### Review Prompts

```
Does the pipeline continue to the next contact after an error in one?
Is the terminal output organized and easy to follow?
Do CLI args properly override .env values?
```

---

## Phase 6: SMTP Sender Evaluation

### Pass/Fail Checklist

- [ ] `DryRunSender` logs intent without connecting to SMTP
- [ ] `SmtpSender` builds proper MIME message with From, To, Subject
- [ ] `SmtpSender` uses STARTTLS for encryption
- [ ] `SmtpSender` handles `SMTPAuthenticationError` gracefully
- [ ] `SmtpSender` handles `SMTPException` (general) gracefully
- [ ] `SmtpSender` handles connection timeout gracefully
- [ ] `get_sender()` returns `DryRunSender` when `dry_run=True`
- [ ] `get_sender()` returns `SmtpSender` when `dry_run=False, send_method="smtp"`
- [ ] `send_email()` is a clean public API function

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Functionality | 35% | Doesn't send | Sends successfully | Sends + drafts + dry-run |
| Error Handling | 30% | Unhandled SMTP errors | Auth + timeout handled | All 5+ error types handled |
| Architecture | 20% | Monolithic | Strategy pattern | Clean strategy + factory |
| Security | 15% | Plaintext credentials | Uses .env | STARTTLS + .env + clear logging |

**Pass threshold**: ≥ 6.5 average

### Review Prompts

```
Does SmtpSender properly log the connection steps for debugging?
Are SMTP credentials never logged or printed in plain text?
Does the strategy pattern make it easy to add GmailApiSender later?
```

---

## Phase 7: Safety & Polish Evaluation

### Pass/Fail Checklist

- [ ] Opt-out list is respected: opted-out recipients are silently skipped
- [ ] `opt_out.txt` is created on first opt-out addition
- [ ] `add_opt_out()` prevents duplicate entries
- [ ] Email editing lets user change subject and body
- [ ] Word count is recalculated after editing
- [ ] `is_opted_out()` is case-insensitive
- [ ] Safety confirmation appears when `dry_run=false`
- [ ] User can abort send during safety confirmation (type anything but "yes")

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Safety | 40% | No opt-out or confirm | Opt-out + confirm | Full guardrails per spec |
| Edit UX | 30% | No editing | Can edit subject | Full subject + body editing |
| Robustness | 30% | Case-sensitive opt-out | Case-insensitive | Case-insensitive + comments |

**Pass threshold**: ≥ 7.0 (safety-critical phase)

### Review Prompts

```
Does the safety confirmation actually prevent accidental sends?
Are there any paths where an email could be sent without human review?
Can the user edit both subject and body during preview?
```

---

## Phase 8: Testing Suite Evaluation

### Pass/Fail Checklist

- [ ] `tests/test_models.py` — Contact validation, Email warnings, edge cases
- [ ] `tests/test_config.py` — Config validation with temp env isolation
- [ ] `tests/test_loader.py` — JSON, CSV, demo contacts, file-not-found
- [ ] `tests/test_generator.py` — Template rendering, word count, edge cases
- [ ] `tests/test_logger.py` — CSV append, read, summary, cleanup
- [ ] `tests/test_sender.py` — DryRunSender, get_sender factory, NotImplementedError
- [ ] `tests/test_integration.py` — Full dry-run pipeline, word count, uniqueness
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Tests do not depend on real `.env` file
- [ ] Tests clean up temp files after run (no leftover `outreach_log.csv`)

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Coverage | 35% | < 3 files tested | 5+ files tested | All 7 test files present |
| Pass Rate | 35% | < 50% pass | 100% pass | All pass + no warnings |
| Isolation | 20% | Tests depend on .env | Temp file isolation | Full isolation + parallel-safe |
| Edge Cases | 10% | Only happy path | Some edge cases | Comprehensive edge cases |

**Pass threshold**: ≥ 7.0 average

### Review Prompts

```
Do the generator tests verify the 150-word limit?
Do tests clean up after themselves (no leftover CSV files)?
Are network-dependent tests properly mocked?
```

---

## Phase 9: Documentation & Demo Evaluation

### Pass/Fail Checklist

- [ ] `README.md` has Quick Start section with exact commands
- [ ] `README.md` has Setup section with App Password instructions
- [ ] `README.md` has Usage section with all CLI flags
- [ ] `README.md` has Features list
- [ ] `contacts.json` has 5 valid sample contacts
- [ ] `python main.py --file contacts.json` works end-to-end
- [ ] `docs/problemStatement.md`, `docs/architecture.md`, `docs/implementation-plan.md` are consistent
- [ ] `docs/edge-case.md` covers all phases
- [ ] `docs/eval.md` covers all phases with scoring rubrics

### Scoring Rubric

| Dimension | Weight | 0–3 (Fail) | 4–6 (Pass) | 7–10 (Excellent) |
|-----------|--------|------------|------------|-------------------|
| Completeness | 35% | Missing major sections | All sections present | Comprehensive with examples |
| Accuracy | 30% | Outdated commands | All commands work | Validated end-to-end |
| Clarity | 20% | Hard to follow | Clear instructions | New-user-friendly |
| Consistency | 15% | Docs contradict each other | No contradictions | Cross-referenced, aligned |

**Pass threshold**: ≥ 6.5 average

### Review Prompts

```
Can a new user go from zero to running the app using only README.md?
Are the setup instructions specific to Gmail App Passwords?
Do all documentation files agree on folder structure and env vars?
```

---

## Phase X: Stretch Goals Evaluation

### Groq LLM Enhancement Evaluation

**Pass/Fail Checklist:**

- [ ] `GROQ_API_KEY` env var is loaded from `.env`
- [ ] `groq` package is in requirements.txt (commented by default)
- [ ] `enhance_with_llm()` calls Groq API with `llama-3.3-70b-versatile`
- [ ] Fact preservation: names, URLs, and company names unchanged
- [ ] Word count enforced to ≤ 150 after rewrite
- [ ] API errors handled gracefully (falls back to template email)
- [ ] Hallucination check rejects fabricated claims

**Scoring (0–10):**

| Criteria | Points |
|----------|--------|
| Basic integration (API call works) | 3 |
| Fact preservation | 3 |
| Error handling + fallback | 2 |
| Hallucination detection | 2 |

### Gmail API Drafting Evaluation

**Pass/Fail Checklist:**

- [ ] OAuth flow creates `token.json`
- [ ] Draft appears in Gmail Drafts folder
- [ ] Draft has correct To, Subject, and body
- [ ] Token refresh works

### Streamlit UI Evaluation

**Pass/Fail Checklist:**

- [ ] File upload for JSON/CSV works
- [ ] Email preview panel shows formatted email
- [ ] Send/Draft/Skip buttons work

---

## Appendix: Aggregated Scoring Sheet

Use this table to track overall project quality.

| Phase | Functionality (0–10) | Code Quality (0–10) | Safety (0–10) | Tests (0–10) | Docs (0–10) | **Average** |
|-------|---------------------|--------------------|--------------|-------------|-------------|-------------|
| 0: Scaffolding | | | | N/A | | |
| 1: Data Layer | | | | | | |
| 2: Generator | | | | | | |
| 3: Preview | | | | | | |
| 4: Logger | | | | | | |
| 5: Orchestrator | | | | | | |
| 6: SMTP Sender | | | | | | |
| 7: Safety | | | | | | |
| 8: Testing | | | N/A | | | |
| 9: Docs | | | N/A | N/A | | |
| **Average** | | | | | | |

### Scoring Guide

| Score | Meaning |
|-------|---------|
| 9–10 | Production-ready, no issues found |
| 7–8 | Solid, minor improvements possible |
| 6 | Pass threshold — acceptable for MVP |
| 4–5 | Needs significant improvement |
| 0–3 | Requires rewrite |

---

## Automated Eval Script Skeleton

```python
# Place in: eval/__init__.py
# Run: python -m eval.phase_N

import sys
import importlib.util

def run_checks(phase_name: str, checks: list[tuple[str, callable]]):
    """Run a list of (description, callable) checks."""
    passed = 0
    failed = 0

    print(f"\n{'='*50}")
    print(f"  Evaluating: {phase_name}")
    print(f"{'='*50}\n")

    for desc, check_fn in checks:
        try:
            result = check_fn()
            if result:
                print(f"  ✅ {desc}")
                passed += 1
            else:
                print(f"  ❌ {desc}")
                failed += 1
        except Exception as e:
            print(f"  ❌ {desc} (ERROR: {e})")
            failed += 1

    print(f"\n  Results: {passed}/{passed + failed} passed")
    return passed, failed

# Phase 0 example:
# checks = [
#     (" .env.example exists", lambda: Path(".env.example").exists()),
#     (" .gitignore exists", lambda: Path(".gitignore").exists()),
#     ...
# ]
# run_checks("Phase 0: Scaffolding", checks)
```
