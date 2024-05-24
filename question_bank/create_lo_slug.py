import argparse
import os
from openai_utils import create_slug


parser = argparse.ArgumentParser()
parser.add_argument("--lo_file_path")
args = parser.parse_args()

print(f"Reading {args.lo_file_path}")
with open(args.lo_file_path, "r") as f:
    lo_text = f.read()
slug_text = create_slug(lo_text, model_name="gpt-4o")
args.slug_file_path = "{}/slug.txt".format(os.path.dirname(args.lo_file_path))
print(f"Writing slug to {args.slug_file_path}")
with open(args.slug_file_path, "w") as f:
    f.write(slug_text)
