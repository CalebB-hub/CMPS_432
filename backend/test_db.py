from src.db import PocketDB

from unittest import TestCase
from unittest import main as test_main


class TestPocketDB(TestCase):
    def test_add_user(self):
        db = PocketDB()

        name = "john"
        user_id = db._get_user_id(name)
        self.assertEqual(
            user_id, -1,
            "User should not be in DB yet"
        )
        db.add_user(name=name, password="pizza3")
        user_id = db._get_user_id(name)
        self.assertEqual(
            user_id, 1,
            "User not added successfully"
        )
    def test_add_item(self):
        db = PocketDB()

        user = "ethan"
        db.add_user(user, "pizza")
        user_id = db._get_user_id(name=user)

        name = "nonsense"
        path = "http://burger.com"

        item_id = db._get_item_id(user_id=user_id, name=name)
        self.assertEqual(
            item_id, -1
        )

        db.add_item(user=user, name=name, path=path)

        item_id = db._get_item_id(user_id=user_id, name=name)
        self.assertEqual(
            item_id, 1
        )

    def test_add_tag(self):
        db = PocketDB()

        user = "ethan"
        password = "pass"
        db.add_user(name=user, password=password)
        user_id = db._get_user_id(name=user)

        name = "fruit"
        tag_id = db._get_tag_id(name=name, user_id=user_id)
        self.assertEqual(
            tag_id, -1
        )

        db.add_tag(name=name, user=user)

        tag_id = db._get_tag_id(name=name, user_id=user_id)
        self.assertEqual(
            tag_id, 1
        )







if __name__ == "__main__":
    test_main()
