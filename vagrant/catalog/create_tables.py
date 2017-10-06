#!/usr/bin/env python3

import psycopg2


ITEM_TABLE = """
    CREATE TABLE item(
        name text,
        category_id integer,
        description text,
        date_created date,
        id integer,
        user_id integer
    );
"""


CATEGORY_TABLE = """
    CREATE TABLE category(
        name text,
        description text,
        id integer
    );
"""


USER_TABLE = """
    CREATE TABLE users(
        name text,
        email text,
        id integer
    );
"""


def create_tables():
    conn, cursor = connect_to_db('item_catalog')

    cursor.execute(USER_TABLE)
    cursor.execute(CATEGORY_TABLE)
    cursor.execute(ITEM_TABLE)

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

