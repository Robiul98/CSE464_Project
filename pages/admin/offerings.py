"""
pages/admin/offerings.py
Admin management of course offerings and sections.
Create sections, extend seats, close sections, manage schedules, adjust rooms.
"""

import datetime
import pandas as pd
import streamlit as st
from db import fetch_all, fetch_one, execute
from utils.provenance import write_provenance


def _get_schedule_str(section_id: int) -> str:
    rows = fetch_all(
        """
        SELECT day_of_week,
               TO_CHAR(start_time,'HH24:MI') AS st,
               TO_CHAR(end_time,  'HH24:MI') AS et,
               class_type
        FROM   section_schedule WHERE section_id = :sid ORDER BY day_of_week
        """,
        {"sid": section_id},
    )
    if not rows:
        return "—"
    return " | ".join(f"{r['day_of_week']} {r['st']}-{r['et']} ({r['class_type']})" for r in rows)


def _render_section_management(offering_id: int, course_code: str, admin_id: str):
    """Render section table + all section-level actions for one offering."""

    sections = fetch_all(
        """
        SELECT cs.section_id, cs.section_name, cs.room_no,
               cs.max_capacity, cs.available_seats, cs.section_status,
               f.faculty_name
        FROM   course_sections cs
        LEFT   JOIN faculty f ON cs.faculty_id = f.user_id
        WHERE  cs.offering_id = :oid
        ORDER  BY cs.section_name
        """,
        {"oid": offering_id},
    )

    faculty_list = fetch_all(
        "SELECT user_id, faculty_name, department FROM faculty ORDER BY faculty_name"
    )
    # SAFELY ADD A "TBA" OPTION:
    fac_map = {"None (TBA)": None}
    for f in faculty_list:
        fac_map[f["faculty_name"]] = f["user_id"]

    for sec in sections:
        sid  = sec["section_id"]
        skey = f"sec_{sid}"

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1.2, 1.5, 1.5, 1.5])
            col1.markdown(f"**Sec {sec['section_name']}**")
            col2.markdown(f"Faculty: {sec['faculty_name'] or '—'}")
            col3.markdown(
                f"Seats: {sec['available_seats']}/{sec['max_capacity']}  \n"
                f"Room: {sec['room_no'] or '—'}"
            )
            col4.markdown(f"Status: **{sec['section_status']}**")
            st.caption(f"Schedule: {_get_schedule_str(sid)}")

            action_tabs = st.tabs(["Extend Seats", "Schedule", "Room / Faculty", "Close"])

            # ── Extend Seats ──────────────────────────────────────────────────
            with action_tabs[0]:
                n = st.number_input("Add N seats", min_value=1, value=1, key=f"ext_{skey}")
                if st.button("Extend", key=f"extbtn_{skey}", type="primary"):
                    old_avail = sec["available_seats"]
                    old_max   = sec["max_capacity"]
                    execute(
                        """
                        UPDATE course_sections
                        SET    available_seats = available_seats + :n,
                               max_capacity    = max_capacity + :n,
                               section_status  = CASE WHEN section_status = 'FULL' THEN 'OPEN'
                                                      ELSE section_status END
                        WHERE  section_id = :sid
                        """,
                        {"n": n, "sid": sid},
                        commit=False,
                    )
                    execute(
                        """
                        INSERT INTO section_seat_history
                            (sections_id, old_available_seats, new_available_seats,
                             users_user_id, change_reason)
                        VALUES (:sid, :old, :new, :actor, 'Admin seat extension')
                        """,
                        {"sid": sid, "old": old_avail, "new": old_avail + n, "actor": admin_id},
                        commit=True,
                    )
                    write_provenance(
                        "course_sections", str(sid), "UPDATE", admin_id, "ADMIN",
                        f"Extended seats by {n}", "Admin / Offerings", "Seat extension",
                        old_value={"available_seats": old_avail, "max_capacity": old_max},
                        new_value={"available_seats": old_avail + n, "max_capacity": old_max + n},
                    )
                    st.toast(f"Added {n} seats to Section {sec['section_name']}.", icon="✅")
                    st.rerun()

            # ── Schedule ──────────────────────────────────────────────────────
            with action_tabs[1]:
                existing_sched = fetch_all(
                    """
                    SELECT schedule_id, day_of_week,
                           TO_CHAR(start_time,'HH24:MI') AS st,
                           TO_CHAR(end_time,  'HH24:MI') AS et,
                           class_type
                    FROM   section_schedule WHERE section_id = :sid ORDER BY day_of_week
                    """,
                    {"sid": sid},
                )
                if existing_sched:
                    for sched in existing_sched:
                        sc1, sc2, sc3 = st.columns([4, 1, 1])
                        sc1.write(
                            f"{sched['day_of_week']}  {sched['st']}–{sched['et']}  ({sched['class_type']})"
                        )
                        if sc3.button("🗑", key=f"delsched_{sched['schedule_id']}"):
                            execute(
                                "DELETE FROM section_schedule WHERE schedule_id = :sid",
                                {"sid": sched["schedule_id"]},
                            )
                            st.toast("Schedule row deleted.", icon="🗑️")
                            st.rerun()

                st.markdown("**Add Schedule Row**")
                days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                sc_a, sc_b, sc_c, sc_d = st.columns(4)
                new_day  = sc_a.selectbox("Day", days, key=f"nday_{skey}")
                new_st   = sc_b.time_input("Start", value=datetime.time(8, 0), key=f"nst_{skey}")
                new_et   = sc_c.time_input("End",   value=datetime.time(9, 30), key=f"net_{skey}")
                new_type = sc_d.selectbox("Type", ["THEORY", "LAB"], key=f"ntype_{skey}")

                if st.button("Add Row", key=f"addschedbtn_{skey}"):
                    today = datetime.date.today()
                    execute(
                        """
                        INSERT INTO section_schedule
                            (section_id, day_of_week, start_time, end_time, class_type)
                        VALUES
                            (:sid, :day,
                             TO_TIMESTAMP(:st, 'HH24:MI'),
                             TO_TIMESTAMP(:et, 'HH24:MI'),
                             :ctype)
                        """,
                        {
                            "sid": sid, "day": new_day,
                            "st": new_st.strftime("%H:%M"),
                            "et": new_et.strftime("%H:%M"),
                            "ctype": new_type,
                        },
                    )
                    st.toast("Schedule row added.", icon="✅")
                    st.rerun()

            # ── Room / Faculty ────────────────────────────────────────────────
            with action_tabs[2]:
                new_room = st.text_input("Room No", value=sec["room_no"] or "", key=f"room_{skey}")
                fac_names = list(fac_map.keys())
                cur_fac   = sec["faculty_name"] or ""
                fac_idx   = fac_names.index(cur_fac) if cur_fac in fac_names else 0
                new_fac   = st.selectbox("Faculty", fac_names, index=fac_idx, key=f"fac_{skey}")

                if st.button("Save Room / Faculty", key=f"saverfbtn_{skey}", type="primary"):
                    execute(
                        """
                        UPDATE course_sections
                        SET    room_no    = :room,
                               faculty_id = :fid
                        WHERE  section_id = :sid
                        """,
                        {"room": new_room.strip() or None,
                         "fid": fac_map[new_fac], "sid": sid},
                    )
                    write_provenance(
                        "course_sections", str(sid), "UPDATE", admin_id, "ADMIN",
                        "Updated room/faculty", "Admin / Offerings", "Form edit",
                    )
                    st.toast("Room/Faculty updated.", icon="✅")
                    st.rerun()

            # ── Close ─────────────────────────────────────────────────────────
            with action_tabs[3]:
                if sec["section_status"] == "CLOSED":
                    st.info("Section is already closed.")
                else:
                    if st.button("Close This Section", key=f"closebtn_{skey}", type="primary"):
                        st.session_state[f"confirm_close_{skey}"] = True

                    if st.session_state.get(f"confirm_close_{skey}"):
                        st.warning("Close this section? Students will not be able to register.")
                        c1, c2 = st.columns(2)
                        if c1.button("Confirm Close", key=f"cclose_{skey}", type="primary"):
                            execute(
                                "UPDATE course_sections SET section_status = 'CLOSED' WHERE section_id = :sid",
                                {"sid": sid},
                            )
                            write_provenance(
                                "course_sections", str(sid), "UPDATE", admin_id, "ADMIN",
                                "Closed section", "Admin / Offerings", "Admin close",
                            )
                            st.session_state.pop(f"confirm_close_{skey}", None)
                            st.toast("Section closed.", icon="✅")
                            st.rerun()
                        if c2.button("Cancel", key=f"cancelclose_{skey}"):
                            st.session_state.pop(f"confirm_close_{skey}", None)
                            st.rerun()

    # ── Create New Section ────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("➕ Create New Section"):
        with st.form(f"new_sec_form_{offering_id}"):
            c1, c2 = st.columns(2)
            ns_name = c1.text_input("Section Name *", placeholder="e.g. A, B, L1")
            ns_room = c2.text_input("Room No")
            fac_sel = st.selectbox("Assign Faculty *", list(fac_map.keys()))
            n1, n2  = st.columns(2)
            ns_cap  = n1.number_input("Max Capacity *", min_value=1, value=30)
            ns_avail= n2.number_input("Initial Available Seats", min_value=0, value=30)
            submitted_ns = st.form_submit_button("Create Section", type="primary")

        if submitted_ns:
            if not ns_name.strip():
                st.error("Section name is required.")
            else:
                execute(
                    """
                    INSERT INTO course_sections
                        (offering_id, section_name, faculty_id, room_no,
                         max_capacity, available_seats, section_status)
                    VALUES
                        (:oid, :name, :fid, :room, :cap, :avail, 'OPEN')
                    """,
                    {
                        "oid": offering_id,
                        "name": ns_name.strip().upper(),
                        "fid": fac_map[fac_sel],
                        "room": ns_room.strip() or None,
                        "cap": ns_cap,
                        "avail": ns_avail,
                    },
                )
                write_provenance(
                    "course_sections", "NEW", "INSERT", admin_id, "ADMIN",
                    f"Created new section {ns_name} for offering {offering_id}",
                    "Admin / Offerings", "Admin create section",
                )
                st.toast(f"Section {ns_name} created.", icon="✅")
                st.rerun()


def render():
    st.title("📖 Course Offerings Management")
    admin_id = st.session_state.user_id

    semesters = fetch_all(
        "SELECT semester_id, term_name, status FROM semesters ORDER BY semester_id DESC"
    )
    if not semesters:
        st.warning("No semesters found.")
        return

    sem_map     = {s["term_name"]: s["semester_id"] for s in semesters}
    active_name = next((s["term_name"] for s in semesters if s["status"] == "ACTIVE"), semesters[0]["term_name"])
    sem_sel     = st.selectbox("Select Semester", list(sem_map.keys()),
                               index=list(sem_map.keys()).index(active_name))
    semester_id = sem_map[sem_sel]

    offerings = fetch_all(
        """
        SELECT co.offering_id, c.course_code, c.course_title, c.credits,
               c.department, co.offering_status,
               COUNT(cs.section_id)    AS section_count,
               SUM(cs.max_capacity)    AS total_seats,
               SUM(cs.available_seats) AS avail_seats
        FROM   course_offerings co
        JOIN   courses c ON co.course_id = c.course_id
        LEFT   JOIN course_sections cs ON cs.offering_id = co.offering_id
        WHERE  co.semesters_id = :sem
        GROUP  BY co.offering_id, c.course_code, c.course_title, c.credits,
                  c.department, co.offering_status
        ORDER  BY c.department, c.course_code
        """,
        {"sem": semester_id},
    )

    # ── ADD COURSE TO SEMESTER ────────────────────────────────────────────────
    with st.expander("➕ Add Course to this Semester", expanded=False):
        # Fetch active courses that aren't already offered in this semester
        available_courses = fetch_all(
            """
            SELECT course_id, course_code, course_title 
            FROM courses 
            WHERE is_active = 'Y' 
              AND course_id NOT IN (
                  SELECT course_id FROM course_offerings WHERE semesters_id = :sem
              )
            ORDER BY course_code
            """,
            {"sem": semester_id}
        )
        
        if not available_courses:
            st.info("All active courses are already offered this semester!")
        else:
            course_opts = {f"{c['course_code']} - {c['course_title']}": c["course_id"] for c in available_courses}
            with st.form("add_offering_form"):
                sel_course = st.selectbox("Select Course to Add", list(course_opts.keys()))
                submit_offering = st.form_submit_button("Add Course to Semester", type="primary")
                
            if submit_offering:
                cid = course_opts[sel_course]
                execute(
                    "INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (:sem, :cid, 'OPEN')",
                    {"sem": semester_id, "cid": cid}
                )
                write_provenance(
                    "course_offerings", "NEW", "INSERT", admin_id, "ADMIN", 
                    f"Added course {sel_course} to semester {semester_id}", 
                    "Admin / Offerings", "Form submit"
                )
                st.toast(f"Added {sel_course} to {sem_sel}.", icon="✅")
                st.rerun()
    # ──────────────────────────────────────────────────────────────────────────

    if not offerings:
        st.info("No offerings for this semester.")
        return

    st.caption(f"**{len(offerings)}** courses offered in {sem_sel}")

    dept_f = st.selectbox("Filter by Department",
                          ["All"] + sorted({o["department"] or "—" for o in offerings}),
                          key="off_dept_f")

    for off in offerings:
        if dept_f != "All" and (off["department"] or "—") != dept_f:
            continue

        status_icon = {"OPEN": "🟢", "CLOSED": "🔴", "CANCELLED": "⚫"}.get(
            off["offering_status"], "❓"
        )

        with st.expander(
            f"{status_icon} {off['course_code']} — {off['course_title']}  "
            f"|  {int(off['section_count'] or 0)} sections  "
            f"|  {int(off['avail_seats'] or 0)}/{int(off['total_seats'] or 0)} seats"
        ):
            col1, col2, col3 = st.columns([2, 2, 2])
            col1.markdown(f"**Department:** {off['department'] or '—'}")
            col2.markdown(f"**Credits:** {off['credits']}")
            new_status = col3.selectbox(
                "Offering Status",
                ["OPEN", "CLOSED", "CANCELLED"],
                index=["OPEN", "CLOSED", "CANCELLED"].index(off["offering_status"]),
                key=f"off_status_{off['offering_id']}",
            )
            if new_status != off["offering_status"]:
                if st.button("Update Status", key=f"upd_off_status_{off['offering_id']}"):
                    execute(
                        "UPDATE course_offerings SET offering_status = :st WHERE offering_id = :oid",
                        {"st": new_status, "oid": off["offering_id"]},
                    )
                    write_provenance(
                        "course_offerings", str(off["offering_id"]), "UPDATE",
                        admin_id, "ADMIN",
                        f"Status changed to {new_status}",
                        "Admin / Offerings", "Status select",
                        old_value={"status": off["offering_status"]},
                        new_value={"status": new_status},
                    )
                    st.toast("Offering status updated.", icon="✅")
                    st.rerun()

            st.divider()
            st.markdown("**Sections:**")
            _render_section_management(off["offering_id"], off["course_code"], admin_id)
