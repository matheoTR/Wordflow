from time import sleep

from .clipboard import get_text, ClipboardError
from .translator import translate, TranslationError
from .notifications import notify
from .anki_flashcard import make_cloze
from .my_classes import TranslatorConfig, AnkiConfig, GlobalConfig


def translate_workflow(
    translator_config: TranslatorConfig, global_config: GlobalConfig
):
    """translates a word or sentence and outputs it in a notification"""
    try:
        # 1. Get text from primary or clipboad
        original_text = get_text()
        # 2. Get translation
        translated_text = translate(
            original_text=original_text,
            target_language=global_config.target_language,
            translator_name=translator_config.translator,
            api_key=translator_config.api_key,
            api_base_url=translator_config.api_base_url,
            engine_model=translator_config.engine_model,
        )
        # 3. Send notification
        notify(
            "Translation: ",
            translated_text,
            enable_notifications=global_config.enable_notifications,
        )

    except ClipboardError as e:
        notify(
            "Clipboard Error",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except TranslationError as e:
        notify(
            "Translation Failed",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except Exception as e:
        notify(
            "Unexpected Error",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )


def cloze_workflow(
    translator_config: TranslatorConfig,
    anki_config: AnkiConfig,
    global_config: GlobalConfig,
):
    """creates an anki cloze flashcard"""
    try:
        # 1. Get text from primary | clipboad
        original_sentence = get_text()
        notify(
            "cloze waiting...",
            "highlight a word to create a cloze flashcard",
            enable_notifications=global_config.enable_notifications,
        )
        # 2. Get cloze target
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
            notify(
                "Cloze Cancelled",
                "No new word was highlighted in time.",
                enable_notifications=global_config.enable_notifications,
            )
            return

        # 3. Translate sentence and word
        translated_sentence = translate(
            original_text=original_sentence,
            target_language=global_config.target_language,
            translator_name=translator_config.translator,
            api_key=translator_config.api_key,
            api_base_url=translator_config.api_base_url,
            engine_model=translator_config.engine_model,
        )
        translated_word = translate(
            original_text=original_word,
            target_language=global_config.target_language,
            translator_name=translator_config.translator,
            api_key=translator_config.api_key,
            api_base_url=translator_config.api_base_url,
            engine_model=translator_config.engine_model,
        )
        # DEBUG:
        # notify("DEBUG sentence:", original_sentence)
        # notify("DEBUG original_word: ", original_word)
        # notify("DEBUG translated_sentence: ", translated_sentence)
        # notify("DEBUG translated_word: ", translated_word)
        #
        # 4. Make the cloze card and send it to anki
        res = make_cloze(
            original_sentence=original_sentence,
            translated_sentence=translated_sentence,
            original_word=original_word,
            translated_word=translated_word,
            anki_config=anki_config,
        )
        # 5. Notify success
        notify(
            "Anki Success",
            f"Cloze card created for: '{original_word}'",
            enable_notifications=global_config.enable_notifications,
        )

    except ClipboardError as e:
        notify(
            "Clipboard Error",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except TranslationError as e:
        notify(
            "Translation Failed",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except Exception as e:
        notify(
            "Anki Error",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
