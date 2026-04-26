"""
pages/student/registration.py
Student self-registration portal with probation gate and window gate.
Renders the three registration panels via the shared component.
"""

import streamlit as st
from utils.window_check import is_window_open, get_upcoming_window_label
from components.registration_panel import render_registration_panels


def render():
    st.title("📝 Registration Portal")

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("⚠️ No active semester found. Registration is unavailable.")
        return

    semester_id   = sem["semester_id"]
    term_name     = sem["term_name"]
    drop_deadline = sem.get("drop_deadline")

    st.caption(f"Active Semester: **{term_name}**")

    # ── Probation Gate ────────────────────────────────────────────────────────
    if st.session_state.get("student_status") == "PROBATION":
        st.error(
            "🔴 **You are on academic probation.**\n\n"
            "Self-registration is disabled. Please contact your faculty advisor "
            "to complete your course registration."
        )
        return

    # ── Window Gate ───────────────────────────────────────────────────────────
    credits = st.session_state.get("credits_completed", 0)
    cgpa    = st.session_state.get("cgpa", 0.0)

    if not is_window_open("STUDENT", semester_id, credits, cgpa):
        st.error("🔒 **Registration is currently closed for your account.**")
        hint = get_upcoming_window_label("STUDENT", semester_id)
        if hint:
            st.info(f"ℹ️ {hint}")
        return

    st.success("✅ Registration window is open.")

    # ── Registration Panels ───────────────────────────────────────────────────
    render_registration_panels(
        student_id=st.session_state.user_id,
        acting_role="SELF",
        actor_id=st.session_state.user_id,
        semester_id=semester_id,
        drop_deadline=drop_deadline,
    )
