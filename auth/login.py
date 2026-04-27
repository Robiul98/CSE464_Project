"""
auth/login.py
Login form. Verifies credentials, checks account status, populates session_state.
"""

import bcrypt
import streamlit as st
from db import fetch_one
from utils.semester import load_active_semester


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def _load_student_profile(user_id: str):
    row = fetch_one(
        """
        SELECT s.users_user_id, s.student_name, s.department, s.program,
               s.semester_no, s.cgpa, s.credits_completed,
               s.admission_term, s.faculty_faculty_id, s.student_status,
               s.email
        FROM   students s
        WHERE  s.users_user_id = :p_user_id
        """,
        {"p_user_id": user_id},
    )
    if row:
        st.session_state.student_name       = row["student_name"]
        st.session_state.student_status     = row["student_status"]
        st.session_state.cgpa               = float(row["cgpa"] or 0)
        st.session_state.credits_completed  = int(row["credits_completed"] or 0)
        st.session_state.faculty_faculty_id = row["faculty_faculty_id"]
        st.session_state.department         = row["department"]
        st.session_state.program            = row["program"]
        st.session_state.semester_no        = row["semester_no"]
        st.session_state.admission_term     = row["admission_term"]
        st.session_state.email              = row["email"]
        st.session_state.display_name       = row["student_name"]


def _load_faculty_profile(user_id: str):
    row = fetch_one(
        """
        SELECT faculty_name, department, designation, phone, email
        FROM   faculty
        WHERE  user_id = :p_user_id
        """,
        {"p_user_id": user_id},
    )
    if row:
        st.session_state.faculty_name   = row["faculty_name"]
        st.session_state.department     = row["department"]
        st.session_state.designation    = row["designation"]
        st.session_state.phone          = row["phone"]
        st.session_state.email          = row["email"]
        st.session_state.display_name   = row["faculty_name"]


def render_login():
    """Render the login page. Returns True if login succeeded."""

    st.markdown(
        "<h1 style='text-align:center;margin-top:60px;'>🎓 University Course Advising System</h1>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Sign In")
            user_id  = st.text_input("User ID", placeholder="Enter your User ID")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.button("Login", use_container_width=True, type="primary")

        if login_btn:
            if not user_id or not password:
                st.error("Please enter both User ID and password.")
                return False

            user = fetch_one(
                "SELECT user_id, password_hash, role, account_status FROM users WHERE user_id = :p_user_id",
                {"p_user_id": user_id},
            )

            if not user:
                st.error("Invalid credentials.")
                return False

            if not _verify_password(password, user["password_hash"]):
                st.error("Invalid credentials.")
                return False

            status = user["account_status"]
            if status == "PENDING":
                st.warning("⏳ Your account is awaiting admin approval.")
                return False
            if status == "REJECTED":
                st.error("❌ Your account has been rejected. Contact the administration.")
                return False
            if status == "BLOCKED":
                st.error("🚫 Your account has been blocked. Contact the administration.")
                return False

            # Approved — populate session
            st.session_state.user_id        = user["user_id"]
            st.session_state.role           = user["role"]
            st.session_state.account_status = user["account_status"]
            st.session_state.display_name   = user["user_id"]

            role = user["role"]
            if role == "STUDENT":
                _load_student_profile(user_id)
            elif role == "FACULTY":
                _load_faculty_profile(user_id)
            # ADMIN has no separate profile table

            load_active_semester()

            st.success(f"Welcome, {st.session_state.display_name}!")
            st.rerun()

    return False
