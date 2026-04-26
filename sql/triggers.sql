-- =============================================================================
-- triggers.sql
-- Application-level triggers for the University Registration System.
-- Run once on Oracle DB after the DDL schema has been applied.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- trg_decrement_seats
-- Fires AFTER INSERT on enrollments with enrollment_status = 'ENROLLED'.
-- Decrements available_seats on the related course_section.
-- Sets section_status to 'FULL' if available_seats reaches 0.
-- NOTE: The application also decrements seats explicitly inside transactions.
--       This trigger acts as a safety net for any direct INSERT that bypasses
--       the application layer.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_decrement_seats
    AFTER INSERT ON enrollments
    FOR EACH ROW
    WHEN (NEW.enrollment_status = 'ENROLLED')
BEGIN
    UPDATE course_sections
    SET    available_seats = available_seats - 1,
           section_status  = CASE
                                 WHEN available_seats - 1 <= 0 THEN 'FULL'
                                 ELSE section_status
                             END
    WHERE  section_id = :NEW.section_id;
END;
/


-- -----------------------------------------------------------------------------
-- trg_increment_seats
-- Fires AFTER UPDATE on enrollments when status changes to 'DROPPED'.
-- Increments available_seats on the related course_section.
-- Resets section_status from FULL to OPEN if seats become available.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_increment_seats
    AFTER UPDATE OF enrollment_status ON enrollments
    FOR EACH ROW
    WHEN (OLD.enrollment_status = 'ENROLLED' AND NEW.enrollment_status = 'DROPPED')
BEGIN
    UPDATE course_sections
    SET    available_seats = available_seats + 1,
           section_status  = CASE
                                 WHEN section_status = 'FULL' THEN 'OPEN'
                                 ELSE section_status
                             END
    WHERE  section_id = :NEW.section_id;
END;
/


-- -----------------------------------------------------------------------------
-- trg_log_seat_history
-- Fires AFTER UPDATE of available_seats on course_sections.
-- Records old and new seat counts into section_seat_history.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_log_seat_history
    AFTER UPDATE OF available_seats ON course_sections
    FOR EACH ROW
BEGIN
    INSERT INTO section_seat_history (
        sections_id,
        old_available_seats,
        new_available_seats,
        changed_at,
        change_reason
    ) VALUES (
        :NEW.section_id,
        :OLD.available_seats,
        :NEW.available_seats,
        SYSTIMESTAMP,
        'Trigger: seat count changed'
    );
END;
/
