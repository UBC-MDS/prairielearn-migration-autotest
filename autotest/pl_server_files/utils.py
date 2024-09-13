from code_feedback import Feedback
import unittest
import os
import json


class MyTestCase(unittest.TestCase):
    include_plt = False
    student_code_file = "user_code.py"
    iter_num = 0
    total_iters = 1
    ipynb_key = "#grade"

    @classmethod
    def setUpClass(self):
        Feedback.set_test(self)

        # Load data so that we can use it in the test cases
        filenames_dir = os.environ.get("FILENAMES_DIR")
        with open(os.path.join(filenames_dir, "data.json"), encoding="utf-8") as f:
            self.data = json.load(f)

    @classmethod
    def get_total_points(self):
        """
        Get the total number of points awarded by this test suite, including
        cases where the test suite is run multiple times.
        """
        methods = [
            y
            for x, y in self.__dict__.items()
            if callable(y)
            and hasattr(y, "__dict__")
            and x.startswith("test_")
            and "points" in y.__dict__
        ]
        if self.total_iters == 1:
            total = sum([m.__dict__["points"] for m in methods])
        else:
            once = sum(
                [
                    m.__dict__["points"]
                    for m in methods
                    if not m.__dict__.get("__repeated__", True)
                ]
            )
            several = sum(
                [
                    m.__dict__["points"]
                    for m in methods
                    if m.__dict__.get("__repeated__", True)
                ]
            )
            total = self.total_iters * several + once
        return total


class MyFeedback(Feedback):
    """
    Implement our own test functions
    """

    @classmethod
    def check_type(cls, name, ref, data, report_failure=True):
        def bad(msg):
            if report_failure:
                cls.add_feedback(msg)
            return False

        if not isinstance(data, type(ref)):
            bad(f"{name} does not have correct the type")

        return True

    def check_bool(cls, name, ref, data, report_failure=True):
        def bad(msg):
            if report_failure:
                cls.add_feedback(msg)
            return False

        if data is None:
            return bad("'%s' is None or not defined" % name)

        if not isinstance(data, bool):
            return bad("'%s' is not a bool" % name)

        if ref != data:
            bad(f"{name} is incorrect")

        return True

    def check_list(cls, name, ref, data, report_failure=True):
        def bad(msg):
            if report_failure:
                cls.add_feedback(msg)
            return False

        if data is None:
            return bad("'%s' is None or not defined" % name)

        if not isinstance(data, list):
            return bad("'%s' is not a list" % name)

        nref = len(ref)
        if len(data) != nref:
            return bad("{} should be of length {}".format(name, nref))

        good = True
        for i in range(nref):
            if type(data[i]) != type(ref[i]):  # noqa: E721
                good = False
                if report_failure:
                    cls.add_feedback(
                        "{}[{}] should be of type {}".format(
                            name, i, type(ref[i]).__name__
                        )
                    )
            elif data[i] != ref[i]:
                good = False

        if not good:
            return bad("'%s' is inaccurate" % name)

        return True


def source_ans(file_name="ans.py", prefix_code="", postfix_code=""):
    filenames_dir = os.environ.get("FILENAMES_DIR")
    return source(f"{filenames_dir}/{file_name}", prefix_code, postfix_code)


def source_student(file_name="user_code.py", prefix_code="", postfix_code=""):
    base_dir = os.environ.get("MERGE_DIR")
    return source(f"{base_dir}/{file_name}", prefix_code, postfix_code)


def source(file_name, prefix_code="", postfix_code=""):
    """
    a function similar to source in R
    """
    file_name_without_extension, extension = os.path.splitext(file_name)
    if extension == ".ipynb":
        ipynb_code_string = extract_ipynb_contents(file_name)
        code_string = prefix_code + "\n" + ipynb_code_string + "\n" + postfix_code
    else:
        code_string = read_code(file_name, prefix_code, postfix_code)
    global_dict = execute_python_code(code_string)
    return global_dict


def read_code(file_name, prefix_code="", postfix_code=""):
    assert isinstance(prefix_code, str)
    assert isinstance(postfix_code, str)
    with open(file_name, "r", encoding="utf-8") as f:
        code_string = f.read()
    combine_code_string = prefix_code + "\n" + code_string + "\n" + postfix_code
    return combine_code_string


def execute_python_code(code_string):
    """
    execute the code string and return the envir as a dictionary, which will be passed to eval()
    """
    global_dict = {}
    exec(code_string, global_dict)
    return global_dict


def extract_ipynb_contents(file_name):
    """
    Extract all cells from a ipynb notebook that start with a given
    delimiter
    """
    from IPython.core.interactiveshell import InteractiveShell
    from nbformat import read

    with open(file_name, "r", encoding="utf-8") as f:
        nb = read(f, 4)
        shell = InteractiveShell.instance()
        content = ""
        for cell in nb.cells:
            if cell["cell_type"] == "code":
                code = shell.input_transformer_manager.transform_cell(cell.source)
                # if code.strip().startswith(ipynb_key):
                content += code.strip()
    return content
