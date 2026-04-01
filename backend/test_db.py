import src.db as db
from unittest import TestCase
from unittest import main as test_main

def init_db():
    engine = db.create_engine('sqlite:///')
    db.create_tables(engine)
    return engine

class TestUser(TestCase):
    def test_add_user(self):
        engine = init_db()

        user = {"name":"john", "password":"terrible"}
        db.add_user(engine, user)

        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.User)
                .where(db.User.name == user['name'])
                .where(db.User.password == user['password'])
            ).all()

        self.assertTrue(len(results) > 0, "User was not added successfully")
        engine.dispose()

    def test_get_all_users(self):
        engine = init_db()

        users = [
            {"name":"john", "password":"terrible"},
            {"name":"harold", "password":"pizza"},
            {"name":"liyana", "password":"glacier"}
        ]

        with engine.connect() as conn:
            conn.execute(
                db.insert(db.User),
                users
            )
            conn.commit()

        users_retrieved = db.get_all_users(engine)

        self.assertEqual(len(users), len(users_retrieved), "Not all users were inputted correctly")
        engine.dispose()

    def test_remove_user(self):
        engine = init_db()

        user = {"name":"john", "password":"terrible"}

        with engine.connect() as conn:
            conn.execute(
                db.insert(db.User),
                [ user ]
            )
            conn.commit()

        name = user['name']
        db.remove_user(engine, name)

        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.User)
            ).all()

        self.assertTrue(len(results) == 0, "User not was not removed properly")
        engine.dispose()

    def test_user_pass_matches(self):
        engine = init_db()
        user = {"name":"john", "password":"terrible"}

        with engine.connect() as conn:
            conn.execute(
                db.insert(db.User),
                [ user ]
            )
            conn.commit()

        self.assertTrue(
            db.user_pass_matches(engine, user['name'], user['password']),
            "User and password should match"
        )

        self.assertFalse(
            db.user_pass_matches(engine, user['name'], user['password'] + "NONSENSE EXTRA TEXT"),
            "User and password shouldn't match"
        )
        engine.dispose()

class TestItem(TestCase):
    def test_add_item(self):
        engine = init_db()

        item = {
            "name":"burger site",
            "path":"https://www.burger.com",
            "user_id":0
        }
        db.add_item(engine, item)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Item)
                .where(db.Item.name == item['name'])
                .where(db.Item.path == item['path'])
                .where(db.Item.user_id == item['user_id'])
            ).all()

        self.assertTrue(
            len(results) == 1,
            "Item was not added successfully"
        )
        engine.dispose()

    def test_remove_item(self):
        engine = init_db()

        item = {
            "name":"burger site",
            "path":"https://www.burger.com",
            "user_id":0
        }
        with engine.connect() as conn:
            conn.execute(
                db.insert(db.Item),
                [item]
            )
            conn.commit()
        item_id = 28
        db.remove_item(engine, item_id)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Item)
            ).all()

        self.assertTrue(
            len(results) != 0,
            "Removed incorrect item"
        )

        item_id = 1 # first item key is always 1
        db.remove_item(engine, item_id)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Item)
            ).all()

        self.assertTrue(
            len(results) == 0,
            "Failed to remove item"
        )
        engine.dispose()

class TestTag(TestCase):
    def test_add_tag(self):
        engine = init_db()
        tag = {"user_id":4, "name":"art"}

        db.add_tag(engine, tag)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Tag)
                .where(db.Tag.user_id == tag['user_id'])
                .where(db.Tag.name == tag['name'])
            ).all()

        self.assertTrue(
            len(results) == 1,
            "Failed to add tag"
        )
        engine.dispose()

    def test_remove_tag(self):
        engine = init_db()
        tag = {"user_id":4, "name":"art"}

        db.add_tag(engine, tag)
        tag_id = 5
        db.remove_tag(engine, tag_id)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Tag)
            ).all()

        self.assertTrue(
            len(results) == 1,
            "Removed incorrect tag"
        )

        tag_id = 1
        db.remove_tag(engine, tag_id)
        results = None
        with engine.connect() as conn:
            results = conn.execute(
                db.select(db.Tag)
            ).all()

        self.assertTrue(
            len(results) == 0,
            "Failed to remove tag"
        )
        engine.dispose()


def exec_tests():
    test_main()
    pass

if __name__ == "__main__":
    exec_tests()
    print("All tests passed")
    pass
