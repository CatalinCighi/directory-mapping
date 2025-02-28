import argparse
import os
import sys
import json
from . import mapper


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Map a directory structure with respect to .gitignore rules."
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Path to the directory to map (default: current working directory)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml", "xml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )

    # Add trim-related arguments
    parser.add_argument(
        "--no-trim",
        action="store_true",
        help="Disable the default trimming of the directory structure",
    )

    parser.add_argument(
        "--exclude-config",
        type=str,
        help="Path to a JSON configuration file with exclude patterns",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: structure.<format> in the mapped directory)",
    )

    parser.add_argument(
        "--trim-file",
        type=str,
        help="Trim an existing structure file without mapping a directory",
    )

    args = parser.parse_args()

    # Show version if requested
    if args.version:
        from . import __version__

        print(f"dirmap version {__version__}")
        return 0

    # Handle trim-file mode (trim an existing structure file)
    if args.trim_file:
        if not os.path.exists(args.trim_file):
            print(f"Error: Input file {args.trim_file} not found", file=sys.stderr)
            return 1

        # Determine output file path
        output_file = (
            args.output or f"{os.path.splitext(args.trim_file)[0]}_trimmed.json"
        )

        try:
            # Load the structure file
            with open(args.trim_file, "r") as f:
                structure = json.load(f)

            # Load exclude patterns
            exclude_patterns = mapper.load_exclude_patterns(args.exclude_config)

            # Trim the structure
            trimmed_structure = mapper.trim_structure(structure, exclude_patterns)

            # Save the trimmed structure
            with open(output_file, "w") as f:
                json.dump(trimmed_structure, f, indent=4)

            print(f"Trimmed structure saved to {output_file}")
            return 0
        except Exception as e:
            print(f"Error trimming file: {e}", file=sys.stderr)
            return 1

    try:
        # Handle normal mapping with integrated trimming
        output_path = mapper.create_map(
            directory=args.directory,
            output_format=args.format,
            output_file=args.output,
            verbose=args.verbose,
            exclude_config=args.exclude_config,
            no_trim=args.no_trim,
        )

        if output_path:
            return 0
        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
