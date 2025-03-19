from typing import Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv("api.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

GPT_MODEL = "gpt-3.5-turbo"
MATCHING_PROMPT = ("You will be provided with 2 lists. List 1 contains tuples of (id, text)."
                   "List 2 contains keywords about a job. You have to iterate through list 1, processing the text "
                   "element inside the tuple, then check if any item in list 2 matches semantically. "
                   "If there is a match, store them as a dictionary, key is the id of the text, value is the list"
                   "of keywords that the text matches. If there is no match, you can have an empty list."
                   "The format must be {id: [matching keywords]}. At the end, all the keywords that matched previously, "
                   "store them as a list of these keywords: [word1, ..]. The final output should be a dictionary of: "
                   "{'matching-pairs': {id: [matching keywords], ..}, 'matched': [word1, ..]}. For matching-pairs, "
                   "even if there is nothing matched, you must include the id with an empty dictionary.")
MATCHING_CREATIVITY = 0.7
MATCHING_ACCURACY = 0.8

WRITING_PROMPT = ("You will act as a helpful hiring manager, you will help me improve my writing significantly. "
                  "You will be provided with a text and a python list of keywords. The text is my version of the "
                  "experience, the list will be keywords that should to be included. Try your best to fit the keywords "
                  "in the text provided, without changing the meaning and details of the text. If a word is completely "
                  "irrelevant, do not force it in. The final output should be a new improved sentence.")
WRITING_CREATIVITY = 0.7
WRITING_ACCURACY = 0.8

REFINING_PROMPT = ("You will act as a helpful hiring manager and a professional writer, you will help me improve "
                   "my writing for resume significantly. You will be provided with a text, your job is to make it "
                   "sound professional and precise. Try your best to not change the keywords or details, but fix the "
                   "sentence structure and make sure they are appropriate to be included in the resume. Additionally, "
                   "there will be a python list attached. Try to use these words if possible. If these words make the "
                   "sentence less impactful, you can then remove it, or else, try to include it. Try not to talk in "
                   "first person, simply write for example: 'develop app' instead of 'i develop an app' "
                   "The final output should be a new improved sentence")
REFINING_CREATIVITY = 0.3
REFINING_ACCURACY = 0.4

COMBINING_PROMPT = ("You will act as a professional writer. You will be given a Python list of text, go through it "
                    "and make sure to delete any duplicate sentences that is in the list, also try your best to replace"
                    " words with synonyms if there are duplicate words or phrases. You will also be given a second "
                    "Python list of text, the second list are sentences, make sure to avoid duplicate words and phrases "
                    "that already existed. The output must contain nothing besides a list, the format [sentence1, sentence2,..]")
COMBINING_CREATIVITY = 0.3
COMBINING_ACCURACY = 0.4

APPLY_MATCHING_PROMPT = ("You will act as a helpful hiring manager and a professional writer."
                         "You will be provided with a list of text and a list of keywords. If you see that there are "
                         "keywords that can be included in the texts, try your best to integrate the keyword inside "
                         "these sentences, without changing too much the structure and meaning. The output must be "
                         "a Python list of list. The first list is the same list of text but now improved with new "
                         "keywords. The second list should be the keywords that has been used, included. So the final "
                         "output would in the [[sentence1, sentence2,..],[word1, word2,..]] format.")
APPLY_MATCHING_CREATIVITY = 0.3
APPLY_MATCHING_ACCURACY = 0.4


class Processor:
    def __init__(self, model: str, prompt: str, creativity: float, accuracy: float) -> None:
        self._model = model
        self._prompt = prompt
        self._creativity = creativity
        self._accuracy = accuracy

    def process(self, data: Any, keywords: Any):
        raise NotImplementedError


class MatchingProcessor(Processor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = MATCHING_PROMPT,
                 creativity: float = MATCHING_CREATIVITY, accuracy: float = MATCHING_ACCURACY):
        Processor.__init__(self, model, prompt, creativity, accuracy)

    def process(self, data: list, keywords: list):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": f"Data to match: {data}, possible matches: {keywords}"
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content


class WritingProcessor(Processor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = WRITING_PROMPT,
                 creativity: float = WRITING_CREATIVITY, accuracy: float = WRITING_ACCURACY):
        Processor.__init__(self, model, prompt, creativity, accuracy)

    def process(self, input: str, keywords: list):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": f"Text: {input}, possible keywords: {keywords}"
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content


class RefiningProcessor(Processor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = REFINING_PROMPT,
                 creativity: float = REFINING_CREATIVITY, accuracy: float = REFINING_ACCURACY):
        Processor.__init__(self, model, prompt, creativity, accuracy)

    def process(self, input: str, keywords: list):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": f"Text: {input}, possible keywords: {keywords}"
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content


class CombiningProcessor(Processor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = COMBINING_PROMPT,
                 creativity: float = COMBINING_CREATIVITY, accuracy: float = COMBINING_ACCURACY):
        Processor.__init__(self, model, prompt, creativity, accuracy)

    def process(self, input: str, keywords=None):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": f"Text to process: {input}. Text to avoid: {keywords}"
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content


class ApplyMatching(Processor):
    def __init__(self, model: str = GPT_MODEL, prompt: str = APPLY_MATCHING_PROMPT,
                 creativity: float = APPLY_MATCHING_CREATIVITY, accuracy: float = APPLY_MATCHING_ACCURACY):
        Processor.__init__(self, model, prompt, creativity, accuracy)

    def process(self, input: str, keywords=None):
        resume_extractor = client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._prompt
                },
                {
                    "role": "user",
                    "content": f"List of text: {input}. Words to avoid: {keywords}"
                }
            ],
            temperature=self._creativity,
            top_p=self._accuracy
        )
        return resume_extractor.choices[0].message.content
