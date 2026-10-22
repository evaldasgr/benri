import os
import subprocess
import tempfile
import random

import aqt
import anki
import requests
from PyQt6.QtWidgets import QLabel, QDialogButtonBox, QVBoxLayout, QDialog, QLineEdit


class PhraseEntryDialog(QDialog):
    def __init__(self, editor, phrase, parent=None):
        super(PhraseEntryDialog, self).__init__(parent)

        self.editor = editor

        self.setWindowTitle("benritalk")

        text = QLabel(self)
        text.setText("Enter phrase:")

        self.entry = QLineEdit()
        self.entry.setText(phrase)

        btn = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons = QDialogButtonBox(btn, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        buttons.button(QDialogButtonBox.StandardButton.Cancel).setAutoDefault(False)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setDefault(False)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setAutoDefault(True)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(self.entry)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.entry.setFocus()

    def accept(self):
        if not self.entry.text() == "":
            benritalk_process(self.entry.text(), self.editor)
        super(PhraseEntryDialog, self).accept()


def next_id() -> str:
    alpha = list('0123456789abcdefghijklmnopqrstuvwxyz')
    while True:
        fn = ""
        for i in range(7):
            fn += random.choice(alpha)

        if not os.path.exists(os.path.join(aqt.mw.col.media.dir(), fn + ".ogg")):
            return fn


def benritalk_voicevox(editor):
    def launch(editor):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        lookup = cfg["fields"]["expression"]
        if lookup == "":
            return

        rel_fn = next_id() + ".ogg"
        abs_fn = os.path.join(aqt.mw.col.media.dir(), rel_fn)

        query_result = requests.post(cfg["benritalk"]["voicevox_url"] + "/audio_query?text=" + lookup + "&speaker=" + cfg["benritalk"]["voicevox_speaker"])
        synthesis_result = requests.post(cfg["benritalk"]["voicevox_url"] + "/synthesis?speaker=" + cfg["benritalk"]["voicevox_speaker"], data=query_result.content)
        subprocess.run([
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-i", "pipe:0",
            "-c:a", "libopus",
            "-b:a", "64k",
            abs_fn
        ], input=synthesis_result.content)

        aqt.sound.av_player.play_tags([anki.sound.SoundOrVideoTag(filename=rel_fn)])

        editor.note[cfg["fields"]["audio"]] = "[sound:" + rel_fn + "]"
        editor.loadNoteKeepingFocus()

    return launch

def benritalk_process(phrase, editor):
    wav_fn = None
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        wav_fn = tmp_file.name
    rel_fn = next_id() + ".ogg"
    abs_fn = os.path.join(aqt.mw.col.media.dir(), rel_fn)

    cfg = aqt.mw.addonManager.getConfig(__name__)
    subprocess.run([
        "open_jtalk",
        "-x", cfg["benritalk"]["open_jtalk_dic_path"],
        "-m", cfg["benritalk"]["open_jtalk_voice_path"],
        "-ow", wav_fn
    ], input=phrase.encode("utf-8"))

    subprocess.run([
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-i", wav_fn,
        "-c:a", "libopus",
        "-b:a", "32k",
        abs_fn
    ])
    os.remove(wav_fn)

    aqt.sound.av_player.play_tags([anki.sound.SoundOrVideoTag(filename=rel_fn)])

    editor.note[cfg["fields"]["audio"]] = "[sound:" + rel_fn + "]"
    editor.loadNoteKeepingFocus()


def benritalk_jtalk(editor):
    def launch(editor):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        lookup = editor.note[cfg["fields"]["expression"]]
        if lookup == "" or aqt.utils.KeyboardModifiersPressed().shift:
            aqt.mw.benritalk_dialog = PhraseEntryDialog(editor, lookup)
            aqt.mw.benritalk_dialog.show()
        else:
            benritalk_process(lookup, editor)

    return launch


def benritalk_play(editor):
    def launch(editor):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        lookup = editor.note[cfg["fields"]["audio"]]
        if lookup == "":
            return

        rel_fn = lookup.replace("[sound:", "").replace("]", "")
        aqt.sound.av_player.play_tags([anki.sound.SoundOrVideoTag(filename=rel_fn)])

    return launch


def benritalk_add_button(buttons, editor):
    cfg = aqt.mw.addonManager.getConfig(__name__)
    if cfg["benritalk"]["method"] == "open_jtalk":
        new_button = editor.addButton(None, 'benritalk', benritalk_jtalk(editor))
    elif cfg["benritalk"]["method"] == "voicevox":
        new_button = editor.addButton(None, 'benritalk', benritalk_voicevox(editor))
    else:
        raise Exception("Unrecognized benritalk method")
    play_button = editor.addButton(None, 'benriplay', benritalk_play(editor))
    buttons.append(new_button)
    buttons.append(play_button)
    return buttons


aqt.gui_hooks.editor_did_init_buttons.append(benritalk_add_button)
