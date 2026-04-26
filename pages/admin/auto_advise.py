"""
pages/admin/auto_advise.py
Bulk auto-enrollment for newly admitted students (0 credits, no current enrollments).
"""

import streamlit as st
from db import fetch_all, execute, fetch_one
from utils.provenance import write_provenance


def _auto_enroll_student(student_id: str, semester_id: int,
                          credit_limit: int, level_no: int,
                          dept: str, admin_id: str,
                          dry_run: bool) -> dict:
    """
    Enroll a student in level_no courses up to credit_limit.
    Returns dict with enrolled courses and total credits.
    """
    # Get eligible courses for this student's department at the given level
    courses = fetch_all(
        """
        SELECT co.offering_id, c.course_id, c.course_code, c.course_title, c.credits
        FROM   course_offerings co
        JOIN   courses c ON co.course_id = c.course_id
        WHERE  co.semesters_id    = :sem
          AND  co.offering_status = 'OPEN'
          AND  c.level_no         = :lvl
          AND  c.department       = :dept
        ORDER  BY c.course_code
        """,
        {"sem": semester_id, "lvl": level_no, "dept": dept},
    )

    total_credits = 0
    enrolled      = []
    failed        = []

    for course in courses:
        if total_credits + course["credits"] > credit_limit:
            continue

        # Find section with most available seats
        section = fetch_one(
            """
            SELECT section_id, available_seats, section_name
            FROM   course_sections
            WHERE  offering_id     = :oid
              AND  section_status  = 'OPEN'
              AND  available_seats > 0
            ORDER  BY available_seats DESC
            FETCH FIRST 1 ROW ONLY
            """,
            {"oid": course["offering_id"]},
        )

        if not section:
            failed.append(f"{course['course_code']} (no open seats)")
            continue

        if not dry_run:
            try:
                # Insert request
                execute(
                    """
                    INSERT INTO registration_requests
                        (students_id, section_id, users_id, request_type,
                         request_reason, request_status, processed_at)
                    VALUES
                        (:sid, :sec, :actor, 'AUTO-ADVISE',
                         'Auto-advise for new student', 'APPROVED', SYSTIMESTAMP)
                    """,
                    {"sid": student_id, "sec": section["section_id"], "actor": admin_id},
                    commit=False,
                )

                req_row = fetch_one(
                    """
                    SELECT MAX(request_id) AS rid FROM registration_requests
                    WHERE students_id = :sid AND section_id = :sec
                    """,
                    {"sid": student_id, "sec": section["section_id"]},
                )
                req_id = req_row["rid"] if req_row else None

                # Insert enrollment
                execute(
                    """
                    INSERT INTO enrollments
                        (students_id, section_id, users_user_id, enrollment_source, enrollment_status)
                    VALUES
                        (:sid, :sec, :actor, 'AUTO', 'ENROLLED')
                    """,
                    {"sid": student_id, "sec": section["section_id"], "actor": admin_id},
                    commit=False,
                )

                # Decrement seats
                execute(
                    """
                    UPDATE course_sections
                    SET    available_seats = available_seats - 1,
                           section_status = CASE WHEN available_seats - 1 <= 0 THEN 'FULL'
                                                 ELSE section_status END
                    WHERE  section_id = :sec
                    """,
                    {"sec": section["section_id"]},
                    commit=True,
                )

                write_provenance(
                    "enrollments",
                    f"student={student_id},section={section['section_id']}",
                    "AUTO-ADVISE", admin_id, "ADMIN",
                    "Auto-advise enrollment for new student",
                    "Admin / Auto Advise", "proc_auto_advise",
                    new_value={"student_id": student_id,
                               "section_id": section["section_id"],
                               "course": course["course_code"]},
                    request_id=req_id, # type: ignore
                )
                enrolled.append(f"{course['course_code']} (Sec {section['section_name']})")
                total_credits += course["credits"]

            except Exception as e:
                failed.append(f"{course['course_code']} (error: {str(e)[:60]})")
        else:
            enrolled.append(f"{course['course_code']} (Sec {section['section_name']}) [DRY RUN]")
            total_credits += course["credits"]

    return {
        "student_id": student_id,
        "enrolled": enrolled,
        "failed": failed,
        "total_credits": total_credits,
    }


def render():
    st.title("🤖 Auto Advise — New Student Enrollment")
    admin_id = st.session_state.user_id

    st.info(
        "This tool auto-enrolls newly admitted students (credits_completed = 0, "
        "no current enrollments) into Level courses up to a credit limit."
    )

    # ── Configuration ─────────────────────────────────────────────────────────
    semesters = fetch_all(
        "SELECT semester_id, term_name, status FROM semesters ORDER BY semester_id DESC"
    )
    sem_map     = {s["term_name"]: s["semester_id"] for s in semesters}
    active_name = next((s["term_name"] for s in semesters if s["status"] == "ACTIVE"),
                       semesters[0]["term_name"] if semesters else None)
    if not active_name:
        st.error("No semesters found.")
        return

    with st.form("auto_advise_config"):
        sem_sel      = st.selectbox("Target Semester", list(sem_map.keys()),
                                    index=list(sem_map.keys()).index(active_name))
        col1, col2   = st.columns(2)
        credit_limit = col1.number_input("Max Credits per Student", min_value=1, value=15)
        level_no     = col2.number_input("Course Level (level_no)", min_value=1, value=1)

        depts = fetch_all(
            "SELECT DISTINCT department FROM courses WHERE department IS NOT NULL ORDER BY department"
        )
        dept_list = [d["department"] for d in depts]
        dept_sel  = st.selectbox("Department Filter (required)", dept_list)
        dry_run   = st.checkbox("🧪 Dry Run (preview without enrolling)", value=True)
        submitted = st.form_submit_button("▶ Run Auto-Advise", type="primary")

    if not submitted:
        return

    semester_id = sem_map[sem_sel]

    # Find eligible students
    eligible = fetch_all(
        """
        SELECT s.users_user_id, s.student_name, s.department
        FROM   students s
        WHERE  s.credits_completed = 0
          AND  s.student_status    = 'ACTIVE'
          AND  s.department        = :dept
          AND  s.users_user_id NOT IN (
              SELECT e.students_id FROM enrollments e
              JOIN   course_sections cs ON e.section_id = cs.section_id
              JOIN   course_offerings co ON cs.offering_id = co.offering_id
              WHERE  co.semesters_id    = :sem
                AND  e.enrollment_status = 'ENROLLED'
          )
        ORDER  BY s.student_name
        """,
        {"dept": dept_sel, "sem": semester_id},
    )

    if not eligible:
        st.warning("No eligible students found for the selected criteria.")
        return

    mode_label = "DRY RUN" if dry_run else "LIVE"
    st.subheader(f"Results — {mode_label} — {len(eligible)} eligible student(s)")

    if not dry_run:
        st.warning(f"⚠️ This will enroll **{len(eligible)}** students. Proceed?")
        if not st.button("✅ Confirm and Execute", type="primary", key="aa_confirm"):
            st.info("Click Confirm to proceed.")
            return

    total_enrolled = 0
    total_failed   = 0

    for stu in eligible:
        result = _auto_enroll_student(
            stu["users_user_id"], semester_id,
            credit_limit, level_no, dept_sel, # type: ignore
            admin_id, dry_run,
        )
        total_enrolled += len(result["enrolled"])
        total_failed   += len(result["failed"])

        with st.expander(f"{'✅' if result['enrolled'] else '⚠️'} {stu['student_name']} ({stu['users_user_id']})"):
            st.markdown(f"**Total Credits:** {result['total_credits']}")
            if result["enrolled"]:
                st.success("Enrolled: " + ", ".join(result["enrolled"]))
            if result["failed"]:
                st.error("Failed/Skipped: " + ", ".join(result["failed"]))

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("Total Enrollments Created", total_enrolled)
    col2.metric("Failures / Skips", total_failed)

    if dry_run:
        st.info("✅ Dry run complete. Uncheck 'Dry Run' and run again to execute.")
