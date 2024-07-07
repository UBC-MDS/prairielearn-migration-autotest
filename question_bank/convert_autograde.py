import json
import argparse
from bs4 import BeautifulSoup
import os
import yaml


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "t"):
        return True
    elif v.lower() in ("false", "f"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo")
parser.add_argument("--question_folder")
parser.add_argument("--question_type", default="coding")
parser.add_argument("--initial_code_block", default="none")
parser.add_argument("--create_data_file", default=False, type=str2bool)
parser.add_argument("--create_server_file", default=False, type=str2bool)
parser.add_argument("--create_workspace", default=False, type=str2bool)
parser.add_argument("--mcq_block", default="none")
parser.add_argument("--mcq_partial_credict", default="false")
parser.add_argument("--language", default="python")
parser.add_argument("--config_path", default="autotest/autotests.yml")
args = parser.parse_args()
assert args.question_type in ["coding", "mcq", "numeric", "matching", "order-blocks"]
assert args.mcq_block in ["none", "checkbox", "multiple-choice"]
assert args.mcq_partial_credict in ["false", "COV", "EDC", "PC"]
assert args.language in ["r", "python"]

question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
with open("{}/info.json".format(question_folder), "r") as f:
    question_info = json.load(f)
with open("{}/question.html".format(question_folder), "r") as f:
    question_html = f.read()

# Situations that require a test folder to be created
test_conditions = [args.question_type == "coding", args.create_data_file == True]

# Create test folder if required
if any(test_conditions):
    # creat a test folder
    test_folder = "{}/tests".format(question_folder)
    if os.path.exists(test_folder) is False:
        os.mkdir(test_folder)
    else:
        # remove existing ans.R
        if os.path.exists("{}/ans.R".format(test_folder)):
            print("remove {}/ans.R".format(test_folder))
            os.remove("{}/ans.R".format(test_folder))

# Check for server_file
if args.create_server_file:
    # create a server file to read data.txt
    server_file_name = "{}/server.py".format(question_folder)
    if os.path.exists(server_file_name) is False:
        print(f"create {server_file_name}")
        with open(server_file_name, "w") as f:
            f.write(
                'import prairielearn as pl\nimport pandas as pd\n\n\ndef generate(data):\n    df = pd.read_csv("tests/data.txt")\n    data["params"]["df"] = pl.to_json(df.head(10))\n'
            )

# Check for data_file
if args.create_data_file:
    # create an empty data.txt. Note we need to add data manually
    data_file_name = "{}/data.txt".format(test_folder)
    if os.path.exists(data_file_name) is False:
        print(f"create {data_file_name}")
        with open(data_file_name, "w") as f:
            f.write("")

# update tags in info.json
tag_list = question_info["tags"]
if "manual" in tag_list:
    tag_list.remove("manual")
if args.question_type not in tag_list:
    tag_list.append(args.question_type)
if args.create_workspace:
    if "workspace" not in tag_list:
        tag_list.append("workspace")
question_info["tags"] = tag_list

# Remove manual grader unless needed
if args.question_type != "manual":
    question_info.pop("gradingMethod", None)

if args.question_type == "coding":
    print("loading template autotests.yml...")
    with open(args.config_path, "r") as f:
        autotest_config_dict = yaml.safe_load(f)
    autograder_info = autotest_config_dict[args.language]["pl"]

    # add external autograder
    question_info["gradingMethod"] = "External"
    question_info["externalGradingOptions"] = {
        "enabled": True,
        "image": autograder_info["image"],
        "entrypoint": autograder_info["entrypoint"],
        "timeout": 30,
    }
    if autograder_info["server_files"] != "":
        question_info["externalGradingOptions"]["serverFilesCourse"] = [
            autograder_info["server_files"]
        ]

    # add workspace to info.json
    if args.create_workspace:
        question_info["workspaceOptions"] = {
            "image": autograder_info["workspace_image"],
            "port": autograder_info["workspace_port"],
            "args": "",
            "rewriteUrl": False,
            "home": autograder_info["workspace_home"],
            "gradedFiles": [
                autograder_info["workspace_graded"]
            ]
        }

    # Check workspace files
    if args.create_workspace:
        workspace_folder = "{}/workspace".format(question_folder)
        if os.path.exists(workspace_folder) is False:
            os.mkdir(workspace_folder)
        if args.language == "r":
            r_profile_file_name = "{}/.Rprofile".format(workspace_folder)
            if os.path.exists(r_profile_file_name) is False:
                r_code = '''setHook("rstudio.sessionInit", function(newSession) {
  file.edit("submission.R")
}, action = "append")
'''
                print(f"create {r_profile_file_name}")
                with open(r_profile_file_name, "w") as f:
                    f.write(r_code)

    # update question.html
    soup = BeautifulSoup(question_html, features="html.parser")

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

    # remove text editor
    blocks_to_remove = soup.find_all("pl-rich-text-editor")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    # remove code editor
    blocks_to_remove = soup.find_all("pl-file-editor")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    # remove grader result
    blocks_to_remove = soup.find_all("pl-external-grader-results")
    for block_to_remove in blocks_to_remove:
        block_to_remove.extract()

    # add code editor and grader result or workspace
    question_html = str(soup)
    if not args.create_workspace:
        file_editor_blocks = soup.find_all("pl-file-editor")
        if len(file_editor_blocks) == 0:
            question_html += '<pl-file-editor file-name="{}" ace-mode="{}" source-file-name="{}"></pl-file-editor>\n'.format(
                autograder_info["submission_file_name"],
                autograder_info["ace_mode"],
                autograder_info["source_file_name"],
            )
    else:
        workspace_blocks = soup.find_all("pl-workspace")
        if len(workspace_blocks) == 0:
            question_html += '\n<pl-workspace></pl-workspace>\n'
        preview_blocks = soup.find_all("pl-workspace")
        if len(preview_blocks) == 0:
            question_html += '<pl-file-preview></pl-file-preview>\n'
        
    results_blocks = soup.find_all("pl-external-grader-results")
    if len(results_blocks) == 0:
        question_html += "<pl-external-grader-results></pl-external-grader-results>"

    # create the initial code file
    if args.create_workspace:
        source_file_name = "{}/{}".format(
            workspace_folder, autograder_info["submission_file_name"]
        )
    else:
        source_file_name = "{}/{}".format(
            question_folder, autograder_info["source_file_name"]
        )
    
    if os.path.exists(source_file_name) is False:
        with open(source_file_name, "w") as f:
            f.write(code_text)
    else:
        print(f"{source_file_name} already exists")

    # creat a solution file in the test folder
    solution_file_name = "{}/{}".format(
        test_folder, autograder_info["solution_file_name"]
    )
    if os.path.exists(solution_file_name) is False:
        with open(solution_file_name, "w") as f:
            f.write("")
    else:
        print(f"{solution_file_name} already exists")

elif args.question_type == "mcq":
    # remove pl-rich-text-editor
    soup = BeautifulSoup(question_html)
    text_editor_blocks = soup.find_all("pl-rich-text-editor")
    for text_editor_block in text_editor_blocks:
        print("remove pl-rich-text-editor")
        text_editor_block.extract()
    question_html = str(soup)

    if args.mcq_block != "none":
        checkbox_blocks = soup.find_all("pl-checkbox")
        mc_blocks = soup.find_all("pl-multiple-choice")
        if len(checkbox_blocks) == 0 and len(mc_blocks) == 0:
            print(
                f"No pl-checkbox and pl-multiple-choice. Add a template for pl-{args.mcq_block}."
            )
            if (
                args.mcq_block == "multiple-choice"
                or args.mcq_partial_credict == "false"
            ):
                question_html += f'\n<pl-{args.mcq_block} answers-name="answer">\n'
            else:
                question_html += f'\n<pl-checkbox answers-name="answer" partial-credit="true" partial-credit-method="{args.mcq_partial_credict}">\n'
            question_html += '<pl-answer correct="true"> True statement </pl-answer>\n'
            question_html += (
                '<pl-answer correct="false"> False statement </pl-answer>\n'
            )
            question_html += f"</pl-{args.mcq_block}>"
        else:
            if len(checkbox_blocks) > 0:
                print(
                    f"update pl-{args.mcq_block} with partial-credit={args.mcq_partial_credict}"
                )
                for checkbox_block in checkbox_blocks:
                    if args.mcq_partial_credict == "false":
                        del checkbox_block["partial-credit"]
                        del checkbox_block["partial-credit-method"]
                    else:
                        checkbox_block["partial-credit"] = "true"
                        checkbox_block["partial-credit-method"] = (
                            args.mcq_partial_credict
                        )
            if len(mc_blocks) > 0:
                for checkbox_block in mc_blocks:
                    if args.mcq_partial_credict == "false":
                        del checkbox_block["partial-credit"]
                        del checkbox_block["partial-credit-method"]
                    else:
                        checkbox_block["partial-credit"] = "true"
                        checkbox_block["partial-credit-method"] = (
                            args.mcq_partial_credict
                        )
            question_html = str(soup)

with open("{}/info.json".format(question_folder), "w") as f:
    json.dump(question_info, f, indent=2)

# run BeautifulSoup again to convert the question_html string to an HTML file
soup = BeautifulSoup(question_html, features="html.parser")
question_html = str(soup)
with open("{}/question.html".format(question_folder), "w") as f:
    f.write(question_html)

# check if question_type exists in infoCourse.json
course_json = "{}/infoCourse.json".format(args.pl_repo)
if os.path.exists(course_json):
    with open(course_json, "r") as f:
        course_info = json.load(f)
    current_question_types = [tag["name"] for tag in course_info["tags"]]
    if args.question_type not in current_question_types:
        print(
            f"question_type '{args.question_type}' is not in '{course_json}' - you may need to create it manually"
        )
else:
    print(
        f"Could not find '{course_json}' - if this is where it belongs, please make sure to create it"
    )
