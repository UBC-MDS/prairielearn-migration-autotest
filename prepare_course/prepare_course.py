import argparse
from instances import create_instance
from questions import clear_questions

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "t"):
        return True
    elif v.lower() in ("false", "f"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")

parser = argparse.ArgumentParser()
parser.add_argument("--pl_repo", required=True)

parser.add_argument("--create_instance", default=False, type=str2bool)
parser.add_argument("--instance_dir")
parser.add_argument("--instance_long")
parser.add_argument("--instance_short", default=None)

parser.add_argument("--clear_questions", default=False, type=str2bool)
parser.add_argument("--questions_scope")

args = parser.parse_args()

if args.create_instance:
    assert args.instance_dir is not None, "--instance_dir cannot be 'None' when --create_instance True"
    assert args.instance_long is not None, "--instance_long cannot be 'None' when --create_instance True"

if args.clear_questions:
    assert args.questions_scope is not None, "--questions_scope cannot be 'None' when --clear_questions True"

if args.create_instance:
    try:
        instance_args = {k: v for k, v in vars(args).items() if k.startswith('instance')}
        instance_args['pl_repo'] = args.pl_repo
        result = create_instance(**instance_args)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)

if args.clear_questions:
    try:
        question_args = {k: v for k, v in vars(args).items() if k.startswith('questions')}
        question_args['pl_repo'] = args.pl_repo
        result = clear_questions(**question_args)
    except Exception as e:
        print(f"Error: {e}")
    else:
        print(result)