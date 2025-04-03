from __future__ import annotations

import os
import os.path
import sys
import time
from typing import Optional

from colorama import Fore, Style
from tqdm import tqdm
import threading

from bot_manager import Manager, delete_duplicates

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exporter.converter import update_resume, export_to_pdf
from database_manager import UserDatabaseManager
from dotenv import load_dotenv
import utils
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


def login() -> bool:
    """Allows user to login and authenticate the password."""
    username_input = input("Username: ")
    password_input = input("Password: ")
    if authenticate_user(username_input=username_input, password_input=password_input):
        global USER_ID
        USER_ID = get_id(username_input)[0]
        return True
    else:
        return False


def register() -> bool:
    """Allows user to register for a new username."""
    username_input = input("New Username: ")
    password_input = input("New Password: ")
    if register_user(username=username_input, password=password_input):
        return True
    else:
        return False


def reset_database(database: UserDatabaseManager, env) -> None:
    """Resets the user database and create a new one."""
    database.delete_table(table="experiences")
    database.delete_table(table="skills")
    database.delete_table(table="education")
    database.delete_table(table="job_features")
    database.delete_table(table="jobs")

    env["user_database"].create_new_database()


def add_education_to_database(database: UserDatabaseManager, id: Optional[int], env) -> None:
    """Iterates through the resume in the manager and extract the
    information about the user's education."""
    for edu in env["manager"].resume_dict["education"]:
        start_date = utils.make_date(edu["when"], "start")
        end_date = utils.make_date(edu["when"], "end")
        database.add_education(profile_id=id,
                               school=edu["school"],
                               program=edu["program"],
                               start_date=start_date,
                               end_date=end_date,
                               city=edu["city"],
                               country=edu["country"],
                               gpa=edu["gpa"],
                               new=False)


def add_skills_to_database(database: UserDatabaseManager, id: Optional[int], env) -> None:
    """Adds all the user's skills into the database by iterating through the
    skills stored in the resume in the manager"""
    all_soft_skills = [("soft", x) for x in env["manager"].resume_dict["soft-skills"]]
    database.add_skills(profile_id=id, skills=all_soft_skills)
    all_technical_skills = [("technical", x) for x in env["manager"].resume_dict["technical-skills"]]
    database.add_skills(profile_id=id, skills=all_technical_skills)
    all_interests = [("interest", x) for x in env["manager"].resume_dict["interests"]]
    database.add_skills(profile_id=id, skills=all_interests)


def add_experiences_to_database(database: UserDatabaseManager, id: Optional[int], env) -> None:
    """Adds all the user's experiences into the database by iterating through the
    skills stored in the resume in the manager"""
    all_experiences = env["manager"].resume_dict["volunteer-experiences"] + env["manager"].resume_dict["work-experiences"]
    for exp in all_experiences:
        start_date = utils.make_date(exp["when"], "start")
        end_date = utils.make_date(exp["when"], "end")
        database.add_experience(profile_id=id,
                                name=exp["name"],
                                experience_type=exp["type"],
                                where=exp["where"],
                                what=exp["what"],
                                how=exp["how"],
                                result=exp["result"],
                                start_date=start_date,
                                end_date=end_date)


def add_job_to_database(database: UserDatabaseManager, user_id: Optional[int], title: Optional[str], company_name: Optional[str], job_description: Optional[str]) -> int:
    """From the user input, adds a new job to the database, linked to the profile id."""
    return database.add_job(profile_id=user_id, title=title, company=company_name, description=job_description)


def add_job_features(database: UserDatabaseManager, id: Optional[int], env) -> None:
    """Adds job features, keywords, to the database to the chosen job."""
    keywords = ["responsibilities", "soft-skills", "hard-skills", "preferred-experiences", "technologies", "action-verbs", "coding-languages"]
    for keyword in keywords:
        for word in env["manager"].job_desc_dict[keyword]:
            database.add_job_features(job_id=id, word=word, feature_type=keyword)


def edit_experience(env) -> None:
    """Based on the user's inputs, allows user to change the current experiences stored
    in the manager. Iterate through one experience at a time, each time is what-how-result."""
    current_what = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="what")
    improved_what = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="what_improved")
    current_how = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="how")
    improved_how = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="how_improved")
    current_result = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="result")
    improved_result = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="result_improved")
    # Zip all the data (what-how-result) together, so we can iterate through each experience at a time.
    current_ver = zip(current_what, current_how + current_result)
    # Below is the improved version, above is the version inputted by the user.
    improved_ver = zip(improved_what, improved_how, improved_result)
    ver_to_key = {0: ("what", "what_improved"), 1: ("how", "how_improved"), 2: ("result", "result_improved")}

    print("\n══════════════════════════════════════════════")
    print("                    EXPERIENCES               ")
    print("══════════════════════════════════════════════\n")

    for current, improved in zip(current_ver, improved_ver):
        ver = 0
        for curr, impr in zip(current, improved):
            if curr[0] != '' and curr[0] != impr[0]:
                print("Enter 'y' if you want to change or type 'n' to continue.\n")
                print(f"[!] Original: {curr[0]}")
                print(f"    Latest ➝ {impr[0]}\n")
                resp = input("--> ")

                if resp == "y":
                    print("\n══════════════════════════════════════════════")
                    print("   Enter the updated version below.")
                    print("══════════════════════════════════════════════\n")
                    update = input("--> ")

                    env["user_database"].update_item(env["profile_id"], "experiences", impr[0], ver_to_key[ver][1], update, ver_to_key[ver][1])
                    for experience in env["manager"].experience_map.values():
                        if getattr(experience, ver_to_key[ver][0]) == impr[0]:
                            setattr(experience, ver_to_key[ver][0], update)
            ver += 1


def login_screen():
    print("\n══════════════════════════════════════════════")
    print("                RESUME BUILDER                ")
    print("══════════════════════════════════════════════\n")

    # Allows user to login and validate the data.
    logged_in = False
    while not logged_in:
        print("Would you like to 'login' or 'signup'?")
        response = input("--> ")

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


def profile_screen(db: UserDatabaseManager, env):
    # Allows user to select the profiles that they have built, or create new profiles
    # Different profiles will have different personal information
    selected_profile = False
    while not selected_profile:
        print("\n══════════════════════════════════════════════")
        print("               AVAILABLE PROFILES             ")
        print("══════════════════════════════════════════════\n")

        existing_profiles = db.get_profile(USER_ID, "user_id")
        for profile in existing_profiles:
            print(f"Id: {profile[0]}\n"
                  f"Name: {profile[1]}\n"
                  f"Email: {profile[2]}\n"
                  f"Phone Number: {profile[3]}\n"
                  f"Linkedin: {profile[4]}\n"
                  f"Github: {profile[5]}")
            print("\n══════════════════════════════════════════════\n")
        print("Enter the id of the profile to select or type 'n' to create a new profile.")
        response = input("--> ")
        if response == "n":
            name = input("What is your name? ")
            email = input("What is your email? ")
            phone = input("What is your phone number? ")
            linkedin = input("What is your linkedin (leave empty if none)? ")
            github = input("What is your github (leave empty if none)? ")
            db.add_profile(user_id=USER_ID,
                           name=name,
                           email=email,
                           phone=phone,
                           linkedin=linkedin,
                           github=github)
        else:
            env["profile_id"] = int(response)
            # Current profile stores all the basic information of the current user
            env["current_profile"] = env["user_database"].get_profile(env["profile_id"], "profile_id")[0]
            selected_profile = True


def job_screen(env):
    print("\n══════════════════════════════════════════════")
    print("                      JOBS                    ")
    print("══════════════════════════════════════════════\n")
    print("Enter the job title for the position.")
    env["title"] = input("--> ")
    print("Enter the company name.")
    env["company_name"] = input("--> ")
    env["input_files"] = on_call()
    notify()
    env["input_file"] = env["input_files"][0]
    env["job_description"] = env["input_files"][1]
    with open("../documents/inputs/jobs.txt", "w") as file:
        file.write(env["job_description"])
    env["job_file"] = "../documents/inputs/jobs.txt"
    # This is for when the user input in a job file instead of a text
    # env["job_file"] = env["input_files"][1]
    # with open(env["job_file"], "r") as f:
    #     env["job_description"] = f.read()



def edit_screen(env):
    """Based on the user's inputs, allows user to change the current experiences stored
    in the manager. Iterate through one experience at a time, each time is what-how-result."""
    current_what = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="what")
    improved_what = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="what_improved")
    current_how = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="how")
    improved_how = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="how_improved")
    current_result = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="result")
    improved_result = env["user_database"].get_items(profile_id=env["profile_id"], table="experiences", column="result_improved")
    # Zip all the data (what-how-result) together, so we can iterate through each experience at a time.
    current_ver = zip(current_what, current_how + current_result)
    # Below is the improved version, above is the version inputted by the user.
    improved_ver = zip(improved_what, improved_how, improved_result)
    ver_to_key = {0: ("what", "what_improved"), 1: ("how", "how_improved"), 2: ("result", "result_improved")}
    options = []
    for current, improved in zip(current_ver, improved_ver):
        ver = 0
        for curr, impr in zip(current, improved):
            if curr[0] != '':
                if curr[0] != impr[0]:
                    options.append((curr[0], impr[0], ver, True))
                else:
                    options.append((curr[0], impr[0], ver, False))
            ver += 1

    print("\n══════════════════════════════════════════════")
    print("                 EXPERIENCE EDITOR            ")
    print("══════════════════════════════════════════════\n")

    for i, option in enumerate(options):
        if option[3]:
            print(f"[{i}] Original: {option[0]}")
            print(f"    Latest ➝ {option[1]}\n")
        else:
            print(f"[{i}] Original (unchanged): {option[0]}\n")

    response = None
    while response != "n":
        print("\n══════════════════════════════════════════════")
        print("   Enter the index of the item you want to change or type 'n' to continue.")
        print("══════════════════════════════════════════════\n")
        response = input("--> ")
        if response != "n":
            print("\n══════════════════════════════════════════════")
            print("   Enter the updated version below.")
            print("══════════════════════════════════════════════\n")
            update = input("--> ")

            env["user_database"].update_item(env["profile_id"], "experiences", options[int(response)][1], ver_to_key[options[int(response)][2]][1], update, ver_to_key[options[int(response)][2]][1])
            for experience in env["manager"].experience_map.values():
                if getattr(experience, ver_to_key[options[int(response)][2]][0]) == options[int(response)][1]:
                    setattr(experience, ver_to_key[options[int(response)][2]][0], update)
            options[int(response)] = (options[int(response)][0], update, options[int(response)][2])

    compile_resume(env)


def compile_resume(env):
    env["data"]["work"] = []
    env["data"]["volunteers"] = []
    env["data"]["projects"] = []
    env["data"]["proficient"] = []
    env["data"]["intermediate"] = []
    env["data"]["technologies"] = []
    env["data"]["soft_skills"] = []
    utils.add_experience(env["data"], env["manager"].experience_map)
    utils.add_coding_languages(env["data"], env["manager"].job_desc_dict["coding-languages"], env["manager"].skill_data)
    utils.add_technical_skills(env["data"]["technologies"], env["manager"].resume_dict, env["data"]["proficient"], env["data"]["intermediate"])
    utils.add_soft_skills(env["data"]["soft_skills"], env["manager"].job_desc_dict["soft-skills"], env["manager"].resume_dict["soft-skills"])

    update_resume("../exporter", env["data"])
    export_to_pdf("generated_resume.tex", "../exporter")

    edit_screen(env)


if __name__ == "__main__":
    env = {"user_database": None,
           "profile_id": None,
           "current_profile": [],
           "title": None,
           "company_name": None,
           "input_file": None,
           "job_file": None,
           "job_description": None,
           "current_job_id": None,
           "manager": Manager(None, None),
           "data": None}

    login_screen()

    # Sets up the user database, with the correct host, port and information
    env["user_database"] = UserDatabaseManager(HOSTNAME, DATABASE, USERNAME, PWD, PORT_ID)

    # Resets the old database if needed (not recommended)
    reset_database(env["user_database"], env)

    profile_screen(env["user_database"], env)

    job_screen(env)

    loading = True

    def long_process(env):
        global loading
        # Adds the user job input to the database and get back to id of the job
        env["current_job_id"] = add_job_to_database(env["user_database"], env["profile_id"], env["title"], env["company_name"], env["job_description"])

        env["manager"] = Manager(resume=env["input_file"], job_desc=env["job_file"])
        env["manager"].extract_information_resume("../documents/outputs/output.txt", True)
        env["manager"].extract_information_job("../documents/outputs/output-job.txt", True)
        env["manager"].update_data()
        env["manager"].update_matches()
        env["manager"].update_experience_maps()

        env["manager"].allocate_matching("what")
        env["manager"].allocate_matching("how")
        env["manager"].allocate_matching("result")

        loading = False


    def show_progress():
        processing = Fore.GREEN + "Processing --" + Style.RESET_ALL
        with tqdm(desc=processing, total=100, unit="block", ncols=100, colour="green", bar_format="{desc} {bar} -- {rate_fmt}") as pbar:
            while loading:
                pbar.update(0.5)
                time.sleep(0.2)
            pbar.close()

    process_thread = threading.Thread(target=long_process, args=(env,))
    progress_thread = threading.Thread(target=show_progress)

    process_thread.start()
    progress_thread.start()

    process_thread.join()
    progress_thread.join()

    # This is the data that will be used to construct the improved resume
    env["data"] = {
        "name": env["current_profile"][1],
        "phone": env["current_profile"][2],
        "email": env["current_profile"][3],
        "linkedin": env["current_profile"][4],
        "github": env["current_profile"][5],
        "schools": [{"name": env["manager"].resume_dict["education"][0]["school"],
                     "city": env["manager"].resume_dict["education"][0]["city"],
                     "country": env["manager"].resume_dict["education"][0]["country"],
                     "program": env["manager"].resume_dict["education"][0]["program"],
                     "gpa": env["manager"].resume_dict["education"][0]["gpa"]},
                    {"name": env["manager"].resume_dict["education"][1]["school"],
                     "city": env["manager"].resume_dict["education"][1]["city"],
                     "country": env["manager"].resume_dict["education"][1]["country"],
                     "program": env["manager"].resume_dict["education"][1]["program"],
                     "gpa": env["manager"].resume_dict["education"][1]["gpa"]}],
        "work": [],
        "volunteers": [],
        "projects": [],
        "proficient": [],
        "intermediate": [],
        "technologies": [],
        "soft_skills": []
    }

    add_education_to_database(env["user_database"], env["profile_id"], env)
    add_skills_to_database(env["user_database"], env["profile_id"], env)
    add_experiences_to_database(env["user_database"], env["profile_id"], env)
    add_job_features(env["user_database"], env["current_job_id"], env)

    for exp_id, exp in env["manager"].experience_map.items():
        env["user_database"].update_item(env["profile_id"], "experiences", exp.name, "name", exp.what, "what_improved")
        env["user_database"].update_item(env["profile_id"], "experiences", exp.name, "name", exp.how, "how_improved")
        env["user_database"].update_item(env["profile_id"], "experiences", exp.name, "name", exp.result, "result_improved")

    edit_experience(env)

    compile_resume(env)
