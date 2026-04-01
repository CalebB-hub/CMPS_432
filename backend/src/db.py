from sqlalchemy import create_engine, text, insert, select, delete
import logging
from .tables import *

DB_FILENAME = "db.sqlite"

def init():
    engine = create_engine(f"sqlite:///{DB_FILENAME}")
    create_tables(engine)
    return engine
    pass
def create_tables(engine):
    with engine.connect() as conn:
        Base.metadata.create_all(conn)
        conn.commit()

def add_user(engine, user):
    with engine.connect() as conn:
        conn.execute(
            insert(User), [
                user
            ]
        )
        conn.commit()
def user_exists(engine, name):
    rows = None
    with engine.connect() as conn:
        rows = conn.execute(
            select(User).where(User.name == name)
        ).all()
    logging.info(f"Number of users named {name}: {len(rows)}")
    return len(rows) > 0

def username_matches_password(engine, name, password):
    rows = None
    with engine.connect() as conn:
        rows = conn.execute(
            select(User)
            .where(User.name == name)
            .where(User.password == password)
        ).all()

    return len(rows) > 0

def get_all_users(engine):
    rows = None
    with engine.connect() as conn:
        rows = conn.execute(
            select(User)
        ).all()
    return rows

def remove_user(engine, name):
    with engine.connect() as conn:
        conn.execute(
            delete(User)
            .where(User.name == name)
        )
        conn.commit()

def user_pass_matches(engine, name, password):
    results = None
    with engine.connect() as conn:
        stmt = (
            select(User)
            .where(User.name == name)
            .where(User.password == password)
        )
        results = conn.execute(
            stmt
        ).all()

    return len(results) > 0

def add_item(engine, item):
    with engine.connect() as conn:
        conn.execute(
            insert(Item),
            [ item ]
        )
        conn.commit()
def remove_item(engine, item_id):
    with engine.connect() as conn:
        conn.execute(
            delete(Item)
            .where(Item.id == item_id)
        )
        conn.commit()
def add_tag(engine, tag):
    with engine.connect() as conn:
        conn.execute(
            insert(Tag),
            [ tag ]
        )
        conn.commit()
def remove_tag(engine, tag_id):
    with engine.connect() as conn:
        conn.execute(
            delete(Tag)
            .where(Tag.id == tag_id)
        )
        conn.commit()
