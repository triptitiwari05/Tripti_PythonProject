#  Tutorial: Student Grade Management System

This guide explains how to set up and run the project.

---

##  1. Overview

This is a Python + SQLite based system to manage:

* Students
* Courses
* Grades
* GPA and reports

---

##  2. Requirements

* Python 3.8 or higher
* VS Code (recommended)

Check Python:

```bash
python --version
```

---

##  3. Setup

### Clone the repository

```bash
git clone https://github.com/your-username/student-grade-system.git
cd student-grade-system
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the project

```bash
python main.py
```

---

##  4. Features

* Add students and courses
* Enroll students
* Record and update grades
* View transcripts
* Calculate GPA
* View class statistics

---

##  5. Example Menu

```bash
Student Grade Management System

1 Add Student
2 Add Course
3 Enroll Student
4 Record Grade
5 View Transcript
6 Calculate GPA
7 Class Statistics
8 Exit
```

---

##  6. How It Works

* Uses SQLite database
* Tables: Students, Courses, Grades
* Operations: INSERT, UPDATE, SELECT, JOIN

---

##  7. Notes

* Ensure `grades_system.db` is inside `data/`
* Use correct IDs while entering data

---

##  Author

Tripti Arun Tiwari
BCA - Sinhgad college of commerce
