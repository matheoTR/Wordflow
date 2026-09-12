$$\      $$\                           $$\       $$$$$$$$\ $$\                         
$$ | $\  $$ |                          $$ |      $$  _____|$$ |                        
$$ |$$$\ $$ | $$$$$$\   $$$$$$\   $$$$$$$ |      $$ |      $$ | $$$$$$\  $$\  $$\  $$\ 
$$ $$ $$\$$ |$$  __$$\ $$  __$$\ $$  __$$ |      $$$$$\    $$ |$$  __$$\ $$ | $$ | $$ |
$$$$  _$$$$ |$$ /  $$ |$$ |  \__|$$ /  $$ |      $$  __|   $$ |$$ /  $$ |$$ | $$ | $$ |
$$$  / \$$$ |$$ |  $$ |$$ |      $$ |  $$ |      $$ |      $$ |$$ |  $$ |$$ | $$ | $$ |
$$  /   \$$ |\$$$$$$  |$$ |      \$$$$$$$ |      $$ |      $$ |\$$$$$$  |\$$$$$\$$$$  |
\__/     \__| \______/ \__|       \_______|      \__|      \__| \______/  \_____\____/ 

# Wordflow

A lightning-fast, dependency-free, keyboard-driven language acquisition tool for Linux.

Wordflow bridges your system clipboard, Google's internal translation APIs, Text-To-Speech, and Anki into a single seamless workflow. By simply highlighting text and pressing a shortcut, you can instantly translate sentences or dynamically generate Anki flashcards without ever leaving your browser, book, or current window.
# ✨ Features

    Zero-Dependency Translation: Directly hooks into Google's native API endpoints for instantaneous, rate-limit-resistant translations without relying on web scrapers.

    Rich Dictionary Data: Automatically fetches synonyms, monolingual definitions, alternate translations, and curated example sentences for single words.

    Phonetics & Romanization: Natively captures pronunciations like Pinyin for Chinese or Romaji for Japanese.

    Dual Audio Generation: Generates native MP3 audio for both the isolated word and the full sentence, directly embedded into your flashcards.

    Infinite Layout Flexibility: Map any piece of fetched data to any field on your Anki cards using a highly intuitive placeholder configuration system.

# ⚠️ Limitations & Scope

    Linux Only: Wordflow is built specifically for Linux environments (X11/Wayland).

    Internet Required: Translations and audio generation rely on live online APIs.

# 🛠 Prerequisites

    Python 3.10+

    Clipboard Manager: xclip (X11) or wl-clipboard (Wayland) must be installed.

    Anki Desktop: Must be installed and running in the background.

    AnkiConnect: You must install the AnkiConnect add-on to allow Wordflow to communicate with Anki.

# Installing AnkiConnect

    Open Anki.

    Go to Tools -> Add-ons -> Get Add-ons...

    Paste the AnkiConnect code: 2055492159

    Restart Anki.

# 🚀 Installation
## 1. Via pipx (Recommended)
### a) Install directly from Github
    pipx install wordflow-cli
### b) Clone and install locally
    git clone [https://github.com/matheoTR/Wordflow.git](https://github.com/matheoTR/Wordflow.git)
    cd Wordflow
    pipx install .
## 2. Via git and makepkg (Arch build)
  If you prefer building from the versioned source using a PKGBUILD, you can clone the repository and run makepkg. It will then be managed by pacman.

    git clone https://github.com/matheoTR/Wordflow.git
    cd Wordflow
    makepkg -si

## 3. Via Package Managers (apt, pacman, dnf)
  Not yet available.

# ⚙️ Configuration
  Run the initialization wizard to generate your default configuration:

    wordflow --wizard

  This guides you through setting up your default Anki deck and creates your configuration file at ~/.config/wordflow/config.toml.
  ## Field Mappings & Placeholders

  Wordflow's true power lies in its dynamic field mappings. In your config.toml, you map Anki note fields (left) to Wordflow's data placeholders (right). You can combine multiple placeholders and inject custom HTML. Missing or empty data is gracefully ignored by Anki.

### Available Placeholders:

    {cloze} - The sentence with the {{c1::word}} deletion and optional dictionary hyperlink.

    {translation} - The translation of the full sentence.

    {source_word} - The isolated highlighted word.

    {word_audio} - Audio play button for the isolated word.

    {sentence_audio} - Audio play button for the full sentence.

    {sentence_phonetic} - Phonetics/Romanization of the sentence.

    {word_phonetic} - Phonetics/Romanization of the word.

    {alternates} - Alternative translation variations.

    {definitions} - Monolingual dictionary definitions.

    {synonyms} - Synonyms of the target word.

    {examples} - Example sentences using the word.

### Configuration Example
    Ini, TOML

    [anki.default.fields]
    "Front" = "{cloze}"
    "Back" = "{translation}"
    "Audio" = "{word_audio} &nbsp;&nbsp;&nbsp; {sentence_audio}"
    "Phonetics" = "{word_phonetic} &nbsp;&nbsp;&nbsp; {sentence_phonetic}"
    "Definitions" = "{definitions}"
    "Synonyms" = "{synonyms}"
    "Alternates" = "{alternates}"
    "Examples" = "{examples}"

## Language-Specific Overrides

  You can manually edit config.toml to route different languages to different Anki decks, models, and dictionaries. Wordflow automatically detects the language of your highlighted text and applies the correct settings.

    Override for Chinese (-l zh-cn)
    [anki.zh-cn]
    deck = "Languages::Chinese"
    card_model = "Chinese Hanzi Cloze"
    dict_url = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={word}"

    [anki.zh-cn.fields]
    "Hanzi" = "{cloze}"
    "Translation" = "{translation}"
    "Pinyin" = "{word_phonetic} {sentence_phonetic}"

## Text-To-Speech Accents

Wordflow automatically routes audio to native speakers of the detected language. You can customize the accent for pluricentric languages (like English or Spanish) by changing the optional audio_accent setting to match a regional Top-Level Domain (TLD). This setting does not work for all languages.
### example
    [anki.es]
    # Generates Mexican Spanish audio instead of Castilian Spanish
    audio_accent = "com.mx" 

# 🖱️ Usage
## Instant Translation (-t)

  Highlight any text on your screen and trigger the wordflow --translate command. Wordflow detects the language, translates it, and sends a desktop notification. Clicking the notification copies the translation to your clipboard.
## Cloze Card Creation (-c)

  To create a flashcard, highlight the target word/sentence and trigger wordflow --cloze. Wordflow will parse all dictionary data, build the card according to your TOML layout, and push it directly to Anki.

Use wordflow --help to list all command-line arguments.

# ⌨️ Creating Shortcuts

Wordflow is designed to be bound to your window manager's shortcuts, allowing you to seamlessly translate and capture vocabulary without losing focus on your current task.
## Hyprland Example (Submap)
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

## Sway / i3 Example
    bindsym Mod4+t exec "wordflow -t"
    bindsym Mod4+c exec "wordflow -c"
