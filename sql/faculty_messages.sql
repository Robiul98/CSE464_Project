-- =============================================================================
-- faculty_messages.sql
-- New table (not in original DDL).
-- Run this once on the Oracle DB before starting the application.
-- =============================================================================

-- Sequence for auto-increment PK
CREATE SEQUENCE faculty_messages_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- Table
CREATE TABLE faculty_messages (
    message_id   NUMBER          NOT NULL,
    faculty_id   VARCHAR2(20)    NOT NULL,
    subject      VARCHAR2(200)   NOT NULL,
    body         CLOB            NOT NULL,
    sent_at      TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    status       VARCHAR2(10)    DEFAULT 'UNREAD' NOT NULL,
    admin_note   VARCHAR2(500),
    read_at      TIMESTAMP,

    CONSTRAINT pk_faculty_messages PRIMARY KEY (message_id),
    CONSTRAINT fk_fm_faculty       FOREIGN KEY (faculty_id)
        REFERENCES faculty(user_id),
    CONSTRAINT chk_fm_status       CHECK (status IN ('UNREAD', 'READ'))
);

-- Auto-increment trigger
CREATE OR REPLACE TRIGGER faculty_messages_trg
    BEFORE INSERT ON faculty_messages
    FOR EACH ROW
BEGIN
    IF :NEW.message_id IS NULL THEN
        :NEW.message_id := faculty_messages_seq.NEXTVAL;
    END IF;
END;
/
