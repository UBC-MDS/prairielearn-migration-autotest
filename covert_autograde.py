import json
import argparse
import html2text
from bs4 import BeautifulSoup
import os

# from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", default="pl-ubc-dsci523")
parser.add_argument(
    "--question_folder",
    default="lec_tidy-eval/obj_data-masking/filter-select-planes",
)
parser.add_argument(
    "--question_type",
    default="coding",
)
parser.add_argument(
    "--initial_code_block",
    default="code",
)
args = parser.parse_args()
assert args.question_type in ["coding", "mcq", "numeric"]

question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
with open("{}/info.json".format(question_folder), "r") as f:
    question_info = json.load(f)
with open("{}/question.html".format(question_folder), "r") as f:
    question_html = f.read()

# h = html2text.HTML2Text()
# question_text = h.handle(question_html)

# update info.json
tag_list = question_info["tags"]
if "manual" in tag_list:
    tag_list.remove("manual")
if args.question_type not in tag_list:
    tag_list.append(args.question_type)

question_info["tags"] = tag_list

if args.question_type == "coding":
    question_info["gradingMethod"] = "External"
    question_info["externalGradingOptions"] = {
        "enabled": True,
        "image": "prairielearn/grader-r",
        "entrypoint": "r_autograder/run.sh",
        "timeout": 5,
    }

    # update question.html
    soup = BeautifulSoup(question_html)
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

    text_editor_blocks = soup.find_all("pl-rich-text-editor")
    for text_editor_block in text_editor_blocks:
        text_editor_block.extract()

    question_html = str(soup)
    file_editor_blocks = soup.find_all("pl-file-editor")
    if len(file_editor_blocks) == 0:
        question_html += '<pl-file-editor file-name="solution.R" ace-mode="ace/mode/r" source-file-name="initial_code.R"></pl-file-editor>'
        question_html += "<pl-external-grader-results></pl-external-grader-results>"

    with open("{}/initial_code.R".format(question_folder), "w") as f:
        f.write(code_text)

    test_folder = "{}/tests".format(question_folder)
    if os.path.exists(test_folder) is False:
        os.mkdir(test_folder)

    with open("{}/ans.R".format(test_folder), "w") as f:
        f.write("")

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
