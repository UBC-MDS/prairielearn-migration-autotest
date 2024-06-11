import argparse
import yaml
from autograde_utils import (
    Template,
    find_autotest_variables,
    extract_lines_before_delimiter,
    extract_lines_after_delimiter,
)
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

parser = argparse.ArgumentParser()
parser.add_argument("--pl_question_folder", default="pl-ubc-dsci523/questions")
parser.add_argument("--config_path", default="autotests.yml")
args = parser.parse_args()


def find_folders_with_file(base_dir, target_file="question.html"):
    folders_with_file = []

    # Walk the directory tree
    for root, dirs, files in os.walk(base_dir):
        if target_file in files:
            folders_with_file.append(root)

    return folders_with_file


logging.info("loading template autotests.yml...")
with open(args.config_path, "r") as f:
    autotest_config_dict = yaml.safe_load(f)

all_question_folders = find_folders_with_file(args.pl_question_folder)
if len(all_question_folders) == 0:
    logging.info("No question under {}".format(args.pl_question_folder))

for question_folder in all_question_folders:
    # find the coding question is R or python
    if os.path.exists(
        "{}/tests/{}".format(
            question_folder, autotest_config_dict["r"]["pl"]["solution_file_name"]
        )
    ):
        code_language = "r"
    elif os.path.exists(
        "{}/tests/{}".format(
            question_folder, autotest_config_dict["python"]["pl"]["solution_file_name"]
        )
    ):
        code_language = "python"
    else:
        logging.info("{} does not have a solution file.".format(question_folder))
        continue

    logging.info(
        "############ {} is a {} coding question ############".format(
            question_folder, code_language
        )
    )
    autotest_config = autotest_config_dict[code_language]

    logging.info("update info.json to use the right autograder")
    with open("{}/info.json".format(question_folder), "r") as f:
        question_info = json.load(f)

    question_info["gradingMethod"] = "External"
    question_info["externalGradingOptions"] = {
        "enabled": True,
        "image": autotest_config["pl"]["image"],
        "entrypoint": autotest_config["pl"]["entrypoint"],
        "timeout": 30,
    }
    if autotest_config["pl"]["server_files"] != "":
        question_info["externalGradingOptions"]["serverFilesCourse"] = [
            autotest_config["pl"]["server_files"]
        ]

    with open("{}/info.json".format(question_folder), "w") as f:
        json.dump(question_info, f, indent=2)

    # find test folder and solution
    tests_folder = "{}/tests".format(question_folder)
    solution_path = "{}/{}".format(
        tests_folder, autotest_config["pl"]["solution_file_name"]
    )
    test_path = "{}/{}".format(tests_folder, autotest_config["pl"]["test_file_name"])

    # prefix_code = r""
    # postfix_code = r""
    # error_code = r""

    snippets, error_handling_snippets, prefix_code, postfix_code = (
        find_autotest_variables(
            solution_path,
            test_delimiter="# AUTOTEST ",
            error_delimiter="# EXPECT-ERROR ",
            prefix_delimiter="# SOLUTION",
            postfix_delimiter="# TESTSETUP",
        )
    )
    # postfix_code_lines = extract_lines_after_delimiter(
    #     solution_path, delimiter="# TESTSETUP "
    # )
    # snippets = find_autotest_variables(solution_path, delimiter="# AUTOTEST ")
    # error_handling_snippets = find_autotest_variables(
    #     solution_path, delimiter="# EXPECT-ERROR "
    # )
    # if len(postfix_code_lines) > 0:
    #     postfix_code += r"\n".join(postfix_code_lines)
    # if len(prefix_code_lines) > 0:
    #     prefix_code += r"\n".join(prefix_code_lines)

    logging.info("found snippets to test: [{}]".format(",".join(snippets)))
    if len(error_handling_snippets) > 0:
        logging.info(
            "found error_handling_snippets to test: [{}]".format(
                ",".join(error_handling_snippets)
            )
        )
    total_snippets = len(snippets) + len(error_handling_snippets)

    test_file = autotest_config["testfile_template"]
    test_count = 0

    for snippet in snippets:
        if code_language == "r":
            import rpy2.robjects as robjects

            # execute solution in R
            logging.info(f"executing {solution_path} to determine type...\n")
            current_wd = robjects.r("getwd()")[0]
            robjects.r("setwd('{}')".format(tests_folder))
            robjects.r["source"]("solution.R")
            dispatch_result = robjects.r(
                autotest_config["dispatch"].replace("{{snippet}}", snippet)
            )
            robjects.r("setwd('{}')".format(current_wd))

            if len(list(dispatch_result)) == 1:
                dispatch_result = dispatch_result[0]
            if "tbl" in list(dispatch_result):
                dispatch_result = "tbl"
            elif "data.frame" in list(dispatch_result):
                dispatch_result = "data.frame"
            elif dispatch_result not in autotest_config["test_expr_templates"].keys():
                dispatch_result = "default"
                logging.info("unknown data type. use default test template.")

            # add source template
            source_template = Template(autotest_config["source_template"])
            test_file += source_template.render(
                {
                    "solution_params": "",
                    "submission_params": "prefix_code='{}', postfix_code='{}'".format(
                        prefix_code, postfix_code
                    ),
                }
            )
            # add test case templates
            test_templates = autotest_config["test_expr_templates"][dispatch_result]
            for template in test_templates:
                test_expr_template = Template(template["test"])
                test_expr = test_expr_template.render({"snippet": snippet})

                test_case_template = Template(autotest_config["test_case_template"])
                test_file += test_case_template.render(
                    {
                        "score": template["point"] / total_snippets,
                        "test_expr": test_expr,
                    }
                )

        else:
            logging.info(
                f"executing {solution_path} to determine type...\n############"
            )
            # execute solution in python
            solution_env = {}
            with open(solution_path, "r", encoding="utf-8") as f:
                code_string = f.read()
            # run solution with postfix code
            # code_string += postfix_code
            current_wd = os.getcwd()
            os.chdir(tests_folder)
            exec(code_string, solution_env)
            os.chdir(current_wd)
            dispatch_template = Template(autotest_config["dispatch"])
            dispatch_result = eval(
                dispatch_template.render({"snippet": snippet}), solution_env
            )
            dispatch_result = dispatch_result.__name__
            print("############")

            if dispatch_result not in autotest_config["test_expr_templates"].keys():
                raise Exception(
                    f"Unknown data type {dispatch_result}. Need to update the check function."
                )

            test_templates = autotest_config["test_expr_templates"][dispatch_result]
            for template in test_templates:
                test_expr_template = Template(template["test"])
                test_expr = test_expr_template.render({"snippet": snippet})
                # variable_type_to_check = eval(test_expr, solution_env).__name__
                # check_list, check_tuple, check_scalar, check_numpy_array_features, check_numpy_array_sanity

                test_case_template = Template(autotest_config["test_case_template"])
                test_file += test_case_template.render(
                    {
                        "score": template["point"],
                        "count": test_count,
                        "check_fn": template["check_fn"],
                        "test_expr": test_expr,
                        "solution_params": "postfix_code='{}'".format(postfix_code),
                        "submission_params": "prefix_code='{}', postfix_code='{}'".format(
                            prefix_code, postfix_code
                        ),
                    }
                )
                test_count += 1

        for snippet in error_handling_snippets:
            if code_language == "r":
                error_case_template = Template(autotest_config["error_case_template"])
                test_file += error_case_template.render(
                    {"score": 1 / total_snippets, "snippet": snippet}
                )
            else:
                # TODO: error handling test for python
                raise NotImplementedError

    if total_snippets > 0:
        logging.info(f"added test file to {test_path}")
        with open(test_path, "w") as f:
            f.write(test_file)
