import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs
from dotenv import load_dotenv
import os

load_dotenv("api.env")

HOSTNAME = os.getenv("HOSTNAME")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PWD = os.getenv("PWD")
PORT_ID = os.getenv("PORT_ID")


class UserDatabaseManager:
    def __init__(self, hostname=HOSTNAME, database=DATABASE, username=USERNAME, pwd=PWD, port_id=PORT_ID):
        self._host = hostname
        self._dbname = database
        self._user = username
        self._password = pwd
        self._port = port_id

    def create_new_database(self, name="NULL", email="NULL", phone="NULL", linkedin="NULL", github="NULL", new=True):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:

                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                    if new:
                        cur.execute("DROP TABLE IF EXISTS profile")

                    create_table = """CREATE TABLE IF NOT EXISTS profile (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(100),
                    linkedin VARCHAR(100),
                    github VARCHAR(100))"""
                    cur.execute(create_table)

                    insert_command = ("INSERT INTO profile (name, email, phone, linkedin, github) "
                                      "VALUES (%s, %s, %s, %s, %s)")
                    insert_item = [(name, email, phone, linkedin, github)]
                    for item in insert_item:
                        cur.execute(insert_command, item)

                    connection.commit()

        except Exception as error:
            print(error)

    def delete_table(self, table):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(f"DROP TABLE IF EXISTS {table}")
                    connection.commit()
        except Exception as error:
            print(error)

    def get_id(self, user_input: str):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    get_command = "SELECT id FROM profile WHERE name ILIKE %s"
                    get_item = (f"%{user_input}%",)
                    cur.execute(get_command, get_item)
                    results = cur.fetchall()
                    connection.commit()
                    return results
        except Exception as error:
            print(error)

    def add_education(self, user_id, school, program="NULL", start_date="NULL", end_date="NULL", city="NULL", country="NULL",
                      gpa="NULL", new=False):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    if new:
                        cur.execute("DROP TABLE IF EXISTS education")

                    create_table = """CREATE TABLE IF NOT EXISTS education (
                                        id SERIAL PRIMARY KEY,
                                        school VARCHAR(100) NOT NULL,
                                        program VARCHAR(100),
                                        start_date TEXT,
                                        end_date TEXT,
                                        city VARCHAR(100),
                                        country VARCHAR(100),
                                        gpa VARCHAR(100),
                                        user_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(user_id)
                                                REFERENCES profile(id) ON DELETE CASCADE)"""
                    cur.execute(create_table)
                    insert_command = ("INSERT INTO education "
                                      "(school, program, start_date, end_date, city, country, gpa, user_id)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(school, program, start_date, end_date, city, country, gpa, user_id)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_skills(self, user_id, skills, new=False):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    if new:
                        cur.execute("DROP TABLE IF EXISTS skills")

                    create_table = """CREATE TABLE IF NOT EXISTS skills (
                                        id SERIAL PRIMARY KEY,
                                        skill_type VARCHAR(100) CHECK (skill_type IN ('soft', 'technical', 'interest')),
                                        name VARCHAR(100),
                                        user_id INTEGER REFERENCES profile(id) ON DELETE CASCADE)"""
                    cur.execute(create_table)
                    insert_command = ("INSERT INTO skills "
                                      "(skill_type, name, user_id)"
                                      "VALUES (%s, %s, %s)")

                    insert_item = [(skill[0], skill[1], user_id) for skill in skills]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_experience(self, user_id, name, experience_type, what="NULL", where="NULL", how="NULL",
                       start_date="NULL", end_date="NULL", result="NULL"):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    create_table = """CREATE TABLE IF NOT EXISTS experiences (
                                        id SERIAL PRIMARY KEY,
                                        name VARCHAR NOT NULL,
                                        experience_type VARCHAR(100) CHECK (experience_type IN ('work', 'volunteer')),
                                        what VARCHAR,
                                        location VARCHAR,
                                        how VARCHAR,
                                        start_date TEXT,
                                        end_date TEXT,
                                        result VARCHAR,
                                        user_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(user_id)
                                                REFERENCES profile(id) ON DELETE CASCADE)"""
                    cur.execute(create_table)
                    insert_command = ("INSERT INTO experiences "
                                      "(name, experience_type, what, location, how, start_date, end_date, result, user_id)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(name, experience_type, what, where, how, start_date, end_date, result, user_id)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_job(self, user_id, title, company, description):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    create_table = """CREATE TABLE IF NOT EXISTS jobs (
                                        id SERIAL PRIMARY KEY,
                                        title VARCHAR(100),
                                        company VARCHAR(100),
                                        description TEXT,
                                        user_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(user_id)
                                                REFERENCES profile(id) ON DELETE CASCADE)"""
                    cur.execute(create_table)
                    insert_command = ("INSERT INTO jobs "
                                      "(title, company, description, user_id)"
                                      "VALUES (%s, %s, %s, %s)")
                    insert_item = [(title, company, description, user_id)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_job_features(self, word, feature_type, job_id):
        try:
            with psycopg2.connect(host=self._host,
                                  dbname=self._dbname,
                                  user=self._user,
                                  password=self._password,
                                  port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    create_table = """CREATE TABLE IF NOT EXISTS job_features (
                                        id SERIAL PRIMARY KEY,
                                        word VARCHAR NOT NULL,
                                        feature_type VARCHAR(100) CHECK (feature_type IN ('responsibility', 'soft-skill', 'hard-skill', 'preferred-experience', 
                                        'technology', 'action-verb', 'coding-language')),
                                        job_id INT,
                                        CONSTRAINT fk_job
                                            FOREIGN KEY(job_id)
                                                REFERENCES jobs(id) ON DELETE CASCADE)"""
                    cur.execute(create_table)
                    insert_command = ("INSERT INTO job_features "
                                      "(word, feature_type, job_id)"
                                      "VALUES (%s, %s, %s)")
                    insert_item = [(word, feature_type, job_id)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)
