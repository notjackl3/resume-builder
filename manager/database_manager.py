import psycopg2
import psycopg2.extras
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

    def create_new_database(self):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    # Create profile table
                    cur.execute("""CREATE TABLE IF NOT EXISTS profile (
                    profile_id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(100),
                    linkedin VARCHAR(100),
                    github VARCHAR(100),
                    user_id INT,
                    CONSTRAINT fk_user
                        FOREIGN KEY(user_id)
                            REFERENCES users(id) ON DELETE CASCADE)""")

                    # Create education table
                    cur.execute("""CREATE TABLE IF NOT EXISTS education (
                                        id SERIAL PRIMARY KEY,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE,
                                        school VARCHAR(100) NOT NULL,
                                        program VARCHAR(100),
                                        start_date TEXT,
                                        end_date TEXT,
                                        city VARCHAR(100),
                                        country VARCHAR(100),
                                        gpa VARCHAR(100))""")

                    # Create experiences table
                    cur.execute("""CREATE TABLE IF NOT EXISTS experiences (
                                        id SERIAL PRIMARY KEY,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE,                        
                                        name VARCHAR NOT NULL,
                                        experience_type VARCHAR(100) CHECK (experience_type IN ('work', 'volunteer')),
                                        location VARCHAR,
                                        what VARCHAR,
                                        how VARCHAR,
                                        result VARCHAR,
                                        start_date TEXT,
                                        end_date TEXT,
                                        what_improved VARCHAR,
                                        how_improved VARCHAR,
                                        result_improved VARCHAR)""")

                    # Create skills table
                    cur.execute("""CREATE TABLE IF NOT EXISTS skills (
                                        id SERIAL PRIMARY KEY,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE,
                                        skill_type VARCHAR(100) CHECK (skill_type IN ('soft', 'technical', 'interest')),
                                        name VARCHAR(100))""")

                    # Create jobs table
                    cur.execute("""CREATE TABLE IF NOT EXISTS jobs (
                                        id SERIAL PRIMARY KEY,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE,
                                        title VARCHAR(100),
                                        company VARCHAR(100),
                                        description TEXT)""")

                    # Create job_features table
                    cur.execute("""CREATE TABLE IF NOT EXISTS job_features (
                                        id SERIAL PRIMARY KEY,
                                        job_id INT,
                                        CONSTRAINT fk_job
                                            FOREIGN KEY(job_id)
                                                REFERENCES jobs(id) ON DELETE CASCADE,
                                        word VARCHAR NOT NULL,
                                        feature_type VARCHAR(100) CHECK (feature_type IN ('responsibilities', 'soft-skills', 'hard-skills', 'preferred-experiences', 
                                        'technologies', 'action-verbs', 'coding-languages')))""")
                    connection.commit()
        except Exception as error:
            print(error)

    def add_profile(self, user_id, name="NULL", email="NULL", phone="NULL", linkedin="NULL", github="NULL"):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute("""INSERT INTO profile (name, email, phone, linkedin, github, user_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                                (name, email, phone, linkedin, github, user_id))
                    connection.commit()
        except Exception as error:
            print(error)

    def get_profile(self, user_id, search):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor() as cur:
                    get_command = f"SELECT * FROM profile WHERE {search} = %s"
                    cur.execute(get_command, (user_id,))
                    results = cur.fetchall()
                    connection.commit()
                    return results
        except Exception as error:
            print(error)

    def delete_table(self, table):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(f"DROP TABLE IF EXISTS {table}")
                    connection.commit()
        except Exception as error:
            print(error)

    def get_id(self, user_input: str, table):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    get_command = f"SELECT id FROM {table} WHERE name ILIKE %s"
                    get_item = (f"%{user_input}%",)
                    cur.execute(get_command, get_item)
                    results = cur.fetchone()
                    connection.commit()
                    return results
        except Exception as error:
            print(error)

    def add_education(self, profile_id, school, program="NULL", start_date="NULL", end_date="NULL", city="NULL", country="NULL",
                      gpa="NULL", new=False):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO education "
                                      "(profile_id, school, program, start_date, end_date, city, country, gpa)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(profile_id, school, program, start_date, end_date, city, country, gpa)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_skills(self, profile_id, skills, new=False):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO skills "
                                      "(profile_id, skill_type, name)"
                                      "VALUES (%s, %s, %s)")
                    insert_item = [(profile_id, skill[0], skill[1]) for skill in skills]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_experience(self, profile_id, name, experience_type, where="NULL", what="NULL", how="NULL",
                       result="NULL", start_date="NULL", end_date="NULL"):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO experiences "
                                      "(profile_id, name, experience_type, location, what, how, result, start_date, end_date)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(profile_id, name, experience_type, where, what, how, result, start_date, end_date)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_job(self, profile_id, title, company, description):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO jobs "
                                      "(profile_id, title, company, description)"
                                      "VALUES (%s, %s, %s, %s) RETURNING id")
                    cur.execute(insert_command, (profile_id, title, company, description))
                    new_job_id = cur.fetchone()[0]
                    connection.commit()
                    return new_job_id
        except Exception as error:
            print(error)

    def add_job_features(self, job_id, word, feature_type):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO job_features "
                                      "(job_id, word, feature_type)"
                                      "VALUES (%s, %s, %s)")
                    insert_item = [(job_id, word, feature_type)]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def get_items(self, profile_id, table, column):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    get_command = f"SELECT {column} FROM {table} WHERE profile_id = %s"
                    cur.execute(get_command, (profile_id,))
                    results = cur.fetchall()
                    connection.commit()
                    return results
        except Exception as error:
            print(error)

    def update_item(self, profile_id, table, search, column_search, update, column_update):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    update_command = (f"UPDATE {table} "
                                      f"SET {column_update} = %s "
                                      f"WHERE profile_id = %s AND {column_search}= %s")
                    cur.execute(update_command, (update, profile_id, search))
                    connection.commit()
        except Exception as error:
            print(error)
