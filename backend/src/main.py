import db
import logging

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
    pass

if __name__ == "__main__":
    testing()
