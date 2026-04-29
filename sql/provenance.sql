-- =============================================================================
-- provenance.sql
-- 15 Oracle SQL Provenance Queries for the University Registration System
-- Categorized as: WHY (Q1-Q5), WHERE (Q6-Q10), HOW (Q11-Q15)
--
-- DATABASE STATE (from seed_data_v2.sql):
--   provenance_log      : 30 rows, all operation_type='INSERT', actor_role='STUDENT'
--                         why_provenance  = 'Self-enrolled'
--                         where_provenance= 'enrollments'
--                         how_provenance  = 'Self via advising'
--                         source_table    = 'enrollments', row_pk = '1'..'30'
--                         request_id      = 1..30  (maps 1:1 to registration_requests)
--   section_seat_history: 10 manual rows  (sections_id 1..10)
--                       + 30 trigger rows (change_reason='Trigger: seat change')
--                         request_id      = NULL for manual rows
--   registration_requests: 30 rows, all request_type='ADD', request_status='APPROVED'
--   enrollments          : 30 rows, all enrollment_status='ENROLLED'
--   students             : 30 rows (STU-01..STU-30)
--   course_sections      : 30 rows (section_id 1..30)
-- =============================================================================


-- =============================================================================
-- WHY-PROVENANCE (Justification) -- Queries 1 to 5
-- WHY: Explains the reason/justification for why a data value exists.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 1: List the Justification for Every Enrollment Action Logged
-- Provenance Type: WHY
-- Reason: The why_provenance column directly stores the textual justification
--         for why the enrollment INSERT was performed. This query surfaces all
--         30 reasons, grouped so you can see which reason dominates.
-- Expected: 30 rows (all say 'Self-enrolled') -- provenance_log is INSERT-only.
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.users_user_id                                        AS student_id,
    pl.row_pk                                               AS enrollment_pk,
    pl.actor_role,
    pl.operation_type,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS event_time,
    pl.why_provenance                                       AS justification
FROM
    provenance_log pl
WHERE
    pl.source_table = 'enrollments'
ORDER BY
    pl.event_time ASC;


-- -----------------------------------------------------------------------------
-- Query 2: Summarise Why-Provenance Reasons by Count (Why Each Action Happened)
-- Provenance Type: WHY
-- Reason: Aggregating why_provenance by (operation_type, actor_role, reason)
--         answers "why is each category of audit event present?" -- the
--         justification dimension at a population level.
-- Expected: 1 aggregated row: INSERT / STUDENT / Self-enrolled / 30
-- -----------------------------------------------------------------------------
SELECT
    pl.operation_type,
    pl.actor_role,
    pl.why_provenance                                       AS reason,
    COUNT(*)                                                AS occurrence_count
FROM
    provenance_log pl
WHERE
    pl.why_provenance IS NOT NULL
GROUP BY
    pl.operation_type,
    pl.actor_role,
    pl.why_provenance
ORDER BY
    occurrence_count DESC,
    pl.operation_type;


-- -----------------------------------------------------------------------------
-- Query 3: Why Were Seats Assigned to Sections? (Admin Capacity Init Reason)
-- Provenance Type: WHY
-- Reason: The change_reason column in section_seat_history is the per-row
--         justification for why seat counts changed -- classic WHY provenance
--         for the seat management subsystem.
-- Expected: 10 manual rows ('Admin capacity init') + 30 trigger rows
--           ('Trigger: seat change') = 40 rows total.
-- -----------------------------------------------------------------------------
SELECT
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    (ssh.new_available_seats - ssh.old_available_seats)     AS seats_delta,
    ssh.users_user_id                                       AS changed_by,
    ssh.change_reason                                       AS why_seats_changed,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')       AS change_time
FROM
    section_seat_history ssh
ORDER BY
    ssh.changed_at ASC;


-- -----------------------------------------------------------------------------
-- Query 4: Why Was Seat Capacity Initialised for Section 1 (CSE101-A)?
-- Provenance Type: WHY
-- Reason: Drills into one specific section to show the explicit justification
--         (change_reason) recorded at the time of each seat modification.
--         Hardcoded to sections_id = 1 (CSE101 Section A) which is guaranteed
--         to have at least 2 rows: the manual init + the enrollment trigger.
-- Expected: 2 rows -- admin init row + trigger row when STU-01 enrolled.
-- -----------------------------------------------------------------------------
SELECT
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    (ssh.new_available_seats - ssh.old_available_seats)     AS seats_delta,
    ssh.users_user_id                                       AS changed_by,
    ssh.change_reason                                       AS why_seats_changed,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')       AS change_time
FROM
    section_seat_history ssh
WHERE
    ssh.sections_id = 1          -- CSE101 Section A
ORDER BY
    ssh.changed_at ASC;


-- -----------------------------------------------------------------------------
-- Query 5: Why Did Each Student Enrol? (Join provenance_log + registration_requests)
-- Provenance Type: WHY
-- Reason: Combines the audit log's why_provenance with the original
--         request_reason from registration_requests, giving TWO layers of
--         justification -- the request motive AND the provenance label.
-- Expected: 30 rows, one per student enrollment.
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.users_user_id                                        AS student_id,
    pl.row_pk                                               AS enrollment_pk,
    rr.request_reason                                       AS original_request_reason,
    pl.why_provenance                                       AS provenance_justification,
    rr.request_status                                       AS request_outcome,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS logged_at
FROM
    provenance_log    pl
JOIN
    registration_requests rr
    ON rr.request_id = pl.request_id
WHERE
    pl.source_table = 'enrollments'
ORDER BY
    pl.event_time ASC;


-- =============================================================================
-- WHERE-PROVENANCE (Lineage / Source) -- Queries 6 to 10
-- WHERE: Identifies the origin -- which user, role, or source table caused the change.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 6: Which Student (User) Originated Each Enrollment Audit Entry?
-- Provenance Type: WHERE
-- Reason: where_provenance + users_user_id together pin the exact data origin:
--         the source table name AND the actor who caused the INSERT.
-- Expected: 30 rows -- one per student.
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.users_user_id                                        AS originating_user,
    pl.actor_role                                           AS originating_role,
    pl.source_table                                         AS source_of_change,
    pl.where_provenance                                     AS declared_lineage,
    pl.row_pk                                               AS affected_row_pk,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS event_time
FROM
    provenance_log pl
WHERE
    pl.source_table = 'enrollments'
ORDER BY
    pl.users_user_id ASC;


-- -----------------------------------------------------------------------------
-- Query 7: Count Audit Events Per Source Table and Actor Role (Activity Heatmap)
-- Provenance Type: WHERE
-- Reason: Groups the audit log by source_table and actor_role, directly showing
--         WHERE (which table) each role generates most activity -- lineage at scale.
-- Expected: 1 row (enrollments / STUDENT / INSERT / 30).
-- -----------------------------------------------------------------------------
SELECT
    pl.source_table,
    pl.actor_role,
    pl.operation_type,
    COUNT(*)                                                AS total_events,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    )                                                       AS pct_of_all_events,
    MIN(TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS'))   AS first_event,
    MAX(TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS'))   AS last_event
FROM
    provenance_log pl
GROUP BY
    pl.source_table,
    pl.actor_role,
    pl.operation_type
ORDER BY
    total_events DESC;


-- -----------------------------------------------------------------------------
-- Query 8: Pinpoint the Source User Behind Every Seat History Entry
-- Provenance Type: WHERE
-- Reason: Joins section_seat_history to provenance_log via request_id to
--         attribute each seat change back to the originating user and their role.
--         For manual admin rows (request_id IS NULL) the provenance_log join
--         yields NULL gracefully via LEFT JOIN.
-- Expected: 40 rows (10 admin-init + 30 trigger), with actor_role filled in
--           for the 30 trigger rows that have matching request_id.
-- -----------------------------------------------------------------------------
SELECT
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.users_user_id                                       AS seat_change_actor,
    pl.actor_role                                           AS actor_role_in_log,
    pl.where_provenance                                     AS log_lineage,
    ssh.change_reason,
    ssh.old_available_seats,
    ssh.new_available_seats,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')       AS changed_at
FROM
    section_seat_history ssh
LEFT JOIN
    provenance_log pl
    ON  pl.request_id    = ssh.request_id
    AND pl.users_user_id = ssh.users_user_id
ORDER BY
    ssh.sections_id ASC,
    ssh.changed_at  ASC;


-- -----------------------------------------------------------------------------
-- Query 9: Which Source Tables Appear in the Audit Log and How Frequently?
-- Provenance Type: WHERE
-- Reason: Ranks every distinct source_table value by audit frequency, showing
--         where in the schema provenance-generating activity originates.
-- Expected: 1 row (enrollments = 30 events = 100%).
-- -----------------------------------------------------------------------------
SELECT
    pl.source_table                                         AS data_origin,
    pl.where_provenance                                     AS declared_lineage,
    COUNT(*)                                                AS audit_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    )                                                       AS pct_of_total_events
FROM
    provenance_log pl
GROUP BY
    pl.source_table,
    pl.where_provenance
ORDER BY
    audit_count DESC;


-- -----------------------------------------------------------------------------
-- Query 10: Full Source Trace for Request ID 1 (STU-01 Enrolling in CSE101-A)
-- Provenance Type: WHERE
-- Reason: Joins both audit tables on request_id = 1 to reconstruct the complete
--         origin picture: who (users_user_id), what role, which source table,
--         and which seat change it triggered.
-- Expected: 1 provenance_log row LEFT JOINed with 1 seat history row = 1 row.
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.source_table,
    pl.row_pk                                               AS enrollment_pk,
    pl.users_user_id                                        AS change_origin_user,
    pl.actor_role                                           AS change_origin_role,
    pl.operation_type,
    pl.where_provenance,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS log_event_time,
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    ssh.change_reason,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')       AS seat_changed_at
FROM
    provenance_log pl
LEFT JOIN
    section_seat_history ssh
    ON  ssh.request_id    = pl.request_id
    AND ssh.sections_id   = TO_NUMBER(pl.row_pk)
WHERE
    pl.request_id = 1     -- Registration request for STU-01 enrolling in section 1
ORDER BY
    pl.event_time ASC,
    ssh.changed_at ASC;


-- =============================================================================
-- HOW-PROVENANCE (Derivation / Transformation) -- Queries 11 to 15
-- HOW: Shows how a data value was derived or evolved -- state transitions over time.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- Query 11: Show the Complete Audit Trail for Enrollment Row PK = '5' (STU-05)
-- Provenance Type: HOW
-- Reason: Chronicles every logged operation on a single row (row_pk = '5'),
--         reading the how_provenance label alongside old/new value CLOBs to
--         reconstruct HOW the record was derived from its initial insert.
-- Expected: 1 row (the INSERT event for enrollment_id = 5).
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.operation_type                                       AS transition_action,
    pl.actor_role,
    pl.how_provenance                                       AS derivation_method,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS transition_time,
    DBMS_LOB.SUBSTR(pl.old_value, 500, 1)                  AS state_before,
    DBMS_LOB.SUBSTR(pl.new_value, 500, 1)                  AS state_after
FROM
    provenance_log pl
WHERE
    pl.source_table = 'enrollments'
    AND pl.row_pk   = '5'       -- enrollment_id = 5, student STU-05
ORDER BY
    pl.event_time ASC;


-- -----------------------------------------------------------------------------
-- Query 12: Seat Depletion Timeline with Running Total for Section 1 (CSE101-A)
-- Provenance Type: HOW
-- Reason: Uses SUM() OVER (window) to compute the cumulative seats consumed
--         over time, showing HOW seat availability evolved step-by-step for
--         section 1 (CSE101-A), which has both an admin init row and a trigger row.
-- Expected: 2 rows -- init (delta = +30) then trigger depletion (delta = -1),
--           cumulative shows the net progression.
-- -----------------------------------------------------------------------------
SELECT
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    (ssh.new_available_seats - ssh.old_available_seats)                 AS seat_delta,
    SUM(ssh.new_available_seats - ssh.old_available_seats)
        OVER (
            PARTITION BY ssh.sections_id
            ORDER BY     ssh.changed_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                                               AS running_net_change,
    ssh.change_reason,
    ssh.users_user_id                                                   AS actor,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')                   AS recorded_at
FROM
    section_seat_history ssh
WHERE
    ssh.sections_id = 1        -- CSE101 Section A (manual init + trigger row)
ORDER BY
    ssh.changed_at ASC;


-- -----------------------------------------------------------------------------
-- Query 13: Full Seat Depletion Evolution Across ALL Sections (Running Totals)
-- Provenance Type: HOW
-- Reason: Extends Q12 to all sections, showing HOW available seats evolved
--         over time for every section in the system via analytic window function.
--         Demonstrates derivation of current seat count from initial capacity.
-- Expected: 40 rows (10 init + 30 trigger), each annotated with running change.
-- -----------------------------------------------------------------------------
SELECT
    ssh.seat_log_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    (ssh.new_available_seats - ssh.old_available_seats)                 AS seat_delta,
    SUM(ssh.new_available_seats - ssh.old_available_seats)
        OVER (
            PARTITION BY ssh.sections_id
            ORDER BY     ssh.changed_at
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )                                                               AS running_net_change,
    ssh.change_reason,
    ssh.users_user_id                                                   AS actor,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')                   AS recorded_at
FROM
    section_seat_history ssh
ORDER BY
    ssh.sections_id ASC,
    ssh.changed_at  ASC;


-- -----------------------------------------------------------------------------
-- Query 14: Ordered Transformation Steps Across All Provenance Log Entries
-- Provenance Type: HOW
-- Reason: Uses ROW_NUMBER() windowed by request_id to assign a step number
--         to each logged event, explicitly reconstructing the derivation order
--         (step 1 = INSERT) for every request processed through the system.
-- Expected: 30 rows, each with step_number = 1 (single-step INSERT workflow).
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id,
    pl.request_id,
    ROW_NUMBER() OVER (
        PARTITION BY pl.request_id
        ORDER BY     pl.event_time ASC
    )                                                       AS step_number,
    pl.operation_type                                       AS transformation_step,
    pl.source_table,
    pl.users_user_id                                        AS actor,
    pl.actor_role,
    pl.how_provenance                                       AS derivation_description,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')        AS step_time
FROM
    provenance_log pl
ORDER BY
    pl.request_id  ASC,
    pl.event_time  ASC;


-- -----------------------------------------------------------------------------
-- Query 15: Enrollment-to-Seat-Change Derivation Chain (How One Action Triggers Another)
-- Provenance Type: HOW
-- Reason: Joins provenance_log (the INSERT event) to section_seat_history
--         (the triggered seat decrement) via request_id for all 30 requests.
--         This reconstructs HOW the enrollment event causally derived the seat
--         deduction -- a two-step automatic derivation chain.
-- Expected: 30 rows, one per enrollment, each showing the derived seat change.
-- -----------------------------------------------------------------------------
SELECT
    pl.log_id                                           AS provenance_log_id,
    pl.request_id,
    pl.users_user_id                                    AS student_id,
    pl.how_provenance                                   AS step_1_derivation,
    pl.operation_type                                   AS step_1_operation,
    TO_CHAR(pl.event_time, 'YYYY-MM-DD HH24:MI:SS')     AS step_1_time,
    ssh.seat_log_id                                     AS seat_history_id,
    ssh.sections_id,
    ssh.old_available_seats,
    ssh.new_available_seats,
    ssh.change_reason                                   AS step_2_derivation,
    TO_CHAR(ssh.changed_at, 'YYYY-MM-DD HH24:MI:SS')    AS step_2_time
FROM
    provenance_log pl
JOIN
    section_seat_history ssh
    ON pl.row_pk = TO_CHAR(ssh.sections_id) 
    AND pl.source_table = 'course_sections'
    AND ssh.change_reason = 'Trigger: seat change'
ORDER BY
    pl.request_id ASC;
