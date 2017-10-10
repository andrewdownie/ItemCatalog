#!/usr/bin/env python3

import psycopg2
import json

import flask
from flask import render_template

# From oauth tutorial
"""
from flask import request
from flask import redirect
from flask import jsonify
from flask import url_for
from flask import flash
#from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
#import httplib2
import json
import requests
"""


# From google's tutorials
import httplib2

from apiclient import discovery #pip install google-api-python-client
from oauth2client import client


app = flask.Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
#APPLICATION_NAME = "FSND Item Catalog Client ID"



#####
#####
#####                   Html Routing
#####
#####
@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      scope='https://www.googleapis.com/auth/userinfo.email',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
      #deleted 'include granted scopes'
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('view_recent_items'))


@app.route("/")
@app.route("/index.html")
def view_recent_items():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        """
        drive = discovery.build('drive', 'v2', http_auth)
        files = drive.files().list().execute()
        return json.dumps(files)
        """
        return render_template('index.html', active_link="index", user_email=get_user_email(), current_category="Recent Items", categories=get_categories(), items=get_recent_items())


@app.route("/catalog/<category_name>/items", methods=["GET"])
def view_category_items(category_name):
    return render_template('index.html', active_link="index", user_email=get_user_email(), current_category=category_name, categories=get_categories(), items=get_category_items(category_name))


@app.route("/catalog/<category_name>/<item_name>", methods=["GET"])                                                    
def view_single_item(category_name, item_name):
    return render_template('item.html', active_link="index", user_email=get_user_email(), single_item=get_single_item(category_name, item_name))


@app.route("/manage.html")
def manage_items():
    return render_template('manage.html', active_link="manage", user_email=get_user_email(), items=get_items())


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
            'item_name', item.name, 
            'category_name', category.name,
            'category_id', category_id, 
            'description', item.description,
            'date', CAST(date_created AS TEXT), 
            'item_id', item.id
        ))
        FROM item
        INNER JOIN category
        ON item.category_id = category.id;
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
        'item_name', item.name,
        'category_name', category.name,
        'description', item.description,
        'date_created', CAST(item.date_created AS TEXT),
        'item_id', item.id
    ))
    FROM item
    INNER JOIN category
    ON category.id = item.category_id
    WHERE category.name=%(category_name)s;
    """,
    {'category_name' : category_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

    return results


def get_single_item(category_name, item_name):
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
    """
    SELECT json_agg(json_build_object(
        'item_name',        named_item.item_name,
        'category_name',    named_item.category_name,
        'description',      named_item.item_description,
        'date_created',     CAST(named_item.item_date_created AS TEXT),
        'item_id',          named_item.item_id,
        'category_id',      named_item.category_id
    ))
    FROM 
        (
            SELECT
                item.id AS item_id,
                item.name AS item_name,
                item.description AS item_description,
                item.date_created AS item_date_created,
                category.id AS category_id,
                category.name AS category_name 
            FROM item
            INNER JOIN category
            ON category.id=item.category_id
            WHERE
                item.name=%(item_name)s
                AND
                category.name=%(category_name)s
            LIMIT 1
        ) AS named_item;
    """,
    {'category_name' : category_name, 'item_name': item_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

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
            item.name AS item_name, 
            item.description,
            item.date_created,
            item.id,
            category.name AS category_name,
            category.description AS category_description
            FROM item
            INNER JOIN category
                ON category_id = category.id
            ORDER BY date_created LIMIT 10
        ) AS recent_items
    """)
    results = strip_containers(cursor.fetchall())
    conn.close()

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

    conn.close()
    return results


#####
#####
#####                   Rest API
#####
#####
@app.route("/catalog/item", methods=["GET"])
def rest_get_items():
    return json.dumps(get_items())


@app.route("/catalog/<category_name>/items", methods=["GET"])
def rest_get_category_items(category_name):
    return json.dumps(get_category_items())


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


def get_user_email():
    if 'credentials' in flask.session:
        return json.loads(flask.session['credentials'])['id_token']['email']
    return None


#####
#####
#####                   OAuth Functions
#####
#####
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)







#####
#####
#####                   Main
#####
#####
if __name__ == '__main__':
    #TODO: this is directy from the google guides
    import uuid
    app.secret_key = str(uuid.uuid4())
  
    app.run(host='0.0.0.0', port=8000)