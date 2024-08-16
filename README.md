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
python question_bank/organize_questions.py --pl_repo <pl_repo> --slug_file_path <slug_path>
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


#### 3.2.3. Create Question

> This will require an understanding of the course content
>> You will need to do one of the following, make the solution yourself, ask ChatGPT, or consult the professor

All PrairieLearn questions require a question file which displays the layout of the question. Each question type must be graded according to one of the following three methods:

1. *Internal Autograder*
2. *External Autograder*
3. *Manually Graded*

The majority of question types will fall under the *Internal Autograder* category. The solutions to these questions are included inside the `question.html` file, typically using attributes within the HTML. Some questions will rely on our *External Autograder*, namely `coding` questions. The solution for these questions must be defined in a separate file and will require you to generate test files accordingly. *Manually Graded* questions will rely on the instructor to keep track of the solutions in an organised and secure fashion so that they are only accessible by the relevant parties.

For questions that use the *Internal Autograder*, our script may provide some assistance in automating the question generation process (detailed in this section if so). However, the [PrairieLearn documentation](https://prairielearn.readthedocs.io/en/latest/elements/) should be consulted to ensure your questions are kept inline with the version of PrairieLearn that is deployed. For questions using our *External Autograder*, please see **4.1** for instructions after completing the steps in this section.

A lot of questions will benefit from the inclusion of data from an external file or by randomisation of the question parameters and/or data. Details will be provided where appropriate on how to do this, with some further information provided at the end of **Section 3**. It is recommended to consult this section **during** the creation of questions to reduce the time to develop each question.

Creating questions is assisted through the development of our `convert_autograde` script. This will assist with ensuring questions match the standard template for PrairieLearn that is used by the MDS. It will include features such as reformatting questions and updating the `info.json` file with the appropriate details.

- The `convert_autograde` script has the following optional parameters that can be applied to all question type
   - `--create_data_file True` - this will create an empty `data.txt` file
   - `--create_server_file True` - this will create an empty `server.py` file

Skip ahead to the section that is relevant for your question type

##### MCQ

> This is for questions that could have multiple solutions, i.e. not TRUE/FALSE or numeric options
>> This documentation will be updated for those questions as time goes by

- The `convert_autograde` script has the following optional parameters that can be applied to `MCQ` questions
   - `--mcq_block <checkbox or multiple-choice>` to define the type of `MCQ` question
   - `--mcq_partial_credit <COV or EDC or PC>` to define the grading method. More details [here](https://prairielearn.readthedocs.io/en/latest/elements/#partial-credit-grading)
   - Any additional parameters mentioned at the start of **3.2.3.**

[//]: <> (# Create white space in the markdown)

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

- The `convert_autograde` script has the following optional parameters that can be applied to `coding` questions
   - `--create_workspace True` - this will create a workspace based on `--language`
   - Any additional parameters mentioned at the start of **3.2.3.**

[//]: <> (# Create white space in the markdown)

- Run the following script and fill in the blanks from **3.2.2.**
   - This will create the file structures required for a `coding` question
   - It will create either `initial_code.R` or `initial_code.py`
   - It will create a `test` folder with a solution file for the relevant language
   - It will also edit the `config.json`
   - Can optionally create a `workspace` instead of a `<pl-file-editor>`
     - Don't forget to update the image using the [PrairieLearn Dockers](https://github.com/UBC-MDS/prairielearn-dockers) `update_image.py` script

> Don't forget the optional parameters if you need them

```
python question_bank/convert_autograde.py --pl_repo <pl_repo> --question_folder <question_folder> --question_type <coding or mcq> --initial_code_block <> --language <python or r> --create_server_file <> --create_data_file <> --create_workspace <>
```

- Now you must go through a series of steps to prepare the solution for autograding. Follow steps in 4.1
   - It is hoped in the future that some of these steps will be moved to the above script

##### Input
> We do not cover this yet

##### Manual
> Manual questions should already be in the correct format

### 3.3. Importing Data and Randomisation

- We recommend doing this during the creation of a question in **3.2.** but it can be performed retroactively as well.

#### 3.3.1. Importing Data

> This section is a work in progress

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

#### 3.3.2 Randomising Questions

> This section is to be updated in the future

### 3.4. Using Workspaces 

our `convert_autograde` script can also be used to create/edit files to use workspace by setting `--create_workspace=True`
- First please update `autotest.yml` if you want to use specific workspace image 
- The script will update `info.json` to specify the workspace image and add the `workspace` tag. If the question uses autograder, it would specify the graded files so that the question can still be autograded.  
- A new folder `workspace` with necessary files will be created automatically 
- Two html tags `<pl-workspace></pl-workspace>` and `<pl-file-preview></pl-file-preview>` will be added to `question.html`. Please make sure these tags are placed in the correct place. 
- Finally, if there is the initial code in the question folder, please make sure you copy the files.

## 4. Generating test files

> Run this once for each course
>
>>Multiple choice questions should already be complete at this stage
>
>> This may be extended later to more than just coding questions

### 4.1 Writing solutions
> This assumes all questions are in the format as described in the [documentation](https://prairielearn.readthedocs.io/en/latest/question/)

1. Write the code in the solution file
   - If you need to use quotation marks, use only the double quotation mark ("<string>") in the solution file. 
2. Make sure this file can be run
   - Import any libraries
   - Make sure any supplementary files exist (i.e. data files that are read)
   - Store the solution in a variable 
3. Use `# SOLUTION` to indicate the solution. All lines before this `# SOLUTION` tag will be added in students' submission files, so we can import libraries or read data
   - Make sure it is clear in the question text which packages are loaded, for example, `The <code>tidyverse</code> library has already been loaded.`
   - You can disable some functions, for example, `max <- function(){NULL}`
4. If needed, use `# TESTSETUP` to define additional variables or modify variables. All lines (except `AUTOTEST` and `EXPECT-ERROR`) after this `# TESTSETUP` tag will be added in students' submission files as well.
5. Append one of the following to the solution file to tell PrairieLearn what to autograde
   - `# AUTOTEST <variable_name>` or `# AUTOTEST <function_name(value)>`
   - `# DISPATCH <variable_name>` or `# DISPATCH <function_name(value)>`: specify the variables to determine variable types (see examples below)
   - `# EXPECT-ERROR <function_name(value)>`

###### Example
> Add `# SOLUTION` to indicate the solution. Add a line starting with `# AUTOTEST ` to indicate the variable to test. For example,  
>```r
> library(tidyverse)
> # SOLUTION
> grades_data <- read_csv("grades.csv", skip = 2)
> # AUTOTEST grades_data
>```

>For coding questions with test cases, use `# TESTSETUP` to define the test cases. For example, 
>```python
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
># TESTSETUP 
>x1 = [1, [2, 3], 4, [5, [6, 7], 8], 9]
>x2 = [1, 2, 3, [4, 5]]
># AUTOTEST unravel(x1);unravel(x2)
>```

>For coding questions with error handling, use `# EXPECT-ERROR`. For example,
>```r
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

> For questions where the test variables are randomized, you need to write variables in '# DISPATCH' so that we can check the variable types to generate test files 
>```python
> import numpy as np
> # SOLUTION
> def max_rowsum(x):
>     return np.max(np.sum(x, axis=1))
>
> def min_rowsum(x):
>     return np.min(np.sum(x, axis=1))
> 
> # TESTSETUP
> x1 = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
> # AUTOTEST {self.data["params"]["variable_name"]}(x1)
> # DISPATCH max_rowsum(x1)
>```

> If you want to test a data frame and it is okay to have a different column order:  
>```r
> # TESTSETUP 
> result <- result[,order(names(result))]
> # AUTOTEST result
>```

#### 4.2. Automatic Creation

- Run  the script to generate test files automatically
  - The script would find all folders with `question.html` under `pl_question_folder`, so `pl_question_folder` can be at any level (for example, the entire course, one lecture, or just one question)
  - `config_path` is the path to the file [autotests.yml](https://github.com/VincentLiu3/prairielearn-migrationa-autotest/blob/main/autotest/autotests.yml) 
```
python autotest/instantiatetests.py --pl_question_folder <pl_question_folder> --config_path <config_path>
```

- Review and push the changes to PrairieLearn