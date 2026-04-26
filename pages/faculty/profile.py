"""
pages/faculty/profile.py
Faculty's own read-only profile view.
"""

import streamlit as st
from db import fetch_one


def render():
    st.title("👤 My Profile")

    uid = st.session_state.user_id
    
    # Changed :p_user_id to :p_user_id in both the SQL string and the dictionary
    row = fetch_one(
        """
        SELECT user_id, faculty_name, email, department, designation, phone
        FROM   faculty
        WHERE  user_id = :p_user_id
        """,
        {"p_user_id": uid},
    )

    if not row:
        st.error("Profile not found.")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Faculty Name:** {row['faculty_name']}")
            st.markdown(f"**Faculty ID:** {row['user_id']}")
            st.markdown(f"**Email:** {row['email'] or '—'}")
        with col2:
            st.markdown(f"**Department:** {row['department'] or '—'}")
            st.markdown(f"**Designation:** {row['designation'] or '—'}")
            st.markdown(f"**Phone:** {row['phone'] or '—'}")