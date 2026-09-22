import sys
import argparse
import traceback

# local modules
from .configuration import create_config, load_config, print_config
from .workflows import translate_workflow, cloze_workflow, undo_workflow
from .wizard import launch_wizard
from .my_classes import GlobalConfig, AnkiConfig
from .notifications import notify


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
        "-u", "--undo", action="store_true", help="cancel last created card"
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

    return parser


def main():

    # 1. Parse CL arguments
    parser = get_parser()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # handle correct operation
    try:
        if args.wizard:
            config = launch_wizard()
            create_config(config)
            sys.exit(0)
        if args.print_config:
            print_config()
            sys.exit(0)

        # loads configuration
        global_config, raw_anki_data = load_config(
            args.source_language, args.target_language, args.notify
        )

        if args.translate:
            translate_workflow(global_config)
            sys.exit(0)

        if args.cloze:
            cloze_workflow(global_config, raw_anki_data)
            sys.exit(0)

        if args.undo:
            url = raw_anki_data.get("default", {}).get("url", "http://localhost:8765")
            undo_workflow(url, global_config.enable_notifications)
            sys.exit(0)

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
