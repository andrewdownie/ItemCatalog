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
## Setting up the vagrant environment
It is assumed you already have virtual box and vagrant installed.
### Download the vagrant environment file:
Download the vagrant environment file, and put it into a folder (make sure to save it without a file extension).
https://github.com/udacity/fullstack-nanodegree-vm/blob/master/vagrant/Vagrantfile
### Download and start the vagrant environment:
With a terminal, navigate to the folder you created with the vagrant environment file, and run the following command:
```bash
vagrant up
```
### Ssh into the vagrant environment:
Once the ```vagrant up``` command has completed, run:
```bash
vagrant ssh
```
You are now ready to setup the database.
## Setting up the database
### Download the newsdata.zip file:
https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip

### Extract the newsdata.sql file: 
Extract the newsdata.sql file from the newsdata.zip into the vagrant folder you created earlier.

From within a terminal ssh session with the vagrant environment, navigate to ```/vagrant``` and run the command line command:
```
psql -d news -f newsdata.sql
```

## Creating the required views
Two views will need to be created in the _news_ database before this program can be run. These views are: article_views and daily_status, and they are listed at the bottom of this readme. 

One method to create the required article_views and daily_status views is from within environment vagrant, enter the database interactively from the command line with: ```psql -d news``` and then copy and paste, the sql code to create the two views. The sql code can be found at the bottom of this file.


# Running this project 
make sure the application.py script from this repo is in the vagrant folder, and run:
```python
python3 databaseAnalysis.py
```


# The views needed for this program are:

## article_views for questions 1 and 2
```sql
CREATE VIEW article_views AS 
SELECT COUNT(REPLACE(path, '/article/', '')), 
       articles.slug, 
       articles.title, 
       articles.author 
    FROM articles 
    INNER JOIN log 
    ON articles.slug 
    LIKE REPLACE(path, '/article/', '') 
    GROUP BY articles.slug, articles.id 
    ORDER BY count DESC;
```

## dailyStatus for question 3
```sql
CREATE VIEW daily_status AS
SELECT COUNT(status),
          status,
          LEFT(CAST(time AS TEXT), 10)
   AS day
   FROM log
   GROUP BY day, status;
```



