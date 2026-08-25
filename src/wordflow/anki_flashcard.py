# Handles the JSON formatting and AnkiConnect requests
# creates payload
#

import requests
import re
from .my_classes import AnkiConfig


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


def setup_anki_model(
    url: str,
    model_name: str,
    front_field_name: str,
    back_field_name: str,
    extra_field_name: str,
):
    """
    Checks if the required Cloze model exists. If not, it creates it
    with the exact fields and dark-mode styling needed.
    """
    existing_models = invoke(url, "modelNames")
    print(existing_models)
    print(f"Is '{model_name}' in Anki? -> {model_name in existing_models}\n")
    # map lowercase names
    # existing_models_lowered = {m.lower(): m for m in existing_models}

    # if wordflow cloze model does not exist, we create it
    if model_name not in existing_models:
        css = """
        .card { font-family: arial; font-size: 20px; text-align: center; color: white; background-color: #282a36; }
        .cloze { font-weight: bold; color: #ffb86c; }
        #answer { border-top: 1px solid #6272a4; margin-top: 15px; padding-top: 15px; }
        """
        front_anki = f"{{{{cloze:{front_field_name}}}}}"
        back_anki = f"{{{{{back_field_name}}}}}"
        extra_anki = f"{{{{{extra_field_name}}}}}"

        # DEBUG
        print("front: ", front_anki)
        print("trans: ", back_anki)
        print("notes: ", extra_anki)
        print("css: ", css)
        print("front_field_name: ", front_field_name)
        print("translation_field_name: ", back_field_name)
        print("additionnal_info_field_name: ", extra_field_name)

        res = invoke(
            url,
            "createModel",
            modelName=model_name,
            inOrderFields=[
                front_field_name,
                back_field_name,
                extra_field_name,
            ],
            isCloze=True,
            css=css,
            cardTemplates=[
                {
                    "Name": "Wordflow Cloze",
                    "Front": front_anki,
                    "Back": f"{front_anki}<div id=answer>{back_anki}<br><br>{extra_anki}</div>",
                }
            ],
        )
        print(res)


def is_duplicate_note(url: str, note: dict) -> bool:
    """
    Returns True if the note already exists.
    """
    results = invoke(url, "canAddNotes", notes=[note])
    # results is a list of booleans matching the input list
    return not results[0] if results else False


def make_cloze(
    original_sentence: str,
    translated_sentence: str,
    original_word: str,
    translated_word: str,
    anki_config: AnkiConfig,
):
    """
    makes a cloze flashcard and sends it to anki through AnkiConnect
    based on language and packet
    """
    # check environment (create card type and deck if non-existing)
    print("Model name: ", anki_config.card_model)
    setup_anki_model(
        anki_config.url,
        anki_config.card_model,
        anki_config.front_field_name,
        anki_config.back_field_name,
        anki_config.extra_field_name,
    )
    invoke(anki_config.url, "createDeck", deck=anki_config.deck)

    # clean trailing spaces
    clean_sentence = original_sentence.strip()
    clean_word = original_word.strip()
    clean_translated_word = translated_word.strip()

    # CARD FIELDS
    cloze_field = f"{{{{c1::{clean_word}::{clean_translated_word}}}}}"
    # case-insensitive replacement
    pattern = re.compile(re.escape(clean_word), re.IGNORECASE)
    front_field = pattern.sub(cloze_field, clean_sentence)

    # Cloze card health check
    if "{{c1::" not in front_field:
        raise ValueError(
            f"Could not find the word '{clean_word}' inside the sentence. Cloze creation failed."
        )

    note = {
        "deckName": anki_config.deck,
        "modelName": anki_config.card_model,
        "fields": {
            f"{anki_config.front_field_name}": front_field,
            f"{anki_config.back_field_name}": translated_sentence,
            f"{anki_config.extra_field_name}": "",
        },
        "tags": anki_config.tags,
    }
    if is_duplicate_note(anki_config.url, note) and not anki_config.allow_duplicates:
        raise DuplicateNoteError(f"a note for '{clean_word}' already exists")

    invoke(anki_config.url, "addNote", note=note)
    return True
