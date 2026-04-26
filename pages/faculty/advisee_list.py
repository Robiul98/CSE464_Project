"""
pages/faculty/advisee_list.py
List of students assigned to this faculty advisor.
"""

import pandas as pd
import streamlit as st
from db import fetch_all


STATUS_BADGE = {
    "ACTIVE":    "🟢 ACTIVE",
    "PROBATION": "🔴 PROBATION",
    "INACTIVE":  "⚫ INACTIVE",
    "GRADUATED": "🎓 GRADUATED",
}


def render():
    st.title("👥 My Advisees")

    faculty_id = st.session_state.user_id

    students = fetch_all(
        """
        SELECT users_user_id, student_name, department, program,
               semester_no, cgpa, credits_completed, student_status
        FROM   students
        WHERE  faculty_faculty_id = :fid
        ORDER  BY student_name
        """,
        {"fid": faculty_id},
    )

    if not students:
        st.info("No advisees assigned to you.")
        return

    # Search
    search = st.text_input("🔍 Search by name or ID", key="advisee_search")
    if search:
        s = search.lower()
        students = [
            r for r in students
            if s in r["student_name"].lower() or s in r["users_user_id"].lower()
        ]

    if not students:
        st.info("No results match your search.")
        return

    for stu in students:
        badge = STATUS_BADGE.get(stu["student_status"], stu["student_status"])
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])
            col1.markdown(f"**{stu['student_name']}**  \n`{stu['users_user_id']}`")
            col2.markdown(f"{stu['department'] or '—'}  \n{stu['program'] or '—'}")
            col3.markdown(f"CGPA: **{float(stu['cgpa']):.2f}**  \nCr: {stu['credits_completed']}")
            col4.markdown(badge)

            b1, b2, _ = st.columns([1, 1, 2])
            if b1.button("👁 Profile", key=f"view_{stu['users_user_id']}"):
                st.session_state.viewed_student_id = stu["users_user_id"]
                st.session_state.nav_page = "Student View"
                st.rerun()
            if b2.button("✏️ Advise", key=f"advise_{stu['users_user_id']}"):
                st.session_state.viewed_student_id = stu["users_user_id"]
                st.session_state.nav_page = "Advising"
                st.rerun()
