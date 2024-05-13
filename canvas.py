import argparse
from collections import OrderedDict
import requests, json, os


class ExtendAction(argparse.Action):
    """Add argparse action='extend' for pre-3.8 python"""

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


class Canvas:
    """Canvas"""

    def __init__(self, token=None, args=None):
        self.debug = args.debug if args else False
        with open(os.path.join(os.path.dirname(__file__), "config.json")) as config:
            self.config = json.load(config)
        self.token = self.config["access_token"]
        self.token_header = {"Authorization": f"Bearer {self.token}"}

        ###
        self.api_url = "https://canvas.ubc.ca/api/"
        self.url_prefix = "v1"
        self.new_url_prefix = "quiz/v1"
        ###

    @staticmethod
    def add_arguments(parser, course=True, quiz=False, assignment=False):
        """docstring"""

        parser.add_argument(
            "-d", "--debug", action="store_true", help="Enable debugging mode"
        )
        if course:
            parser.add_argument("-c", "--course", type=int, help="Course ID")
        if quiz:
            parser.add_argument("-q", "--quiz", type=int, help="Quiz ID")
        if assignment:
            parser.add_argument("-a", "--assignment", type=int, help="Assignment ID")

    def request(self, request, stop_at_first=False):
        """docstring"""
        retval = []
        response = requests.get(self.api_url + request, headers=self.token_header)
        while True:
            response.raise_for_status()
            if self.debug:
                print(response.text)
            retval.append(response.json())
            if (
                stop_at_first
                or "current" not in response.links
                or "last" not in response.links
                or response.links["current"]["url"] == response.links["last"]["url"]
            ):
                break
            response = requests.get(
                response.links["next"]["url"], headers=self.token_header
            )
        return retval

    def put(self, url, data):
        """docstring"""
        response = requests.put(
            self.api_url + url, json=data, headers=self.token_header
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def post(self, url, data):
        """docstring"""
        response = requests.post(
            self.api_url + url, json=data, headers=self.token_header
        )
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def delete(self, url):
        """docstring"""
        response = requests.delete(self.api_url + url, headers=self.token_header)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def course(self, course_id, prompt_if_needed=False):
        """docstring"""
        if course_id:
            for course in self.request(
                f"{self.url_prefix}/courses/{course_id}?include[]=term"
            ):
                return Course(self, course)
        return None

    def file(self, file_id):
        """docstring"""
        for file in self.request(f"/files/{file_id}"):
            return file


class Course(Canvas):
    """Course"""

    def __init__(self, canvas, course_data):
        super().__init__(canvas.token)
        self.data = course_data
        self.id = course_data["id"]
        self.course_url_prefix = f"{self.url_prefix}/courses/{self.id}"
        self.new_course_url_prefix = f"{self.new_url_prefix}/courses/{self.id}"

    def __getitem__(self, index):
        return self.data[index]

    def quiz(self, assignment_id):
        if assignment_id:
            try:
                for quiz in self.request(
                    f"{self.course_url_prefix}/quizzes/{assignment_id}"
                ):
                    return Quiz(self, quiz)
            except requests.exceptions.HTTPError:
                print("[Warning] Quiz not found. Try new course API.")
                return self.new_quiz(assignment_id)
        return None

    def new_quiz(self, assignment_id):
        if assignment_id:
            for quiz in self.request(
                f"{self.new_course_url_prefix}/quizzes/{assignment_id}"
            ):
                return NewQuiz(self, quiz)
        return None

    # def assignment(self, assignment_id):
    #     if assignment_id:
    #         for assignment in self.request(
    #             f"{self.course_url_prefix}/assignments/{assignment_id}"
    #         ):
    #             return Assignment(self, assignment)
    #     return None


class CourseSubObject(Canvas):

    # If not provided, the request_param_name defaults to the lower-cased class name.
    def __init__(
        self, parent, route_name, data, id_field="id", request_param_name=None
    ):
        # MUST be available before calling self.get_course.
        self.parent = parent
        super().__init__(self.get_course().token)

        self.data = data
        self.id_field = id_field
        self.id = self.compute_id()
        self.route_name = route_name
        if not request_param_name:
            request_param_name = type(self).__name__.lower()
        self.request_param_name = request_param_name
        self.object_url_prefix = self.compute_url_prefix()

    def get_course(self):
        if isinstance(self.parent, Course):
            return self.parent
        else:
            return self.parent.get_course()

    def compute_id(self):
        return self.data[self.id_field]

    def compute_url_prefix(self, new_quiz=False):
        if new_quiz:
            return f"{self.parent.new_course_url_prefix}/{self.route_name}/{self.id}"
        else:
            return f"{self.parent.course_url_prefix}/{self.route_name}/{self.id}"

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def items(self):
        """docstring"""
        return self.data.items()


class Quiz(CourseSubObject):
    """Quiz"""

    def __init__(self, course, quiz_data):
        super().__init__(course, "quizzes", quiz_data)

    def question_group(self, group_id):
        """docstring"""
        if group_id is None:
            return None
        for group in self.request(f"{self.object_url_prefix}/groups/{group_id}"):
            return group
        return None

    def questions(self, qfilter=None):
        """docstring"""
        questions = {}
        groups = {}
        i = 1
        for result in self.request(f"{self.object_url_prefix}/questions?per_page=100"):
            for question in result:
                if question["quiz_group_id"] in groups:
                    group = groups[question["quiz_group_id"]]
                else:
                    group = self.question_group(question["quiz_group_id"])
                    groups[question["quiz_group_id"]] = group

                if group:
                    question["points_possible"] = group["question_points"]
                    question["position"] = group["position"]
                else:
                    question["position"] = i
                    i += 1
                if not qfilter or qfilter(question["id"]):
                    questions[question["id"]] = question
        if None in groups:
            del groups[None]
        for grp in groups.values():
            for question in [
                q
                for q in questions.values()
                if q["position"] >= grp["position"] and q["quiz_group_id"] is None
            ]:
                question["position"] += 1
        return (
            OrderedDict(sorted(questions.items(), key=lambda t: t[1]["position"])),
            OrderedDict(sorted(groups.items(), key=lambda t: t[1]["position"])),
        )

    def has_time_limit(self):
        return self.data["time_limit"]


class NewQuiz(CourseSubObject):
    """Quiz"""

    def __init__(self, course, quiz_data):
        super().__init__(course, "quizzes", quiz_data)
        self.object_url_prefix = self.compute_url_prefix(new_quiz=True)

    def questions(self, qfilter=None):
        """docstring"""
        questions = {}
        groups = {}
        i = 1
        for result in self.request(f"{self.object_url_prefix}/items?per_page=100"):
            for question in result:
                new_question_dict = {}
                for key in ["id", "position", "points_possible"]:
                    new_question_dict[key] = question[key]

                new_question_dict["question_name"] = question["entry"]["title"]
                new_question_dict["question_text"] = question["entry"]["item_body"]
                new_question_dict["question_type"] = question["entry"][
                    "interaction_type_slug"
                ]
                new_question_dict["interaction_data"] = question["entry"][
                    "interaction_data"
                ]
                new_question_dict["answer_feedback"] = question["entry"][
                    "answer_feedback"
                ]
                questions[question["id"]] = new_question_dict

        return (
            OrderedDict(sorted(questions.items(), key=lambda t: t[1]["position"])),
            OrderedDict(sorted(groups.items(), key=lambda t: t[1]["position"])),
        )

    def has_time_limit(self):
        return self.data["quiz_settings"]["has_time_limit"]


# class QuizQuestion(CourseSubObject):
#     # If the quiz is not supplied, fetches it via quiz_question_data['quiz_id'].
#     def __init__(self, quiz_question_data, quiz=None):
#         if quiz is None:
#             if "quiz_id" not in quiz_question_data:
#                 raise RuntimeError(
#                     "No quiz provided and cannot find quiz id for: %s"
#                     % quiz_question_data
#                 )
#             quiz = course.quiz(quiz_question_data)
#         super().__init__(
#             quiz, "questions", quiz_question_data, request_param_name="question"
#         )
#
#     def update(self, data=None):
#         if data:
#             self.data = data
#
#         # Reformat question data to account for different format
#         # between input and output in Canvas API
#         if "answers" in self.data:
#             for answer in self.data["answers"]:
#                 if "html" in answer:
#                     answer["answer_html"] = answer["html"]
#                 if self.data["question_type"] == "matching_question":
#                     if "left" in answer:
#                         answer["answer_match_left"] = answer["left"]
#                     if "right" in answer:
#                         answer["answer_match_right"] = answer["right"]
#                 if self.data["question_type"] == "multiple_dropdowns_question":
#                     if "weight" in answer:
#                         answer["answer_weight"] = answer["weight"]
#                     if "text" in answer:
#                         answer["answer_text"] = answer["text"]
#
#         return super().update(self.data)
#
#     def update_question(self, data=None):
#         return self.update(data)


# class Assignment(CourseSubObject):
#     """Assignment"""
#
#     def __init__(self, course, assg_data):
#         super().__init__(course, "assignments", assg_data)
#
#     def update_assignment(self, data=None):
#         return self.update(data)
#
#     def rubric(self):
#         """docstring"""
#         for result in self.request(
#             f"{self.course.url_prefix}/rubrics/{self.data['rubric_settings']['id']}?include[]=associations"
#         ):
#             return result
#         return None
#
#     def update_rubric(self, rubric):
#         """docstring"""
#         rubric_data = {
#             "rubric": rubric,
#             "rubric_association": {
#                 "association_id": self.id,
#                 "association_type": "Assignment",
#                 "use_for_grading": True,
#                 "purpose": "grading",
#             },
#         }
#         self.post(f"{self.course.url_prefix}/rubrics", rubric_data)
#
#     def send_assig_grade(self, student, assessment):
#         """docstring"""
#         self.put(
#             f"{self.url_prefix}/submissions/{student['id']}",
#             {"rubric_assessment": assessment},
#         )


class Page(CourseSubObject):

    def __init__(self, course, page_data):
        super().__init__(
            course, "pages", page_data, id_field="url", request_param_name="wiki_page"
        )

    def update_page(self, data=None):
        return self.update(data)
