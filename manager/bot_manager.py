import ast
from typing import Union
import json
from openai import OpenAI
import textract
import re

from extractor import ResumeExtractor, JobDescriptionExtractor
from processor import MatchingProcessor, WritingProcessor, RefiningProcessor, CombiningProcessor, ApplyMatching
from experiences_manager import Experience

from dotenv import load_dotenv
import os

load_dotenv("api.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def process_information(bot: Union[ResumeExtractor, JobDescriptionExtractor], to_file: str, input: str):
    with open(to_file, "w") as file:
        output = bot.extract(input)
        file.write(output)
    return output


def use_file(file: str):
    with open(file) as file:
        return file.read()


class Manager:
    def __init__(self, resume: str, job_desc: str):
        self.resume_file = resume
        self.job_desc_file = job_desc
        self.matching_file = "../documents/outputs/output-match.json"
        self.resume_dict = {}
        self.job_desc_dict = {}
        self.matching_dict = {}

        self.resume_bot = ResumeExtractor()
        self.job_desc_bot = JobDescriptionExtractor()
        self.matching_bot = MatchingProcessor()
        self.writing_bot = WritingProcessor()
        self.refining_bot = RefiningProcessor()
        self.combining_bot = CombiningProcessor()
        self.apply_matching_bot = ApplyMatching()

        self.experience_data = []
        self.skill_data = []
        self.matching_data = None
        self.experience_map = {}
        self.mixed_map = {}

    def extract_information_resume(self, path: str, update: bool=True):
        if update:
            extracted_resume_text = textract.process(self.resume_file, method='pdfminer').decode('utf-8')
            process_information(self.resume_bot, path, extracted_resume_text)
        # self.resume_dict = ast.literal_eval(use_file(path))
        self.resume_dict = json.loads(use_file(path))

    def extract_information_job(self, path: str, update: bool=True):
        if update:
            extracted_job_desc_text = textract.process(self.job_desc_file, method='pdfminer').decode('utf-8')
            process_information(self.job_desc_bot, path,
                                extracted_job_desc_text)
        self.job_desc_dict = ast.literal_eval(use_file(path))

    def _add_experience(self, target):
        output = []
        for exp in self.resume_dict[target]:
            output.append(Experience(name=exp["name"],
                                     what=exp["what"],
                                     where=exp["where"],
                                     how=exp["how"],
                                     when=exp["when"],
                                     result=exp["result"],
                                     type=exp["type"]))
        return output

    def _add_skills(self, target):
        output = []
        for skill in self.resume_dict[target]:
            output.append(skill)
        return output

    def update_data(self):
        self.experience_data.extend(self._add_experience("work-experiences"))
        self.experience_data.extend(self._add_experience("volunteer-experiences"))
        self.skill_data.extend(self._add_skills("technical-skills"))
        self.skill_data.extend(self._add_skills("soft-skills"))
        self.skill_data.extend(self._add_skills("interests"))

    def _matching(self, data, search: str, to_look: list):
        if search == "what":
            return ast.literal_eval(self.matching_bot.process([(x.id, x.what) for x in data], to_look))
        elif search == "how":
            return ast.literal_eval(self.matching_bot.process([(x.id, x.how) for x in data], to_look))
        elif search == "result":
            return ast.literal_eval(self.matching_bot.process([(x.id, x.result) for x in data], to_look))

    def update_matches(self):
        self.matching_data = {"what": self._matching(data=self.experience_data, search="what",
                                                     to_look=self.job_desc_dict["responsibilities"]
                                                             + self.job_desc_dict["soft-skills"]
                                                             + self.job_desc_dict["action-verbs"]),
                              "how": self._matching(data=self.experience_data, search="how",
                                                    to_look=self.job_desc_dict["hard-skills"]
                                                            + self.job_desc_dict["technology"]
                                                            + self.job_desc_dict["action-verbs"]),
                              "result": self._matching(data=self.experience_data, search="result",
                                                       to_look=self.job_desc_dict["action-verbs"]
                                                               + self.job_desc_dict["responsibilities"]
                                                               + self.job_desc_dict["preferred-experiences"])}
        with open(self.matching_file, "w") as file:
            json.dump(self.matching_data, file)
        with open(self.matching_file, "r") as file:
            self.matching_dict = json.load(file)

    def update_experience_maps(self):
        self.experience_map = {}
        self.mixed_map = {}
        for exp in self.experience_data:
            self.experience_map[exp.id] = exp
        for exp in self.experience_data:
            self.mixed_map[exp.id] = []

    def allocate_matching(self, search: str):
        for exp_id, matches in self.matching_dict[search]["matching-pairs"].items():
            if matches:
                to_match = self.matching_dict[search]["matching-pairs"][exp_id]
                output = self.writing_bot.process(getattr(self.experience_map[int(exp_id)], search), to_match)
                refined_output = self.refining_bot.process(output, to_match)
                setattr(self.experience_map[int(exp_id)], search, refined_output)
        # if search == "what":
        #     for exp_id, matches in self.matching_dict["what"]["matching-pairs"].items():
        #         if matches:
        #             to_match = self.matching_dict["what"]["matching-pairs"][exp_id]
        #             output = self.writing_bot.process(self.experience_map[int(exp_id)].what, to_match)
        #             refined_output = self.refining_bot.process(output, to_match)
        #             self.experience_map[int(exp_id)].what += refined_output
        # elif search == "how":
        #     for exp_id, matches in self.matching_dict["how"]["matching-pairs"].items():
        #         if matches:
        #             to_match = self.matching_dict["how"]["matching-pairs"][exp_id]
        #             output = self.writing_bot.process(self.experience_map[int(exp_id)].how, to_match)
        #             refined_output = self.refining_bot.process(output, to_match)
        #             self.experience_map[int(exp_id)].how += refined_output
        # elif search == "result":
        #     for exp_id, matches in self.matching_dict["result"]["matching-pairs"].items():
        #         if matches:
        #             to_match = self.matching_dict["result"]["matching-pairs"][exp_id]
        #             output = self.writing_bot.process(self.experience_map[int(exp_id)].result, to_match)
        #             refined_output = self.refining_bot.process(output, to_match)
        #             self.experience_map[int(exp_id)].result += refined_output

    def apply_match(self):
        output = []
        final = []
        existed = []
        for key, lst in self.job_desc_dict.items():
            for word in lst:
                output.append(word.lower())
        for exp_id, exp in enumerate(self.experience_data):
            result = ast.literal_eval(self.apply_matching_bot.process(exp.info, output))
            refined = ast.literal_eval(re.search(r'\[(.*?)\]', self.combining_bot.process(result[0], existed)).group(1))
            existed.extend(refined)
            result[0] = refined
            for word in result[1]:
                if word.lower() in output:
                    output.remove(word.lower())
            final.append([exp_id] + result)
        return final
