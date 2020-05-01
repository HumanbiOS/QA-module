import json
import os

from .setup import languages, get_question, get_question_index, get_question_id_from_index

cache = {}


class InternQuestion:
    def __init__(self, question_id, score=False, category=False, guard=False, **kwargs):
        self.question_id = question_id
        self.score = score
        self.category = category
        if not guard:
            self.guard = []

    def __repr__(self):
        tmp = dict()
        for k, v in self.__dict__.items():
            tmp[k] = v
        return str(tmp)


class ExternQuestion:
    def __init__(self, lang, question_id, text, answers, comment=False, multi=False, **kwargs):
        self._lang = lang
        self.id = question_id
        self.text = self._get_string(text)
        if comment:
            self.comment = self._get_string(comment)
        else:
            self.comment = False
        if next(iter(answers)) == "free":
            self.free = True
            self.answers = answers["free"]
        else:
            self.free = False
            temp_dict = {}
            for answer in answers:
                temp_dict[self._get_string(answer)] = answers[answer]
            self.answers = temp_dict
        self.multi = multi

    def _get_string(self, string):
        return languages[self._lang][string]

    def __repr__(self):
        tmp = dict()
        for k, v in self.__dict__.items():
            tmp[k] = v
        return str(tmp)


def get_next_question(user_id, lang, next_question_id="P0"):
    if not get_question(next_question_id):
        return False
    question = InternQuestion(next_question_id, **get_question(next_question_id))
    if user_id in cache:
        old_question = cache[user_id]["question"]
        if old_question.score:
            if next_question_id not in old_question.score:
                # this might happen in some weird access way, not able to fix it, its an issue with upstream code
                pass
            elif old_question.score[next_question_id] > 0:
                if old_question.category in cache[user_id]:
                    cache[user_id][old_question.category] += old_question.score[next_question_id]
                else:
                    cache[user_id][old_question.category] = old_question.score[next_question_id]
        cache[user_id]["question"] = question
    else:
        cache[user_id] = {"question": question}
    if question.guard:
        fail = False
        for test in question.guard:
            if test["category"] not in cache[user_id]:
                fail = True
                break
            else:
                if cache[user_id][test["category"]] < test["min"]:
                    fail = True
                    break
        if fail:
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
