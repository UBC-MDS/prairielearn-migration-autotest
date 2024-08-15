import os
import yaml
import json
import uuid

def build_json(pl_repo):
    yml_template = "prepare_course/infoCourse.yml"
    if not os.path.exists(yml_template):
        raise Exception(f"Your '{yml_template}' is missing")
    
    # Load the existing JSON if it exists
    existing_json = load_existing(pl_repo)
    
    # Use the values from the existing JSON if they exist, otherwise generate a new one
    course_uuid = existing_json.get("uuid", str(uuid.uuid4()))
    course_name = existing_json.get("name", "Template Name")
    course_title = existing_json.get("title", "Template Title")

    # Load the YAML file
    with open(yml_template, 'r') as yaml_file:
        yaml_content = yaml.safe_load(yaml_file)

    # Prepare the JSON content
    new_json = {
        "uuid": course_uuid,
        "name": course_name,
        "title": course_title,
        "options": yaml_content["pl"].get("options", {}),
        "topics": yaml_content["pl"].get("topics", []),
        "tags": yaml_content["pl"].get("tags", []),
        "timezone": yaml_content["pl"].get("timezone", "")
    }

    return new_json
    
def create_file(pl_repo, content):
    # Save the JSON content to a file
    with open("{}/infoCourse.json".format(pl_repo), "w") as f:
        json.dump(content, f, indent=4)
    return 1

def load_existing(pl_repo):
    existing_json = "{}/infoCourse.json".format(pl_repo)
    if not os.path.exists(existing_json):
        return {}
    else:
        with open(existing_json, "r") as f:
            course_json = json.load(f)
    return course_json

def update_json(new, existing):
    # Add unique topics from existing to new
    existing_topics = {topic["name"]: topic for topic in existing.get("topics", [])}
    new_topics = {topic["name"]: topic for topic in new.get("topics", [])}
    combined_topics = {**existing_topics, **new_topics}
    new["topics"] = list(combined_topics.values())
    
    # Add unique tags from existing to new
    existing_tags = {tag['name']: tag for tag in existing.get("tags", [])}
    new_tags = {tag['name']: tag for tag in new.get("tags", [])}
    combined_tags = {**existing_tags, **new_tags}
    new["tags"] = list(combined_tags.values())

    # Add any additional fields from existing to new if they don't already exist in new
    for key, value in existing.items():
        if key not in new:
            new[key] = value

    return new

def update_infoCourse(pl_repo, course_status):
    
    new_json = build_json(pl_repo)
    
    if course_status == "overwrite":
        create_file(pl_repo, new_json)
    elif course_status == "update":
        updated_json = update_json(new_json, load_existing(pl_repo))
        create_file(pl_repo, updated_json)
    else:
        raise Exception(f"'{course_status}' is not a valid value for --course_status")
    
    return f"Successfully completed {course_status} of infoCourse.json"


""" # Example usage
if __name__ == "__main__":
    new_json = build_json("../pl-ubc-dsci532", "CourseName", "CourseTitle")
    existing_json = load_existing("../pl-ubc-dsci532")
    updated_json = update_json(new_json, existing_json)
    create_file("../pl-ubc-dsci532", updated_json) """
