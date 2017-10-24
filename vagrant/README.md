# About this project
This project requires vagrant, and virtual box:

https://www.vagrantup.com/ 

https://www.virtualbox.org/wiki/Downloads


## Outline
The purpose of this project is to allow users to view items in a catalog format. Users can login with a third-party OAuth provider to add, edit and delete items to/from the catalog.

### The database has three tables:
1. users - holds info about users. Links their email address from the third-party OAuth provider to the items they own.
2. item - holds info about items. Including: name, description, category id, owner.
3. category - holds info about categories. Links category id to its name and description.

### User interaction with the site
If the user is not logged in, they can visit the index page to:
- log in
- view the most recently added items
- view the list of all categoies
- choose a category to view all items in that category
- chose an item to view that items description

If the user logs in, they can do everything a logged out user can do on the index page. They can also visit the manage page to:
- view items they've created
- create new items
- edit items they've created
- delete items they've created



# Getting started with this project
## Copying the vagrant environment
It is assumed you already have virtual box and vagrant installed.
### Download the vagrant environment file:
Clone (or download) the vagrant setup from here (unzip it if needed).
https://github.com/udacity/fullstack-nanodegree-vm
### Copy this projects files into the vagrant directory
Copy the following 5 files and folders into the /vagrant folder of the fullstack-nanodegree-vm-master repo:
application.py
setup_database.py,
client_secrets.json
static/
templates/
### Run the vagrant environment
With a terminal, navigate to the /vagrant folder in the fullstack-nanodegree-vm-master repo you downloaded in the first step, and run the command:
```bash
vagrant up
```
It will now download the vagrant environment.
### Ssh into the vagrant environment:
Once the ```vagrant up``` command from the previous step has completed, run:
```bash
vagrant ssh
```
You are now ready to setup the database.
## Setting up the database
### Create the database:
To create the database for this project, we will need to enter three commands on the command line in the vagrant ssh session:
First, enter psql by typing the command:
```
psql
```
Second, create the database with the command:
```
CREATE DATABASE item_catalog;
```
Finally, exit psql with the command:
```
\q
```
### Install Google OAuth python tools
from withing the vagrant ssh session, run:
```
sudo pip install google-api-python-client
```
### Setup the database tables:
from within the vagrant ssh session, run: 
```
python /vagrant/catalog/setup_database.py
```
### Run the application
From within vagrant, run:
```
python /vagrant/catalog/application.py
```
### Visit the website
In your host OS open a webbrowser, and navigate to the url
```
localhost:8000
```
You should now be able to view and use the website.
