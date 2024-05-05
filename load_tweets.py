#!/usr/bin/python3

# imports
import sqlalchemy
import os
import datetime
import zipfile
import io
import json
import random
import string
from datetime import datetime

def insert_tweet(connection,tweet,user):
    '''
    Insert the tweet into the database.

    Args:
        connection: a sqlalchemy connection to the postgresql db
        tweet: a dictionary representing the json tweet object

    '''
    time = datetime.now()
    try:
        sql = """
        INSERT INTO tweets (tweet, user, time) VALUES (?, ?, ?);
        """
        connection.execute(sql, [tweet, user, time])
    except sqlalchemy.exc.IntegrityError:
        print('load tweet error')            

def insert_user(connection, username, password):
    try:      
        # id_users is autoincremented
        sql = """
        INSERT INTO users (usernmae, password) VALUES (?, ?);
        """
        connection.execute(sql, [username, password])
    except sqlalchemy.exc.IntegrityError:
        print('load user error')        

def insert_url(connection, url):
    try:
        sql = """
        INSERT INTO urls (url) VALUES (?);
        """
        connection.execute(sql, [url])
    except sqlalchemy.exc.IntegrityError:
        print('load url error')

def gen_user():
    num_digits = random.randint(4, 8)
    username = ''
    for i in range(num_digits):
            username += random.choice(string.ascii_letters)
    return username

def gen_pass():
    num_digits = random.randint(4, 8)
    password = ''
    for i in range(num_digits):
            password += random.choice(string.ascii_letters)
    return password 


def gen_tweet():
    tweet = ''
    num_words = random.randint(1, 15)
    for i in range(num_words):
        word = ''
        num_digits = random.randint(4, 8)
        for j in range(num_digits):
            word += random.choice(string.ascii_letters)
        tweet = tweet + word + ' '
    return tweet 


# Main function

if __name__ == '__main__':

    # process command line args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',required=True)
    parser.add_argument('--inputs',nargs='+',required=True)
    parser.add_argument('--print_every',type=int,default=1000)
    args = parser.parse_args()

    # create database connection
    engine = sqlalchemy.create_engine(args.db, connect_args={
        'application_name': 'load_tweets.py',
        })
    connection = engine.connect()

    # inserts random users
    for i in range(5):

        # load and insert the tweet
        username = gen_user()
        password = gen_pass()
        insert_user(connection,username,password)

        # print message
        print('new user')



    # inserts random urls
    for i in range(5):

        # load and insert the tweet
        url = gen_url()
        insert_url(connection,url)

        # print message
        print('new url')





    # inserts random tweets
    # range sets the number of tweets inserted 
   
    sql = sqlalchemy.sql.text("""
    SELECT id_users FROM users;
    """)
    res = connection.execute(sql)
    users = [user[0] for user in res.fetchall()]

    sql = sqlalchemy.sql.text("""
    SELECT id_urls FROM urls;
    """)
    res = connection.execute(sql)
    urls = [url[0] for url in res.fetchall()]

    
    for i in range(5):     
        
        user = random.choice(users)
        
        url = random.choice(urls)
        urls.remove(url)

        # load and insert the tweet
        tweet = gen_tweet() 
        insert_tweet(connection,tweet,user,url)

        # print message
        print('new tweet')


#    connection.close()    # DO I NEED THIS??
