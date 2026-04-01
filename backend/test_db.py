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

def exec_tests():
    test_main()
    pass

if __name__ == "__main__":
    exec_tests()
    print("All tests passed")
    pass
