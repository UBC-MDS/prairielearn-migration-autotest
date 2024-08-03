import json
import argparse
import os
import uuid

def create_instance(pl_repo, instance_dir, instance_long=None, instance_short=None):
    course_json = {
        "uuid": str(uuid.uuid4()),
        "longName": instance_long if instance_long else instance_dir,
    }

    if instance_short:
        course_json["shortName"] = instance_short

    course_instance_dir = "{}/courseInstances".format(pl_repo)
    if os.path.exists(course_instance_dir) is False:
        os.mkdir(course_instance_dir)

    instance_dir = "{}/{}".format(course_instance_dir, instance_dir)
    if os.path.exists(instance_dir):
        raise Exception(f"Instance with directory name '{instance_dir}' already exists")
    else:
        os.mkdir(instance_dir)
        assessment_dir = "{}/assessments".format(instance_dir)
        os.mkdir(assessment_dir)

        with open("{}/infoCourseInstance.json".format(instance_dir), "w") as f:
            json.dump(course_json, f, indent=4)

    return f"Successfully created course instance '{course_json['longName']}'"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl_repo", required=True)
    parser.add_argument("--instance_dir", required=True)
    parser.add_argument("--instance_long", default=None)
    parser.add_argument("--instance_short", default=None)
    args = parser.parse_args()

    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    print(create_instance(**kwargs))