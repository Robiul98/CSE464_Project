# 🎓 East West University Course Registration System

A Streamlit web application for managing university course registration, faculty advising, and administrative operations. Backend is **Oracle Autonomous Free DB**.

---
## 📁 Project Structure
```
streamlit_app.py              # Entry point — login, sidebar, routing
requirements.txt
.streamlit/
    secrets.toml.template     # Copy to secrets.toml (not committed)
db/
    connection.py             # Oracle connection, fetch_all, execute, raw_execute
utils/
    semester.py               # Active semester resolver
    window_check.py           # Advising window open/closed check
    provenance.py             # write_provenance() — called after every DB write
auth/
    login.py                  # Login form, password verify, session init
components/
    registration_panel.py     # Shared F/R/General registration panels
    curriculum_viewer.py      # Prerequisite tree viewer
pages/
    student/
        profile.py            # Student own profile
        registration.py       # Registration portal (probation + window gated)
        all_courses.py        # Read-only all courses with flags
    faculty/
        profile.py            # Faculty own profile
        my_courses.py         # Sections assigned to faculty
        advisee_list.py       # Assigned students list
        student_view.py       # Read-only student profile + enrollments
        advising.py           # Faculty advising portal for a student
        all_courses.py        # Read-only all courses (no student flags)
        messages.py           # Compose and view messages to admin
    admin/
        requests.py           # Registration requests — approve/reject/ignore
        messages.py           # Faculty message inbox
        windows.py            # Advising window CRUD
        approvals.py          # User account approve/reject/block/unblock
        offerings.py          # Course offerings and section management
        auto_advise.py        # Bulk new student enrollment
        logs.py               # Provenance log — 5 views
        terminal.py           # Direct SQL terminal
sql/
    faculty_messages.sql      # New table creation
    triggers.sql              # Seat management triggers
    functions.sql             # fn_prereqs_met, fn_is_window_open
    procedures.sql            # proc_process_request, proc_auto_advise
```

---

## 👱 Roles

| Role    | Key Capabilities |
|---------|-----------------|
| STUDENT | View profile, self-register (if window open and not on probation), browse all courses |
| FACULTY | View own profile/courses, manage advisees, advise students, browse courses, message admin |
| ADMIN   | Manage requests, messages, windows, users, offerings, auto-advise, view logs, SQL terminal |

---

## 📒 Notes

- Passwords must be stored as **bcrypt hashes** in `users.password_hash`
- The `oracledb` driver runs in **thin mode** — no Oracle Client installation needed
- All data changes write to `provenance_log` via `utils/provenance.py`
- The SQL terminal is admin-only and passes raw SQL directly to Oracle — for demo/presentation use


---

## 🚀 Key Features & Technical Highlights

This application is built with robust security, strict business logic, and comprehensive auditing to simulate a real-world university environment:

* **Advanced Concurrency Control:** Implements a strict "first-come, first-serve" mechanism for seat management. If multiple students attempt to claim the last remaining seat in a section simultaneously, the system safely processes the requests without double-booking.
* **Comprehensive Conflict Checking:** The registration engine automatically prevents scheduling errors. It thoroughly checks for section time conflicts, ensuring a student cannot register for overlapping classes.
* **Tiered Advising Windows:** Advising access is dynamically categorized based on student credits and time windows (e.g., seniors registering before freshmen), alongside specific time-based advising windows allocated by faculty.
* **Granular Provenance Logging:** Every insert, update, or delete action performed by a Student, Faculty, or Admin is recorded in the `provenance_log`. This guarantees total transparency and accountability across the system.
* **SQL Injection Prevention:** All database transactions enforce the use of **bind variables** rather than string formatting, completely escaping malicious inputs and preventing SQL injection attacks.
* **Secure Authentication:** User passwords are encrypted using **bcrypt hashing**, ensuring sensitive credentials are never stored in plaintext.
* **Admin SQL Terminal:** A built-in terminal allows administrators and faculty to directly query the database, evaluate provenance tracking, and maintain historical audits natively within the browser.
* **Database Triggers:** Utilizes Oracle database triggers to automatically manage seat counts and enforce data integrity constraints at the database level.

---


