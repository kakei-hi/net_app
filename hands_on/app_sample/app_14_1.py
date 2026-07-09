import os
import re

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import ForeignKey, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DATABASE_PATH = os.path.join(INSTANCE_DIR, 'app_14_1_students.db')

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


class StudentCourse(db.Model):
    __tablename__ = 'student_courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)


class Course(db.Model):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    students: Mapped[list['Student']] = relationship(
        secondary='student_courses',
        back_populates='courses'
    )


class Student(db.Model):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    department: Mapped['Department'] = relationship(back_populates='students')
    courses: Mapped[list['Course']] = relationship(
        secondary='student_courses',
        back_populates='students'
    )


def get_departments() -> list[Department]:
    return list(db.session.scalars(select(Department).order_by(Department.name)))


def get_courses() -> list[Course]:
    return list(db.session.scalars(select(Course).order_by(Course.name)))


def get_students(keyword: str = '') -> list[Student]:
    stmt = (
        select(Student)
        .options(selectinload(Student.department), selectinload(Student.courses))
        .order_by(Student.student_number)
    )
    cleaned_keyword = keyword.strip()
    if cleaned_keyword:
        stmt = stmt.where(
            or_(
                Student.student_number.ilike(f'%{cleaned_keyword}%'),
                Student.name.ilike(f'%{cleaned_keyword}%')
            )
        )
    return list(db.session.scalars(stmt).unique())


def get_student_or_none(student_id: int) -> Student | None:
    stmt = (
        select(Student)
        .options(selectinload(Student.department), selectinload(Student.courses))
        .where(Student.id == student_id)
    )
    return db.session.scalar(stmt)


def validate_student_form(form: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    student_number = form.get('student_number', '').strip()
    name = form.get('name', '').strip()
    department_raw = form.get('department_id', '').strip()
    course_values = request.form.getlist('course_ids')

    if not student_number:
        errors.append('学生番号は必須です。')
    elif not STUDENT_NUMBER_PATTERN.fullmatch(student_number):
        errors.append('学生番号は3〜20文字の英数字またはハイフンで入力してください。')

    if not name:
        errors.append('氏名は必須です。')
    elif len(name) > 50:
        errors.append('氏名は50文字以内で入力してください。')

    department_id: int | None = None
    if not department_raw:
        errors.append('所属学部は必須です。')
    elif not department_raw.isdigit():
        errors.append('所属学部の値が不正です。')
    else:
        department_id = int(department_raw)
        if db.session.get(Department, department_id) is None:
            errors.append('選択した所属学部は存在しません。')

    course_ids: list[int] = []
    invalid_course_value = False
    for course_value in course_values:
        if not course_value.isdigit():
            invalid_course_value = True
            break
        course_ids.append(int(course_value))
    if invalid_course_value:
        errors.append('履修科目の値が不正です。')
    elif course_ids:
        course_count = db.session.scalar(select(db.func.count(Course.id)).where(Course.id.in_(course_ids)))
        if course_count != len(set(course_ids)):
            errors.append('選択した履修科目に存在しないデータが含まれています。')

    return errors, {
        'student_number': student_number,
        'name': name,
        'department_id': department_id,
        'course_ids': list(dict.fromkeys(course_ids)),
    }


def validate_search_keyword(keyword: str) -> str | None:
    if not keyword.strip():
        return '検索キーワードを入力してください。'
    if len(keyword.strip()) > 50:
        return '検索キーワードは50文字以内で入力してください。'
    return None


def validate_course_update(course_values: list[str]) -> tuple[list[str], list[int]]:
    errors: list[str] = []
    course_ids: list[int] = []

    for course_value in course_values:
        if not course_value.isdigit():
            errors.append('履修科目の値が不正です。')
            return errors, []
        course_ids.append(int(course_value))

    unique_course_ids = list(dict.fromkeys(course_ids))
    if unique_course_ids:
        course_count = db.session.scalar(select(db.func.count(Course.id)).where(Course.id.in_(unique_course_ids)))
        if course_count != len(unique_course_ids):
            errors.append('選択した履修科目に存在しないデータが含まれています。')

    return errors, unique_course_ids


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
        'app_14_1_index.html',
        students=students,
        departments=get_departments(),
        courses=get_courses(),
        keyword=keyword,
        search_error=search_error,
    )


@app.route('/register', methods=['POST'])
def register():
    errors, payload = validate_student_form(request.form)
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('index'))

    new_student = Student(
        student_number=payload['student_number'],
        name=payload['name'],
        department_id=payload['department_id'],
    )

    if payload['course_ids']:
        selected_courses = list(db.session.scalars(select(Course).where(Course.id.in_(payload['course_ids']))))
        new_student.courses = selected_courses

    db.session.add(new_student)
    try:
        db.session.commit()
        flash('学生レコードを登録しました。', 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f"学生番号 {payload['student_number']} は既に登録されています。", 'error')

    return redirect(url_for('index'))


@app.route('/students/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id: int):
    student = db.session.get(Student, student_id)
    if student is None:
        flash('削除対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    db.session.delete(student)
    db.session.commit()
    flash(f'学生 {student.name} を削除しました。', 'success')
    return redirect(url_for('index'))


@app.route('/students/<int:student_id>/courses/edit', methods=['GET'])
def edit_courses(student_id: int):
    student = get_student_or_none(student_id)
    if student is None:
        flash('対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    return render_template(
        'app_14_1_edit_courses.html',
        student=student,
        courses=get_courses(),
    )


@app.route('/students/<int:student_id>/courses', methods=['POST'])
def update_courses(student_id: int):
    student = get_student_or_none(student_id)
    if student is None:
        flash('対象の学生が見つかりません。', 'error')
        return redirect(url_for('index'))

    errors, course_ids = validate_course_update(request.form.getlist('course_ids'))
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('edit_courses', student_id=student_id))

    selected_courses = []
    if course_ids:
        selected_courses = list(db.session.scalars(select(Course).where(Course.id.in_(course_ids))))

    student.courses = selected_courses
    db.session.commit()
    flash(f'学生 {student.name} の履修科目を更新しました。', 'success')
    return redirect(url_for('index'))


def init_data():
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

    db.session.commit()


if __name__ == '__main__':
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    with app.app_context():
        db.create_all()
        init_data()

    app.run(debug=True)
