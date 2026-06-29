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


def print_monsters(label: str) -> None:
    print(f"\n[{label}]")
    monsters = db.session.query(Monster).order_by(Monster.id).all()
    if not monsters:
        print("  (no monster records)")
        return

    for monster in monsters:
        software = db.session.get(Software, monster.software_id)
        links = db.session.query(MonsterType).filter_by(monster_id=monster.id).all()
        type_names: list[str] = []
        for link in links:
            t = db.session.get(Type, link.type_id)
            if t is not None:
                type_names.append(t.type)

        print(
            f"  id={monster.id}, name={monster.name}, "
            f"software={software.title if software else 'Unknown'}, "
            f"types={', '.join(type_names) if type_names else '(none)'}"
        )


with app.app_context():
    db.drop_all()
    db.create_all()

    print("=== CRUD Sample Start ===")

    # C: Create
    software = Software(
        title="Pokemon Red/Green",
        release_date=datetime.date(1996, 2, 27),
    )
    db.session.add(software)
    db.session.flush()

    grass = Type(type="Grass")
    poison = Type(type="Poison")
    db.session.add_all([grass, poison])
    db.session.flush()

    monster = Monster(name="Fushigidane", software_id=software.id)
    db.session.add(monster)
    db.session.flush()

    db.session.add_all(
        [
            MonsterType(monster_id=monster.id, type_id=grass.id),
            MonsterType(monster_id=monster.id, type_id=poison.id),
        ]
    )
    db.session.commit()
    print_monsters("Create")

    # R: Read
    found = db.session.query(Monster).filter_by(name="Fushigidane").first()
    print("\n[Read]")
    if found:
        print(f"  found monster: id={found.id}, name={found.name}")

    # U: Update
    if found:
        found.name = "Ivysaur"
        db.session.commit()
    print_monsters("Update")

    # D: Delete
    if found:
        db.session.query(MonsterType).filter_by(monster_id=found.id).delete()
        db.session.delete(found)
        db.session.commit()
    print_monsters("Delete")

    print("\n=== CRUD Sample End ===")
