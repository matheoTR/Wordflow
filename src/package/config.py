# Reads/writes user settings from ~/.config/
# if no config file exists, creates a default one

import tomllib
from pathlib import Path
import importlib.resources

config_dir = Path.home() / ".config" / "foo"
config_file = config_dir / "config.toml"

default_config = importlib.resources.read_text("package.data", "default_config.txt")


def load_config():
    """reads user config or creates one if there is none"""
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(default_config.strip())

    with open(config_file, "rb") as f:
        return tomllib.load(f)
