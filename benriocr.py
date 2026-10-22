import aqt

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice
import urllib3
import json

def benriocr_paste(editor):
    def launch(editor):
        img = QApplication.clipboard().image()
        if img.isNull():
            return

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        # BMP, WEBP takes around the same time to encode, send and receive
        img.save(buffer, 'PNG')

        cfg = aqt.mw.addonManager.getConfig(__name__)
        http = urllib3.PoolManager()
        fields = {'file': ('image.png', buffer.data(), 'image/png')}
        headers = {'accept': 'application/json'}
        response = http.request('POST', cfg["benriocr"]["url"] + "/ocr", fields=fields, headers=headers)
        editor.note[cfg["fields"]["expression"]] = json.loads(response.data.decode('utf-8'))["text"]
        editor.loadNoteKeepingFocus()

    return launch


def benriocr_add_button(buttons, editor):
    button = editor.addButton(None, 'benriocr', benriocr_paste(editor))
    buttons.append(button)
    return buttons


aqt.gui_hooks.editor_did_init_buttons.append(benriocr_add_button)
