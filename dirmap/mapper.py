import os
import json
import yaml
import logging
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from pathspec import PathSpec


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_gitignore_patterns(gitignore_path):
    """
    Load .gitignore patterns using pathspec library.

    Args:
        gitignore_path (str): Path to the .gitignore file

    Returns:
        PathSpec: Compiled gitignore patterns
    """
    try:
        with open(gitignore_path, "r") as file:
            logger.info(f"Loaded .gitignore from {gitignore_path}")
            return PathSpec.from_lines("gitwildmatch", file)
    except FileNotFoundError:
        logger.info(
            f"No .gitignore file found at {gitignore_path}. Continuing without it."
        )
        return PathSpec.from_lines("gitwildmatch", [])


def map_directory(directory, pathspec):
    """
    Map the directory structure while respecting .gitignore rules.

    Args:
        directory (str): Directory to map
        pathspec (PathSpec): Compiled gitignore patterns

    Returns:
        dict: Mapped directory structure
    """
    structure = {}
    for root, dirs, files in os.walk(directory):
        logger.debug(f"Scanning directory: {root}")

        # Convert paths to be relative to the directory for proper pathspec matching
        rel_root = os.path.relpath(root, directory)

        # Filter directories and files using pathspec
        dirs[:] = [
            d
            for d in dirs
            if not pathspec.match_file(
                os.path.join(rel_root, d) if rel_root != "." else d
            )
        ]

        filtered_files = [
            f
            for f in files
            if not pathspec.match_file(
                os.path.join(rel_root, f) if rel_root != "." else f
            )
        ]

        if dirs or filtered_files:
            structure[root] = {"files": filtered_files, "dirs": dirs}
            logger.debug(
                f"Added to structure: {root} with {len(filtered_files)} files and {len(dirs)} directories"
            )

    return structure


def save_output(data, format_type, output_path):
    """
    Save the mapped directory structure in the specified format.

    Args:
        data (dict): Mapped directory structure
        format_type (str): Output format ('json', 'yaml', or 'xml')
        output_path (str): Path to save the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if format_type == "json":
            with open(output_path, "w") as file:
                json.dump(data, file, indent=4)
            logger.info(f"Saved structure as JSON at {output_path}")

        elif format_type == "yaml":
            with open(output_path, "w") as file:
                yaml.dump(data, file, default_flow_style=False)
            logger.info(f"Saved structure as YAML at {output_path}")

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
            logger.info(f"Saved structure as XML at {output_path}")

        return True
    except Exception as e:
        logger.error(f"Error saving output: {e}")
        return False


def create_map(directory=None, output_format="json", verbose=False):
    """
    Main function that maps a directory and saves the output.

    Args:
        directory (str, optional): Directory to map. Defaults to current working directory.
        output_format (str, optional): Output format. Defaults to "json".
        verbose (bool, optional): Enable verbose logging. Defaults to False.

    Returns:
        str: Path to the saved structure file
    """
    # Set logging level based on verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)

    # Set directory to map
    directory_to_map = os.path.abspath(directory or os.getcwd())

    # Path to gitignore file
    gitignore_path = os.path.join(directory_to_map, ".gitignore")

    logger.info(f"Starting directory mapping for {directory_to_map}...")

    # Load gitignore patterns
    pathspec = load_gitignore_patterns(gitignore_path)

    # Map directory structure
    mapped_structure = map_directory(directory_to_map, pathspec)

    # Path to save output
    output_path = os.path.join(directory_to_map, f"structure.{output_format}")

    logger.info("Saving output...")

    # Save output in specified format
    save_success = save_output(mapped_structure, output_format, output_path)

    if save_success:
        logger.info(f"Process completed. Directory structure saved at {output_path}")
        return output_path
    else:
        logger.error("Failed to save directory structure")
        return None
