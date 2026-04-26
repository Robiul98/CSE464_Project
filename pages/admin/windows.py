"""
pages/admin/windows.py
CRUD interface for advising_windows.
"""

import datetime
import pandas as pd
import streamlit as st
from db import fetch_all, execute, fetch_one
from utils.provenance import write_provenance


def _combine_dt(date_val, time_val) -> datetime.datetime | None:
    if date_val and time_val:
        return datetime.datetime.combine(date_val, time_val)
    return None


def _window_status(start, end) -> str:
    now = datetime.datetime.now()
    if isinstance(start, str):
        return "—"
    if start and end:
        if now < start:
            return "⏳ Upcoming"
        if start <= now <= end:
            return "🟢 Active NOW"
        return "⚫ Expired"
    return "—"


def render():
    st.title("🕐 Advising Windows")
    admin_id = st.session_state.user_id

    # ── Semester options ──────────────────────────────────────────────────────
    semesters = fetch_all(
        "SELECT semester_id, term_name FROM semesters ORDER BY semester_id DESC"
    )
    sem_map = {s["term_name"]: s["semester_id"] for s in semesters}

    # ── Create / Edit form ────────────────────────────────────────────────────
    editing_id = st.session_state.get("edit_window_id")
    edit_data  = {}
    if editing_id:
        edit_data = fetch_one(
            "SELECT * FROM advising_windows WHERE window_id = :wid", {"wid": editing_id}
        ) or {}

    form_title = f"✏️ Edit Window #{editing_id}" if editing_id else "➕ Create New Window"
    with st.expander(form_title, expanded=bool(editing_id)):
        with st.form("window_form"):
            sem_names = list(sem_map.keys())
            default_sem = 0
            if edit_data.get("semester_id"):
                for i, s in enumerate(semesters):
                    if s["semester_id"] == edit_data["semester_id"]:
                        default_sem = i
                        break

            sem_sel  = st.selectbox("Semester *", sem_names, index=default_sem)
            role_sel = st.radio(
                "Target Role *", ["STUDENT", "FACULTY", "ADMIN"],
                index=["STUDENT", "FACULTY", "ADMIN"].index(edit_data.get("target_role", "STUDENT")),
                horizontal=True,
            )
            label    = st.text_input("Reason Label *",
                                     value=edit_data.get("reason_label", ""),
                                     placeholder="e.g. Regular Registration Window")

            col1, col2 = st.columns(2)
            start_date = col1.date_input("Start Date *",
                                         value=edit_data.get("start_time", datetime.date.today()))
            start_time = col2.time_input("Start Time *",
                                         value=edit_data.get("start_time",
                                                              datetime.time(8, 0))
                                         if isinstance(edit_data.get("start_time"), datetime.time)
                                         else datetime.time(8, 0))
            col3, col4 = st.columns(2)
            end_date   = col3.date_input("End Date *",
                                         value=edit_data.get("end_time", datetime.date.today()))
            end_time   = col4.time_input("End Time *",
                                         value=datetime.time(23, 59))

            show_credit = role_sel == "STUDENT"
            min_cr = max_cr = min_gpa = max_gpa = None
            if show_credit:
                c1, c2, c3, c4 = st.columns(4)
                
                # Safely handle NULL (None) values from the database
                val_min_cr  = edit_data.get("min_credits")
                val_max_cr  = edit_data.get("max_credits")
                val_min_gpa = edit_data.get("min_cgpa")
                val_max_gpa = edit_data.get("max_cgpa")
                
                min_cr  = c1.number_input("Min Credits", min_value=0,   
                                          value=int(val_min_cr) if val_min_cr is not None else 0)
                max_cr  = c2.number_input("Max Credits", min_value=0,   
                                          value=int(val_max_cr) if val_max_cr is not None else 9999)
                min_gpa = c3.number_input("Min CGPA",   min_value=0.0, max_value=4.0,
                                          value=float(val_min_gpa) if val_min_gpa is not None else 0.0, step=0.01)
                max_gpa = c4.number_input("Max CGPA",   min_value=0.0, max_value=4.0,
                                          value=float(val_max_gpa) if val_max_gpa is not None else 4.0, step=0.01)

            submitted = st.form_submit_button(
                "Update Window" if editing_id else "Create Window", type="primary"
            )

        if submitted:
            if not label.strip(): # type: ignore
                st.error("Reason Label is required.")
            else:
                start_dt = _combine_dt(start_date, start_time)
                end_dt   = _combine_dt(end_date,   end_time)
                sem_id   = sem_map[sem_sel]

                if editing_id:
                    execute(
                        """
                        UPDATE advising_windows
                        SET    semester_id   = :sem,
                               target_role  = :role,
                               reason_label = :label,
                               start_time   = :st,
                               end_time     = :et,
                               min_credits  = :minc,
                               max_credits  = :maxc,
                               min_cgpa     = :ming,
                               max_cgpa     = :maxg
                        WHERE  window_id = :wid
                        """,
                        {
                            "sem": sem_id, "role": role_sel, "label": label.strip(), # type: ignore
                            "st": start_dt, "et": end_dt,
                            "minc": min_cr, "maxc": max_cr, "ming": min_gpa, "maxg": max_gpa,
                            "wid": editing_id,
                        },
                    )
                    write_provenance(
                        "advising_windows", str(editing_id), "UPDATE",
                        admin_id, "ADMIN", "Updated advising window",
                        "Admin / Advising Windows", "Form edit",
                    )
                    st.session_state.pop("edit_window_id", None)
                    st.toast("Window updated.", icon="✅")
                else:
                    execute(
                        """
                        INSERT INTO advising_windows
                            (semester_id, target_role, reason_label,
                             start_time, end_time,
                             min_credits, max_credits, min_cgpa, max_cgpa)
                        VALUES
                            (:sem, :role, :label, :st, :et, :minc, :maxc, :ming, :maxg)
                        """,
                        {
                            "sem": sem_id, "role": role_sel, "label": label.strip(), # type: ignore
                            "st": start_dt, "et": end_dt,
                            "minc": min_cr or 0, "maxc": max_cr or 9999,
                            "ming": min_gpa, "maxg": max_gpa,
                        },
                    )
                    write_provenance(
                        "advising_windows", "NEW", "INSERT",
                        admin_id, "ADMIN", "Created advising window",
                        "Admin / Advising Windows", "Form create",
                    )
                    st.toast("Window created.", icon="✅")
                st.rerun()

    # ── Existing Windows ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("Existing Windows")

    windows = fetch_all(
        """
        SELECT aw.window_id, s.term_name, aw.target_role, aw.reason_label,
               aw.start_time, aw.end_time,
               aw.min_credits, aw.max_credits, aw.min_cgpa, aw.max_cgpa
        FROM   advising_windows aw
        JOIN   semesters s ON aw.semester_id = s.semester_id
        ORDER  BY aw.start_time DESC
        """,
    )

    if not windows:
        st.info("No advising windows configured.")
        return

    for w in windows:
        w_status = _window_status(w["start_time"], w["end_time"])
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1.5, 2, 1.5])
            col1.markdown(f"**{w['reason_label']}**  \n{w['term_name']}")
            col2.markdown(f"Role: **{w['target_role']}**  \n{w_status}")
            col3.markdown(
                f"Start: {w['start_time']}  \nEnd: {w['end_time']}"
            )
            if w["target_role"] == "STUDENT":
                col4.markdown(
                    f"Credits: {w['min_credits']}–{w['max_credits']}  \n"
                    f"CGPA: {w['min_cgpa'] or 0}–{w['max_cgpa'] or 4}"
                )

            ba, bd = st.columns([1, 1])
            if ba.button("✏️ Edit", key=f"edit_w_{w['window_id']}"):
                st.session_state["edit_window_id"] = w["window_id"]
                st.rerun()
            if bd.button("🗑️ Delete", key=f"del_w_{w['window_id']}"):
                st.session_state[f"confirm_del_w_{w['window_id']}"] = True

            if st.session_state.get(f"confirm_del_w_{w['window_id']}"):
                st.warning("Delete this window permanently?")
                c1, c2 = st.columns(2)
                if c1.button("Confirm Delete", key=f"cdelw_{w['window_id']}", type="primary"):
                    execute(
                        "DELETE FROM advising_windows WHERE window_id = :wid",
                        {"wid": w["window_id"]},
                    )
                    write_provenance(
                        "advising_windows", str(w["window_id"]), "DELETE",
                        admin_id, "ADMIN", "Deleted advising window",
                        "Admin / Advising Windows", "Delete button",
                    )
                    st.session_state.pop(f"confirm_del_w_{w['window_id']}", None)
                    st.toast("Window deleted.", icon="🗑️")
                    st.rerun()
                if c2.button("Cancel", key=f"canceldelw_{w['window_id']}"):
                    st.session_state.pop(f"confirm_del_w_{w['window_id']}", None)
                    st.rerun()
