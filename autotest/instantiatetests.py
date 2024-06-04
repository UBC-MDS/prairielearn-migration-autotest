import argparse
import yaml
import rpy2.robjects as robjects
from autograde_utils import SimpleTemplate, find_autotest_variables
import os


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


print("[INFO] loading template autotests.yml...")
with open(args.config_path, "r") as f:
    autotest_config_dict = yaml.safe_load(f)


all_question_folders = find_folders_with_file(args.pl_question_folder)
if len(all_question_folders) == 0:
    print("[INFO] No question under {}".format(args.pl_question_folder))

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
        print("[INFO] {} does not have a solution file.".format(question_folder))
        continue

    print("[INFO] {} is a {} coding question.".format(question_folder, code_language))
    autotest_config = autotest_config_dict[code_language]

    # find test folder and solution
    tests_folder = "{}/tests".format(question_folder)
    solution_path = "{}/{}".format(
        tests_folder, autotest_config["pl"]["solution_file_name"]
    )
    test_path = "{}/{}".format(tests_folder, autotest_config["pl"]["test_file_name"])

    snippets = find_autotest_variables(solution_path, delimiter="# AUTOTEST ")
    test_setups = find_autotest_variables(solution_path, delimiter="# TESTSETUP ")
    if len(test_setups) > 0:
        additional_code_string = ";".join(test_setups)
    else:
        additional_code_string = ""
    print("[INFO] found snippets to test:", snippets)

    test_file = autotest_config["setup"]
    test_count = 0

    for snippet in snippets:
        if code_language == "r":
            # execute solution in R
            print(
                f"[INFO] executing {solution_path} to determine type...\n############"
            )
            current_wd = robjects.r("getwd()")[0]
            robjects.r("setwd('{}')".format(tests_folder))
            robjects.r["source"]("solution.R")
            dispatch_result = robjects.r(
                autotest_config["dispatch"].replace("{{snippet}}", snippet)
            )
            robjects.r("setwd('{}')".format(current_wd))
            print("############")

            if len(list(dispatch_result)) == 1:
                dispatch_result = dispatch_result[0]
            if "tbl" in list(dispatch_result):
                dispatch_result = "tbl"
            elif "data.frame" in list(dispatch_result):
                dispatch_result = "data.frame"
            if dispatch_result not in autotest_config["test_expr_templates"].keys():
                dispatch_result = "default"
                print("unknown data type. use default test template.")

            # create test file
            test_templates = autotest_config["test_expr_templates"][dispatch_result]
            for template in test_templates:
                test_expr_template = SimpleTemplate(template["test"])
                test_expr = test_expr_template.render({"snippet": snippet})

                test_case_template = SimpleTemplate(
                    autotest_config["test_case_template"]
                )
                test_file += test_case_template.render(
                    {"score": template["point"], "test_expr": test_expr}
                )

        else:
            print(
                f"[INFO] executing {solution_path} to determine type...\n############"
            )
            solution_env = {}
            with open(solution_path, "r", encoding="utf-8") as f:
                code_string = f.read()
            code_string += additional_code_string
            exec(code_string, solution_env)
            dispatch_template = SimpleTemplate(autotest_config["dispatch"])
            dispatch_result = eval(
                dispatch_template.render({"snippet": snippet}), solution_env
            )
            dispatch_result = dispatch_result.__name__
            print("############")

            if dispatch_result not in autotest_config["test_expr_templates"].keys():
                dispatch_result = "default"
                print("unknown data type. use default test template.")
            test_templates = autotest_config["test_expr_templates"][dispatch_result]
            for template in test_templates:
                test_expr_template = SimpleTemplate(template["test"])
                test_expr = test_expr_template.render({"snippet": snippet})
                # variable_type_to_check = eval(test_expr, solution_env).__name__
                # check_list, check_tuple, check_scalar, check_numpy_array_features, check_numpy_array_sanity

                test_case_template = SimpleTemplate(
                    autotest_config["test_case_template"]
                )
                test_file += test_case_template.render(
                    {
                        "score": 1,
                        "count": test_count,
                        "check_fn": "check_{}".format(dispatch_result),
                        "test_expr": test_expr,
                        "source_params": 'additional_code_string="{}"'.format(
                            additional_code_string
                        ),
                    }
                )
                test_count += 1

    if len(snippets) > 0:
        print(f"[INFO] added test file to {test_path}")
        with open(test_path, "w") as f:
            f.write(test_file)
