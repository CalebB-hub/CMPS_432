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


    def test_add_tagitem(self):
        db = PocketDB()

        user = "ethan"
        password = "pass"
        db.add_user(name=user, password=password)


        item = "burger"
        path = "https://burger.com"
        db.add_item(name=item, path=path, user=user)

        tag = "food"
        db.add_tag(user=user, name=tag)

        user_id = db._get_user_id(name=user)
        item_id = db._get_item_id(user_id=user_id, name=item)
        tag_id = db._get_tag_id(user_id=user_id, name=tag)

        tagitem_id = db._get_tagitem_id(item_id=item_id, tag_id=tag_id)
        self.assertEqual(
            tagitem_id, -1
        )

        db.assign_tag(user=user, item=item, tag=tag)

        tagitem_id = db._get_tagitem_id(item_id=item_id, tag_id=tag_id)
        self.assertEqual(
            tagitem_id, 1
        )

    def test_add_tag_relation(self):
        db = PocketDB()

        user = "ethan"
        password = "pizza"

        db.add_user(name=user, password=password)
        user_id = db._get_user_id(name=user)

        parent = "food"
        child = "fruit"
        db.add_tag(name=parent, user=user)
        db.add_tag(name=child, user=user)

        parent_id = db._get_tag_id(user_id=user_id, name=parent)
        child_id = db._get_tag_id(user_id=user_id, name=child)
        tagtag_id = db._get_tagtag_id(parent_id=parent_id, child_id=child_id)
        self.assertEqual(
            tagtag_id, -1
        )
        db.add_tag_relation(user=user, parent="food", child="fruit")

        tagtag_id = db._get_tagtag_id(parent_id=parent_id, child_id=child_id)
        self.assertEqual(
            tagtag_id, 1
        )
    def test_get_tag_children(self):
        db = PocketDB()

        user = "ethan"
        password = "pizza"
        db.add_user(name=user, password=password)
        user_id = db._get_user_id(name=user)

        db.add_tag(user=user, name="food")
        db.add_tag(user=user, name="fruit")
        db.add_tag(user=user, name="burger")
        db.add_tag(user=user, name="apple")


        db.add_tag_relation(user=user, parent="food", child="fruit")
        db.add_tag_relation(user=user, parent="food", child="burger")

        db.add_tag_relation(user=user, parent="fruit", child="apple")

        def print_tag_id(tag):
            print(tag, db._get_tag_id(user_id=user_id, name=tag))

        print_tag_id("food")
        print_tag_id("fruit")
        print_tag_id("burger")
        print_tag_id("apple")

        def print_children(tag):
            print(
                tag,
                db._get_tag_children(
                    tag_id=db._get_tag_id(user_id=user_id, name=tag)
                )
            )

        print_children("food")
        print_children("fruit")
        print_children("burger")
        print_children("apple")
    def test_get_tag_lineage(self):
        db = PocketDB()

        user = "ethan"
        password = "pizza"
        db.add_user(name=user, password=password)
        user_id = db._get_user_id(name=user)

        db.add_tag(user=user, name="food")
        db.add_tag(user=user, name="fruit")
        db.add_tag(user=user, name="burger")
        db.add_tag(user=user, name="apple")
        db.add_tag(user=user, name="macintosh")


        db.add_tag_relation(user=user, parent="food", child="fruit")
        db.add_tag_relation(user=user, parent="food", child="burger")

        db.add_tag_relation(user=user, parent="fruit", child="apple")
        db.add_tag_relation(user=user, parent="apple", child="macintosh")

        def print_tag_id(tag):
            print(tag, db._get_tag_id(user_id=user_id, name=tag))
        print()
        print()
        print_tag_id("food")
        print_tag_id("fruit")
        print_tag_id("burger")
        print_tag_id("apple")
        print_tag_id("macintosh")

        def print_tag_lineage(tag):
            print(
                f"{tag}\n",
                db._get_tag_lineage(
                    tag_id=db._get_tag_id(user_id=user_id, name=tag),
                    user_id=user_id
                )
            )
        print_tag_lineage("food")
        print_tag_lineage("fruit")
        print_tag_lineage("burger")
        print_tag_lineage("apple")
        print_tag_lineage("macintosh")

        # test loop
        db.add_tag_relation(user=user, parent="macintosh", child="food")
        print_tag_lineage("food")

        # test self parent
        db.add_tag_relation(user=user, parent="food", child="food")
        print_tag_lineage("food")

    def test_get_items_by_tags(self):
        db = PocketDB()

        user = "ethan"
        password = "pizza"
        db.add_user(name=user, password=password)
        user_id = db._get_user_id(name=user)

        db.add_tag(user=user, name="food")
        db.add_tag(user=user, name="fruit")
        db.add_tag(user=user, name="burger")
        db.add_tag(user=user, name="apple")
        db.add_tag(user=user, name="macintosh")


        db.add_tag_relation(user=user, parent="food", child="fruit")
        db.add_tag_relation(user=user, parent="food", child="burger")

        db.add_tag_relation(user=user, parent="fruit", child="apple")
        db.add_tag_relation(user=user, parent="apple", child="macintosh")

        def print_tag_id(tag):
            print(tag, db._get_tag_id(user_id=user_id, name=tag))
        print()
        print()
        print_tag_id("food")
        print_tag_id("fruit")
        print_tag_id("burger")
        print_tag_id("apple")
        print_tag_id("macintosh")

        def print_tag_lineage(tag):
            print(
                f"{tag}\n",
                db._get_tag_lineage(
                    tag_id=db._get_tag_id(user_id=user_id, name=tag),
                    user_id=user_id
                )
            )
        print_tag_lineage("food")
        print_tag_lineage("fruit")
        print_tag_lineage("burger")
        print_tag_lineage("apple")
        print_tag_lineage("macintosh")

        # test loop
        db.add_tag_relation(user=user, parent="macintosh", child="food")
        print_tag_lineage("food")

        # test self parent
        db.add_tag_relation(user=user, parent="food", child="food")
        print_tag_lineage("food")

        apple_item = "green apple"
        apple_path = "https://images.com/green-apple.png"
        db.add_item(user="ethan", name=apple_item, path=apple_path)
        db.assign_tag(user="ethan", tag="apple", item="apple_item")

        db.add_user(name='john', password='pass')
        db.add_tag(name='clothing', user='john')
        db.add_tag(name='headwear', user='john')
        db.add_tag_relation(user='john', parent='clothing', child='headwear')

        db.add_tag(user='john', name='stylish')

        db.add_item(name='hat', path='hat.com', user='john')
        db.assign_tag(user='john', tag='headwear', item='hat')

        db.add_item(name='sunglasses', path='suncentral.net', user='john')
        db.assign_tag(user='john', tag='headwear', item='sunglasses')
        db.assign_tag(user='john', tag='stylish', item='sunglasses')

        print(
            db.get_items_by_tags(user='john', tags=['clothing'])
        )
        print(
            db.get_items_by_tags(user='john', tags=['clothing', 'stylish'])
        )












if __name__ == "__main__":
    test_main()
