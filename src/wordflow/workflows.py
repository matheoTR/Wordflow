from .clipboard import get_text, ClipboardError, TimeOutError
from .translator import translate, TranslationError
from .notifications import notify
from .anki_flashcard import AnkiConnectError, DuplicateNoteError, make_cloze
from .my_classes import TranslatorConfig, AnkiConfig, GlobalConfig
from .configuration import resolve_anki_config


def translate_workflow(
    global_config: GlobalConfig, translator_config: TranslatorConfig
):
    """translates a word or sentence and outputs it in a notification"""
    try:
        # 1. Get text from primary or clipboad
        original_text = get_text()
        # 2. Get translation
        translated_text, _ = translate(
            original_text=original_text,
            source_language=global_config.source_language,
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
    except TimeOutError as e:
        notify(
            "Timeout Error",
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
    global_config: GlobalConfig,
    translator_config: TranslatorConfig,
    raw_anki_data: dict,
):
    """creates an anki cloze flashcard from clipboard, automatically detecting correct language settings"""
    try:
        # 1. Get sentence
        # notify(
        #     "(1/2) cloze waiting...",
        #     "highlight a sentence",
        #     enable_notifications=global_config.enable_notifications,
        # )
        original_sentence = get_text()

        # 2. Get word to cloze
        notify(
            "Cloze waiting...",
            "highlight the word to cloze",
            enable_notifications=global_config.enable_notifications,
        )
        word_to_cloze = get_text(original_sentence)

        # 3. Translate sentence and word
        translated_sentence, detected_source_language = translate(
            original_text=original_sentence,
            source_language=global_config.source_language,
            target_language=global_config.target_language,
            translator_name=translator_config.translator,
            api_key=translator_config.api_key,
            api_base_url=translator_config.api_base_url,
            engine_model=translator_config.engine_model,
        )
        # translates word using previously detected language if not specified
        translated_word, _ = translate(
            original_text=word_to_cloze,
            source_language=detected_source_language,
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

        # 4. Resolve anki config to match detected language (or override)
        resolved_anki_config = resolve_anki_config(
            raw_anki_data, detected_source_language
        )
        # 5. Make the cloze card and send it to anki
        res = make_cloze(
            original_sentence=original_sentence,
            translated_sentence=translated_sentence,
            original_word=word_to_cloze,
            translated_word=translated_word,
            anki_config=resolved_anki_config,
            source_language=detected_source_language,
            target_language=global_config.target_language,
        )
        # 5. Notify success
        notify(
            "Anki Success",
            f"Cloze card created for: '{word_to_cloze}' in {resolved_anki_config.deck}",
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
    except DuplicateNoteError as e:
        notify(
            "Card Duplicate",
            str(e),
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except TimeOutError as e:
        notify(
            "Timeout Error",
            "Cancelling cloze creation.",
            urgency="critical",
            enable_notifications=global_config.enable_notifications,
        )
    except AnkiConnectError as e:
        notify(
            "Anki Error",
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
