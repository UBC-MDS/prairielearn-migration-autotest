# Prairielearn Tools for Migration \& Autotest

The repo contains scripts for the following tasks. 

## Migration from Canvas to PL
First create a `config.json` file with the following information:
```
{
    "access_token": "<your Canvas access key>",
    "course_id": {
        "<course_id>": [<quiz_id>, <quiz_id>]
    }
}
```

We can create a question bank by imporing the quizzes to a PL repo:
```
python create_quiz_bank.py --pl_repo <the folder containing the PL repo>
```
The questions will be added to `<pl_repo>/questions/QuestionBank/`.

## Organize questions 

## Convert questions to MCQ or coding 

## Generating test files for autograding in Prairielearn
