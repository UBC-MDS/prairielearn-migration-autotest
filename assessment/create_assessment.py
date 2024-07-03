import uuid
import os
import json
from assessment_utils import QuestionBank

####
# You need to provide the course details here, especially quiz_number
pl_repo = "pl-ubc-dsci523"
course_instance = "Fall2024"
quiz_set = "Quiz"
quiz_number = "2"
quiz_title = ""
quiz_description = ""
quiz_time = ""

qb = QuestionBank(f"{pl_repo}/questions")

# choose your questions using qb.find_questions. The function returns a list of QIDs that match all tags
# The example below are for 512. The first example is fot Quiz 1 and the second example if for Quiz 2
pl_zones = [
    {
        "title": "Lecture 1",
        "questions": [
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["read"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["tidy-data", "mcq"])
                + qb.find_questions(["pipe-operator", "mcq"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["pivot-wider-longer", "coding"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["dplyr-functions", "coding"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["datatypes-definition", "mcq"])
                + qb.find_questions(["subset", "mcq"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["tidyverse-style", "mcq"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["tidyverse-style", "coding"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["date-time-manipulation", "coding"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["string-modification"])
                + qb.find_questions(["factor-management"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["joins-comparison"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["dplyr-join-functions"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["conditional-statements"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["for-loop"]),
            },
        ],
    }
]
pl_zones = [
    {
        "title": "Lecture 1",
        "questions": [
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["missing-erroneous"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["split-apply-combine"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["function-definition"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["lazy-evaluation"])
                + qb.find_questions(["testthat"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["error-handling"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["function-documentation"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["nested-df"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["nested-df-discussion"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["purrr-map-functions"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["data-masking"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["enquo-bang"]),
            },
            {
                "numberChoose": 1,
                "autoPoints": 2,
                "alternatives": qb.find_questions(["curly-operator"]),
            },
        ],
    }
]
####


assessment_name = f"{quiz_set}{quiz_number}"

pl_assessment = {
    "uuid": str(uuid.uuid4()),
    "type": "Exam",
    "text": quiz_description,
    "set": quiz_set,
    "number": quiz_number,
    "title": quiz_title,
    "shuffleQuestions": True,
    "allowAccess": [],  # {"startDate": quiz_time, "credit": 100}
    "zones": pl_zones,
    "comment": "You can add comments to JSON files using this property.",
}

assessment_folder = os.path.join(
    pl_repo, "courseInstances", course_instance, "assessments"
)
if not os.path.exists(assessment_folder):
    os.mkdir(assessment_folder)

assessment_folder = os.path.join(assessment_folder, assessment_name)
if not os.path.exists(assessment_folder):
    os.mkdir(assessment_folder)

with open(os.path.join(assessment_folder, "infoAssessment.json"), "w") as assessment:
    json.dump(pl_assessment, assessment, indent=4)
