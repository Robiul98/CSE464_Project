"""
pages/student/profile.py
Student's own read-only profile view.
"""

import streamlit as st
from db import fetch_one


def render():
    st.title("👤 My Profile")

    uid = st.session_state.user_id
    
    # The comment is now OUTSIDE the SQL string so Oracle won't read it
    row = fetch_one(
        """
        SELECT s.users_user_id, s.student_name, s.email, s.department,
               s.program, s.semester_no, s.cgpa, s.credits_completed,
               s.admission_term, s.student_status,
               f.faculty_name AS advisor_name
        FROM   students s
        LEFT   JOIN faculty f ON s.faculty_faculty_id = f.user_id
        WHERE  s.users_user_id = :p_student_id
        """,
        {"p_student_id": uid},
    )

    if not row:
        st.error("Profile not found.")
        return

    status = row["student_status"]

    if status == "PROBATION":
        st.error("🔴 **ON ACADEMIC PROBATION** — Self-registration is disabled. Contact your advisor.")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Student Name:** {row['student_name']}")
            st.markdown(f"**Student ID:** {row['users_user_id']}")
            st.markdown(f"**Email:** {row['email'] or '—'}")
            st.markdown(f"**Department:** {row['department'] or '—'}")
            st.markdown(f"**Program:** {row['program'] or '—'}")
        with col2:
            st.markdown(f"**Current Semester:** {row['semester_no'] or '—'}")
            st.markdown(f"**Admission Term:** {row['admission_term'] or '—'}")
            st.markdown(f"**Credits Completed:** {row['credits_completed']}")
            st.markdown(f"**CGPA:** {float(row['cgpa']):.2f}")
            st.markdown(f"**Advisor:** {row['advisor_name'] or '—'}")

        status_colors = {
            "ACTIVE": "🟢 ACTIVE",
            "PROBATION": "🔴 PROBATION",
            "INACTIVE": "⚫ INACTIVE",
            "GRADUATED": "🎓 GRADUATED",
        }
        st.markdown(f"**Status:** {status_colors.get(status, status)}")