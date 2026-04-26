# University Course Registration System

A Streamlit web application for managing university course registration, faculty advising, and administrative operations. Backend is **Oracle Autonomous Free DB**.

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure DB credentials
Copy the secrets template and fill in your Oracle credentials:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your DB_USER, DB_PASSWORD, DB_DSN
```

### 4. Set up the Oracle DB
Run the following SQL scripts **in order** on your Oracle Autonomous Free DB (via SQL Developer, SQLcl, or the Oracle console):

```
1. your_original_schema.ddl      ← your provided DDL (run first)
2. sql/faculty_messages.sql      ← new table not in original DDL
3. sql/triggers.sql              ← seat management triggers
4. sql/functions.sql             ← fn_prereqs_met, fn_is_window_open
5. sql/procedures.sql            ← proc_process_request, proc_auto_advise
```

### 5. Run locally
```bash
streamlit run streamlit_app.py
```

### 6. Deploy to Streamlit Community Cloud
- Push your repo to GitHub (without secrets.toml)
- Connect repo at https://share.streamlit.io
- Add your secrets in the Streamlit Cloud dashboard under **App settings → Secrets**

---

## Project Structure

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

## Roles

| Role    | Key Capabilities |
|---------|-----------------|
| STUDENT | View profile, self-register (if window open and not on probation), browse all courses |
| FACULTY | View own profile/courses, manage advisees, advise students, browse courses, message admin |
| ADMIN   | Manage requests, messages, windows, users, offerings, auto-advise, view logs, SQL terminal |

---

## Notes

- Passwords must be stored as **bcrypt hashes** in `users.password_hash`
- The `oracledb` driver runs in **thin mode** — no Oracle Client installation needed
- All data changes write to `provenance_log` via `utils/provenance.py`
- The SQL terminal is admin-only and passes raw SQL directly to Oracle — for demo/presentation use
