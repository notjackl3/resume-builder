from bot_manager import Manager
from exporter.converter import update_resume
from exporter.converter import export_to_pdf
from database_manager import UserDatabaseManager

MONTH_TO_MONTH = {
    "january": '01', "jan": '01',
    "february": '02', "feb": '02',
    "march": '03', "mar": '03',
    "april": '04', "apr": '04',
    "may": '05',
    "june": '06', "jun": '06',
    "july": '07', "jul": '07',
    "august": '08', "aug": '08',
    "september": '09', "sep": '09',
    "october": '10', "oct": '10',
    "november": '11', "nov": '11',
    "december": '12', "dec": '12'
}

manager = Manager(resume="../documents/Resume Huu An Duc Le.pdf",
                  job_desc="../documents/jobs.txt")
manager.extract_information_resume("../documents/outputs/output.txt", update=False)
manager.extract_information_job("../documents/outputs/output-job.txt", update=False)
manager.update_data()


def make_date(input, start_end):
    temp = None
    if start_end.lower() == "start":
        temp = input.split("-")[0].split(",")
    elif start_end.lower() == "end":
        temp = input.split("-")[1].split(",")
        for info in temp:
            if info.lower().strip() == "present":
                return "Present"

    m = temp[0].strip()
    y = temp[1].strip()

    start_month = None
    start_year = y
    for key, value in MONTH_TO_MONTH.items():
        if key in m.lower():
            start_month = value
    if start_month:
        return f"{start_year}-{start_month}-01"
    else:
        return "NULL"


user_database = UserDatabaseManager("localhost",
                                    "resume builder",
                                    "notjackl3",
                                    "itismejack",
                                    "5432")


def reset_database(database: UserDatabaseManager):
    database.delete_table("experiences")
    database.delete_table("skills")
    database.delete_table("education")
    database.delete_table("jobs")
    database.delete_table("job_features")
    database.delete_table("profile")
    user_database.create_new_database(manager.resume_dict["name"],
                                      manager.resume_dict["contact"]["email"],
                                      manager.resume_dict["contact"]["phone"],
                                      manager.resume_dict["contact"]["linkedin"],
                                      manager.resume_dict["contact"]["github"],
                                      new=False)


reset_database(user_database)


# output = user_database.get_id("Jack")
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


add_education_to_database(user_database, 1)


def add_skills_to_database(database: UserDatabaseManager, id: int):
    all_soft_skills = [("soft", x) for x in manager.resume_dict["soft-skills"]]
    database.add_skills(id, all_soft_skills)

    all_technical_skills = [("technical", x) for x in manager.resume_dict["technical-skills"]]
    database.add_skills(id, all_technical_skills)

    all_interests = [("interest", x) for x in manager.resume_dict["interests"]]
    database.add_skills(1, all_interests)


add_skills_to_database(user_database, 1)


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


add_experiences_to_database(user_database, 1)


def add_job_to_database(database: UserDatabaseManager, id: int):
    title = input("What is the job title? ")
    company_name = input("What is the company name? ")
    with open("../documents/inputs/jobs.txt") as file:
        job_description = file.read()
    database.add_job(id, title, company_name, job_description)


add_job_to_database(user_database, 1)


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


add_job_features(user_database, 1)
