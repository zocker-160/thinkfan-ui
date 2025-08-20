# src/ui/range_controls.py

# This file defines the right-hand pane in the Curve Editor tab, which includes
# the curve selector, buttons, and a scrollable list of TempRangeEditor widgets.

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
    """
    The main widget for the right-hand side of the curve editor.
    Contains the curve selector dropdown and all control buttons.
    """
    def __init__(self, model, parent=None):
        """
        Initializes the layout and widgets for the control pane.

        Args:
            model (FanCurveModel): The data model containing the fan curve data.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.model = model
        self.range_editors = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # --- Curve Selector ComboBox ---
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Editing Curve for:"))
        self.curve_selector = QComboBox()
        self.curve_selector.setToolTip("Select which sensor's fan curve to view and edit.")
        selector_layout.addWidget(self.curve_selector)
        self.main_layout.addLayout(selector_layout)

        # --- Top Buttons in a horizontal layout ---
        top_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Range")
        self.add_button.setToolTip("Add a new temperature/fan level entry to the current curve.")
        top_button_layout.addWidget(self.add_button)
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
        
        # --- Bottom Buttons (File Operations) ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)

        bottom_button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load")
        self.load_button.setToolTip("Load the fan curve(s) from /etc/thinkfan.conf.")
        
        self.generate_button = QPushButton("Generate Conf")
        self.generate_button.setToolTip("Open a wizard to generate a new thinkfan.conf from scratch.")

        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save all currently defined curves to /etc/thinkfan.conf.")
        
        bottom_button_layout.addWidget(self.generate_button)
        bottom_button_layout.addWidget(self.load_button)
        bottom_button_layout.addWidget(self.save_button)
        self.main_layout.addLayout(bottom_button_layout)
        
        # --- Connections ---
        self.add_button.clicked.connect(self.model.add_range)
        self.model.modelChanged.connect(self.rebuild_view)
        self.curve_selector.currentTextChanged.connect(self._on_curve_selected)
        self.rebuild_view()

    def _on_curve_selected(self, key):
        """
        Slot that is called when the user selects a different curve
        from the ComboBox. It tells the model to change the active curve.

        Args:
            key (str): The new active curve key (sensor label).
        """
        if key:
            self.model.set_active_curve(key)

    def rebuild_view(self):
        """
        Rebuilds the entire view based on the current state of the data model.
        This is called whenever the model emits the `modelChanged` signal.
        """
        # --- Update ComboBox ---
        # Block signals to prevent this update from re-triggering the view change.
        self.curve_selector.blockSignals(True)
        self.curve_selector.clear()
        self.curve_selector.addItems(self.model.get_curve_keys())
        self.curve_selector.setCurrentText(self.model.get_active_curve_key())
        self.curve_selector.blockSignals(False)

        # --- Rebuild Range Editors for the active curve ---
        # Clear the old editor widgets.
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.range_editors.clear()
        
        # Create a new set of editor widgets for the currently active curve.
        for range_data in self.model.get_ranges():
            group = QGroupBox()
            editor_layout = QVBoxLayout(group)
            editor = TempRangeEditor(self.model, range_data)
            editor_layout.addWidget(editor)
            
            self.list_layout.addWidget(group)
            self.range_editors.append(group)
