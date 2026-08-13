# The orchestration logic (e.g., the Cloze waiting loop)

# Cloze:
# call clipboard to get content
# send notif to ask for a second highlight (while clipboard same)
# call translator with both word and sentence
# pass the result to anki.py
# send success/failure

from clipboard import get_text
from translator import translate
from notifications import send_notification


def translate_workflow(config):
    """translates a word or sentence and outputs it in a notification"""

    native_language = config["native_language"]
    original_text = get_text()
    translated_text = translate(original_text, native_language=native_language)
    send_notification("Translation: ", translated_text)


def cloze_workflow(config):
    """creates an anki cloze flashcard"""
