# imports

from __future__ import print_function
import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask allows python to interact with html,css,javascript
from flask import render_template #a template is the webpage html that gets returned by each function in the python file
from flask import request, url_for, redirect, session, send_from_directory, flash #utility functions
from database import db #sqlaclhemy database
'''models holds the objects stored in the database'''
from models import Summary as Summary
#from models import User as User
'''forms holds the form objects used to take in user data'''
from forms import RegisterForm, LoginForm, InputTextForm
from werkzeug.utils import secure_filename #url_for() is how we supply the url for most functions
from ML_models import algo_1
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
 
'''
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

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    #if session.get('user'): #check that a user is currently logged into the session
    #    return render_template('index.html', user=session['user']) #return the html page for index.html and pass session['user'] as user to the html page
    input_text_form = InputTextForm()
    if request.method == 'POST' and input_text_form.validate_on_submit():
        input_text = request.form['inputText']

        id = db.Column("id", db.Integer, primary_key=True)
        title, best_summary = algo_1(input_text)

        new_summary = Summary(title, input_text, best_summary) #, session['user_id'] add when users are implemented
        db.session.add(new_summary)
        db.session.commit()
        #summary_id = db.session.query(Summary).order_by(Summary.id.desc()).first()
        #show_summary(new_summary)
        return show_summary(new_summary)
    return render_template('summarize.html')

@app.route('/show_summary')
def show_summary(summary):
    if summary:
        #summary = db.session.query(Summary).filter_by(id=summary_id).one()
        return render_template('show_summary.html', summary = summary)
    else:
        summary = db.session.query(Summary).order_by(Summary.id.desc()).first()
        return render_template('show_summary.html', summary = summary)
    return redirect(url_for('summarize'))

app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True) #this runs the app locally