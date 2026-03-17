class Course:
    def __init__(self, db):
        self.db = db

    def add(self, course_name, credits, instructor):
        course_name = (course_name or "").strip()
        instructor = (instructor or "").strip()
        if not course_name:
            raise ValueError("Course name is required.")
        if not instructor:
            raise ValueError("Instructor is required.")
        credits = self._parse_credits(credits)
        return self.db.execute(
            "INSERT INTO courses (course_name, credits, instructor) VALUES (?, ?, ?)",
            (course_name, int(credits), instructor),
        )

    def update(self, course_id, course_name=None, credits=None, instructor=None):
        course = self.get_by_id(course_id)
        if not course:
            raise ValueError("Course not found.")
        course_name = (course_name if course_name is not None else course["course_name"]).strip()
        instructor = (instructor if instructor is not None else course["instructor"]).strip()
        credits = self._parse_credits(credits if credits is not None else course["credits"])
        if not course_name:
            raise ValueError("Course name is required.")
        if not instructor:
            raise ValueError("Instructor is required.")
        self.db.execute(
            "UPDATE courses SET course_name = ?, credits = ?, instructor = ? WHERE course_id = ?",
            (course_name, credits, instructor, course_id),
        )

    def delete(self, course_id):
        self.db.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))

    def get_by_id(self, course_id):
        return self.db.fetch_one(
            "SELECT course_id, course_name, credits, instructor FROM courses WHERE course_id = ?",
            (course_id,),
        )

    def list_all(self):
        return self.db.fetch_all(
            "SELECT course_id, course_name, credits, instructor FROM courses ORDER BY course_name"
        )

    @staticmethod
    def _parse_credits(value):
        if value is None:
            raise ValueError("Credits are required.")
        try:
            credits = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Credits must be a positive integer.") from exc
        if credits <= 0:
            raise ValueError("Credits must be a positive integer.")
        return credits
