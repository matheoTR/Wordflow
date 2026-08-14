# The orchestration logic (e.g., the Cloze waiting loop)

from clipboard import get_text
from translator import translate
from notifications import send_notification
from time import sleep
from anki_flashcard import make_cloze

def translate_workflow(config):
    """translates a word or sentence and outputs it in a notification"""

    native_language = config["native_language"]
    original_text = get_text()
    translated_text = translate(original_text, native_language=native_language)
    send_notification("Translation: ", translated_text)


def cloze_workflow(config):
    """creates an anki cloze flashcard"""

    original_sentence = get_text()
    send_notification("cloze waiting...", "highlight a word to create a cloze flashcard")
    original_word = get_text()
    for _ in range ( 10 ):
        if original_word == original_sentence:
            original_word = get_text()
            sleep(1)
        else:
            break
    translated_sentence = translate(original_sentence, native_language=config["native_language"])
    translated_word = translate(original_word, native_language=config["native_language"])
    res = make_cloze(original_sentence, translated_sentence, original_word, translated_word, config)
