import re
import datetime
import random

import psycopg2
import json

import flask
from flask import render_template
from flask import request

import httplib2

# To install apiclient: sudo pip install google-api-python-client
from apiclient import discovery
from oauth2client import client


app = flask.Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

"""
    Html Routing ----------------------------------------------------
"""


@app.route('/logout')
def logout():
    # When a user navigates to /logout, delete their credentials
    # in their session variable, and redirect them to index
    print("logout")
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return flask.redirect(flask.url_for('view_recent_items'))


@app.route('/oauth2callback')
def oauth2callback():
    # Handle logging the user in with Google

    # Setup a client flow in order to login
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=flask.url_for('oauth2callback', _external=True))

    # If they haven't logged in yet, do so now first,
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    # Otherwise exchange auth code for a token, and then go to index
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('view_recent_items'))


@app.route("/")
@app.route("/index.html")
def view_recent_items():
    # Render the index page, grabbing categories and recent items to do so
    return render_template('index.html',
                           active_link="index",
                           user_email=get_user_email(),
                           current_category="Recent Items",
                           categories=get_categories(),
                           items=get_recent_items())


@app.route("/catalog/<category_name>/items", methods=["GET"])
def view_category_items(category_name):
    # Render all items of a specific category
    return render_template('index.html',
                           active_link="index",
                           user_email=get_user_email(),
                           current_category=category_name,
                           categories=get_categories(),
                           items=get_category_items(category_name))


@app.route("/catalog/<category_name>/<item_name>", methods=["GET"])
def view_single_item(category_name, item_name):
    # Render a specific item
    return render_template('item.html',
                           active_link="index",
                           user_email=get_user_email(),
                           single_item=get_single_item(category_name,
                                                       item_name))


@app.route("/manage.html")
def manage_items():
    # Render a users items to allow them to manage the items they own
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('view_recent_items'))
    return render_template('manage.html',
                           active_link="manage",
                           categories=get_categories(),
                           user_email=get_user_email(),
                           items=get_owned_items())

"""
    Database functions ----------------------------------------------
"""


def get_items():
    # Get all items from the database along with category names in json
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

    results = strip_containers(cursor.fetchall())

    conn.close()
    return results


def get_category_items(category_name):
    # Get all items of a specific type from the database in json
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
        {'category_name': category_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

    return results


def get_single_item(category_name, item_name):
    # Get all info about a single item
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
        {'category_name': category_name, 'item_name': item_name})

    results = strip_containers(cursor.fetchall())
    cursor.close()

    return results


def get_recent_items():
    # Get the 10 most recently created items
    conn, cursor = connect_to_db("item_catalog")
    cursor.execute(
        """
        SELECT json_agg(json_build_object(
            'item_name', recent_items.item_name,
            'category_name', recent_items.category_name,
            'description', recent_items.description,
            'date_created', CAST(recent_items.date_created AS TEXT),
            'item_id', recent_items.id
        ))
        FROM
            (SELECT
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
    # Get all categories
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


def get_owned_items():
    # Get all items owned by a specific user
    conn, cursor = connect_to_db("item_catalog")
    select_owned_items = """
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
        ON item.category_id = category.id
        INNER JOIN users
        ON item.user_id = users.id
        WHERE users.email = %(email)s;
        """
    cursor.execute(
        select_owned_items,
        {"email": get_user_email()}
    )

    results = strip_containers(cursor.fetchall())
    if(results):
        results.reverse()

    conn.close()
    return results


def create_item(name, category_id, description):
    # Create a new item for a specific user
    errors = []

    print("create item pls")
    conn, cursor = connect_to_db("item_catalog")

    if 'credentials' not in flask.session:
        print("user not logged in!")
        errors.append("User is not logged in.")
        return json.dumps({"status": "failure", "messages": errors})

    # Check to make sure name, category and description are valid
    name = str(name)
    if(valid_item_name(name) is False):
        errors.append(
            """Item names can only contain alphanumeric characters,
             dashes and underscores.""")
        return json.dumps({"status": "failure", "messages": errors})

    description = str(description)
    category_id = int(category_id)

    date_created = datetime.date.today()
    print(date_created)

    # Check to make sure an item doesn't already exist with this name
    cursor.execute("""
    SELECT
        COUNT(*)
    FROM item
    WHERE item.name= %(name)s;
    """, {"name": name})
    count = strip_containers(cursor.fetchall())
    print("Count was: " + str(count))

    if(count != 0):
        errors.append("Item with that name already exists.")
        return json.dumps({"status": "failure", "messages": errors})

    # Get the users id that is currently logged in from their email address
    user_email = get_user_email()
    user_id = get_user_id(cursor)
    print("creator is: " + str(user_id))

    # Check if the item name already exists
    cursor.execute("""
    SELECT id FROM item WHERE name=%(item_name)s;
    """, {"item_name": name})

    # TODO: check if a result was returned-----------------------"
    # if a result was returned, abort with failure

    cursor.execute("""
    INSERT INTO item
    (name, category_id, description, date_created, user_id)
    VALUES (%(name)s,
            %(category_id)s,
            %(description)s,
            %(date_created)s,
            %(user_id)s)
    """, {"name": name,
          "category_id": category_id,
          "description": description,
          "date_created": date_created,
          "user_id": user_id})
    conn.commit()

    cursor.execute("SELECT LASTVAL();")
    lastid = str(cursor.fetchone()[0])

    conn.close()

    if(len(errors) == 0):
        return json.dumps(
            {"status": "success",
             "messages":
             ["Successfully created item"], "item_id": lastid})

    return json.dumps(
        {"status":
         "failure",
         "messages":
         ["Unhandled error occurred!"]})


def edit_item(id, name, category_id, description):
    # Edit a specific users item
    messages = []

    conn, cursor = connect_to_db("item_catalog")

    if 'credentials' not in flask.session:
        messages.append("User not logged in.")
        return json.dumps({"status": "failure", "messages": messages})

    #  Check to make sure name, category and description are valid
    name = str(name)
    if(valid_item_name(name) is False):
        messages.append("""Item names can only contain alpha
            numeric characters, dashes and spaces.""")
        return json.dumps({"status": "failure", "messages": messages})

    description = str(description)
    category_id = int(category_id)
    id = int(id)
    user_email = get_user_email()

    # Get the users id that is currently logged in from their email address
    user_id = get_user_id(cursor)
    print("creator is: " + str(user_id))

    # Make sure the user owns this item
    cursor.execute("""
    SELECT json_agg(json_build_object(
        'owner_id', user_id
    ))
    FROM item
    WHERE id=%(item_id)s;
    """, {"item_id": id})

    owner_id = strip_containers(cursor.fetchall())[0]['owner_id']

    if(owner_id != user_id):
        print("User does not own this item!")
        return json.dumps(
            {"status":
             "failure",
             "messages":
             ["User does not own the item they are trying to edit!"]})

    cursor.execute(
        """
        UPDATE item
        SET name = %(name)s,
            category_id = %(category_id)s,
            description = %(description)s
        WHERE id=%(item_id)s
        """,
        {
            "name": name,
            "category_id": category_id,
            "description": description,
            "item_id": id
        }
    )

    conn.commit()
    print("update item pls -- after commit")

    conn.close()

    print('pre final return')
    return json.dumps({"status": "success", "messages": messages})


def delete_item(id):
    # Delete an item for a specific user in json
    messages = []

    conn, cursor = connect_to_db("item_catalog")

    if 'credentials' not in flask.session:
        messages.append("User not logged in.")
        return json.dumps({"status": "failure", "messages": messages})

    id = int(id)

    # Get the users id that is currently logged in from their email address
    user_id = get_user_id(cursor)
    print("creator is: " + str(user_id))

    # Make sure the user owns this item
    cursor.execute("""
    SELECT json_agg(json_build_object(
        'owner_id', user_id
    ))
    FROM item
    WHERE id=%(item_id)s;
    """, {"item_id": id})

    owner_id = strip_containers(cursor.fetchall())[0]['owner_id']

    if(owner_id != user_id):
        print("User does not own this item!")
        return json.dumps(
            {"status":
                "failure",
                "messages":
                ["User does not own the item they are trying to delete!"]})

    cursor.execute("""
    DELETE FROM item
    WHERE id=%(item_id)s
    """, {"item_id": id})

    conn.commit()
    print("update item pls -- after commit")

    conn.close()

    print('pre final return')
    return json.dumps({"status": "success", "messages": messages})


def get_items_by_category():
    # Get all items sorted by which category they belong to in json
    conn, cursor = connect_to_db("item_catalog")

    cursor.execute("""
    SELECT json_agg(json_build_object(
        'id', category.id,
        'name', category.name,
        'Item',
            (
            SELECT json_agg(json_build_object(
                'name', item_contents.name,
                'id', item_contents.id
                ))
                FROM item
                AS item_contents
                WHERE category.id = item_contents.category_id
            )
    ))
    FROM category;
    """)

    print("Get items sorted by category")
    result_json = strip_containers(cursor.fetchall())
    result = json.dumps(result_json)
    result_container = {"Category": result_json}

    conn.close()
    return (result_container)

"""
    Rest API --------------------------------------------------------
"""


@app.route("/catalog/createitem", methods=["POST"])
def rest_create_item():
    # Rest function to create an item for a user
    # Does validation of sent data, and then calls create_item function
    messages = []

    data = request.data
    loaded_data = json.loads(data)

    if(loaded_data["name"] is None):
        messages.append("Missing json key: name")

    if(loaded_data["category"] is None):
        messages.append("Missing json key: category")

    if(loaded_data["description"] is None):
        messages.append("Missing json key: description")

    if(len(messages) == 0):
        name = str(loaded_data["name"])
        category = int(loaded_data["category"])
        description = str(loaded_data["description"])

        print('pre create item call')

        return create_item(name, category, description)

    return json.dumps({"messages": ["fake message"]})


@app.route("/catalog/edititem", methods=["POST"])
def rest_edit_item():
    # Rest function to edit an item for a user
    # Does validation of sent data, and then calls edit_item function
    errorList = []

    data = request.data
    loaded_data = json.loads(data)

    if("name" not in loaded_data):
        errorList.append("Missing json key: name")

    if("category" not in loaded_data):
        errorList.append("Missing json key: category")

    if("description" not in loaded_data):
        errorList.append("Missing json key: description")

    if("item_id" not in loaded_data):
        errorList.append("Missing json key: item_id")

    if(len(errorList) == 0):
        name = str(loaded_data["name"])
        category = int(loaded_data["category"])
        description = str(loaded_data["description"])
        item_id = str(loaded_data["item_id"])
        return edit_item(item_id, name, category, description)

    return json.dumps({"messages": errorList})


@app.route("/catalog/deleteitem", methods=["POST"])
def rest_delete_item():
    # Rest function to delete an item for a user
    # Does validation of sent data, and then calls delete_item function
    errorList = []

    data = request.data
    loaded_data = json.loads(data)

    if("item_id" not in loaded_data):
        errorList.append("Missing json key: item_id")

    if(len(errorList) == 0):
        item_id = str(loaded_data["item_id"])
        return delete_item(item_id)

    return json.dumps({"messages": errorList})


@app.route("/catalog/item", methods=["GET"])
def rest_get_items():
    # Gets all items, and returns it as json string
    return json.dumps(get_items())


@app.route("/catalog/<category_name>/items", methods=["GET"])
def rest_get_category_items(category_name):
    # Gets all items of a specific category
    # and returns it as a json string
    return json.dumps(get_category_items())


@app.route("/catalog/<category_name>/<item_name>", methods=["GET"])
def rest_get_single_item(category_name, item_name):
    # Gets all info about a single item
    # and returns it as a json string
    return json.dumps(get_single_item(category_name, item_name))


@app.route("/recent-items", methods=["GET"])
def rest_get_recent_items():
    # Get the top 10 most recent items
    # and returns it as a json string
    return json.dumps(get_recent_items())


@app.route("/catalog/categories", methods=["GET"])
def rest_get_categories():
    # Gets all of the item categoris
    # and returns them as a json string
    return json.dumps(get_categories())


@app.route("/catalog.json", methods=["GET"])
def rest_json_endpoint():
    # Gets all items sorted by their category,
    # and returns them as a json string
    return json.dumps(get_items_by_category())

"""
    Helper Functions ------------------------------------------------
"""


def get_user_id(cursor):
    # Get the users id that is currently logged in from their email address
    user_id = None
    user_email = get_user_email()

    cursor.execute("""
    SELECT json_agg(json_build_object(
        'user_id', id
    ))
    FROM users
    WHERE users.email = %(email)s;
    """, {"email": user_email})

    user_id = strip_containers(cursor.fetchall())[0]['user_id']
    return user_id


def connect_to_db(db_name):
    # Connects to the database
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
    # Gets the users email address, requires they be signed in
    if 'credentials' in flask.session:
        return json.loads(flask.session['credentials'])['id_token']['email']
    return None


def valid_item_name(item_name):
    # Checks to make sure the item name is valid
    reg = re.compile('^[a-zA-Z0-9_-]+$')
    match = reg.match(item_name)
    if(match is None):
        print("item name " + item_name + " is not valid")
        return False
    print("valid item name")
    return True


"""
    OAuth Functions -------------------------------------------------
"""


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

"""
    Main ------------------------------------------------------------
"""
if __name__ == '__main__':
    # TODO: this is directy from the google guides
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.run(host='0.0.0.0', port=8000)
