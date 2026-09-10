# Reads/writes user settings from ~/.config/
# if no config file exists, creates a default one
import tomllib
from pathlib import Path
from importlib.resources import files
import tomli_w

from .my_classes import GlobalConfig, TranslatorConfig, AnkiConfig


config_dir = Path.home() / ".config" / "wordflow"
config_file = config_dir / "config.toml"


class ConfigError(Exception):
    """Custom exception raised when configuration loading fails."""

    pass


def print_config():
    """
    Reads and prints the current configuration file
    """

    print("default config path: .config/wordflow/config.toml")
    try:
        print(config_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            "Error: Could not find config.toml in .config/wordflow. \n",
            "If this is the first time you run this program, wordflow will automatically create one when called with --translate, --cloze, or --wizard",
        )


def create_config(config_dict: dict | None = None):
    # create default config
    if not config_dict:
        try:
            default_config = (
                files("wordflow")
                .joinpath("data", "default_config.toml")
                .read_text(encoding="utf-8")
            )
        except FileNotFoundError:
            raise ConfigError(
                "CRITICAL: Could not find default_config.toml in package data. Try a clean install."
            )

        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(default_config.strip(), encoding="utf-8")
        return 0
    # else we make a custom config (from the wizard)
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_file, "wb") as f:
            tomli_w.dump(config_dict, f)
        return config_file

    except Exception as e:
        # Fallback error handling if there's a permission issue
        raise ConfigError(
            f"\n[-] Critical Error: Failed to write config file. \n Details: {e}"
        )


def load_config(
    source_language_override: str | None = None,
    target_language_override: str | None = None,
    notify: bool | None = None,
):
    """
    reads user config or creates one if there is none
    returns GlobalConfig, TranslatorConfig classes, and raw anki data dictionnary
    """

    # create default config the first time
    if not config_file.exists():
        create_config()

    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

            global_data = config.get("global", {})
            global_config = GlobalConfig(
                source_language=source_language_override
                or global_data.get("source_language", "auto"),
                target_language=target_language_override
                or global_data.get("target_language", "en"),
                enable_notifications=notify
                if notify is not None
                else global_data.get("enable_notifications", True),
            )
            raw_anki_data = config.get("anki", {})

            return global_config, raw_anki_data

    except tomllib.TOMLDecodeError as e:
        # Catch syntax errors
        raise ConfigError(
            f"Syntax error in config file ({config_file}):\n  -> {e}\n\nPlease fix the typo, or delete the file to regenerate the defaults."
        )
    except PermissionError:
        raise ConfigError(f"Permission denied: Cannot read {config_file}.")


def resolve_anki_config(
    raw_anki_data: dict, active_language: str | None = None
) -> AnkiConfig:
    """
    Merges [anki.default] with language-specific [anki.<lang>] overrides.
    Returns a final AnkiConfig class with resolved names.
    if there is no override, simply returns the default anki config
    """

    anki_defaults = raw_anki_data.get("default", {})
    anki_override = raw_anki_data.get(str(active_language), {})

    anki_defaults_fields = anki_defaults.get("fields", {})
    anki_override_fields = anki_override.get("fields", {})

    anki_config = AnkiConfig(
        url=anki_override.get("url", anki_defaults.get("url")),
        deck=anki_override.get(
            "deck", anki_defaults.get("deck", "Wordflow::{source_language}")
        ).replace("{source_language}", str(active_language)),
        card_model=anki_override.get("card_model", anki_defaults.get("card_model")),
        tags=anki_override.get("tags", anki_defaults.get("tags", "")),
        allow_duplicates=anki_override.get(
            "allow_duplicates", anki_defaults.get("allow_duplicates", False)
        ),
        dict_url=anki_override.get("dict_url", anki_defaults.get("dict_url", "")),
        fields=anki_override_fields if anki_override_fields else anki_defaults_fields,
        audio_mode=anki_override.get(
            "audio_mode", anki_defaults.get("audio_mode", "none")
        ),
        audio_accent=anki_override.get(
            "audio_accent", anki_defaults.get("audio_accent", "com")
        ),
        max_synonyms=anki_override.get(
            "max_synonyms", anki_defaults.get("max_synonyms")
        ),
        max_alternates=anki_override.get(
            "max_alternates", anki_defaults.get("max_alternates")
        ),
        max_definitions=anki_override.get(
            "max_definitions", anki_defaults.get("max_definitions")
        ),
        max_examples=anki_override.get(
            "max_examples", anki_defaults.get("max_examples")
        ),
    )
    return anki_config
