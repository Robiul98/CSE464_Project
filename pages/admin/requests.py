"""
pages/admin/requests.py
Admin view of registration requests. Approve / Reject / Ignore pending requests.
"""

import pandas as pd
import streamlit as st
from db import fetch_all, execute, fetch_one
from utils.provenance import write_provenance


def _approve_request(req: dict, admin_id: str):
    """Approve a pending ADD or DROP request."""
    req_type   = req["request_type"]
    section_id = req["section_id"]
    student_id = req["students_id"]

    if req_type in ("ADD", "FACULTY-ADVISE", "ADMIN-OVERRIDE", "AUTO-ADVISE"):
        # Check not already enrolled
        existing = fetch_one(
            """
            SELECT enrollment_id FROM enrollments
            WHERE students_id = :sid AND section_id = :sec AND enrollment_status = 'ENROLLED'
            """,
            {"sid": student_id, "sec": section_id},
        )
        if not existing:
            execute(
                """
                INSERT INTO enrollments
                    (students_id, section_id, users_user_id, enrollment_source, enrollment_status)
                VALUES (:sid, :sec, :actor, 'ADMIN', 'ENROLLED')
                """,
                {"sid": student_id, "sec": section_id, "actor": admin_id},
                commit=False,
            )
            execute(
                """
                UPDATE course_sections
                SET    available_seats = available_seats - 1,
                       section_status = CASE WHEN available_seats - 1 <= 0 THEN 'FULL'
                                             ELSE section_status END
                WHERE  section_id = :sec
                """,
                {"sec": section_id},
                commit=False,
            )

    elif req_type == "DROP":
        execute(
            """
            UPDATE enrollments
            SET    enrollment_status = 'DROPPED',
                   dropped_at = SYSTIMESTAMP,
                   drop_reason = 'Admin approved drop',
                   users_user_id1 = :actor
            WHERE  students_id = :sid AND section_id = :sec AND enrollment_status = 'ENROLLED'
            """,
            {"actor": admin_id, "sid": student_id, "sec": section_id},
            commit=False,
        )
        execute(
            """
            UPDATE course_sections
            SET    available_seats = available_seats + 1,
                   section_status = CASE WHEN section_status = 'FULL' THEN 'OPEN'
                                         ELSE section_status END
            WHERE  section_id = :sec
            """,
            {"sec": section_id},
            commit=False,
        )

    execute(
        """
        UPDATE registration_requests
        SET    request_status = 'APPROVED',
               processed_at   = SYSTIMESTAMP,
               processed_note = 'Approved by admin'
        WHERE  request_id = :rid
        """,
        {"rid": req["request_id"]},
        commit=True,
    )

    write_provenance(
        source_table="registration_requests",
        row_pk=str(req["request_id"]),
        operation_type="APPROVE",
        actor_id=admin_id,
        actor_role="ADMIN",
        why="Admin approved registration request",
        where_page="Admin / Registration Requests",
        how="Manual approval",
        old_value={"status": "PENDING"},
        new_value={"status": "APPROVED"},
        request_id=req["request_id"],
    )


def _reject_request(req_id: int, reason: str, admin_id: str):
    execute(
        """
        UPDATE registration_requests
        SET    request_status = 'REJECTED',
               processed_at   = SYSTIMESTAMP,
               processed_note = :note
        WHERE  request_id = :rid
        """,
        {"note": reason, "rid": req_id},
    )
    write_provenance(
        source_table="registration_requests",
        row_pk=str(req_id),
        operation_type="UPDATE",
        actor_id=admin_id,
        actor_role="ADMIN",
        why=f"Rejected: {reason}",
        where_page="Admin / Registration Requests",
        how="Manual rejection",
        old_value={"status": "PENDING"},
        new_value={"status": "REJECTED"},
        request_id=req_id,
    )


def render():
    st.title("📋 Registration Requests")
    admin_id = st.session_state.user_id

    # ── Filters ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        f_status  = col1.selectbox("Status",
                        ["All", "PENDING", "APPROVED", "REJECTED", "FAILED"],
                        key="rr_status")
        f_type    = col2.selectbox("Type",
                        ["All", "ADD", "DROP", "FACULTY-ADVISE", "ADMIN-OVERRIDE", "AUTO-ADVISE"],
                        key="rr_type")
        f_student = col3.text_input("Student ID", key="rr_student")
        d1, d2    = st.columns(2)
        f_date_from = d1.date_input("From date", value=None, key="rr_from")
        f_date_to   = d2.date_input("To date",   value=None, key="rr_to")

    where_clauses = ["1=1"]
    params: dict = {}
    if f_status != "All":
        where_clauses.append("rr.request_status = :status")
        params["status"] = f_status
    if f_type != "All":
        where_clauses.append("rr.request_type = :rtype")
        params["rtype"] = f_type
    if f_student:
        where_clauses.append("rr.students_id = :stu")
        params["stu"] = f_student.strip()
    if f_date_from:
        where_clauses.append("TRUNC(rr.request_time) >= :dfrom")
        params["dfrom"] = f_date_from
    if f_date_to:
        where_clauses.append("TRUNC(rr.request_time) <= :dto")
        params["dto"] = f_date_to

    where_sql = " AND ".join(where_clauses)

    requests = fetch_all(
        f"""
        SELECT rr.request_id, rr.students_id, s.student_name,
               c.course_code, c.course_title, cs.section_name,
               rr.section_id,
               rr.request_type, rr.request_reason, rr.request_status,
               TO_CHAR(rr.request_time, 'YYYY-MM-DD HH24:MI') AS request_time,
               rr.users_id AS submitted_by,
               TO_CHAR(rr.processed_at, 'YYYY-MM-DD HH24:MI') AS processed_at,
               rr.processed_note
        FROM   registration_requests rr
        JOIN   students s      ON rr.students_id  = s.users_user_id
        JOIN   course_sections cs ON rr.section_id = cs.section_id
        JOIN   course_offerings co ON cs.offering_id = co.offering_id
        JOIN   courses c       ON co.course_id     = c.course_id
        WHERE  {where_sql}
        ORDER  BY rr.request_time DESC
        """,
        params,
    )

    if not requests:
        st.info("No requests match the current filters.")
        return

    st.caption(f"Showing **{len(requests)}** request(s)")

    for req in requests:
        rid    = req["request_id"]
        status = req["request_status"]

        status_icon = {
            "PENDING":  "🟡",
            "APPROVED": "🟢",
            "REJECTED": "🔴",
            "FAILED":   "⚫",
        }.get(status, "❓")

        with st.expander(
            f"{status_icon} #{rid} | {req['course_code']} Sec {req['section_name']} "
            f"| {req['student_name']} | {req['request_type']} | {req['request_time']}"
        ):
            col1, col2 = st.columns(2)
            col1.markdown(f"**Student:** {req['student_name']} (`{req['students_id']}`)")
            col1.markdown(f"**Course:** {req['course_code']} — {req['course_title']}")
            col1.markdown(f"**Section:** {req['section_name']}")
            col2.markdown(f"**Type:** {req['request_type']}")
            col2.markdown(f"**Status:** {status}")
            col2.markdown(f"**Submitted by:** {req['submitted_by']}")
            if req["request_reason"]:
                st.markdown(f"**Reason:** {req['request_reason']}")
            if req["processed_at"]:
                st.markdown(f"**Processed at:** {req['processed_at']}")
            if req["processed_note"]:
                st.markdown(f"**Note:** {req['processed_note']}")

            if status == "PENDING":
                ba, br, bi = st.columns([1, 1, 1])

                if ba.button("✅ Approve", key=f"appr_{rid}", type="primary"):
                    st.session_state[f"confirm_approve_{rid}"] = True

                if br.button("❌ Reject", key=f"rej_{rid}"):
                    st.session_state[f"confirm_reject_{rid}"] = True

                if bi.button("⏭ Ignore", key=f"ign_{rid}"):
                    execute(
                        """
                        UPDATE registration_requests
                        SET processed_note = 'IGNORED by admin'
                        WHERE request_id = :rid
                        """,
                        {"rid": rid},
                    )
                    st.toast("Request marked as ignored.", icon="⏭")
                    st.rerun()

                if st.session_state.get(f"confirm_approve_{rid}"):
                    st.warning("Approve this request? This will create/modify an enrollment.")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirm Approve", key=f"cappr_{rid}", type="primary"):
                        _approve_request(req, admin_id)
                        st.session_state.pop(f"confirm_approve_{rid}", None)
                        st.toast(f"Request #{rid} approved.", icon="✅")
                        st.rerun()
                    if c2.button("Cancel", key=f"cancelappr_{rid}"):
                        st.session_state.pop(f"confirm_approve_{rid}", None)
                        st.rerun()

                if st.session_state.get(f"confirm_reject_{rid}"):
                    reason_input = st.text_input("Rejection reason *", key=f"rej_reason_{rid}")
                    c1, c2 = st.columns(2)
                    if c1.button("Confirm Reject", key=f"crej_{rid}", type="primary"):
                        if not reason_input.strip():
                            st.error("Reason is required.")
                        else:
                            _reject_request(rid, reason_input.strip(), admin_id)
                            st.session_state.pop(f"confirm_reject_{rid}", None)
                            st.toast(f"Request #{rid} rejected.", icon="❌")
                            st.rerun()
                    if c2.button("Cancel", key=f"cancelrej_{rid}"):
                        st.session_state.pop(f"confirm_reject_{rid}", None)
                        st.rerun()
