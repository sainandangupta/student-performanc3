"""
Seed data script — populates the database with sample students, subjects, marks, and attendance.
Run this after creating the database tables.
"""

import random
from models import db, User, Student, Subject, Mark, Attendance


def seed_database():
    """Pre-populate the database with sample data."""

    # ── Faculty account ──────────────────────────────────────────────
    faculty_user = User(username='faculty1', email='faculty1@college.edu', role='faculty')
    faculty_user.set_password('faculty123')
    db.session.add(faculty_user)

    # ── Subjects (Semester 1) ────────────────────────────────────────
    subjects_data = [
        {'name': 'Mathematics',            'semester': 1, 'max_marks': 100},
        {'name': 'Python Programming',     'semester': 1, 'max_marks': 100},
        {'name': 'Data Structures',        'semester': 1, 'max_marks': 100},
        {'name': 'English Communication',  'semester': 1, 'max_marks': 100},
        {'name': 'Physics',                'semester': 1, 'max_marks': 100},
        {'name': 'Computer Networks',      'semester': 1, 'max_marks': 100},
    ]

    subjects = []
    for sd in subjects_data:
        subj = Subject(**sd)
        db.session.add(subj)
        subjects.append(subj)

    db.session.flush()  # get IDs before FK usage

    # ── Students ─────────────────────────────────────────────────────
    student_names = [
        ('Aarav Sharma',    'CSE'),
        ('Priya Patel',     'CSE'),
        ('Rohan Gupta',     'CSE'),
        ('Sneha Reddy',     'CSE'),
        ('Vikram Singh',    'CSE'),
        ('Ananya Iyer',     'CSE'),
        ('Karthik Nair',    'CSE'),
        ('Meera Joshi',     'AIML'),
        ('Arjun Kumar',     'AIML'),
        ('Divya Menon',     'AIML'),
        ('Rahul Verma',     'AIML'),
        ('Pooja Desai',     'AIML'),
        ('Siddharth Rao',   'AIML'),
        ('Neha Agarwal',    'AIML'),
        ('Aditya Chauhan',  'AIML'),
    ]

    students = []
    for idx, (name, branch) in enumerate(student_names, start=1):
        uname = f'student{idx}'
        user = User(username=uname, email=f'{uname}@college.edu', role='student')
        user.set_password(f'student{idx}23' if idx > 1 else 'student123')
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.user_id,
            name=name,
            enrollment_no=f'EN2024{idx:03d}',
            branch=branch,
            semester=1,
        )
        db.session.add(student)
        students.append(student)

    db.session.flush()

    # ── Marks & Attendance ───────────────────────────────────────────
    random.seed(42)  # reproducible
    for student in students:
        for subj in subjects:
            internal = random.randint(10, 30)   # max 30
            assignment = random.randint(5, 20)  # max 20
            external = random.randint(15, 50)   # max 50

            for exam_type, score, max_s in [
                ('internal',   internal,   30),
                ('assignment', assignment, 20),
                ('external',   external,   50),
            ]:
                mark = Mark(
                    student_id=student.student_id,
                    subject_id=subj.subject_id,
                    score=score,
                    max_score=max_s,
                    exam_type=exam_type,
                )
                db.session.add(mark)

            total_cls = random.randint(30, 45)
            present = random.randint(int(total_cls * 0.55), total_cls)
            att = Attendance(
                student_id=student.student_id,
                subject_id=subj.subject_id,
                classes_present=present,
                total_classes=total_cls,
            )
            db.session.add(att)

    db.session.commit()
    print('[OK] Database seeded with 15 students, 6 subjects, marks & attendance.')
