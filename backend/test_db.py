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

if __name__ == "__main__":
    test_main()
