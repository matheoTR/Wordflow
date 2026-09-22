import requests
from time import sleep

from wordflow.my_classes import TranslationData


class TranslationError(Exception):
    """Custom exception raised when translation fails to prevent bad Anki cards."""

    pass


def normalize_lang_code(google_code: str) -> str:
    """Converts Google's legacy or dialect-specific codes into ISO 639-1."""
    if not google_code:
        return ""

    code = google_code.lower()

    legacy_map = {
        "iw": "he",  # Hebrew
        "in": "id",  # Indonesian
        "jw": "jv",  # Javanese
        "ji": "yi",  # Yiddish
    }
    if code in legacy_map:
        return legacy_map[code]

    if code in ["zh-cn", "zh-tw"]:
        return code

    # 2. Strip regional subtags (e.g., 'zh-cn' -> 'zh', 'en-us' -> 'en')
    if "-" in code:
        code = code.split("-")[0]

    return code


def translate(
    text: str,
    source_language: str = "auto",
    target_language: str = "en",
    max_retries: int = 3,
) -> TranslationData:
    """
    Takes text in any language and translates it into target_language.
    Returns a dictionnary containing the translation, source language used, and additional info in case of singe word translation: pronounciation, alternate translations, definition, synonyms, examples
    """
    text_to_translate = text.strip()
    if not text_to_translate:
        raise TranslationError("No text was provided for translation.")

    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",  # The magical bypass client
        "sl": source_language,  # (auto is supported)
        "tl": target_language,
        "q": text,  # The text to translate
        "dt": [
            "t",
            "bd",
            "rm",
            "md",
            "ss",
            "ex",
        ],  # Request the "translation", pronounciation, alternate translations, definition, synonyms, and examples
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    last_error = None

    for _ in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            # FAIL FAST: If Google rate-limits, abort instantly to avoid extending the ban.
            if response.status_code == 429:
                raise TranslationError(
                    "Google temporarily rate-limited your IP (HTTP 429). Please wait a few minutes."
                )
            # other errors
            response.raise_for_status()

            data = parse_translation_data(response.json())
            translation_data = TranslationData(
                source_data=text,
                translated_data=data["translation"],
                source_language=data["source_language"],
                target_language=target_language,
                phonetic=data.get("phonetic"),
                alternate_translations=data.get("alternates", ""),
                synonyms=data.get("synonyms"),
                definitions=data.get("definitions"),
                examples=data.get("examples"),
            )
            # DEBUG
            # print("json data: ", response.json())
            # print("translation data: ", translation_data)
            return translation_data

        except requests.RequestException as e:
            last_error = e
            sleep(1)  # wait ane retry

    raise TranslationError(f"Failed to translate. Last error: {last_error}")


def parse_translation_data(data) -> dict:
    # parse TRANSLATION
    translation = "".join([sentence[0] for sentence in data[0] if sentence[0]])
    # parse PHONETIC
    phonetic = ""
    for item in data[0]:
        # Romanizations are placed in the 3rd index of a specific sub-array
        if len(item) > 3 and item[3]:
            phonetic = item[3]
            break
    # 3. parse DICTIONARY (Alternate translations)
    # data[1] exists if it's a single word and dt=bd was requested
    alternates = []
    if len(data) > 1 and data[1]:
        for pos_group in data[1]:
            # pos_group[0] is the part of speech (e.g., "noun")
            # pos_group[1] is a list of translated words
            if len(pos_group) > 1:
                alternates.extend(pos_group[1])
    # SOURCE LANGUAGE
    detected_source_language = data[2]
    iso_source_language = normalize_lang_code(detected_source_language)

    definitions = []
    synonyms = []
    examples = []
    # 4. parse SYNONYMS
    ## Located at data[11]. Structure: [ ["noun", [ [ ["syn1", "syn2"], "id" ] ] ], ... ]
    if len(data) > 11 and data[11]:
        for pos_group in data[11]:
            if len(pos_group) > 1 and isinstance(pos_group[1], list):
                for entry in pos_group[1]:
                    if (
                        isinstance(entry, list)
                        and len(entry) > 0
                        and isinstance(entry[0], list)
                    ):
                        synonyms.extend(entry[0])

    # 5. parse DEFINITIONS
    # Located at data[12]. Structure: [ ["noun", [ ["definition1", "id", "example"], ... ] ], ... ]
    if len(data) > 12 and data[12]:
        for pos_group in data[12]:
            if len(pos_group) > 1 and isinstance(pos_group[1], list):
                for entry in pos_group[1]:
                    if isinstance(entry, list) and len(entry) > 0:
                        definitions.append(entry[0])

    # 6. parse EXAMPLES
    # Located at data[13]. Structure: [ [ ["example 1 with <b>tags</b>", ...], ... ] ]
    if len(data) > 13 and data[13]:
        if isinstance(data[13], list) and len(data[13]) > 0:
            for ex_group in data[13][0]:
                if isinstance(ex_group, list) and len(ex_group) > 0:
                    examples.append(str(ex_group[0]))
    return {
        "translation": translation,
        "phonetic": phonetic,
        "alternates": list(set(alternates)),
        "definitions": definitions,
        "synonyms": list(set(synonyms)),
        "examples": examples,
        "source_language": iso_source_language,
    }
