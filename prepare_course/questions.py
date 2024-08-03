import argparse
import os
import shutil
from check_overlap import check_questions

DEFAULT_SCOPE = "template"


def clear_questions(pl_repo, questions_scope=DEFAULT_SCOPE):
    
    questions_dir = "{}/questions".format(pl_repo)
    if os.path.exists(questions_dir) is False:
        raise Exception(f"Directory with name '{questions_dir}' does not exist")
    
    assessment_dir = "{}/courseInstances".format(pl_repo)
    

    if questions_scope == "template":
        
        if (check_questions(questions_dir, assessment_dir, "externalgrader") or check_questions(questions_dir, assessment_dir, "Gallery")) is True:
            raise Exception("Cannot delete template questions as there are assessments which use them.")

        gallery_dir = "{}/Gallery".format(questions_dir)
        grader_dir = "{}/externalgrader".format(questions_dir)
        
        if os.path.exists(gallery_dir):
            shutil.rmtree(gallery_dir, ignore_errors=True)
        if os.path.exists(grader_dir):
            shutil.rmtree(grader_dir, ignore_errors=True)        
    
    elif questions_scope == "all":
        
        if check_questions(questions_dir, assessment_dir) is True:
            raise Exception("Cannot delete all questions as there are assessments which use them.")
        
        shutil.rmtree(questions_dir, ignore_errors=True)
        os.mkdir(questions_dir)
    
    else:
        raise Exception(f"'{questions_scope}' is an invalid scope.")

    return f"Successfully deleted '{questions_scope}' question(s)"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl_repo", required=True)
    parser.add_argument("--questions_scope", default=DEFAULT_SCOPE)
    args = parser.parse_args()

    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    print(clear_questions(**kwargs))
