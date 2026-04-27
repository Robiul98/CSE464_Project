-- =============================================================================
-- 6. COURSE_PREREQUISITES  (10 rows -- composite natural PK, no sequence)
--    courses_course_id  = the course that has the requirement
--    courses_course_id1 = the prerequisite course
--    Both FK -> courses.course_id (IDs 1..15 all exist above)
-- =============================================================================
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (188, 187);  -- CSE102 requires CSE101
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (189, 188);  -- CSE201 requires CSE102
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (190, 187);  -- CSE202 requires CSE101
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (191, 189);  -- CSE301 requires CSE201
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (192, 190);  -- CSE302 requires CSE202
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (193, 189);  -- CSE401 requires CSE201
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (194, 190);  -- CSE402 requires CSE202
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (199, 189);  -- CSE303 requires CSE201
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (200, 199);  -- CSE304 requires CSE303
INSERT INTO course_prerequisites (courses_course_id, courses_course_id1) VALUES (201, 192);  -- CSE403 requires CSE302


-- =============================================================================
-- 7. ADVISING_WINDOWS  (5 rows -- sequence -> window_id 1..5)
--    FK: semester_id -> semesters.semester_id
-- =============================================================================
INSERT INTO advising_windows (semester_id, target_role, min_credits, max_credits, min_cgpa, max_cgpa, start_time, end_time, reason_label)
VALUES (16, 'STUDENT', 0, 9999, 0.00, 4.00, TIMESTAMP '2026-04-25 09:00:00', TIMESTAMP '2026-05-10 23:59:59', 'Regular student window');

INSERT INTO advising_windows (semester_id, target_role, min_credits, max_credits, min_cgpa, max_cgpa, start_time, end_time, reason_label)
VALUES (16, 'FACULTY', 0, 9999, NULL, NULL, TIMESTAMP '2026-04-20 09:00:00', TIMESTAMP '2026-04-25 23:59:59', 'Faculty review window');

INSERT INTO advising_windows (semester_id, target_role, min_credits, max_credits, min_cgpa, max_cgpa, start_time, end_time, reason_label)
VALUES (16, 'ADMIN', 0, 9999, NULL, NULL,   TIMESTAMP '2026-04-15 09:00:00', TIMESTAMP '2026-05-15 23:59:59', 'Admin full-access window');

INSERT INTO advising_windows (semester_id, target_role, min_credits, max_credits, min_cgpa, max_cgpa, start_time, end_time, reason_label)
VALUES (17, 'STUDENT', 0, 9999, 0.00, 4.00, TIMESTAMP '2026-07-25 09:00:00', TIMESTAMP '2026-08-10 23:59:59', 'Fall 2026 student window');

INSERT INTO advising_windows (semester_id, target_role, min_credits, max_credits, min_cgpa, max_cgpa, start_time, end_time, reason_label)
VALUES (15, 'STUDENT', 0, 9999, 0.00, 4.00, TIMESTAMP '2025-11-25 09:00:00', TIMESTAMP '2025-12-10 23:59:59', 'Spring 2026 student window');


-- =============================================================================
-- 8. COURSE_OFFERINGS  (15 rows -- sequence -> offering_id 1..15)
--    All 15 courses offered in Summer 2026 (semesters_id=4).
--    UNIQUE constraint: (semesters_id, course_id) -- all 15 combos are unique.
--    FK: semesters_id -> semesters.semester_id (4 exists)
--    FK: course_id    -> courses.course_id    (1..15 all exist)
-- =============================================================================
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 187, 'OPEN');  -- offering_id=1  CSE101
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 188, 'OPEN');  -- offering_id=2  CSE102
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 189, 'OPEN');  -- offering_id=3  CSE201
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 190, 'OPEN');  -- offering_id=4  CSE202
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 191, 'OPEN');  -- offering_id=5  CSE301
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 192, 'OPEN');  -- offering_id=6  CSE302
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 193, 'OPEN');  -- offering_id=7  CSE401
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 194, 'OPEN');  -- offering_id=8  CSE402
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 195, 'OPEN');  -- offering_id=9  MAT101
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 196, 'OPEN');  -- offering_id=10 MAT102
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 197, 'OPEN');  -- offering_id=11 PHY101
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 198, 'OPEN');  -- offering_id=12 EEE101
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 199, 'OPEN');  -- offering_id=13 CSE303
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 200, 'OPEN');  -- offering_id=14 CSE304
INSERT INTO course_offerings (semesters_id, course_id, offering_status) VALUES (16, 201, 'OPEN');  -- offering_id=15 CSE403


-- =============================================================================
-- 9. TAKES  (30 rows -- composite natural PK (user_id, course_id), no sequence)
--    All 30 students have completed CSE101 (course_id=1).  Grades cycle.
--    FK: user_id   -> students.users_user_id  (STU-01..30 all exist)
--    FK: course_id -> courses.course_id       (1 exists)
-- =============================================================================
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-01', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-02', 187, 'A-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-03', 187, 'B+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-04', 187, 'B');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-05', 187, 'B-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-06', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-07', 187, 'C+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-08', 187, 'C');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-09', 187, 'B+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-10', 187, 'D');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-11', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-12', 187, 'A-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-13', 187, 'B');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-14', 187, 'B-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-15', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-16', 187, 'B+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-17', 187, 'C');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-18', 187, 'B');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-19', 187, 'C+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-20', 187, 'A-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-21', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-22', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-23', 187, 'D');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-24', 187, 'B+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-25', 187, 'A-');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-26', 187, 'B');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-27', 187, 'C+');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-28', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-29', 187, 'A');
INSERT INTO takes (user_id, course_id, grade) VALUES ('STU-30', 187, 'B+');


-- =============================================================================
-- 10. COURSE_SECTIONS  (30 rows -- sequence -> section_id 1..30)
--     2 sections ('A' and 'B') per offering.  Faculty rotates FAC-01..FAC-10.
--     UNIQUE: (offering_id, section_name) -- each offering gets one A and one B.
--     FK: offering_id -> course_offerings.offering_id  (1..15 all exist)
--     FK: faculty_id  -> faculty.user_id               (FAC-01..10 all exist)
--     available_seats = max_capacity initially.  trg_decrement_seats
--     will decrement by 1 for each ENROLLED enrollment insert below.
-- =============================================================================
-- offering 1 (CSE101)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (204,  '1', 'FAC-01', 'Room-101', 'Sun-Tue 08:00-09:30',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (204,  '2', 'FAC-02', 'Room-102', 'Mon-Wed 08:00-09:30',  30, 30, 'OPEN');
-- offering 2 (CSE102)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (205,  '1', 'FAC-03', 'Room-103', 'Sun-Tue 09:30-11:00',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (205,  '2', 'FAC-04', 'Room-104', 'Mon-Wed 09:30-11:00',  30, 30, 'OPEN');
-- offering 3 (CSE201)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (206,  '1', 'FAC-05', 'Room-201', 'Sun-Tue 11:00-12:30',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (206,  '2', 'FAC-06', 'Room-202', 'Mon-Wed 11:00-12:30',  30, 30, 'OPEN');
-- offering 4 (CSE202)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (207,  '1', 'FAC-07', 'Room-203', 'Sun-Tue 12:30-14:00',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (207,  '2', 'FAC-08', 'Room-204', 'Mon-Wed 12:30-14:00',  30, 30, 'OPEN');
-- offering 5 (CSE301)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (208,  '1', 'FAC-09', 'Room-301', 'Sun-Tue 14:00-15:30',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (208,  '2', 'FAC-10', 'Room-302', 'Mon-Wed 14:00-15:30',  30, 30, 'OPEN');
-- offering 6 (CSE302)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (209,  '1', 'FAC-01', 'Room-303', 'Sun-Tue 15:30-17:00',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (209,  '2', 'FAC-02', 'Room-304', 'Mon-Wed 15:30-17:00',  30, 30, 'OPEN');
-- offering 7 (CSE401)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (210,  '1', 'FAC-03', 'Room-401', 'Tue-Thu 08:00-09:30',  25, 25, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (210,  '2', 'FAC-04', 'Room-402', 'Tue-Thu 09:30-11:00',  25, 25, 'OPEN');
-- offering 8 (CSE402)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (211,  '1', 'FAC-05', 'Room-403', 'Tue-Thu 11:00-12:30',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (211,  '2', 'FAC-06', 'Room-404', 'Tue-Thu 12:30-14:00',  30, 30, 'OPEN');
-- offering 9 (MAT101)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (212,  '1', 'FAC-07', 'Room-101', 'Tue-Thu 14:00-15:30',  35, 35, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (212,  '2', 'FAC-08', 'Room-102', 'Tue-Thu 15:30-17:00',  35, 35, 'OPEN');
-- offering 10 (MAT102)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (213, '1', 'FAC-09', 'Room-103', 'Mon-Wed 08:00-09:30',  35, 35, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (213, '2', 'FAC-10', 'Room-104', 'Sun-Tue 08:00-09:30',  35, 35, 'OPEN');
-- offering 11 (PHY101) – LAB-style room, smaller capacity
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (214, '1', 'FAC-01', 'Lab-101',  'Sat 08:00-11:00',     20, 20, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (214, '2', 'FAC-02', 'Lab-102',  'Sat 11:00-14:00',     20, 20, 'OPEN');
-- offering 12 (EEE101) – LAB
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (215, '1', 'FAC-03', 'Lab-103',  'Sat 08:00-11:00',     20, 20, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (215, '2', 'FAC-04', 'Lab-104',  'Sat 11:00-14:00',     20, 20, 'OPEN');
-- offering 13 (CSE303)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (216, '1', 'FAC-05', 'Room-201', 'Sun-Tue 09:30-11:00',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (216, '2', 'FAC-06', 'Room-202', 'Mon-Wed 09:30-11:00',  30, 30, 'OPEN');
-- offering 14 (CSE304)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (217, '1', 'FAC-07', 'Room-203', 'Sun-Tue 11:00-12:30',  25, 25, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (217, '2', 'FAC-08', 'Room-204', 'Mon-Wed 11:00-12:30',  25, 25, 'OPEN');
-- offering 15 (CSE403)
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (218, '1', 'FAC-09', 'Room-301', 'Sun-Tue 12:30-14:00',  30, 30, 'OPEN');
INSERT INTO course_sections (offering_id, section_name, faculty_id, room_no, class_schedule,      max_capacity, available_seats, section_status) VALUES (218, '2', 'FAC-10', 'Room-302', 'Mon-Wed 12:30-14:00',  30, 30, 'OPEN');


-- =============================================================================
-- 11. SECTION_SCHEDULE  (30 rows -- sequence -> schedule_id 1..30)
--     One schedule row per section.  Reference date 2026-06-07 = first Sunday.
--     class_type CHECK: 'THEORY' or 'LAB'
--     day_of_week VARCHAR2(10): 'Wednesday'=9 chars (max in list) -- OK
--     FK: section_id -> course_sections.section_id (1..30 all exist)
-- =============================================================================
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (875,  'Sunday',    TIMESTAMP '2026-06-07 08:00:00', TIMESTAMP '2026-06-07 09:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (876,  'Monday',    TIMESTAMP '2026-06-08 08:00:00', TIMESTAMP '2026-06-08 09:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (877,  'Sunday',    TIMESTAMP '2026-06-07 09:30:00', TIMESTAMP '2026-06-07 11:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (878,  'Monday',    TIMESTAMP '2026-06-08 09:30:00', TIMESTAMP '2026-06-08 11:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (879,  'Tuesday',   TIMESTAMP '2026-06-09 08:00:00', TIMESTAMP '2026-06-09 09:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (880,  'Wednesday', TIMESTAMP '2026-06-10 08:00:00', TIMESTAMP '2026-06-10 09:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (881,  'Sunday',    TIMESTAMP '2026-06-07 11:00:00', TIMESTAMP '2026-06-07 12:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (882,  'Monday',    TIMESTAMP '2026-06-08 11:00:00', TIMESTAMP '2026-06-08 12:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (883,  'Tuesday',   TIMESTAMP '2026-06-09 09:30:00', TIMESTAMP '2026-06-09 11:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (884, 'Wednesday', TIMESTAMP '2026-06-10 09:30:00', TIMESTAMP '2026-06-10 11:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (885, 'Sunday',    TIMESTAMP '2026-06-07 12:30:00', TIMESTAMP '2026-06-07 14:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (886, 'Monday',    TIMESTAMP '2026-06-08 12:30:00', TIMESTAMP '2026-06-08 14:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (887, 'Tuesday',   TIMESTAMP '2026-06-09 11:00:00', TIMESTAMP '2026-06-09 12:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (888, 'Wednesday', TIMESTAMP '2026-06-10 11:00:00', TIMESTAMP '2026-06-10 12:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (889, 'Thursday',  TIMESTAMP '2026-06-11 08:00:00', TIMESTAMP '2026-06-11 09:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (890, 'Thursday',  TIMESTAMP '2026-06-11 09:30:00', TIMESTAMP '2026-06-11 11:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (891, 'Thursday',  TIMESTAMP '2026-06-11 11:00:00', TIMESTAMP '2026-06-11 12:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (892, 'Thursday',  TIMESTAMP '2026-06-11 12:30:00', TIMESTAMP '2026-06-11 14:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (893, 'Sunday',    TIMESTAMP '2026-06-07 14:00:00', TIMESTAMP '2026-06-07 15:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (894, 'Monday',    TIMESTAMP '2026-06-08 14:00:00', TIMESTAMP '2026-06-08 15:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (895, 'Saturday',  TIMESTAMP '2026-06-13 08:00:00', TIMESTAMP '2026-06-13 11:00:00', 'LAB');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (896, 'Saturday',  TIMESTAMP '2026-06-13 11:00:00', TIMESTAMP '2026-06-13 14:00:00', 'LAB');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (897, 'Saturday',  TIMESTAMP '2026-06-13 08:00:00', TIMESTAMP '2026-06-13 11:00:00', 'LAB');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (898, 'Saturday',  TIMESTAMP '2026-06-13 11:00:00', TIMESTAMP '2026-06-13 14:00:00', 'LAB');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (899, 'Tuesday',   TIMESTAMP '2026-06-09 12:30:00', TIMESTAMP '2026-06-09 14:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (900, 'Wednesday', TIMESTAMP '2026-06-10 12:30:00', TIMESTAMP '2026-06-10 14:00:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (901, 'Tuesday',   TIMESTAMP '2026-06-09 14:00:00', TIMESTAMP '2026-06-09 15:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (902, 'Wednesday', TIMESTAMP '2026-06-10 14:00:00', TIMESTAMP '2026-06-10 15:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (903, 'Thursday',  TIMESTAMP '2026-06-11 14:00:00', TIMESTAMP '2026-06-11 15:30:00', 'THEORY');
INSERT INTO section_schedule (section_id, day_of_week, start_time, end_time, class_type) VALUES (904, 'Thursday',  TIMESTAMP '2026-06-11 15:30:00', TIMESTAMP '2026-06-11 17:00:00', 'THEORY');


-- =============================================================================
-- 12. REGISTRATION_REQUESTS  (30 rows -- sequence -> request_id 1..30)
--     STU-XX requests ADD for section XX.  All APPROVED.
--     request_type CHECK: 'ADD'|'ADMIN-OVERRIDE'|'AUTO-ADVISE'|'DROP'|'FACULTY-ADVISE'
--     request_status CHECK: 'APPROVED'|'FAILED'|'PENDING'|'REJECTED'
--     FK: students_id -> students.users_user_id  (STU-01..30 all exist)
--     FK: section_id  -> course_sections.section_id (1..30 all exist)
--     FK: users_id    -> users.user_id            (STU-01..30 are valid users)
--     Request times stagger in 1-hour groups of 3.
-- =============================================================================
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-01', 875,  'STU-01', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 08:00:00', 'APPROVED', TIMESTAMP '2026-04-26 08:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-02', 876,  'STU-02', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 08:00:00', 'APPROVED', TIMESTAMP '2026-04-26 08:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-03', 877,  'STU-03', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 08:00:00', 'APPROVED', TIMESTAMP '2026-04-26 08:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-04', 878,  'STU-04', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 09:00:00', 'APPROVED', TIMESTAMP '2026-04-26 09:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-05', 879,  'STU-05', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 09:00:00', 'APPROVED', TIMESTAMP '2026-04-26 09:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-06', 880,  'STU-06', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 09:00:00', 'APPROVED', TIMESTAMP '2026-04-26 09:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-07', 881,  'STU-07', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 10:00:00', 'APPROVED', TIMESTAMP '2026-04-26 10:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-08', 882,  'STU-08', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 10:00:00', 'APPROVED', TIMESTAMP '2026-04-26 10:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-09', 883,  'STU-09', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 10:00:00', 'APPROVED', TIMESTAMP '2026-04-26 10:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-10', 884, 'STU-10', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 11:00:00', 'APPROVED', TIMESTAMP '2026-04-26 11:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-11', 885, 'STU-11', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 11:00:00', 'APPROVED', TIMESTAMP '2026-04-26 11:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-12', 886, 'STU-12', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 11:00:00', 'APPROVED', TIMESTAMP '2026-04-26 11:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-13', 887, 'STU-13', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 12:00:00', 'APPROVED', TIMESTAMP '2026-04-26 12:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-14', 888, 'STU-14', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 12:00:00', 'APPROVED', TIMESTAMP '2026-04-26 12:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-15', 889, 'STU-15', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 12:00:00', 'APPROVED', TIMESTAMP '2026-04-26 12:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-16', 890, 'STU-16', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 13:00:00', 'APPROVED', TIMESTAMP '2026-04-26 13:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-17', 891, 'STU-17', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 13:00:00', 'APPROVED', TIMESTAMP '2026-04-26 13:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-18', 892, 'STU-18', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 13:00:00', 'APPROVED', TIMESTAMP '2026-04-26 13:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-19', 893, 'STU-19', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 14:00:00', 'APPROVED', TIMESTAMP '2026-04-26 14:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-20', 894, 'STU-20', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 14:00:00', 'APPROVED', TIMESTAMP '2026-04-26 14:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-21', 895, 'STU-21', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 14:00:00', 'APPROVED', TIMESTAMP '2026-04-26 14:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-22', 896, 'STU-22', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 15:00:00', 'APPROVED', TIMESTAMP '2026-04-26 15:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-23', 897, 'STU-23', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 15:00:00', 'APPROVED', TIMESTAMP '2026-04-26 15:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-24', 898, 'STU-24', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 15:00:00', 'APPROVED', TIMESTAMP '2026-04-26 15:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-25', 899, 'STU-25', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 16:00:00', 'APPROVED', TIMESTAMP '2026-04-26 16:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-26', 900, 'STU-26', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 16:00:00', 'APPROVED', TIMESTAMP '2026-04-26 16:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-27', 901, 'STU-27', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 16:00:00', 'APPROVED', TIMESTAMP '2026-04-26 16:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-28', 902, 'STU-28', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 17:00:00', 'APPROVED', TIMESTAMP '2026-04-26 17:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-29', 903, 'STU-29', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 17:00:00', 'APPROVED', TIMESTAMP '2026-04-26 17:05:00', 'Approved within advising window');
INSERT INTO registration_requests (students_id, section_id, users_id, request_type, request_reason, request_time, request_status, processed_at, processed_note) VALUES ('STU-30', 904, 'STU-30', 'ADD', 'Course registration', TIMESTAMP '2026-04-26 17:00:00', 'APPROVED', TIMESTAMP '2026-04-26 17:05:00', 'Approved within advising window');


-- =============================================================================
-- 13. ENROLLMENTS  (30 rows -- sequence -> enrollment_id 1..30)
--     STU-XX enrolled in section XX (1:1 mapping, no UNIQUE violation).
--     UNIQUE: (students_id, section_id) -- all 30 pairs are distinct.
--     enrollment_source CHECK: 'ADMIN'|'AUTO'|'FACULTY'|'SELF'  -> 'SELF'
--     enrollment_status CHECK: 'DROPPED'|'ENROLLED'             -> 'ENROLLED'
--     FK: students_id   -> students.users_user_id  (STU-01..30)
--     FK: section_id    -> course_sections.section_id (1..30)
--     FK: users_user_id -> users.user_id  (actor = the student)
--     FK: users_user_id1-> users.user_id  (approver = ADMIN-01, optional)
--     NOTE: trg_decrement_seats fires on each row below, decrementing
--           course_sections.available_seats for the corresponding section by 1.
-- =============================================================================
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-01', 875,  TIMESTAMP '2026-04-26 08:05:00', 'STU-01', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-02', 876,  TIMESTAMP '2026-04-26 08:05:00', 'STU-02', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-03', 877,  TIMESTAMP '2026-04-26 08:05:00', 'STU-03', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-04', 878,  TIMESTAMP '2026-04-26 09:05:00', 'STU-04', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-05', 879,  TIMESTAMP '2026-04-26 09:05:00', 'STU-05', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-06', 880,  TIMESTAMP '2026-04-26 09:05:00', 'STU-06', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-07', 881,  TIMESTAMP '2026-04-26 10:05:00', 'STU-07', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-08', 882,  TIMESTAMP '2026-04-26 10:05:00', 'STU-08', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-09', 883,  TIMESTAMP '2026-04-26 10:05:00', 'STU-09', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-10', 884, TIMESTAMP '2026-04-26 11:05:00', 'STU-10', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-11', 885, TIMESTAMP '2026-04-26 11:05:00', 'STU-11', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-12', 886, TIMESTAMP '2026-04-26 11:05:00', 'STU-12', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-13', 887, TIMESTAMP '2026-04-26 12:05:00', 'STU-13', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-14', 888, TIMESTAMP '2026-04-26 12:05:00', 'STU-14', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-15', 889, TIMESTAMP '2026-04-26 12:05:00', 'STU-15', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-16', 890, TIMESTAMP '2026-04-26 13:05:00', 'STU-16', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-17', 891, TIMESTAMP '2026-04-26 13:05:00', 'STU-17', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-18', 892, TIMESTAMP '2026-04-26 13:05:00', 'STU-18', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-19', 893, TIMESTAMP '2026-04-26 14:05:00', 'STU-19', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-20', 894, TIMESTAMP '2026-04-26 14:05:00', 'STU-20', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-21', 895, TIMESTAMP '2026-04-26 14:05:00', 'STU-21', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-22', 896, TIMESTAMP '2026-04-26 15:05:00', 'STU-22', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-23', 897, TIMESTAMP '2026-04-26 15:05:00', 'STU-23', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-24', 898, TIMESTAMP '2026-04-26 15:05:00', 'STU-24', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-25', 899, TIMESTAMP '2026-04-26 16:05:00', 'STU-25', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-26', 900, TIMESTAMP '2026-04-26 16:05:00', 'STU-26', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-27', 901, TIMESTAMP '2026-04-26 16:05:00', 'STU-27', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-28', 902, TIMESTAMP '2026-04-26 17:05:00', 'STU-28', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-29', 903, TIMESTAMP '2026-04-26 17:05:00', 'STU-29', 'SELF', 'ENROLLED', 'ADMIN-01');
INSERT INTO enrollments (students_id, section_id, enrolled_at, users_user_id, enrollment_source, enrollment_status, users_user_id1) VALUES ('STU-30', 904, TIMESTAMP '2026-04-26 17:05:00', 'STU-30', 'SELF', 'ENROLLED', 'ADMIN-01');


-- =============================================================================
-- 14. SECTION_SEAT_HISTORY  (10 rows -- sequence -> seat_log_id 1..10)
--     These are MANUAL admin-initiated capacity initialization records,
--     separate from the 30 trigger-generated rows (change_reason='Trigger: seat
--     change') that were auto-inserted when the enrollments above were committed.
--     FK: sections_id    -> course_sections.section_id  (1..10, all exist)
--     FK: users_user_id  -> users.user_id               ('ADMIN-01' exists)
--     FK: request_id     -> registration_requests.request_id  (NULL = no request)
--     change_reason VARCHAR2(100): 'Admin capacity init' = 20 chars -- OK
-- =============================================================================
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (875,  0, 30, TIMESTAMP '2026-04-10 08:00:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (876,  0, 30, TIMESTAMP '2026-04-10 08:05:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (877,  0, 30, TIMESTAMP '2026-04-10 08:10:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (878,  0, 30, TIMESTAMP '2026-04-10 08:15:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (879,  0, 30, TIMESTAMP '2026-04-10 08:20:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (880,  0, 30, TIMESTAMP '2026-04-10 08:25:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (881,  0, 25, TIMESTAMP '2026-04-10 08:30:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (882,  0, 25, TIMESTAMP '2026-04-10 08:35:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (883,  0, 30, TIMESTAMP '2026-04-10 08:40:00', 'ADMIN-01', 'Admin capacity init', NULL);
INSERT INTO section_seat_history (sections_id, old_available_seats, new_available_seats, changed_at, users_user_id, change_reason, request_id) VALUES (884, 0, 30, TIMESTAMP '2026-04-10 08:45:00', 'ADMIN-01', 'Admin capacity init', NULL);


-- =============================================================================
-- 15. PROVENANCE_LOG  (30 rows -- sequence -> log_id 1..30)
--     Logs one INSERT event for each of the 30 enrollment rows above.
--     operation_type CHECK: 'ADD'|'APPROVE'|'AUTO-ADVISE'|'DELETE'|'DROP'|
--                           'INSERT'|'UPDATE'  -> 'INSERT'
--     why/where/how_provenance VARCHAR2(300): all kept under 40 chars -- OK
--     old_value / new_value are CLOB; EMPTY_CLOB() is safe for Oracle CLOBs.
--     FK: users_user_id -> users.user_id                  (STU-01..30)
--     FK: request_id    -> registration_requests.request_id (1..30 all exist)
-- =============================================================================
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '1',  'INSERT', 'STU-01', 'STUDENT', TIMESTAMP '2026-04-26 08:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 38);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '2',  'INSERT', 'STU-02', 'STUDENT', TIMESTAMP '2026-04-26 08:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 39);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '3',  'INSERT', 'STU-03', 'STUDENT', TIMESTAMP '2026-04-26 08:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 40);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '4',  'INSERT', 'STU-04', 'STUDENT', TIMESTAMP '2026-04-26 09:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 41);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '5',  'INSERT', 'STU-05', 'STUDENT', TIMESTAMP '2026-04-26 09:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 42);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '6',  'INSERT', 'STU-06', 'STUDENT', TIMESTAMP '2026-04-26 09:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 43);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '7',  'INSERT', 'STU-07', 'STUDENT', TIMESTAMP '2026-04-26 10:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 44);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '8',  'INSERT', 'STU-08', 'STUDENT', TIMESTAMP '2026-04-26 10:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 45);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '9',  'INSERT', 'STU-09', 'STUDENT', TIMESTAMP '2026-04-26 10:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 46);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '10', 'INSERT', 'STU-10', 'STUDENT', TIMESTAMP '2026-04-26 11:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 47);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '11', 'INSERT', 'STU-11', 'STUDENT', TIMESTAMP '2026-04-26 11:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 48);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '12', 'INSERT', 'STU-12', 'STUDENT', TIMESTAMP '2026-04-26 11:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 49);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '13', 'INSERT', 'STU-13', 'STUDENT', TIMESTAMP '2026-04-26 12:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 50);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '14', 'INSERT', 'STU-14', 'STUDENT', TIMESTAMP '2026-04-26 12:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 51);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '15', 'INSERT', 'STU-15', 'STUDENT', TIMESTAMP '2026-04-26 12:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 52);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '16', 'INSERT', 'STU-16', 'STUDENT', TIMESTAMP '2026-04-26 13:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 53);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '17', 'INSERT', 'STU-17', 'STUDENT', TIMESTAMP '2026-04-26 13:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 54);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '18', 'INSERT', 'STU-18', 'STUDENT', TIMESTAMP '2026-04-26 13:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 55);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '19', 'INSERT', 'STU-19', 'STUDENT', TIMESTAMP '2026-04-26 14:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 56);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '20', 'INSERT', 'STU-20', 'STUDENT', TIMESTAMP '2026-04-26 14:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 57);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '21', 'INSERT', 'STU-21', 'STUDENT', TIMESTAMP '2026-04-26 14:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 58);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '22', 'INSERT', 'STU-22', 'STUDENT', TIMESTAMP '2026-04-26 15:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 59);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '23', 'INSERT', 'STU-23', 'STUDENT', TIMESTAMP '2026-04-26 15:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 60);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '24', 'INSERT', 'STU-24', 'STUDENT', TIMESTAMP '2026-04-26 15:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 61);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '25', 'INSERT', 'STU-25', 'STUDENT', TIMESTAMP '2026-04-26 16:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 62);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '26', 'INSERT', 'STU-26', 'STUDENT', TIMESTAMP '2026-04-26 16:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 63);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '27', 'INSERT', 'STU-27', 'STUDENT', TIMESTAMP '2026-04-26 16:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 64);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '28', 'INSERT', 'STU-28', 'STUDENT', TIMESTAMP '2026-04-26 17:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 65);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '29', 'INSERT', 'STU-29', 'STUDENT', TIMESTAMP '2026-04-26 17:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 66);
INSERT INTO provenance_log (source_table, row_pk, operation_type, users_user_id, actor_role, event_time, why_provenance, where_provenance, how_provenance, old_value, new_value, request_id) VALUES ('enrollments', '30', 'INSERT', 'STU-30', 'STUDENT', TIMESTAMP '2026-04-26 17:05:00', 'Self-enrolled', 'enrollments', 'Self via advising', EMPTY_CLOB(), EMPTY_CLOB(), 67);


-- =============================================================================
-- 16. FACULTY_MESSAGES  (10 rows -- sequence -> message_id 1..10)
--     One message to each faculty member FAC-01..FAC-10.
--     status CHECK: 'UNREAD'|'READ'
--     FK: faculty_id -> faculty.user_id  (FAC-01..10 all exist)
--     body is CLOB; TO_CLOB() handles the literal-to-CLOB conversion safely.
-- =============================================================================
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-01', 'Summer 2026 Schedule Confirmed', TO_CLOB('Your section assignments for Summer 2026 have been finalized. Please review via the portal.'), 'UNREAD', 'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-02', 'Summer 2026 Schedule Confirmed', TO_CLOB('Your section assignments for Summer 2026 have been finalized. Please review via the portal.'), 'UNREAD', 'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-03', 'Summer 2026 Schedule Confirmed', TO_CLOB('Your section assignments for Summer 2026 have been finalized. Please review via the portal.'), 'UNREAD', 'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-04', 'Summer 2026 Schedule Confirmed', TO_CLOB('Your section assignments for Summer 2026 have been finalized. Please review via the portal.'), 'UNREAD', 'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-05', 'Enrollment Update - MAT101',    TO_CLOB('MAT101 Section A has 35 seats. Registration is now open for enrolled students.'),           'READ',   'Sent by ADMIN-02');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-06', 'Enrollment Update - CSE302',    TO_CLOB('CSE302 enrollment is live. Students may drop/add through May 10.'),                        'UNREAD', 'Sent by ADMIN-02');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-07', 'Room Assignment - PHY101',      TO_CLOB('PHY101 Section A is assigned to Lab-101 on Saturdays 08:00-11:00.'),                       'READ',   'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-08', 'Room Assignment - EEE101',      TO_CLOB('EEE101 Section B is assigned to Lab-104 on Saturdays 11:00-14:00.'),                       'UNREAD', 'Sent by ADMIN-01');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-09', 'Advising Reminder',             TO_CLOB('Advising window closes May 10. Please complete all student advising by that date.'),        'UNREAD', 'Sent by ADMIN-03');
INSERT INTO faculty_messages (faculty_id, subject, body, status, admin_note) VALUES ('FAC-10', 'Advising Reminder',             TO_CLOB('Advising window closes May 10. Please complete all student advising by that date.'),        'READ',   'Sent by ADMIN-03');


-- =============================================================================
COMMIT;
-- =============================================================================
