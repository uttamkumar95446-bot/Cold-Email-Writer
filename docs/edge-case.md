# Edge Cases — The Closer

> **Cold Email Writer + Send Bot** | Comprehensive Edge Case Catalog
> Covers all modules across Phases 0–9 and stretch goals

---

## Table of Contents

1. [Phase 0: Scaffolding Edge Cases](#phase-0-scaffolding-edge-cases)
2. [Phase 1: Data Layer Edge Cases](#phase-1-data-layer-edge-cases)
3. [Phase 2: Email Generator Edge Cases](#phase-2-email-generator-edge-cases)
4. [Phase 3: Preview & Confirm Edge Cases](#phase-3-preview--confirm-edge-cases)
5. [Phase 4: Logger Edge Cases](#phase-4-logger-edge-cases)
6. [Phase 5: Orchestrator Edge Cases](#phase-5-orchestrator-edge-cases)
7. [Phase 6: SMTP Sender Edge Cases](#phase-6-smtp-sender-edge-cases)
8. [Phase 7: Safety & Opt-Out Edge Cases](#phase-7-safety--opt-out-edge-cases)
9. [Phase 8: Testing Edge Cases](#phase-8-testing-edge-cases)
10. [Phase 9: Demo & Documentation Edge Cases](#phase-9-demo--documentation-edge-cases)
11. [Phase X: Stretch Goal Edge Cases](#phase-x-stretch-goal-edge-cases)

---

## Phase 0: Scaffolding Edge Cases

### .env.example

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 0.1 | `.env.example` is missing a required variable | User gets clear error at startup listing missing vars | High |
| 0.2 | `.env.example` has typos in variable names | Config loader silently uses defaults; no obvious email send | Medium |
| 0.3 | User copies `.env.example` to `.env` without editing | App defaults to DRY_RUN=true; no accidental sends | Low (safe) |
| 0.4 | `.env` file has trailing spaces in values | Loader should `.strip()` all values | Medium |
| 0.5 | `.env` file has quoted values (e.g., `SMTP_PASSWORD="pass"`) | Quotes should be stripped, not included in value | Medium |

### requirements.txt

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 0.6 | `pip install` fails due to dependency conflict | Clear error message with resolution steps | High |
| 0.7 | Python version < 3.9 (f-strings with `str | float` syntax) | Install error or syntax error at runtime | High |
| 0.8 | User runs with `pip install` but misses `python-dotenv` | Imports fail with ModuleNotFoundError | High |

### .gitignore

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 0.9 | `.env` not in `.gitignore` | Secrets could be committed accidentally | Critical |
| 0.10 | `outreach_log.csv` committed to git | Personal outreach data leaked | Critical |

---

## Phase 1: Data Layer Edge Cases

### models.py — Contact

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 1.1 | `recipient_email` is empty string | `ValueError` with clear message | High |
| 1.2 | `recipient_email` has no `@` symbol | `ValueError` — "Invalid or missing recipient_email" | High |
| 1.3 | `recipient_email` has multiple `@` symbols | `ValueError` — invalid format | Medium |
| 1.4 | `recipient_email` is valid but domain has no TLD (e.g., `user@localhost`) | `ValueError` — regex requires TLD | Medium |
| 1.5 | `company` name with special characters (`Acme & Sons, Ltd.`) | Accepted as valid string | Low |
| 1.6 | `company` name with only whitespace | `ValueError` — "company is required" | High |
| 1.7 | `recipient_name` is empty | Falls back to email prefix via `get_recipient_name_or_fallback()` | Medium |
| 1.8 | Email prefix has dots + underscores (`john.doe_smith@...`) | `title()` produces "John.doe_smith" (dot preserved) | Low |
| 1.9 | All optional fields are empty | Email generated with fallback values; no crash | Low |
| 1.10 | `personalization_note` contains single quotes | String handled correctly; no syntax error | Low |
| 1.11 | `candidate_background` is extremely long (500+ chars) | Must still enforce 150-word limit in generator | Medium |
| 1.12 | `portfolio_url` is not a valid URL (e.g., `not-a-url`) | Accepted as string; only used in template | Low |

### config.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 1.13 | `.env` file doesn't exist | Warning printed; default config used; DRY_RUN=true | Medium |
| 1.14 | `SMTP_PORT` is non-numeric string (e.g., `abc`) | `int()` conversion raises `ValueError` | High |
| 1.15 | `DRY_RUN` is not `true` or `false` (e.g., `DRY_RUN=yes`) | `"yes".lower() == "true"` evaluates to False → sends real emails | Critical |
| 1.16 | `DRY_RUN` is uppercase `TRUE` | `.lower() == "true"` works correctly | Low |
| 1.17 | `MAX_EMAILS_PER_RUN` is 0 or negative | Slicing `contacts[:0]` yields empty list; no contacts processed | Medium |
| 1.18 | `MAX_EMAILS_PER_RUN` is missing entirely | Defaults to 10 | Low |
| 1.19 | `SEND_METHOD` is empty string | Falls through to default "smtp" | Low |
| 1.20 | `dry_run=false` but `SMTP_USER` is empty | `validate_config()` returns error; app exits | High |
| 1.21 | `dry_run=false` but `SMTP_PASSWORD` is empty | `validate_config()` returns error; app exits | High |
| 1.22 | `dry_run=false` but `SENDER_NAME` is empty | `validate_config()` returns error; app exits | Medium |

### loader.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 1.23 | JSON file is empty array `[]` | Returns empty list; summary shows 0 contacts | Medium |
| 1.24 | JSON file is empty (0 bytes) | `json.load()` raises `json.JSONDecodeError` | High |
| 1.25 | JSON file contains a single object instead of array | `isinstance(data, list)` check fails → `ValueError` | High |
| 1.26 | JSON file has extra unknown fields | `Contact(**item)` ignores extras via `__post_init__` validation | Low |
| 1.27 | CSV file has BOM (Byte Order Mark) | `csv.DictReader` handles it; first column name may have `\ufeff` prefix | Medium |
| 1.28 | CSV file has mismatched column count in a row | `csv.reader` yields varying-length rows; `Contact(**cleaned)` may fail | High |
| 1.29 | CSV file is empty (header only, no data rows) | Returns empty list | Medium |
| 1.30 | CSV file path has unicode characters (e.g., `contatos.json`) | `Path()` handles unicode on modern Python | Low |
| 1.31 | File path uses Windows backslashes vs Unix forward slashes | `Path()` normalizes; fine on both OS | Low |
| 1.32 | `load_contacts()` called with unsupported extension (e.g., `.xlsx`) | `ValueError` — "Unsupported file format" | High |
| 1.33 | File is locked by another process | `PermissionError` — caught by caller or crashes | Medium |
| 1.34 | Demo contacts exceed 150 words when generated | Must verify in test; generator should stay under limit | Medium |

---

## Phase 2: Email Generator Edge Cases

### generator.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 2.1 | `personalization_note` is empty | Auto-generated: "I noticed {company} is hiring for {role} and wanted to reach out." | Medium |
| 2.2 | `portfolio_url` and `linkedin_url` are both empty | `portfolio_or_linkedin` variable is empty string; blank line in template | Low |
| 2.3 | Template file not found at `templates/default.txt` | Falls back to inline `DEFAULT_TEMPLATE` constant | Medium |
| 2.4 | Template file has Windows line endings (`\r\n`) | `split("\n")` leaves trailing `\r` in body lines | Medium |
| 2.5 | Template contains a `{variable}` that doesn't exist in `prepare_variables()` dict | `str.replace()` leaves `{variable}` unrendered in output | High |
| 2.6 | Generated email body is empty (template issue) | `Email` still created; `is_valid()` returns False | Medium |
| 2.7 | Word count exceeds 150 words | `warnings()` returns warning; preview shows it; not blocked | Medium |
| 2.8 | Body contains only URLs (all words excluded from count) | `word_count = 0`; email is empty text | High |
| 2.9 | Template has mismatched curly braces (e.g., `{name}}`) | Variable name doesn't match; left as-is in output | Medium |
| 2.10 | Subject line contains URL that gets counted in word count | No — `count_words` specifically excludes URLs | Low |
| 2.11 | `render_template` has keys with shared prefixes (e.g., `recipient_name` vs `recipient_name_or_fallback`) | Use sorted keys by length (descending) to avoid partial replacement | Medium |

---

## Phase 3: Preview & Confirm Edge Cases

### preview.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 3.1 | User types empty string at prompt | Re-prompts with error message "Invalid choice" | Low |
| 3.2 | User types uppercase `S` | `.lower()` normalizes to "s" → works | Low |
| 3.3 | User types spaces before input (e.g., `  s`) | `.strip()` removes whitespace → works | Low |
| 3.4 | User types `Ctrl+C` (KeyboardInterrupt) at prompt | Unhandled: will raise KeyboardInterrupt and crash | Medium |
| 3.5 | User types `Ctrl+D` (EOFError) at prompt | Unhandled: will raise EOFError and crash | Medium |
| 3.6 | Email body contains ANSI escape sequences or terminal-breaking chars | Printed raw; may look odd but not crash | Low |
| 3.7 | Total emails is 0 (empty contact list) | Never reaches preview; handled in orchestrator | Low |
| 3.8 | Email body is extremely long (1000+ chars) | Terminal wraps naturally; may be hard to read | Low |
| 3.9 | User enters `e` for edit but edit_email function not imported | `NameError` at runtime | Critical |

---

## Phase 4: Logger Edge Cases

### logger.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 4.1 | `outreach_log.csv` is locked by another process | `PermissionError` when opening for append | Medium |
| 4.2 | `outreach_log.csv` already exists from a previous run | Appends correctly; no header duplication (checks `file_exists`) | Medium |
| 4.3 | CSV header row is manually modified by user | `csv.DictReader` expects header; misaligned columns | Medium |
| 4.4 | Log file grows very large (1000+ entries) | `read_log()` loads all into memory; acceptable for small-scale use | Low |
| 4.5 | `status` field contains special formatting (e.g., `drafted (dry_run)`) | Written as-is to CSV; may affect summary counts | Low |
| 4.6 | Status is "failed" but `error` is empty string | Logged without error message; user can't debug | Medium |
| 4.7 | Multiple runs create duplicate timestamps | Fine — timestamps have seconds precision; still distinguishable | Low |
| 4.8 | `show_proof()` called when log file is empty | "No log entries found" message shown | Low |
| 4.9 | Timestamp format contains commas (e.g., ISO with TZ offset) | Could break CSV parsing if not quoted | Medium |

---

## Phase 5: Orchestrator Edge Cases

### main.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 5.1 | Contact list is empty | Summary shows "Total contacts processed: 0" | Low |
| 5.2 | User quits at first prompt | Pipeline stops; partial log written | Medium |
| 5.3 | User quits at last prompt | Pipeline stops; all prior contacts logged | Low |
| 5.4 | All contacts skipped | Summary shows 5 skipped, 0 sent/drafted | Low |
| 5.5 | CLI args conflict (e.g., `--dry-run --send` | Last one wins (argparse handles dest) | Medium |
| 5.6 | `--file` points to a directory instead of a file | `Path.exists()` true but `open()` fails | Medium |
| 5.7 | `--log` flag combined with `--file` | `--log` takes priority; exits after showing log | Medium |
| 5.8 | Generator raises exception for a contact | Logged as "failed"; pipeline continues to next contact | High |
| 5.9 | Summary line overflow (very long company/role names) | Terminal wraps naturally | Low |
| 5.10 | Running without any CLI args when no .env exists | Works fine; uses demo contacts + dry-run mode | Low |

---

## Phase 6: SMTP Sender Edge Cases

### sender.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 6.1 | SMTP server hostname not found (DNS failure) | `smtplib.SMTP()` raises `gaierror` → caught as `Exception` | High |
| 6.2 | SMTP server connection refused | `ConnectionRefusedError` → caught; status="failed" | High |
| 6.3 | SMTP connection times out (slow server) | `smtplib.SMTP()` has default timeout; catches `socket.timeout` | High |
| 6.4 | SMTP authentication fails (wrong password) | `SMTPAuthenticationError` → caught; specific error message | High |
| 6.5 | SMTP auth fails due to expired App Password | Same as 6.4; user told to generate new password | High |
| 6.6 | Gmail blocks login as "less secure app" | `SMTPAuthenticationError` → user directed to enable 2FA | High |
| 6.7 | Sender email not authorized (SMTP relay) | Same auth error pattern | Medium |
| 6.8 | Recipient email domain does not exist | SMTP server accepts message; returns "sent" but will bounce | Medium |
| 6.9 | `From` header has special characters in sender name | MIME encodes properly; no corruption | Low |
| 6.10 | Email body contains non-ASCII characters (emojis, accents) | `MIMEText` with utf-8 handles correctly | Low |
| 6.11 | Connection lost during `send_message()` | Partial send; exception caught; status="failed" | High |
| 6.12 | STARTTLS handshake fails | `smtplib.SMTP.starttls()` raises exception → caught | High |
| 6.13 | Rate limit hit (Gmail: ~500/day) | Gmail sends error through SMTP; caught as `SMTPException` | Medium |
| 6.14 | `DryRunSender` called when dry_run=false (logic error) | Won't happen — `get_sender()` returns based on config flag | Low |
| 6.15 | `SmtpSender` instantiated but credentials empty | Will fail at `.login()` with auth error | High |

---

## Phase 7: Safety & Opt-Out Edge Cases

### opt_out.py

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 7.1 | `opt_out.txt` doesn't exist | `load_opt_outs()` returns empty list | Low |
| 7.2 | `opt_out.txt` has blank lines between entries | Filtered out by `if line.strip()` check | Low |
| 7.3 | `opt_out.txt` has comment lines starting with `#` | Filtered out by `not line.startswith("#")` | Low |
| 7.4 | Same email added to opt-out list twice | Duplicate check prevents second write | Medium |
| 7.5 | Opt-out email has different casing than contact email | Both lowercased for comparison | Medium |
| 7.6 | Opt-out file is read-only after creation | `add_opt_out()` raises `PermissionError` | Medium |

### preview.py — Edit Mode

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 7.7 | User presses Enter on subject (keeps current) | `if new_subject:` is False; original kept | Low |
| 7.8 | User enters only whitespace as new subject | `strip()` results in empty string → original kept | Low |
| 7.9 | User enters `.` as first line of body edit | Immediately exits edit mode; body unchanged | Medium |
| 7.10 | User edits body to be empty | Word count = 0; empty email sent | High |
| 7.11 | User edits body to exceed 150 words | Warning shown in re-preview; still allowed | Medium |
| 7.12 | `Ctrl+C` during multi-line body input | `EOFError` not caught; edit mode exits | Medium |

### Safety Confirmation

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 7.13 | User types "YES" at safety prompt | `.lower()` returns "yes" → send proceeds | Low |
| 7.14 | User types "y" or "yeah" at safety prompt | Only "yes" accepted; treated as "no" | Medium |
| 7.15 | User types nothing (empty) | `strip()` returns "" → treated as "no" → skip | Low |

---

## Phase 8: Testing Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 8.1 | Tests depend on real `.env` file | Fixture isolation required; CI may fail | Critical |
| 8.2 | Tests write to `outreach_log.csv` in real location | Temp isolation needed; can corrupt real logs | High |
| 8.3 | Tests run in parallel (`pytest -n auto`) | File-based tests (`test_logger.py`) conflict | High |
| 8.4 | Network-dependent test fails in offline CI | SMTP tests must use mocks, not real connection | High |
| 8.5 | Generator tests produce flaky results (LLM not deterministic) | Template-based generation is deterministic; fine | Low |

---

## Phase 9: Demo & Documentation Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| 9.1 | `README.md` has outdated setup instructions | User can't set up the project | High |
| 9.2 | `contacts.json` has invalid JSON structure | Loader shows validation errors; demo fails | High |
| 9.3 | User follows README but skips `.env` setup | DRY_RUN mode; safe but user sees no sent emails | Low |
| 9.4 | Screenshot proof requires Gmail Sent folder access | User must verify manually; not automated | Medium |

---

## Phase X: Stretch Goal Edge Cases

### Groq LLM Enhancement

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| X.1 | `GROQ_API_KEY` is missing from `.env` | `Groq()` raises auth error; caught gracefully | High |
| X.2 | Groq API rate limit exceeded | HTTP 429 from API; retry with backoff | Medium |
| X.3 | Groq API is down/unreachable | Request timeout; fall back to template-based email | Medium |
| X.4 | LLM adds fake experience to email | Hallucination detector must catch and reject | Critical |
| X.5 | LLM changes company name or candidate name | Fact preservation check must detect | Critical |
| X.6 | LLM output exceeds 150 words | Enforce word limit after LLM rewrite | High |
| X.7 | API key is invalid | Groq client raises auth error on first call | High |
| X.8 | Free tier quota exhausted | HTTP 429 or 403; user needs to upgrade | Medium |

### Gmail API

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| X.9 | OAuth token expired | Refresh token flow should handle automatically | High |
| X.10 | OAuth consent screen not configured | Auth flow fails with consent error | High |
| X.11 | Gmail API not enabled in GCP project | API call returns 403; clear error message needed | High |
| X.12 | User revokes app access after token granted | API call fails; need to re-authenticate | Medium |

### Streamlit UI

| # | Edge Case | Expected Behavior | Severity |
|---|-----------|-------------------|----------|
| X.13 | User uploads a .txt file instead of JSON/CSV | Streamlit file type validation; show error | Medium |
| X.14 | User uploads a 100MB CSV file | Streamlit has default 200MB limit; show progress | Medium |
| X.15 | Multiple users interact simultaneously | Streamlit is single-user per session; fine | Low |

---

## Summary: Edge Case Severity Distribution

| Severity | Count | Action Required |
|----------|-------|-----------------|
| **Critical** | 5 | Must handle before production use |
| **High** | 31 | Must handle before live demo |
| **Medium** | 30 | Should handle before submission |
| **Low** | 12 | Nice-to-have improvements |

**Total edge cases documented: ~82**

---

## Quick Reference: Top 10 Must-Handle Edge Cases

| Rank | Edge Case | Phase | Why Critical |
|------|-----------|-------|-------------|
| 1 | `.env` secrets committed to git | 0 | Security breach |
| 2 | `DRY_RUN=false` when intended to be dry | 1 | Accidental real sending |
| 3 | LLM hallucinates fake experience | X | Ethical/legal risk |
| 4 | SMTP credentials wrong or expired | 6 | Can't send emails |
| 5 | Template variable missing from data | 2 | Broken email output |
| 6 | CSV malformed with wrong columns | 1 | Data loading fails |
| 7 | Test isolation failure (real .env used) | 8 | Non-deterministic tests |
| 8 | User Ctrl+C during preview | 3 | Ungraceful shutdown |
| 9 | Concurrent log file access | 4 | Log corruption |
| 10 | Network failure during SMTP send | 6 | Email silently unsent |
