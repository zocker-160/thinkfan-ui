from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QScrollArea,
    QHBoxLayout,
    QFrame
)
from PyQt6.QtCore import Qt
from .range_editor import TempRangeEditor

class RangeControls(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.range_editors = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # --- Top Buttons in a horizontal layout ---
        top_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Range")
        self.generate_button = QPushButton("Generate Conf") # New Button
        top_button_layout.addWidget(self.add_button)
        top_button_layout.addWidget(self.generate_button)
        self.main_layout.addLayout(top_button_layout)
        
        # --- Scroll Area for Editors ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(scroll_area)

        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content)
        
        # --- Bottom Buttons (Save/Load) ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)

        bottom_button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.save_button = QPushButton("Save")
        bottom_button_layout.addWidget(self.load_button)
        bottom_button_layout.addWidget(self.save_button)
        self.main_layout.addLayout(bottom_button_layout)
        
        # --- Connections ---
        self.add_button.clicked.connect(self.model.add_range)
        self.model.modelChanged.connect(self.rebuild_view)
        self.rebuild_view()

    def rebuild_view(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.range_editors.clear()
        
        for range_data in self.model.get_ranges():
            group = QGroupBox()
            editor_layout = QVBoxLayout(group)
            editor = TempRangeEditor(self.model, range_data)
            editor_layout.addWidget(editor)
            
            self.list_layout.addWidget(group)
            self.range_editors.append(group)
