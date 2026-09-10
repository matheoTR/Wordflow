from dataclasses import dataclass


@dataclass
class AnkiConfig:
    url: str
    deck: str
    card_model: str
    tags: list[str]
    dict_url: str | None
    allow_duplicates: bool
    fields: dict
    audio_mode: str = "none"
    audio_accent: str = "com"
    max_synonyms: int = 3
    max_alternates: int = 3
    max_definitions: int = 2
    max_examples: int = 1


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


@dataclass
class TranslationData:
    source_data: str
    translated_data: str
    source_language: str
    target_language: str
    phonetic: str | None
    alternate_translations: list[str] | None
    synonyms: list[str] | None
    definitions: list[str] | None
    examples: list[str] | None
