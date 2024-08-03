import argparse
import inspect
from instances import create_instance, remove_instance
from questions import clear_questions
from info_course import update_infoCourse

# Utilities
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "t"):
        return True
    elif v.lower() in ("false", "f"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

def filter_kwargs(func, kwargs):
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters and v is not None}

# Argument Parsing
parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", required=True)

parser.add_argument("--create_instance", default=False, type=str2bool)
parser.add_argument("--instance_mkdir")
parser.add_argument("--instance_long")
parser.add_argument("--instance_short", default=None)

parser.add_argument("--remove_instance", default=False, type=str2bool)
parser.add_argument("--instance_rmdir", default="TemplateCourseInstance", type=str)

parser.add_argument("--clear_questions", default=False, type=str2bool)
parser.add_argument("--questions_scope")

parser.add_argument("--update_infoCourse", default=False, type=str2bool)
parser.add_argument("--course_status", default="update")

args = parser.parse_args()
args_dict = vars(args)  # Convert Namespace to dict for **kwargs usage

# Assertions
if args.create_instance:
    assert args.instance_mkdir is not None, "--instance_mkdir cannot be 'None' when --create_instance True"
    assert args.instance_long is not None, "--instance_long cannot be 'None' when --create_instance True"

if args.clear_questions:
    assert args.questions_scope is not None, "--questions_scope cannot be 'None' when --clear_questions True"

# Actions
if args.create_instance:
    try:
        create_instance_kwargs = filter_kwargs(create_instance, args_dict)
        result = create_instance(**create_instance_kwargs)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)

if args.remove_instance:
    try:
        remove_instance_kwargs = filter_kwargs(remove_instance, args_dict)
        result = remove_instance(**remove_instance_kwargs)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)

if args.clear_questions:
    try:
        clear_questions_kwargs = filter_kwargs(clear_questions, args_dict)
        result = clear_questions(**clear_questions_kwargs)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)

if args.update_infoCourse:
    try:
        update_infoCourse_kwargs = filter_kwargs(update_infoCourse, args_dict)
        result = update_infoCourse(**update_infoCourse_kwargs)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)