
import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import sqlalchemy
from sqlalchemy import text, create_engine
import psycopg2
import bleach


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)

engine = sqlalchemy.create_engine("postgresql://postgres:pass@postgres:5432", connect_args={
    'application_name': '__init__.py',
    })
connection = engine.connect()



@app.route('/')
def root():

    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_creds = check_creds(username,password)


    return render_template('root.html', logged_in=good_creds)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    approved = check_creds(username,password)
    if username is None:
        return render_template('login.html', bad_creds=False, logged_in=False)
    else:
        if approved:

            # create cookie
            template = render_template('login.html', bad_creds=False, logged_in=True)
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response
        else:
            return render_template('login.html', bad_creds=True, logged_in=False) 

@app.route('/logout')
def logout():
    
    #delete cookies
    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')

    return response 

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():


    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')


    if username is not None and password is not None and password2 is not None:
        if (password != password2):
            return render_template('create_account.html', logged_in=False, mismatch=True, taken=False, empty=False)
        elif check_taken(username):
            return render_template('create_account.html', logged_in=False, mismatch=False, taken=True, empty=False)
        else:
            try:
                result = connection.execute(text(
                    "INSERT INTO users (username, password) VALUES (:username, :password);"
                    ),  {"username": username, "password": password})  
            except sqlalchemy.exc.IntegrityError:
                pass 
            return render_template('create_account.html', logged_in=False, mismatch=False, taken=False, empty=False)
    else:
        return render_template('create_account.html', logged_in=False, mismatch=False, taken=False, empty=True)

@app.route('/create_message', methods=['GET', 'POST'])
def create_message():

    message = request.form.get('message')
    
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_creds = check_creds(username,password)
    if not message:
            return render_template('create_message.html',logged_in=good_creds, message_inserted=False)
    if good_creds and message is not None:
        insert_tweet(message, username)
        return render_template('create_message.html',logged_in=good_creds, message_inserted=True)

    return render_template('create_message.html',logged_in=good_creds, message_inserted=False)

@app.route('/search', methods=['GET', 'POST'])
def search():

    '''
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_creds = check_creds(username,password)

    search = request.form.get('search')

    page = 1

    tweets = get_tweets(search, page)
    
    return render_template('search.html',logged_in=good_creds, tweets=tweets, page=page, search=search)
    '''
    return render_template('search.html')


#helper functions:
def check_creds(username, password):
    
    sql = sqlalchemy.sql.text('''
        SELECT * FROM users
        WHERE username = :username
        AND password = :password;
        ''')

    res = connection.execute(sql, {
        'username': username,
        'password': password
    })

    # if there is a user with the corresponding username and password, then the query will have a non empty result
    if res.fetchone() is None:
        return False
    else:
        return True

def check_taken(username):
    sql = sqlalchemy.sql.text('''
        SELECT * FROM users
        WHERE username = :username;
        ''')

    res = connection.execute(sql, {
        'username': username
    })
    
    # if there is a user with the corresponding username then it query qill have a non empty result (username taken)
    if res.fetchone() is None:
        return False
    else:
        return True

def insert_tweet(text, username):
    
    sql = sqlalchemy.sql.text('''
        SELECT id_users FROM users
        WHERE username = :username;
        ''')

    result_id_users = connection.execute(sql, {'username': username})
    for row in result_id_users.fetchall():
        id_users = row[0]


    sql = sqlalchemy.sql.text('''
        SELECT MIN(u.id_urls)               
        FROM urls u
        LEFT JOIN tweets t ON u.id_urls = t.id_urls
        WHERE t.id_urls IS NULL;
        ''')

    result_id_urls = connection.execute(sql)
    for row in result_id_urls.fetchall():
        id_urls = row[0]

    sql = sqlalchemy.sql.text(
            '''
            INSERT INTO tweets (text, id_users, id_urls) 
            VALUES (:text, :id_users, :id_urls)
            ''')

    sql = sql.bindparams(text=text,
        id_users=id_users,
        id_urls=id_urls)
    connection.execute(sql)
    connection.commit()


'''
def get_tweets(search, page):
    offset = (page - 1) * 20
    tweets = []
    sql = sqlalchemy.sql.text("""
    SELECT id_tweets,
    ts_headline('english', text, plainto_tsquery(:search), 'StartSel=<span> StopSel=</span>') AS highlighted_text,
    created_at,
    id_users
    FROM tweets
    WHERE to_tsvector('english', text) @@ plainto_tsquery(:search)
    ORDER BY created_at DESC
    LIMIT 20 OFFSET :offset;
    """)

    res = connection.execute(sql, {'search': ' & '.join(search.split()), 'offset': offset})
    for row in res.fetchall():
        user_sql = sqlalchemy.sql.text("""
            SELECT username
            FROM users
            WHERE id_users = :id_users;
        """)
        user_res = connection.execute(user_sql, {'id_users': row[3]})
        user_row = user_res.fetchone()
        tweets.append({
            'username': user_row[0],
            'text': bleach.clean(row[1], tags=['p', 'br', 'a', 'b', 'span'], attributes={'a': ['href']}).replace("<span>", "<span class=highlight>"),
            'created_at': row[2]
        })

    return tweets
'''
