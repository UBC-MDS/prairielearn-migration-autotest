# Prairielearn Tools for Migration \& Autotest

The repo contains scripts for the following tasks. 

## Set up 
```
virtualenv --no-download .env
source .env/bin/activate
pip install --upgrade pip 
pip install -r requirements.txt
```

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
You can find the course_id and quiz_id from the url, for example, `canvas.ubc.ca/courses/<course ID>/quizzes/<Quiz ID>`.

We can create a question bank by importing the quizzes to a PL repo:
```
python create_quiz_bank.py --pl_repo <the folder containing the PL repo>
```
The questions will be added to `<pl_repo>/questions/QuestionBank/`.

## Organize questions 
This step requires OpenAI API access key. 


## Convert questions to MCQ or coding 

## Generating test files for autograding in Prairielearn
