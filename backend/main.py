import db
import logging
if __name__ == "__main__":
    pass

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
    pass
