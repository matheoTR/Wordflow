import os
from pathlib import Path
from importlib.resources import files


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


def _prompt_int(text: str, default: int) -> int:
    """Helper to prompt for an integer."""
    while True:
        ans = input(f"{text} [{default}]: ").strip()
        if not ans:
            return default
        if ans.isdigit():
            return int(ans)
        print("[-] Invalid input. Please type a valid number.\n")


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

    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    while True:
        ans = input("Select a number (or press ENTER for default): ").strip()

        if not ans:
            return default

        if ans.isdigit():
            idx = int(ans)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]

        for choice in choices:
            if ans.lower() == choice.lower():
                return choice

        print(
            f"[-] Invalid input. Please type a number between 1 and {len(choices)}.\n"
        )


def _display_ascii_art():
    """Attempts to load and print the ASCII art logo from the package data."""
    try:
        art = files("wordflow").joinpath("data", "logo.txt").read_text(encoding="utf-8")
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

    # --- ANKI ---
    print("--- 2. Anki Settings ---")
    print("Make sure Anki is open with AnkiConnect installed.")
    anki_url = _prompt("AnkiConnect URL", "http://localhost:8765")
    deck = _prompt(
        "Default Deck name (use {source_language} for dynamic)",
        "Languages::{source_language}",
    )
    card_model = _prompt("Default Card Model name", "wordflow cloze")

    # Inform the user about the new dictionary-based field layout instead of asking them to type it
    print(
        "\n -> Wordflow will automatically configure a rich 8-field layout (Sentence, Translation, Audio, Dictionary, etc.)."
    )
    print(
        " -> You can easily customize these mappings or add HTML later in the config file.\n"
    )

    tags = _prompt_list(
        "Default tags to apply to cards", ["wordflow", "auto-generated"]
    )

    allow_duplicates = _prompt_bool("Allow duplicate cards?", False)

    audio_mode = _prompt_numbered_choice(
        "Audio generation mode", ["none", "word", "sentence", "both"], "sentence"
    )

    add_dic_url = _prompt_bool(
        "Add automatic dictionary hyperlinks to flashcards?", False
    )
    if add_dic_url:
        dict_url = _prompt(
            "Dictionary URL. Supported dynamic tags: {source_language}, {target_language}, {word}",
            "https://glosbe.com/{source_language}/{target_language}/{word}",
        )
    else:
        dict_url = ""

    # --- DICTIONARY DATA ---
    print("--- 3. Dictionary & Card Richness ---")
    print("Set the maximum number of items to display on your cards if available.")
    max_alternates = _prompt_int("Max alternate translations", 3)
    max_definitions = _prompt_int("Max monolingual definitions", 2)
    max_synonyms = _prompt_int("Max synonyms", 2)
    max_examples = _prompt_int("Max example sentences", 1)

    print("\n" + "=" * 60)
    print(" Configuration complete!")
    print(
        " Note: You can tweak dictionary limits, field mappings, and language-specific"
    )
    print(f" overrides by editing {config_path} manually later.")
    print("=" * 60)

    # Construct the dictionary perfectly matching the new TOML schema
    return {
        "global": {
            "source_language": source_language,
            "target_language": target_language,
            "enable_notifications": enable_notifs,
        },
        "anki": {
            "default": {
                "url": anki_url,
                "deck": deck,
                "card_model": card_model,
                "allow_duplicates": allow_duplicates,
                "tags": tags,
                "audio_mode": audio_mode,
                "dict_url": dict_url,
                "max_alternates": 3,
                "max_definitions": 2,
                "max_synonyms": 2,
                "max_examples": 1,
                "fields": {
                    "Sentence": "{cloze}",
                    "Translation": "{translation}",
                    "Audio": "{word_audio} &nbsp;&nbsp;&nbsp; {sentence_audio}",
                    "Phonetics": "{word_phonetic} &nbsp;&nbsp;&nbsp; {sentence_phonetic}",
                    "Definitions": "{definitions}",
                    "Synonyms": "{synonyms}",
                    "Alternates": "{alternates}",
                    "Examples": "{examples}",
                },
            },
            # Examples of override
            "nl": {"deck": "Languages::Nederlands"},
            "es": {"audio_accent": "com.mx"},
        },
    }
