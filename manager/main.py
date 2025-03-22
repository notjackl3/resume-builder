def run(file1, file2):
    import os
    import sys
    import tkinter as tk
    from tkinterdnd2 import DND_FILES, TkinterDnD

    from bot_manager import Manager

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from exporter.converter import update_resume
    from exporter.converter import export_to_pdf
    from database_manager import UserDatabaseManager
    from dotenv import load_dotenv
    from utils import make_date
    from utils import add_experience, add_coding_languages, add_technical_skills, add_soft_skills

    load_dotenv("api.env")

    HOSTNAME = os.getenv("HOSTNAME")
    DATABASE = os.getenv("DATABASE")
    USERNAME = os.getenv("USERNAME")
    PWD = os.getenv("PWD")
    PORT_ID = os.getenv("PORT_ID")

    # manager = Manager(resume="../documents/inputs/Diep Anh Nguyen Official Resume.pdf",
    #                   job_desc="../documents/inputs/jobs.txt")

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
        user_database.create_new_database(manager.resume_dict["name"],
                                          manager.resume_dict["contact"]["email"],
                                          manager.resume_dict["contact"]["phone"],
                                          manager.resume_dict["contact"]["linkedin"],
                                          manager.resume_dict["contact"]["github"],
                                          new=False)

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
        database.add_skills(1, all_interests)

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
        for x in manager.job_desc_dict["responsibilities"]:
            database.add_job_features(x, "responsibility", id)
        for x in manager.job_desc_dict["soft-skills"]:
            database.add_job_features(x, "soft-skill", id)
        for x in manager.job_desc_dict["hard-skills"]:
            database.add_job_features(x, "hard-skill", id)
        for x in manager.job_desc_dict["preferred-experiences"]:
            database.add_job_features(x, "preferred-experience", id)
        for x in manager.job_desc_dict["technologies"]:
            database.add_job_features(x, "technology", id)
        for x in manager.job_desc_dict["action-verbs"]:
            database.add_job_features(x, "action-verb", id)
        for x in manager.job_desc_dict["coding-languages"]:
            database.add_job_features(x, "coding-language", id)

    reset_database(user_database)
    add_education_to_database(user_database, 1)
    add_skills_to_database(user_database, 1)
    add_experiences_to_database(user_database, 1)
    add_job_to_database(user_database, 1)
    add_job_features(user_database, 1)
