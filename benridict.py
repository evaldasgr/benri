import os
import aqt
from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QLabel, QDialogButtonBox, QLineEdit


class PhraseEntryDialog(QDialog):
    def __init__(self, editor, phrase, parent=None):
        super(PhraseEntryDialog, self).__init__(parent)

        self.editor = editor

        self.setWindowTitle("benridict")

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
            benridict_process(self.entry.text(), self.editor)
        super(PhraseEntryDialog, self).accept()


class NoDefinitionsFoundDialog(QDialog):
    def __init__(self, parent=None):
        super(NoDefinitionsFoundDialog, self).__init__(parent)

        self.setWindowTitle("benridict")

        text = QLabel(self)

        text.setText("No definitions were found.")

        btn = (QDialogButtonBox.StandardButton.Ok)
        buttons = QDialogButtonBox(btn, self)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(buttons)

        self.setLayout(layout)


class DefinitionsDialog(QDialog):
    def __init__(self, results, editor, parent=None):
        super(DefinitionsDialog, self).__init__(parent)

        self.results = results
        self.editor = editor

        self.setWindowTitle("benridict")

        text = QLabel(self)

        text.setText("Multiple definitions were found. Select the desired definition:")

        self.list = QListWidget(self)
        for r in results:
            self.list.addItem(r[1])
        self.list.setCurrentRow(0)

        btn = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons = QDialogButtonBox(btn, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(text)
        layout.addWidget(self.list)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def accept(self):
        if not self.editor is None:
            cfg = aqt.mw.addonManager.getConfig(__name__)
            if len(self.list.selectedItems()) < 1:
                self.editor.note[cfg["fields"]["meaning"]] = self.results[0][1]
            else:
                self.editor.note[cfg["fields"]["meaning"]] = self.list.selectedItems()[0].text()
            self.editor.loadNoteKeepingFocus()

        super(DefinitionsDialog, self).accept()

    def reject(self):
        super(DefinitionsDialog, self).reject()

def benridict_process(phrase, editor):
    lookup = phrase
    results = []

    if lookup == "":
        return

    cfg = aqt.mw.addonManager.getConfig(__name__)
    with open(os.path.join(os.path.dirname(__file__), cfg["benridict"]["edict_path"]), "r", encoding="euc-jp") as edict_file:
        for line in edict_file:
            # Priorities are: 0(exact+priority), 1(exact), 2(priority), 3
            priority = 0

            result = line.strip().split(" ", 1)
            if not len(result) == 2:
                continue

            match = False
            word = result[0]
            meaning = result[1]
            if word == lookup or meaning.startswith(lookup + " "):
                match = True
            elif lookup in word or lookup in meaning:
                priority += 2
                match = True

            if match:
                if "(P)" in meaning:
                    meaning = meaning.replace("/(P)", "")
                else:
                    priority += 1

                meaning = meaning.replace("[", "").replace("] /", " ").replace("/", "; ")
                if meaning.startswith("; "):
                    meaning = meaning[2:]
                if meaning.endswith("; "):
                    meaning = meaning[:-2]
                results.append((priority, word + " " + meaning))

    results = sorted(results)

    if len(results) == 1:
        cfg = aqt.mw.addonManager.getConfig(__name__)
        editor.note[cfg["fields"]["meaning"]] = results[0][1]
        editor.loadNoteKeepingFocus()
    elif len(results) > 1:
        aqt.mw.benridict_dialog = DefinitionsDialog(results, editor)
        aqt.mw.benridict_dialog.show()
    else:
        aqt.mw.benridict_dialog = NoDefinitionsFoundDialog()
        aqt.mw.benridict_dialog.show()


def benridict_create_lambda(editor):
    def launch(editor):
        cfg = aqt.mw.addonManager.getConfig(__name__)
        lookup = cfg["fields"]["expression"]
        if lookup == "" or aqt.utils.KeyboardModifiersPressed().shift:
            aqt.mw.benridict_dialog = PhraseEntryDialog(editor, lookup)
            aqt.mw.benridict_dialog.show()
        else:
            benridict_process(lookup, editor)

    return launch

def benridict_add_button(buttons, editor):
    new_button = editor.addButton(None, 'benridict', benridict_create_lambda(editor))
    buttons.append(new_button)
    return buttons


aqt.gui_hooks.editor_did_init_buttons.append(benridict_add_button)
