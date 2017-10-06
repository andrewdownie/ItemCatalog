#!/usr/bin/env python3

import psycopg2
import random
import sys


MOCK_ITEM = """
INSERT INTO item (name, category_id, description, date_created, user_id, id)
VALUES (%(name)s, %(category_id)s, %(description)s, %(date_created)s, %(user_id)s, %(id)s); 
"""


MOCK_CATEGORY = """
INSERT INTO category (name, description, id)
VALUES (%(name)s, %(description)s, %(id)s);
"""


def InsertMockItems(count):
    conn, cursor = connect_to_db('item_catalog')
    print("Getting the current category id's")
    cursor.execute("SELECT json_agg(json_build_object('id', id)) FROM category")
    categoryIDs = cursor.fetchall()[0][0]
    categoryCount = len(categoryIDs)
    print(categoryIDs)


    if(categoryCount == 0):
        print("\nThere are currently no categories for items to randomly associate to, please add some categories first.")
        print("\nexiting...\n")
        sys.exit()

    print("Inserting " + str(count) + " mock items...")
    for i in range(1, count):
        id = random.randint(1, 1000000)
        category_id = random.randint(0, categoryCount - 1)
        item_name = "item_name_" + str(id)
        date = "2007-12-31"
        print(categoryIDs[category_id]['id'])
        cursor.execute(MOCK_ITEM, {"name": item_name, "category_id": categoryIDs[category_id]['id'], "description": "this is test item desc", "date_created": date, "user_id": 69, "id": id})

    conn.commit()
    conn.close()


def InsertMockCategories(count):
    conn, cursor = connect_to_db('item_catalog')


    print("Inserting " + str(count) +  " mock categories...")
    for i in range(1, count):
        id = random.randint(1, 1000000)
        category_name = "category_name_" + str(id)
        category_description = " category desc " + str(id)
        cursor.execute(MOCK_CATEGORY, {"name": category_name, "description": category_description, "id": id})

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
    print("\n")
    if(len(sys.argv) > 3):
        print("Too many arguments")
        print("\nexiting...\n")
        sys.exit()

    if(len(sys.argv) < 2):
        print("First argument of program missing:")
        print("    enter an integer to choose how many items/categories to add")
        print("\nexiting...\n")
        sys.exit()

    if(len(sys.argv) < 3):
        print("Second argument of program missing, available options are:")
        print("    category")
        print("    item")
        print("\nexiting...\n")
        sys.exit()

    print("Correct number of arguments entered\n")

    amount_to_add = int(sys.argv[1])
    type_to_add = sys.argv[2]
    print("First arg is: " + str(amount_to_add))
    print("Second arg is: " + str(type_to_add))
    print("")

    if(type_to_add == "item"):
        InsertMockItems(amount_to_add)
    elif(type_to_add == "category"):
        InsertMockCategories(amount_to_add)

    print("")
