import argparse
import yaml
import os
import rpy2.robjects as robjects


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
args = parser.parse_args()

question_folder = "{}/questions/{}".format(args.pl_repo, args.question_folder)
tests_folder = "{}/tests".format(question_folder)
solution_path = "{}/solution.R".format(tests_folder)
test_path = "{}/test.R".format(tests_folder)

test_yaml_path = "tools/autotests.yml"


def find_autotest_variables(file_path, delimiter="AUTOTEST"):
    test_variables = []

    # Open the .R file and read its contents
    with open(file_path, "r") as file:
        # Read lines from the file
        lines = file.readlines()

        # Iterate through each line
        for line in lines:
            # Check if the delimiter is present in the line
            if delimiter in line:
                # Split the line by the space
                split_line = line.strip().split(" ")
                test_variables.extend(split_line[2:])

    if "" in test_variables:
        test_variables.remove("")

    if " " in test_variables:
        test_variables.remove(" ")

    return test_variables


print("loading solution.R...")
snippets = find_autotest_variables(solution_path)
print("found snippets to test:", snippets)

print("loading template autotests.yml...")
with open(test_yaml_path, "r") as f:
    autotest_config = yaml.safe_load(f)

print("writing test.R...")
test_file = ""
for snippet in snippets:
    # add setup code
    test_file += "{}\n\n".format(autotest_config["ir"]["setup"])

    # import both files
    if args.log_progress:
        test_file += "cat('[autotest] import submission.R')\n"
    test_file += (
        "student <- new.env()\nsource('/grade/student/submission.R', student)\n\n"
    )
    if args.log_progress:
        test_file += "cat('[autotest] import solution.R')\n"
    test_file += "solution <- new.env()\nsource('solution.R', solution)\n\n"

    # execute solution in R
    print("executing solution.R to determine type")
    current_wd = robjects.r("getwd()")[0]
    robjects.r("setwd('{}')".format(tests_folder))
    robjects.r["source"]("solution.R")
    dispatch_result = robjects.r(
        autotest_config["ir"]["dispatch"].replace("{{snippet}}", snippet)
    )
    if list(dispatch_result) == ["spec_tbl_df", "tbl_df", "tbl", "data.frame"]:
        dispatch_result = (
            "dataframe"  # should be called tibble. TODO: add a template tibble tbl
        )
    robjects.r("setwd('{}')".format(current_wd))
    #

    test_templates = autotest_config["ir"]["templates"][dispatch_result]
    for template in test_templates:
        test_code = template["test"].replace("{{snippet}}", snippet)
        test_point = template["point"]
        test_file += "## @title test {}\n## @score {}\n".format(test_code, test_point)
        if args.log_progress:
            test_file += "cat('[autotest] test {}')\n".format(test_code)
        test_file += "expect_equal(eval(parse(text = '{}'), envir = solution), eval(parse(text = '{}'), envir = student))\n\n".format(
            test_code, test_code
        )

with open(test_path, "w") as f:
    f.write(test_file)

print("done")
