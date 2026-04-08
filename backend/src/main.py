import db
import logging
import json

def testing():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    engine = db.init()
    test_user = {"name":"jogn", "password":"pass"}

    if not db.user_exists(engine, test_user['name']):
        logger.info(f"User {test_user['name']} does not exist...")
        logger.info(f"Adding User {test_user['name']}...")
        db.add_user(engine, test_user)
    else:
        logger.info(f"User {test_user['name']} already exists...")
    rows = db.get_all_users(engine)
    for row in rows:
        logger.info(row.name)

    logger.info(db.username_matches_password(engine, "jogn", "pass"))

    item = {"name":"burger", "path":"https://burger.com", "user_id": 2}
    item_id = db.add_item(engine, item)
    print(f"item_id: {item_id}")

    tags = [
            {"name":"food", "user_id":2},
            {"name":"delicious", "user_id":2},
            {"name":"lunch", "user_id":2}
    ]
    other_tag = {"name":"lunch","user_id":3}


    db.add_item_with_tags(engine, item, tags)
    print(db.get_items_with_tags(engine, tags))

    child_id = db.get_tag_id(engine, tags[1])
    parent_id = db.get_tag_id(engine, tags[0])
    grandchild_id = db.get_tag_id(engine, tags[2])

    # db.add_tag_relation(engine, child_id, parent_id)
    # db.add_tag_relation(engine, grandchild_id, child_id)

    print(f"children of {parent_id}: {db.get_tag_children(engine, parent_id)}")
    print(f"children of {child_id}: {db.get_tag_children(engine, child_id)}")

    pass

def testing2():
    engine = db.init(filename="")

    ########################################

    tag_names = [
        "food",
        "apple",
        "fruit",
        "burger"
    ]
    user_id = 0
    tags = {}
    for name in tag_names:
        tags[name] = {"name":name, "user_id":user_id}

    print(json.dumps(tags, indent=4))
    db.add_tags(engine, list(tags.values()))
    tag_ids = db.get_tag_ids(engine, list(tags.values()))

    idx = 0
    for key, value in zip(tags.keys(), tags.values()):
        value['id'] = tag_ids[idx]
        idx+=1

    print(
        json.dumps(
            list(tags.values()),
            indent=4
        )
    )
    with engine.connect() as conn:
        print(
            conn.execute(
                db.select(db.Tag)
            ).all()
        )

    db.add_tag_relation(engine=engine, parent_id=tags['food']['id'], child_id=tags['fruit']['id'])
    db.add_tag_relation(engine=engine, parent_id=tags['fruit']['id'], child_id=tags['apple']['id'])
    db.add_tag_relation(engine=engine, parent_id=tags['apple']['id'], child_id=tags['fruit']['id'])
    def print_children(parent_id):
        with engine.connect() as conn:
            print(
                conn.execute(
                    db.select(db.Tag.name)
                    .join(db.TagTag, db.Tag.id == db.TagTag.child_id)
                    .where(db.TagTag.parent_id == parent_id)
                ).all()
            )
    print("print_children")
    print_children(tags['fruit']['id'])
    print_children(tags['food']['id'])
    print_children(tags['burger']['id'])
    print("get_tag_children")
    print(db.get_tag_children(engine, tags['fruit']['id']))
    print(db.get_tag_children(engine, tags['food']['id']))
    print(db.get_tag_children(engine, tags['burger']['id']))
    print("get_tag_descendents")
    print(db.get_tag_descendents(engine, tags['food']['id'], []))
    print(db.get_tag_descendents(engine, tags['fruit']['id'], []))
    print(db.get_tag_descendents(engine, tags['burger']['id'], []))
    ########################################

    items = {

    }

    engine.dispose()
if __name__ == "__main__":
    testing2()
