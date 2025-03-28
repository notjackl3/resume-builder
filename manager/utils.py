from random import shuffle

CODING_LANGUAGES = [
    "python",
    "javascript",
    "java",
    "c",
    "c++",
    "ruby",
    "php",
    "swift",
    "go",
    "kotlin",
    "typescript",
    "rust",
    "r",
    "html",
    "css",
    "sql",
    "shell",
    "dart",
    "lua",
    "haskell",
    "objective-c",
    "perl",
    "scala",
    "groovy",
    "elixir",
    "c#"
]

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


def make_date(input, start_end):
    if not input:
        return ""

    temp = None
    if start_end.lower() == "start":
        temp = input.split("-")[0].split(",")
    elif start_end.lower() == "end":
        temp = input.split("-")[1].split(",")
        for info in temp:
            if info.lower().strip() == "present":
                return "Present"
            elif info.lower().strip() == "now":
                return "Now"

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


def add_experience(data: dict, information: dict):
    for exp_id, exp in information.items():
        if exp.type == "work":
            print(exp.name)
            data["work"].append({"title": exp.name.strip(),
                                 "start_date": exp.when.split("-")[0].strip(),
                                 "end_date": exp.when.split("-")[1].strip(),
                                 "where": exp.where.strip(),
                                 "country": exp.where.strip(),
                                 "description": [attr.strip() for attr in [exp.what, exp.how, exp.result] if attr]})
        elif exp.type == "volunteer":
            data["volunteers"].append({"title": exp.name.strip(),
                                       "start_date": exp.when.split("-")[0].strip(),
                                       "end_date": exp.when.split("-")[1].strip(),
                                       "where": exp.where.strip(),
                                       "country": exp.where.strip(),
                                       "description": [attr.strip() for attr in [exp.what, exp.how, exp.result] if attr]})


def add_coding_languages(data: dict, coding_languages: list, black_list: list):
    for x in coding_languages:
        if x not in black_list:
            data["intermediate"].append(x)
        else:
            data["proficient"].append(x)


def add_technical_skills(data: list, information: dict, proficient: list, intermediate: list):
    for x in information["technical-skills"]:
        if x not in proficient + intermediate:
            if x.lower() in CODING_LANGUAGES:
                proficient.append(x)
            else:
                data.append(x)


def add_soft_skills(data: list, job_soft_skills: list, soft_skills: list):
    word_count = 0
    possible_soft_skills = job_soft_skills + soft_skills
    shuffle(possible_soft_skills)
    for x in possible_soft_skills:
        if word_count < 200 and x not in data:
            data.append(x)
            word_count += len(x)
