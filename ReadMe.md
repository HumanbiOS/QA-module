How to use

Pretty easy. Import `get_next_question` from `methods`. Pass a unique user_id, lang (currently only "de" or "en"). You can expect to get an object returned which has the following attributes: `text` which is the basic text and `answers` which is a dictionary, mapping the answer to the next question id. The following attributes are optional, but always there and set to false (so you can do if question.attribute): `comment` which is a longer explanation or `multi` which would be a multi answer question.

In the end, return the new question id alongside the other variables. For the multi questions, pick the last answer/question id you get. If the returned value is False, you have reached the end.

Development

make sure that you initialized the submodule, then you need to run `npm ci` from inside the covapp directory to install the dependencies. Then run `npm start` which copies the rest of the modules. Once its running, abort it. From there, run `tsc covapp/src/global/questions.ts 
` which generates the .js file from that ts one. Ignore the one error popping up and telling you that --jsx is not set. Now you can use `node question_object_to_json.js` to generate the `q_a.json`
`