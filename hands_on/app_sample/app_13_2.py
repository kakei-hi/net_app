import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table

# Flaskインスタンスの生成と設定
app = Flask(__name__)

# instanceディレクトリの下にデータベースを自動生成・配置するためのパス設定
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'students.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyで利用するベースクラスを定義（SQLAlchemy 2.0+ スタイル）
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)


# ==============================================================================
# ORMモデル（データベース設計）
# ==============================================================================

class Department(db.Model):
    """所属学部モデル（学生とは 1対多 の関係）"""
    __tablename__ = 'departments'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # リレーションシップ定義
    students: Mapped[list["Student"]] = relationship(back_populates="department")


class StudentCourse(db.Model):
    """学生と履修科目の中間テーブル（多対多をつなぐサロゲートキー設計）"""
    __tablename__ = 'student_courses'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # サロゲートキー
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)


class Course(db.Model):
    """履修科目モデル（学生とは 多対多 の関係）"""
    __tablename__ = 'courses'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # 中間テーブルStudentCourseを経由するリレーションシップ
    students: Mapped[list["Student"]] = relationship(
        secondary="student_courses",
        back_populates="courses"
    )


class Student(db.Model):
    """学生情報モデル"""
    __tablename__ = 'students'
    
    id: Mapped[int] = mapped_column(primary_key=True)  # サロゲートキー
    student_number: Mapped[str] = mapped_column(unique=True, nullable=False)  # 学生番号
    name: Mapped[str] = mapped_column(nullable=False)  # 氏名
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)  # 多対1用のFK
    
    # リレーションシップ定義
    department: Mapped["Department"] = relationship(back_populates="students")
    courses: Mapped[list["Course"]] = relationship(
        secondary="student_courses",
        back_populates="students"
    )


# ==============================================================================
# ルーティング（コントローラ処理）
# ==============================================================================

@app.route('/', methods=['GET'])
def index():
    """一覧取得機能
    - ブラウザが一覧ページにアクセスする
    - Flaskがルーティングを実行する
    - SQLAlchemyがデータを取得する
    - テンプレートにデータを渡す
    - HTMLを生成してブラウザに返す
    """
    # 学生一覧、マスタ選択用の学部一覧、科目一覧をそれぞれ取得
    students = db.session.query(Student).all()
    departments = db.session.query(Department).all()
    courses = db.session.query(Course).all()
    
    return render_template('index.html', students=students, departments=departments, courses=courses)


@app.route('/register', methods=['POST'])
def register():
    """データ登録機能
    - ユーザーがフォームへ入力し、POSTリクエストを送信する
    - Flaskが入力値を受信する
    - レコードのオブジェクトを生成する
    - データベースへ保存する
    - 一覧画面へリダイレクトする
    """
    # フォームからの入力値受信
    student_number = request.form.get('student_number')
    name = request.form.get('name')
    department_id = request.form.get('department_id')
    course_ids = request.form.getlist('course_ids')  # 複数選択のチェックボックス値を取得
    
    if student_number and name and department_id:
        # 学生オブジェクトの生成
        new_student = Student(
            student_number=student_number,
            name=name,
            department_id=int(department_id)
        )
        
        # 選択された科目のオブジェクトを検索し、学生に関連付け
        if course_ids:
            selected_courses = db.session.query(Course).filter(Course.id.in_([int(cid) for cid in course_ids])).all()
            new_student.courses.extend(selected_courses)
        
        # データベースへの保存
        db.session.add(new_student)
        db.session.commit()
        
    return redirect(url_for('index'))


# ==============================================================================
# 初期データ投入用スクリプト（アプリ起動時に自動実行）
# ==============================================================================

def init_data():
    """初期マスタデータの登録用関数"""
    if db.session.query(Department).count() == 0:
        tech = Department(name="工学部")
        science = Department(name="理学部")
        lit = Department(name="文学部")
        db.session.add_all([tech, science, lit])
        
    if db.session.query(Course).count() == 0:
        prog = Course(name="プログラミング演習")
        database = Course(name="データベース論")
        math = Course(name="離散数学")
        db.session.add_all([prog, database, math])
        
    db.session.commit()


if __name__ == '__main__':
    # instanceディレクトリがなければ自動作成
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    
    with app.app_context():
        db.create_all()  # テーブルの自動作成
        init_data()      # サンプルマスタデータの投入
        
    app.run(debug=True)
