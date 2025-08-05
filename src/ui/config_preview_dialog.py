# src/ui/config_preview_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
)
from PyQt6.QtGui import QFont

class ConfigPreviewDialog(QDialog):
    """
    A dialog that shows a preview of the generated thinkfan.conf content
    and prompts the user to either save or cancel.
    """
    def __init__(self, config_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Preview")
        self.setMinimumSize(600, 500)

        self.main_layout = QVBoxLayout(self)

        # Text area to display the config content
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(config_content)
        
        # Use a monospaced font for better readability
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.text_edit.setFont(font)
        
        self.main_layout.addWidget(self.text_edit)

        # Standard Save/Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(button_box)
