import re
from datetime import date, datetime

class Student:
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, db):
        self.db = db

    def add(self, name, email, enrollment_date=None):
        name = (name or "").strip()
        email = (email or "").strip()
        if not name:
            raise ValueError("Name is required.")
        if not email or not self.EMAIL_PATTERN.match(email):
            raise ValueError("Valid email is required.")
        if enrollment_date is None:
            enrollment_date = date.today().isoformat()
        else:
            self._validate_date(enrollment_date)
        return self.db.execute(
            "INSERT INTO students (name, email, enrollment_date) VALUES (?, ?, ?)",
            (name, email, enrollment_date),
        )

    def update(self, student_id, name=None, email=None):
        student = self.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found.")
        name = (name if name is not None else student["name"]).strip()
        email = (email if email is not None else student["email"]).strip()
        if not name:
            raise ValueError("Name is required.")
        if not self.EMAIL_PATTERN.match(email):
            raise ValueError("Valid email is required.")
        self.db.execute(
            "UPDATE students SET name = ?, email = ? WHERE student_id = ?",
            (name, email, student_id),
        )

    def delete(self, student_id):
        self.db.execute("DELETE FROM students WHERE student_id = ?", (student_id,))

    def get_by_id(self, student_id):
        return self.db.fetch_one(
            "SELECT student_id, name, email, enrollment_date FROM students WHERE student_id = ?",
            (student_id,),
        )

    def search_by_name(self, name_query):
        name_query = (name_query or "").strip()
        return self.db.fetch_all(
            "SELECT student_id, name, email, enrollment_date "
            "FROM students "
            "WHERE name LIKE ? COLLATE NOCASE "
            "ORDER BY name",
            (f"%{name_query}%",),
        )

    def list_all(self):
        return self.db.fetch_all(
            "SELECT student_id, name, email, enrollment_date FROM students ORDER BY name"
        )

    @staticmethod
    def _validate_date(value):
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Enrollment date must be in YYYY-MM-DD format.") from exc
