from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QScrollArea
)
from PyQt6.QtCore import Qt
from .range_editor import TempRangeEditor # Import the new class name

class RangeControls(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.range_editors = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_button = QPushButton("Add New Range") # Updated text
        self.main_layout.addWidget(self.add_button)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(scroll_area)

        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.scroll_content)

        self.add_button.clicked.connect(self.model.add_range) # Connect to the new method
        self.model.modelChanged.connect(self.rebuild_view)
        self.rebuild_view()

    def rebuild_view(self):
        # Clear old editor widgets
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.range_editors.clear()
        
        # Create a new editor widget for each range in the model
        for range_data in self.model.get_ranges():
            # Using a simple QGroupBox for now. Can be customized later.
            group = QGroupBox()
            editor_layout = QVBoxLayout(group)
            editor = TempRangeEditor(self.model, range_data) # Use the new editor
            editor_layout.addWidget(editor)
            
            self.list_layout.addWidget(group)
            self.range_editors.append(group)
