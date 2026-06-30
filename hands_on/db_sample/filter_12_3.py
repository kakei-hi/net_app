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


def seed_data() -> None:
    # 毎回同じ状態でJOIN結果を確認できるように初期化する。
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
    db.session.add_all([grass, poison, water])
    db.session.flush()

    monsters = [
        Monster(name="Fushigidane", software_id=software_red_green.id),
        Monster(name="Hitokage", software_id=software_red_green.id),
        Monster(name="Zenigame", software_id=software_gold_silver.id),
        Monster(name="Pikachu", software_id=software_gold_silver.id),
        Monster(name="Karakara", software_id=software_ruby_sapphire.id),
    ]
    db.session.add_all(monsters)
    db.session.flush()

    # あえて全モンスターにはタイプを付与せず、OUTER JOINとの差分が出るようにする。
    db.session.add_all(
        [
            MonsterType(monster_id=monsters[0].id, type_id=grass.id),
            MonsterType(monster_id=monsters[0].id, type_id=poison.id),
            MonsterType(monster_id=monsters[2].id, type_id=water.id),
        ]
    )

    db.session.commit()


def show_all_data() -> None:
    print("\n=== 登録済み全データ ===")

    print("[software]")
    for software in db.session.query(Software).order_by(Software.id).all():
        print(
            f"id={software.id}, title={software.title}, "
            f"release_date={software.release_date}"
        )

    print("\n[type]")
    for t in db.session.query(Type).order_by(Type.id).all():
        print(f"id={t.id}, type={t.type}")

    print("\n[monster]")
    for monster in db.session.query(Monster).order_by(Monster.id).all():
        print(
            f"id={monster.id}, name={monster.name}, "
            f"software_id={monster.software_id}"
        )

    print("\n[monster_type]")
    for link in db.session.query(MonsterType).order_by(MonsterType.id).all():
        print(
            f"id={link.id}, monster_id={link.monster_id}, "
            f"type_id={link.type_id}"
        )


def show_inner_join() -> None:
    print("\n=== INNER JOIN (タイプが登録されているモンスターのみ) ===")
    # INNER JOINは、結合先に対応レコードがある行だけを返す。
    rows = (
        db.session.query(Monster, Type)
        .join(MonsterType, Monster.id == MonsterType.monster_id)
        .join(Type, MonsterType.type_id == Type.id)
        .order_by(Monster.id, Type.id)
        .all()
    )

    for monster, monster_type in rows:
        print(f"monster={monster.name}, type={monster_type.type}")


def show_left_outer_join() -> None:
    print("\n=== LEFT OUTER JOIN (すべてのモンスター) ===")
    # LEFT OUTER JOINは、左表(Monster)の行を必ず残し、未対応はNULLになる。
    rows = (
        db.session.query(Monster, Type)
        .outerjoin(MonsterType, Monster.id == MonsterType.monster_id)
        .outerjoin(Type, MonsterType.type_id == Type.id)
        .order_by(Monster.id, Type.id)
        .all()
    )

    for monster, monster_type in rows:
        type_name = monster_type.type if monster_type else "(none)"
        print(f"monster={monster.name}, type={type_name}")


def show_filtered_join() -> None:
    print("\n=== 条件抽出付きJOIN（Grassタイプのみ） ===")
    rows = (
        db.session.query(Monster, Type)
        .join(MonsterType, Monster.id == MonsterType.monster_id)
        .join(Type, MonsterType.type_id == Type.id)
        .filter(Type.type == "Grass")
        .order_by(Monster.id)
        .all()
    )

    for monster, monster_type in rows:
        print(f"monster={monster.name}, type={monster_type.type}")


with app.app_context():
    seed_data()
    show_all_data()
    show_inner_join()
    show_left_outer_join()
    show_filtered_join()
