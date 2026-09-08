import time
import requests
import re
import urllib.parse

from .text_to_speech import get_audio
from .my_classes import AnkiConfig, TranslationData


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


def setup_anki_model(url: str, model_name: str, field_names: list[str]):
    """
    Checks if the required Cloze model exists. If not, it creates it
    with the exact fields and dark-mode styling needed.
    """
    if not field_names:
        raise ValueError("field_names must contain at least one field for the cloze.")

    existing_models = invoke(url, "modelNames")
    # DEBUG
    # print(existing_models)
    # print(f"Is '{model_name}' in Anki? -> {model_name in existing_models}\n")

    # if wordflow cloze model does not exist, we create it
    if model_name not in existing_models:
        css = """
        .card { font-family: arial; font-size: 20px; text-align: center; color: white; background-color: #282a36; }
        .cloze { font-weight: bold; color: #ffb86c; }
        #answer { border-top: 1px solid #6272a4; margin-top: 15px; padding-top: 15px; }
        """
        # front
        front_anki = f"{{{{cloze:{field_names[0]}}}}}"

        # back
        back_anki_parts = [f'{front_anki}<div id="answer">']
        for field in field_names[1:]:
            # Using Anki conditional rendering
            # This ensures no whitespace is added if the field is left blank.
            back_anki_parts.append(
                f"{{{{#{field}}}}}<br><br>{{{{{{{field}}}}}}}{{{{/{field}}}}}"
            )
        back_anki_parts.append("</div>")
        # we join all parts
        back_anki = "".join(back_anki_parts)

        # DEBUG
        # print("front: ", front_anki)
        # print("trans: ", back_anki)
        # print("notes: ", extra_anki)
        # print("css: ", css)
        # print("front_field_name: ", front_field_name)
        # print("translation_field_name: ", back_field_name)
        # print("additionnal_info_field_name: ", extra_field_name)

        res = invoke(
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
        # DEBUG
        # print(res)


def is_duplicate_note(url: str, note: dict) -> bool:
    """
    Returns True if the note already exists.
    """
    results = invoke(url, "canAddNotes", notes=[note])
    # results is a list of booleans matching the input list
    return not results[0] if results else False


def make_cloze(
    anki_config: AnkiConfig, sentence_data: TranslationData, word_data: TranslationData
):
    """
    makes a cloze flashcard and sends it to anki through AnkiConnect
    """
    # check environment (create card type and deck if non-existing)
    # DEBUG:
    # print("Model name: ", anki_config.card_model)
    setup_anki_model(anki_config.url, anki_config.card_model, anki_config.field_names)
    # make sure deck exists
    invoke(anki_config.url, "createDeck", deck=anki_config.deck)

    # clean trailing spaces
    source_sentence = sentence_data.source_data.strip()
    source_word = word_data.source_data.strip()
    translated_word = word_data.translated_data.strip()

    # CARD FIELDS
    cloze_tag = f"{{{{c1::{source_word}::{translated_word}}}}}"

    # add dictionnary hyperlink
    if anki_config.dict_url:
        # url encode the word
        safe_word = urllib.parse.quote(source_word)
        final_url = anki_config.dict_url.format(
            word=safe_word,
            source_language=word_data.source_language,
            target_language=word_data.target_language,
        )
        cloze_field = f'<a href="{final_url}">{cloze_tag}</a>'
    else:
        cloze_field = cloze_tag

    # DEBUG
    # print(cloze_field)
    # case-insensitive replacement
    pattern = re.compile(re.escape(source_word), re.IGNORECASE)
    front_field = pattern.sub(cloze_field, source_sentence)

    # Cloze card health check
    if "{{c1::" not in front_field:
        raise ValueError(
            f"Could not find the word '{source_word}' inside the sentence. Cloze creation failed."
        )

    # add optional audio
    word_audio_tag = ""
    sentence_audio_tag = ""
    if anki_config.audio_mode in ["word", "both"]:
        word_audio_tag = add_audio_to_anki(
            url=anki_config.url,
            text=source_word,
            lang_code=word_data.source_language,
            accent=anki_config.audio_accent,
        )
    if anki_config.audio_mode in ["sentence", "both"]:
        sentence_audio_tag = add_audio_to_anki(
            url=anki_config.url,
            text=source_sentence,
            lang_code=word_data.source_language,
            accent=anki_config.audio_accent,
        )

    # Create a populate field dictionnary.
    # if user has extra custom fields, they are left blank (but will be passed to ankiconnect)
    back_field_content = sentence_data.translated_data
    if word_audio_tag or sentence_audio_tag:
        back_field_content += "<br><br>"
    if word_audio_tag:
        back_field_content += f"<b>Word:</b> {word_audio_tag} "
    if sentence_audio_tag:
        if word_audio_tag:
            back_field_content += "&nbsp;&nbsp;"  # adds | separator
        back_field_content += f"<b>Sentence:<b>{sentence_audio_tag} "

    fields_dict = {field: "" for field in anki_config.field_names}
    fields_dict[anki_config.field_names[0]] = front_field  # front
    fields_dict[anki_config.field_names[1]] = back_field_content  # back

    # create payload
    note = {
        "deckName": anki_config.deck,
        "modelName": anki_config.card_model,
        "fields": fields_dict,
        "tags": anki_config.tags,
    }
    # check for duplicate
    if is_duplicate_note(anki_config.url, note) and not anki_config.allow_duplicates:
        raise DuplicateNoteError(f"a note for '{source_word}' already exists")

    invoke(anki_config.url, "addNote", note=note)
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
