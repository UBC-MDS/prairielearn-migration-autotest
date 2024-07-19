import json
import argparse
import html2text
from glob import glob
import os
from openai_utils import get_folder_name
import uuid


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", help="Directory where PrairieLearn repo is stored")
parser.add_argument(
    "--slug_file_path", default="", help="Directory where the slug is stored"
)
parser.add_argument(
    "--question_folder", default="QuestionBank", help="Questions will be added to"
)
parser.add_argument(
    "--model_type", default="gpt-3.5-turbo", help="gpt-4-0125-preview or gpt-3.5-turbo"
)
args = parser.parse_args()

h = html2text.HTML2Text()
question_root_folder = "{}/questions".format(args.pl_repo)
question_list = glob(
    "{}/{}/*".format(question_root_folder, args.question_folder), recursive=True
)
question_list.sort()

# check the file exists
if os.path.exists(args.slug_file_path):
    print(f"reading {args.slug_file_path}")
    with open(args.slug_file_path, "r") as f:
        name_mapping = f.read()
else:
    raise Exception(f"{args.slug_file_path} does not exists.")

print("processing {} questions".format(len(question_list)))
question_check_list = []
count = -1
unnamed_questions_count = 0
for question_folder in question_list:
    count += 1

    with open("{}/info.json".format(question_folder), "r") as f:
        question_info = json.load(f)
    with open("{}/question.html".format(question_folder), "r") as f:
        question_html = f.read()

    question_text = h.handle(question_html)
    question_text = (
        question_text.replace("\n", " ")
        .replace("  ", " ")
        .replace("  ", " ")
        .replace("  ", " ")
    )

    if len(question_text) > 5000:
        # if the question is too long. do not call the API to save cost
        print(
            f"Question too long. Use `others` for question {count}: {question_folder}"
        )
        # use others/unnamed_question_1, ...
        lecture_obj_slug = "others"
        question_slug = f"unnamed-question-{unnamed_questions_count}"
        question_title = f"Unnamed Question {unnamed_questions_count}"
        unnamed_questions_count += 1
    else:
        responses = get_folder_name(
            name_mapping, question_text, model_name=args.model_type
        )

        key_list = list(responses.keys())
        if "lec_slug" not in key_list:
            responses["lec_slug"] = "others"

        if "lo_slug" not in key_list:
            responses["lo_slug"] = "others"

        if "question_slug" not in key_list:
            responses["question_slug"] = f"unnamed-question-{unnamed_questions_count}"
            unnamed_questions_count += 1

        if "question_title" not in key_list:
            responses["question_title"] = "Unnamed question"

    # add suffix if the question folder already exists
    suffix = 0
    if os.path.exists(
        os.path.join(
            question_root_folder,
            responses["lec_slug"],
            responses["lo_slug"],
            responses["question_slug"],
        )
    ):
        new_question_slug = responses["question_slug"]
        while os.path.exists(
            os.path.join(
                question_root_folder,
                responses["lec_slug"],
                responses["lo_slug"],
                new_question_slug,
            )
        ):
            suffix += 1
            new_question_slug = f"{responses["question_slug"]}_{suffix}"
        responses["question_slug"] = new_question_slug

    # create question folder
    new_folder = question_root_folder
    for new_folder_extension in [responses["lec_slug"], responses["lo_slug"], responses["question_slug"]]:
        new_folder += "/{}".format(new_folder_extension)
        if os.path.exists(new_folder) is False:
            os.mkdir(new_folder)

    # write data
    question_info["uuid"] = str(uuid.uuid4())
    question_info["title"] = responses["question_title"]
    question_info["topic"] = responses["lec_slug"]
    question_info["tags"] = [responses["lo_slug"]]
    if (
        "gradingMethod" in question_info.keys()
        and question_info["gradingMethod"] == "Manual"
    ):
        question_info["tags"].append("manual")

    with open("{}/info.json".format(new_folder), "w") as f:
        json.dump(question_info, f, indent=2)

    with open("{}/question.html".format(new_folder), "w") as f:
        f.write(question_html)

    print("Copy Question {} from {} to {}.".format(count, question_folder, new_folder))

if len(question_check_list):
    print(
        "Some question are not correctly copied. Please check question_check_list.txt"
    )
    with open("question_check_list.txt", "w") as f:
        for q in question_check_list:
            f.write("{}\n".format(q))
