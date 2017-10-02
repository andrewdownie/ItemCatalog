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

    """
    mock_categories = [
      {"category_name": "Recent Items"},
      {"category_name": "Tools"},
      {"category_name": "Food"},
      {"category_name": "Kitchen"}
    ]
    """

    mock_categories = get_recent_items()

    return render_template('index.html', categories=mock_categories, items=get_recent_items())

@app.route("/manage.html")
def manage_items():

    """
    mock_items = [
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"}
    ]
    """

    mock_items = get_items()

    return render_template('manage.html', items=mock_items)

@app.route("/login.html")
def login():
    return render_template('login.html')

def connect_to_db(db_name):
    try:
        conn = psycopg2.connect('dbname=' + str(db_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Error connecting to database...")


#####
#####
#####                   Rest API
#####
#####

@app.route("/items", methods=["GET"])
def get_items():
    conn, cursor = connect_to_db("item_catalog")
    #cursor.execute("SELECT name, category_id, description, CAST(date_created AS TEXT), id FROM items LIMIT 10;")
    cursor.execute(
        """
        SELECT json_agg(json_build_object(
            'item_name', name, 
            'category_name', 'DEFAULT_CAT_NAME',
            'category_id', category_id, 
            'description', description,
            'date', CAST(date_created AS TEXT), 
            'item_id', id
        ))
        FROM items LIMIT 10;
        """
    )

    fetchAll= cursor.fetchall()
    results = fetchAll[0][0]
    print(results)

    conn.close()
    return results 


@app.route("/recent-items", methods=["GET"])
def get_recent_items():
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
    """
    SELECT json_agg(json_build_object(
        'item_name', items.name, 
        'category_name', 'DEFAULT_CAT_NAME',
        'description', description,
        'date_created', CAST(date_created AS TEXT), 
        'item_id', items.id))
    FROM items 
    INNER JOIN category
    ON category_id = category.id
    ORDER BY date_created LIMIT 10;
    """)

    json_string = list(cursor.fetchall())
    print(json_string)

    conn.close()
    return json_string


@app.route("/category", methods=["GET"])
def get_category():
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute("SELECT * FROM category LIMIT 10;")

    json_string = json.dumps(cursor.fetchall())

    conn.close()
    return json_string





if __name__ == '__main__':
  get_items()
  app.run(host='0.0.0.0', port=8000)