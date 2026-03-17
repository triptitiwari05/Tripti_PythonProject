+import os
+import tempfile
+import unittest
+
+from src.database import Database
+from src.student import Student
+from src.course import Course
+from src.grade import Grade
+from src.reporter import Reporter
+
+
+class TestQueries(unittest.TestCase):
+    def setUp(self):
+        self.tmp = tempfile.TemporaryDirectory()
+        self.db_path = os.path.join(self.tmp.name, "test.db")
+        self.schema_path = os.path.join(
+            os.path.dirname(os.path.dirname(__file__)), "schema", "schema.sql"
+        )
+        self.db = Database(self.db_path, self.schema_path)
+        self.student = Student(self.db)
+        self.course = Course(self.db)
+        self.grade = Grade(self.db)
+        self.reporter = Reporter(self.db, self.grade)
+
+        self.s1 = self.student.add("Alice Johnson", "alice@example.com")
+        self.s2 = self.student.add("Alicia Brown", "alicia@example.com")
+        self.c1 = self.course.add("Science", 4, "Dr. Green")
+        self.c2 = self.course.add("History", 2, "Dr. Gray")
+        self.grade.enroll_student(self.s1, self.c1)
+        self.grade.enroll_student(self.s2, self.c1)
+        self.grade.enroll_student(self.s1, self.c2)
+        self.grade.record_grade(self.s1, self.c1, "A", 95)
+        self.grade.record_grade(self.s2, self.c1, "C", 75)
+        self.grade.record_grade(self.s1, self.c2, "B", 88)
+
+    def tearDown(self):
+        self.tmp.cleanup()
+
+    def test_search_by_name(self):
+        rows = self.student.search_by_name("Ali")
+        names = [row["name"] for row in rows]
+        self.assertIn("Alice Johnson", names)
+        self.assertIn("Alicia Brown", names)
+
+    def test_find_students_in_course(self):
+        rows = self.grade.find_students_in_course(self.c1)
+        ids = {row["student_id"] for row in rows}
+        self.assertEqual({self.s1, self.s2}, ids)
+
+    def test_filter_by_grade_range(self):
+        rows, low, high = self.grade.filter_by_grade_range("A", "B")
+        self.assertEqual((3, 4), (low, high))
+        grades = {row["grade"] for row in rows}
+        self.assertTrue("A" in grades or "B" in grades)
+
+    def test_reporter_stats_and_distribution(self):
+        stats = self.reporter.class_statistics(self.c1)
+        self.assertEqual(2, stats["count"])
+        distribution = self.reporter.grade_distribution(self.c1)
+        self.assertEqual(1, distribution.get("A"))
+        self.assertEqual(1, distribution.get("C"))
