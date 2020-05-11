import json
import os

folder_path = os.path.dirname(os.path.abspath(__file__)) + "/covapp/src/global/i18n/"
languages = {}

for _file_name in os.listdir(folder_path):
    languages[_file_name[:-5]] = json.load(open(folder_path + _file_name))
    languages[_file_name[:-5]] = languages[_file_name[:-5]]["keys"]
# now we have to extract the questions and answers in an easier format for us. First we gather all unused keys
keys_to_delete = []
for key in languages["en"]:
    # all keys not starting with a q_ are not questions
    if not key.startswith("q_"):
        # and we need to include the answers
        if not key.startswith("answer_"):
            # and we need the next key
            if key != "questionnaire_button_next":
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
# now we save it to a json
json.dump(languages, open(os.path.dirname(os.path.abspath(__file__)) + "/strings.json", "w"), indent=4)
