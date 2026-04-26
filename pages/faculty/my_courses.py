"""
pages/faculty/my_courses.py
Sections assigned to this faculty member in the active semester.
"""

import pandas as pd
import streamlit as st
from db import fetch_all


def render():
    st.title("📖 My Courses")

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("No active semester found.")
        return

    semester_id = sem["semester_id"]
    faculty_id  = st.session_state.user_id
    st.caption(f"Active Semester: **{sem['term_name']}**")

    sections = fetch_all(
        """
        SELECT c.course_code, c.course_title, c.credits,
               cs.section_id, cs.section_name, cs.room_no,
               cs.max_capacity, cs.available_seats, cs.section_status
        FROM   course_sections cs
        JOIN   course_offerings co ON cs.offering_id = co.offering_id
        JOIN   courses c ON co.course_id = c.course_id
        WHERE  cs.faculty_id    = :fid
          AND  co.semesters_id  = :sem
        ORDER  BY c.course_code, cs.section_name
        """,
        {"fid": faculty_id, "sem": semester_id},
    )

    if not sections:
        st.info("No sections assigned to you this semester.")
        return

    for sec in sections:
        with st.expander(
            f"**{sec['course_code']}** — {sec['course_title']}  |  Section {sec['section_name']}  |  {sec['section_status']}"
        ):
            col1, col2 = st.columns(2)
            col1.markdown(f"**Credits:** {sec['credits']}")
            col1.markdown(f"**Room:** {sec['room_no'] or '—'}")
            col2.markdown(f"**Max Capacity:** {sec['max_capacity']}")
            col2.markdown(f"**Available Seats:** {sec['available_seats']}")

            # Schedule
            schedule = fetch_all(
                """
                SELECT day_of_week,
                       TO_CHAR(start_time, 'HH24:MI') AS st,
                       TO_CHAR(end_time,   'HH24:MI') AS et,
                       class_type
                FROM   section_schedule
                WHERE  section_id = :sid
                ORDER  BY day_of_week
                """,
                {"sid": sec["section_id"]},
            )
            if schedule:
                st.markdown("**Schedule:**")
                df = pd.DataFrame(schedule)
                df.columns = ["Day", "Start", "End", "Type"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No schedule entries found.")
