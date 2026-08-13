# The entry point (handles command-line arguments)
# what the user runs
# 1. parses CL arguments
# 2. loads the configuration
# 3. dispatches orders (trigger a workflow)

# LIST OF FUNCTIONS
# foo -translate
# foo --cloze
# foo --help
# foo --configure

import argparse
from config import load_config
from workflows import *
import sys
import importlib.resources
from wizard import launch_wizard


def print_help():
    # load help message
    try:
        help_text = importlib.resources.read_text("package.data", "help_manual.txt")
        print(help_text)
    except FileNotFoundError:
        print("Help manual not found.", file=sys.stderr)


def get_args():
    commandline_parser = argparse.ArgumentParser(
        prog="foo", description="interprets program mode"
    )
    commandline_parser.add_argument(
        "-t", "--translate", action="store_true", dest="translate"
    )
    commandline_parser.add_argument("-c", "--cloze", action="store_true", dest="cloze")
    commandline_parser.add_argument("-h", "--help", action="store_true", dest="help")
    commandline_parser.add_argument(
        "-w", "--wizard", action="store_true", dest="wizard"
    )
    return commandline_parser.parse_args()


def main():
    # 1. Parse CL arguments
    args = get_args()
    # 2. loads configuration as a dictionnary
    config = load_config()

    # 3. trigger workflow
    if args.translate:
        translate_workflow(config)

    elif args.cloze:
        cloze_workflow(config)

    elif args.help:
        print_help()

    elif args.wizard:
        launch_wizard()
