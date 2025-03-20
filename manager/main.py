from bot_manager import Manager
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exporter.converter import update_resume
from exporter.converter import export_to_pdf
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

manager = Manager(resume="../documents/inputs/Resume Huu An Duc Le.pdf",
                  job_desc="../documents/inputs/jobs.txt"
                  )
manager.extract_information_resume("../documents/outputs/output.txt")
manager.extract_information_job("../documents/outputs/output-job.txt")
manager.update_data()
manager.update_matches()
manager.update_experience_maps()

manager.allocate_matching("what")
manager.allocate_matching("how")
manager.allocate_matching("result")

# matching_output = manager.apply_match()
# for match in matching_output:
#     if match[0] in manager.experience_map:
#         manager.experience_map[match[0]].improved_version = match[1]

data = {
    "name": manager.resume_dict["name"],
    "phone": manager.resume_dict["contact"]["phone"],
    "email": manager.resume_dict["contact"]["email"],
    "linkedin": manager.resume_dict["contact"]["linkedin"],
    "github": "...",
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

for exp_id, exp in manager.experience_map.items():
    if exp.type == "work":
        data["jobs"].append({"title": exp.name.strip(),
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

for x in manager.job_desc_dict["coding-languages"]:
    if x not in manager.skill_data:
        data["intermediate"].append(x)
    else:
        data["proficient"].append(x)

for x in manager.resume_dict["technical-skills"]:
    if x not in data["proficient"] + data["intermediate"]:
        if x.lower() in CODING_LANGUAGES:
            data["proficient"].append(x)
        else:
            data["technologies"].append(x)

word_count = 0
possible_soft_skills = manager.job_desc_dict["soft-skills"] + manager.resume_dict["soft-skills"]
shuffle(possible_soft_skills)
for x in possible_soft_skills:
    if word_count < 200 and x not in data["soft_skills"]:
        data["soft_skills"].append(x)
        word_count += len(x)

update_resume("../exporter", data)
export_to_pdf("generated_resume.tex", "../exporter")

print(manager.job_desc_dict)
