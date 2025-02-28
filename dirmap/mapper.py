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


def load_exclude_patterns(config_path=None):
    """
    Load exclude patterns from a configuration file or use defaults.

    Args:
        config_path (str, optional): Path to a JSON config file with exclude patterns.
                                    If None, use the default config file.

    Returns:
        list: List of patterns to exclude
    """
    # If no custom config provided, use the default one packaged with dirmap
    if not config_path:
        config_path = os.path.join(os.path.dirname(__file__), "default_exclude.json")

    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            logger.info(f"Loaded exclude patterns from {config_path}")
            return config.get("exclude_patterns", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load exclude patterns from {config_path}: {e}")
        logger.warning("Continuing without additional exclude patterns.")
        return []


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


def trim_structure(structure, exclude_patterns):
    """
    Trim a directory structure by excluding paths matching patterns.

    Args:
        structure (dict): Directory structure map to trim
        exclude_patterns (list): List of patterns to exclude

    Returns:
        dict: Trimmed directory structure
    """
    # Create a new trimmed structure
    trimmed_structure = {}

    # Keep track of stats for logging
    original_count = len(structure)

    # Filter out paths containing exclude patterns
    for path, content in structure.items():
        # Check if path contains any exclude pattern
        if not any(pattern in path for pattern in exclude_patterns):
            # Filter the directories list too
            filtered_dirs = [
                d
                for d in content.get("dirs", [])
                if not any(pattern in d for pattern in exclude_patterns)
            ]

            # Create filtered entry with original files but filtered dirs
            trimmed_structure[path] = {
                "files": content.get("files", []),
                "dirs": filtered_dirs,
            }

    # Log the results
    trimmed_count = len(trimmed_structure)
    excluded_count = original_count - trimmed_count

    logger.info(
        f"Trimmed structure: {trimmed_count} directories kept, {excluded_count} excluded"
    )

    return trimmed_structure


def trim_paths(structure, base_dir):
    """
    Convert absolute paths to relative paths in the structure dictionary.

    Args:
        structure (dict): The directory structure with absolute paths as keys
        base_dir (str): The base directory to make paths relative to

    Returns:
        dict: A new structure with relative paths as keys
    """
    trimmed = {}
    for path, content in structure.items():
        # Convert absolute path to relative path
        rel_path = os.path.relpath(path, base_dir)
        # Use directory name for the base directory itself
        if rel_path == ".":
            rel_path = os.path.basename(base_dir)
        trimmed[rel_path] = content

    logger.info(f"Converted absolute paths to relative paths (base: {base_dir})")
    return trimmed


def save_output(data, format_type, output_path, trim_paths_flag=True, base_dir=None):
    """
    Save the mapped directory structure in the specified format.

    Args:
        data (dict): Mapped directory structure
        format_type (str): Output format ('json', 'yaml', or 'xml')
        output_path (str): Path to save the output file
        trim_paths_flag (bool): Whether to trim absolute paths to relative paths. Defaults to True.
        base_dir (str): Base directory for relative paths (if trim_paths_flag is True)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Apply path trimming if requested
        if trim_paths_flag and base_dir:
            data = trim_paths(data, base_dir)

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


def create_map(
    directory=None,
    output_format="json",
    output_file=None,
    verbose=False,
    exclude_config=None,
    no_trim=False,
    trim_paths_flag=True,  # Changed default to True
):
    """
    Main function that maps a directory and saves the output.

    Args:
        directory (str, optional): Directory to map. Defaults to current working directory.
        output_format (str, optional): Output format. Defaults to "json".
        output_file (str, optional): Output file path. Defaults to structure.<format> in the mapped directory.
        verbose (bool, optional): Enable verbose logging. Defaults to False.
        exclude_config (str, optional): Path to a JSON config file with exclude patterns.
                                      If None, use the default config.
        no_trim (bool, optional): If True, do not trim the structure. Defaults to False.
        trim_paths_flag (bool, optional): If True, convert absolute paths to relative. Defaults to True.

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

    # Trim the structure by default unless no_trim is True
    if not no_trim:
        # Load exclude patterns from config
        exclude_patterns = load_exclude_patterns(exclude_config)
        if exclude_patterns:
            logger.info(
                f"Trimming structure with {len(exclude_patterns)} exclude patterns..."
            )
            mapped_structure = trim_structure(mapped_structure, exclude_patterns)
        else:
            logger.info("No exclude patterns found. Skipping trim step.")

    # Path to save output
    if output_file:
        output_path = output_file
    else:
        output_path = os.path.join(directory_to_map, f"structure.{output_format}")

    logger.info("Saving output...")

    # Save output in specified format with optional path trimming
    save_success = save_output(
        mapped_structure, output_format, output_path, trim_paths_flag, directory_to_map
    )

    if save_success:
        logger.info(f"Process completed. Directory structure saved at {output_path}")
        return output_path
    else:
        logger.error("Failed to save directory structure")
        return None
