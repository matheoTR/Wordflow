import deep_translator
import inspect


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
    translator_name: str = "GoogleTranslator",
    native_language: str = "en",
    api_key: str = "",
    api_base_url: str = "",
    engine_model: str = "",
) -> str:
    """
    Takes text in any language and translates it into native_language,
    supporting optional API keys, base URLs, and engine models.
    """
    text_to_translate = original_text.strip()
    if not text_to_translate:
        raise TranslationError("No text was provided for translation.")

    if (
        not hasattr(deep_translator, translator_name)
        or translator_name == "PapagoTranslator"
    ):
        raise TranslationError(
            f"Translator '{translator_name}' is not recognized. please check manual or config file for full list of supported translators"
        )

    TranslatorClass = getattr(deep_translator, translator_name)

    try:
        if translator_name in API_KEY_TRANSLATORS and not api_key:
            raise TranslationError(
                f"'{translator_name}' requires an API key, but none is set in your config."
            )

        init_args = {"source": "auto", "target": native_language}

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

        return translated_text

    except Exception as e:
        if isinstance(e, TranslationError):
            raise e
        raise TranslationError(f"Failed to translate using {translator_name}: {str(e)}")
