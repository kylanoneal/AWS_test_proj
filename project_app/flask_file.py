# imports

from __future__ import print_function
import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask allows python to interact with html,css,javascript
from flask import \
    render_template  # a template is the webpage html that gets returned by each function in the python file
from flask import request, url_for, redirect, session, send_from_directory, flash  # utility functions
from database import db  # sqlaclhemy database

'''models holds the objects stored in the database'''
from models import Summary as Summary
from models import User as User

'''forms holds the form objects used to take in user data'''
from forms import RegisterForm, LoginForm, InputTextForm
from werkzeug.utils import secure_filename  # url_for() is how we supply the url for most functions
from ML_models import generate_sent_extraction, generate_trans_inference
from text_from_file import *
import bcrypt  # password hashing for security
import sys
import math

app = Flask(__name__)  # create an app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_project_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'

db.init_app(app)  # initialize the database and tie it to this app

with app.app_context():  # instantiate the database objects for this app
    db.create_all()


@app.route('/')  # @app.route('') tells the app to run the following block whenever this url is used
@app.route('/index')
# define a function same as normal
def index():
    if session.get('user'):  # check that a user is currently logged into the session
        return render_template('index.html', user=session[
            'user'])  # return the html page for index.html and pass session['user'] as user to the html page
    return render_template('index.html')  # return the html page for index.html


# summarize takes in user text and creates a summary object in the database
@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if not 'sentence_extraction' in session:
        session['sentence_extraction'] = True

    # creates an InputTextForm object from forms.py
    input_text_form = InputTextForm()
    # check that the submit button has been clicked and the text entry is valid
    if request.method == 'POST' and input_text_form.validate_on_submit():
        # retrieve the input text

        if "sentence_extraction_button" in request.form:
            session['sentence_extraction'] = True
            return render_summarize(input_text_form)
        elif "transformer_model_button" in request.form:
            session['sentence_extraction'] = False
            return render_summarize(input_text_form)

        # storing uploaded files in /instance directory
        if input_text_form.attach_text_file.data:
            file = input_text_form.attach_text_file.data
            file.save('instance/' + file.filename)  # save the file for text extraction
            input_text = get_text_from_text_file('instance/' + file.filename)  # extract text
            os.remove('instance/' + file.filename)  # remove file
        elif input_text_form.attach_image_file.data:
            file = input_text_form.attach_image_file.data
            file.save('instance/' + file.filename)  # save the file for text extraction
            input_text = get_text_from_image('instance/' + file.filename)  # extract text
            os.remove('instance/' + file.filename)  # remove file
        else:
            input_text = input_text_form.input_text.data

        if session['sentence_extraction']:
            algorithm_choice = int(request.form['algorithm_choice'])  # dist, bow, nlp
            sentence_resolution = int(request.form['sentence_resolution'])  # 1,2,3
            title, best_summary = generate_sent_extraction(input_text, algorithm_choice,
                                                           sentence_resolution)  # generate summary
        else:
            genre_choice = request.form['genre_choice']
            model_choice = request.form['model_choice']
            title, best_summary = generate_trans_inference(input_text, genre_choice, model_choice)  # generate summary

        # create a new Summary object from models.py
        if session.get('user'):
            # commit if the user is logged in
            new_summary = Summary(title, input_text, best_summary, session['user_id'])
            # add the new_summary object to the database
            db.session.add(new_summary)
            # commit changes to the database
            db.session.commit()
            # show the user the newly created summary
        else:
            # don't commit summary to database if the user isn't logged in
            new_summary = Summary(title, input_text, best_summary, 0)
        return show_summary(new_summary)

    # reload the summarize page if method is not POST
    return render_summarize(input_text_form)


def render_summarize(form):
    if session.get('user'):
        return render_template('summarize.html', form=form, sentence_extraction=session['sentence_extraction'],
                               user=session['user'])
    else:
        return render_template('summarize.html', form=form, sentence_extraction=session['sentence_extraction'])


# show_summary shows a summary to the user
@app.route('/show_summary<summary_id>')
def show_summary(summary=None, summary_id=0):
    # check if a summary has been passed
    if summary:
        # send summary to show_summary.html
        if session.get('user'):
            # send user if available
            return render_template('show_summary.html', summary=summary, user=session['user'])
        else:
            return render_template('show_summary.html', summary=summary)
    # check if summary_id has been passed
    elif summary_id:
        summary = db.session.query(Summary).get(summary_id)
        if session.get('user'):
            # send user if available
            return render_template('show_summary.html', summary=summary, user=session['user'])
        else:
            return render_template('show_summary.html', summary=summary)

    # will be used when functionality for user selecting from all previous summaries is added
    else:
        # currently chooses the most recently created summary
        summary = db.session.query(Summary).order_by(Summary.id.desc()).first()
        return render_template('show_summary.html', summary=summary)
    # return to summarize if this function fails
    return redirect(url_for('summarize'))


# initialize trained models
@app.route('/initialize')
def init_models():
    # initialize and or train models if they don't exist in the database
    # will be used for when the database is reset and the trained models don't exist anymore
    return


@app.route('/help')
# define a function same as normal
def help():
    if session.get('user'):  # check that a user is currently logged into the session
        return render_template('help.html', user=session[
            'user'])  # return the html page for help.html and pass session['user'] as user to the html page
    return render_template("help.html")  # return the html page for help.html


@app.route('/register', methods=['POST', 'GET'])
def register():
    register_form = RegisterForm()

    if request.method == 'POST' and register_form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('tutorial'))

    return render_template("register.html", form=register_form)


@app.route('/tutorial')
def tutorial():
    if session.get('user'):
        return render_template('tutorial.html', user=session['user'])
    else:
        return render_template('tutorial.html')


# @app.route('/login')
# define a function same as normal
# def login():
#    if session.get('user'):  # check that a user is currently logged into the session
#       return render_template('login.html', user=session[
#            'user'])  # return the html page for login.html and pass session['user'] as user to the html page
#    return render_template("login.html")  # return the html page for login.html

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('index'))

        # password check failed
        # set error message to alert user
        print('error logging user in')
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()
    return redirect(url_for('index'))


@app.route('/pastSummaries')
# define a function same as normal
def pastSummaries():
    if session.get('user'):  # check that a user is currently logged into the session
        past_summaries_list = db.session.query(Summary).filter_by(user_id=session['user_id'])
        num_summaries = past_summaries_list.count()
        num_pages = math.ceil(num_summaries / 10)
        return render_template('past_summaries.html', past_summaries_list=past_summaries_list,
                               num_summaries=num_summaries, user=session[
                'user'])  # return the html page for pastSummaries.html and pass session['user'] as user to the html page
    return render_template("past_summaries.html")  # return the html page for login.html


if __name__ == "__main__":
    app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)),
            debug=True)  # this runs the app locally

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
