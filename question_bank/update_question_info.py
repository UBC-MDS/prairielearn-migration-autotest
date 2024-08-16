import argparse
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

parser = argparse.ArgumentParser()
parser.add_argument("--pl_question_folder", default="pl-ubc-dsci523/questions")
args = parser.parse_args()


def find_folders_with_file(
    base_dir, target_file="question.html", contain_base_dir=True
):
    folders_with_file = []

    # Walk the directory tree
    for root, dirs, files in os.walk(base_dir):
        if target_file in files:
            if contain_base_dir:
                folders_with_file.append(root)
            else:
                folders_with_file.append(root.replace(base_dir + "/", ""))

    return folders_with_file


all_question_folders = find_folders_with_file(args.pl_question_folder)
if len(all_question_folders) == 0:
    logging.info("No question under {}".format(args.pl_question_folder))

print(all_question_folders)
for question_folder in all_question_folders:
    logging.info("update info.json")
    with open("{}/info.json".format(question_folder), "r") as f:
        question_info = json.load(f)

    slugs = question_folder.split("/")
    lecture_slug = [s.replace("lec_", "") for s in slugs if s.startswith("lec")]
    obj_slug = [s.replace("obj_", "") for s in slugs if s.startswith("obj")]

    if len(lecture_slug) == 1 and len(obj_slug) == 1:
        lecture_slug = lecture_slug[0]
        obj_slug = obj_slug[0]

        if obj_slug not in question_info["tags"]:
            question_info["tags"].append(obj_slug)
        if lecture_slug in question_info["tags"]:
            question_info["tags"].remove(lecture_slug)

        if question_info["topic"] != lecture_slug:
            question_info["topic"] = lecture_slug

        with open("{}/info.json".format(question_folder), "w") as f:
            json.dump(question_info, f, indent=2)
    elif "others" in slugs:
        if question_info["topic"] != "others":
            question_info["topic"] = "others"

        with open("{}/info.json".format(question_folder), "w") as f:
            json.dump(question_info, f, indent=2)
    else:
        logging.info(f"{question_folder}: Does not find lecture and obj slug")
