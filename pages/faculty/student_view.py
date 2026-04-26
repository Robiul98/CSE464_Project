"""
pages/faculty/student_view.py
Read-only student profile viewed by faculty.
Also shows current semester enrollments for the student.
"""

import pandas as pd
import streamlit as st
from db import fetch_one, fetch_all


STATUS_BADGE = {
    "ACTIVE":    "🟢 ACTIVE",
    "PROBATION": "🔴 PROBATION",
    "INACTIVE":  "⚫ INACTIVE",
    "GRADUATED": "🎓 GRADUATED",
}


def render():
    st.title("👤 Student Profile")

    student_id = st.session_state.get("viewed_student_id")
    if not student_id:
        st.warning("No student selected. Go to My Advisees and click View Profile.")
        return

    if st.button("← Back to Advisees"):
        st.session_state.nav_page = "My Advisees"
        st.rerun()

    row = fetch_one(
        """
        SELECT s.users_user_id, s.student_name, s.email, s.department,
               s.program, s.semester_no, s.cgpa, s.credits_completed,
               s.admission_term, s.student_status,
               f.faculty_name AS advisor_name
        FROM   students s
        LEFT   JOIN faculty f ON s.faculty_faculty_id = f.user_id
        WHERE  s.users_user_id = :p_user_id
        """,
        {"p_user_id": student_id},
    )

    if not row:
        st.error("Student not found.")
        return

    status = row["student_status"]
    badge  = STATUS_BADGE.get(status, status)

    if status == "PROBATION":
        st.error("🔴 This student is on academic probation.")

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
        st.markdown(f"**Status:** {badge}")

    # Current semester enrollments
    sem = st.session_state.get("active_semester")
    if sem:
        st.subheader(f"Current Enrollments — {sem['term_name']}")
        enrollments = fetch_all(
            """
            SELECT c.course_code, c.course_title, c.credits,
                   cs.section_name, f.faculty_name,
                   cs.room_no, e.enrollment_status,
                   TO_CHAR(e.enrolled_at, 'YYYY-MM-DD HH24:MI') AS enrolled_at
            FROM   enrollments e
            JOIN   course_sections cs ON e.section_id = cs.section_id
            JOIN   course_offerings co ON cs.offering_id = co.offering_id
            JOIN   courses c ON co.course_id = c.course_id
            LEFT   JOIN faculty f ON cs.faculty_id = f.user_id
            WHERE  e.students_id      = :sid
              AND  co.semesters_id    = :sem
              AND  e.enrollment_status = 'ENROLLED'
            ORDER  BY c.course_code
            """,
            {"sid": student_id, "sem": sem["semester_id"]},
        )
        if enrollments:
            df = pd.DataFrame(enrollments)
            df.columns = ["Code", "Title", "Credits", "Section",
                          "Faculty", "Room", "Status", "Enrolled At"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active enrollments this semester.")

    # Quick advise button
    if st.button("✏️ Go to Advising for this Student", type="primary"):
        st.session_state.nav_page = "Advising"
        st.rerun()
