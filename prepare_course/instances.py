import json
import argparse
import os
import uuid
import shutil

def create_instance(pl_repo, instance_mkdir, instance_long=None, instance_short=None):
    course_json = {
        "uuid": str(uuid.uuid4()),
        "longName": instance_long if instance_long else instance_mkdir,
    }

    if instance_short:
        course_json["shortName"] = instance_short

    course_instance_mkdir = "{}/courseInstances".format(pl_repo)
    if os.path.exists(course_instance_mkdir) is False:
        os.mkdir(course_instance_mkdir)

    instance_mkdir = "{}/{}".format(course_instance_mkdir, instance_mkdir)
    if os.path.exists(instance_mkdir):
        raise Exception(f"Instance with directory name '{instance_mkdir}' already exists")
    else:
        os.mkdir(instance_mkdir)
        assessment_dir = "{}/assessments".format(instance_mkdir)
        os.mkdir(assessment_dir)

        with open("{}/infoCourseInstance.json".format(instance_mkdir), "w") as f:
            json.dump(course_json, f, indent=4)

    return f"Successfully created course instance '{course_json['longName']}'"

def remove_instance(pl_repo, instance_rmdir):
    course_instance_rmdir = "{}/courseInstances/{}".format(pl_repo, instance_rmdir)
    if os.path.exists(course_instance_rmdir):
        shutil.rmtree(course_instance_rmdir, ignore_errors=True)
    else:
        raise Exception(f"Instance '{course_instance_rmdir}' does not exist.")
    
    return f"Successfully removed course instance '{course_instance_rmdir}'"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pl_repo", required=True)
    parser.add_argument("--instance_mkdir", required=True)
    parser.add_argument("--instance_long", default=None)
    parser.add_argument("--instance_short", default=None)
    args = parser.parse_args()

    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    print(create_instance(**kwargs))