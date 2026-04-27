"""
pages/student/registration.py
Student self-registration portal with probation gate and window gate.
Renders the registration panels via the shared component.
"""

import streamlit as st
from utils.window_check import is_window_open, get_upcoming_window_label
from components.registration_panel import render_registration_panels


def render():
    # ── HEADER SECTION ────────────────────────────────────────────────────────
    st.markdown("## 📝 Course Registration Portal")
    st.markdown("Plan your upcoming semester. Select, add, and manage your courses below.")
    st.divider()

    sem = st.session_state.get("active_semester")
    if not sem:
        st.warning("⚠️ **No active semester found.** Registration is currently unavailable.")
        return

    semester_id   = sem["semester_id"]
    term_name     = sem["term_name"]
    drop_deadline = sem.get("drop_deadline")

    # ── ACTIVE SEMESTER INFO CARD ─────────────────────────────────────────────
    # Wraps the semester details in a clean, dashboard-style bordered box
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🗓️ Active Term:** {term_name}")
        with col2:
            st.markdown(f"**⏳ Drop Deadline:** {drop_deadline or 'TBA'}")

    st.write("") # Adds a bit of breathing room

    # ── PROBATION GATE ────────────────────────────────────────────────────────
    if st.session_state.get("student_status") == "PROBATION":
        st.error(
            "🚨 **ACTION REQUIRED: ACADEMIC PROBATION** \n\n"
            "Self-registration is currently disabled. Please contact your faculty advisor "
            "to complete your course registration and discuss your academic plan."
        )
        return

    # ── WINDOW GATE ───────────────────────────────────────────────────────────
    credits = st.session_state.get("credits_completed", 0)
    cgpa    = st.session_state.get("cgpa", 0.0)

    if not is_window_open("STUDENT", semester_id, credits, cgpa):
        st.warning("🔒 **Registration is currently closed for your account.**")
        hint = get_upcoming_window_label("STUDENT", semester_id)
        if hint:
            st.info(f"ℹ️ **Upcoming Window:** {hint}")
        return

    st.success("✅ **Your registration window is open!** Proceed with your course selection below.")
    st.write("") 

    # ── REGISTRATION PANELS ───────────────────────────────────────────────────
    # This will render your updated tabbed design (Regular, Retake, F-Grade) 
    # handled inside components/registration_panel.py
    render_registration_panels(
        student_id=st.session_state.user_id,
        acting_role="SELF",
        actor_id=st.session_state.user_id,
        semester_id=semester_id,
        drop_deadline=drop_deadline,
    )