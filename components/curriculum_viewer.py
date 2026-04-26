"""
components/curriculum_viewer.py
Reusable curriculum / prerequisite tree viewer.
"""

import streamlit as st
from db import fetch_all


def show_curriculum(course_id: int, student_id: str = None): # type: ignore
    """
    Render the prerequisite list for a course in a dialog/expander.
    If student_id is provided, shows Met / Not Met status per prereq.
    """
    prereqs = fetch_all(
        """
        SELECT cp.courses_course_id1 AS prereq_id,
               c.course_code, c.course_title, c.credits
        FROM   course_prerequisites cp
        JOIN   courses c ON cp.courses_course_id1 = c.course_id
        WHERE  cp.courses_course_id = :cid
        ORDER  BY c.course_code
        """,
        {"cid": course_id},
    )

    if not prereqs:
        st.info("✅ No prerequisites required for this course.")
        return

    met_set = set()
    if student_id:
        taken = fetch_all(
            """
            SELECT course_id FROM takes
            WHERE  user_id = :p_user_id
              AND  grade IS NOT NULL
              AND  grade != 'F'
            """,
            {"p_user_id": student_id},
        )
        met_set = {r["course_id"] for r in taken}

    rows = []
    for p in prereqs:
        if student_id:
            status = "✅ Met" if p["prereq_id"] in met_set else "❌ Not Met"
        else:
            status = "—"
        rows.append({
            "Course Code": p["course_code"],
            "Title": p["course_title"],
            "Credits": p["credits"],
            "Status": status,
        })

    import pandas as pd
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
