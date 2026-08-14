# Handles the JSON formatting and AnkiConnect requests
# creates payload
#

import requests


def make_cloze(
    original_sentence, translated_sentence, original_word, translated_word, config
):
    """
    makes a cloze flashcard and sends it to anki through AnkiConnect
    based on language and packet
    """
    # PARAMS
    deckname = config["default_deck"]
    modelname = config["cloze_modelname"]
    url = config["url"]

    # CARD FIELDS
    cloze_field = f"{{c1::{original_word}::{translated_word}}}"
    front_field = original_sentence.replace("original_word", cloze_field)

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deckname,
                "modelName": modelname,
                "fields": {
                    "front": front_field,
                    "translation": translated_sentence,
                    "additional notes": "",
                },
            }
        },
    }

    # REQUEST
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to Anki: {e}"
