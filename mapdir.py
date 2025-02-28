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
    # Always explicitly add .git to the patterns
    default_patterns = [".git/", ".git"]

    try:
        with open(gitignore_path, "r") as file:
            patterns = file.readlines()
            print(f"Loaded .gitignore from {gitignore_path}")

            # Add default patterns if they're not already included
            for pattern in default_patterns:
                if not any(p.strip() == pattern for p in patterns):
                    patterns.append(pattern)

            return PathSpec.from_lines("gitwildmatch", patterns)
    except FileNotFoundError:
        print(f"No .gitignore file found at {gitignore_path}. Using default excludes.")
        return PathSpec.from_lines("gitwildmatch", default_patterns)


def map_directory(directory, pathspec):
    """
    Map the directory structure while respecting .gitignore rules.
    """
    structure = {}
    directory = os.path.normpath(directory)

    for root, dirs, files in os.walk(directory):
        print(f"Scanning directory: {root}")

        # Make root path relative to the directory being scanned for proper matching
        rel_root = os.path.relpath(root, directory)

        # Filter directories - more careful relative path handling
        filtered_dirs = []
        for d in dirs:
            # Construct the proper relative path for the directory
            rel_path = os.path.join(rel_root, d) if rel_root != "." else d

            # Check if it should be excluded
            if not pathspec.match_file(rel_path):
                filtered_dirs.append(d)
            else:
                print(f"Excluding directory: {rel_path}")

        dirs[:] = filtered_dirs  # Update dirs in-place for os.walk

        # Filter files - same careful relative path handling
        filtered_files = []
        for f in files:
            rel_path = os.path.join(rel_root, f) if rel_root != "." else f
            if not pathspec.match_file(rel_path):
                filtered_files.append(f)
            else:
                print(f"Excluding file: {rel_path}")

        if dirs or filtered_files:
            structure[root] = {"files": filtered_files, "dirs": dirs}
            print(
                f"Added to structure: {root} with {len(filtered_files)} files and {len(dirs)} directories"
            )

    return structure


def trim_paths(structure, base_dir):
    """
    Convert absolute paths to relative paths in the structure dictionary.
    """
    trimmed = {}
    for path, content in structure.items():
        # Convert absolute path to relative path
        rel_path = os.path.relpath(path, base_dir)
        # Use directory name for the base directory itself
        if rel_path == ".":
            rel_path = os.path.basename(path)
        trimmed[rel_path] = content

    print(f"Converted absolute paths to relative paths (base: {base_dir})")
    return trimmed


def save_output(data, format_type, output_path, trim_paths_flag=False, base_dir=None):
    """
    Save the mapped directory structure in the specified format.
    """
    try:
        # Apply path trimming if requested
        if trim_paths_flag and base_dir:
            data = trim_paths(data, base_dir)

        if format_type == "json":
            with open(output_path, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Saved structure as JSON at {output_path}")

        elif format_type == "yaml":
            with open(output_path, "w") as file:
                yaml.dump(data, file, default_flow_style=False)
            print(f"Saved structure as YAML at {output_path}")

        elif format_type == "xml":
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

        return True
    except Exception as e:
        print(f"Error saving output: {e}")
        return False


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
    parser.add_argument(
        "--directory",
        type=str,
        default=os.getcwd(),
        help="Path to the directory to map (default: current working directory)",
    )
    parser.add_argument(
        "--trim-paths",
        action="store_true",
        help="Convert absolute paths to relative paths in the output",
    )
    args = parser.parse_args()

    directory_to_map = os.path.abspath(args.directory)  # Resolve full path
    gitignore_path = os.path.join(directory_to_map, ".gitignore")

    print(f"Starting directory mapping for {directory_to_map}...")
    pathspec = load_gitignore_patterns(gitignore_path)
    mapped_structure = map_directory(directory_to_map, pathspec)

    output_path = os.path.join(directory_to_map, f"structure.{args.format}")

    print("Saving output...")
    save_success = save_output(
        mapped_structure, args.format, output_path, args.trim_paths, directory_to_map
    )

    if save_success:
        print(f"Process completed. Directory structure saved at {output_path}")
        return 0
    else:
        print("Failed to save directory structure")
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
