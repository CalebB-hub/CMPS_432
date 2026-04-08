from sqlalchemy import create_engine, text, insert, select, delete, intersect, join, intersect_all
import logging
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, mapped_column, Mapped
from sqlalchemy.orm.properties import ForeignKey
class Base(MappedAsDataclass, DeclarativeBase):
    pass

def primary_key():
    return mapped_column(primary_key=True, init=False)

class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = primary_key()
    name: Mapped[str]
    password: Mapped[str]

class Item(Base):
    __tablename__ = "Item"

    id: Mapped[int] = primary_key()
    name: Mapped[str]
    path: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))

class Share(Base):
    __tablename__ = "Share"

    id: Mapped[int] = primary_key()
    item_id: Mapped[int] = mapped_column(ForeignKey("Item.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("User.id"))

class Tag(Base):
    __tablename__ = "Tag"

    id: Mapped[int] = primary_key()
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    name: Mapped[str]


class TagItem(Base):
    __tablename__ = "TagItem"

    id: Mapped[int] = primary_key()
    tag_id: Mapped[int] = mapped_column(ForeignKey("Tag.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("Item.id"))

class TagTag(Base):
    __tablename__ = "TagTag"

    id: Mapped[int] = primary_key()
    parent_id: Mapped[int] = mapped_column(ForeignKey("Tag.id"))
    child_id: Mapped[int] = mapped_column(ForeignKey("Tag.id"))

class Alias(Base):
    __tablename__ = "Alias"

    id: Mapped[int] = primary_key()
    tag_id: Mapped[int] = mapped_column(ForeignKey("Tag.id"))
    name: Mapped[str]

class PocketDB:
    def __init__(self, filename=""):
        self._engine = self._init_engine(filename=filename)

    def _init_engine(self, filename):
        engine = create_engine(f"sqlite:///{filename}")
        self._create_tables(engine)
        return engine

    def _create_tables(self, engine):
        with engine.connect() as conn:
            Base.metadata.create_all(conn)
            conn.commit()
    def _exec(self, stmt, params=[], get_results=False):
        results = None
        with self._engine.connect() as conn:
            print("~~~~~~~~~~~~~~~~~~~~~~")
            print(f"stmt: {stmt}")
            print(f"params: {params}")

            results = conn.execute(
                stmt,
                params
            )
            conn.commit()

        if get_results:
            return results.all()

    def _get_user_id(self, name):
        stmt = select(User.id).where(User.name == name)
        results = self._exec(stmt, params=None, get_results=True)
        if len(results) == 0: return -1
        return results[0][0]

    def _add_user(self, name, password):
        stmt = insert(User)
        params = [{"name":name, "password":password}]
        self._exec(stmt, params)

    def add_user(self, name, password):
        user_id = self._get_user_id(name)
        if user_id == -1:
            self._add_user(name, password)
        pass
