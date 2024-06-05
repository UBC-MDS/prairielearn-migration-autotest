import logging


class Template:
    def __init__(self, template):
        self.template = template

    def render(self, context):
        result = self.template
        placeholders = self._find_placeholders()

        for placeholder in placeholders:
            var_name = placeholder.strip("{}")
            value = context.get(var_name, "")
            result = result.replace(placeholder, str(value))

        return result

    def _find_placeholders(self):
        import re

        return re.findall(r"{{\s*[\w]+\s*}}", self.template)


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


def extract_lines_before_delimiter(file_path, delimiter="# SOLUTION"):
    find_delimiter = False
    lines_before_solution = []
    with open(file_path, "r") as file:
        for line in file:
            # Check if the line contains the marker
            if line.strip() == delimiter:
                find_delimiter = True
                break
            # Append the line to the list of lines before the marker
            lines_before_solution.append(line.rstrip("\n"))
    if find_delimiter is False:
        logging.info(f"no {delimiter} lines found")
        return []
    return lines_before_solution
