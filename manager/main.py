from __future__ import annotations

import os
import os.path
import sys
import time

from bot_manager import Manager, delete_duplicates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exporter.converter import update_resume, export_to_pdf
from database_manager import UserDatabaseManager
from dotenv import load_dotenv
from utils import make_date, add_experience, add_coding_languages, add_technical_skills, add_soft_skills
from authentication_manager import authenticate_user, register_user, get_id
from user_interface import on_call, notify

load_dotenv("api.env")

HOSTNAME = os.getenv("HOSTNAME")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PWD = os.getenv("PWD")
PORT_ID = os.getenv("PORT_ID")
USER_ID = 0
input_file, job_file, title, company_name, profile_id = "", "", "", "", ""
current_profile = None


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


def reset_database(database: UserDatabaseManager):
    database.delete_table("experiences")
    database.delete_table("skills")
    database.delete_table("education")
    database.delete_table("job_features")
    database.delete_table("jobs")

    user_database.create_new_database()


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
                                experience["where"],
                                experience["what"],
                                experience["how"],
                                experience["result"],
                                start_date,
                                end_date)


def add_job_to_database(database: UserDatabaseManager, user_id: int, title, company_name, job_description):
    # with open("../documents/inputs/jobs.txt") as file:
    #     job_description = file.read()
    return database.add_job(user_id, title, company_name, job_description)


def add_job_features(database: UserDatabaseManager, id: int):
    keywords = ["responsibilities", "soft-skills", "hard-skills", "preferred-experiences", "technologies", "action-verbs", "coding-languages"]
    for keyword in keywords:
        for x in manager.job_desc_dict[keyword]:
            database.add_job_features(id, x, keyword)


def alter_experience():
    current_what = user_database.get_items(profile_id, "experiences", "what")
    improved_what = user_database.get_items(profile_id, "experiences", "what_improved")
    current_how = user_database.get_items(profile_id, "experiences", "how")
    improved_how = user_database.get_items(profile_id, "experiences", "how_improved")
    current_result = user_database.get_items(profile_id, "experiences", "result")
    improved_result = user_database.get_items(profile_id, "experiences", "result_improved")
    current_ver = zip(current_what, current_how + current_result)
    improved_ver = zip(improved_what, improved_how, improved_result)
    resp = ''
    ver_to_key = {0: ("what", "what_improved"), 1: ("how", "how_improved"), 2: ("result", "result_improved")}
    for current, improved in zip(current_ver, improved_ver):
        print("· · ─────── ·𖥸· ─────── · ·")
        ver = 0
        for curr, impr in zip(current, improved):
            if curr[0] != '':
                print(f"Previous -- {curr[0]}")
                print(f"Improved -- {impr[0]}")
            resp = input("Would you like to change the final output? (y/n)")
            if resp == "y":
                update = input("Please enter a full sentence to edit: ")
                user_database.update_item(profile_id, "experiences", impr[0], ver_to_key[ver][1], update, ver_to_key[ver][1])
                for experience in manager.experience_map.values():
                    if getattr(experience, ver_to_key[ver][0]) == impr[0]:
                        setattr(experience, ver_to_key[ver][0], update)
            ver += 1


if __name__ == "__main__":
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

    user_database = UserDatabaseManager(HOSTNAME, DATABASE, USERNAME, PWD, PORT_ID)
    reset_database(user_database)

    selected_profile = False
    while not selected_profile:
        existing_profiles = user_database.get_profile(USER_ID, "user_id")
        for profile in existing_profiles:
            print("Results:")
            print(f"Id: {profile[0]}\n"
                  f"Name: {profile[1]}\n"
                  f"Email: {profile[2]}\n"
                  f"Phone Number: {profile[3]}\n"
                  f"Linkedin: {profile[4]}\n"
                  f"Github: {profile[5]}\n· · ─────── ·𖥸· ─────── · ·")
        response = input("Please select a profile id (type n to create new): ")
        if response == "n":
            name = input("What is your name? ")
            email = input("What is your email? ")
            phone = input("What is your phone number? ")
            linkedin = input("What is your linkedin (leave empty if none)? ")
            github = input("What is your github (leave empty if none)? ")
            user_database.add_profile(USER_ID,
                                      name,
                                      email,
                                      phone,
                                      linkedin,
                                      github)
        else:
            profile_id = int(response)
            # Current profile stores all of the basic information of the current user
            current_profile = user_database.get_profile(profile_id, "profile_id")[0]
            selected_profile = True

    selected_job = False
    while not selected_job:
        title = input("Job title: ")
        company_name = input("Company name: ")

        input_files = on_call()
        notify()
        input_file = input_files[0]
        job_file = input_files[1]
        selected_job = True
        # input_file = input("What resume file do you want to improve (file path)? ")
        # if os.path.isfile(input_file):
        #     selected_job = True
        # else:
        #     print("Invalid file path.")
        # job_file = input("What is your job description (file path)? ")
        # if not os.path.isfile(job_file):
        #     print("Invalid file path.")
        #     selected_job = False
    with open(job_file, "r") as f:
        job_description = f.read()

    current_job_id = add_job_to_database(user_database, profile_id, title, company_name, job_description)

    manager = Manager(resume=input_file, job_desc=job_file)
    manager.extract_information_resume("../documents/outputs/output.txt", True)
    manager.extract_information_job("../documents/outputs/output-job.txt", True)
    manager.update_data()
    manager.update_matches()
    manager.update_experience_maps()

    manager.allocate_matching("what")
    manager.allocate_matching("how")
    manager.allocate_matching("result")

    data = {
        "name": current_profile[1],
        "phone": current_profile[2],
        "email": current_profile[3],
        "linkedin": current_profile[4],
        "github": current_profile[5],
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
        "work": [],
        "volunteers": [],
        "projects": [],
        "proficient": [],
        "intermediate": [],
        "technologies": [],
        "soft_skills": []
    }

    add_education_to_database(user_database, profile_id)
    add_skills_to_database(user_database, profile_id)
    add_experiences_to_database(user_database, profile_id)
    add_job_features(user_database, current_job_id)

    for exp_id, exp in manager.experience_map.items():
        user_database.update_item(profile_id, "experiences", exp.name, "name", exp.what, "what_improved")
        user_database.update_item(profile_id, "experiences", exp.name, "name", exp.how, "how_improved")
        user_database.update_item(profile_id, "experiences", exp.name, "name", exp.result, "result_improved")

    alter_experience()
    # alter_experience("how", "how_improved")
    # alter_experience("result", "result_improved")

    add_experience(data, manager.experience_map)
    add_coding_languages(data, manager.job_desc_dict["coding-languages"], manager.skill_data)
    add_technical_skills(data["technologies"], manager.resume_dict, data["proficient"], data["intermediate"])
    add_soft_skills(data["soft_skills"], manager.job_desc_dict["soft-skills"], manager.resume_dict["soft-skills"])

    update_resume("../exporter", data)
    export_to_pdf("generated_resume.tex", "../exporter")
