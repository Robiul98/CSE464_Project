-- =============================================================================
-- procedures.sql
-- Oracle stored procedures for the University Registration System.
-- Run once on Oracle DB.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- proc_process_request
-- Atomic enrollment processing procedure.
-- Handles ADD and DROP request types.
-- Creates a registration_request record, modifies enrollments,
-- adjusts seat counts, and inserts into section_seat_history.
-- Provenance logging is handled by the application layer (Python).
--
-- Parameters:
--   p_student_id      : students.users_user_id
--   p_section_id      : course_sections.section_id
--   p_actor_id        : users.user_id (who is making the request)
--   p_request_type    : 'ADD' | 'DROP' | 'FACULTY-ADVISE' | 'ADMIN-OVERRIDE' | 'AUTO-ADVISE'
--   p_enrollment_src  : 'SELF' | 'FACULTY' | 'ADMIN' | 'AUTO'
--   p_reason          : human-readable reason text
--   p_request_id      : OUT parameter — newly created request_id
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE proc_process_request (
    p_student_id     IN  VARCHAR2,
    p_section_id     IN  NUMBER,
    p_actor_id       IN  VARCHAR2,
    p_request_type   IN  VARCHAR2,
    p_enrollment_src IN  VARCHAR2,
    p_reason         IN  VARCHAR2,
    p_request_id     OUT NUMBER
)
IS
    v_avail  NUMBER;
    v_exists NUMBER;
BEGIN
    -- Insert registration request (status = APPROVED for direct processing)
    INSERT INTO registration_requests (
        students_id, section_id, users_id,
        request_type, request_reason,
        request_status, processed_at, processed_note
    ) VALUES (
        p_student_id, p_section_id, p_actor_id,
        p_request_type, p_reason,
        'APPROVED', SYSTIMESTAMP, 'Processed via proc_process_request'
    )
    RETURNING request_id INTO p_request_id;

    -- Handle ADD types
    IF p_request_type IN ('ADD', 'FACULTY-ADVISE', 'ADMIN-OVERRIDE', 'AUTO-ADVISE') THEN

        -- Check available seats
        SELECT available_seats
        INTO   v_avail
        FROM   course_sections
        WHERE  section_id = p_section_id
        FOR UPDATE;

        IF v_avail <= 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20001, 'No available seats in section ' || p_section_id);
        END IF;

        -- Check not already enrolled
        SELECT COUNT(*)
        INTO   v_exists
        FROM   enrollments
        WHERE  students_id       = p_student_id
          AND  section_id        = p_section_id
          AND  enrollment_status = 'ENROLLED';

        IF v_exists > 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20002, 'Student already enrolled in section ' || p_section_id);
        END IF;

        -- Insert enrollment
        INSERT INTO enrollments (
            students_id, section_id, users_user_id,
            enrollment_source, enrollment_status
        ) VALUES (
            p_student_id, p_section_id, p_actor_id,
            p_enrollment_src, 'ENROLLED'
        );

        -- Decrement seats
        UPDATE course_sections
        SET    available_seats = available_seats - 1,
               section_status  = CASE
                                     WHEN available_seats - 1 <= 0 THEN 'FULL'
                                     ELSE section_status
                                 END
        WHERE  section_id = p_section_id;

        -- Log seat history
        INSERT INTO section_seat_history (
            sections_id, old_available_seats, new_available_seats,
            users_user_id, change_reason, request_id
        )
        SELECT section_id,
               available_seats + 1,
               available_seats,
               p_actor_id,
               'Enrollment via proc_process_request',
               p_request_id
        FROM   course_sections
        WHERE  section_id = p_section_id;

    -- Handle DROP
    ELSIF p_request_type = 'DROP' THEN

        -- Update enrollment to DROPPED
        UPDATE enrollments
        SET    enrollment_status = 'DROPPED',
               dropped_at        = SYSTIMESTAMP,
               drop_reason       = p_reason,
               users_user_id1    = p_actor_id
        WHERE  students_id        = p_student_id
          AND  section_id         = p_section_id
          AND  enrollment_status  = 'ENROLLED';

        IF SQL%ROWCOUNT = 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20003, 'No active enrollment found to drop.');
        END IF;

        -- Increment seats (trigger also fires but explicit update ensures consistency)
        UPDATE course_sections
        SET    available_seats = available_seats + 1,
               section_status  = CASE
                                     WHEN section_status = 'FULL' THEN 'OPEN'
                                     ELSE section_status
                                 END
        WHERE  section_id = p_section_id;

        -- Log seat history
        INSERT INTO section_seat_history (
            sections_id, old_available_seats, new_available_seats,
            users_user_id, change_reason, request_id
        )
        SELECT section_id,
               available_seats - 1,
               available_seats,
               p_actor_id,
               'Drop via proc_process_request',
               p_request_id
        FROM   course_sections
        WHERE  section_id = p_section_id;

    END IF;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END proc_process_request;
/


-- -----------------------------------------------------------------------------
-- proc_auto_advise
-- Bulk auto-enrollment for newly admitted students.
-- Finds eligible students (credits_completed = 0, ACTIVE, no current enrollment)
-- in the given department and enrolls them in level_no courses up to credit_limit.
-- Called from the admin panel but can also be run directly.
--
-- Parameters:
--   p_semester_id  : target semester
--   p_credit_limit : max total credits to assign per student
--   p_level_no     : course level to pull from (e.g. 1 for first-year)
--   p_department   : filter students and courses by department
--   p_admin_id     : the admin user triggering the action
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE proc_auto_advise (
    p_semester_id  IN NUMBER,
    p_credit_limit IN NUMBER,
    p_level_no     IN NUMBER,
    p_department   IN VARCHAR2,
    p_admin_id     IN VARCHAR2
)
IS
    v_req_id      NUMBER;
    v_total_cr    NUMBER;
    v_avail       NUMBER;

    CURSOR c_students IS
        SELECT s.users_user_id, s.department
        FROM   students s
        WHERE  s.credits_completed = 0
          AND  s.student_status    = 'ACTIVE'
          AND  s.department        = p_department
          AND  s.users_user_id NOT IN (
              SELECT e.students_id
              FROM   enrollments e
              JOIN   course_sections cs ON e.section_id   = cs.section_id
              JOIN   course_offerings co ON cs.offering_id = co.offering_id
              WHERE  co.semesters_id     = p_semester_id
                AND  e.enrollment_status = 'ENROLLED'
          );

    CURSOR c_courses IS
        SELECT co.offering_id, c.course_id, c.course_code, c.credits
        FROM   course_offerings co
        JOIN   courses c ON co.course_id = c.course_id
        WHERE  co.semesters_id    = p_semester_id
          AND  co.offering_status = 'OPEN'
          AND  c.level_no         = p_level_no
          AND  c.department       = p_department
        ORDER  BY c.course_code;

BEGIN
    FOR stu IN c_students LOOP
        v_total_cr := 0;

        FOR crs IN c_courses LOOP
            EXIT WHEN v_total_cr + crs.credits > p_credit_limit;

            -- Find best section (most available seats)
            BEGIN
                SELECT section_id, available_seats
                INTO   v_req_id, v_avail        -- reuse v_req_id temporarily
                FROM   (
                    SELECT section_id, available_seats
                    FROM   course_sections
                    WHERE  offering_id     = crs.offering_id
                      AND  section_status  = 'OPEN'
                      AND  available_seats > 0
                    ORDER  BY available_seats DESC
                )
                WHERE  ROWNUM = 1;

                -- Enroll via proc_process_request
                proc_process_request(
                    p_student_id     => stu.users_user_id,
                    p_section_id     => v_req_id,
                    p_actor_id       => p_admin_id,
                    p_request_type   => 'AUTO-ADVISE',
                    p_enrollment_src => 'AUTO',
                    p_reason         => 'Auto-advise for new student',
                    p_request_id     => v_req_id
                );

                v_total_cr := v_total_cr + crs.credits;

            EXCEPTION
                WHEN NO_DATA_FOUND THEN
                    -- No open section found, skip this course
                    NULL;
                WHEN OTHERS THEN
                    -- Log and continue with next course
                    NULL;
            END;
        END LOOP;
    END LOOP;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END proc_auto_advise;
/


CREATE OR REPLACE PROCEDURE proc_process_request (
    p_student_id     IN  VARCHAR2,
    p_section_id     IN  NUMBER,
    p_actor_id       IN  VARCHAR2,
    p_request_type   IN  VARCHAR2,
    p_enrollment_src IN  VARCHAR2,
    p_reason         IN  VARCHAR2,
    p_request_id     OUT NUMBER
)
IS
    v_avail  NUMBER;
    v_exists NUMBER;
BEGIN
    -- Insert registration request (status = APPROVED for direct processing)
    INSERT INTO registration_requests (
        students_id, section_id, users_id,
        request_type, request_reason,
        request_status, processed_at, processed_note
    ) VALUES (
        p_student_id, p_section_id, p_actor_id,
        p_request_type, p_reason,
        'APPROVED', SYSTIMESTAMP, 'Processed via proc_process_request'
    )
    RETURNING request_id INTO p_request_id;

    -- Handle ADD types
    IF p_request_type IN ('ADD', 'FACULTY-ADVISE', 'ADMIN-OVERRIDE', 'AUTO-ADVISE') THEN

        -- Check available seats
        SELECT available_seats
        INTO   v_avail
        FROM   course_sections
        WHERE  section_id = p_section_id
        FOR UPDATE;

        IF v_avail <= 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20001, 'No available seats in section ' || p_section_id);
        END IF;

        -- Check not already enrolled in this exact section
        SELECT COUNT(*)
        INTO   v_exists
        FROM   enrollments
        WHERE  students_id       = p_student_id
          AND  section_id        = p_section_id
          AND  enrollment_status = 'ENROLLED';

        IF v_exists > 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20002, 'Student already enrolled in section ' || p_section_id);
        END IF;

        -- *** FIX 1: Check not enrolled in a different section of the same course ***
        SELECT COUNT(*)
        INTO   v_exists
        FROM   enrollments e
        JOIN   course_sections cs  ON e.section_id    = cs.section_id
        JOIN   course_offerings co ON cs.offering_id  = co.offering_id
        JOIN   course_sections  cs2 ON cs2.section_id = p_section_id
        JOIN   course_offerings co2 ON cs2.offering_id = co2.offering_id
        WHERE  e.students_id       = p_student_id
          AND  e.enrollment_status = 'ENROLLED'
          AND  co.course_id        = co2.course_id;

        IF v_exists > 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20004,
                'Student is already enrolled in another section of this course.');
        END IF;

        -- *** FIX 2: Check for schedule/time conflict ***
        IF fn_has_schedule_conflict(p_student_id, p_section_id) = 'Y' THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20005,
                'Schedule conflict: this section overlaps with an existing enrollment.');
        END IF;

        
        -- Insert enrollment
        INSERT INTO enrollments (
            students_id, section_id, users_user_id,
            enrollment_source, enrollment_status
        ) VALUES (
            p_student_id, p_section_id, p_actor_id,
            p_enrollment_src, 'ENROLLED'
        );

        -- Decrement seats
        UPDATE course_sections
        SET    available_seats = available_seats - 1,
               section_status  = CASE
                                     WHEN available_seats - 1 <= 0 THEN 'FULL'
                                     ELSE section_status
                                 END
        WHERE  section_id = p_section_id;

        -- Log seat history
        INSERT INTO section_seat_history (
            sections_id, old_available_seats, new_available_seats,
            users_user_id, change_reason, request_id
        )
        SELECT section_id,
               available_seats + 1,
               available_seats,
               p_actor_id,
               'Enrollment via proc_process_request',
               p_request_id
        FROM   course_sections
        WHERE  section_id = p_section_id;

    -- Handle DROP
    ELSIF p_request_type = 'DROP' THEN

        -- Update enrollment to DROPPED
        UPDATE enrollments
        SET    enrollment_status = 'DROPPED',
               dropped_at        = SYSTIMESTAMP,
               drop_reason       = p_reason,
               users_user_id1    = p_actor_id
        WHERE  students_id        = p_student_id
          AND  section_id         = p_section_id
          AND  enrollment_status  = 'ENROLLED';

        IF SQL%ROWCOUNT = 0 THEN
            ROLLBACK;
            RAISE_APPLICATION_ERROR(-20003, 'No active enrollment found to drop.');
        END IF;

        -- Increment seats (trigger also fires but explicit update ensures consistency)
        UPDATE course_sections
        SET    available_seats = available_seats + 1,
               section_status  = CASE
                                     WHEN section_status = 'FULL' THEN 'OPEN'
                                     ELSE section_status
                                 END
        WHERE  section_id = p_section_id;

        -- Log seat history
        INSERT INTO section_seat_history (
            sections_id, old_available_seats, new_available_seats,
            users_user_id, change_reason, request_id
        )
        SELECT section_id,
               available_seats - 1,
               available_seats,
               p_actor_id,
               'Drop via proc_process_request',
               p_request_id
        FROM   course_sections
        WHERE  section_id = p_section_id;

    END IF;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END proc_process_request;
/
