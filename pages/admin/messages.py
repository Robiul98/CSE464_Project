"""
pages/admin/messages.py
Admin inbox for faculty messages. Mark as read, add notes.
"""

import streamlit as st
from db import fetch_all, execute


def render():
    st.title("📬 Faculty Messages")

    messages = fetch_all(
        """
        SELECT fm.message_id, f.faculty_name, f.department,
               fm.subject,
               TO_CHAR(fm.sent_at, 'YYYY-MM-DD HH24:MI') AS sent_at,
               fm.status, fm.admin_note,
               TO_CHAR(fm.read_at, 'YYYY-MM-DD HH24:MI') AS read_at,
               fm.body
        FROM   faculty_messages fm
        JOIN   faculty f ON fm.faculty_id = f.user_id
        ORDER  BY fm.sent_at DESC
        """,
    )

    unread = [m for m in messages if m["status"] == "UNREAD"]
    all_m  = messages

    tab1, tab2 = st.tabs([f"📬 Unread ({len(unread)})", "📭 All Messages"])

    def _render_messages(msg_list):
        if not msg_list:
            st.info("No messages.")
            return
        for msg in msg_list:
            mid         = msg["message_id"]
            is_unread   = msg["status"] == "UNREAD"
            icon        = "📬" if is_unread else "📭"
            border_flag = True

            with st.expander(
                f"{icon}  **{msg['faculty_name']}** ({msg['department']})  |  "
                f"{msg['subject']}  |  {msg['sent_at']}"
            ):
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**From:** {msg['faculty_name']} — {msg['department']}")
                col1.markdown(f"**Sent:** {msg['sent_at']}")
                if msg["read_at"]:
                    col1.markdown(f"**Read:** {msg['read_at']}")
                col2.markdown(f"**Status:** {'🔴 UNREAD' if is_unread else '🟢 READ'}")

                st.divider()
                st.markdown("**Message:**")
                st.write(msg["body"])

                st.divider()
                note_val = msg["admin_note"] or ""
                new_note = st.text_area(
                    "Admin Note (optional — visible to faculty on their sent messages)",
                    value=note_val,
                    key=f"note_{mid}",
                )

                b1, b2, _ = st.columns([1.2, 1.2, 3])

                if is_unread:
                    if b1.button("✅ Mark as Read", key=f"read_{mid}"):
                        execute(
                            """
                            UPDATE faculty_messages
                            SET    status = 'READ', read_at = SYSTIMESTAMP
                            WHERE  message_id = :mid
                            """,
                            {"mid": mid},
                        )
                        st.toast("Marked as read.", icon="✅")
                        st.rerun()

                if b2.button("💾 Save Note", key=f"savenote_{mid}"):
                    execute(
                        "UPDATE faculty_messages SET admin_note = :note WHERE message_id = :mid",
                        {"note": new_note.strip() or None, "mid": mid},
                    )
                    st.toast("Note saved.", icon="💾")
                    st.rerun()

    with tab1:
        _render_messages(unread)

    with tab2:
        _render_messages(all_m)
