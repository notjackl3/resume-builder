import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from bcrypt import hashpw, gensalt, checkpw

load_dotenv("api.env")

HOSTNAME = os.getenv("HOSTNAME")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PWD = os.getenv("PWD")
PORT_ID = os.getenv("PORT_ID")


# Hash password to improve security
def hash_password(password):
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')


def verify_password(password, hashed_password):
    return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_database(new=False):
    try:
        with psycopg2.connect(host=HOSTNAME, dbname=DATABASE, user=USERNAME, password=PWD, port=PORT_ID) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                if new:
                    cur.execute("DROP TABLE IF EXISTS users")
                cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL)""")
                connection.commit()
    except Exception as error:
        print(error)


def register_user(username, password):
    try:
        with psycopg2.connect(host=HOSTNAME, dbname=DATABASE, user=USERNAME, password=PWD, port=PORT_ID) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                if result:
                    return False
                else:
                    hashed_password = hash_password(password)
                    cur.execute("""INSERT INTO users (username, hashed_password) VALUES (%s, %s)""",
                                (username, hashed_password))
                    connection.commit()
                    return True
    except Exception as error:
        print(error)


def authenticate_user(username_input, password_input):
    try:
        with psycopg2.connect(host=HOSTNAME, dbname=DATABASE, user=USERNAME, password=PWD, port=PORT_ID) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id, hashed_password FROM users WHERE username = %s", (username_input,))
                result = cur.fetchone()
        if result and verify_password(password_input, result["hashed_password"]):
            return result["id"]
        return False
    except Exception as error:
        print(error)


def get_id(username):
    try:
        with psycopg2.connect(host=HOSTNAME, dbname=DATABASE, user=USERNAME, password=PWD, port=PORT_ID) as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
        if result:
            return result
        return False
    except Exception as error:
        print(error)
