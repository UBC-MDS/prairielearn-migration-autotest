import json
import argparse
import html2text
from glob import glob
import os
from src.openai_call import get_folder_name


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", help="Directory where PrairieLearn repo is stored")
parser.add_argument(
    "--question_folder", default="QuestionBank", help="Questions will be added to"
)
parser.add_argument(
    "--lo_file_path", help="Directory where the learning objective is stored"
)
args = parser.parse_args()
print(args)

h = html2text.HTML2Text()

question_root_folder = "{}/questions".format(args.pl_repo)
question_list = glob(
    "{}/{}/*".format(question_root_folder, args.question_folder), recursive=True
)
question_list.sort()

# TODO: check the file exists
with open(args.lo_file_path, "r") as f:
    name_mapping = f.read()

print("processing {} questions".format(len(question_list)))
question_check_list = []
count = -1
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

    if len(question_text) > 2000:
        # if the question is too long. do not call the API to save cost
        print(f"skip the question {count}: {question_folder}")
        question_check_list.append(question_folder)
        continue

    respond = get_folder_name(name_mapping, question_text, model_name="gpt-3.5-turbo")
    respond = respond.replace(".", "")
    outputs = respond.split("\n")
    if len(outputs) != 3:
        print(f"check this question {count}: {question_folder}")
        question_check_list.append(question_folder)
        continue

    lecture_obj_slug = outputs[0]
    question_slug = outputs[1]
    question_title = outputs[2]

    suffix = 0
    if os.path.exists(
        os.path.join(question_root_folder, lecture_obj_slug, question_slug)
    ):
        new_question_slug = question_slug
        while os.path.exists(
            os.path.join(question_root_folder, lecture_obj_slug, new_question_slug)
        ):
            suffix += 1
            new_question_slug = f"{question_slug}_{suffix}"
        question_slug = new_question_slug

    if len(lecture_obj_slug.split("/")) == 1:
        lecture_slug = lecture_obj_slug
        obj_slug = lecture_obj_slug
        new_folder_extension_list = [lecture_obj_slug, question_slug]

    elif len(lecture_obj_slug.split("/")) == 2:
        lecture_slug, obj_slug = lecture_obj_slug.split("/")
        new_folder_extension_list = [lecture_slug, obj_slug, question_slug]

    else:
        print(f"check this question {count}: {question_folder}")
        question_check_list.append(question_folder)
        continue

    new_folder = question_root_folder
    for new_folder_extension in new_folder_extension_list:
        new_folder += "/{}".format(new_folder_extension)
        if os.path.exists(new_folder) is False:
            os.mkdir(new_folder)

    # write data
    question_info["title"] = question_title
    question_info["topic"] = lecture_slug.split("_")[-1]
    question_info["tags"] = [obj_slug.split("_")[-1]]
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
