import argparse
import os
import sys
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

    args = parser.parse_args()

    # Show version if requested
    if args.version:
        from . import __version__

        print(f"dirmap version {__version__}")
        return 0

    try:
        output_path = mapper.create_map(
            directory=args.directory, output_format=args.format, verbose=args.verbose
        )

        if output_path:
            return 0
        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
