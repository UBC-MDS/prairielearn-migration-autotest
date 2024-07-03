import os
import json


class QuestionBank:
    def __init__(self, question_dir, question_file="question.html"):
        self.questions = {}

        # Walk the directory tree
        for root, dirs, files in os.walk(question_dir):
            if question_file in files and "lec_" in root:
                with open(os.path.join(root, "info.json"), "r") as f:
                    question_info = json.load(f)

                qid = root.replace(question_dir + "/", "")
                self.questions[qid] = question_info["tags"]

    def find_questions(self, tags):
        if isinstance(tags, str):
            tags = [tags]

        questions_list = []
        for key, item in self.questions.items():
            save = True
            for tag in tags:
                if tag not in item:
                    save = False
            if save:
                questions_list.append(key)
        if len(questions_list) == 0:
            print("No question found for tags {}".format(tags))
        return [{"id": qid} for qid in questions_list]
