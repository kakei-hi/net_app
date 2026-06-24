from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Date, ForeignKey
import datetime
from pathlib import Path
    
class Base(DeclarativeBase):
    pass

base_dir = Path(__file__).resolve().parent
instance_dir = base_dir / "instance"
instance_dir.mkdir(exist_ok=True)

app = Flask(__name__, instance_path=str(instance_dir))
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
    monster_id: Mapped[int] = mapped_column(ForeignKey("monster.id"))
    type_id: Mapped[int] = mapped_column(Integer)


class Software(Base):
    __tablename__ = "software"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    release_date: Mapped[datetime.date] = mapped_column(Date)


with app.app_context():
    db.create_all()
    for table_name, table in Base.metadata.tables.items():
        print(f"【{table_name}】")
        for column in table.columns:
            print(f"  {column.name} ({column.type})")
        print()
