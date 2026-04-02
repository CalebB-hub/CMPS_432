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
    results = None
    with engine.connect() as conn:
        results = conn.execute(
            insert(Item)
            .returning(Item.id),
            [ item ]
        ).all()
        conn.commit()
    return results[0][0]
def remove_item(engine, item_id):
    with engine.connect() as conn:
        conn.execute(
            delete(Item)
            .where(Item.id == item_id)
        )
        conn.commit()
def add_tag(engine, tag):
    results = None
    with engine.connect() as conn:
        results = conn.execute(
            insert(Tag)
            .returning(Tag.id),
            [ tag ]
        ).all()
        conn.commit()
    return results[0][0]
def remove_tag(engine, tag_id):
    with engine.connect() as conn:
        conn.execute(
            delete(Tag)
            .where(Tag.id == tag_id)
        )
        conn.commit()
def add_tag_relation(engine, child_id, parent_id):
    relation = {"child_id":child_id, "parent_id":parent_id}
    with engine.connect() as conn:
        conn.execute(
            insert(TagTag),
            [relation]
        )
        conn.commit()
def add_tags(engine, tags):
    results = None
    with engine.connect() as conn:
        results = conn.execute(
            insert(Tag)
            .returning(Tag.id),
            tags
        ).all()
        conn.commit()

    return results
def get_tag_id(engine, tag):
    results = None
    with engine.connect() as conn:
        results = conn.execute(
                select(Tag.id)
                .where(Tag.name == tag['name'] )
                .where(Tag.user_id == tag['user_id'])
        ).all()
    if len(results) == 0: return -1
    return results[0][0]
def tag_exists(engine, tag):
    return get_tag_id(engine, tag) != -1
def get_tag_item_relation_id(engine, item_id, tag_id):
    results = None
    with engine.connect() as conn:
        results = conn.execute(
            select(TagItem)
            .where(TagItem.item_id == item_id)
            .where(TagItem.tag_id == tag_id)
        ).all()
    if len(results) == 0: return -1
    return results[0][0]
def tag_item_relation_exists(engine, item_id, tag_id):
    return get_tag_item_relation_id(engine, item_id, tag_id) != -1
def add_tag_item_relation(engine, item_id, tag_id):
    with engine.connect() as conn:
        conn.execute(
            insert(TagItem),
            [ {"item_id":item_id, "tag_id":tag_id} ]
        )
        conn.commit()
def add_tags_to_item(engine, item_id, tag_ids):
    for tag_id in tag_ids:
        if tag_item_relation_exists(engine, item_id, tag_id): continue
        add_tag_item_relation(engine, item_id, tag_id)
def get_tag_ids(engine, tags):
    tag_ids = []
    for tag in tags:
        tag_ids.append(get_tag_id(engine, tag))
    return tag_ids


def add_item_with_tags(engine, item, tags):
    user_id = item['user_id']
    item_id = add_item(engine, item)
    
    tag_ids = []

    for tag in tags:
        tag_id = get_tag_id(engine, tag)
        if tag_id == -1:
            tag_id = add_tag(engine, tag)
        tag_ids.append(tag_id)
    
    for tag_id in tag_ids:
        add_tags_to_item(engine, item_id, [tag_id])
def get_items_with_tags(engine, tags):
    if len(tags) == 0: return None
    tag_ids = get_tag_ids(engine, tags)
    selects = []
    for tag_id in tag_ids:
        selects.append(
            select(Item.id, Item.name, Item.user_id)
            .select_from(join(TagItem, Item))
            .where(TagItem.tag_id == tag_id)
        )

    stmt = intersect(*selects)
    results = None
    with engine.connect() as conn:
        results = conn.execute(
            stmt
        ).all()

    return results

