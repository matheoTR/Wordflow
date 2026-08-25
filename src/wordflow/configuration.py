# Reads/writes user settings from ~/.config/
# if no config file exists, creates a default one
import tomllib
from pathlib import Path
from importlib.resources import files

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


def load_config(
    source_language_override: str | None = None,
    target_language_override: str | None = None,
):
    """
    reads user config or creates one if there is none
    returns GlobalConfig, TranslatorConfig classes, and raw anki data dictionnary
    """

    # create default config the first time
    if not config_file.exists():
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

    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
            # Making the Objects
            translator_data = config.get("translator", {})
            translator_config = TranslatorConfig(
                translator=translator_data.get("translator_name", ""),
                api_key=translator_data.get("api_key", ""),
                api_base_url=translator_data.get("api_base_url", ""),
                engine_model=translator_data.get("engine_model", ""),
            )
            raw_anki_data = config.get("anki", {})

            global_data = config.get("global", {})
            global_config = GlobalConfig(
                source_language=source_language_override
                or global_data.get("source_language", "auto"),
                target_language=target_language_override
                or global_data.get("target_language", "en"),
                enable_notifications=global_data.get("enable_notifications", True),
            )
            return global_config, translator_config, raw_anki_data

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
    anki_defaults_fields = anki_defaults.get("fields", {})
    anki_override = raw_anki_data.get(str(active_language), {})
    anki_override_fields = anki_override.get("fields", {})

    # overrides if exists, otherwise falls back to default
    anki_config = AnkiConfig(
        url=anki_override.get("url", anki_defaults.get("url")),
        deck=anki_override.get("deck", anki_defaults.get("deck")).replace(
            "{source_language}", str(active_language)
        ),
        card_model=anki_override.get("card_model", anki_defaults.get("card_model")),
        tags=anki_override.get("tags", anki_defaults.get("tags")),
        allow_duplicates=anki_override.get(
            "allow_duplicates", anki_defaults.get("allow_duplicates")
        ),
        front_field_name=anki_override_fields.get(
            "front_field_name", anki_defaults_fields.get("front_field_name")
        ),
        back_field_name=anki_override_fields.get(
            "back_field_name", anki_defaults_fields.get("back_field_name")
        ),
        extra_field_name=anki_override_fields.get(
            "extra_field_name", anki_defaults_fields.get("extra_field_name")
        ),
    )
    return anki_config
