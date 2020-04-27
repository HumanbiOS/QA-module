import os
import json
import string
from collections import OrderedDict
q_a = json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/q_a.json", "r"))
folder_path = os.path.dirname(os.path.abspath(__file__)) + "/covapp/src/global/i18n/"
languages = {}

for _file_name in os.listdir(folder_path):
    languages[_file_name[:-5]] = json.load(open(folder_path + _file_name))
    languages[_file_name[:-5]] = languages[_file_name[:-5]]["keys"]
# now we have to extract the questions and answers in an easier format for us. First we gather all unused keys
keys_to_delete = []
for key in languages["en"]:
    if not key.startswith("q_"):
        if not key.startswith("answer_"):
            keys_to_delete.append(key)
# then we delete them from the dictionaries
for language in languages:
    for key in keys_to_delete:
        del languages[language][key]
# now there are html li tags in there which we can not support, so we replace them with \n
# list of those strings:
html_strings = ["q_SB_comment", "q_C0_comment"]
for language in languages:
    for key in html_strings:
        value_string = languages[language][key]
        # we replace the beginning and end of the list with nothing
        value_string = value_string.replace("<ul><li>", "")
        value_string = value_string.replace("</li></ul>", "")
        # and the middle parts with \n
        value_string = value_string.replace("</li><li>", "\n")
        languages[language][key] = value_string
# this is the basic order we follow, taken from
# https://github.com/d4l-data4life/covapp/blob/d4e91c7311459528b319484a36b74495fd67fcb8/src/global/questions.ts#L51
order = ['P', 'C', 'S', 'D', 'M', 'X']
# then they add numbers
numbers = list(range(10))
# and then letters
letters = string.ascii_uppercase
# now we reorder it so we have the correct order for all questions which dont lead to specific questions
actual_order = []
for beginning in order:
    for number in numbers:
        for dic in q_a:
            if dic["id"] == beginning + str(number):
                actual_order.append(dic)
    for letter in letters:
        for dic in q_a:
            if dic["id"] == beginning + str(letter):
                actual_order.append(dic)
# now we split up the questions to questions and answers
# json.dump(actual_order, open("q_order.json", "w"), indent=4)
questions = OrderedDict()
for index, question in enumerate(actual_order):
    temp_dict = {"text": question["text"], "answers": {}}
    if "nextQuestionMap" in question:
        for next_question_id, answer in enumerate(question["nextQuestionMap"]):
            temp_dict["answers"][question["options"][next_question_id]] = answer
    elif "options" in question:
        if type(question["options"][0]) == str:
            for answer in question["options"]:
                try:
                    temp_dict["answers"][answer] = actual_order[index + 1]["id"]
                except IndexError:
                    break
        # this means we have multiple choices
        else:
            temp_dict["multi"] = True
            for answer in question["options"]:
                temp_dict["answers"][answer["label"]] = answer["id"]
    else:
        temp_dict["answers"]["free"] = actual_order[index + 1]["id"]
    if "comment" in question and question["comment"] is not None:
        temp_dict["comment"] = question["comment"]
    if "scoreMap" in question:
        temp_dict.update({"score": {}, "category": question["category"]})
        for answer_id, score in enumerate(question["scoreMap"]):
            try:
                temp_dict["score"][temp_dict["answers"][question["options"][answer_id]]] = score
            except TypeError:
                # this means we are in multi questions
                temp_dict["score"][temp_dict["answers"][question["options"][answer_id]["label"]]] = score
    if "guard" in question:
        if "conditions" in question["guard"]:
            temp_dict["guard"] = question["guard"]["conditions"]
    questions[question["id"]] = temp_dict
# deleting the empty answer in S2
del questions["S2"]["answers"][""]


def get_question(question_id):
    try:
        return questions[question_id]
    except KeyError:
        return False


def get_question_index(question_id):
    for ind, q_id in enumerate(questions):
        if question_id == q_id:
            return ind


def get_question_id_from_index(question_index):
    for ind, q_id in enumerate(questions):
        if ind == question_index:
            return q_id
