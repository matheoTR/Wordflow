# Handles calling 'trans' or other dictionary APIs
# 1. takes a string and passes it to trans or another
# 2. returns a clean object

"""
# input: current selection OR clipboard
HANZI=$(wl-paste -p || wl-paste)
# translates from chinese to english
PINYIN=$(trans zh:en "$HANZI" | awk -F '[()]' '{print $2}' | xargs)
ENGLISH=$(trans zh:en -brief "$HANZI" | xargs)
# combines them
COMBINED=$(printf "<b>%s</b>\n<i>%s</i>" "$PINYIN" "$ENGLISH")
# sends a notification
notify-send "$HANZI" "$COMBINED" -t 10000
"""

import deep_translator


class TranslationError(Exception):
    """Custom exception raised when translation fails to prevent bad Anki cards."""

    pass


FREE_TRANSLATORS = [
    "GoogleTranslator",
    "MyMemoryTranslator",
    "LingueeTranslator",
    "PonsTranslator",
]

API_KEY_TRANSLATORS = [
    "DeeplTranslator",
    "ChatGptTranslator",
    "MicrosoftTranslator",
    "YandexTranslator",
    "QcriTranslator",
]


def translate(
    original_text: str,
    native_language: str = "en",
    translator_name: str = "GoogleTranslator",
    apikey: str = "",
) -> str:
    """
    takes text in any language and translates it into native_language
    """
    text_to_translate = original_text.strip()
    if not text_to_translate:
        raise TranslationError("No text was provided for translation.")

    # dynamically fetch the correct translator
    if (
        not hasattr(deep_translator, translator_name)
        or translator_name == "PapagoTranslator"
    ):
        raise TranslationError(f"Translator '{translator_name}' is not recognized.")

    TranslatorClass = getattr(deep_translator, translator_name)

    try:
        if translator_name in API_KEY_TRANSLATORS:
            if not apikey:
                raise TranslationError(
                    f"'{translator_name}' requires an API key, but none is set in your config."
                )
            translator_instance = TranslatorClass(
                api_key=apikey, source="auto", target=native_language
            )
        else:
            translator_instance = TranslatorClass(source="auto", target=native_language)

        translated_text = translator_instance.translate(text_to_translate)
        if not translated_text:
            raise TranslationError("The translation API returned an empty response.")

        return translated_text

    except Exception as e:
        # Catch network timeouts, rate limits, or unsupported languages
        raise TranslationError(f"Failed to translate using {translator_name}: {str(e)}")
