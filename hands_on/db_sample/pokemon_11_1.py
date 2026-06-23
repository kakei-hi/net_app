from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Date
import datetime

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pokemon.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Monster(Base):
    __tablename__ = "monster"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    software_id: Mapped[int] = mapped_column(Integer)


class Type(Base):
    __tablename__ = "type"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))


class MonsterType(Base):
    __tablename__ = "monster_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    monster_id: Mapped[int] = mapped_column(Integer)
    type_id: Mapped[int] = mapped_column(Integer)


class Software(Base):
    __tablename__ = "software"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    release_date: Mapped[datetime.date] = mapped_column(Date)


with app.app_context():
    db.create_all()
    print("テーブルを作成しました。")
