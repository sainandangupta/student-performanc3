"""
Student Performance Analysis — Flask Application
"""

import os
from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, jsonify, session
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from models import db, User, Student, Subject, Mark, Attendance
from seed_data import seed_database

# ─── App factory ────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-performance-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_performance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─── Helper utilities ──────────────────────────────────────────────
def _student_performance(student):
    """Build a full performance dict for a single student."""
    subjects = Subject.query.filter_by(semester=student.semester).all()
    rows = []
    total_pct_sum = 0
    total_att_present = 0
    total_att_classes = 0
    best_subj = None
    best_pct = -1

    for subj in subjects:
        marks = {m.exam_type: m for m in Mark.query.filter_by(
            student_id=student.student_id, subject_id=subj.subject_id).all()}
        att = Attendance.query.filter_by(
            student_id=student.student_id, subject_id=subj.subject_id).first()

        internal = marks.get('internal')
        assignment = marks.get('assignment')
        external = marks.get('external')

        int_score = internal.score if internal else 0
        int_max = internal.max_score if internal else 30
        asgn_score = assignment.score if assignment else 0
        asgn_max = assignment.max_score if assignment else 20
        ext_score = external.score if external else 0
        ext_max = external.max_score if external else 50

        total_score = int_score + asgn_score + ext_score
        total_max = int_max + asgn_max + ext_max
        subj_pct = round((total_score / total_max) * 100, 1) if total_max else 0

        att_pct = att.percentage if att else 0
        present = att.classes_present if att else 0
        total_cls = att.total_classes if att else 0

        status = 'Pass' if subj_pct >= 40 and att_pct >= 75 else 'Fail'

        total_pct_sum += subj_pct
        total_att_present += present
        total_att_classes += total_cls

        if subj_pct > best_pct:
            best_pct = subj_pct
            best_subj = subj.name

        rows.append({
            'subject': subj.name,
            'subject_id': subj.subject_id,
            'internal': int_score,
            'internal_max': int_max,
            'assignment': asgn_score,
            'assignment_max': asgn_max,
            'external': ext_score,
            'external_max': ext_max,
            'total': total_score,
            'total_max': total_max,
            'percentage': subj_pct,
            'attendance_pct': att_pct,
            'present': present,
            'total_classes': total_cls,
            'status': status,
        })

    num_subjects = len(subjects)
    overall_pct = round(total_pct_sum / num_subjects, 1) if num_subjects else 0
    gpa = round(overall_pct / 10, 2)
    overall_att = round((total_att_present / total_att_classes) * 100, 1) if total_att_classes else 0

    return {
        'rows': rows,
        'overall_pct': overall_pct,
        'gpa': gpa,
        'overall_att': overall_att,
        'num_subjects': num_subjects,
        'best_subject': best_subj,
    }


# ─── Routes ────────────────────────────────────────────────────────

# Landing / Login
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.role != role:
                flash(f'This account is registered as {user.role}, not {role}.', 'danger')
                return render_template('login.html')
            login_user(user)
            flash('Logged in successfully!', 'success')
            if user.role == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        enrollment = request.form.get('enrollment', '').strip()
        branch = request.form.get('branch', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('login.html', show_register=True)
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('login.html', show_register=True)

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'student':
            student = Student(
                user_id=user.user_id,
                name=fullname,
                enrollment_no=enrollment,
                branch=branch,
                semester=1,
            )
            db.session.add(student)

        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('login.html', show_register=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


# ─── Student Dashboard ─────────────────────────────────────────────
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('faculty_dashboard'))

    student = current_user.student
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('login'))

    perf = _student_performance(student)
    return render_template('student_dashboard.html', student=student, perf=perf)


# ─── Data Entry (Student) ──────────────────────────────────────────
@app.route('/student/data-entry')
@login_required
def data_entry():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    student = current_user.student
    subjects = Subject.query.filter_by(semester=student.semester).all()
    return render_template('data_entry.html', student=student, subjects=subjects)


# ─── Performance Charts Page ───────────────────────────────────────
@app.route('/student/charts')
@login_required
def student_charts():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    student = current_user.student
    perf = _student_performance(student)
    return render_template('charts.html', student=student, perf=perf)


# ─── Faculty Dashboard ─────────────────────────────────────────────
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty':
        flash('Access denied.', 'danger')
        return redirect(url_for('student_dashboard'))

    students = Student.query.all()
    subjects = Subject.query.all()
    branches = sorted(set(s.branch for s in students))
    semesters = sorted(set(s.semester for s in students))

    # Build summary for each student
    student_summaries = []
    total_pct_sum = 0
    at_risk_count = 0
    subj_totals = {}

    for s in students:
        perf = _student_performance(s)
        overall = perf['overall_pct']
        att = perf['overall_att']
        total_pct_sum += overall

        # at-risk: overall <50% OR any subject attendance <60%
        is_at_risk = overall < 50
        for r in perf['rows']:
            if r['attendance_pct'] < 60:
                is_at_risk = True
            subj_totals.setdefault(r['subject'], []).append(r['percentage'])

        if is_at_risk:
            at_risk_count += 1

        student_summaries.append({
            'student': s,
            'overall_pct': overall,
            'attendance_pct': att,
            'status': 'At Risk' if is_at_risk else 'Good',
            'perf': perf,
        })

    # Sort by overall_pct descending for ranking
    student_summaries.sort(key=lambda x: x['overall_pct'], reverse=True)
    for i, ss in enumerate(student_summaries, 1):
        ss['rank'] = i

    class_avg = round(total_pct_sum / len(students), 1) if students else 0

    # Subject with lowest average
    lowest_subj = None
    lowest_avg = 999
    subj_averages = {}
    for sname, pcts in subj_totals.items():
        avg = round(sum(pcts) / len(pcts), 1)
        subj_averages[sname] = avg
        if avg < lowest_avg:
            lowest_avg = avg
            lowest_subj = sname

    below_40 = sum(1 for ss in student_summaries if ss['overall_pct'] < 40)

    return render_template('faculty_dashboard.html',
                           students_data=student_summaries,
                           total_students=len(students),
                           class_avg=class_avg,
                           at_risk=at_risk_count,
                           below_40=below_40,
                           lowest_subject=lowest_subj,
                           subjects=subjects,
                           branches=branches,
                           semesters=semesters,
                           subj_averages=subj_averages)


# ─── Faculty data entry ────────────────────────────────────────────
@app.route('/faculty/data-entry')
@login_required
def faculty_data_entry():
    if current_user.role != 'faculty':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))

    students = Student.query.all()
    subjects = Subject.query.all()
    return render_template('data_entry.html', student=None, subjects=subjects, students=students, is_faculty=True)


# ─── API Routes ────────────────────────────────────────────────────

@app.route('/api/marks/add', methods=['POST'])
@login_required
def api_add_marks():
    data = request.get_json() if request.is_json else request.form
    student_id = int(data.get('student_id', 0))
    subject_id = int(data.get('subject_id', 0))

    # Permissions check
    if current_user.role == 'student':
        if not current_user.student or current_user.student.student_id != student_id:
            return jsonify({'error': 'Unauthorized'}), 403

    for exam_type, max_field in [('internal', 30), ('assignment', 20), ('external', 50)]:
        score_val = float(data.get(f'{exam_type}_marks', 0))
        existing = Mark.query.filter_by(
            student_id=student_id, subject_id=subject_id, exam_type=exam_type
        ).first()
        if existing:
            existing.score = score_val
        else:
            mark = Mark(
                student_id=student_id,
                subject_id=subject_id,
                score=score_val,
                max_score=max_field,
                exam_type=exam_type,
            )
            db.session.add(mark)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Marks saved successfully!'})


@app.route('/api/attendance/add', methods=['POST'])
@login_required
def api_add_attendance():
    data = request.get_json() if request.is_json else request.form
    student_id = int(data.get('student_id', 0))
    subject_id = int(data.get('subject_id', 0))
    present = int(data.get('classes_present', 0))
    total = int(data.get('total_classes', 0))

    if current_user.role == 'student':
        if not current_user.student or current_user.student.student_id != student_id:
            return jsonify({'error': 'Unauthorized'}), 403

    existing = Attendance.query.filter_by(
        student_id=student_id, subject_id=subject_id
    ).first()
    if existing:
        existing.classes_present = present
        existing.total_classes = total
    else:
        att = Attendance(
            student_id=student_id,
            subject_id=subject_id,
            classes_present=present,
            total_classes=total,
        )
        db.session.add(att)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Attendance saved successfully!'})


@app.route('/api/student/<int:sid>/data')
@login_required
def api_student_data(sid):
    student = db.session.get(Student, sid)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    perf = _student_performance(student)
    return jsonify({
        'student': {
            'name': student.name,
            'enrollment_no': student.enrollment_no,
            'branch': student.branch,
            'semester': student.semester,
        },
        'performance': perf,
    })


@app.route('/api/class/data')
@login_required
def api_class_data():
    if current_user.role != 'faculty':
        return jsonify({'error': 'Unauthorized'}), 403

    students = Student.query.all()
    results = []
    for s in students:
        perf = _student_performance(s)
        results.append({
            'student_id': s.student_id,
            'name': s.name,
            'enrollment_no': s.enrollment_no,
            'branch': s.branch,
            'semester': s.semester,
            'overall_pct': perf['overall_pct'],
            'overall_att': perf['overall_att'],
            'subjects': perf['rows'],
        })
    return jsonify(results)


# ─── Gemini AI Routes ──────────────────────────────────────────────
from gemini_service import get_prediction, get_alerts, get_recommendations


def _get_student_and_perf():
    """Helper: get current student + performance (or by ?student_id for faculty)."""
    sid = request.args.get('student_id')
    if sid and current_user.role == 'faculty':
        student = db.session.get(Student, int(sid))
    elif current_user.role == 'student' and current_user.student:
        student = current_user.student
    else:
        return None, None
    if not student:
        return None, None
    return student, _student_performance(student)


@app.route('/predict')
@login_required
def predict():
    student, perf = _get_student_and_perf()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    result = get_prediction(student, perf)
    return jsonify(result)


@app.route('/alerts')
@login_required
def alerts():
    student, perf = _get_student_and_perf()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    result = get_alerts(student, perf)
    return jsonify(result)


@app.route('/recommendations')
@login_required
def recommendations():
    student, perf = _get_student_and_perf()
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    result = get_recommendations(student, perf)
    return jsonify(result)


# ─── Bootstrap ──────────────────────────────────────────────────────
with app.app_context():
    db.create_all()
    # Seed if empty
    if User.query.count() == 0:
        seed_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
