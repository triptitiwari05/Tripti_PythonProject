import os
from src.database import Database
from src.student import Student
from src.course import Course
from src.grade import Grade
from src.reporter import Reporter


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "grades_system.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema", "schema.sql")


def prompt_int(label, allow_blank=False):
    while True:
        value = input(label).strip()
        if allow_blank and value == "":
            return None
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_float(label, allow_blank=False):
    while True:
        value = input(label).strip()
        if allow_blank and value == "":
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def print_students(students):
    if not students:
        print("No students found.")
        return
    for s in students:
        print(f"[{s['student_id']}] {s['name']} | {s['email']} | {s['enrollment_date']}")


def print_courses(courses):
    if not courses:
        print("No courses found.")
        return
    for c in courses:
        print(f"[{c['course_id']}] {c['course_name']} | Credits: {c['credits']} | {c['instructor']}")


def print_grades(rows):
    if not rows:
        print("No grade records found.")
        return
    for r in rows:
        print(
            f"[{r['grade_id']}] {r['name']} | {r['course_name']} | "
            f"Grade: {r['grade']} | Marks: {r['marks']}"
        )


def main():
    db = Database(DB_PATH, SCHEMA_PATH)
    student_service = Student(db)
    course_service = Course(db)
    grade_service = Grade(db)
    reporter = Reporter(db, grade_service)

    menu = """
Student Grade Management System
1. Add student
2. Add course
3. Enroll student in course
4. Record grades
5. Update grades
6. View grades
7. Student transcript
8. Class statistics
9. Grade distribution
10. Find students in a course
11. Search student by name
12. Filter by grade range
 13. List all students
 14. List all courses
0. Exit
"""

    while True:
        print(menu)
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                name = input("Student name: ")
                email = input("Student email: ")
                enrollment_date = input("Enrollment date (YYYY-MM-DD, blank for today): ").strip() or None
                student_id = student_service.add(name, email, enrollment_date)
                print(f"Student added with ID {student_id}.")

            elif choice == "2":
                course_name = input("Course name: ")
                credits = prompt_int("Credits: ")
                instructor = input("Instructor: ")
                course_id = course_service.add(course_name, credits, instructor)
                print(f"Course added with ID {course_id}.")

            elif choice == "3":
                print_students(student_service.list_all())
                student_id = prompt_int("Student ID: ")
                print_courses(course_service.list_all())
                course_id = prompt_int("Course ID: ")
                grade_id = grade_service.enroll_student(student_id, course_id)
                print(f"Enrollment created with grade record ID {grade_id}.")

            elif choice == "4":
                print_students(student_service.list_all())
                student_id = prompt_int("Student ID: ")
                print_courses(course_service.list_all())
                course_id = prompt_int("Course ID: ")
                grade = input("Grade (A/B/C/D/F): ")
                marks = prompt_float("Marks: ")
                grade_service.record_grade(student_id, course_id, grade, marks)
                print("Grade recorded.")

            elif choice == "5":
                grade_id = prompt_int("Grade record ID: ")
                grade = input("Grade (A/B/C/D/F, blank to keep): ").strip() or None
                marks = prompt_float("Marks (blank to keep): ", allow_blank=True)
                grade_service.update_grade(grade_id, grade, marks)
                print("Grade updated.")

            elif choice == "6":
                sub = input("View by (A)ll, (S)tudent, (C)ourse: ").strip().upper()
                if sub == "S":
                    student_id = prompt_int("Student ID: ")
                    rows = grade_service.view_grades(student_id=student_id)
                elif sub == "C":
                    course_id = prompt_int("Course ID: ")
                    rows = grade_service.view_grades(course_id=course_id)
                else:
                    rows = grade_service.view_grades()
                print_grades(rows)

            elif choice == "7":
                print_students(student_service.list_all())
                student_id = prompt_int("Student ID: ")
                student, grades, gpa = reporter.student_transcript(student_id)
                print(f"Transcript for {student['name']} ({student['email']})")
                if not grades:
                    print("No grades recorded yet.")
                else:
                    for row in grades:
                        print(
                            f"{row['course_name']} | Credits: {row['credits']} | "
                            f"Grade: {row['grade']} | Marks: {row['marks']}"
                        )
                print(f"GPA: {gpa}")

            elif choice == "8":
                print_courses(course_service.list_all())
                course_id = prompt_int("Course ID: ")
                stats = reporter.class_statistics(course_id)
                print(
                    f"Count: {stats['count']} | Avg: {stats['average']} | "
                    f"Min: {stats['min']} | Max: {stats['max']}"
                )

            elif choice == "9":
                print_courses(course_service.list_all())
                course_id = prompt_int("Course ID (blank for all): ", allow_blank=True)
                distribution = reporter.grade_distribution(course_id)
                if not distribution:
                    print("No grades found.")
                else:
                    for grade_key in sorted(distribution.keys()):
                        print(f"{grade_key}: {distribution[grade_key]}")

            elif choice == "10":
                print_courses(course_service.list_all())
                course_id = prompt_int("Course ID: ")
                rows = grade_service.find_students_in_course(course_id)
                if not rows:
                    print("No students found for this course.")
                else:
                    for row in rows:
                        print(f"[{row['student_id']}] {row['name']} | {row['email']}")

            elif choice == "11":
                name_query = input("Search name: ")
                rows = student_service.search_by_name(name_query)
                print_students(rows)

            elif choice == "12":
                min_grade = input("Minimum grade (A/B/C/D/F): ")
                max_grade = input("Maximum grade (A/B/C/D/F): ")
                rows, low, high = grade_service.filter_by_grade_range(min_grade, max_grade)
                if not rows:
                    print("No grades found in the specified range.")
                else:
                    print(f"Grade points range: {low} to {high}")
                    for row in rows:
                        print(
                            f"[{row['grade_id']}] {row['name']} | {row['course_name']} | "
                            f"Grade: {row['grade']} | Marks: {row['marks']}"
                        )

            elif choice == "13":
                print_students(student_service.list_all())

            elif choice == "14":
                print_courses(course_service.list_all())

            elif choice == "0":
                print("Goodbye.")
                break

            else:
                print("Invalid option. Please try again.")

        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
