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
user_database.create_new_database(manager.resume_dict["name"],
                                  manager.resume_dict["contact"]["email"],
                                  manager.resume_dict["contact"]["phone"],
                                  manager.resume_dict["contact"]["linkedin"],
                                  manager.resume_dict["contact"]["github"],
                                  new=False)

# output = user_database.get_id("Jack")
new_edu = False
for edu in manager.resume_dict["education"]:
    start_date = make_date(edu["when"], "start")
    end_date = make_date(edu["when"], "end")

    user_database.add_education(1,
                                edu["school"],
                                edu["program"],
                                start_date,
                                end_date,
                                edu["city"],
                                edu["school"],
                                edu["gpa"],
                                new=new_edu)

    new_edu = False


def add_skills_to_database(database: UserDatabaseManager, id: int):
    all_soft_skills = [("soft", x) for x in manager.resume_dict["soft-skills"]]
    database.add_skills(id, all_soft_skills)

    all_technical_skills = [("technical", x) for x in manager.resume_dict["technical-skills"]]
    database.add_skills(id, all_technical_skills)

    all_interests = [("interest", x) for x in manager.resume_dict["interests"]]
    database.add_skills(1, all_interests)


user_database.delete_table("skills")
add_skills_to_database(user_database, 1)


def add_experiences_to_database(database: UserDatabaseManager, id: int):
    # for work in manager.resume_dict["work-experiences"]:
    #     start_date = make_date(work["when"], "start")
    #     end_date = make_date(work["when"], "end")
    #     database.add_experience(id,
    #                             work["name"],
    #                             work["type"],
    #                             work["what"],
    #                             work["where"],
    #                             work["how"],
    #                             start_date,
    #                             end_date,
    #                             work["result"],
    #                             new=True)
    # for volunteer in manager.resume_dict["volunteer-experiences"]:
    #     start_date = make_date(volunteer["when"], "start")
    #     end_date = make_date(volunteer["when"], "end")
    #     database.add_experience(id,
    #                             volunteer["name"],
    #                             volunteer["type"],
    #                             volunteer["what"],
    #                             volunteer["where"],
    #                             volunteer["how"],
    #                             start_date,
    #                             end_date,
    #                             volunteer["result"],
    #                             new=False)
    database.delete_table("experiences")
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
