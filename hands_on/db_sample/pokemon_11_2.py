from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
from pathlib import Path


class Base(DeclarativeBase):
    pass


base_dir = Path(__file__).resolve().parent
instance_dir = base_dir / "instance"
instance_dir.mkdir(exist_ok=True)

app = Flask(__name__, instance_path=str(instance_dir))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pokemon.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Monster(Base):
    __tablename__ = "monster"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    software_id: Mapped[int] = mapped_column(ForeignKey("software.id"))


class Type(Base):
    __tablename__ = "type"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))


class MonsterType(Base):
    __tablename__ = "monster_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monster.id"))
    type_id: Mapped[int] = mapped_column(ForeignKey("type.id"))


class Software(Base):
    __tablename__ = "software"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    release_date: Mapped[datetime.date] = mapped_column(Date)


with app.app_context():
    db.create_all()

    software = Software(
        title="Pokemon Red/Green",
        release_date=datetime.date(1996, 2, 27),
    )
    db.session.add(software)
    db.session.flush()

    monster = Monster(
        name="Fushigidane",
        software_id=software.id,
    )
    db.session.add(monster)

    monster_type = Type(type="Grass")
    db.session.add(monster_type)
    db.session.flush()

    monster_type_link = MonsterType(
        monster_id=monster.id,
        type_id=monster_type.id,
    )
    db.session.add(monster_type_link)

    db.session.commit()

    print("Inserted 1 record into each table: software, monster, type, monster_type")
