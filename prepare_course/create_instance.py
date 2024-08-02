import json
import argparse
import os
import uuid

DEFAULT_SHORT = "Demo"
DEFAULT_LONG = "Demonstration Course"

def create_instance(repo, short=DEFAULT_SHORT, long=DEFAULT_LONG):
    course_json = {
        "uuid": str(uuid.uuid4()),
        "shortName": short,
        "longName": long,
    }

    course_instance_dir = "{}/courseInstances".format(repo)
    if os.path.exists(course_instance_dir) is False:
        os.mkdir(course_instance_dir)

    instance_dir = "{}/{}".format(course_instance_dir, short)
    if os.path.exists(instance_dir):
        raise Exception(f"Directory with name '{short}' already exists")
        #return {-1, f"Directory with name '{short}' already exists"}
    else:
        os.mkdir(instance_dir)
        assessment_dir = "{}/assessments".format(instance_dir)
        os.mkdir(assessment_dir)

        with open("{}/infoCourseInstance.json".format(instance_dir), "w") as f:
            json.dump(course_json, f, indent=4)

    return f"Successfully created course instance '{long}'"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl_repo", required=True)
    parser.add_argument("--short", default=DEFAULT_SHORT)
    parser.add_argument("--long", default=DEFAULT_LONG)
    args = parser.parse_args()
    create_instance(args.pl_repo, args.short, args.long)
