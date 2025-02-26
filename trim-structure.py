import json
import os


def trim_structure(input_file, output_file, exclude_patterns):
    """
    Trim a structure.json file by excluding directories matching patterns

    Args:
        input_file (str): Path to input structure.json
        output_file (str): Path for trimmed output file
        exclude_patterns (list): List of patterns to exclude
    """
    # Load the structure data
    with open(input_file, "r") as f:
        structure = json.load(f)

    # Create a new trimmed structure
    trimmed_structure = {}

    # Filter out paths containing exclude patterns
    for path, content in structure.items():
        # Check if path contains any exclude pattern
        if not any(pattern in path for pattern in exclude_patterns):
            # Recursively filter the files and directories too
            filtered_dirs = [
                d
                for d in content.get("dirs", [])
                if not any(pattern in d for pattern in exclude_patterns)
            ]

            # Create filtered entry
            trimmed_structure[path] = {
                "files": content.get("files", []),
                "dirs": filtered_dirs,
            }

    # Write the trimmed structure to output file
    with open(output_file, "w") as f:
        json.dump(trimmed_structure, f, indent=2, sort_keys=True)

    print(f"Original structure had {len(structure)} directories")
    print(f"Trimmed structure has {len(trimmed_structure)} directories")
    print(f"Trimmed structure saved to {output_file}")


if __name__ == "__main__":
    # Configure these paths
    input_file = "structure.json"
    output_file = "structure_trimmed.json"

    # Add patterns you want to exclude
    exclude_patterns = [
        ".git",
        "venv",
        "__pycache__",
        ".ipynb_checkpoints",
        "site-packages",
        ".dist-info",
        "pip-",
        "numpy",
        "pandas",
        "dateutil",
        "tzdata",
        "pytz",
        "six-",
        "dirmap",
        "lib/python",
        "bin/",
    ]

    trim_structure(input_file, output_file, exclude_patterns)
