import json
import argparse
from bs4 import BeautifulSoup
import os
import yaml


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", default="pl-ubc-dsci523")
parser.add_argument("--question_folder")
parser.add_argument(
    "--question_type",
    default="coding",
)
parser.add_argument(
    "--initial_code_block",
    default="none",
)
parser.add_argument(
    "--language",
    default="python",
)
parser.add_argument(
    "--config_path",
    default="autotest/autotests.yml",
)
args = parser.parse_args()
assert args.question_type in ["coding", "mcq", "numeric"]
assert args.language in ["r", "python"]

print("loading template autotests.yml...")
with open(args.config_path, "r") as f:
    autotest_config_dict = yaml.safe_load(f)
autograder_info = autotest_config_dict[args.language]["pl"]

question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
with open("{}/info.json".format(question_folder), "r") as f:
    question_info = json.load(f)
with open("{}/question.html".format(question_folder), "r") as f:
    question_html = f.read()

# update tags in info.json
tag_list = question_info["tags"]
if "manual" in tag_list:
    tag_list.remove("manual")
if args.question_type not in tag_list:
    tag_list.append(args.question_type)
question_info["tags"] = tag_list

if args.question_type == "coding":
    # add external autograder
    question_info["gradingMethod"] = "External"
    question_info["externalGradingOptions"] = {
        "enabled": True,
        "image": autograder_info["image"],
        "entrypoint": autograder_info["entrypoint"],
        "timeout": 1,
    }

    # update question.html
    soup = BeautifulSoup(question_html)
    # extract code text to initial code
    code_text = ""
    if args.initial_code_block in ["code", "auto"]:
        code_blocks = soup.find_all("code")
        if len(code_blocks) > 0:
            code_text = code_blocks[-1].get_text(separator="\n", strip=True)
            code_blocks[-1].extract()
            # remove empty pre block
            pre_blocks = soup.find_all("pre")
            if len(pre_blocks) > 0 and pre_blocks[-1].text == "":
                pre_blocks[-1].extract()

    if args.initial_code_block in ["pre", "auto"]:
        code_blocks = soup.find_all("pre")
        if len(code_blocks) > 0:
            code_text = code_blocks[-1].get_text(separator="\n", strip=True)
            code_blocks[-1].extract()

    blocks_to_remove = soup.find_all("pl-rich-text-editor")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    blocks_to_remove = soup.find_all("pl-file-editor")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    blocks_to_remove = soup.find_all("pl-external-grader-results")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    # add code editor
    question_html = str(soup)
    file_editor_blocks = soup.find_all("pl-file-editor")
    if len(file_editor_blocks) == 0:
        question_html += '<pl-file-editor file-name="{}" ace-mode="{}" source-file-name="{}"></pl-file-editor>\n'.format(
            autograder_info["submission_file_name"],
            autograder_info["ace_mode"],
            autograder_info["source_file_name"],
        )
    results_blocks = soup.find_all("pl-external-grader-results")
    if len(results_blocks) == 0:
        question_html += "<pl-external-grader-results></pl-external-grader-results>"

    # create the initial code file
    source_file_name = "{}/{}".format(
        question_folder, autograder_info["source_file_name"]
    )
    if os.path.exists(source_file_name) is False:
        with open(source_file_name, "w") as f:
            f.write(code_text)
    else:
        print(f"{source_file_name} already exists")

    # creat test folders with a solution file
    test_folder = "{}/tests".format(question_folder)
    if os.path.exists(test_folder) is False:
        os.mkdir(test_folder)
    else:
        if os.path.exists("{}/ans.R".format(test_folder)):
            print("remove {}/ans.R".format(test_folder))
            os.remove("{}/ans.R".format(test_folder))

    solution_file_name = "{}/{}".format(
        test_folder, autograder_info["solution_file_name"]
    )
    if os.path.exists(solution_file_name) is False:
        with open(solution_file_name, "w") as f:
            f.write("")
    else:
        print(f"{solution_file_name} already exists")

elif args.question_type == "mcq":
    question_info.pop("gradingMethod", None)

    # update question.html
    # soup = BeautifulSoup(question_html)
    # text_editor_blocks = soup.find_all("pl-rich-text-editor")
    # for text_editor_block in text_editor_blocks:
    #     text_editor_block.extract()
    #
    # check_box_string = ""
    # check_box_string += '<pl-checkbox answers-name="select">\n'
    # check_box_string += '<pl-answer correct="true">  Eagle </pl-answer>\n'
    # check_box_string += '<pl-answer correct="false"> Tilapia </pl-answer>'
    # check_box_string += '<pl-answer correct="true">  Crow </pl-answer>'
    # check_box_string += '<pl-answer correct="false"> Crocodile </pl-answer>'
    # check_box_string += "</pl-checkbox>"

with open("{}/info.json".format(question_folder), "w") as f:
    json.dump(question_info, f, indent=2)

with open("{}/question.html".format(question_folder), "w") as f:
    f.write(question_html)

print("Done")
