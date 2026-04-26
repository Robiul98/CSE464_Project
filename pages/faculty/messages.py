"""
pages/faculty/messages.py
Faculty message compose and sent history.
Messages are free-form text sent to admin for manual action.
"""

import pandas as pd
import streamlit as st
from db import fetch_all, execute


def render():
    st.title("📨 Messages to Admin")

    faculty_id = st.session_state.user_id
    tab1, tab2 = st.tabs(["✉️ Compose", "📬 Sent Messages"])

    # ── Compose ───────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Send a Message to Admin")
        st.caption(
            "Use this to request course changes, new sections, seat extensions, "
            "or any other administrative action. Admin will review and act manually."
        )

        with st.form("compose_message_form", clear_on_submit=True):
            subject = st.text_input("Subject *", max_chars=200,
                                    placeholder="e.g. Request: Add new section for CS101")
            body    = st.text_area("Message *", height=200,
                                   placeholder="Describe your request in detail...")
            submit  = st.form_submit_button("📤 Send Message", type="primary")

        if submit:
            if not subject.strip():
                st.error("Subject is required.")
            elif not body.strip():
                st.error("Message body is required.")
            else:
                execute(
                    """
                    INSERT INTO faculty_messages
                        (faculty_id, subject, body, sent_at, status)
                    VALUES
                        (:fid, :subj, :body, SYSTIMESTAMP, 'UNREAD')
                    """,
                    {"fid": faculty_id, "subj": subject.strip(), "body": body.strip()},
                )
                st.toast("Message sent to admin.", icon="📨")

    # ── Sent Messages ─────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Sent Messages")

        messages = fetch_all(
            """
            SELECT message_id, subject,
                   TO_CHAR(sent_at, 'YYYY-MM-DD HH24:MI') AS sent_at,
                   status, admin_note,
                   TO_CHAR(read_at, 'YYYY-MM-DD HH24:MI') AS read_at,
                   body
            FROM   faculty_messages
            WHERE  faculty_id = :fid
            ORDER  BY sent_at DESC
            """,
            {"fid": faculty_id},
        )

        if not messages:
            st.info("No messages sent yet.")
            return

        for msg in messages:
            status_icon = "📭 READ" if msg["status"] == "READ" else "📬 UNREAD"
            with st.expander(
                f"{status_icon}  |  {msg['subject']}  |  {msg['sent_at']}"
            ):
                st.markdown(f"**Status:** {status_icon}")
                if msg["read_at"]:
                    st.markdown(f"**Read at:** {msg['read_at']}")
                st.divider()
                st.markdown("**Your message:**")
                st.write(msg["body"])
                if msg["admin_note"]:
                    st.divider()
                    st.markdown("**Admin note:**")
                    st.info(msg["admin_note"])
