# LIST OF FUNCTIONS
# wordflow --translate
# wordflow --cloze (--lang)
# wordflow --help
# wordflow --wizard
# wordflow --print_config

import sys
import argparse
from importlib.resources import files
import traceback

# local modules
from .configuration import create_config, load_config, print_config
from .workflows import translate_workflow, cloze_workflow
from .wizard import launch_wizard
from .my_classes import GlobalConfig, AnkiConfig, TranslatorConfig
from .notifications import notify


def print_manual():
    """Reads and prints the long-form manual."""
    try:
        # temporary
        # manual_path = Path(__file__).parent / "data" / "help_manual.txt"
        # manual_text = manual_path.read_text(encoding="utf-8")
        # print(manual_text)  # TODO: change to manual

        manual = (
            files(__package__)
            .joinpath("data", "help_manual.txt")
            .read_text(encoding="utf-8")
        )
        print(manual)
    except FileNotFoundError:
        print("Help manual not found.", file=sys.stderr)


def get_parser():
    parser = argparse.ArgumentParser(
        prog="wordflow",
        description="Automate Anki flashcard creation and text translation directly from your clipboard!",
        epilog="Run 'wordflow --manual' to read the full detailed documentation.",
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

    group.add_argument(
        "--print_config",
        action="store_true",
        help="print current configuration file and path to file",
    )
    # Commandline Overrides
    parser.add_argument(
        "-sl",
        "--source_language",
        type=str,
        default=None,
        help="Override the source language used for translation",
    )
    parser.add_argument(
        "-tl",
        "--target_language",
        type=str,
        default=None,
        help="Override the target language used for translation",
    )
    parser.add_argument(
        "--notify",
        action=argparse.BooleanOptionalAction,
        help="Enable or disable notifications (overrides config.toml)",
    )
    parser.add_argument(
        "--translator",
        type=str,
        default=None,
        help="Override translator used for translation",
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
        # 2. Handle manual, config and wizard
        if args.manual:
            print_manual()
            sys.exit(0)
        if args.wizard:
            config = launch_wizard()
            create_config(config)
            sys.exit(0)
        if args.print_config:
            print_config()
            sys.exit(0)

        # 3. loads configuration
        global_config, translator_config, raw_anki_data = load_config(
            args.source_language, args.target_language, args.notify, args.translator
        )

        # 4. trigger workflow
        if args.translate:
            translate_workflow(global_config, translator_config)

        elif args.cloze:
            cloze_workflow(global_config, translator_config, raw_anki_data)

    except KeyboardInterrupt:
        notify(
            "Wordflow",
            "Operation cancelled.",
            enable_notifications=global_config.enable_notifications,
        )
    except Exception as e:
        print("\n[DEBUG TRACEBACK]:", file=sys.stderr)
        traceback.print_exc()  # Prints exact file, line number, and call stack
        sys.exit(1)


if __name__ == "__main__":
    main()
