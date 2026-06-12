"""
Streamlit UI for The Closer -- Cold Email Writer + Send Bot.
Provides a web interface for the complete cold email pipeline."""

import sys
import os
import io
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
import pandas as pd

# Add project root to path
_project_root = Path(__file__).parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from models import Contact, Email as EmailModel
from config import Config, load_config, validate_config
from loader import load_contacts, get_demo_contacts, load_from_json, load_from_csv
from generator import generate_email, generate_all, prepare_variables, count_words
from sender import DryRunSender, SmtpSender, get_sender, send_email
from logger import log_result, read_log, get_log_summary
from opt_out import is_opted_out, add_opt_out


# ─── Page Configuration ─────────────────────────────────

st.set_page_config(
    page_title="The Closer -- Cold Email Bot",
    page_icon=":email:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Session State Initialization ──────────────────────

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "contacts": [],
        "generated_emails": {},
        "results": [],
        "current_index": 0,
        "processing": False,
        "processed_count": 0,
        "total_to_process": 0,
        "config_loaded": False,
        "app_config": None,
        "uploaded_file_content": None,
        "data_source": "demo",        "log_refresh_counter": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ─── Helper Functions ──────────────────────────────────

def contact_to_dict(c: Contact) -> dict:
    """Convert a Contact to a dict for pandas."""
    return {
        "recipient_email": c.recipient_email,
        "recipient_name": c.recipient_name,
        "company": c.company,
        "role": c.role,
        "candidate_name": c.candidate_name,
        "candidate_background": c.candidate_background,
        "personalization_note": c.personalization_note,
        "portfolio_url": c.portfolio_url,
        "linkedin_url": c.linkedin_url,
        "job_url": c.job_url,
        "resume_link": c.resume_link,
    }


def dict_to_contact(d: dict) -> Optional[Contact]:
    """Convert a dict back to a Contact, returning None on validation error."""
    try:
        return Contact(**d)
    except (ValueError, TypeError):
        return None


def render_email_preview(email: EmailModel, contact: Contact):
    """Render a generated email preview in Streamlit."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**To:** {contact.recipient_email}")
        st.markdown(f"**Company:** {contact.company}")
        st.markdown(f"**Role:** {contact.role}")
    with col2:
        word_color = "red" if email.word_count > 150 else "green"
        st.markdown(f"**Word Count:** :{word_color}[{email.word_count}/150]")

    st.markdown("---")
    st.markdown(f"### Subject: {email.subject}")
    st.markdown("---")
    st.text_area("Body", email.body, height=250, disabled=True, label_visibility="collapsed")
    st.markdown("---")

    warnings = email.warnings()
    if warnings:
        for w in warnings:
            st.warning(w)


def get_config_from_sidebar() -> Optional[Config]:
    """Load config from .env file (silently — no SMTP fields shown on the dashboard)."""
    config = load_config()

    config.dry_run = st.sidebar.checkbox("Dry Run (log only, no sending)", value=config.dry_run)

    errors = validate_config(config)
    if errors and not config.dry_run:
        for err in errors:
            st.sidebar.error(err)
        return None

    return config


def load_contacts_from_source(source_type: str, uploaded_file=None, file_content=None) -> list:
    """Load contacts from the selected source."""
    if source_type == "demo":
        with st.spinner("Loading demo contacts..."):
            return get_demo_contacts()
    elif source_type == "json" and file_content:
        with st.spinner("Loading contacts from JSON..."):
            try:
                content = file_content.decode("utf-8")
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
                    f.write(content)
                    path = f.name
                contacts = load_from_json(path)
                os.unlink(path)
                return contacts
            except Exception as e:
                st.error(f"Failed to load JSON: {e}")
                return []
    elif source_type == "csv" and file_content:
        with st.spinner("Loading contacts from CSV..."):
            try:
                content = file_content.decode("utf-8")
                with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
                    f.write(content)
                    path = f.name
                contacts = load_from_csv(path)
                os.unlink(path)
                return contacts
            except Exception as e:
                st.error(f"Failed to load CSV: {e}")
                return []
    return []


def display_log_viewer():
    """Display the outreach log in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Outreach Log")

    if st.sidebar.button("Refresh Log"):
        st.session_state.log_refresh_counter += 1

    entries = read_log()
    if not entries:
        st.sidebar.info("No log entries yet.")
        return

    summary = get_log_summary()
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Total", summary["total"])
    col2.metric("Sent", summary["sent"])
    col1.metric("Drafted", summary["drafted"])
    col2.metric("Skipped", summary["skipped"])
    col1.metric("Failed", summary["failed"])

    with st.sidebar.expander("View Log Entries", expanded=False):
        log_df = pd.DataFrame(entries)
        st.dataframe(log_df, use_container_width=True, hide_index=True)


# ─── Sidebar ────────────────────────────────────────────

with st.sidebar:
    st.title("The Closer")
    st.caption("Cold Email Writer + Send Bot")

    st.markdown("---")
    st.subheader("Data Source")

    source_type = st.radio(
        "Choose source:",
        options=["demo", "json", "csv"],
        format_func=lambda x: {"demo": "Demo Contacts", "json": "JSON File", "csv": "CSV File"}[x],
        key="source_type_radio",
    )

    uploaded_file = None
    file_content = None
    if source_type in ("json", "csv"):
        ext = ".json" if source_type == "json" else ".csv"
        uploaded_file = st.file_uploader(
            f"Upload {ext.upper()} file",
            type=[ext.replace(".", "")],
            key="file_uploader",
        )
        if uploaded_file is not None:
            file_content = uploaded_file.getvalue()

    load_button = st.button("Load Contacts", type="primary", use_container_width=True)

    if load_button:
        contacts = load_contacts_from_source(source_type, uploaded_file, file_content)
        if contacts:
            st.session_state.contacts = contacts
            st.session_state.generated_emails = {}
            st.session_state.results = []
            st.session_state.current_index = 0
            st.session_state.processing = False
            st.session_state.processed_count = 0
            st.success(f"Loaded {len(contacts)} contacts!")
        else:
            st.error("No contacts loaded.")

    st.markdown("---")
    app_config = get_config_from_sidebar()
    if app_config:
        st.session_state.app_config = app_config
        st.session_state.config_loaded = True

    display_log_viewer()


# ─── Main Area ──────────────────────────────────────────

st.title("The Closer -- Cold Email Writer + Send Bot")
st.markdown(f"**{len(st.session_state.contacts)}** contacts loaded")

if not st.session_state.contacts:
    st.info("Load contacts from the sidebar to get started. Use demo contacts or upload a JSON/CSV file.")

    with st.expander("Quick Start", expanded=True):
        st.markdown("""
        1. **Choose a data source** in the sidebar (Demo, JSON, or CSV)
        2. Click **Load Contacts**
        3. Browse and edit contacts in the **Contacts** tab
        4. Process contacts with email generation in the **Process** tab
        5. View your outreach history in the **Log** tab
        """)
else:
    tab_contacts, tab_process, tab_log = st.tabs(["Contacts", "Process", "Log"])

    # ─── Tab 1: Contacts Table ─────────────────────────
    with tab_contacts:
        st.subheader("Contact List")

        # Convert contacts to DataFrame for editing
        contacts_data = [contact_to_dict(c) for c in st.session_state.contacts]
        df = pd.DataFrame(contacts_data)

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "recipient_email": st.column_config.TextColumn("Email", required=True, width="medium"),
                "recipient_name": st.column_config.TextColumn("Recipient Name", width="medium"),
                "company": st.column_config.TextColumn("Company", required=True, width="medium"),
                "role": st.column_config.TextColumn("Role", required=True, width="medium"),
                "candidate_name": st.column_config.TextColumn("Your Name", required=True, width="medium"),
                "candidate_background": st.column_config.TextColumn("Background", required=True, width="large"),
                "personalization_note": st.column_config.TextColumn("Personalization", width="large"),
                "portfolio_url": st.column_config.TextColumn("Portfolio", width="medium"),
                "linkedin_url": st.column_config.TextColumn("LinkedIn", width="medium"),
                "job_url": st.column_config.TextColumn("Job URL", width="medium"),
                "resume_link": st.column_config.TextColumn("Resume", width="medium"),
            },
            key="contact_editor",
        )

        if st.button("Update Contacts from Table", use_container_width=True):
            new_contacts = []
            errors = 0
            for _, row in edited_df.iterrows():
                row_dict = row.to_dict()
                # Remove NaN values
                cleaned = {k: v for k, v in row_dict.items() if pd.notna(v)}
                c = dict_to_contact(cleaned)
                if c:
                    new_contacts.append(c)
                else:
                    errors += 1

            if new_contacts:
                st.session_state.contacts = new_contacts
                st.session_state.generated_emails = {}
                st.session_state.results = []
                st.success(f"Updated {len(new_contacts)} contacts!")
                if errors:
                    st.warning(f"{errors} row(s) had validation errors and were skipped.")
                st.rerun()
            else:
                st.error("No valid contacts found in the table.")

    # ─── Tab 2: Email Processing ───────────────────────
    with tab_process:
        st.subheader("Email Processing Pipeline")

        if not st.session_state.config_loaded:
            st.warning("SMTP configuration is incomplete. Check your .env file and ensure SMTP credentials are set.")
        else:
            config = st.session_state.app_config
            contacts = st.session_state.contacts

            # Mode indicator
            mode_color = "green" if config.dry_run else "red"
            st.markdown(f"**:{mode_color}[{'DRY RUN MODE' if config.dry_run else 'LIVE SEND MODE'}]**")
            if config.dry_run:
                st.caption("No emails will be sent. Emails will be drafted and logged.")
            else:
                st.warning("Emails will actually be sent! Ensure your SMTP configuration is correct.")

            st.markdown("---")

            # Contact selector
            contact_names = [
                f"{i+1}. {c.company} -- {c.role} ({c.recipient_email})"
                for i, c in enumerate(contacts)
            ]

            selected_idx = st.selectbox(
                "Select contact to process:",
                range(len(contacts)),
                format_func=lambda i: contact_names[i],
                key="contact_selector",
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                generate_btn = st.button("Generate Email", type="primary", use_container_width=True)
            with col2:
                batch_btn = st.button("Process All (Batch)", use_container_width=True)
            with col3:
                if st.session_state.generated_emails:
                    st.button("Clear Results", use_container_width=True, on_click=lambda: st.session_state.update({
                        "generated_emails": {},
                        "results": [],
                        "processed_count": 0,
                    }))

            # Generate single email
            if generate_btn:
                contact = contacts[selected_idx]
                try:
                    email = generate_email(contact)
                    st.session_state.generated_emails[selected_idx] = email
                    st.success(f"Email generated! ({email.word_count} words)")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

            # Batch processing
            if batch_btn:
                st.session_state.processing = True
                st.session_state.total_to_process = len(contacts)
                st.session_state.processed_count = 0
                st.session_state.results = []

                progress_bar = st.progress(0, text="Starting batch processing...")
                status_text = st.empty()

                for i, contact in enumerate(contacts):
                    status_text.info(f"Processing {i+1}/{len(contacts)}: {contact.company}")

                    try:
                        email = generate_email(contact)
                        st.session_state.generated_emails[i] = email

                        if config.dry_run:
                            status = "drafted (dry_run)"
                        else:
                            result = send_email(contact, email, config)
                            status = result.status
                            if result.error:
                                log_result(contact, email, status, result.error)
                                st.session_state.results.append((contact, status))
                                st.session_state.processed_count = i + 1
                                progress = (i + 1) / len(contacts)
                                progress_bar.progress(progress, text=f"Processed {i+1}/{len(contacts)}")
                                continue

                        log_result(contact, email, status)
                        st.session_state.results.append((contact, status))

                    except Exception as e:
                        log_result(contact, EmailModel("", "", 0, contact), "failed", str(e))
                        st.session_state.results.append((contact, "failed"))

                    st.session_state.processed_count = i + 1
                    progress = (i + 1) / len(contacts)
                    progress_bar.progress(progress, text=f"Processed {i+1}/{len(contacts)}")

                st.session_state.processing = False
                status_text.success(f"Batch complete! Processed {len(contacts)} contacts.")
                st.rerun()

            st.markdown("---")

            # Email preview for selected contact
            if selected_idx in st.session_state.generated_emails:
                email = st.session_state.generated_emails[selected_idx]
                contact = contacts[selected_idx]

                render_email_preview(email, contact)

                # Subject & Body editing
                with st.expander("Edit Email", expanded=False):
                    new_subject = st.text_input("Subject", value=email.subject, key="edit_subject")
                    new_body = st.text_area("Body", value=email.body, height=200, key="edit_body")

                    if st.button("Apply Edits", use_container_width=True):
                        email.subject = new_subject
                        email.body = new_body
                        email.word_count = count_words(new_body)
                        st.success(f"Email updated! ({email.word_count} words)")
                        st.rerun()

                # Action buttons
                st.markdown("### Actions")
                act_col1, act_col2, act_col3, act_col4 = st.columns(4)

                with act_col1:
                    if st.button(":white_check_mark: Send", type="primary", use_container_width=True):
                        if config.dry_run:
                            log_result(contact, email, "drafted (dry_run)")
                            st.success(f"Drafted (dry run): {contact.recipient_email}")
                        else:
                            result = send_email(contact, email, config)
                            if result.status == "sent":
                                log_result(contact, email, "sent")
                                st.success(f"Sent to {contact.recipient_email}")
                            else:
                                log_result(contact, email, result.status, result.error)
                                st.error(f"Failed: {result.error}")
                        st.session_state.results.append((contact, "sent" if not config.dry_run else "drafted"))
                        st.rerun()

                with act_col2:
                    if st.button(":pause_button: Draft", use_container_width=True):
                        log_result(contact, email, "drafted")
                        st.info(f"Drafted: {contact.recipient_email}")
                        st.session_state.results.append((contact, "drafted"))
                        st.rerun()

                with act_col3:
                    if st.button(":next_track_button: Skip", use_container_width=True):
                        log_result(contact, email, "skipped")
                        st.info(f"Skipped: {contact.company}")
                        st.session_state.results.append((contact, "skipped"))
                        st.rerun()

                with act_col4:
                    if st.button(":no_entry: Opt Out", use_container_width=True):
                        add_opt_out(contact.recipient_email)
                        log_result(contact, email, "skipped")
                        st.warning(f"Opted out: {contact.recipient_email}")
                        st.session_state.results.append((contact, "skipped"))
                        st.rerun()
            elif selected_idx < len(contacts):
                st.info("Select a contact and click 'Generate Email' to see the preview here.")

            # Results summary
            if st.session_state.results:
                st.markdown("---")
                st.subheader("Results Summary")
                results_df = pd.DataFrame(
                    [(c.company, c.role, c.recipient_email, s) for c, s in st.session_state.results],
                    columns=["Company", "Role", "Email", "Status"],
                )
                st.dataframe(results_df, use_container_width=True, hide_index=True)

    # ─── Tab 3: Log Viewer ────────────────────────────
    with tab_log:
        st.subheader("Outreach Log")

        entries = read_log()
        if not entries:
            st.info("No log entries yet. Process some contacts to see the log here.")
        else:
            summary = get_log_summary()

            metrics_cols = st.columns(5)
            metrics_cols[0].metric("Total", summary["total"])
            metrics_cols[1].metric("Sent", summary["sent"])
            metrics_cols[2].metric("Drafted", summary["drafted"])
            metrics_cols[3].metric("Skipped", summary["skipped"])
            metrics_cols[4].metric("Failed", summary["failed"])

            st.markdown("---")
            log_df = pd.DataFrame(entries)
            st.dataframe(log_df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download Log as CSV",
                data=pd.DataFrame(entries).to_csv(index=False).encode("utf-8"),
                file_name="outreach_log.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ─── Footer ─────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.caption("The Closer v1.0 | Cold Email Writer + Send Bot")
