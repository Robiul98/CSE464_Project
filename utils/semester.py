"""
utils/semester.py
Resolve the active semester. Called once on login and stored in session_state.
"""

import streamlit as st
from db import fetch_one


def get_active_semester() -> dict | None:
    """
    Return the ACTIVE semester row as a dict, or None if none exists.
    Keys: semester_id, term_name, start_date, end_date,
          registration_start, registration_end, drop_deadline, status
    """
    row = fetch_one(
        """
        SELECT semester_id, term_name, start_date, end_date,
               registration_start, registration_end, drop_deadline, status
        FROM   semesters
        WHERE  status = 'ACTIVE'
        FETCH FIRST 1 ROW ONLY
        """,
    )
    return row


def load_active_semester():
    """
    Load active semester into st.session_state.active_semester.
    Called during login. Safe to call multiple times.
    """
    if "active_semester" not in st.session_state:
        sem = get_active_semester()
        st.session_state.active_semester = sem  # None if no active semester
