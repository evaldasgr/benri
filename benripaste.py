import os
import subprocess
import random

import aqt
from PyQt6.QtCore import QMimeData, QByteArray, QBuffer


def next_id() -> str:
    alpha = list('0123456789abcdefghijklmnopqrstuvwxyz')
    while True:
        fn = ""
        for i in range(7):
            fn += random.choice(alpha)

        if not os.path.exists(os.path.join(aqt.mw.col.media.dir(), fn + ".webp")):
            return fn


def convert_mime(mime: QMimeData, text: bool) -> QMimeData:
    if mime.hasImage():
        fn = next_id() + ".webp"

        image_bytes = QByteArray()
        mime.imageData().save(QBuffer(image_bytes), format="png")

        cfg = aqt.mw.addonManager.getConfig(__name__)
        subprocess.run([
            cfg["ffmpeg_path"],
            "-y",
            "-loglevel", "error",
            "-i", "pipe:0",
            "-filter:v", "scale='min(1500,iw)':min'(1000,ih)':force_original_aspect_ratio=decrease",
            "-compression_level", "6",
            "-quality", "87.5",
            "-preset", "text" if text else "none",
            os.path.join(aqt.mw.col.media.dir(), fn)
        ], input=image_bytes.data())

        mime = QMimeData()
        mime.setHtml("<img src=\"" + fn + "\">")

    return mime


def on_process_mime(mime: QMimeData, editor_web_view: aqt.editor.EditorWebView, internal: bool, _extended: bool,
                    drop_event: bool) -> QMimeData:
    if internal or aqt.utils.KeyboardModifiersPressed().shift:
        return mime

    # Copy & paste assumed to be text, drag & drop - photo
    return convert_mime(mime, not drop_event)


aqt.gui_hooks.editor_will_process_mime.append(on_process_mime)
