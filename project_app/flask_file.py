# imports

from __future__ import print_function
import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask allows python to interact with html,css,javascript
from flask import render_template #a template is the webpage html that gets returned by each function in the python file
from flask import request, url_for, redirect, session, send_from_directory, flash #utility functions
from database import db #sqlaclhemy database
'''models holds the objects stored in the database'''
from models import Project as Project
from models import User as User
from models import Comment as Comment
from models import Tasks as Tasks
'''forms holds the form objects used to take in user data'''
from forms import RegisterForm, LoginForm, CommentForm
from werkzeug.utils import secure_filename #url_for() is how we supply the url for most functions
import bcrypt #password hashing for security
import sys
app = Flask(__name__)     # create an app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'

db.init_app(app) #initialize the database and tie it to this app

with app.app_context(): #instantiate the database objects for this app
    db.create_all()

@app.route('/') #@app.route('') tells the app to run the following block whenever this url is used
@app.route('/index')
#define a function same as normal
def index():
    if session.get('user'): #check that a user is currently logged into the session
        return render_template('index.html', user=session['user']) #return the html page for index.html and pass session['user'] as user to the html page
    return render_template("index.html") #return the html page for index.html
 
app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)
'''this runs the app locally
!!!you can pip install -r requirements.txt to get all of the packages, but I am not sure which ones are unnecessary from other classes

To install flask:
    Mac:
        cd into the project_app folder
        python -m venv venv             #maybe python3; this creates a virtual environment
        source venv/bin/activate        #activates the ve
        pip install Flask               #maybe pip3; this installs flask

    Windows:
        cd into the project_app folder
        python -m venv venv
        source venv/Scripts/activate
        pip install Flask

To run the flask app

I belive mac does:
    export FLASK_APP=flask_file.py
    flask run

windows:
    python flask_file.py

copy the local address into a browser (http://127.0.0.1:5000)
'''
