#!/usr/bin/env python3

import psycopg2
import json

from flask import Flask
from flask import render_template 
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#####
#####
#####                   Html Routing
#####
#####

@app.route("/")
@app.route("/index.html")
def view_items():
    return render_template('index.html', categories=get_categories(), items=get_recent_items())


@app.route("/manage.html")
def manage_items():
    return render_template('manage.html', items=get_items())


@app.route("/login.html")
def login():
    return render_template('login.html')


#####
#####
#####                   Database functions
#####
#####
def get_items():
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
        """
        SELECT json_agg(json_build_object(
            'item_name', items.name, 
            'category_name', category.name,
            'category_id', category_id, 
            'description', items.description,
            'date', CAST(date_created AS TEXT), 
            'item_id', items.id
        ))
        FROM items
        INNER JOIN category
        ON items.category_id = category.id;
        """
    )

    fetchAll= cursor.fetchall()
    results = fetchAll[0][0]

    conn.close()
    return results 

def get_category_items(category_name):
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
    """
    SELECT json_agg(json_build_object(
        'item_name', items.name,
        'category_name', category.name,
        'description', items.description,
        'date_created', CAST(items.date_created AS TEXT),
        'item_id', items.id
    ))
    FROM items
    INNER JOIN category
    ON category.id = items.category_id
    WHERE category.name=%(category_name)s;
    """,
    {'category_name' : category_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

    print("Printing get cetegory items results")
    print(results)

    return results

def get_single_item(category_name, item_name):
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
    """
    SELECT json_agg(json_build_object(
        'item_name',        named_items.item_name,
        'category_name',    named_items.category_name,
        'description',      named_items.item_description,
        'date_created',     CAST(named_items.item_date_created AS TEXT),
        'item_id',          named_items.item_id,
        'category_id',      named_items.category_id
    ))
    FROM 
        (
            SELECT
                items.id AS item_id,
                items.name AS item_name,
                items.description AS item_description,
                items.date_created AS item_date_created,
                category.id AS category_id,
                category.name AS category_name 
            FROM items
            INNER JOIN category
            ON category.id=items.category_id
            WHERE
                items.name=%(item_name)s
                AND
                category.name=%(category_name)s
            LIMIT 1
        ) AS named_items;
    """,
    {'category_name' : category_name, 'item_name': item_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

    print("Printing get single item results:")
    print(results)

    return results

def get_recent_items():
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
    """
    SELECT json_agg(json_build_object(                      -- 2) Package these items into json
        'item_name', recent_items.item_name, 
        'category_name', recent_items.category_name, 
        'description', recent_items.description,
        'date_created', CAST(recent_items.date_created AS TEXT), 
        'item_id', recent_items.id
    ))
    FROM 
        (SELECT                                             -- 1) Select the items we need
            items.name AS item_name, 
            items.description,
            items.date_created,
            items.id,
            category.name AS category_name,
            category.description AS category_description
            FROM items
            INNER JOIN category
                ON category_id = category.id
            ORDER BY date_created LIMIT 10
        ) AS recent_items
    """)
    results = strip_containers(cursor.fetchall())
    conn.close()
    #print("Printing recent items")
    #print(results)

    return results 

def get_categories():
    conn, cursor = connect_to_db("item_catalog")

    cursor.execute("""
    SELECT json_agg(json_build_object(
        'category_name', name,
        'category_id', id
    )) 
    FROM category;
    """)

    results = strip_containers(cursor.fetchall())

    print("Printing categories...")
    print(results)

    conn.close()
    return results

#####
#####
#####                   Rest API
#####
#####
@app.route("/catalog/items", methods=["GET"])
def rest_get_items():
    return json.dumps(get_items())

@app.route("/catalog/<category_name>/items", methods=["GET"])
def rest_get_category_items(category_name):
    return json.dumps(get_category_items(category_name))

@app.route("/catalog/<category_name>/<item_name>", methods=["GET"])                                                    
def rest_get_single_item(category_name, item_name):
    return json.dumps(get_single_item(category_name, item_name))

@app.route("/recent-items", methods=["GET"])
def rest_get_recent_items():
    return json.dumps(get_recent_items())

@app.route("/catalog/categories", methods=["GET"])
def rest_get_categories():
    return json.dumps(get_categories())


#####
#####
#####                   Helper Functions
#####
#####
def connect_to_db(db_name):
    try:
        conn = psycopg2.connect('dbname=' + str(db_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Error connecting to database...")


def strip_containers(cursor_fetchall):
    """
    Strips the outter list and tuple that psql returns
    when it packages results into json when using 
    json_agg(json_build_object(...))
    """
    return cursor_fetchall[0][0]


#####
#####
#####                   Main
#####
#####
if __name__ == '__main__':
    get_single_item("test-cat-name", "item name 553368")
    #get_category_items(1234)
    app.run(host='0.0.0.0', port=8000)