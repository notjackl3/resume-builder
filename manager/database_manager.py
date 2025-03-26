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
                                        school VARCHAR(100) NOT NULL,
                                        program VARCHAR(100),
                                        start_date TEXT,
                                        end_date TEXT,
                                        city VARCHAR(100),
                                        country VARCHAR(100),
                                        gpa VARCHAR(100),
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE)""")

                    # Create experiences table
                    cur.execute("""CREATE TABLE IF NOT EXISTS experiences (
                                        id SERIAL PRIMARY KEY,
                                        name VARCHAR NOT NULL,
                                        experience_type VARCHAR(100) CHECK (experience_type IN ('work', 'volunteer')),
                                        what VARCHAR,
                                        location VARCHAR,
                                        how VARCHAR,
                                        start_date TEXT,
                                        end_date TEXT,
                                        result VARCHAR,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE)""")

                    # Create skills table
                    cur.execute("""CREATE TABLE IF NOT EXISTS skills (
                                        id SERIAL PRIMARY KEY,
                                        skill_type VARCHAR(100) CHECK (skill_type IN ('soft', 'technical', 'interest')),
                                        name VARCHAR(100),
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE)""")

                    # Create jobs table
                    cur.execute("""CREATE TABLE IF NOT EXISTS jobs (
                                        id SERIAL PRIMARY KEY,
                                        title VARCHAR(100),
                                        company VARCHAR(100),
                                        description TEXT,
                                        profile_id INT,
                                        CONSTRAINT fk_user
                                            FOREIGN KEY(profile_id)
                                                REFERENCES profile(profile_id) ON DELETE CASCADE)""")

                    # Create job_features table
                    cur.execute("""CREATE TABLE IF NOT EXISTS job_features (
                                        id SERIAL PRIMARY KEY,
                                        word VARCHAR NOT NULL,
                                        feature_type VARCHAR(100) CHECK (feature_type IN ('responsibilities', 'soft-skills', 'hard-skills', 'preferred-experiences', 
                                        'technologies', 'action-verbs', 'coding-languages')),
                                        job_id INT,
                                        CONSTRAINT fk_job
                                            FOREIGN KEY(job_id)
                                                REFERENCES jobs(id) ON DELETE CASCADE)""")

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
                                      "(school, program, start_date, end_date, city, country, gpa, profile_id)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(school, program, start_date, end_date, city, country, gpa, profile_id)]
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
                                      "(skill_type, name, profile_id)"
                                      "VALUES (%s, %s, %s)")
                    insert_item = [(skill[0], skill[1], profile_id) for skill in skills]
                    for item in insert_item:
                        cur.execute(insert_command, item)
                    connection.commit()
        except Exception as error:
            print(error)

    def add_experience(self, profile_id, name, experience_type, what="NULL", where="NULL", how="NULL",
                       start_date="NULL", end_date="NULL", result="NULL"):
        try:
            with psycopg2.connect(host=self._host,dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO experiences "
                                      "(name, experience_type, what, location, how, start_date, end_date, result, profile_id)"
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    insert_item = [(name, experience_type, what, where, how, start_date, end_date, result, profile_id)]
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
                                      "(title, company, description, profile_id)"
                                      "VALUES (%s, %s, %s, %s) RETURNING id")
                    cur.execute(insert_command, (title, company, description, profile_id))
                    new_job_id = cur.fetchone()[0]
                    connection.commit()
                    return new_job_id
        except Exception as error:
            print(error)

    def add_job_features(self, word, feature_type, job_id):
        try:
            with psycopg2.connect(host=self._host, dbname=self._dbname, user=self._user, password=self._password, port=self._port) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    insert_command = ("INSERT INTO job_features "
                                      "(word, feature_type, job_id)"
                                      "VALUES (%s, %s, %s)")
                    insert_item = [(word, feature_type, job_id)]
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
                    cur.execute(get_command, (profile_id, ))
                    results = cur.fetchall()
                    connection.commit()
                    return results
        except Exception as error:
            print(error)
