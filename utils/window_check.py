"""
utils/window_check.py
Check whether an advising window is currently open for a given role / student profile.
"""

import streamlit as st
from db import fetch_one


def is_window_open(role: str, semester_id: int,
                   credits_completed: int = None, cgpa: float = None) -> bool: # type: ignore
    """
    Returns True if at least one advising_windows row is currently active
    matching the given role and (optionally) credit/cgpa range.

    - role: 'STUDENT' | 'FACULTY' | 'ADMIN'
    - semester_id: active semester pk
    - credits_completed / cgpa: only relevant for STUDENT windows
    """
    if semester_id is None:
        return False

    sql = """
        SELECT 1
        FROM   advising_windows
        WHERE  target_role  = :role
          AND  semester_id  = :sem_id
          AND  SYSTIMESTAMP BETWEEN start_time AND end_time
          AND  (:credits IS NULL OR :credits BETWEEN min_credits AND max_credits)
          AND  (min_cgpa IS NULL OR :cgpa IS NULL OR :cgpa >= min_cgpa)
          AND  (max_cgpa IS NULL OR :cgpa IS NULL OR :cgpa <= max_cgpa)
        FETCH FIRST 1 ROW ONLY
    """
    row = fetch_one(sql, {
        "role": role,
        "sem_id": semester_id,
        "credits": credits_completed,
        "cgpa": cgpa,
    })
    return row is not None


def get_upcoming_window_label(role: str, semester_id: int) -> str | None:
    """
    Return reason_label + start_time of the next upcoming window, or None.
    Used to give students a hint about when registration will open.
    """
    if semester_id is None:
        return None
    row = fetch_one(
        """
        SELECT reason_label, start_time
        FROM   advising_windows
        WHERE  target_role = :role
          AND  semester_id = :sem_id
          AND  start_time  > SYSTIMESTAMP
        ORDER BY start_time ASC
        FETCH FIRST 1 ROW ONLY
        """,
        {"role": role, "sem_id": semester_id},
    )
    if row:
        label = row.get("reason_label") or "Registration"
        st_time = row.get("start_time")
        return f"{label} opens at {st_time}"
    return None
