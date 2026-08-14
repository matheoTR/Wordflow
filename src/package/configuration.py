# Reads/writes user settings from ~/.config/
# if no config file exists, creates a default one

import tomllib
from pathlib import Path
from importlib.resources import files
import sys


config_dir = Path.home() / ".config" / "foo"
config_file = config_dir / "config.toml"


class ConfigError(Exception):
    """Custom exception raised when configuration loading fails."""

    pass


def load_config() -> dict:
    """reads user config or creates one if there is none"""

    # create default config the first time
    if not config_file.exists():
        try:
            default_config = (
                files("package.data")
                .joinpath("default_config.toml")
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
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        # Catch syntax errors
        raise ConfigError(
            f"Syntax error in config file ({config_file}):\n  -> {e}\n\nPlease fix the typo, or delete the file to regenerate the defaults."
        )
    except PermissionError:
        raise ConfigError(f"Permission denied: Cannot read {config_file}.")
