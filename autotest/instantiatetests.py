import argparse
import yaml
import rpy2.robjects as robjects
from src.autograde_utils import autograder_info_dict


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", default="pl-ubc-dsci523")
parser.add_argument(
    "--question_folder",
    default="lec_read-data/obj_read/read-grades",
)
parser.add_argument(
    "--log_progress",
    default=False,
)
parser.add_argument(
    "--language",
    default="r",
)
args = parser.parse_args()
# --pl_repo pl-ubc-dsci512 --question_folder lec_recursive-algo/obj_write-recursive/unravel-nested-lists --language python

assert args.language in ["r", "python"]
autograder_info = autograder_info_dict[args.language]

test_yaml_path = "tools/autotests.yml"
question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
tests_folder = "{}/tests".format(question_folder)
solution_path = "{}/{}".format(tests_folder, autograder_info["solution-file-name"])
test_path = "{}/{}".format(tests_folder, autograder_info["test-file-name"])


class SimpleTemplate:
    def __init__(self, template):
        self.template = template

    def render(self, context):
        result = self.template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result


def find_autotest_variables(file_path, delimiter="# AUTOTEST "):
    test_variables = []

    with open(file_path, "r") as file:
        lines = file.readlines()

        # Iterate through each line
        for line in lines:
            # Check if the delimiter is present in the line
            if delimiter in line:
                test_variable_string = line.strip().replace(delimiter, "")
                test_variables.extend(test_variable_string.split(";"))

    if "" in test_variables:
        test_variables.remove("")

    if " " in test_variables:
        test_variables.remove(" ")

    return test_variables


print("loading solution file...")
snippets = find_autotest_variables(solution_path)
print("found snippets to test:", snippets)

print("loading template autotests.yml...")
with open(test_yaml_path, "r") as f:
    autotest_config_dict = yaml.safe_load(f)
autotest_config = autotest_config_dict[args.language]


print("writing test file...")
test_file = autotest_config["setup"]
for snippet in snippets:
    if args.language == "r":
        # execute solution in R
        print("executing solution.R to determine type...\n############")
        current_wd = robjects.r("getwd()")[0]
        robjects.r("setwd('{}')".format(tests_folder))
        robjects.r["source"]("solution.R")
        dispatch_result = robjects.r(
            autotest_config["dispatch"].replace("{{snippet}}", snippet)
        )
        if list(dispatch_result) == ["spec_tbl_df", "tbl_df", "tbl", "data.frame"]:
            dispatch_result = "tbl"
        robjects.r("setwd('{}')".format(current_wd))
        print("############")

        # create test file
        test_templates = autotest_config["test_expr_templates"][dispatch_result]
        for template in test_templates:
            test_expr_template = SimpleTemplate(template["test"])
            test_expr = test_expr_template.render({"snippet": snippet})

            test_case_template = SimpleTemplate(autotest_config["test_case_template"])
            test_file += test_case_template.render(
                {"score": template["point"], "test_expr": test_expr}
            )

    else:
        # execute solution in python
        dispatch_result = "default"

        test_templates = autotest_config["test_expr_templates"][dispatch_result]
        test_count = 0
        for template in test_templates:
            test_expr_template = SimpleTemplate(template["test"])
            test_expr = test_expr_template.render({"snippet": snippet})

            test_case_template = SimpleTemplate(autotest_config["test_case_template"])
            test_file += test_case_template.render(
                {
                    "score": 1,
                    "count": test_count,
                    "check_fn": "check_list",
                    "test_expr": test_expr,
                }
            )
            test_count += 1

with open(test_path, "w") as f:
    f.write(test_file)

print(f"Add test file to {test_path}")
