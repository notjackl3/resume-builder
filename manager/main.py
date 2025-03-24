import os
import sys
from bot_manager import Manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exporter.converter import update_resume, export_to_pdf
from database_manager import UserDatabaseManager
from dotenv import load_dotenv
from utils import make_date, add_experience, add_coding_languages, add_technical_skills, add_soft_skills
from authentication_manager import authenticate_user, register_user, get_id

load_dotenv("api.env")

HOSTNAME = os.getenv("HOSTNAME")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PWD = os.getenv("PWD")
PORT_ID = os.getenv("PORT_ID")
USER_ID = 0


def login():
    username_input = input("Username: ")
    password_input = input("Password: ")
    if authenticate_user(username_input, password_input):
        global USER_ID
        USER_ID = get_id(username_input)[0]
        return True
    else:
        return False


def register():
    username_input = input("New Username: ")
    password_input = input("New Password: ")
    if register_user(username_input, password_input):
        return True
    else:
        return False


def run(file1, file2):
    logged_in = False
    while not logged_in:
        response = input("Would you like to login or signup? ")
        if response.lower() == "login":
            if login():
                print("Logged in.")
                logged_in = True
            else:
                print("Password is incorrect.")
        elif response.lower() == "signup":
            if register():
                print("User created.")
            else:
                print("Username already existed.")
        else:
            print("Invalid input. Please choose either 'login' or 'signup'.")

    manager = Manager(resume=file1, job_desc=file2)
    manager.extract_information_resume("../documents/outputs/output.txt", True)
    manager.extract_information_job("../documents/outputs/output-job.txt", True)
    manager.update_data()
    manager.update_matches()
    manager.update_experience_maps()

    manager.allocate_matching("what")
    manager.allocate_matching("how")
    manager.allocate_matching("result")

    data = {
        "name": manager.resume_dict["name"],
        "phone": manager.resume_dict["contact"]["phone"],
        "email": manager.resume_dict["contact"]["email"],
        "linkedin": manager.resume_dict["contact"]["linkedin"],
        "github": manager.resume_dict["contact"]["github"],
        "schools": [{"name": manager.resume_dict["education"][0]["school"],
                     "city": manager.resume_dict["education"][0]["city"],
                     "country": manager.resume_dict["education"][0]["country"],
                     "program": manager.resume_dict["education"][0]["program"],
                     "gpa": manager.resume_dict["education"][0]["gpa"]},
                    {"name": manager.resume_dict["education"][1]["school"],
                     "city": manager.resume_dict["education"][1]["city"],
                     "country": manager.resume_dict["education"][1]["country"],
                     "program": manager.resume_dict["education"][1]["program"],
                     "gpa": manager.resume_dict["education"][1]["gpa"]}],
        "jobs": [],
        "volunteers": [],
        "projects": [],
        "proficient": [],
        "intermediate": [],
        "technologies": [],
        "soft_skills": []
    }

    add_experience(data, manager.experience_map)
    add_coding_languages(data, manager.job_desc_dict["coding-languages"], manager.skill_data)
    add_technical_skills(data["technologies"], manager.resume_dict, data["proficient"], data["intermediate"])
    add_soft_skills(data["soft_skills"], manager.job_desc_dict["soft-skills"], manager.resume_dict["soft-skills"])
    update_resume("../exporter", data)
    export_to_pdf("generated_resume.tex", "../exporter")

    user_database = UserDatabaseManager(HOSTNAME, DATABASE, USERNAME, PWD, PORT_ID)

    def reset_database(database: UserDatabaseManager):
        database.delete_table("experiences")
        database.delete_table("skills")
        database.delete_table("education")
        database.delete_table("job_features")
        database.delete_table("jobs")
        database.delete_table("profile")

        user_database.create_new_database()
        user_database.add_profile(USER_ID,
                                  manager.resume_dict["name"],
                                  manager.resume_dict["contact"]["email"],
                                  manager.resume_dict["contact"]["phone"],
                                  manager.resume_dict["contact"]["linkedin"],
                                  manager.resume_dict["contact"]["github"])

    def add_education_to_database(database: UserDatabaseManager, id: int):
        for edu in manager.resume_dict["education"]:
            start_date = make_date(edu["when"], "start")
            end_date = make_date(edu["when"], "end")
            database.add_education(id,
                                   edu["school"],
                                   edu["program"],
                                   start_date,
                                   end_date,
                                   edu["city"],
                                   edu["school"],
                                   edu["gpa"],
                                   new=False)

    def add_skills_to_database(database: UserDatabaseManager, id: int):
        all_soft_skills = [("soft", x) for x in manager.resume_dict["soft-skills"]]
        database.add_skills(id, all_soft_skills)

        all_technical_skills = [("technical", x) for x in manager.resume_dict["technical-skills"]]
        database.add_skills(id, all_technical_skills)

        all_interests = [("interest", x) for x in manager.resume_dict["interests"]]
        database.add_skills(id, all_interests)

    def add_experiences_to_database(database: UserDatabaseManager, id: int):
        all_experiences = manager.resume_dict["volunteer-experiences"] + manager.resume_dict["work-experiences"]
        for experience in all_experiences:
            start_date = make_date(experience["when"], "start")
            end_date = make_date(experience["when"], "end")
            database.add_experience(id,
                                    experience["name"],
                                    experience["type"],
                                    experience["what"],
                                    experience["where"],
                                    experience["how"],
                                    start_date,
                                    end_date,
                                    experience["result"])

    def add_job_to_database(database: UserDatabaseManager, id: int):
        title = input("What is the job title? ")
        company_name = input("What is the company name? ")
        with open("../documents/inputs/jobs.txt") as file:
            job_description = file.read()
        database.add_job(id, title, company_name, job_description)

    def add_job_features(database: UserDatabaseManager, id: int):
        keywords = ["responsibilities", "soft-skills", "hard-skills", "preferred-experiences", "technologies", "action-verbs", "coding-languages"]
        for keyword in keywords:
            for x in manager.job_desc_dict[keyword]:
                database.add_job_features(x, keyword, id)

    reset_database(user_database)
    add_education_to_database(user_database, USER_ID)
    add_skills_to_database(user_database, USER_ID)
    add_experiences_to_database(user_database, USER_ID)
    add_job_to_database(user_database, USER_ID)
    add_job_features(user_database, 1)


if __name__ == "__main__":
    run("../documents/inputs/sample_resume.pdf", "../documents/inputs/jobs.txt")
