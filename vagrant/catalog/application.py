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
def view_recent_items():
    return render_template('index.html', current_category="Recent Items", categories=get_categories(), items=get_recent_items())


@app.route("/catalog/<category_name>/items", methods=["GET"])
def view_category_items(category_name):
    return render_template('index.html', current_category=category_name, categories=get_categories(), items=get_category_items(category_name))


@app.route("/catalog/<category_name>/<item_name>", methods=["GET"])                                                    
def view_single_item(category_name, item_name):
    return render_template('item.html', single_item=get_single_item(category_name, item_name))


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
@app.route("/catalog/items", methods=["GET"])
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

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response







#####
#####
#####                   Main
#####
#####
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)