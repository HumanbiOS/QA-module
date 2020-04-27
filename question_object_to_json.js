"use strict";
exports.__esModule = true;
var questions_1 = require("./covapp/src/global/questions");
var fs = require('fs');
var jsonString = JSON.stringify(questions_1.QUESTIONS);
fs.writeFile(__dirname + "/q_a.json", jsonString, function(err) {
    if (err) {
        console.log(err);
    }
});
