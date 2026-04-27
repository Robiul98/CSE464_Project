"""
pages/faculty/profile.py
Faculty's own read-only profile view.
"""

import streamlit as st
from db import fetch_one

def render():
    # ── HEADER SECTION ────────────────────────────────────────────────────────
    st.markdown("## 👨‍🏫 My Faculty Profile")
    st.markdown("View professional details, departmental affiliation, and contact information.")
    st.divider()

    uid = st.session_state.user_id
    
    # ── DATABASE FETCH (Untouched) ────────────────────────────────────────────
    row = fetch_one(
        """
        SELECT user_id, faculty_name, email, department, designation, phone
        FROM   faculty
        WHERE  user_id = :p_user_id
        """,
        {"p_user_id": uid},
    )

    if not row:
        st.warning("⚠️ **Profile not found.** Please contact the system administrator.")
        return

    # ── QUICK OVERVIEW METRICS ────────────────────────────────────────────────
    st.subheader("📌 Overview")
    
    # Using metrics to make their title and department stand out immediately
    m1, m2 = st.columns(2)
    m1.metric(label="Designation", value=row['designation'] or "—")
    m2.metric(label="Department", value=row['department'] or "—")

    st.write("") # Add a little breathing room

    # ── DETAILED INFORMATION CARD ─────────────────────────────────────────────
    st.subheader("📋 Professional Details")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Identity")
            st.markdown(f"**Faculty Name:** {row['faculty_name']}")
            st.markdown(f"**Faculty ID:** {row['user_id']}")
            
        with col2:
            st.markdown("#### 📞 Contact Info")
            st.markdown(f"**Email:** {row['email'] or '—'}")
            st.markdown(f"**Phone:** {row['phone'] or '—'}")