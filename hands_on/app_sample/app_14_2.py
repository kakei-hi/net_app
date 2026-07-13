import os
import re

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, inspect, or_, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DATABASE_PATH = os.path.join(INSTANCE_DIR, 'app_14_2_grades.db')

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    instance_path=INSTANCE_DIR,
)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

csrf = CSRFProtect(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)

STUDENT_NUMBER_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9-]{2,19}$')


class Department(db.Model):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    students: Mapped[list['Student']] = relationship(back_populates='department')


class Course(db.Model):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    grades: Mapped[list['Grade']] = relationship(back_populates='course')


class Student(db.Model):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    department: Mapped['Department'] = relationship(back_populates='students')
    grades: Mapped[list['Grade']] = relationship(back_populates='student')


class Grade(db.Model):
    __tablename__ = 'grades'
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='uq_grade_student_course'),
        CheckConstraint('score >= 0 AND score <= 100', name='ck_grade_score_range'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    score: Mapped[int | None] = mapped_column(nullable=True)

    student: Mapped['Student'] = relationship(back_populates='grades')
    course: Mapped['Course'] = relationship(back_populates='grades')


def get_departments() -> list[Department]:
    return list(db.session.scalars(select(Department).order_by(Department.name)))


def get_courses() -> list[Course]:
    return list(db.session.scalars(select(Course).order_by(Course.name)))


def get_students(keyword: str = '') -> list[Student]:
    stmt = (
        select(Student)
        .options(selectinload(Student.department), selectinload(Student.grades).selectinload(Grade.course))
        .order_by(Student.student_number)
    )
    cleaned_keyword = keyword.strip()
    if cleaned_keyword:
        stmt = stmt.where(
            or_(
                Student.student_number.ilike(f'%{cleaned_keyword}%'),
                Student.name.ilike(f'%{cleaned_keyword}%'),
            )
        )
    return list(db.session.scalars(stmt).unique())


def get_student(student_id: int) -> Student | None:
    stmt = (
        select(Student)
        .options(
            selectinload(Student.department),
            selectinload(Student.grades).selectinload(Grade.course),
        )
        .where(Student.id == student_id)
    )
    return db.session.scalar(stmt)


def get_student_grade(student_id: int, course_id: int) -> Grade | None:
    stmt = select(Grade).where(Grade.student_id == student_id, Grade.course_id == course_id)
    return db.session.scalar(stmt)


def validate_search_keyword(keyword: str) -> str | None:
    cleaned_keyword = keyword.strip()
    if not cleaned_keyword:
        return '検索キーワードを入力してください。'
    if len(cleaned_keyword) > 50:
        return '検索キーワードは50文字以内で入力してください。'
    return None


def validate_score(score_raw: str) -> tuple[int | None, str | None]:
    cleaned_score = score_raw.strip()
    if not cleaned_score:
        return None, '成績は必須です。'
    if not cleaned_score.isdigit():
        return None, '成績は0以上100以下の整数で入力してください。'

    score = int(cleaned_score)
    if score < 0 or score > 100:
        return None, '成績は0以上100以下で入力してください。'
    return score, None


def get_grade_rows(student: Student) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for grade in sorted(student.grades, key=lambda item: item.course.name):
        rows.append({
            'course': grade.course,
            'grade': grade,
            'has_grade': grade.score is not None,
        })

    return rows


def get_available_courses(student: Student) -> list[Grade]:
    return [grade for grade in sorted(student.grades, key=lambda item: item.course.name) if grade.score is None]


def get_grading_target(student: Student, course_id_raw: str, available_courses: list[Grade]) -> tuple[Grade | None, str | None]:
    cleaned_course_id = course_id_raw.strip()
    if not cleaned_course_id:
        return None, '履修科目を選択してください。'
    if not cleaned_course_id.isdigit():
        return None, '履修科目の値が不正です。'

    course_id = int(cleaned_course_id)
    for grade in available_courses:
        if grade.course_id == course_id:
            return grade, None
    return None, '選択した履修科目は登録対象ではありません。'


def ensure_grade_rows() -> None:
    students = list(db.session.scalars(select(Student).options(selectinload(Student.grades))))
    courses = get_courses()

    existing_pairs = {
        (grade.student_id, grade.course_id)
        for student in students
        for grade in student.grades
    }

    new_rows: list[Grade] = []
    for student in students:
        for course in courses:
            if (student.id, course.id) in existing_pairs:
                continue
            new_rows.append(Grade(student_id=student.id, course_id=course.id, score=None))

    if new_rows:
        db.session.add_all(new_rows)
        db.session.commit()


@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('keyword', '')
    search_error = None
    students = get_students()

    if 'keyword' in request.args:
        search_error = validate_search_keyword(keyword)
        if search_error is None:
            students = get_students(keyword)
        else:
            students = []

    return render_template(
        'app_14_2_index.html',
        students=students,
        keyword=keyword,
        search_error=search_error,
    )


@app.route('/students/<int:student_id>/grades', methods=['GET'])
def student_grades(student_id: int):
    student = get_student(student_id)
    if student is None:
        flash('対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    return render_template(
        'app_14_2_student_grades.html',
        student=student,
        grade_rows=get_grade_rows(student),
    )


@app.route('/students/<int:student_id>/grades/new', methods=['GET', 'POST'])
def register_grade(student_id: int):
    student = get_student(student_id)
    if student is None:
        flash('対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    available_grades = get_available_courses(student)
    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('student_grades', student_id=student_id))

        grade, course_error = get_grading_target(student, request.form.get('course_id', ''), available_grades)
        score, score_error = validate_score(request.form.get('score', ''))

        errors = [error for error in [course_error, score_error] if error is not None]
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register_grade', student_id=student_id))

        if grade is None or score is None:
            flash('成績の登録に失敗しました。', 'error')
            return redirect(url_for('register_grade', student_id=student_id))

        grade.score = score
        db.session.commit()
        flash(f'学生 {student.name} の {grade.course.name} の成績を登録しました。', 'success')
        return redirect(url_for('student_grades', student_id=student_id))

    selected_course_id = request.args.get('course_id', type=int)
    return render_template(
        'app_14_2_grade_register.html',
        student=student,
        available_courses=available_grades,
        selected_course_id=selected_course_id,
    )


@app.route('/students/<int:student_id>/grades/<int:course_id>/edit', methods=['GET', 'POST'])
def edit_grade(student_id: int, course_id: int):
    student = get_student(student_id)
    if student is None:
        flash('対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    grade = get_student_grade(student_id, course_id)
    if grade is None:
        flash('修正対象の成績が見つかりません。', 'error')
        return redirect(url_for('student_grades', student_id=student_id))

    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            return redirect(url_for('student_grades', student_id=student_id))

        score, score_error = validate_score(request.form.get('score', ''))
        if score_error is not None:
            flash(score_error, 'error')
            return redirect(url_for('edit_grade', student_id=student_id, course_id=course_id))

        grade.score = score
        db.session.commit()
        flash(f'学生 {student.name} の {grade.course.name} の成績を修正しました。', 'success')
        return redirect(url_for('student_grades', student_id=student_id))

    return render_template(
        'app_14_2_grade_edit.html',
        student=student,
        grade=grade,
    )


def seed_data() -> None:
    if db.session.scalar(select(db.func.count(Department.id))) == 0:
        db.session.add_all([
            Department(name='工学部'),
            Department(name='理学部'),
            Department(name='文学部'),
        ])

    if db.session.scalar(select(db.func.count(Course.id))) == 0:
        db.session.add_all([
            Course(name='プログラミング演習'),
            Course(name='データベース論'),
            Course(name='離散数学'),
        ])

    db.session.flush()

    if db.session.scalar(select(db.func.count(Student.id))) == 0:
        departments = {department.name: department for department in db.session.scalars(select(Department)).all()}
        courses = {course.name: course for course in db.session.scalars(select(Course)).all()}

        students = [
            Student(student_number='K25001', name='徳島 太郎', department_id=departments['工学部'].id),
            Student(student_number='K25002', name='佐藤 花子', department_id=departments['理学部'].id),
            Student(student_number='K25003', name='山田 次郎', department_id=departments['文学部'].id),
        ]
        db.session.add_all(students)
        db.session.flush()

        students_by_number = {student.student_number: student for student in students}

        db.session.add_all([
            Grade(student_id=students_by_number['K25001'].id, course_id=courses['プログラミング演習'].id, score=88),
            Grade(student_id=students_by_number['K25001'].id, course_id=courses['データベース論'].id, score=91),
            Grade(student_id=students_by_number['K25001'].id, course_id=courses['離散数学'].id, score=None),
            Grade(student_id=students_by_number['K25002'].id, course_id=courses['データベース論'].id, score=75),
            Grade(student_id=students_by_number['K25002'].id, course_id=courses['離散数学'].id, score=None),
            Grade(student_id=students_by_number['K25003'].id, course_id=courses['離散数学'].id, score=None),
        ])

    db.session.commit()


def migrate_student_courses_to_grades() -> None:
    inspector = inspect(db.engine)
    if 'student_courses' not in inspector.get_table_names():
        return

    existing_grade_pairs = {
        (student_id, course_id)
        for student_id, course_id in db.session.execute(
            select(Grade.student_id, Grade.course_id)
        )
    }

    for student_id, course_id in db.session.execute(text('SELECT student_id, course_id FROM student_courses')):
        if (student_id, course_id) in existing_grade_pairs:
            continue
        db.session.add(Grade(student_id=student_id, course_id=course_id, score=None))

    db.session.commit()
    db.session.execute(text('DROP TABLE student_courses'))
    db.session.commit()


if __name__ == '__main__':
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    with app.app_context():
        db.create_all()
        migrate_student_courses_to_grades()
        seed_data()
        ensure_grade_rows()

    app.run(debug=True)
