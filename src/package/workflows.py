from time import sleep

from clipboard import get_text, ClipboardError
from package import translator
from translator import translate, TranslationError
from notifications import send_notification
from anki_flashcard import make_cloze, AnkiConfig


def translate_workflow(config: dict):
    """translates a word or sentence and outputs it in a notification"""
    try:
        native_language = config.get("native_language", "en")
        translator = config.get("translator", "GoogleTranslator")
        api_key = config.get("api_key", "")
        api_base_url = config.get("api_base_url", "")
        engine_model = config.get("engine_model", "")

        original_text = get_text()
        translated_text = translate(
            original_text,
            native_language=native_language,
            translator_name=translator,
            api_key=api_key,
            api_base_url=api_base_url,
            engine_model=engine_model,
        )

        send_notification("Translation: ", translated_text)
    except ClipboardError as e:
        send_notification("Clipboard Error", str(e), urgency="critical")
    except TranslationError as e:
        send_notification("Translation Failed", str(e), urgency="critical")
    except Exception as e:
        send_notification("Unexpected Error", str(e), urgency="critical")


def cloze_workflow(config: dict):
    """creates an anki cloze flashcard"""
    try:
        native_language = config.get("native_language", "en")
        translator = config.get("translator", "GoogleTranslator")
        api_key = config.get("api_key", "")
        api_base_url = config.get("api_base_url", "")
        engine_model = config.get("engine_model", "")

        original_sentence = get_text()
        send_notification(
            "cloze waiting...", "highlight a word to create a cloze flashcard"
        )
        original_word = original_sentence
        timeout_reached = True
        for _ in range(10):
            try:
                current_highlight = get_text()
            except ClipboardError:
                current_highlight = original_sentence

            if current_highlight != original_sentence:
                original_word = current_highlight
                timeout_reached = False
                break
            else:
                sleep(1)

        if timeout_reached:
            send_notification("Cloze Cancelled", "No new word was highlighted in time.")
            return

        translated_sentence = translate(
            original_sentence,
            native_language=native_language,
            translator_name=translator,
            api_key=api_key,
            api_base_url=api_base_url,
            engine_model=engine_model,
        )
        translated_word = translate(
            original_word,
            native_language=native_language,
            translator_name=translator,
            api_key=api_key,
            api_base_url=api_base_url,
            engine_model=engine_model,
        )
        anki_params = AnkiConfig
        anki_params.deck = config.get("deck", "Wordpipe")
        anki_params.card_model = config.get("card_model", "Wordpipe Cloze")
        anki_params.url = config.get("url", "http://localhost:8765")
        anki_params.tags = config.get("tags", "")

        res = make_cloze(
            original_sentence,
            translated_sentence,
            original_word,
            translated_word,
            anki_params,
        )
        # Notify success
        send_notification("Anki Success", f"Cloze card created for: '{original_word}'")

    except ClipboardError as e:
        send_notification("Clipboard Error", str(e), urgency="critical")
    except TranslationError as e:
        send_notification("Translation Failed", str(e), urgency="critical")
    except Exception as e:
        send_notification("Anki Error", str(e), urgency="critical")
