from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, ForeignKey, String, func, or_
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
    weight: Mapped[float] = mapped_column()
    height: Mapped[float] = mapped_column()
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


class Ability(Base):
    __tablename__ = "ability"

    id: Mapped[int] = mapped_column(primary_key=True)
    ability: Mapped[str] = mapped_column(String(50))


class MonsterAbility(Base):
    __tablename__ = "monster_ability"

    id: Mapped[int] = mapped_column(primary_key=True)
    monster_id: Mapped[int] = mapped_column(ForeignKey("monster.id"))
    ability_id: Mapped[int] = mapped_column(ForeignKey("ability.id"))


class Software(Base):
    __tablename__ = "software"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    release_date: Mapped[datetime.date] = mapped_column(Date)


def seed_data() -> None:
    # 毎回同じ状態で確認できるように初期化する。
    db.drop_all()
    db.create_all()

    software_red_green = Software(
        title="Pokemon Red/Green",
        release_date=datetime.date(1996, 2, 27),
    )
    software_gold_silver = Software(
        title="Pokemon Gold/Silver",
        release_date=datetime.date(1999, 11, 21),
    )
    software_ruby_sapphire = Software(
        title="Pokemon Ruby/Sapphire",
        release_date=datetime.date(2002, 11, 21),
    )
    db.session.add_all([software_red_green, software_gold_silver, software_ruby_sapphire])
    db.session.flush()

    grass = Type(type="Grass")
    poison = Type(type="Poison")
    water = Type(type="Water")
    electric = Type(type="Electric")
    db.session.add_all([grass, poison, water, electric])
    db.session.flush()

    overgrow = Ability(ability="Overgrow")
    blaze = Ability(ability="Blaze")
    torrent = Ability(ability="Torrent")
    static = Ability(ability="Static")
    db.session.add_all([overgrow, blaze, torrent, static])
    db.session.flush()

    monsters = [
        Monster(name="Fushigidane", weight=6.9, height=0.7, software_id=software_red_green.id),
        Monster(name="Hitokage", weight=8.5, height=0.6, software_id=software_red_green.id),
        Monster(name="Zenigame", weight=9.0, height=0.5, software_id=software_gold_silver.id),
        Monster(name="Pikachu", weight=6.0, height=0.4, software_id=software_gold_silver.id),
        Monster(name="Karakara", weight=6.5, height=0.4, software_id=software_ruby_sapphire.id),
    ]
    db.session.add_all(monsters)
    db.session.flush()

    db.session.add_all(
        [
            MonsterType(monster_id=monsters[0].id, type_id=grass.id),
            MonsterType(monster_id=monsters[0].id, type_id=poison.id),
            MonsterType(monster_id=monsters[1].id, type_id=electric.id),
            MonsterType(monster_id=monsters[2].id, type_id=water.id),
            MonsterType(monster_id=monsters[3].id, type_id=poison.id),
            MonsterType(monster_id=monsters[4].id, type_id=grass.id),
        ]
    )

    db.session.add_all(
        [
            MonsterAbility(monster_id=monsters[0].id, ability_id=overgrow.id),
            MonsterAbility(monster_id=monsters[1].id, ability_id=static.id),
            MonsterAbility(monster_id=monsters[2].id, ability_id=torrent.id),
            MonsterAbility(monster_id=monsters[3].id, ability_id=blaze.id),
            MonsterAbility(monster_id=monsters[4].id, ability_id=torrent.id),
        ]
    )

    db.session.commit()


def show_all_data() -> None:
    print("\n=== 登録済み全データ ===")

    print("[ability]")
    for row in db.session.query(Ability).order_by(Ability.id).all():
        print(f"id={row.id}, ability={row.ability}")

    print("\n[monster]")
    for monster in db.session.query(Monster).order_by(Monster.id).all():
        print(
            f"id={monster.id}, name={monster.name}, "
            f"weight={monster.weight}, height={monster.height}, "
            f"software_id={monster.software_id}"
        )

    print("\n[monster_ability]")
    for row in db.session.query(MonsterAbility).order_by(MonsterAbility.id).all():
        print(
            f"id={row.id}, monster_id={row.monster_id}, "
            f"ability_id={row.ability_id}"
        )


def show_monster_ability_join() -> None:
    print("\n=== monster と ability の JOIN ===")
    rows = (
        db.session.query(Monster, Ability)
        .join(MonsterAbility, Monster.id == MonsterAbility.monster_id)
        .join(Ability, MonsterAbility.ability_id == Ability.id)
        .order_by(Monster.id)
        .all()
    )

    for monster, ability in rows:
        print(
            f"monster={monster.name}, weight={monster.weight}, "
            f"height={monster.height}, "
            f"ability={ability.ability}"
        )


def show_monster_ability_type_software_list() -> None:
    print("\n=== monster.name, monster.weight, monster.height, ability.ability, type.type, software.title ===")
    rows = (
        db.session.query(Monster, Ability, Type, Software)
        .join(MonsterAbility, Monster.id == MonsterAbility.monster_id)
        .join(Ability, MonsterAbility.ability_id == Ability.id)
        .join(MonsterType, Monster.id == MonsterType.monster_id)
        .join(Type, MonsterType.type_id == Type.id)
        .join(Software, Monster.software_id == Software.id)
        .order_by(Monster.id, Type.id)
        .all()
    )

    for monster, ability, monster_type, software in rows:
        print(
            f"{monster.name}, {monster.weight}, {monster.height}, "
            f"{ability.ability}, {monster_type.type}, {software.title}"
        )


def show_filtered_weight_and_ability_or_type() -> None:
    print("\n=== monster.weight >= 6.5 かつ (ability.ability='Static' または type.type='water') ===")
    rows = (
        db.session.query(Monster, Ability, Type)
        .join(MonsterAbility, Monster.id == MonsterAbility.monster_id)
        .join(Ability, MonsterAbility.ability_id == Ability.id)
        .join(MonsterType, Monster.id == MonsterType.monster_id)
        .join(Type, MonsterType.type_id == Type.id)
        .filter(Monster.weight >= 6.5)
        .filter(
            or_(
                Ability.ability == "Static",
                func.lower(Type.type) == "water",
            )
        )
        .order_by(Monster.id, Type.id)
        .all()
    )

    if not rows:
        print("(該当データなし)")
        return

    for monster, ability, monster_type in rows:
        print(
            f"{monster.name}, {monster.weight}, "
            f"{ability.ability}, {monster_type.type}"
        )


with app.app_context():
    seed_data()
    show_all_data()
    show_monster_ability_join()
    show_monster_ability_type_software_list()
    show_filtered_weight_and_ability_or_type()
