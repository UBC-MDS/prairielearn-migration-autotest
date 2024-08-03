import os
import json

def extract_ids_from_json(data):
    # Recursively extract all values associated with the key 'id' from the JSON data.
    ids = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "id":
                ids.append(value)
            ids.extend(extract_ids_from_json(value))
    elif isinstance(data, list):
        for item in data:
            ids.extend(extract_ids_from_json(item))
    return ids

def find_and_extract_ids(directory):
    # Find all 'infoAssessment.json' files and extract 'id' values.
    all_ids = []
    for dirpath, _, filenames in os.walk(directory):
        if "infoAssessment.json" in filenames:
            filepath = os.path.join(dirpath, "infoAssessment.json")
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    all_ids.extend(extract_ids_from_json(data))
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from file: {filepath}")
    return all_ids


def find_info_json_files(directory):
    # List to store the parent folders of info.json files
    parent_folders = []
    
    # Use os.walk to traverse the directory structure
    for root, dirs, files in os.walk(directory):
        if 'info.json' in files:
            # Find the relative path of the parent folder
            parent_folder = os.path.relpath(root, directory)
            # Add the parent folder to the list
            parent_folders.append(parent_folder)
    
    return parent_folders


def check_questions(questions, assessments, filter=None):
    ids = find_and_extract_ids(assessments)
    
    if filter:
        questions = os.path.join(questions, filter)
    
    parent_folders = find_info_json_files(questions)

    if filter:
        if not filter.endswith('/'):
            filter += '/'

        filtered_ids = [id[len(filter):] for id in ids if id.startswith(filter)]
    else:
        filtered_ids = ids

    exists = bool(set(filtered_ids) & set(parent_folders))

    return exists


#print(check_questions("../pl-ubc-dsci523/questions", "../pl-ubc-dsci523/courseInstances"))


