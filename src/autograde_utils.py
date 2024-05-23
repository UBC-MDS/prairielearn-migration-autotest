autograder_info_dict = {
    "python": {
        "image": "prairielearn/grader-python",
        "entrypoint": "/python_autograder/run.sh",
        "file-name": "user_code.py",
        "ace-mode": "ace/mode/python",
        "source-file-name": "initial_code.py",
        "solution-file-name": "ans.py",
        "test-file-name": "test.py",
    },
    "r": {
        "image": "prairielearn/grader-r",
        "entrypoint": "r_autograder/run.sh",
        "file-name": "submission.R",
        "ace-mode": "ace/mode/r",
        "source-file-name": "initial_code.R",
        "solution-file-name": "solution.R",
        "test-file-name": "test.R",
    },
}
