+import os
+import tempfile
+import unittest
+
+from src.database import Database
+from src.student import Student
+
+
+class TestDatabase(unittest.TestCase):
+    def setUp(self):
+        self.tmp = tempfile.TemporaryDirectory()
+        self.db_path = os.path.join(self.tmp.name, "test.db")
+        self.schema_path = os.path.join(
+            os.path.dirname(os.path.dirname(__file__)), "schema", "schema.sql"
+        )
+        self.db = Database(self.db_path, self.schema_path)
+        self.student = Student(self.db)
+
+    def tearDown(self):
+        self.tmp.cleanup()
+
+    def test_tables_exist(self):
+        rows = self.db.fetch_all(
+            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('students', 'courses', 'grades')"
+        )
+        names = {row["name"] for row in rows}
+        self.assertEqual({"students", "courses", "grades"}, names)
+
+    def test_unique_email_constraint(self):
+        self.student.add("Alice", "alice@example.com")
+        with self.assertRaises(ValueError):
+            self.student.add("Alice 2", "alice@example.com")
