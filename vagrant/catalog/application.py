#!/usr/bin/env python3

import psycopg2

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

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)