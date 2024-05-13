import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template
    make_response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


app = Flask(__name__)
db = SQLAlchemy(app)

engine = sqlalchemy.create_engine("postgresql://postgres:pass@postgres:5432", connect_args={
    'application_name': '__init__.py',
    })
connection = engine.connect()



@app.route('/')
def root():

    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_creds = check_creds(username,passowrd)


    return render_template('root.html', logged_in=good_creds)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    approved = check_creds(username,password)
    if username is None:
        return render_template('login.html', bad_creds=False)
    else:
        if approved:

            # create cookie
            template = render_template('login.html', bad_creds=False, logged_in=True)
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response
        else:
            return render_template('login.html', bad_creds=True) 

@app.route('/logout')
def logout():
    
    #delete cookies

    return render_template('logout.html') 

@app.route('/create_account')
def create_account():

    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if (password != password2):
        return render_template('create_account.html', mismatch=True, taken=False)
    elif check_taken(username):
        return render_template('create_account.html', mismatch=False, taken=True)
    else:
        return render_template('create_account.html', mismatch=False, taken=False)

@app.route('/create_message')
def create_message():
    return render_template('create_message.html')

@app.route('/search')
def search():
    return render_template('search.html')



#helper functions:
def check_creds(username, password):
    return true

def check_taken(username):
    return false

app.run()

