"""
pages/admin/semesters.py
Admin management of academic semesters.
"""

import datetime
import pandas as pd
import streamlit as st
from db import fetch_all, execute
from utils.provenance import write_provenance

def _combine_dt(date_val, time_val) -> datetime.datetime | None:
    if date_val and time_val:
        return datetime.datetime.combine(date_val, time_val)
    return None

def render():
    st.title("📅 Semesters Management")
    admin_id = st.session_state.user_id

    # ── Create New Semester Form ──────────────────────────────────────────────
    with st.expander("➕ Create New Semester", expanded=False):
        with st.form("new_semester_form"):
            term_name = st.text_input("Term Name *", placeholder="e.g., Spring 2027")
            
            c1, c2 = st.columns(2)
            start_date = c1.date_input("Start Date *", value=datetime.date.today())
            end_date   = c2.date_input("End Date *", value=datetime.date.today() + datetime.timedelta(days=120))
            
            st.markdown("**Registration Window**")
            r1, r2, r3, r4 = st.columns(4)
            reg_start_d = r1.date_input("Reg Start Date", value=datetime.date.today())
            reg_start_t = r2.time_input("Reg Start Time", value=datetime.time(8, 0))
            reg_end_d   = r3.date_input("Reg End Date", value=datetime.date.today() + datetime.timedelta(days=14))
            reg_end_t   = r4.time_input("Reg End Time", value=datetime.time(23, 59))
            
            st.markdown("**Drop Deadline**")
            d1, d2 = st.columns(2)
            drop_d = d1.date_input("Drop Deadline Date", value=datetime.date.today() + datetime.timedelta(days=30))
            drop_t = d2.time_input("Drop Deadline Time", value=datetime.time(23, 59))
            
            status = st.selectbox("Status", ["PLANNED", "ACTIVE", "CLOSED"])
            
            submitted = st.form_submit_button("Create Semester", type="primary")
            
        if submitted:
            if not term_name.strip():
                st.error("Term Name is required.")
            elif end_date < start_date:
                st.error("End date cannot be before start date.")
            else:
                reg_start_dt = _combine_dt(reg_start_d, reg_start_t)
                reg_end_dt   = _combine_dt(reg_end_d, reg_end_t)
                drop_dt      = _combine_dt(drop_d, drop_t)
                
                execute(
                    """
                    INSERT INTO semesters 
                        (term_name, start_date, end_date, registration_start, registration_end, drop_deadline, status)
                    VALUES 
                        (:term, :sd, :ed, :rs, :re, :dd, :st)
                    """,
                    {
                        "term": term_name.strip(), "sd": start_date, "ed": end_date,
                        "rs": reg_start_dt, "re": reg_end_dt, "dd": drop_dt, "st": status
                    }
                )
                write_provenance(
                    "semesters", "NEW", "INSERT", admin_id, "ADMIN",
                    "Created new semester", "Admin / Semesters", "Form create"
                )
                st.toast(f"Semester '{term_name}' created successfully.", icon="✅")
                st.rerun()
    
    # ── List Existing Semesters ───────────────────────────────────────────────
    st.divider()
    st.subheader("Existing Semesters")
    
    sems = fetch_all(
        """
        SELECT semester_id, term_name, status, 
               TO_CHAR(start_date, 'YYYY-MM-DD') as start_date, 
               TO_CHAR(end_date, 'YYYY-MM-DD') as end_date,
               TO_CHAR(drop_deadline, 'YYYY-MM-DD') as drop_deadline
        FROM semesters 
        ORDER BY semester_id DESC
        """
    )
    
    if not sems:
        st.info("No semesters found.")
        return
        
    df = pd.DataFrame(sems)
    df.columns = ["ID", "Term Name", "Status", "Start Date", "End Date", "Drop Deadline"]
    st.dataframe(df, use_container_width=True, hide_index=True)