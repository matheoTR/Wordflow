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

from deep_translator import GoogleTranslator


def translate(text: str, native_language="en") -> str:
    """
    takes text in any language and translates it into native_language
    """
    try:
        translated = GoogleTranslator(source="auto", target=native_language).translate(
            text
        )
        return translated
    except Exception as e:
        return f"translation error: {e}"
