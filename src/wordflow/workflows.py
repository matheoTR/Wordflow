from .clipboard import get_text, ClipboardError, TimeOutError
from .translator import translate, TranslationError
from .notifications import notify
from .anki_flashcard import AnkiConnectError, DuplicateNoteError, make_cloze
from .my_classes import TranslationData, TranslatorConfig, AnkiConfig, GlobalConfig
from .configuration import resolve_anki_config


def translate_workflow(
    global_config: GlobalConfig, translator_config: TranslatorConfig
):
    """translates a word or sentence and outputs it in a clickable notification"""
    try:
        # 1. Get text from primary or clipboad
        text = get_text()
        # 2. Get translation
        translation_data = translate(
            text=text,
            source_language=global_config.source_language,
            target_language=global_config.target_language,
        )
        # 3. Send notification
        notify(
            "Translation: ",
            translation_data.translated_data,
            enable_notifications=global_config.enable_notifications,
            copy_output_to_clipboard=True,
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
    raw_anki_data: dict,
):
    """creates an anki cloze flashcard from clipboard, automatically detecting correct language settings"""
    try:
        # 1. Get sentence
        original_sentence = get_text()

        # 2. Get word to cloze
        notify(
            "Cloze waiting...",
            "highlight the word to cloze",
            enable_notifications=global_config.enable_notifications,
        )
        word_to_cloze = get_text(original_sentence)

        # 3. Translate sentence and word
        sentence_translation_data = translate(
            text=original_sentence,
            source_language=global_config.source_language,
            target_language=global_config.target_language,
        )
        word_translation_data = translate(
            text=word_to_cloze,
            source_language=sentence_translation_data.source_language,
            target_language=global_config.target_language,
        )

        # 4. Resolve anki config to match detected language (or override)
        resolved_anki_config = resolve_anki_config(
            raw_anki_data, sentence_translation_data.source_language
        )
        #
        # 5. Make the cloze card and send it to anki
        make_cloze(
            anki_config=resolved_anki_config,
            sentence_data=sentence_translation_data,
            word_data=word_translation_data,
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
    except TimeOutError:
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
