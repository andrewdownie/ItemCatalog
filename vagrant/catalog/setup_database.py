#!/usr/bin/env python3

import psycopg2


ITEM_TABLE = """
    CREATE TABLE item(
        name text NOT NULL UNIQUE,
        category_id integer,
        description text,
        date_created date,
        id SERIAL,
        user_id integer,
        PRIMARY KEY  (id)
    );
"""


CATEGORY_TABLE = """
    CREATE TABLE category(
        name text,
        description text,
        id SERIAL,
        PRIMARY KEY (id)
    );
"""


USER_TABLE = """
    CREATE TABLE users(
        email text,
        id SERIAL,
        PRIMARY KEY (id)
    );
"""

ADD_CATEGORY = """
INSERT INTO category
(name, description)
VALUES(%(name)s, %(description)s);
"""


def create_tables():
    conn, cursor = connect_to_db("item_catalog")

    cursor.execute(USER_TABLE)
    cursor.execute(CATEGORY_TABLE)
    cursor.execute(ITEM_TABLE)

    cursor.execute(ADD_CATEGORY, {"name": "Tools", "description": "These are tools."})
    cursor.execute(ADD_CATEGORY, {"name": "Office Supplies", "description": "These are office supplies."})
    cursor.execute(ADD_CATEGORY, {"name": "Food", "description": "Edible items."})
    cursor.execute(ADD_CATEGORY, {"name": "Kitchen", "description": "Everything you need for cooking."})
    cursor.execute(ADD_CATEGORY, {"name": "Outdoors", "description": "This is camping stuff."})
    cursor.execute(ADD_CATEGORY, {"name": "Electronics", "description": "Computers and phones."})

    conn.commit()
    conn.close()

def connect_to_db(db_name):
    try:
        conn = psycopg2.connect('dbname=' + str(db_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Error connecting to database...")


if __name__ == '__main__':
    create_tables()

