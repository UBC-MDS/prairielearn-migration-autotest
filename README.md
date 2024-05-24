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
        "<course_id1>": [<quiz_id1>, <quiz_id2>, ...],
        "<course_id2>": [<quiz_id1>, <quiz_id2>, ...]
    }
}
```
You can find the course_id and quiz_id from the url, for example, `canvas.ubc.ca/courses/<course ID>/quizzes/<Quiz ID>`.

We can create a question bank by importing the quizzes to a PL repo:
```
python create_quiz_bank.py --pl_repo <the folder containing the PL repo> --config_file config.json
```
The questions will be added to `<pl_repo>/questions/QuestionBank/`.

## Organize a question bank

### Labelling each question with a learning objective
This step requires OpenAI API access key. Follow the [instruction](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)) to set up your API key. 

The script generates slug for each lecture and learning objective:
```
python create_lo_slug.py --lo_file_path <lo_file_path>
```

Then run the script to label each question with the corresponding lecture and learning objective slug: 
```
python organize_questions.py --pl_repo <pl_repo> --lo_file_path <slug_path>
```

### Convert questions to MCQ or coding questions
This step requires manually checking each question
- If the question was not aligned with the lecture and learning objective, move the question to the correct folder manually.
- We might want to change a manually-graded question to a coding question or a MCQ question. To do so, run the script
```
python covert_autograde.py --pl_repo <pl_repo> --question_folder <question_folder> --question_type <coding or mcq> --initial_code_block <> --language <python or r>
```
If `question_type=='coding'`, the script will find the code in initial_code_block and move it to a new file called `initial_code.R` or `initial_code.py`, and create files needed for autograding. 
If `question_type=='mcq'`, you will need to automatically update the question. 

## Generating test files for coding questions
