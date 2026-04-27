"""
components/registration_panel.py

Reusable registration panel rendered by:
  - pages/student/registration.py  (acting_role='SELF')
  - pages/faculty/advising.py      (acting_role='FACULTY')

Panels:
  - Current Enrollments
  - F Grade Courses
  - Retakable Courses
  - General Registration
  - Section Change for Faculty
"""

import datetime
import pandas as pd
import streamlit as st

from db import fetch_all, fetch_one, execute
from utils.provenance import write_provenance


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _format_schedule(section_id: int) -> str:
    rows = fetch_all(
        """
        SELECT day_of_week,
               TO_CHAR(start_time, 'HH24:MI') AS st,
               TO_CHAR(end_time,   'HH24:MI') AS et,
               class_type
        FROM   section_schedule
        WHERE  section_id = :sid
        ORDER  BY day_of_week
        """,
        {"sid": section_id},
    )

    if not rows:
        return "—"

    parts = [
        f"{r['day_of_week']} {r['st']}-{r['et']} ({r['class_type']})"
        for r in rows
    ]
    return " | ".join(parts)


def _enrolled_sections(student_id: str, semester_id: int) -> set:
    """Return section_ids the student is currently ENROLLED in this semester."""
    rows = fetch_all(
        """
        SELECT e.section_id
        FROM   enrollments e
        JOIN   course_sections cs ON e.section_id = cs.section_id
        JOIN   course_offerings co ON cs.offering_id = co.offering_id
        WHERE  e.students_id       = :sid
          AND  e.enrollment_status = 'ENROLLED'
          AND  co.semesters_id     = :sem
        """,
        {"sid": student_id, "sem": semester_id},
    )
    return {r["section_id"] for r in rows}


def _f_grade_course_ids(student_id: str) -> set:
    rows = fetch_all(
        """
        SELECT course_id
        FROM   takes
        WHERE  user_id = :p_user_id
          AND  grade = 'F'
        """,
        {"p_user_id": student_id},
    )
    return {r["course_id"] for r in rows}


def _passed_course_ids(student_id: str) -> set:
    """Courses taken with a non-F, non-NULL grade."""
    rows = fetch_all(
        """
        SELECT course_id
        FROM   takes
        WHERE  user_id = :p_user_id
          AND  grade IS NOT NULL
          AND  grade != 'F'
        """,
        {"p_user_id": student_id},
    )
    return {r["course_id"] for r in rows}


def _prereqs_met(student_id: str, course_id: int, passed_ids: set) -> bool:
    """Return True if all prerequisites for course_id are in passed_ids."""
    prereqs = fetch_all(
        """
        SELECT courses_course_id1
        FROM   course_prerequisites
        WHERE  courses_course_id = :cid
        """,
        {"cid": course_id},
    )

    if not prereqs:
        return True

    return all(p["courses_course_id1"] in passed_ids for p in prereqs)


def _sections_for_courses(course_ids: set, semester_id: int) -> list[dict]:
    """Return open/full sections for selected courses in the active semester."""
    if not course_ids:
        return []

    id_list = ",".join(str(i) for i in course_ids)

    return fetch_all(
        f"""
        SELECT cs.section_id,
               cs.section_name,
               cs.room_no,
               cs.max_capacity,
               cs.available_seats,
               cs.section_status,
               c.course_id,
               c.course_code,
               c.course_title,
               c.credits,
               f.faculty_name
        FROM   course_offerings co
        JOIN   courses c          ON co.course_id   = c.course_id
        JOIN   course_sections cs ON cs.offering_id = co.offering_id
        LEFT   JOIN faculty f     ON cs.faculty_id  = f.user_id
        WHERE  co.semesters_id    = :sem
          AND  co.offering_status = 'OPEN'
          AND  cs.section_status IN ('OPEN', 'FULL')
          AND  c.course_id IN ({id_list})
        ORDER  BY c.course_code, cs.section_name
        """,
        {"sem": semester_id},
    )


def _all_offered_sections(semester_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT cs.section_id,
               cs.section_name,
               cs.room_no,
               cs.max_capacity,
               cs.available_seats,
               cs.section_status,
               c.course_id,
               c.course_code,
               c.course_title,
               c.credits,
               f.faculty_name
        FROM   course_offerings co
        JOIN   courses c          ON co.course_id   = c.course_id
        JOIN   course_sections cs ON cs.offering_id = co.offering_id
        LEFT   JOIN faculty f     ON cs.faculty_id  = f.user_id
        WHERE  co.semesters_id    = :sem
          AND  co.offering_status = 'OPEN'
          AND  cs.section_status IN ('OPEN', 'FULL')
        ORDER  BY c.course_code, cs.section_name
        """,
        {"sem": semester_id},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Validation helpers
# ─────────────────────────────────────────────────────────────────────────────

def _already_enrolled_same_section(student_id: str, section_id: int):
    return fetch_one(
        """
        SELECT enrollment_id
        FROM   enrollments
        WHERE  students_id = :sid
          AND  section_id = :sec
          AND  enrollment_status = 'ENROLLED'
        """,
        {"sid": student_id, "sec": section_id},
    )


def _already_enrolled_same_course(student_id: str, new_section_id: int):
    """
    Prevent student from taking same course in more than one section
    in the same semester.
    """
    return fetch_one(
        """
        SELECT e.enrollment_id
        FROM   enrollments e
        JOIN   course_sections old_cs
               ON e.section_id = old_cs.section_id
        JOIN   course_offerings old_co
               ON old_cs.offering_id = old_co.offering_id

        JOIN   course_sections new_cs
               ON new_cs.section_id = :new_sec
        JOIN   course_offerings new_co
               ON new_cs.offering_id = new_co.offering_id

        WHERE  e.students_id = :sid
          AND  e.enrollment_status = 'ENROLLED'
          AND  old_co.course_id = new_co.course_id
          AND  old_co.semesters_id = new_co.semesters_id
        """,
        {"sid": student_id, "new_sec": new_section_id},
    )


def _has_schedule_conflict(student_id: str, new_section_id: int):
    """
    Prevent student from taking two courses with overlapping schedules
    in the same semester.
    """
    return fetch_one(
        """
        SELECT 1
        FROM   section_schedule new_s
        JOIN   course_sections new_cs
               ON new_s.section_id = new_cs.section_id
        JOIN   course_offerings new_co
               ON new_cs.offering_id = new_co.offering_id

        WHERE  new_s.section_id = :new_sec
          AND  EXISTS (
                SELECT 1
                FROM   enrollments e
                JOIN   course_sections old_cs
                       ON e.section_id = old_cs.section_id
                JOIN   course_offerings old_co
                       ON old_cs.offering_id = old_co.offering_id
                JOIN   section_schedule old_s
                       ON old_s.section_id = e.section_id

                WHERE  e.students_id = :sid
                  AND  e.enrollment_status = 'ENROLLED'
                  AND  old_co.semesters_id = new_co.semesters_id
                  AND  old_s.day_of_week = new_s.day_of_week
                  AND  new_s.start_time < old_s.end_time
                  AND  new_s.end_time > old_s.start_time
          )
        """,
        {"sid": student_id, "new_sec": new_section_id},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Enroll / Drop actions
# ─────────────────────────────────────────────────────────────────────────────

def _do_enroll(student_id: str, section_id: int, actor_id: str,
               acting_role: str, course_code: str, section_name: str) -> bool:
    """
    Insert/update registration request + enrollment,
    decrement seats, log provenance.

    Returns True if enrollment succeeds.
    Returns False if enrollment is blocked.
    """

    # 1. Prevent same exact section enrollment
    existing = _already_enrolled_same_section(student_id, section_id)
    if existing:
        st.error("⚠️ You are already enrolled in this section.")
        return False

    # 2. Prevent same course in different section
    same_course = _already_enrolled_same_course(student_id, section_id)
    if same_course:
        st.error("⚠️ You are already enrolled in another section of this same course.")
        return False

    # 3. Prevent schedule conflict
    schedule_conflict = _has_schedule_conflict(student_id, section_id)
    if schedule_conflict:
        st.error("⚠️ Schedule conflict: this section overlaps with one of your enrolled courses.")
        return False

    # 4. Prevent enrolling if section is full
    sec_row = fetch_one(
        """
        SELECT available_seats, section_status
        FROM   course_sections
        WHERE  section_id = :sec
        """,
        {"sec": section_id},
    )

    if not sec_row:
        st.error("⚠️ Section not found.")
        return False

    if sec_row["available_seats"] <= 0 or sec_row["section_status"] == "FULL":
        st.error("⚠️ This section is already full.")
        return False

    req_type = "ADD"
    note = "Auto-approved via portal" if acting_role == "SELF" else "Faculty Advise"
    source = "SELF" if acting_role == "SELF" else "FACULTY"

    try:
        # Handle existing registration request by update pattern
        req_exists = fetch_one(
            """
            SELECT request_id
            FROM   registration_requests
            WHERE  students_id = :sid
              AND  section_id = :sec
            """,
            {"sid": student_id, "sec": section_id},
        )

        if req_exists:
            execute(
                """
                UPDATE registration_requests
                SET    request_type = :rtype,
                       request_reason = :reason,
                       request_status = 'APPROVED',
                       processed_at = SYSTIMESTAMP,
                       processed_note = :note,
                       users_id = :actor
                WHERE  students_id = :sid
                  AND  section_id = :sec
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "rtype": req_type,
                    "reason": f"Registration: {course_code} {section_name}",
                    "note": note,
                },
                commit=False,
            )
        else:
            execute(
                """
                INSERT INTO registration_requests
                    (students_id, section_id, users_id, request_type, request_reason,
                     request_status, processed_at, processed_note)
                VALUES
                    (:sid, :sec, :actor, :rtype, :reason,
                     'APPROVED', SYSTIMESTAMP, :note)
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "rtype": req_type,
                    "reason": f"Registration: {course_code} {section_name}",
                    "note": note,
                },
                commit=False,
            )

        req_row = fetch_one(
            """
            SELECT MAX(request_id) AS rid
            FROM   registration_requests
            WHERE  students_id = :sid
              AND  section_id = :sec
            """,
            {"sid": student_id, "sec": section_id},
        )
        req_id = req_row["rid"] if req_row else None

        # Insert/reactivate enrollment
        enrollment_exists = fetch_one(
            """
            SELECT enrollment_id
            FROM   enrollments
            WHERE  students_id = :sid
              AND  section_id = :sec
            """,
            {"sid": student_id, "sec": section_id},
        )

        if enrollment_exists:
            execute(
                """
                UPDATE enrollments
                SET    enrollment_status = 'ENROLLED',
                       enrolled_at = SYSTIMESTAMP,
                       dropped_at = NULL,
                       drop_reason = NULL,
                       enrollment_source = :source,
                       users_user_id = :actor
                WHERE  students_id = :sid
                  AND  section_id = :sec
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "source": source,
                },
                commit=False,
            )
        else:
            execute(
                """
                INSERT INTO enrollments
                    (students_id, section_id, users_user_id,
                     enrollment_source, enrollment_status)
                VALUES
                    (:sid, :sec, :actor, :source, 'ENROLLED')
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "source": source,
                },
                commit=False,
            )

        # Decrement available seats
        execute(
            """
            UPDATE course_sections
            SET    available_seats = available_seats - 1,
                   section_status = CASE
                       WHEN available_seats - 1 <= 0 THEN 'FULL'
                       ELSE section_status
                   END
            WHERE  section_id = :sec
            """,
            {"sec": section_id},
            commit=False,
        )

        # Seat history
        execute(
            """
            INSERT INTO section_seat_history
                (sections_id, old_available_seats, new_available_seats,
                 users_user_id, change_reason, request_id)
            SELECT section_id,
                   available_seats + 1,
                   available_seats,
                   :actor,
                   'Enrollment',
                   :rid
            FROM   course_sections
            WHERE  section_id = :sec
            """,
            {"actor": actor_id, "rid": req_id, "sec": section_id},
            commit=True,
        )

        write_provenance(
            source_table="enrollments",
            row_pk=f"student={student_id},section={section_id}",
            operation_type="ADD",
            actor_id=actor_id,
            actor_role=acting_role,
            why=f"Enrolled in {course_code} section {section_name}",
            where_page="Registration Portal",
            how=f"{source} registration",
            new_value={"student_id": student_id, "section_id": section_id},
            request_id=req_id,
        )

        return True

    except Exception as e:
        error_msg = str(e)

        if "ORA-20005" in error_msg:
            st.error("⚠️ Schedule conflict: this section overlaps with one of your enrolled courses.")
        elif "ORA-20004" in error_msg:
            st.error("⚠️ You are already enrolled in another section of this same course.")
        elif "ORA-20002" in error_msg:
            st.error("⚠️ You are already enrolled in this section.")
        elif "ORA-20001" in error_msg:
            st.error("⚠️ No available seats in this section.")
        else:
            st.error(f"Enrollment failed: {e}")

        return False


def _do_drop(student_id: str, section_id: int, actor_id: str,
             acting_role: str, course_code: str, section_name: str,
             drop_reason: str = "") -> bool:
    """
    Drop an enrollment, increment seats, log provenance.

    Returns True if drop succeeds.
    Returns False if drop is blocked.
    """

    existing = fetch_one(
        """
        SELECT enrollment_id
        FROM   enrollments
        WHERE  students_id = :sid
          AND  section_id = :sec
          AND  enrollment_status = 'ENROLLED'
        """,
        {"sid": student_id, "sec": section_id},
    )

    if not existing:
        st.error("⚠️ Student is not currently enrolled in this section.")
        return False

    source_drop = "SELF" if acting_role == "SELF" else "FACULTY"

    try:
        req_exists = fetch_one(
            """
            SELECT request_id
            FROM   registration_requests
            WHERE  students_id = :sid
              AND  section_id = :sec
            """,
            {"sid": student_id, "sec": section_id},
        )

        if req_exists:
            execute(
                """
                UPDATE registration_requests
                SET    request_type = 'DROP',
                       request_reason = :reason,
                       request_status = 'APPROVED',
                       processed_at = SYSTIMESTAMP,
                       processed_note = 'Drop approved via portal',
                       users_id = :actor
                WHERE  students_id = :sid
                  AND  section_id = :sec
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "reason": drop_reason or "Student drop",
                },
                commit=False,
            )
        else:
            execute(
                """
                INSERT INTO registration_requests
                    (students_id, section_id, users_id, request_type,
                     request_reason, request_status, processed_at,
                     processed_note)
                VALUES
                    (:sid, :sec, :actor, 'DROP',
                     :reason, 'APPROVED', SYSTIMESTAMP,
                     'Drop approved via portal')
                """,
                {
                    "sid": student_id,
                    "sec": section_id,
                    "actor": actor_id,
                    "reason": drop_reason or "Student drop",
                },
                commit=False,
            )

        req_row = fetch_one(
            """
            SELECT MAX(request_id) AS rid
            FROM   registration_requests
            WHERE  students_id = :sid
              AND  section_id = :sec
            """,
            {"sid": student_id, "sec": section_id},
        )
        req_id = req_row["rid"] if req_row else None

        # Mark enrollment as dropped
        execute(
            """
            UPDATE enrollments
            SET    enrollment_status = 'DROPPED',
                   dropped_at = SYSTIMESTAMP,
                   drop_reason = :reason,
                   users_user_id1 = :actor
            WHERE  students_id = :sid
              AND  section_id = :sec
              AND  enrollment_status = 'ENROLLED'
            """,
            {
                "reason": drop_reason or "Student drop",
                "actor": actor_id,
                "sid": student_id,
                "sec": section_id,
            },
            commit=False,
        )

        # Increment available seats
        execute(
            """
            UPDATE course_sections
            SET    available_seats = available_seats + 1,
                   section_status = CASE
                       WHEN section_status = 'FULL' THEN 'OPEN'
                       ELSE section_status
                   END
            WHERE  section_id = :sec
            """,
            {"sec": section_id},
            commit=False,
        )

        # Seat history
        execute(
            """
            INSERT INTO section_seat_history
                (sections_id, old_available_seats, new_available_seats,
                 users_user_id, change_reason, request_id)
            SELECT section_id,
                   available_seats - 1,
                   available_seats,
                   :actor,
                   'Drop',
                   :rid
            FROM   course_sections
            WHERE  section_id = :sec
            """,
            {"actor": actor_id, "rid": req_id, "sec": section_id},
            commit=True,
        )

        write_provenance(
            source_table="enrollments",
            row_pk=f"student={student_id},section={section_id}",
            operation_type="DROP",
            actor_id=actor_id,
            actor_role=acting_role,
            why=drop_reason or "Dropped by user",
            where_page="Registration Portal",
            how=f"{source_drop} drop",
            old_value={"student_id": student_id, "section_id": section_id},
            request_id=req_id,
        )

        return True

    except Exception as e:
        st.error(f"Drop failed: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Panel renderer
# ─────────────────────────────────────────────────────────────────────────────

def _render_section_row(row: dict, enrolled_sections: set, student_id: str,
                        actor_id: str, acting_role: str, drop_deadline,
                        panel_key: str):
    """Render a single section as a row in an st.container."""

    section_id = row["section_id"]
    course_code = row["course_code"]
    section_name = row["section_name"]
    avail = row["available_seats"]
    status = row["section_status"]
    is_enrolled = section_id in enrolled_sections

    schedule_str = _format_schedule(section_id)

    cols = st.columns([1.2, 2.5, 0.6, 0.8, 1.8, 2.5, 0.8, 0.8, 1.2])

    cols[0].write(f"**{course_code}**")
    cols[1].write(row["course_title"])
    cols[2].write(str(row["credits"]))
    cols[3].write(section_name)
    cols[4].write(row["faculty_name"] or "—")
    cols[5].write(schedule_str)
    cols[6].write(row["room_no"] or "—")

    if status == "FULL":
        cols[7].markdown(":orange[FULL]")
    else:
        cols[7].write(str(avail))

    btn_key = f"{panel_key}_{section_id}"

    if is_enrolled:
        can_drop = True

        if acting_role != "FACULTY":
            if drop_deadline:
                now = datetime.datetime.now()
                dl = (
                    drop_deadline
                    if isinstance(drop_deadline, datetime.datetime)
                    else datetime.datetime.combine(drop_deadline, datetime.time.max)
                )

                if now > dl:
                    can_drop = False

        if can_drop:
            if cols[8].button("Drop", key=f"drop_{btn_key}", type="secondary"):
                st.session_state[f"confirm_drop_{btn_key}"] = True

            if st.session_state.get(f"confirm_drop_{btn_key}"):
                with st.container(border=True):
                    st.warning(f"Drop **{course_code} - {section_name}**?")
                    reason = st.text_input("Reason (optional)", key=f"drop_reason_{btn_key}")

                    c1, c2 = st.columns(2)

                    if c1.button("Confirm Drop", key=f"dropok_{btn_key}", type="primary"):
                        success = _do_drop(
                            student_id,
                            section_id,
                            actor_id,
                            acting_role,
                            course_code,
                            section_name,
                            reason,
                        )

                        if success:
                            st.session_state.pop(f"confirm_drop_{btn_key}", None)
                            st.toast(f"Dropped {course_code} - {section_name}", icon="🗑️")
                            st.rerun()

                    if c2.button("Cancel", key=f"dropcancel_{btn_key}"):
                        st.session_state.pop(f"confirm_drop_{btn_key}", None)
                        st.rerun()
        else:
            cols[8].markdown(":red[Drop Closed]")

    else:
        disabled = status == "FULL" or avail == 0
        label = "Full" if disabled else "Add"

        if cols[8].button(label, key=f"add_{btn_key}", disabled=disabled, type="primary"):
            st.session_state[f"confirm_add_{btn_key}"] = True

        if st.session_state.get(f"confirm_add_{btn_key}"):
            with st.container(border=True):
                st.info(f"Enroll in **{course_code} - {section_name}**?")

                c1, c2 = st.columns(2)

                if c1.button("Confirm", key=f"addok_{btn_key}", type="primary"):
                    success = _do_enroll(
                        student_id,
                        section_id,
                        actor_id,
                        acting_role,
                        course_code,
                        section_name,
                    )

                    if success:
                        st.session_state.pop(f"confirm_add_{btn_key}", None)
                        st.toast(f"Enrolled in {course_code} - {section_name}", icon="✅")
                        st.rerun()

                if c2.button("Cancel", key=f"addcancel_{btn_key}"):
                    st.session_state.pop(f"confirm_add_{btn_key}", None)
                    st.rerun()

    st.divider()


def _panel_header():
    cols = st.columns([1.2, 2.5, 0.6, 0.8, 1.8, 2.5, 0.8, 0.8, 1.2])
    headers = ["Code", "Title", "Cr", "Sec", "Faculty", "Schedule", "Room", "Seats", "Action"]

    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")

    st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_registration_panels(
    student_id: str,
    acting_role: str,
    actor_id: str,
    semester_id: int,
    drop_deadline=None,
):
    """
    Render registration panels for a student.
    """

    enrolled = _enrolled_sections(student_id, semester_id)
    f_ids = _f_grade_course_ids(student_id)
    p_ids = _passed_course_ids(student_id)

    # Current enrollments
    with st.expander("✅ Current Enrollments", expanded=True):
        st.caption("Courses you are currently enrolled in this semester. You can drop them here.")

        if not enrolled:
            st.info("You are not enrolled in any courses this semester.")
        else:
            enrolled_rows = fetch_all(
                """
                SELECT cs.section_id,
                       cs.section_name,
                       cs.room_no,
                       cs.max_capacity,
                       cs.available_seats,
                       cs.section_status,
                       c.course_id,
                       c.course_code,
                       c.course_title,
                       c.credits,
                       f.faculty_name
                FROM   enrollments e
                JOIN   course_sections cs ON e.section_id = cs.section_id
                JOIN   course_offerings co ON cs.offering_id = co.offering_id
                JOIN   courses c ON co.course_id = c.course_id
                LEFT   JOIN faculty f ON cs.faculty_id = f.user_id
                WHERE  e.students_id = :sid
                  AND  e.enrollment_status = 'ENROLLED'
                  AND  co.semesters_id = :sem
                ORDER  BY c.course_code, cs.section_name
                """,
                {"sid": student_id, "sem": semester_id},
            )

            if enrolled_rows:
                _panel_header()
                for row in enrolled_rows:
                    _render_section_row(
                        row,
                        enrolled,
                        student_id,
                        actor_id,
                        acting_role,
                        drop_deadline,
                        "panelE",
                    )

    # Panel A: F Grade Courses
    with st.expander("🔴 Panel A — F Grade Courses", expanded=False):
        st.caption("Courses you have previously failed that are offered this semester.")

        if not f_ids:
            st.info("No F grade courses found.")
        else:
            rows = _sections_for_courses(f_ids, semester_id)
            rows = [r for r in rows if r["section_id"] not in enrolled]

            if not rows:
                st.info("Your F grade courses are not offered or you are already enrolled.")
            else:
                _panel_header()
                for row in rows:
                    _render_section_row(
                        row,
                        enrolled,
                        student_id,
                        actor_id,
                        acting_role,
                        drop_deadline,
                        "panelA",
                    )

    # Panel B: Retakable Courses
    with st.expander("🔁 Panel B — Retakable Courses", expanded=False):
        st.caption("Courses you have already passed that you wish to retake.")

        if not p_ids:
            st.info("No retakable courses found.")
        else:
            retake_rows = _sections_for_courses(p_ids, semester_id)
            retake_rows = [r for r in retake_rows if r["section_id"] not in enrolled]

            if not retake_rows:
                st.info("Your previously passed courses are not available or you are already enrolled.")
            else:
                _panel_header()
                for row in retake_rows:
                    _render_section_row(
                        row,
                        enrolled,
                        student_id,
                        actor_id,
                        acting_role,
                        drop_deadline,
                        "panelB",
                    )

    # Panel C: General Registration
    with st.expander("📋 Panel C — General Registration", expanded=False):
        st.caption("All eligible courses excluding F-grade, retakable, and unmet prerequisites.")

        all_rows = _all_offered_sections(semester_id)
        general_rows = []

        for row in all_rows:
            cid = row["course_id"]

            if row["section_id"] in enrolled:
                continue

            if cid in f_ids:
                continue

            if cid in p_ids:
                continue

            if not _prereqs_met(student_id, cid, p_ids):
                continue

            general_rows.append(row)

        if not general_rows:
            st.info("No eligible courses available for general registration.")
        else:
            _panel_header()
            for row in general_rows:
                _render_section_row(
                    row,
                    enrolled,
                    student_id,
                    actor_id,
                    acting_role,
                    drop_deadline,
                    "panelC",
                )

    # Faculty-only section change
    if acting_role == "FACULTY":
        with st.expander("🔄 Section Change", expanded=False):
            _render_section_change(student_id, actor_id, semester_id, enrolled)


def _render_section_change(student_id: str, actor_id: str,
                           semester_id: int, enrolled_sections: set):
    """Faculty-only: move student from one section to another section of the same course."""

    st.caption("Move student from one section to another section of the same course.")

    if not enrolled_sections:
        st.info("Student has no current enrollments to change.")
        return

    enrolled_rows = fetch_all(
        """
        SELECT e.section_id,
               c.course_id,
               c.course_code,
               c.course_title,
               cs.section_name AS current_section
        FROM   enrollments e
        JOIN   course_sections cs ON e.section_id = cs.section_id
        JOIN   course_offerings co ON cs.offering_id = co.offering_id
        JOIN   courses c ON co.course_id = c.course_id
        WHERE  e.students_id = :sid
          AND  e.enrollment_status = 'ENROLLED'
          AND  co.semesters_id = :sem
        ORDER  BY c.course_code, cs.section_name
        """,
        {"sid": student_id, "sem": semester_id},
    )

    if not enrolled_rows:
        st.info("No current enrollments found.")
        return

    course_options = {
        f"{r['course_code']} — {r['course_title']} (Sec: {r['current_section']})": r
        for r in enrolled_rows
    }

    selected_label = st.selectbox(
        "Select current enrollment",
        list(course_options.keys()),
        key="sc_course_select",
    )
    selected = course_options[selected_label]

    other_sections = fetch_all(
        """
        SELECT cs.section_id,
               cs.section_name,
               cs.available_seats,
               cs.section_status,
               f.faculty_name,
               cs.room_no
        FROM   course_sections cs
        JOIN   course_offerings co ON cs.offering_id = co.offering_id
        LEFT   JOIN faculty f ON cs.faculty_id = f.user_id
        WHERE  co.course_id = :cid
          AND  co.semesters_id = :sem
          AND  cs.section_id != :cur_sec
          AND  cs.section_status IN ('OPEN', 'FULL')
        ORDER  BY cs.section_name
        """,
        {
            "cid": selected["course_id"],
            "sem": semester_id,
            "cur_sec": selected["section_id"],
        },
    )

    if not other_sections:
        st.warning("No other open sections available for this course.")
        return

    sec_options = {
        f"Section {r['section_name']} — {r['faculty_name'] or 'N/A'} — Seats: {r['available_seats']}": r
        for r in other_sections
    }

    new_sec_label = st.selectbox(
        "Move to section",
        list(sec_options.keys()),
        key="sc_new_sec",
    )
    new_sec = sec_options[new_sec_label]

    if new_sec["section_status"] == "FULL" or new_sec["available_seats"] <= 0:
        st.error("Selected section is full.")
        return

    if st.button("Confirm Section Change", type="primary", key="sc_confirm"):
        dropped = _do_drop(
            student_id,
            selected["section_id"],
            actor_id,
            "FACULTY",
            selected["course_code"],
            selected["current_section"],
            "Section change",
        )

        if not dropped:
            st.error("Section change failed during drop.")
            return

        enrolled = _do_enroll(
            student_id,
            new_sec["section_id"],
            actor_id,
            "FACULTY",
            selected["course_code"],
            new_sec["section_name"],
        )

        if not enrolled:
            st.error("Old section was dropped, but new section could not be added. Please add manually.")
            return

        st.toast(f"Section changed to {new_sec['section_name']}", icon="✅")
        st.rerun()