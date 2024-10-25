from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit


class NoDeleteTextEdit(QPlainTextEdit):
    realTextEdited = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.setUndoRedoEnabled(False)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.previousText = self.toPlainText()
        self.textChanged.connect(self.onTextChanged)

    def onCursorPositionChanged(self):
        self.moveCursorToEnd()

    def moveCursorToEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def set_text(self, text: str):
        self.previousText = text
        self.setPlainText(text)

    def onTextChanged(self):
        currentText = self.toPlainText()
        if len(currentText) < len(self.previousText):
            self.blockSignals(True)
            self.setPlainText(self.previousText)
            self.blockSignals(False)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
        else:
            sameEvent = self.previousText == currentText
            if not sameEvent:
                self.previousText = currentText
                self.realTextEdited.emit(currentText)