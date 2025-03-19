from typing import Any
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv("api.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

GPT_MODEL = "gpt-3.5-turbo"
RESUME_PROMPT = ("You will be provided with a resume file, your job is to extract exactly the information."
                 "For each experience (both volunteer and work), store them as a dictionary, talking about"
                 "what they do, where they do it, how they do it, when they do it, type of experience (volunteer/work),"
                 "the results: {[{'name': <str>}, {'what': <str>}, {'where': <str>}, {'how': <str>}, {'when': <str>}, "
                 "{'type': <str>} {'result': <str>}]}. Education, skills, interests and other information should stored as a dictionary:"
                 "{'education': [{'school': <str>, 'program':<str>, 'when': <str>, 'city': <str>, 'country': <str>, 'gpa':<str>}], "
                 "'soft-skills': [<str>], 'technical-skills': [<str>], 'interests': [<str>], 'awards': [<str>]}."
                 "The output must follow this structure strictly and do not skip small details like numerical data."
                 "The final structure of the dictionary should be name, contact (email, phone, linkedin, github), education, work-experiences,"
                 "volunteer-experiences, soft-skills, technical-skills, interests.")
RESUME_CREATIVITY = 0.2
RESUME_ACCURACY = 0.2

JOB_PROMPT = ("You will act as a helpful hiring manager. You will be given a job description,"
              "and your task is to list out every keywords, such as responsibilities,"
              "skills-based keywords (technical and soft skills), industry keywords, action verbs,"
              "certification, tools, and even the words that are repeated the most. If the word contains"
              "the character ', remember to add an escape character before it, to prevent errors."
              "The output must be a python dictionary containing lists of these SINGLE keywords, {aspect: [<str>]}. "
              "The aspects are responsibilities, soft-skills, hard-skills, preferred-experiences, technology, "
              "action-verbs, coding-languages"
              "These aspects are the dictionary keys, with list of SINGLE keywords as the values."
              "Keywords should be a single word or phrase, they cannot be sentences, try to include as many keywords "
              "as possible for each category.")
JOB_CREATIVITY = 0.5
JOB_ACCURACY = 0.5


class Extractor:
    def __init__(self, model: str, prompt: str, creativity: float, accuracy: float) -> None:
        self._model = model
        self._prompt = prompt
        self._creativity = creativity
        self._accuracy = accuracy

    def extract(self, data: Any):
        raise NotImplementedError


class ResumeExtractor(Extractor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = RESUME_PROMPT,
                 creativity: float = RESUME_CREATIVITY, accuracy: float = RESUME_ACCURACY):
        Extractor.__init__(self, model, prompt, creativity, accuracy)

    def extract(self, data: Any):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": data
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy,
            max_tokens=2048,
            frequency_penalty=0,
            presence_penalty=0
        )
        return resume_extractor.choices[0].message.content


class JobDescriptionExtractor(Extractor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = JOB_PROMPT,
                 creativity: float = JOB_CREATIVITY, accuracy: float = JOB_ACCURACY):
        Extractor.__init__(self, model, prompt, creativity, accuracy)

    def extract(self, data: Any):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": data
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content
