#!/usr/bin/env python3

import psycopg2
import random
import sys


MOCK_ITEM = """
INSERT INTO item (name, category_id, description, date_created, user_id)
VALUES (%(name)s, %(category_id)s, %(description)s, %(date_created)s, %(user_id)s); 
"""


MOCK_CATEGORY = """
INSERT INTO category (name, description)
VALUES (%(name)s, %(description)s);
"""


MOCK_USER = """
INSERT INTO users (name, email)
VALUES (%(name)s, %(email)s);
"""


def InsertMockItems(count):
    conn, cursor = connect_to_db('item_catalog')
    print("Getting the current category id's")
    cursor.execute("SELECT json_agg(json_build_object('id', id)) FROM category")
    categoryIDs = cursor.fetchall()[0][0]
    categoryCount = len(categoryIDs)
    #print(categoryIDs)

    print("Getting the current user id's")
    cursor.execute("SELECT json_agg(json_build_object('id', id)) FROM users")
    userIDs = cursor.fetchall()[0][0]
    userCount = len(userIDs)


    if(categoryCount == 0):
        print("\nthere are currently no categories for items to randomly associate to, please add some categories first.")
        print("\nexiting...\n")
        sys.exit()
    if(userCount == 0):
        print("\nthere are currently no users for items to randomly associate to, please add some users first.")
        print("\nexiting...\n")
        sys.exit()

    print("Inserting " + str(count) + " mock items...")
    for i in range(1, count):
        item_name = "item_name_" + str(random.randint(0, 10000))
        date = "2007-12-31"

        category_index = random.randint(0, categoryCount - 1)
        CATEGORY_ID = categoryIDs[category_index]['id']

        user_index = random.randint(0, userCount - 1)
        USER_ID = userIDs[user_index]['id']

        cursor.execute(MOCK_ITEM, {"name": item_name, "category_id": CATEGORY_ID, "description": "this is test item desc", "date_created": date, "user_id": USER_ID})

    conn.commit()
    conn.close()


def InsertMockCategories(count):
    conn, cursor = connect_to_db('item_catalog')


    print("Inserting " + str(count) +  " mock categories...")
    for i in range(1, count):
        rand_name = random.randint(0, 10000)
        category_name = "category_name_" + str(rand_name)
        category_description = " category desc " + str(rand_name)
        cursor.execute(MOCK_CATEGORY, {"name": category_name, "description": category_description})

    conn.commit()
    conn.close()


def InsertMockUsers(count):
    conn, cursor = connect_to_db('item_catalog')


    print("Inserting " + str(count) +  " mock users...")
    for i in range(1, count):
        rand_name = random.randint(0, 10000)
        user_name = "user_name_" + str(rand_name)
        user_email = "user_email_" + str(rand_name)
        cursor.execute(MOCK_USER, {"name": user_name, "email": user_email})

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
        print("    user")
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
    elif(type_to_add == "user"):
        InsertMockUsers(amount_to_add)

    print("")
