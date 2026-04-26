-- =============================================================================
-- functions.sql
-- Oracle stored functions for the University Registration System.
-- Run once on Oracle DB.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- fn_prereqs_met
-- Returns 'Y' if all prerequisites for p_course_id are met by p_student_id,
-- or if the course has no prerequisites.
-- Returns 'N' if any prerequisite is not satisfied.
-- A prerequisite is satisfied when the student has a non-NULL, non-F grade
-- in the takes table for that prerequisite course.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_prereqs_met (
    p_student_id  IN VARCHAR2,
    p_course_id   IN NUMBER
) RETURN CHAR
IS
    v_total_prereqs  NUMBER;
    v_met_prereqs    NUMBER;
BEGIN
    -- Count how many prerequisites exist for this course
    SELECT COUNT(*)
    INTO   v_total_prereqs
    FROM   course_prerequisites
    WHERE  courses_course_id = p_course_id;

    -- If no prerequisites, automatically satisfied
    IF v_total_prereqs = 0 THEN
        RETURN 'Y';
    END IF;

    -- Count how many prerequisites the student has met
    -- (has a non-NULL, non-F grade in takes for each required course)
    SELECT COUNT(*)
    INTO   v_met_prereqs
    FROM   course_prerequisites cp
    WHERE  cp.courses_course_id = p_course_id
      AND  EXISTS (
               SELECT 1
               FROM   takes t
               WHERE  t.user_id   = p_student_id
                 AND  t.course_id = cp.courses_course_id1
                 AND  t.grade IS NOT NULL
                 AND  t.grade != 'F'
           );

    IF v_met_prereqs = v_total_prereqs THEN
        RETURN 'Y';
    ELSE
        RETURN 'N';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RETURN 'N';
END fn_prereqs_met;
/


-- -----------------------------------------------------------------------------
-- fn_is_window_open
-- Returns 'Y' if at least one advising_windows row is currently active
-- for the given role and semester.
-- For STUDENT role, also checks credits and cgpa ranges.
-- For FACULTY/ADMIN, credit and cgpa params are ignored (pass NULL).
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_is_window_open (
    p_role        IN VARCHAR2,
    p_semester_id IN NUMBER,
    p_credits     IN NUMBER   DEFAULT NULL,
    p_cgpa        IN NUMBER   DEFAULT NULL
) RETURN CHAR
IS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*)
    INTO   v_count
    FROM   advising_windows
    WHERE  target_role  = p_role
      AND  semester_id  = p_semester_id
      AND  SYSTIMESTAMP BETWEEN start_time AND end_time
      AND  (p_credits IS NULL OR p_credits BETWEEN min_credits AND max_credits)
      AND  (min_cgpa  IS NULL OR p_cgpa    IS NULL OR p_cgpa >= min_cgpa)
      AND  (max_cgpa  IS NULL OR p_cgpa    IS NULL OR p_cgpa <= max_cgpa);

    IF v_count > 0 THEN
        RETURN 'Y';
    ELSE
        RETURN 'N';
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RETURN 'N';
END fn_is_window_open;
/
