class Grade:
    GRADE_POINTS = {
        "A": 4,
        "B": 3,
        "C": 2,
        "D": 1,
        "F": 0,
    }
    MIN_MARKS = 0.0
    MAX_MARKS = 100.0

    def __init__(self, db):
        self.db = db

    def enroll_student(self, student_id, course_id):
        self._ensure_student_exists(student_id)
        self._ensure_course_exists(course_id)
        existing = self.db.fetch_one(
            "SELECT grade_id FROM grades WHERE student_id = ? AND course_id = ?",
            (student_id, course_id),
        )
        if existing:
            raise ValueError("Student is already enrolled in this course.")
        return self.db.execute(
            "INSERT INTO grades (student_id, course_id) VALUES (?, ?)",
            (student_id, course_id),
        )

    def record_grade(self, student_id, course_id, grade, marks):
        self._ensure_student_exists(student_id)
        self._ensure_course_exists(course_id)
        grade = self._parse_grade(grade)
        marks = self._parse_marks(marks)
        row = self.db.fetch_one(
            "SELECT grade_id FROM grades WHERE student_id = ? AND course_id = ?",
            (student_id, course_id),
        )
        if not row:
            raise ValueError("Student is not enrolled in this course.")
        self.db.execute(
            "UPDATE grades SET grade = ?, marks = ? WHERE student_id = ? AND course_id = ?",
            (grade, marks, student_id, course_id),
        )

    def update_grade(self, grade_id, grade=None, marks=None):
        row = self.db.fetch_one(
            "SELECT grade_id, grade, marks FROM grades WHERE grade_id = ?",
            (grade_id,),
        )
        if not row:
            raise ValueError("Grade record not found.")
        grade_value = grade if grade is not None else row["grade"]
        grade_value = self._parse_grade(grade_value, allow_blank=True)
        marks_value = marks if marks is not None else row["marks"]
        marks_value = self._parse_marks(marks_value, allow_blank=True)
        self.db.execute(
            "UPDATE grades SET grade = ?, marks = ? WHERE grade_id = ?",
            (grade_value, marks_value, grade_id),
        )

    def view_grades(self, student_id=None, course_id=None):
        conditions = []
        params = []
        if student_id is not None:
            conditions.append("g.student_id = ?")
            params.append(student_id)
        if course_id is not None:
            conditions.append("g.course_id = ?")
            params.append(course_id)
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        query = (
            "SELECT g.grade_id, s.student_id, s.name, c.course_id, c.course_name, "
            "c.credits, g.grade, g.marks "
            "FROM grades g "
            "JOIN students s ON s.student_id = g.student_id "
            "JOIN courses c ON c.course_id = g.course_id "
            f"{where_clause} "
            "ORDER BY s.name, c.course_name"
        )
        return self.db.fetch_all(query, params)

    def find_students_in_course(self, course_id):
        return self.db.fetch_all(
            "SELECT s.student_id, s.name, s.email "
            "FROM grades g "
            "JOIN students s ON s.student_id = g.student_id "
            "WHERE g.course_id = ? "
            "ORDER BY s.name",
            (course_id,),
        )

    def filter_by_grade_range(self, min_grade, max_grade):
        min_grade = self._parse_grade(min_grade)
        max_grade = self._parse_grade(max_grade)
        min_points = self.GRADE_POINTS[min_grade]
        max_points = self.GRADE_POINTS[max_grade]
        low = min(min_points, max_points)
        high = max(min_points, max_points)
        rows = self.db.fetch_all(
            "SELECT g.grade_id, s.name, c.course_name, g.grade, g.marks "
            "FROM grades g "
            "JOIN students s ON s.student_id = g.student_id "
            "JOIN courses c ON c.course_id = g.course_id "
            "WHERE g.grade IS NOT NULL",
        )
        filtered = []
        for row in rows:
            points = self.GRADE_POINTS.get((row["grade"] or "").upper())
            if points is None:
                continue
            if low <= points <= high:
                filtered.append(row)
        return filtered, low, high

    def calculate_gpa(self, student_id):
        self._ensure_student_exists(student_id)
        rows = self.db.fetch_all(
            "SELECT c.credits, g.grade "
            "FROM grades g "
            "JOIN courses c ON c.course_id = g.course_id "
            "WHERE g.student_id = ? AND g.grade IS NOT NULL",
            (student_id,),
        )
        total_points = 0.0
        total_credits = 0
        for row in rows:
            grade = (row["grade"] or "").upper()
            if grade not in self.GRADE_POINTS:
                continue
            credits = int(row["credits"])
            total_credits += credits
            total_points += self.GRADE_POINTS[grade] * credits
        if total_credits == 0:
            return 0.0
        return round(total_points / total_credits, 2)

    def _ensure_student_exists(self, student_id):
        row = self.db.fetch_one(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,),
        )
        if not row:
            raise ValueError("Student not found.")

    def _ensure_course_exists(self, course_id):
        row = self.db.fetch_one(
            "SELECT course_id FROM courses WHERE course_id = ?",
            (course_id,),
        )
        if not row:
            raise ValueError("Course not found.")

    def _parse_grade(self, value, allow_blank=False):
        if value is None and allow_blank:
            return None
        grade = (value or "").strip().upper()
        if allow_blank and grade == "":
            return None
        if grade not in self.GRADE_POINTS:
            raise ValueError("Grade must be one of A, B, C, D, F.")
        return grade

    def _parse_marks(self, value, allow_blank=False):
        if value is None and allow_blank:
            return None
        if value is None:
            raise ValueError("Marks are required.")
        try:
            marks = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Marks must be a valid number.") from exc
        if not (self.MIN_MARKS <= marks <= self.MAX_MARKS):
            raise ValueError("Marks must be between 0 and 100.")
        return round(marks, 2)
