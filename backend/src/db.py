from re import A
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
            # print("~~~~~~~~~~~~~~~~~~~~~~")
            # print(f"stmt: {stmt}")
            # print(f"params: {params}")

            results = conn.execute(
                stmt,
                params
            )
            conn.commit()

        if get_results:
            return results.all()
        else:
            return []

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
        user_id = self._get_user_id(name=name)
        if user_id == -1:
            self._add_user(name=name, password=password)
        pass

    def _get_item_id(self, user_id, name):
        stmt = select(Item.id).where(Item.name == name).where(Item.user_id == user_id)
        results = self._exec(stmt=stmt, params=None, get_results=True)
        if len(results) == 0: return -1
        return results[0][0]

    def _add_item(self, user_id, name, path):
        stmt = insert(Item)
        params = [{"user_id":user_id, "name":name, "path":path}]
        self._exec(stmt, params)

    def add_item(self, user, name, path):
        user_id = self._get_user_id(name=user)
        if user_id == -1:
            return

        item_id = self._get_item_id(user_id=user_id, name=name)
        if item_id == -1:
            self._add_item(user_id=user_id, name=name, path=path)

    def _get_tag_id(self, name, user_id):
        stmt = select(Tag.id).where(Tag.name == name).where(Tag.user_id == user_id)
        results = self._exec(stmt=stmt, params=None, get_results=True)

        if len(results) == 0: return -1
        return results[0][0]

    def _add_tag(self, name, user_id):
        stmt = insert(Tag)
        params = [{"name":name, "user_id":user_id}]
        self._exec(stmt=stmt, params=params)

    def add_tag(self, name, user):
        user_id = self._get_user_id(name=user)
        if user_id == -1:
            return

        tag_id = self._get_tag_id(name=name, user_id=user_id)
        if tag_id == -1:
            self._add_tag(name=name, user_id=user_id)

    def _get_tagitem_id(self, item_id:int, tag_id:int):
        stmt = (
            select(TagItem.id)
            .where(TagItem.item_id == item_id)
            .where(TagItem.tag_id == tag_id)
        )
        results = self._exec(stmt, params=None, get_results=True)
        if len(results) == 0: return -1
        return results[0][0]

    def _add_tagitem(self, item_id:int, tag_id:int):
        stmt = (
            insert(TagItem)
        )
        params = [{"item_id":item_id, "tag_id":tag_id}]
        self._exec(stmt=stmt, params=params)

    def assign_tag(self, user:str, item:str, tag:str):
        user_id = self._get_user_id(name=user)
        if user_id == -1:
            return

        item_id = self._get_item_id(name=item, user_id=user_id)
        if item_id == -1:
            return

        tag_id = self._get_tag_id(name=tag, user_id=user_id)
        if tag_id == -1:
            return

        tagitem_id = self._get_tagitem_id(item_id=item_id, tag_id=tag_id)
        if tagitem_id == -1:
            self._add_tagitem(item_id=item_id, tag_id=tag_id)

    def _get_tagtag_id(self, parent_id:int, child_id:int) -> int:
        stmt = (
            select(TagTag.id)
            .where(TagTag.parent_id == parent_id)
            .where(TagTag.child_id == child_id)
        )
        results = self._exec(stmt=stmt, params=None, get_results=True)
        if len(results) == 0:
            return -1
        return results[0][0]

    def _add_tagtag(self, parent_id:int, child_id:int):
        stmt = (
            insert(TagTag)
        )
        params = [{"parent_id":parent_id, "child_id":child_id}]
        self._exec(stmt=stmt, params=params)

    def add_tag_relation(self, user:str, parent:str, child:str):
        user_id = self._get_user_id(name=user)
        if user_id == -1:
            return

        parent_id = self._get_tag_id(user_id=user_id, name=parent)
        child_id = self._get_tag_id(user_id=user_id, name=child)

        if -1 in [parent_id, child_id]:
            return

        tagtag_id = self._get_tagtag_id(parent_id=parent_id, child_id=child_id)
        if tagtag_id == -1:
            self._add_tagtag(parent_id=parent_id, child_id=child_id)

    def _get_tag_children(self, tag_id:int):
        stmt = select(TagTag.child_id).where(TagTag.parent_id == tag_id)
        results = self._exec(stmt=stmt, params=None, get_results=True)
        children = [x[0] for x in results]
        return children

    def _get_list_difference(self, list_a:list, list_b:list) -> list:
        set_difference = set(list_a) - set(list_b)
        return list(set_difference)

    def _get_tag_lineage_helper_deprecated(self, user_id:int, tag_id:int, lineage:list[int]):
        # print(lineage)
        children = self._get_tag_children(tag_id=tag_id)
        lineage.append(tag_id)
        children = self._get_list_difference(children, lineage)
        # print(children)
        for tag in children:
            self._get_tag_lineage_helper(user_id=user_id, tag_id=tag, lineage=lineage)

        '''
        1. remove tags already in lineage from children of initial tag
        2. if no children left return list with just initial tag
        3. go through remaining tags and add each of their lineages to the overall lineage
        '''

        pass
    def _get_tag_lineage_helper(self, user_id:int, tag_id:int, lineage:list[int]):
        if tag_id in lineage:
            return

        lineage.append(tag_id)

        children = self._get_tag_children(tag_id=tag_id)
        for child in children:
            self._get_tag_lineage_helper(user_id=user_id, tag_id=child, lineage=lineage)

    def _get_tag_lineage(self, user_id:int, tag_id:int) -> list[int]:
        lineage = []
        self._get_tag_lineage_helper(user_id=user_id, tag_id=tag_id, lineage=lineage)
        return lineage

    '''
    items must have each tag represented (if that tag is not on the item,
    then one of it's descendents must be on the item)
    '''
    def get_items_by_tags(self, user:str, tags:list[str]) -> list[str]:
        user_id = self._get_user_id(name=user)
        if user_id == -1:
            return []

        if len(tags) == 0:
            return []

        tag_lineages = [[]] * 8
        for i in range(len(tags)):
            tag = tags[i]
            tag_id = self._get_tag_id(user_id=user_id, name=tag)
            if tag_id == -1:
                continue

            tag_lineages[i] = self._get_tag_lineage(user_id=user_id, tag_id=tag_id)
