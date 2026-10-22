import aqt




def benriclear_clear(editor):
    def launch(editor):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        fields = cfg["benriclear"]["fields"]
        for f in fields:
            if f in editor.note:
                editor.note[f] = ""
        editor.loadNoteKeepingFocus()

    return launch


def benriclear_add_button(buttons, editor):
    button = editor.addButton(None, 'benriclear', benriclear_clear(editor))
    buttons.append(button)
    return buttons


aqt.gui_hooks.editor_did_init_buttons.append(benriclear_add_button)
