class SimpleTemplate:
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
