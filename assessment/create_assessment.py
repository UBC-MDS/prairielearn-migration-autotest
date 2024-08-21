import uuid
import argparse
import os
import yaml
import json
from assessment_utils import QuestionBank

parser = argparse.ArgumentParser()
parser.add_argument("--config_path", default="assessment/assessment.yml")
args = parser.parse_args()

if not os.path.exists(args.config_path):
    raise Exception(f"{args.config_path} is missing")

with open(args.config_path, "r") as yaml_file:
    info = yaml.safe_load(yaml_file)

# find the question bank and the questions matching tags
qb = QuestionBank(f"{info['pl_repo']}/questions")

for question in info["pl_zones"]["questions"]:
    alternatives = []
    for tag in question["tags"].split("+"):
        alternatives += qb.find_questions(tag.split("&"))

    question["alternatives"] = alternatives
    del question["tags"]

pl_assessment = {
    "uuid": str(uuid.uuid4()),
    "type": "Exam",
    "text": info["quiz_description"],
    "set": info["quiz_set"],
    "number": info["quiz_number"],
    "title": info["quiz_title"],
    "shuffleQuestions": True,
    "allowAccess": [],  # {"startDate": quiz_time, "credit": 100}
    "zones": [info["pl_zones"]],  # zones need to be a list
    "comment": "",
}

assessment_folder = os.path.join(
    info["pl_repo"], "courseInstances", info["course_instance"], "assessments"
)
if not os.path.exists(assessment_folder):
    os.mkdir(assessment_folder)

assessment_name = f"{info['quiz_set']}{info['quiz_number']}"
assessment_folder = os.path.join(assessment_folder, assessment_name)
if not os.path.exists(assessment_folder):
    os.mkdir(assessment_folder)

with open(os.path.join(assessment_folder, "infoAssessment.json"), "w") as assessment:
    json.dump(pl_assessment, assessment, indent=4)
