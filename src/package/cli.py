# The entry point (handles command-line arguments)
# what the user runs
# 1. parses CL arguments
# 2. loads the configuration
# 3. dispatches orders (trigger a workflow)

# LIST OF FUNCTIONS
# foo -translate
# foo --cloze
# foo --help
# foo --wizard

import sys
import argparse
from importlib.resources import files

# local modules
from configuration import load_config
from workflows import translate_workflow, cloze_workflow
from wizard import launch_wizard


def print_manual():
    """Reads and prints the long-form manual from package data."""
    try:
        manual = (
            files("package.data")
            .joinpath("help_manual.txt")
            .read_text(encoding="utf-8")
        )
        print(manual)
    except FileNotFoundError:
        print("Help manual not found.", file=sys.stderr)


def get_parser():
    parser = argparse.ArgumentParser(
        prog="foo",
        description="Automate Anki flashcard creation and text translation directly from your clipboard!",
        epilog="Run 'foo --manual' to read the full detailed documentation.",
    )
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-t",
        "--translate",
        action="store_true",
        help="Translate the highlighted text and show a notification.",
    )
    group.add_argument(
        "-c",
        "--cloze",
        action="store_true",
        help="Create a cloze flashcard from highlighted text.",
    )
    group.add_argument(
        "-w",
        "--wizard",
        action="store_true",
        help="Launch the interactive configuration wizard.",
    )
    group.add_argument(
        "-m", "--manual", action="store_true", help="Print the full user manual."
    )
    return parser


def main():

    # 1. Parse CL arguments
    parser = get_parser()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    try:
        # 2. Handle manual and wizard
        if args.manual:
            print_manual()
            sys.exit(0)
        if args.wizard:
            launch_wizard()
            sys.exit(0)

        # 3. loads configuration as a dictionnary
        config = load_config()

        # 4. trigger workflow
        if args.translate:
            translate_workflow(config)

        elif args.cloze:
            cloze_workflow(config)

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\n[Error]: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
