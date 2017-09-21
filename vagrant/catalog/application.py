#!/usr/bin/env python3

import psycopg2
import json

from flask import Flask
from flask import render_template 
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
@app.route("/index.html")
def view_items():

    mock_categories = [
      {"category_name": "Recent Items"},
      {"category_name": "Tools"},
      {"category_name": "Food"},
      {"category_name": "Kitchen"}
    ]


    mock_items = [
      {"item_name": "Hammer",   "category_name": "Tools"},
      {"item_name": "Apple",   "category_name": "Food"},
      {"item_name": "Banana",   "category_name": "Food"},
      {"item_name": "Pear",   "category_name": "Food"},
      {"item_name": "Blender", "category_name": "Kitchen"}
    ]


    return render_template('index.html', categories=mock_categories, items=mock_items)

@app.route("/manage.html")
def manage_items():

    mock_items = [
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"},
      {"item_name": "Taco", "category_name": "Food", "id": "abcid", "desc": "This... this is a taco, what else do you really really really really need to know?"}
    ]

    return render_template('manage.html', items=mock_items)


def connect_to_db(db_name):
    try:
        conn = psycopg2.connect('dbname=' + str(db_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print("Error connecting to database...")


@app.route("/items")
def get_items():
    conn, cursor = connect_to_db("item_catalog")

    cursor.execute("SELECT * FROM items LIMIT 10;")

    #array_to_json(array_agg(t))
    json_string = json.dumps(cursor.fetchall())
    print(json_string)

    conn.close()

    return json_string

  

if __name__ == '__main__':
  get_items()
  app.run(host='0.0.0.0', port=8000)