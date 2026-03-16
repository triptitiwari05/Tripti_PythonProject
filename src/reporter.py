from collections import Counter


class Reporter:
    def __init__(self, db, grade_service):
        self.db = db
        self.grade_service = grade_service

    def student_transcript(self, student_id):
        student = self.db.fetch_one(
            "SELECT student_id, name, email, enrollment_date FROM students WHERE student_id = ?",
            (student_id,),
        )
        if not student:
            raise ValueError("Student not found.")
        grades = self.db.fetch_all(
            "SELECT c.course_name, c.credits, g.grade, g.marks "
            "FROM grades g "
            "JOIN courses c ON c.course_id = g.course_id "
            "WHERE g.student_id = ? "
            "ORDER BY c.course_name",
            (student_id,),
        )
        gpa = self.grade_service.calculate_gpa(student_id)
        return student, grades, gpa

    def class_statistics(self, course_id):
        if not self._course_exists(course_id):
            raise ValueError("Course not found.")
        rows = self.db.fetch_all(
            "SELECT g.marks, g.grade "
            "FROM grades g "
            "WHERE g.course_id = ? AND g.marks IS NOT NULL",
            (course_id,),
        )
        if not rows:
            return {
                "count": 0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
            }
        marks = [float(row["marks"]) for row in rows]
        return {
            "count": len(marks),
            "average": round(sum(marks) / len(marks), 2),
            "min": round(min(marks), 2),
            "max": round(max(marks), 2),
        }

    def grade_distribution(self, course_id=None):
        params = []
        where_clause = ""
        if course_id is not None:
            if not self._course_exists(course_id):
                raise ValueError("Course not found.")
            where_clause = "WHERE course_id = ?"
            params.append(course_id)
        rows = self.db.fetch_all(
            f"SELECT grade FROM grades {where_clause}",
            params,
        )
        counter = Counter()
        for row in rows:
            grade = (row["grade"] or "").upper()
            if grade:
                counter[grade] += 1
        return dict(counter)

    def _course_exists(self, course_id):
        row = self.db.fetch_one(
            "SELECT course_id FROM courses WHERE course_id = ?",
            (course_id,),
        )
        return bool(row)
