"""
pages/faculty/advising.py
Faculty advising portal. Faculty selects a student and advises on their behalf.
Uses the shared registration panel component with acting_role='FACULTY'.
"""

import streamlit as st
from db import fetch_one, fetch_all
from utils.window_check import is_window_open
from components.registration_panel import render_registration_panels


STATUS_BADGE = {
    "ACTIVE":    "🟢 ACTIVE",
    "PROBATION": "🔴 PROBATION",
    "INACTIVE":  "⚫ INACTIVE",
    "GRADUATED": "🎓 GRADUATED",
}


def render():
    st.title("✏️ Student Advising")

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("No active semester found. Advising is unavailable.")
        return

    semester_id   = sem["semester_id"]
    drop_deadline = sem.get("drop_deadline")

    # ── Faculty window gate ───────────────────────────────────────────────────
    if not is_window_open("FACULTY", semester_id):
        st.error("🔒 **Faculty advising window is currently closed.**")
        return

    st.success("✅ Faculty advising window is open.")

    # ── Student selection ─────────────────────────────────────────────────────
    st.subheader("Select Student")

    # Pre-fill from advisee list navigation
    pre_id = st.session_state.get("viewed_student_id", "")

    student_id_input = st.text_input(
        "Student ID", value=pre_id,
        placeholder="Enter student ID or select from advisees",
        key="advising_student_input",
    )

    student_row = None
    if student_id_input:
        # Comments are now safely in Python land!
        # Changed variable to :p_student_id and updated the dictionary key
        student_row = fetch_one(
            """
            SELECT s.users_user_id, s.student_name, s.department, s.program,
                   s.semester_no, s.cgpa, s.credits_completed, s.student_status,
                   f.faculty_name AS advisor_name
            FROM   students s
            LEFT   JOIN faculty f ON s.faculty_faculty_id = f.user_id
            WHERE  s.users_user_id = :p_student_id
            """,
            {"p_student_id": student_id_input.strip()},
        )
        if not student_row:
            st.error("Student not found.")
            return

    if not student_row:
        st.info("Enter a student ID above to begin advising.")
        return

    student_id = student_row["users_user_id"]
    status     = student_row["student_status"]
    badge      = STATUS_BADGE.get(status, status)

    # ── Student header card ───────────────────────────────────────────────────
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**{student_row['student_name']}** \n`{student_id}`")
        col2.markdown(
            f"CGPA: **{float(student_row['cgpa']):.2f}** \n"
            f"Credits: **{student_row['credits_completed']}**"
        )
        col3.markdown(f"Status: **{badge}**")

    if status == "PROBATION":
        st.warning("🔴 This student is on academic probation. Faculty advising is permitted.")

    st.caption(f"Active Semester: **{sem['term_name']}**")
    st.divider()

    # ── Registration panels (acting as faculty) ───────────────────────────────
    render_registration_panels(
        student_id=student_id,
        acting_role="FACULTY",
        actor_id=st.session_state.user_id,
        semester_id=semester_id,
        drop_deadline=drop_deadline,
    )