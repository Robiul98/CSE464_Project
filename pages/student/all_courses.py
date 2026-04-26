"""
pages/student/all_courses.py
Read-only all courses list for the active semester with Tot/F/R/Prereq flags.
Accessible regardless of probation status or window status.
"""

import pandas as pd
import streamlit as st
from db import fetch_all
from components.curriculum_viewer import show_curriculum


def _get_student_course_flags(student_id: str) -> tuple[set, set, set]:
    """Return (f_ids, passed_ids, all_taken_ids)."""
    taken = fetch_all(
        # Changed :p_user_id to :p_user_id in both the string and dictionary
        "SELECT course_id, grade FROM takes WHERE user_id = :p_user_id",
        {"p_user_id": student_id},
    )
    f_ids      = {r["course_id"] for r in taken if r["grade"] == "F"}
    passed_ids = {r["course_id"] for r in taken if r["grade"] is not None and r["grade"] != "F"}
    all_taken  = {r["course_id"] for r in taken}
    return f_ids, passed_ids, all_taken


def _prereqs_met(course_id: int, passed_ids: set, prereq_map: dict) -> bool:
    required = prereq_map.get(course_id, set())
    return required.issubset(passed_ids)


def render():
    st.title("📚 All Courses")

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("⚠️ No active semester found.")
        return

    semester_id = sem["semester_id"]
    st.caption(f"Active Semester: **{sem['term_name']}**")

    student_id = st.session_state.user_id
    f_ids, passed_ids, all_taken = _get_student_course_flags(student_id)

    # Build prereq map: course_id → set of required prereq course_ids
    prereq_rows = fetch_all(
        "SELECT courses_course_id AS cid, courses_course_id1 AS preq FROM course_prerequisites"
    )
    prereq_map: dict[int, set] = {}
    for r in prereq_rows:
        prereq_map.setdefault(r["cid"], set()).add(r["preq"])

    # Main query: one row per course (aggregated sections)
    courses = fetch_all(
        """
        SELECT c.course_id, c.course_code, c.course_title, c.credits,
               c.department, c.level_no, co.offering_status,
               COUNT(cs.section_id)      AS total_sections,
               SUM(cs.max_capacity)      AS total_seats,
               SUM(cs.available_seats)   AS avail_seats
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

    # Dept filter
    depts = sorted({c["department"] or "Unknown" for c in courses})
    dept_filter = st.selectbox("Filter by Department", ["All"] + depts, key="ac_dept")

    # Build display list
    display = []
    for c in courses:
        if dept_filter != "All" and (c["department"] or "Unknown") != dept_filter:
            continue
        cid = c["course_id"]
        display.append({
            "_course_id": cid,
            "Code":       c["course_code"],
            "Title":      c["course_title"],
            "Cr":         c["credits"],
            "Dept":       c["department"] or "—",
            "Lvl":        c["level_no"] or "—",
            "Status":     c["offering_status"],
            "Sections":   int(c["total_sections"] or 0),
            "Tot Seats":  int(c["total_seats"] or 0),
            "Avail":      int(c["avail_seats"] or 0),
            "F":          "✓" if cid in f_ids else "",
            "R":          "✓" if cid in passed_ids else "",
            "Prereq":     "✅" if _prereqs_met(cid, passed_ids, prereq_map) else "❌",
            "Taken":      "✓" if cid in all_taken else "",
        })

    if not display:
        st.info("No courses match the filter.")
        return

    df_display = pd.DataFrame(display).drop(columns=["_course_id"])
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 Curriculum Viewer")
    st.caption("Select a course to view its prerequisites.")

    course_options = {f"{c['Code']} — {c['Title']}": c["_course_id"] for c in display}
    selected_label = st.selectbox("Select course", list(course_options.keys()), key="cv_course")
    if selected_label:
        selected_cid = course_options[selected_label]
        show_curriculum(selected_cid, student_id=student_id)
