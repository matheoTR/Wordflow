# Wordflow

A lightning-fast, keyboard-driven language acquisition tool for Linux. 

Wordflow bridges your system clipboard, translation APIs, Text-To-Speech and Anki into a single workflow. By simply highlighting text and pressing a shortcut, you can instantly translate sentences or dynamically generate cloze Anki flashcards without ever leaving your browser, book, or current window. It is also possible to easily copy a translation to clipboard, and to add automatically generated audio to your cards.

## ⚠️ Limitations & Scope
Before installing, please note the intentional scope of this project:
* **Linux Only:** Wordflow is built specifically for Linux environments
* **Cloze Cards Only:** This tool *only* generates Cloze deletion cards. It does not support Basic (Front/Back) cards, synonym mapping, or reverse cards.
* **Fixed Format:** Cards are automatically generated with a strict structure: the clozed word, the full context sentence, the translation, and an optional clickable hyperlink to an online dictionary.
* **No Offline Dictionaries:** Translations rely on online APIs (e.g., Google Translate, DeepL, MyMemory).

## 🛠 Prerequisites
1. **Python 3.10+**
2. **X11/Wayland Clipboard:** `xclip` or `wl-clipboard` must be installed on your system.
3. **Anki Desktop:** Must be installed and running in the background.
4. **AnkiConnect:** You must install the AnkiConnect add-on to allow Wordflow to talk to Anki: https://ankiweb.net/shared/info/2055492159

### Installing AnkiConnect
1. Open Anki.
2. Go to **Tools** -> **Add-ons** -> **Get Add-ons...**
3. Paste the AnkiConnect code: `2055492159`
4. Restart Anki. *(Note: Anki must remain open in the background whenever you use Wordflow).*

## 🚀 Installation
The recommended way to install Wordflow on Linux is using `pipx`, which installs the tool globally while keeping its Python dependencies safely isolated.
```bash
# Install pipx if you haven't already
sudo pacman -S python-pipx   # Arch
sudo apt install pipx        # Debian/Ubuntu

# Install Wordflow
pipx install wordflow
```
(If installing from a local cloned repository, navigate to the folder and run `pipx install .`)
## Configuration
Wordflow comes with a built-in interactive wizard to help you generate your configuration file.
Run the initialization wizard: `wordflow --init`
This will guide you through setting up your preferred translation engine and default Anki deck, saving the results to ~/.config/wordflow/config.toml.
### Language-Specific Overrides
You can manually edit config.toml to route different languages to different Anki decks and dictionaries. Wordflow automatically detects the language of your highlighted text and applies the correct settings.
#### Example
  [anki.zh-cn]
  deck = "Languages::Chinese"
  card_model = "Chinese Hanzi Cloze"
  field_names = ["Hanzi", "Pinyin", "Stroke_Order"]
  dict_url = "[https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=](https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb=){word}"
### Text-To-Speech (TTS)
When `audio_mode` is enabled, Wordflow generates speech using Google's neural TTS engine. By default, it uses standard regional accents, but you can customize this by changing the optional `audio_accent` setting.
The setting corresponds to the Google domain extension for the region you want to target (e.g., `google.co.uk` becomes `co.uk`). Please refer to https://gtts.readthedocs.io/en/latest/module.html#localized-accents for more info
#### Example
  [anki.en]
  audio_mode = "word"
  audio_accent = "co.uk"   # Will read English words with a British accent
## Usage
### 1. Instant Translation (-t)
Highlight any text on your screen and then trigger the `wordflow --translate` command. Wordflow will detect the language, translate it, and send a desktop notification.
Clicking the notification will also copy the translation, making it easy to copy paste.
### 2. Cloze Card Creation (-c)
To create a flashcard, highlight the target word/sentence and trigger the `wordflow --cloze` command. Wordflow will automatically build the card and push it to Anki.
### Other
use `wordflow --help` to list all functionalities

## Creating Shortcuts
This tool really shines if you bind shortcuts to call it. Then you can seamlessly translate and create flashcards from any text without needing to open other windows.
### Hyprland example (submap)
    hl.bind(mod .. " + C", hl.dsp.submap("wordflow")) -- wordflow

    hl.define_submap("wordflow", function()
      --t : Translate
      hl.bind("T", function()
        hl.dispatch(hl.dsp.submap("reset"))
        hl.dispatch(hl.dsp.exec_cmd("wordflow -t"))
      end)
      --c : Cloze
      hl.bind("C", function()
        hl.dispatch(hl.dsp.submap("reset"))
        hl.dispatch(hl.dsp.exec_cmd("wordflow -c"))
      end)

      hl.bind("catchall", hl.dsp.submap("reset"))
    end)
### Sway /i3 example
    bindsym Mod4+t exec "wordflow -t"
    bindsym Mod4+c exec "wordflow -c"
