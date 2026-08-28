import os
from pathlib import Path
from importlib.resources import files

from .constants import SUPPORTED_TRANSLATORS


def _prompt(text: str, default: str) -> str:
    """Helper to prompt for a string with a fallback default."""
    ans = input(f"{text} [{default}]: ").strip()
    return ans if ans else default


def _prompt_bool(text: str, default: bool) -> bool:
    """Helper to prompt for a boolean (y/n)."""
    default_str = "Y/n" if default else "y/N"
    ans = input(f"{text} [{default_str}]: ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes", "true")


def _prompt_list(text: str, default: list[str]) -> list[str]:
    """Helper to prompt for a comma-separated list."""
    default_str = ", ".join(default)
    ans = input(f"{text} [{default_str}]: ").strip()
    if not ans:
        return default
    return [item.strip() for item in ans.split(",") if item.strip()]


def _prompt_numbered_choice(text: str, choices: list[str], default: str) -> str:
    """Prompts the user to choose from a numbered list of options."""
    print(f"{text} [Default: {default}]")

    # Print the options dynamically
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    while True:
        ans = input("Select a number (or press ENTER for default): ").strip()

        # If user just presses ENTER
        if not ans:
            return default

        # If user types a number
        if ans.isdigit():
            idx = int(ans)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]  # Convert 1-based index to 0-based list index

        # Optional fallback: If they type the string anyway
        for choice in choices:
            if ans.lower() == choice.lower():
                return choice

        # Error state
        print(
            f"[-] Invalid input. Please type a number between 1 and {len(choices)}.\n"
        )


def _display_ascii_art():
    """Attempts to load and print the ASCII art logo from the package data."""
    try:
        art = files("wordflow").joinpath("data", "logo.txt").read_text(encoding="utf-8")
        # terminal color codes (e.g., ANSI Blue)
        print(f"\033[94m{art}\033[0m")
    except Exception:
        pass


def launch_wizard() -> dict:
    """
    Launches an interactive command-line wizard to configure Wordflow.
    Returns a dictionary structured for the config.toml file.
    """
    config_path = Path(os.path.expanduser("~/.config/wordflow/config.toml"))

    _display_ascii_art()
    print("=" * 60)
    print(" Welcome to the Wordflow Setup Wizard!")
    print(" This will generate your configuration file at:")
    print(f" {config_path}")
    print(" Press ENTER to accept the [default] values.")
    print("=" * 60 + "\n")

    # --- GLOBAL ---
    print("--- 1. Language & Global Settings ---")
    source_language = _prompt(
        "Source language (translate from) [auto, en, zh-cn...]", "auto"
    )
    target_language = _prompt("Target language (translate to) [en, fr, nl...]", "en")
    enable_notifs = _prompt_bool("Enable desktop notifications?", True)
    print()

    # --- TRANSLATOR ---
    print("--- 2. Translator Settings ---")
    translator_name = _prompt_numbered_choice(
        "Choose your translator engine",
        choices=SUPPORTED_TRANSLATORS,
        default="GoogleTranslator",
    )

    api_key = ""
    if translator_name not in ("GoogleTranslator", "MyMemoryTranslator"):
        api_key = input(
            f"Enter API Key for {translator_name} (leave blank if not needed): "
        ).strip()
    print()

    # --- ANKI ---
    print("--- 3. Anki Settings ---")
    print("Make sure Anki is open with AnkiConnect installed.")
    anki_url = _prompt("AnkiConnect URL", "http://localhost:8765")
    deck = _prompt(
        "Default Deck name (use {source_language} for dynamic)",
        "Languages::{source_language}",
    )
    card_model = _prompt("Default Card Model name", "wordflow cloze")

    field_names = _prompt_list(
        "Fields (comma-separated, first is cloze question, rest go on back)",
        ["front", "translation", "additional notes"],
    )

    tags = _prompt_list(
        "Default tags to apply to cards", ["wordflow", "auto-generated"]
    )

    allow_duplicates = _prompt_bool("Allow duplicate cards?", False)
    add_dic_url = _prompt_bool(
        "Add automatic dictionary hyperlinks to flashcards? ", False
    )
    if add_dic_url:
        dict_url = _prompt(
            "Dictionary URL. Supported dynamic tags: {source_language}, {target_language}, {word}",
            "https://glosbe.com/{source_language}/{target_language}/{word}",
        )
    else:
        dict_url = ""

    print("\n" + "=" * 60)
    print(" Configuration complete!")
    print(
        " Note: You can add advanced settings (like language specific overrides if you need multiple language setups)"
    )
    print(f" by editing {config_path} manually later.")
    print("=" * 60)

    # Construct the dictionary matching the TOML schema
    return {
        "global": {
            "source_language": source_language,
            "target_language": target_language,
            "enable_notifications": enable_notifs,
        },
        "translator": {
            "translator_name": translator_name,
            "api_key": api_key,
            "api_base_url": "",
            "engine_model": "",
        },
        "anki": {
            "default": {
                "url": anki_url,
                "deck": deck,
                "card_model": card_model,
                "field_names": field_names,
                "allow_duplicates": allow_duplicates,
                "tags": tags,
                "dict_url": dict_url,
            }
        },
    }
