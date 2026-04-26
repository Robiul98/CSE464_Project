"""
pages/faculty/all_courses.py
Read-only all courses list for faculty. No student-specific flags.
Includes Curriculum viewer.
"""

import pandas as pd
import streamlit as st
from db import fetch_all
from components.curriculum_viewer import show_curriculum


def render():
    st.title("📚 All Courses")

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("No active semester found.")
        return

    semester_id = sem["semester_id"]
    st.caption(f"Active Semester: **{sem['term_name']}**")

    courses = fetch_all(
        """
        SELECT c.course_id, c.course_code, c.course_title, c.credits,
               c.department, c.level_no, co.offering_status,
               COUNT(cs.section_id)    AS total_sections,
               SUM(cs.max_capacity)    AS total_seats,
               SUM(cs.available_seats) AS avail_seats
        FROM   course_offerings co
        JOIN   courses c ON co.course_id = c.course_id
        LEFT   JOIN course_sections cs ON cs.offering_id = co.offering_id
        WHERE  co.semesters_id = :sem
        GROUP  BY c.course_id, c.course_code, c.course_title, c.credits,
                  c.department, c.level_no, co.offering_status
        ORDER  BY c.department, c.level_no, c.course_code
        """,
        {"sem": semester_id},
    )

    if not courses:
        st.info("No courses offered this semester.")
        return

    depts = sorted({c["department"] or "Unknown" for c in courses})
    dept_filter = st.selectbox("Filter by Department", ["All"] + depts, key="fac_ac_dept")

    display = []
    for c in courses:
        if dept_filter != "All" and (c["department"] or "Unknown") != dept_filter:
            continue
        display.append({
            "_course_id": c["course_id"],
            "Code":       c["course_code"],
            "Title":      c["course_title"],
            "Cr":         c["credits"],
            "Dept":       c["department"] or "—",
            "Lvl":        c["level_no"] or "—",
            "Status":     c["offering_status"],
            "Sections":   int(c["total_sections"] or 0),
            "Tot Seats":  int(c["total_seats"] or 0),
            "Avail":      int(c["avail_seats"] or 0),
        })

    if not display:
        st.info("No courses match the filter.")
        return

    df = pd.DataFrame(display).drop(columns=["_course_id"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 Curriculum Viewer")
    course_options = {f"{c['Code']} — {c['Title']}": c["_course_id"] for c in display}
    selected_label = st.selectbox("Select course", list(course_options.keys()), key="fac_cv")
    if selected_label:
        show_curriculum(course_options[selected_label])
