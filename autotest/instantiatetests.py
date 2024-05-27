import argparse
import yaml
import rpy2.robjects as robjects
from autograde_utils import SimpleTemplate, find_autotest_variables


parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", default="pl-ubc-dsci523")
parser.add_argument(
    "--question_folder",
    default="lec_read-data/obj_read/read-grades",
)
parser.add_argument(
    "--config_path",
    default="autotests.yml",
)
parser.add_argument(
    "--language",
    default="r",
)
args = parser.parse_args()
# --pl_repo pl-ubc-dsci512 --question_folder lec_recursive-algo/obj_write-recursive/unravel-nested-lists --language python
assert args.language in ["r", "python"]

print("loading template autotests.yml...")
with open(args.config_path, "r") as f:
    autotest_config_dict = yaml.safe_load(f)
autotest_config = autotest_config_dict[args.language]

question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
tests_folder = "{}/tests".format(question_folder)
solution_path = "{}/{}".format(
    tests_folder, autotest_config["pl"]["solution_file_name"]
)
test_path = "{}/{}".format(tests_folder, autotest_config["pl"]["test_file_name"])

print("loading solution file...")
snippets = find_autotest_variables(solution_path, delimiter="# AUTOTEST ")
test_setups = find_autotest_variables(solution_path, delimiter="# TESTSETUP ")
if len(test_setups) > 0:
    additional_code_string = ";".join(test_setups)
else:
    additional_code_string = ""
print("found snippets to test:", snippets)

print("writing test file...")
test_file = autotest_config["setup"]
test_count = 0

for snippet in snippets:
    if args.language == "r":
        # execute solution in R
        print(f"executing {solution_path} to determine type...\n############")
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
        print(f"executing {solution_path} to determine type...\n############")
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

        test_templates = autotest_config["test_expr_templates"][dispatch_result]
        for template in test_templates:
            test_expr_template = SimpleTemplate(template["test"])
            test_expr = test_expr_template.render({"snippet": snippet})
            # variable_type_to_check = eval(test_expr, solution_env).__name__
            # check_list, check_tuple, check_scalar, check_numpy_array_features, check_numpy_array_sanity

            test_case_template = SimpleTemplate(autotest_config["test_case_template"])
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

print(f"wrote test file {test_path}")
with open(test_path, "w") as f:
    f.write(test_file)
