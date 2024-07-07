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


def remove_empty_from_list(input_list):
    if "" in input_list:
        input_list.remove("")

    if " " in input_list:
        input_list.remove(" ")

    return input_list


def find_autotest_variables(
    file_path,
    test_delimiter="# AUTOTEST ",
    error_delimiter="# EXPECT-ERROR ",
    dispatch_delimiter="# DISPATCH ",
    prefix_delimiter="# SOLUTION",
    postfix_delimiter="# TESTSETUP",
):
    test_variables = []
    error_variables = []
    dispatch_variables = []
    lines_before_prefix_delimiter = []
    lines_after_postfix_delimiter = []

    find_prefix_delimiter = False
    find_postfix_delimiter = False

    with open(file_path, "r") as file:
        lines = file.readlines()

        for line in lines:
            if prefix_delimiter in line:
                assert (
                    find_postfix_delimiter is False
                ), "prefix should be found before postfix"
                find_prefix_delimiter = True
                assert line.strip() == prefix_delimiter
                continue

            if postfix_delimiter in line:
                find_postfix_delimiter = True
                assert line.strip() == postfix_delimiter
                continue

            if test_delimiter in line:
                test_variables.extend(
                    line.strip().replace(test_delimiter, "").split(";")
                )

            elif error_delimiter in line:
                error_variables.extend(
                    line.strip().replace(error_delimiter, "").split(";")
                )

            elif dispatch_delimiter in line:
                dispatch_variables.extend(
                    line.strip().replace(dispatch_delimiter, "").split(";")
                )

            else:
                # Append the line to the list of lines before the marker
                if find_prefix_delimiter is False:
                    lines_before_prefix_delimiter.append(line.rstrip("\n"))

                if find_postfix_delimiter is True:
                    lines_after_postfix_delimiter.append(line.rstrip("\n"))

    test_variables = remove_empty_from_list(test_variables)
    error_variables = remove_empty_from_list(error_variables)
    dispatch_variables = remove_empty_from_list(dispatch_variables)
    if len(dispatch_variables) != 0:
        assert len(test_variables) == len(
            dispatch_variables
        ), "Dispatch variables should have the same length as test variables"
    elif len(dispatch_variables) == 0:
        dispatch_variables = None

    lines_before_prefix_delimiter = remove_empty_from_list(
        lines_before_prefix_delimiter
    )
    lines_after_postfix_delimiter = remove_empty_from_list(
        lines_after_postfix_delimiter
    )

    if find_prefix_delimiter is False:
        logging.info(f"no prefix delimiter ({find_prefix_delimiter}) found")
        lines_before_prefix_delimiter = []

    prefix_code = r""
    postfix_code = r""
    prefix_code += r"\n".join(lines_before_prefix_delimiter)
    postfix_code += r"\n".join(lines_after_postfix_delimiter)

    return (
        test_variables,
        error_variables,
        dispatch_variables,
        prefix_code,
        postfix_code,
    )


def extract_lines_before_delimiter(file_path, delimiter="# SOLUTION"):
    find_delimiter = False
    lines_before_delimiter = []
    with open(file_path, "r") as file:
        for line in file:
            # Check if the line contains the marker
            if delimiter in line:
                find_delimiter = True
                break
            # Append the line to the list of lines before the marker
            lines_before_delimiter.append(line.rstrip("\n"))

    if "" in lines_before_delimiter:
        lines_before_delimiter.remove("")

    if " " in lines_before_delimiter:
        lines_before_delimiter.remove(" ")

    if find_delimiter is False:
        logging.info(f"no {delimiter} lines found")
        return []
    return lines_before_delimiter


def extract_lines_after_delimiter(file_path, delimiter="# TESTSETUP"):
    find_delimiter = False
    lines_after_delimiter = []
    with open(file_path, "r") as file:
        for line in file:
            # Check if the line contains the marker
            if delimiter in line:
                find_delimiter = True
                lines_after_delimiter.extend(
                    line.strip().replace(delimiter, "").split(";")
                )
                continue

            if find_delimiter:
                # Append the line to the list of lines before the marker
                lines_after_delimiter.append(line.rstrip("\n"))

    if "" in lines_after_delimiter:
        lines_after_delimiter.remove("")

    if " " in lines_after_delimiter:
        lines_after_delimiter.remove(" ")

    if find_delimiter is False:
        logging.info(f"no {delimiter} lines found")
        return []
    return lines_after_delimiter
