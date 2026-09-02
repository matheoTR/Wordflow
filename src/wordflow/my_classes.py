from dataclasses import dataclass


@dataclass
class AnkiConfig:
    url: str
    deck: str
    card_model: str
    tags: list[str]
    dict_url: str
    allow_duplicates: bool
    field_names: list[str]
    audio_mode: str = "none"
    audio_accent: str = "com"


@dataclass
class TranslatorConfig:
    translator: str
    api_key: str
    api_base_url: str
    engine_model: str


@dataclass
class GlobalConfig:
    source_language: str
    target_language: str
    enable_notifications: bool = True
