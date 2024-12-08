import os
import json
import yaml
import argparse
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from pathspec import PathSpec


def load_gitignore_patterns(gitignore_path):
    """
    Load .gitignore patterns using pathspec library.
    """
    try:
        with open(gitignore_path, "r") as file:
            print(f"Loaded .gitignore from {gitignore_path}")
            return PathSpec.from_lines("gitwildmatch", file)
    except FileNotFoundError:
        print(f"No .gitignore file found at {gitignore_path}. Continuing without it.")
        return PathSpec.from_lines("gitwildmatch", [])


def map_directory(directory, pathspec):
    """
    Map the directory structure while respecting .gitignore rules.
    """
    structure = {}
    for root, dirs, files in os.walk(directory):
        print(f"Scanning directory: {root}")

        # Filter directories and files using pathspec
        dirs[:] = [
            d
            for d in dirs
            if not pathspec.match_file(
                os.path.relpath(os.path.join(root, d), directory)
            )
        ]
        filtered_files = [
            f
            for f in files
            if not pathspec.match_file(
                os.path.relpath(os.path.join(root, f), directory)
            )
        ]

        if dirs or filtered_files:
            structure[root] = {"files": filtered_files, "dirs": dirs}
            print(
                f"Added to structure: {root} with {len(filtered_files)} files and {len(dirs)} directories"
            )
    return structure


def save_output(data, format, output_path):
    """
    Save the mapped directory structure in the specified format.
    """
    try:
        if format == "json":
            with open(output_path, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Saved structure as JSON at {output_path}")

        elif format == "yaml":
            with open(output_path, "w") as file:
                yaml.dump(data, file, default_flow_style=False)
            print(f"Saved structure as YAML at {output_path}")

        elif format == "xml":
            root = Element("structure")
            for path, content in data.items():
                dir_element = SubElement(root, "directory", {"path": path})
                files_element = SubElement(dir_element, "files")
                for file in content["files"]:
                    SubElement(files_element, "file").text = file
                dirs_element = SubElement(dir_element, "subdirectories")
                for subdir in content["dirs"]:
                    SubElement(dirs_element, "directory").text = subdir
            tree = ElementTree(root)
            tree.write(output_path)
            print(f"Saved structure as XML at {output_path}")

    except Exception as e:
        print(f"Error saving output: {e}")


def main():
    """
    Main function to parse arguments, map directory, and save the output.
    """
    parser = argparse.ArgumentParser(
        description="Map a directory and save its structure."
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "xml"],
        default="json",
        help="Output format",
    )
    args = parser.parse_args()

    current_directory = os.getcwd()
    gitignore_path = os.path.join(current_directory, ".gitignore")

    print("Starting directory mapping...")
    pathspec = load_gitignore_patterns(gitignore_path)
    mapped_structure = map_directory(current_directory, pathspec)

    output_path = os.path.join(current_directory, f"structure.{args.format}")

    print("Saving output...")
    save_output(mapped_structure, args.format, output_path)

    print(f"Process completed. Directory structure saved at {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
