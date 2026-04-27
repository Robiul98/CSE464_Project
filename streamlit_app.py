"""
streamlit_app.py
Entry point for the University Course Advising System.
Handles login gate, session management, sidebar navigation, and page routing.
"""

import streamlit as st

st.set_page_config(
    page_title="University Course Advising System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session guard helper ──────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return (
        "user_id" in st.session_state
        and "role" in st.session_state
        and st.session_state.get("account_status") == "APPROVED"
    )


def role_guard(expected_role: str):
    if st.session_state.get("role") != expected_role:
        st.error("⛔ Unauthorized access.")
        st.stop()


# ── Login flow ────────────────────────────────────────────────────────────────

if not is_logged_in():
    from auth.login import render_login
    render_login()
    st.stop()

# ── Sidebar navigation ────────────────────────────────────────────────────────

role = st.session_state.role

with st.sidebar:
    st.markdown(f"### 🎓 University Course Advising System")
    st.markdown(f"**{st.session_state.get('display_name', st.session_state.user_id)}**")
    sem = st.session_state.get("active_semester")
    if sem:
        st.caption(f"Semester: {sem['term_name']}")
    else:
        st.caption("No active semester")
    st.divider()

    if role == "STUDENT":
        pages = {
            "👤 My Profile":          "My Profile",
            "📝 Registration Portal": "Registration Portal",
            "📚 All Courses":         "All Courses",
        }
    elif role == "FACULTY":
        pages = {
            "👤 My Profile":    "My Profile",
            "📖 My Courses":    "My Courses",
            "👥 My Advisees":   "My Advisees",
            "✏️ Advising":       "Advising",
            "📚 All Courses":   "All Courses",
            "📨 Messages":      "Messages",
        }
    else:  # ADMIN
        pages = {
            "📋 Registration Requests": "Registration Requests",
            "📬 Faculty Messages":      "Faculty Messages",
            "📅 Semesters":             "Semesters",
            "🕐 Advising Windows":      "Advising Windows",
            "👥 User Approvals":        "User Approvals",
            "📖 Course Offerings":      "Course Offerings",
            "🤖 Auto Advise":           "Auto Advise",
            "📜 Provenance Log":        "Provenance Log",
            "🖥️ SQL Terminal":           "SQL Terminal",
        }

    # Determine current page
    # Allow programmatic navigation (e.g. from advisee list buttons)
    if "nav_page" in st.session_state:
        current_page = st.session_state.nav_page
    else:
        current_page = list(pages.values())[0]

    for label, page_key in pages.items():
        btn_type = "primary" if current_page == page_key else "secondary"
        if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
            st.session_state.nav_page = page_key
            # Clear student selection when navigating away from student-specific pages
            if page_key not in ("Advising", "Student View") and role == "FACULTY":
                pass  # Keep viewed_student_id so Advising pre-fills
            current_page = page_key
            st.rerun()

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Page routing ──────────────────────────────────────────────────────────────

page = st.session_state.get("nav_page", list(pages.values())[0])

# ── Student pages ─────────────────────────────────────────────────────────────
if role == "STUDENT":
    if page == "My Profile":
        from pages.student.profile import render; render()

    elif page == "Registration Portal":
        from pages.student.registration import render; render()

    elif page == "All Courses":
        from pages.student.all_courses import render; render()

    else:
        from pages.student.profile import render; render()

# ── Faculty pages ─────────────────────────────────────────────────────────────
elif role == "FACULTY":
    if page == "My Profile":
        from pages.faculty.profile import render; render()

    elif page == "My Courses":
        from pages.faculty.my_courses import render; render()

    elif page == "My Advisees":
        from pages.faculty.advisee_list import render; render()

    elif page == "Student View":
        from pages.faculty.student_view import render; render()

    elif page == "Advising":
        from pages.faculty.advising import render; render()

    elif page == "All Courses":
        from pages.faculty.all_courses import render; render()

    elif page == "Messages":
        from pages.faculty.messages import render; render()

    else:
        from pages.faculty.profile import render; render()

# ── Admin pages ───────────────────────────────────────────────────────────────
elif role == "ADMIN":
    if page == "Registration Requests":
        from pages.admin.requests import render; render()

    elif page == "Faculty Messages":
        from pages.admin.messages import render; render()
    
    elif page == "Semesters":                          
        from pages.admin.semesters import render; render()

    elif page == "Advising Windows":
        from pages.admin.windows import render; render()

    elif page == "User Approvals":
        from pages.admin.approvals import render; render()

    elif page == "Course Offerings":
        from pages.admin.offerings import render; render()

    elif page == "Auto Advise":
        from pages.admin.auto_advise import render; render()

    elif page == "Provenance Log":
        from pages.admin.logs import render; render()

    elif page == "SQL Terminal":
        from pages.admin.terminal import render; render()

    else:
        from pages.admin.requests import render; render()
