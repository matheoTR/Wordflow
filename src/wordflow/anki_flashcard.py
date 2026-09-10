import time
import requests
import re
import urllib.parse

from .text_to_speech import get_audio
from .my_classes import AnkiConfig, TranslationData


class AnkiConfigError(Exception):
    """Raised if there is an error in the anki configuration"""


class AnkiConnectError(Exception):
    """raised if failure to connect to Anki through AnkiConnect"""

    pass


class DuplicateNoteError(Exception):
    """raised if a duplicate note exists, so no card was created"""


def invoke(url: str, action: str, **params):
    """
    Standard helper to send actions to AnkiConnect and handle its error format.
    """
    payload = {"action": action, "version": 6, "params": params}
    try:
        response = requests.post(url, json=payload, timeout=5).json()

        # AnkiConnect returns {"result": ..., "error": ...}
        if response.get("error"):
            raise AnkiConnectError(f"AnkiConnect Error: {response['error']}")

        return response.get("result")

    except requests.exceptions.RequestException as e:
        raise AnkiConnectError(f"Could not reach Anki. Is it open? ({e})")


def setup_anki_model(url: str, model_name: str, fields: dict):
    """
    Checks if the required Cloze model exists.
    If it does exist, it verifies the fields match to prevent silent crashes.
    If not, it creates it.
    """
    if not fields:
        raise ValueError("fields must contain at least one field.")

    existing_models = invoke(url, "modelNames")
    field_names = list(fields.keys())

    if model_name in existing_models:
        existing_fields = invoke(url, "modelFieldNames", modelName=model_name)

        if existing_fields != field_names:
            raise AnkiConfigError(
                f"\nFATAL: The Anki model '{model_name}' already exists, but its fields do not match your config.toml.\n"
                f"Anki expects : {existing_fields}\n"
                f"Config sends : {field_names}\n"
            )
        return

    # if wordflow cloze model does not exist, we create it
    if model_name not in existing_models:
        css = """
        .card { font-family: arial; font-size: 20px; text-align: center; color: white; background-color: #282a36; }
        .cloze { font-weight: bold; color: #ffb86c; }
        #answer { border-top: 1px solid #6272a4; margin-top: 8px; padding-top: 10px; }
        .anki-field { margin-top: 12px; }
        """
        # front. Works since keys are kept in order in python dict
        front_anki = "{{cloze:" + field_names[0] + "}}"

        # back
        back_anki_parts = [f'{front_anki}<div id="answer">']
        for field in field_names[1:]:
            # Using Anki conditional rendering
            # This ensures no whitespace is added if the field is left blank.
            conditional_render = (
                "{{#"
                + field
                + "}}<div class='anki-field'>{{"
                + field
                + "}}</div>{{/"
                + field
                + "}}"
            )
            back_anki_parts.append(conditional_render)

        back_anki_parts.append("</div>")
        back_anki = "".join(back_anki_parts)

        invoke(
            url,
            "createModel",
            modelName=model_name,
            inOrderFields=field_names,
            isCloze=True,
            css=css,
            cardTemplates=[
                {
                    "Name": "Wordflow Cloze",
                    "Front": front_anki,
                    "Back": back_anki,
                }
            ],
        )


def make_cloze(
    anki_config: AnkiConfig, sentence_data: TranslationData, word_data: TranslationData
):
    """
    makes a cloze flashcard and sends it to anki through AnkiConnect
    """
    # before doing anything, checks that the word is in the sentence
    if word_data.source_data.lower() not in sentence_data.source_data.lower():
        raise ValueError(
            f"Could not find the word '{word_data.source_data}' inside the sentence. Cloze creation failed."
        )

    # check environment (create card type and deck if non-existing)
    setup_anki_model(anki_config.url, anki_config.card_model, anki_config.fields)

    # make sure deck exists
    invoke(anki_config.url, "createDeck", deck=anki_config.deck)

    # Make each field match required instructions in config
    formatted_anki_fields = process_fields(
        anki_config=anki_config, sentence_data=sentence_data, word_data=word_data
    )

    # create payload
    note = {
        "deckName": anki_config.deck,
        "modelName": anki_config.card_model,
        "fields": formatted_anki_fields,
        "tags": anki_config.tags,
        "options": {"allowDuplicate": anki_config.allow_duplicates},
    }

    try:
        invoke(anki_config.url, "addNote", note=note)
    except AnkiConnectError as e:
        if "duplicate" in str(e).lower():
            raise DuplicateNoteError(
                f"A note for '{word_data.source_data}' already exists."
            )
        raise e
    return True


def add_audio_to_anki(url: str, text: str, lang_code: str, accent: str):
    """uses text-to-speech to create an audio of the given text and returns the [sound:...] tag."""
    # generate unique name for the tag
    filename = f"wordflow_{int(time.time_ns())}.mp3"

    # generate audio
    audio = get_audio(text=text, language=lang_code, accent=accent)

    # send anki request
    payload = {"filename": filename, "data": audio}
    invoke(url=url, action="storeMediaFile", **payload)

    # return audio tag
    return f"[sound:{filename}]"


def process_fields(
    anki_config: AnkiConfig, sentence_data: TranslationData, word_data: TranslationData
) -> dict:
    """
    Builds the replacement dictionary, generating audio only if required,
    and formats the user's custom Anki fields.
    """

    # 1. LAZY AUDIO
    all_fields_template = "".join(anki_config.fields.values())

    word_audio_instruction = ""
    if "{word_audio}" in all_fields_template:
        tag = add_audio_to_anki(
            anki_config.url,
            word_data.source_data,
            word_data.source_language,
            anki_config.audio_accent,
        )
        word_audio_instruction = (
            f"<span style='font-size: 15px; color: #8be9fd;'><b>Word:</b> {tag}</span>"
        )

    sentence_audio_instruction = ""
    if "{sentence_audio}" in all_fields_template:
        tag = add_audio_to_anki(
            anki_config.url,
            sentence_data.source_data,
            sentence_data.source_language,
            anki_config.audio_accent,
        )
        sentence_audio_instruction = f"<span style='font-size: 15px; color: #8be9fd;'><b>Sentence:</b> {tag}</span>"

    # 2. CLOZE GENERATION + optionnal dictionary url
    if anki_config.dict_url:
        safe_word = urllib.parse.quote(word_data.source_data)
        final_url = anki_config.dict_url.format(
            word=safe_word,
            source_language=word_data.source_language,
            target_language=word_data.target_language,
        )
        linked_word = f'<a href="{final_url}" style="text-decoration: none;">{word_data.source_data}</a>'
        cloze_tag = "{{c1::" + linked_word + "::" + word_data.translated_data + "}}"
    else:
        cloze_tag = (
            "{{c1::" + word_data.source_data + "::" + word_data.translated_data + "}}"
        )

    pattern = re.compile(re.escape(word_data.source_data), re.IGNORECASE)
    cloze_instruction = pattern.sub(cloze_tag, sentence_data.source_data)

    # 3. BUILD THE DICTIONARY
    def format_labeled_list(data_list, max_items, label, separator=", "):
        if not data_list:
            return ""
        items = separator.join(data_list[:max_items])
        return f"<b>{label}:</b> {items}"

    format_dict = {
        # base
        "cloze": cloze_instruction,
        "translation": sentence_data.translated_data,
        "source_word": word_data.source_data,
        # audio
        "word_audio": word_audio_instruction,
        "sentence_audio": sentence_audio_instruction,
        # phonetic
        "sentence_phonetic": format_labeled_list(
            getattr(sentence_data, "phonetic", ""), 1, "sentence phonetic"
        ),
        "word_phonetic": format_labeled_list(
            getattr(word_data, "phonetic", ""), 1, "word phonetic"
        ),
        # other
        "alternates": format_labeled_list(
            getattr(word_data, "alternate_translations", None),
            anki_config.max_alternates,
            "Alternates",
        ),
        "definitions": format_labeled_list(
            getattr(word_data, "definitions", None),
            anki_config.max_definitions,
            "Definitions",
            separator="<br>&bull; ",
        ),
        "synonyms": format_labeled_list(
            getattr(word_data, "synonyms", None), anki_config.max_synonyms, "Synonyms"
        ),
        "examples": format_labeled_list(
            getattr(word_data, "examples", None),
            anki_config.max_examples,
            "Examples",
            separator="<br>&bull; ",
        ),
    }

    # 4. FORMAT FIELDS
    formatted_anki_fields = {}

    for field_name, field_template in anki_config.fields.items():
        if not field_template:
            formatted_anki_fields[field_name] = ""
            continue

        try:
            formatted_anki_fields[field_name] = field_template.format(**format_dict)
        except KeyError as e:
            raise AnkiConfigError(
                f"Warning: Unknown placeholder {e} in config field '{field_name}'"
            )

    print("fields sent to anki: ", formatted_anki_fields)
    return formatted_anki_fields
