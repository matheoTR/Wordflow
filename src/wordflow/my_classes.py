from dataclasses import dataclass


@dataclass
class AnkiConfig:
    url: str
    deck: str
    card_model: str
    tags: list[str]
    allow_duplicates: bool
    front_field_name: str
    back_field_name: str
    extra_field_name: str


@dataclass
class TranslatorConfig:
    translator: str
    api_key: str
    api_base_url: str
    engine_model: str


@dataclass
class GlobalConfig:
    target_language: str
    confirm_before_add: bool = False
    enable_notifications: bool = True
