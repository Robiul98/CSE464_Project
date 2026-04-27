"""
pages/student/profile.py
Student's own read-only profile view.
"""

import streamlit as st
from db import fetch_one

def render():
    # 1. Welcoming Header
    st.markdown("## 🎓 My Academic Profile")
    st.markdown("View your current academic standing, program details, and progress.")
    st.divider()

    uid = st.session_state.user_id
    
    # 2. Database Fetch (Logic untouched)
    row = fetch_one(
        """
        SELECT s.users_user_id, s.student_name, s.email, s.department,
               s.program, s.semester_no, s.cgpa, s.credits_completed,
               s.admission_term, s.student_status,
               f.faculty_name AS advisor_name
        FROM   students s
        LEFT   JOIN faculty f ON s.faculty_faculty_id = f.user_id
        WHERE  s.users_user_id = :p_student_id
        """,
        {"p_student_id": uid},
    )

    if not row:
        st.warning("⚠️ **Profile not found.** Please contact the administration office.")
        return

    status = row["student_status"]

    # 3. High-Priority Alert (Enhanced visual weight)
    if status == "PROBATION":
        st.error(
            "🚨 **ACTION REQUIRED: ACADEMIC PROBATION** \n\n"
            "Self-registration is currently disabled. Please schedule a meeting with your academic advisor immediately to discuss your next steps."
        )

    # 4. Key Academic Metrics (Eye-catching top row)
    st.subheader("📊 My Status")
    
    # Using metrics makes the important numbers pop out to the student
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="CGPA", value=f"{float(row['cgpa']):.2f}")
    m2.metric(label="Credits Completed", value=str(row['credits_completed']))
    m3.metric(label="Semester", value=str(row['semester_no'] or '—'))
    
    status_colors = {
        "ACTIVE": "🟢 Active",
        "PROBATION": "🔴 Probation",
        "INACTIVE": "⚫ Inactive",
        "GRADUATED": "🎓 Graduated",
    }
    m4.metric(label="Standing", value=status_colors.get(status, status))

    st.write("") # Add a little breathing room

    # 5. Detailed Information Container
    st.subheader("📋 Profile Details")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Personal Information")
            st.markdown(f"**Name:** {row['student_name']}")
            st.markdown(f"**Student ID:** {row['users_user_id']}")
            st.markdown(f"**Email:** {row['email'] or '—'}")
            
        with col2:
            st.markdown("#### 🏛️ Program Details")
            st.markdown(f"**Department:** {row['department'] or '—'}")
            st.markdown(f"**Program:** {row['program'] or '—'}")
            st.markdown(f"**Admission Term:** {row['admission_term'] or '—'}")
            st.markdown(f"**Academic Advisor:** {row['advisor_name'] or '—'}")