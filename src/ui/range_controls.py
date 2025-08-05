from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QScrollArea,
    QHBoxLayout,
    QFrame,
    QComboBox,
    QLabel
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
        
        # --- Curve Selector ComboBox ---
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Editing Curve for:"))
        self.curve_selector = QComboBox()
        selector_layout.addWidget(self.curve_selector)
        self.main_layout.addLayout(selector_layout)

        # --- Top Buttons in a horizontal layout ---
        top_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Range")
        self.add_button.setToolTip("Add a new temperature/fan level entry to the current curve.")
        self.generate_button = QPushButton("Generate Conf")
        self.generate_button.setToolTip("Open a wizard to generate a new thinkfan.conf from scratch.")
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
        self.load_button.setToolTip("Load the fan curve(s) from /etc/thinkfan.conf.")
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save all currently defined curves to /etc/thinkfan.conf.")
        bottom_button_layout.addWidget(self.load_button)
        bottom_button_layout.addWidget(self.save_button)
        self.main_layout.addLayout(bottom_button_layout)
        
        # --- Connections ---
        self.add_button.clicked.connect(self.model.add_range)
        self.model.modelChanged.connect(self.rebuild_view)
        self.curve_selector.currentTextChanged.connect(self._on_curve_selected)
        self.rebuild_view()

    def _on_curve_selected(self, key):
        if key:
            self.model.set_active_curve(key)

    def rebuild_view(self):
        # --- Update ComboBox ---
        self.curve_selector.blockSignals(True)
        self.curve_selector.clear()
        self.curve_selector.addItems(self.model.get_curve_keys())
        self.curve_selector.setCurrentText(self.model.get_active_curve_key())
        self.curve_selector.blockSignals(False)

        # --- Rebuild Range Editors for the active curve ---
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
