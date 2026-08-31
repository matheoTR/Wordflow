import deep_translator
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import inspect
from .constants import SUPPORTED_TRANSLATORS, FREE_TRANSLATORS, API_KEY_TRANSLATORS


class TranslationError(Exception):
    """Custom exception raised when translation fails to prevent bad Anki cards."""

    pass


DetectorFactory.seed = 0


def adapt_lang_code(lang_code: str, translator_name: str) -> str:
    """
    Adapts standard ISO codes to engine-specific formats.
    """
    code = lang_code.lower()

    # 1. Exact string overrides for specific language + engine pairings
    exceptions = {
        "zh-cn": {
            "GoogleTranslator": "zh-CN",
            "MyMemoryTranslator": "zh-CN",
            "DeeplTranslator": "ZH",
        },
        "zh-tw": {
            "GoogleTranslator": "zh-TW",
            "MyMemoryTranslator": "zh-TW",
            "DeeplTranslator": "ZH",
        },
        "yue": {
            "GoogleTranslator": "zh-TW",
            "MyMemoryTranslator": "zh-TW",
        },
        "en": {
            "DeeplTranslator": "EN-US",
        },
        "pt": {
            "DeeplTranslator": "PT-PT",
        },
    }

    # Resolve mapping if an exception exists
    # 95% of languages work as is and will skip this
    if code in exceptions and translator_name in exceptions[code]:
        adapted_code = exceptions[code][translator_name]
    else:
        adapted_code = code

    # Engine-wide formatting quirks
    if translator_name == "DeeplTranslator":
        return adapted_code.upper()

    return adapted_code


def translate(
    original_text: str,
    source_language: str = "auto",
    target_language: str = "en",
    translator_name: str = "GoogleTranslator",
    api_key: str = "",
    api_base_url: str = "",
    engine_model: str = "",
):
    """
    Takes text in any language and translates it into target_language,
    supporting optional API keys, base URLs, and engine models.
    Returns : translated text, detected source language
    """
    text_to_translate = original_text.strip()
    if not text_to_translate:
        raise TranslationError("No text was provided for translation.")

    if translator_name not in SUPPORTED_TRANSLATORS:
        raise TranslationError(
            f"Translator '{translator_name}' is not supported. "
            f"Supported engines: {', '.join(SUPPORTED_TRANSLATORS)}"
        )

    TranslatorClass = getattr(deep_translator, translator_name)

    # resolve source language for anki
    if source_language == "auto":
        try:
            anki_source = detect(text_to_translate)
            # --- Afrikaans/Dutch Overlap Fix ---
            if anki_source == "af":
                anki_source = "nl"
        except LangDetectException:
            # Fallback
            anki_source = "unknown"
        api_source = "auto"
    else:
        anki_source = source_language
        api_source = source_language

    # DEBUG
    print("detected language: ", anki_source)
    try:
        if translator_name in API_KEY_TRANSLATORS and not api_key:
            raise TranslationError(
                f"'{translator_name}' requires an API key, but none is set in your config."
            )

        # formatting for the translator
        api_source_formatted = adapt_lang_code(api_source, translator_name)
        api_target_formatted = adapt_lang_code(target_language, translator_name)
        # DEBUG
        print("api source formatted: ", api_source_formatted)
        init_args = {"source": api_source_formatted, "target": api_target_formatted}

        if api_key:
            init_args["api_key"] = api_key
        if api_base_url:
            init_args["base_url"] = api_base_url
            init_args["api_base_url"] = api_base_url
        if engine_model:
            init_args["model"] = engine_model
            init_args["engine_model"] = engine_model

        # filter arguments to match what the specific translator class accepts
        try:
            sig = inspect.signature(TranslatorClass.__init__)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            if not has_var_keyword:
                init_args = {k: v for k, v in init_args.items() if k in sig.parameters}
        except (ValueError, TypeError):
            pass

        translator_instance = TranslatorClass(**init_args)

        translated_text = translator_instance.translate(text_to_translate)
        if not translated_text:
            raise TranslationError("The translation API returned an empty response.")

        return translated_text, anki_source

    except Exception as e:
        if isinstance(e, TranslationError):
            raise e
        raise TranslationError(f"Failed to translate using {translator_name}: {str(e)}")
