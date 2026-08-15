# Handles the JSON formatting and AnkiConnect requests
# creates payload
#

import requests
from dataclasses import dataclass


@dataclass
class AnkiConfig:
    url: str = "http://localhost:8765"
    deck: str = "Default"
    card_model: str = "Wordpipe Cloze"
    tags: list[str] = None


class AnkiConnectError(Exception):
    """raised if failure to connect to Anki through AnkiConnect"""

    pass


def invoke(url: str, action: str, **params):
    """
    Standard helper to send actions to AnkiConnect and handle its specific error format.
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


def setup_anki_model(url: str, modelname: str):
    """
    Checks if the required Cloze model exists. If not, it creates it
    with the exact fields and dark-mode styling needed.
    """
    existing_models = invoke(url, "modelNames")

    # if wordpipe cloze model does not exist, we create it
    if modelname not in existing_models:
        css = """
        .card { font-family: arial; font-size: 20px; text-align: center; color: white; background-color: #282a36; }
        .cloze { font-weight: bold; color: #ffb86c; }
        #answer { border-top: 1px solid #6272a4; margin-top: 15px; padding-top: 15px; }
        """

        invoke(
            url,
            "createModel",
            modelName=modelname,
            inOrderFields=["front", "translation", "additional notes"],
            isCloze=True,
            css=css,
            cardTemplates=[
                {
                    "Name": "wordpipe cloze",
                    "Front": "{{cloze:front}}",
                    "Back": "{{cloze:front}}<div id=answer>{{translation}}<br><br>{{additional notes}}</div>",
                }
            ],
        )


def make_cloze(
    original_sentence,
    translated_sentence,
    original_word,
    translated_word,
    params: AnkiConfig,
):
    """
    makes a cloze flashcard and sends it to anki through AnkiConnect
    based on language and packet
    """
    # check environment (card type, deck)
    setup_anki_model(params.url, params.card_model)
    invoke(params.url, "createDeck", deck=params.deck)

    # CARD FIELDS
    cloze_field = f"{{{{c1::{original_word}::{translated_word}}}}}"
    front_field = original_sentence.replace(original_word, cloze_field)

    note = {
        "deckName": params.deck,
        "modelName": params.card_model,
        "fields": {
            "front": front_field,
            "translation": translated_sentence,
            "additional notes": "",
        },
        "tags": params.tags,
    }
    invoke(params.url, "addNote", note=note)
