#!/usr/bin/env python3

import psycopg2
import random


MOCK_ITEM = """
INSERT INTO items (name, category_id, description, date_created, id)
VALUES (%(name)s, %(category_id)s, %(description)s, %(date_created)s, %(id)s); 
"""


MOCK_CATEGORY = """
INSERT INTO category (name, id)
VALUES (%(name)s, %(id)s);
"""


def InsertMockItems(count):
    conn, cursor = connect_to_db('item_catalog')

    print("Inserting " + str(count) + " mock items...")
    for i in range(1, count):
        id = random.randint(1, 1000000)
        item_name = "item name " + str(id)
        date = "2007-12-31"
        cursor.execute(MOCK_ITEM, {"name": item_name, "category_id": 1234, "description": "this is test item desc", "date_created": date, "id": id})

    conn.commit()
    conn.close()


def InsertMockCategories(count):
    conn, cursor = connect_to_db('item_catalog')

    print("Inserting " + str(count) +  " mock categories...")
    for i in range(1, count):
        id = random.randint(1, 1000000)
        category_name = "item name " + str(id)
        cursor.execute(MOCK_CATEGORY, {"name": category_name, "id": id})

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
    InsertMockItems(10)
    #InsertMockCategories(4)
