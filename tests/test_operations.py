+import os
+import tempfile
+import unittest
+
+from src.database import Database
+from src.student import Student
+from src.course import Course
+from src.grade import Grade
+
+
+class TestOperations(unittest.TestCase):
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
+
+    def tearDown(self):
+        self.tmp.cleanup()
+
+    def test_enroll_record_update_and_gpa(self):
+        student_id = self.student.add("Bob", "bob@example.com")
+        course_id = self.course.add("Math", 3, "Dr. Stone")
+        grade_id = self.grade.enroll_student(student_id, course_id)
+        self.assertIsInstance(grade_id, int)
+
+        self.grade.record_grade(student_id, course_id, "A", 92)
+        gpa = self.grade.calculate_gpa(student_id)
+        self.assertEqual(4.0, gpa)
+
+        self.grade.update_grade(grade_id, "B", 85)
+        gpa = self.grade.calculate_gpa(student_id)
+        self.assertEqual(3.0, gpa)
