import base64
import requests


class AudioError(Exception):
    """Custom exception raised when TTS generation fails."""

    pass


def get_audio(text: str, language: str, accent: str = ""):
    """
    Fetches TTS audio directly from Google's widget API.
    Returns a base64 UTF-8 encoded string ready for AnkiConnect.

    :param text: The text to be spoken.
    :param source_language: ISO code (e.g., 'en', 'fr', 'zh').
    :param accent: Optional TLD (e.g., 'co.uk', 'com.au', 'ca') to change the accent.
    """
    text_to_speak = text.strip()
    if not text_to_speak:
        return ""
    # Safety mechanism: Google's TTS endpoint has a strict 200-character limit.
    # Truncate to prevent HTTP 400 Bad Request errors on massive clipboard copies.
    if len(text_to_speak) > 200:
        text_to_speak = text_to_speak[:200]
    # Accent trick
    tld = accent.strip() if accent else "com"
    url = f"https://translate.google.{tld}/translate_tts"
    params = {
        "ie": "UTF-8",
        "q": text_to_speak,
        "tl": language,
        "client": "tw-ob",  # Bypasses the token generator
    }

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()

        audio_bytes = response.content

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return audio_b64

    except requests.RequestException as e:
        raise AudioError(f"Failed to fetch audio from Google TTS: {str(e)}")
