"""
streamlit_app.py
Entry point for the University Course Advising System.
Handles login gate, session management, sidebar navigation, and page routing.
"""

import streamlit as st

st.set_page_config(
    page_title="East West University Course Advising System",
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
    # 1. Centered Sidebar Info using HTML injection
    display_name = st.session_state.get('display_name', st.session_state.user_id)
    sem = st.session_state.get("active_semester")
    sem_text = f"Semester: {sem['term_name']}" if sem else "No active semester"
    
    st.markdown(f"""
    <div style='text-align: center;'>
        <h3 style='margin-bottom: 5px;'>🎓 Advising System</h3>
        <p style='font-weight: bold; margin-bottom: 5px;'>{display_name}</p>
        <p style='color: #888888; font-size: 0.85em; margin-top: 0;'>{sem_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    pages = {} # Default to empty so the Admin sidebar stays clean

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
    
    # Only render sidebar buttons for Students and Faculty
    if pages:
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

    # The Logout button automatically fills the width, keeping it centered!
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Page routing ──────────────────────────────────────────────────────────────

# Safely fetch the current page for Student/Faculty
if role in ["STUDENT", "FACULTY"]:
    page = st.session_state.get("nav_page", list(pages.values())[0])
else:
    page = None # Handled dynamically in the Admin block

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

# ── Admin pages (The New Dashboard!) ──────────────────────────────────────────
elif role == "ADMIN":
    # 1. Main Dashboard Header
    st.markdown("## ⚙️ Administrator Dashboard")
    st.markdown("Manage system operations, requests, and configurations from this central hub.")
    st.write("") # Add a little breathing room
    
    # 2. Map labels to exact page routing names
    admin_pages = {
        "📋 Registration Requests": "Registration Requests",
        "📬 Faculty Messages":      "Faculty Messages",
        "📅 Semesters":             "Semesters",
        "🕐 Advising Windows":      "Advising Windows",
        "👥 User Approvals":        "User Approvals",
        "📖 Course Offerings":      "Course Offerings",
        "🤖 Auto Advise":           "Auto Advise",
        "📜 Provenance Log":        "Provenance Log",
        "🖥️ SQL Terminal":          "SQL Terminal",
    }

    # Synchronize with the existing 'nav_page' session state
    current_admin_page = st.session_state.get("nav_page", list(admin_pages.values())[0])

    # 3. Create a 3x3 Grid of BIG text buttons!
    cols = st.columns(3)
    for i, (label, page_key) in enumerate(admin_pages.items()):
        col = cols[i % 3] # This distributes the buttons evenly across the 3 columns
        
        # Highlight the currently active page in primary (red)
        btn_type = "primary" if current_admin_page == page_key else "secondary"
        
        if col.button(label, key=f"admin_dash_{page_key}", use_container_width=True, type=btn_type):
            st.session_state.nav_page = page_key
            st.rerun()

    st.divider()

    # 4. Route to the correct page based on the button clicked
    page = current_admin_page

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