# Prairielearn Tools for Migration \& Question Bank \& Autotest

This repository is a collection of scripts and instructions for migrating questions from Canvas to Prairielearn

- These instructions assume an understanding of `Python`, `git` and `command line` usage

## 1. Set up 

> Only do this the very first time you start working on this project

- This step assumes you have already cloned this repository to your local machine

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
    "access_token": "supersecretkey",
    "course_id": {
        "<123456>": [123123, 456456, ...],
        "<789012>": [456456, 789789, ...]
    }
}
```
#### 2.1.2. Create the question bank

> Requires the directory file structure from GitHub Repository

We can create a question bank by importing the quizzes to a PL repo:
```
python migration/create_quiz_bank.py --pl_repo <the folder containing the PL repo> --config_file config.json
```
The questions will be added to `<pl_repo>/questions/QuestionBank/`.

## 3. Organize a question bank

> Do this until all questions from all quizzes are complete from a desired course

### 3.1. Labelling each question with a learning objective
- You will require an OpenAI API access key for this step. Follow [these instructions](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key) to set up your API key. 
- This step assumes you have already created a question bank

#### 3.1.1. Create the learning objectives file

> Repeat this step for each course

- First find the learning objective of the course you are working on. Ask the instructor to review the learning objective first.

The script generates a slug for each course containing the lecture and learning objective:
- Make sure the file path is within the same folder as the learning objective file (i.e. in the course repository)
```
python question_bank/create_lo_slug.py --lo_file_path <lo_file_path>
```
where `<lo_file_path>` is the path to the learning objective file, and the script will generate another file called `slug.txt`. 

Spend some time reviewing the `slug.txt` file and modify the learning objectives to fix any mistakes made by ChatGPT (it is faster to do this now than later).

Then run the script to label each question with the corresponding lecture and learning objective slug: 
```
python question_bank/organize_questions.py --pl_repo <pl_repo> --lo_file_path <slug_path>
```

### 3.2. Convert questions to MCQ or coding questions

> Repeat all of **3.2.** section for every question in a course

- Each question will require different edits depending on the accuracy of ChatGPT and the style of question
- Make sure to check the question type and only follow the steps relevant to that question

#### 3.2.1. Verify ChatGPT Output

> Folders can be moved at any point if required

Sometimes ChatGPT may make a mistake, for example when a question is a learning objective for multiple courses

- Compare the question with the `slug.txt` to make sure the question is in the right lecture (i.e. folder)
- If the question was not aligned with the lecture and learning objective, move the question to the correct folder manually.

#### 3.2.2. Determine the Question Parameters

> This is to identify the question and provide the information to relevant scripts



At this stage, every question is labelled as *manually* graded in the `config.json` file

- We might want to change a manually-graded question to another type (e.g. *coding* or *MCQ*)
- We need to make note of the `question_type`, the `initial_code_block`, and the programming `language` used

[//]: <> (# Create white space in the markdown)

- Open `<question_folder>/question.html` and find the HTML tag that corresponds to the `initial_code_block` (pre, code or auto if unknown)
   - Typically `pre` or `code`
   - Can leave as `auto` if unsure but may have undesired results
- Choose the correct `question_type`
   - Typically `mcq` or `coding`
- Identify the language
   - Either `r` or `python`
   - `SQL` is not covered here


#### 3.2.3. Create Solutions

> This will require an understanding of the course content
>> You will need to do one of the following, make the solution yourself, ask ChatGPT, or consult the professor

- The `convert_autograde` script has the following optional parameters that can be applied to each question type
   - `--create_data_file True` - this will create an empty `data.txt` file
   - `--create_server_file True` - this will create an empty `server.py` file

##### Example

> Add this to the `server.py` file
>
> ````
>def generate(data):
>  df = pd.read_csv("tests/data.txt")
>  data["params"]["df"] = pl.to_json(df.head(10))
>````
>
> Replace the data in the `question.html` file with this
>
> ````
><pl-dataframe params-name="df" show-index="false" show-dimensions="false" digits="4" display-language="r" show-python="false" show-dtype="true"></pl-dataframe>
>````

- If the data contain `NA`, then you will need to add `keep_default_na=False` in `pd.read_csv()` to avoid getting errors. 

Skip ahead to the section that is relevant for your question type

##### MCQ

> This is for questions that could have multiple solutions, i.e. not TRUE/FALSE or numeric options
>> This documentation will be updated for those questions as time goes by

- Run the following script and fill in the blanks from **3.2.2.**
   - This will create the file structures required for a `MCQ`
   - It will also edit the `config.json`

> Don't forget the optional parameters if you need them

```
python question_bank/convert_autograde.py --pl_repo <pl_repo> --question_folder <question_folder> --question_type <coding or mcq> --language <python or r>
```

- Now you must go through a series of steps to prepare the solution for autograding
   - It is hoped in the future that some of these steps will be moved to the above script

1. Create the choices for each option
   - See the [documentation](https://prairielearn.readthedocs.io/en/latest/elements/) for further examples
   - Replace `<boolean>` with `TRUE` or `FALSE` depending on the choice

```
<pl-multiple-choice answers-name="ans">
  <pl-answer correct="<boolean>">Option 1</pl-answer>
  <pl-answer correct="<boolean>">Option 2</pl-answer>
  ...
</pl-multiple-choice>

```
2. Save them inside of `<question_folder>/question.html`
3. Make sure the question is correct
   - i.e. the wording matches the question type
4. Push the change to *PrairieLearn* and test it

##### Coding

- Run the following script and fill in the blanks from **3.2.2.**
   - This will create the file structures required for a `coding` question
   - It will create either `initial_code.R` or `initial_code.py`
   - It will create a `test` folder with a solution file for the relevant language
   - It will also edit the `config.json`

> Don't forget the optional parameters if you need them

```
python question_bank/convert_autograde.py --pl_repo <pl_repo> --question_folder <question_folder> --question_type <coding or mcq> --initial_code_block <> --language <python or r>
```

- Now you must go through a series of steps to prepare the solution for autograding. Follow steps in 4.1
   - It is hoped in the future that some of these steps will be moved to the above script

##### Numeric
> We do not cover this yet

##### Manual
> Manual questions should already be in the correct format

## 4. Generating test files

> Run this once for each course
>
>>Multiple choice questions should already be complete at this stage
>
>> This may be extended later to more than just coding questions

### 4.1 Writing solutions
> This assumes all questions are in the format as described in the [documentation](https://prairielearn.readthedocs.io/en/latest/question/)

1. Write the code in the solution file
   - If you need to use quotation marks, use the double quotation mark ("<string>") in the solution file. 
2. Make sure this file can be run
   - Import any libraries
   - Make sure any supplementary files exist (i.e. data files that are read)
   - Store the solution in a variable 
3. Use `# SOLUTION` to indicate the solution. All lines before this `# SOLUTION` tag will be added in students' submission files, so we can import libraries or read data
   - Make sure it is clear in the question text which packages are loaded, for example, `Assume the <code>tidyverse</code> library has already been loaded.`
   - You can disable some functions, for example, `max <- function(){NULL}`
4. Append one of the following to the solution file to tell PrairieLearn what to autograde
   - `# AUTOTEST <variable_name>` or `# AUTOTEST <function_name(value)>`
5. If needed, we can define additional variable by the line 
   - `# TESTSETUP <additional_variables>`
6. If needed, we can handle error by adding the line 
   - `# EXPECT-ERROR <call_a_function>`

###### Example
> Add `# SOLUTION` to indicate the solution. Add a line starting with `# AUTOTEST ` to indicate the variable to test. For example,  
>```r
> library(tidyverse)
> 
> # SOLUTION
> grades_data <- read_csv("grades.csv", skip = 2)
> # AUTOTEST grades_data
>```

>For coding questions with test cases, use `# TESTSETUP` to add the test cases. For example, 
>```
> # SOLUTION
>def unravel(x):
>    if not isinstance(x, list):
>        return [x]
>
>    output = []
>    for x_i in x:
>        output += unravel(x_i)
>    return output
>
># TESTSETUP x1 = [1, [2, 3], 4, [5, [6, 7], 8], 9];x2 = [1, 2, 3, [4, 5]]
># AUTOTEST unravel(x1);unravel(x2)
>```

>For coding questions with error handling, use `# EXPECT-ERROR`. For example,
>```
> # SOLUTION
> sort_by_size <- function(sentences) { 
>    if (!is.character(sentences)) {
>        stop("Input must be a character vector.")
>    }
>
>    sorted_sentences <- tibble(sentences = sentences, n = nchar(sentences)) %>%
>        arrange(n) %>%
>        pull(sentences)
>
>    return(sorted_sentences)
> }
> # AUTOTEST sort_by_size(sentences)
> # EXPECT-ERROR sort_by_size(1)
>```

> If you want to test a data frame call `result` but it is okay to have different column order, use 
>```r
> # AUTOTEST result[,order(names(result))] 
>```


#### 4.2. Automatic Creation

- Run  the script to generate test files automatically
  - The script would find all folders with `question.html` under `pl_question_folder`, so `pl_question_folder` can be at any level (for example, the entire course, one lecture, or just one question)
  - `config_path` is the path to the file [autotests.yml](https://github.com/VincentLiu3/prairielearn-migrationa-autotest/blob/main/autotest/autotests.yml) 
```
python autotest/instantiatetests.py --pl_question_folder <pl_question_folder> --config_path <config_path>
```

- Review and push the changes to PrairieLearn