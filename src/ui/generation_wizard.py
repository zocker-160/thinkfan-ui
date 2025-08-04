from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox,
    QLabel, QScrollArea, QCheckBox, QWidget
)
from PyQt6.QtCore import Qt

class GenerationWizard(QDialog):
    def __init__(self, all_sensors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ThinkFan Configuration Wizard")
        self.setMinimumSize(500, 400)
        
        self.main_layout = QVBoxLayout(self)
        
        self.main_layout.addWidget(QLabel("Select all sensors to monitor in thinkfan.conf:"))
        
        # --- Create a Scroll Area ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(scroll_area)

        # --- Create a container widget for the checkboxes ---
        self.scroll_content = QWidget()
        self.checkbox_layout = QVBoxLayout(self.scroll_content)
        self.checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(self.scroll_content)

        # --- Populate with Checkboxes ---
        self.checkboxes = []
        for sensor in all_sensors:
            display_text = f"{sensor['device']} / {sensor['label']}"
            checkbox = QCheckBox(display_text)
            
            # Store the full sensor data directly on the checkbox object
            checkbox.setProperty("sensor_data", sensor)
            
            # By default, check the primary CPU sensor
            is_primary_cpu = sensor['device'] in ['coretemp', 'k10temp'] and \
                             sensor['label'] in ["Package id 0", "Tctl", "Tdie"]
            if is_primary_cpu:
                checkbox.setChecked(True)
            
            self.checkbox_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            
        # --- Dialog Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(button_box)

    def get_selection(self):
        """ Returns the full data object for all checked items. """
        selected_sensors = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                selected_sensors.append(checkbox.property("sensor_data"))
        return selected_sensors
