import json
import os

from .setup import languages, get_question, get_question_index, get_question_id_from_index

cache = {}


def get_string(lang, string):
    try:
        return languages[lang][string]
    except KeyError:
        return languages["en"][string]


class InternQuestion:
    def __init__(self, question_id, score=False, category=False, guard=None, **kwargs):
        if guard is None:
            guard = []
        self.guard = guard
        self.question_id = question_id
        self.score = score
        self.category = category

    def __repr__(self):
        tmp = dict()
        for k, v in self.__dict__.items():
            tmp[k] = v
        return str(tmp)


class ExternQuestion:
    def __init__(self, lang, question_id, text, answers, comment=False, multi=False, **kwargs):
        self._lang = lang
        self.id = question_id
        self.text = get_string(lang, text)
        if comment:
            self.comment = get_string(lang, comment)
        else:
            self.comment = False
        if next(iter(answers)) == "free":
            self.free = True
            self.answers = answers["free"]
        else:
            self.free = False
            temp_dict = {}
            for answer in answers:
                temp_dict[get_string(lang, answer)] = answers[answer]
            self.answers = temp_dict
        self.multi = multi

    def __repr__(self):
        tmp = dict()
        for k, v in self.__dict__.items():
            tmp[k] = v
        return str(tmp)


def get_next_question(user_id, lang, next_question_id="P0"):
    if len(next_question_id) == 3:
        specific = next_question_id
        next_question_id = next_question_id[:2]
    else:
        specific = next_question_id
    if not get_question(next_question_id):
        if "scores" not in cache[user_id]:
            return get_string(lang, "recommendation_2")
        scores = cache[user_id]["scores"]
        if "contact" in scores:
            return get_string(lang, "recommendation_0")
        if "symptoms" in scores and scores["symptoms"] > 3:
            return get_string(lang, "recommendation_0")
        else:
            return get_string(lang, "recommendation_1")
    question = InternQuestion(next_question_id, **get_question(next_question_id))
    if user_id in cache:
        old_question = cache[user_id]["question"]
        if old_question.score:
            if specific not in old_question.score:
                # this might happen in some weird access way, not able to fix it, its an issue with upstream code
                pass
            elif old_question.score[specific] > 0:
                if old_question.category in cache[user_id]["scores"]:
                    cache[user_id]["scores"][old_question.category] += old_question.score[specific]
                else:
                    cache[user_id]["scores"][old_question.category] = old_question.score[specific]
        cache[user_id]["question"] = question
    else:
        cache[user_id] = {"question": question, "scores": {}}
    if question.guard:
        if not _test_question(question, user_id):
            index = get_question_index(question.question_id)
            next_question_id = get_question_id_from_index(index + 1)
            question = InternQuestion(next_question_id, **get_question(next_question_id))
            cache[user_id]["question"] = question
    return ExternQuestion(lang, next_question_id, **get_question(next_question_id))


def get_english_strings():
    return languages["en"]


def put_translated_strings(language_code, language_dict):
    languages[language_code] = language_dict
    json.dump(languages, open(os.path.dirname(os.path.abspath(__file__)) + "/strings.json", "w"), indent=4)


def get_user_scores(user_id):
    return cache[user_id]["scores"]


def get_previous_question(user_id, lang, question_id):
    index = get_question_index(question_id)
    previous_question_id = get_question_id_from_index(index - 1)
    if not previous_question_id:
        return None
    question = InternQuestion(previous_question_id, **get_question(previous_question_id))
    if question.guard:
        if not _test_question(question, user_id):
            index = get_question_index(question.question_id)
            previous_question_id = get_question_id_from_index(index - 1)
            question = InternQuestion(previous_question_id, **get_question(previous_question_id))
            cache[user_id]["question"] = question
    return ExternQuestion(lang, previous_question_id, **get_question(previous_question_id))


def _test_question(question, user_id):
    for test in question.guard:
        if test["category"] not in cache[user_id]["scores"]:
            return False
        else:
            if cache[user_id]["scores"][test["category"]] < test["min"]:
                return False
    return True
