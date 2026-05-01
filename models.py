"""
SQLAlchemy models for the Student Performance Analysis application.
Defines Users, Students, Subjects, Marks, and Attendance tables.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication (students and faculty)."""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student / faculty

    # Relationship
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    """Student profile linked to a User."""
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    enrollment_no = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    marks = db.relationship('Mark', backref='student', lazy=True)
    attendance = db.relationship('Attendance', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}>'


class Subject(db.Model):
    """Subject/course information."""
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False, default=100)

    # Relationships
    marks = db.relationship('Mark', backref='subject', lazy=True)
    attendance = db.relationship('Attendance', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'


class Mark(db.Model):
    """Marks/scores for a student in a subject."""
    __tablename__ = 'marks'

    mark_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    score = db.Column(db.Float, nullable=False, default=0)
    max_score = db.Column(db.Float, nullable=False, default=100)
    exam_type = db.Column(db.String(20), nullable=False)  # internal / external / assignment

    # Unique constraint: one entry per student-subject-exam_type
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'exam_type', name='uq_student_subject_exam'),
    )

    def __repr__(self):
        return f'<Mark S{self.student_id} Sub{self.subject_id} {self.exam_type}: {self.score}>'


class Attendance(db.Model):
    """Attendance record for a student in a subject."""
    __tablename__ = 'attendance'

    att_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    classes_present = db.Column(db.Integer, nullable=False, default=0)
    total_classes = db.Column(db.Integer, nullable=False, default=0)

    # Unique constraint: one record per student-subject
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_att'),
    )

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.classes_present / self.total_classes) * 100, 1)

    def __repr__(self):
        return f'<Attendance S{self.student_id} Sub{self.subject_id}: {self.classes_present}/{self.total_classes}>'
