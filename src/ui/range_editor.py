from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox
)
from PyQt6.QtCore import QSize

class TempRangeEditor(QWidget):
    """ A widget for editing the properties of a single TempRange. """
    def __init__(self, model, range_data, parent=None):
        super().__init__(parent)
        self.model = model
        self.range_data = range_data

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Row 0: Fan Level and Remove Button
        self.layout.addWidget(QLabel("Fan Level:"), 0, 0)
        self.level_combo = QComboBox()
        self.valid_levels = ["auto"] + list(range(8)) + ["Disengaged"]
        self.level_combo.addItems([str(lvl) for lvl in self.valid_levels])
        self.layout.addWidget(self.level_combo, 0, 1, 1, 3)

        self.remove_button = QPushButton("X")
        self.remove_button.setFixedSize(QSize(28, 28))
        self.layout.addWidget(self.remove_button, 0, 4)

        # Row 1: Min Temp
        self.layout.addWidget(QLabel("Min (°C):"), 1, 0)
        self.min_temp_spinbox = QDoubleSpinBox()
        self.min_temp_spinbox.setRange(0, 120)
        self.min_temp_spinbox.setDecimals(0)
        self.layout.addWidget(self.min_temp_spinbox, 1, 1, 1, 4)

        # Row 2: Max Temp
        self.layout.addWidget(QLabel("Max (°C):"), 2, 0)
        self.max_temp_spinbox = QDoubleSpinBox()
        self.max_temp_spinbox.setRange(0, 120)
        self.max_temp_spinbox.setDecimals(0)
        self.layout.addWidget(self.max_temp_spinbox, 2, 1, 1, 4)

        # Connect signals
        self.min_temp_spinbox.valueChanged.connect(self.ui_changed)
        self.max_temp_spinbox.valueChanged.connect(self.ui_changed)
        self.level_combo.currentTextChanged.connect(self.ui_changed)
        self.remove_button.clicked.connect(self.remove_range)
        
        self.update_display()

    def update_display(self):
        """ Populates the controls with the current range data. """
        # --- FIX: Block signals to prevent recursion ---
        self.min_temp_spinbox.blockSignals(True)
        self.max_temp_spinbox.blockSignals(True)
        self.level_combo.blockSignals(True)
        
        self.min_temp_spinbox.setValue(self.range_data.min_temp)
        self.max_temp_spinbox.setValue(self.range_data.max_temp)
        self.level_combo.setCurrentText(str(self.range_data.level))

        self.min_temp_spinbox.blockSignals(False)
        self.max_temp_spinbox.blockSignals(False)
        self.level_combo.blockSignals(False)

    def ui_changed(self):
        """ Called when the user finishes editing a value. """
        new_min = int(self.min_temp_spinbox.value())
        new_max = int(self.max_temp_spinbox.value())
        new_level_str = self.level_combo.currentText()
        new_level = int(new_level_str) if new_level_str.isdigit() else new_level_str
        
        if new_min > new_max:
            if self.sender() == self.min_temp_spinbox:
                self.min_temp_spinbox.setValue(self.range_data.min_temp)
            else:
                self.max_temp_spinbox.setValue(self.range_data.max_temp)
            return

        if (new_min == self.range_data.min_temp and
            new_max == self.range_data.max_temp and
            new_level == self.range_data.level):
            return
            
        self.model.update_range(self.range_data, new_min, new_max, new_level)

    def remove_range(self):
        """ Tells the model to remove this range. """
        self.model.remove_range(self.range_data)
