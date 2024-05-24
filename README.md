# Prairielearn Tools for Migration \& Question Bank \& Autotest

This repository is a collection of scripts and instructions for migrating questions from Canvas to Prairielearn

## 1. Set up 

> Only do this the very first time you start working on this project

```
virtualenv --no-download .env
source .env/bin/activate
pip install --upgrade pip 
pip install -r requirements.txt
```

## 2. Migration from Canvas to PL

> Run this whenever you need to pull questions from Canvas

### 2.1. Migration Process

- Make sure you are inside this repository first and run `source .env/bin/activate` 

#### 2.1.1. Create the configuration file

 Create a `config.json` file in the following format:
```
{
    "access_token": "<your Canvas access key>",
    "course_id": {
        "<course_id>": [<quiz_id>]
    }
}
```
- You can find the course_id and quiz_id from the url, for example, `canvas.ubc.ca/courses/<course ID>/quizzes/<Quiz ID>`.
- Follow step one of [these instructions](https://learninganalytics.ubc.ca/guides/get-started-with-the-canvas-api/) to get your Canvas access key

Here is an example `config.json` for a single course and quiz

```
{
    "access_token": "supersecretkey",
    "course_id": {
        "123456": [123123]
    }
}
```

You can add multiple courses and quizzes by extending the JSON file like so:

```
{
    "access_token": "<your Canvas access key>",
    "course_id": {
        "<123456>": [123123, 456456, ...],
        "<789012>": [456456, 789789, ...]
    }
}
```
#### 2.1.2. Create the question bank

We can create a question bank by importing the quizzes to a PL repo:
```
python create_quiz_bank.py --pl_repo <the folder containing the PL repo> --config_file config.json
```
The questions will be added to `<pl_repo>/questions/QuestionBank/`.

## 3. Organize a question bank

> Do this until all questions from all quizzes are complete from a desired course

### 3.1. Labelling each question with a learning objective
- You will require an OpenAI API access key for this step. Follow [these instructions](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key) to set up your API key. 
- This step assumes you have already created a question bank

#### 3.1.1. Create the learning objectives file

> Repeat this step for each course

- The learning objective file is called the `slug.txt` file

The script generates a slug for each course containing the lecture and learning objective:
- Make sure the file path is within the same folder as the learning objective file (i.e. in the course repository)
```
python create_lo_slug.py --lo_file_path <lo_file_path>
```
Spend some time reviewing the `slug.txt` file and modify the learning objectives to fix any mistakes made by ChatGPT (it is faster to do this now than later).

Then run the script to label each question with the corresponding lecture and learning objective slug: 
```
python organize_questions.py --pl_repo <pl_repo> --lo_file_path <slug_path>
```

### 3.2. Convert questions to MCQ or coding questions

- Each question will require different edits depending on the accuracy of ChatGPT and the style of question
- Make sure to check the question type and only follow the steps relevant to that question

#### 3.2.1. Manual Review

> Repeat this step for every question in a course

This step requires manually checking each question
- If the question was not aligned with the lecture and learning objective, move the question to the correct folder manually.
- We might want to change a manually-graded question to a coding question or a MCQ question. To do so, run the script
```
python covert_autograde.py --pl_repo <pl_repo> --question_folder <question_folder> --question_type <coding or mcq> --initial_code_block <> --language <python or r>
```
If `question_type=='coding'`, the script will find the code in initial_code_block and move it to a new file called `initial_code.R` or `initial_code.py`, and create files needed for autograding. 
If `question_type=='mcq'`, you will need to automatically update the question. 

## 4. Generating test files for coding questions

> Note: Multiple choice questions should already be complete at this stage