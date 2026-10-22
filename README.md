# benri
benri is an Anki addon providing quick access to various functionality useful for learning Japanese, such as dictionary lookups, text to speech and text recognition from images through OCR.

# Functionality
This addon adds the following buttons to the Anki Add window:
- benridict
  - Performs a dictionary lookup on the word in the "Expression" field.
  - If multiple matches were found, a dialog box allows the user to pick the best match.
  - Shift+Click allows the user to enter a custom dictionary lookup.
- benritalk
  - Performs TTS on the word in the "Expression" field and saves it to the "Audio" field.
  - Shift+Click allows the user to enter a custom word.
  - Converts the TTS audio files to efficient Opus format.
- benriplay
  - Plays back the audio from the "Audio" field.
- benriocr
  - Performs OCR on a clipboard image and saves the result to the "Expression" field.
  - Can be useful when the user does not know how to type a kanji in a word they want to add.
- benriclear
  - Clears all fields.
  - Can be useful to clean the slate when the user decides against adding a word.
- benripaste
    - Downscales and converts drag&dropped or pasted images from the clipboard to efficient WEBP format.

In addition, each component may be disabled by the user if it is unnecessary.

# Requirements
Most of the functionality of the addon depends on 3rd party tools and assets which have to be provided by the user:
- benridict
  - Depends on edict.
- benritalk
  - Depends on either VOICEVOX or open_jtalk.
  - Encoding depends on ffmpeg.
- benriocr
  - Depends on manga-ocr-api.
- benripaste
  - Depends on ffmpeg.

The paths to the relevant executables, assets and HTTP services must be set by the user in the addon's configuration.

# Setup
Just clone the repository to your Anki addons folder ("~/.local/share/Anki2/addons21"). After that you can start Anki and configure the addon using the Anki's add-on configuration window. You will probably want to:
- Set the fields to match the field names you use in your note type.
- Set the ffmpeg path (default assumes it is in PATH).
- Set the edict path (default uses edict from kiten installed on a Linux system).
- Choose between VOICEVOX or open_jtalk for TTS.
  - Set "method" to either "voicevox" or "open_jtalk".
  - For VOICEVOX, set the desired speaker ID, and URL if VOICEVOX is running on a different PC.
  - For open_jtalk, set the executable, dictionary and voice paths (defaults are for open_jtalk installed on Arch Linux).
- Set the URL for the manga-ocr-api server.
- Disable any unneeded components.
