from __future__ import annotations

import os
from typing import List

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__, instance_path=INSTANCE_DIR)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'students.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Faculty(db.Model):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    students: Mapped[List["Student"]] = relationship(back_populates="faculty")


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_enrollments_student_subject"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    subject: Mapped["Subject"] = relationship(back_populates="enrollments")


class Student(db.Model):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_number: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"), nullable=False)

    faculty: Mapped[Faculty] = relationship(back_populates="students")
    enrollments: Mapped[List[Enrollment]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Subject(db.Model):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    enrollments: Mapped[List[Enrollment]] = relationship(back_populates="subject")


@app.route("/")
def index() -> str:
    return redirect(url_for("student_list"))


@app.route("/students", methods=["GET", "POST"])
def student_list() -> str:
    if request.method == "POST":
        student_number = request.form.get("student_number", "").strip()
        student_name = request.form.get("student_name", "").strip()
        faculty_name = request.form.get("faculty_name", "").strip()
        subjects_raw = request.form.get("subjects", "").strip()

        if student_number and student_name and faculty_name:
            existing_student = db.session.scalar(
                select(Student).where(Student.student_number == student_number)
            )
            if existing_student is None:
                faculty = db.session.scalar(
                    select(Faculty).where(Faculty.name == faculty_name)
                )
                if faculty is None:
                    faculty = Faculty(name=faculty_name)
                    db.session.add(faculty)
                    db.session.flush()

                student = Student(
                    student_number=student_number,
                    name=student_name,
                    faculty=faculty,
                )
                db.session.add(student)
                db.session.flush()

                subject_names = [
                    name.strip() for name in subjects_raw.split(",") if name.strip()
                ]
                for subject_name in subject_names:
                    subject = db.session.scalar(
                        select(Subject).where(Subject.name == subject_name)
                    )
                    if subject is None:
                        subject = Subject(name=subject_name)
                        db.session.add(subject)
                        db.session.flush()

                    db.session.add(Enrollment(student=student, subject=subject))

                db.session.commit()

        return redirect(url_for("student_list"))

    students = (
        db.session.execute(
            select(Student)
            .options(
                joinedload(Student.faculty),
                joinedload(Student.enrollments).joinedload(Enrollment.subject),
            )
            .order_by(Student.student_number)
        )
        .unique()
        .scalars()
        .all()
    )
    faculties = db.session.execute(select(Faculty).order_by(Faculty.name)).scalars().all()

    return render_template("students_13_1.html", students=students, faculties=faculties)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
