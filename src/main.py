#!/usr/bin/env python3

import os
import sys
import subprocess
import re
import json

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QWidget, QLabel, QHBoxLayout,
    QSpacerItem, QSizePolicy, QButtonGroup, QVBoxLayout, QSplitter
)

from ui.gui import Ui_MainWindow
from ui.systray import QApp_SysTrayIndicator
from ui.curve_editor import FanCurveEditor
from ui.range_controls import RangeControls
from ui.generation_wizard import GenerationWizard
from ui.config_preview_dialog import ConfigPreviewDialog
from data_model import FanCurveModel
import backend
from QSingleApplication import QSingleApplicationTCP

APP_NAME = "ThinkFan UI"
APP_VERSION = "1.0.0"
APP_DESKTOP_NAME = "thinkfan-ui"
APP_UUID = "587dedfb-19f2-4b2a-bc74-3d656e80966a"
GITHUB_URL = "https://github.com/zocker-160/thinkfan-ui"
PROC_FAN = "/proc/acpi/ibm/fan"

SENSOR_TOOLTIPS = {
    "cpu": "CPU Temperature: The temperature of the main processor.",
    "gpu": "GPU Temperature: The temperature of the graphics processor.",
    "fan1": "Fan Speed in Revolutions Per Minute (RPM).",
    "fan2": "Fan Speed for the secondary fan, if present.",
    "level": "The current fan speed level set in the embedded controller (EC).",
    "status": "Indicates if fan control is enabled or disabled by the EC.",
    "composite": "SSD Composite Temperature: Main temperature reading for the NVMe drive.",
    "package id 0": "The overall temperature of the CPU package."
}

class ThinkFanUI(QApp_SysTrayIndicator):
    def __init__(self, app: QSingleApplicationTCP, argv):
        super().__init__()

        self.app = app
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationDisplayName(APP_NAME)
        self.app.setDesktopFileName(APP_DESKTOP_NAME)

        self.fan_curve_model = FanCurveModel(self)

        self.mainWindow = MainWindow(self, self.fan_curve_model)
        self.mainWindow.center()
        self.mainWindow._set_fan_mode_auto()
        self.app.onActivate.connect(self.mainWindow.appear)

        self.useIndicator = "--no-tray" not in argv
        self.hideWindow = "--hide" in argv

        if not checkPermissions():
            updatePermissions()

        if self.useIndicator:
            self.setupSysTrayIndicator()

        if not self.hideWindow or not self.useIndicator:
            self.mainWindow.appear()

        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateUI)
        self.updateTimer.start(1000)
        self.updateTimer.timeout.emit()

    def updateUI(self):
        """ Calls a single data source and updates all UI grids. """
        if self.mainWindow.isVisible():
            all_data = self.get_all_sensor_data()

            # Prepare formatted data for display
            temp_data = {label: f"{value}°C" for label, value in all_data.get('temps', {}).items()}
            # --- FIX --- Cast fan speed value to int to remove decimal
            fan_data = {label: f"{int(value)} RPM" for label, value in all_data.get('fans', {}).items()}
            fan_data.update(all_data.get('fan_state', {}))
            
            # Populate temperature grid
            self._clear_layout(self.mainWindow.tempGridLayout)
            self._populate_grid(self.mainWindow.tempGridLayout, temp_data)

            # Populate fan grid
            self._clear_layout(self.mainWindow.fanGridLayout)
            self._populate_grid(self.mainWindow.fanGridLayout, fan_data)

    def get_all_sensor_data(self):
        """
        Calls 'sensors -j' once and reads /proc/acpi/ibm/fan to get all
        necessary temperature, fan, and status data in a structured format.
        """
        all_data = {'temps': {}, 'fans': {}, 'fan_state': {}}
        allowed_temp_keywords = ["cpu", "gpu", "package id 0"]

        # 1. Get structured data from `sensors -j`
        try:
            result = subprocess.run(
                ["sensors", "-j"], 
                capture_output=True, text=True, check=True, timeout=2
            )
            sensor_data = json.loads(result.stdout)

            for device_info in sensor_data.values():
                for feature_name, feature_data in device_info.items():
                    if not isinstance(feature_data, dict): continue

                    # Extract temperatures
                    temp_input = next((v for k, v in feature_data.items() if k.endswith("_input") and k.startswith("temp")), None)
                    if temp_input is not None and any(keyword in feature_name.lower() for keyword in allowed_temp_keywords):
                        all_data['temps'][feature_name.strip()] = temp_input

                    # Extract fan speeds
                    fan_input = next((v for k, v in feature_data.items() if k.endswith("_input") and k.startswith("fan")), None)
                    if fan_input is not None:
                        fan_label = feature_name.strip()
                        if fan_label.lower() == "fan1": fan_label = "Fan1"
                        if fan_label.lower() == "fan2": fan_label = "Fan2"
                        all_data['fans'][fan_label] = fan_input
        
        except Exception as e:
            all_data['temps']["Error"] = f"'sensors -j' command failed."

        # 2. Get Fan1 level/status from /proc, which is not in `sensors` output
        try:
            with open(PROC_FAN, "r") as f:
                for line in f:
                    if ":" in line:
                        key, value = [x.strip() for x in line.split(":", 1)]
                        if key in ["status", "level"]:
                            all_data['fan_state'][key] = value
        except Exception as e:
            if not all_data['temps'].get("Error"):
                 all_data['temps']["Error"] = str(e)

        return all_data

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_grid(self, grid_layout, data):
        row = 0
        palette = self.app.palette()
        base_color = palette.color(QPalette.ColorRole.Base).name()
        alternate_color = palette.color(QPalette.ColorRole.AlternateBase).name()
        
        for label_text, value_text in sorted(data.items()):
            label = QLabel(f"{label_text}:")
            value = QLabel(str(value_text))
            
            tooltip_key = label_text.lower().replace(":", "")
            tooltip_text = SENSOR_TOOLTIPS.get(tooltip_key, "No additional information available.")
            
            if "fan1" in tooltip_key: tooltip_text = SENSOR_TOOLTIPS.get("fan1")
            if "fan2" in tooltip_key: tooltip_text = SENSOR_TOOLTIPS.get("fan2")
            if "level" in tooltip_key: tooltip_text = SENSOR_TOOLTIPS.get("level")
            if "status" in tooltip_key: tooltip_text = SENSOR_TOOLTIPS.get("status")

            label.setToolTip(tooltip_text)
            value.setToolTip(tooltip_text)
            
            if "Fan1" in label_text:
                highlight_style = "font-weight: bold; color: #87CEEB;"
                label.setStyleSheet(highlight_style)
                value.setStyleSheet(highlight_style)
                label.setToolTip("This is the primary fan controlled by this application.")
                value.setToolTip("This is the primary fan controlled by this application.")
            
            row_container = QWidget()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(5, 2, 5, 2)
            row_layout.addWidget(label)
            spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            row_layout.addItem(spacer)
            row_layout.addWidget(value)
            
            if row % 2 == 1:
                row_style = f"background-color: {alternate_color}; border-radius: 4px;"
            else:
                row_style = f"background-color: {base_color}; border-radius: 4px;"
            row_container.setStyleSheet(row_style)
            
            grid_layout.addWidget(row_container, row, 0, 1, 2)
            row += 1

    def setFanSpeed(self, speed="auto", retry=False):
        print("set speed:", speed)
        try:
            with open(PROC_FAN, "w") as soc:
                soc.write(f"level {speed}")
        except PermissionError:
            updatePermissions()
            if not retry:
                self.setFanSpeed(speed, True)
            else:
                self.mainWindow.showErrorMSG("Missing permissions! Failed to set fan speed.")
        except FileNotFoundError:
            self.mainWindow.showErrorMSG(f"{PROC_FAN} does not exist!")
        except OSError:
            self.mainWindow.showErrorMSG(
                "\"thinkpad_acpi\" does not seem to be set up correctly!",
                detail="Please check that /etc/modprobe.d/thinkpad_acpi.conf contains \"options thinkpad_acpi fan_control=1\"")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app: ThinkFanUI, model: FanCurveModel):
        super(QMainWindow, self).__init__()
        self.app = app
        self.model = model
        self.setupUi(self)
        
        self.curve_editor = FanCurveEditor(self.model, self)
        self.controls_pane = RangeControls(self.model, self)
        self.controls_pane.setMinimumWidth(300)
        splitter = QSplitter(self)
        splitter.addWidget(self.curve_editor)
        splitter.addWidget(self.controls_pane)
        splitter.setSizes([700, 300])
        self.curveEditorLayout = QVBoxLayout(self.tabCurveEditor)
        self.curveEditorLayout.addWidget(splitter)
        
        self.versionLabel.setText(f"v{APP_VERSION}")

        self.controls_pane.load_button.clicked.connect(self.load_curve)
        self.controls_pane.save_button.clicked.connect(self.save_curve)
        self.controls_pane.generate_button.clicked.connect(self.show_generation_wizard)

        self.button_auto.setCheckable(True)
        self.button_full.setCheckable(True)
        self.button_set.setCheckable(True)
        self.button_set.setText("Manual")

        self.fanModeGroup = QButtonGroup(self)
        self.fanModeGroup.addButton(self.button_auto)
        self.fanModeGroup.addButton(self.button_full)
        self.fanModeGroup.addButton(self.button_set)
        self.fanModeGroup.setExclusive(True)

        self.button_auto.clicked.connect(self._set_fan_mode_auto)
        self.button_full.clicked.connect(self._set_fan_mode_full)
        self.button_set.clicked.connect(self._set_fan_mode_manual)
        
        self.slider.valueChanged.connect(self._slider_value_changed)
        self.button_auto.setChecked(True)

        self.actionClose.triggered.connect(self.close)
        self.actionExit.triggered.connect(self.app.app.quit)
        self.actionGitHub.triggered.connect(openGitHub)
        self.actionAbout.triggered.connect(self.showAbout)
        self.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))
        
        self.resize(self.sizeHint())
        
        self._curve_editor_first_load = True
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.button_auto.setToolTip("Set fan to automatic control by the Embedded Controller (EC).")
        self.button_full.setToolTip("Set fan to its maximum speed.")
        self.button_set.setToolTip("Enable slider for manual fan level control (0-7).")

    def on_tab_changed(self, index):
        if self.tabWidget.widget(index) is self.tabCurveEditor:
            if self._curve_editor_first_load:
                self._curve_editor_first_load = False
                if not os.path.exists(backend.THINKFAN_CONF_PATH):
                    reply = QMessageBox.question(self, "thinkfan-ui", 
                                                 "No thinkfan configuration found.\nWould you like to generate one now?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                 QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.show_generation_wizard()

    def show_generation_wizard(self):
        all_sensors = backend.discover_sensors()
        if not all_sensors:
            QMessageBox.critical(self, "Error", "Could not find any temperature sensors. Please ensure 'lm-sensors' is installed.")
            return

        wizard = GenerationWizard(all_sensors, self)
        if wizard.exec():
            selection = wizard.get_selection()
            if selection:
                config_content = backend.generate_config_content(selection)
                preview_dialog = ConfigPreviewDialog(config_content, self)
                if preview_dialog.exec():
                    success = backend.save_content_to_thinkfan(config_content)
                    if success:
                        QMessageBox.information(self, "Success",
                                                "thinkfan.conf has been generated and saved.\n"
                                                "Loading the new curve now.")
                        self.load_curve()
                    else:
                        QMessageBox.critical(self, "Error",
                                             "Failed to save the new thinkfan.conf. "
                                             "Check logs for details.")

    def load_curve(self):
        print("Loading curve from thinkfan.conf...")
        new_curves = backend.load_curve_from_thinkfan()
        if new_curves:
            self.model.set_curves(new_curves)
            QMessageBox.information(self, "Success", "Successfully loaded curves from /etc/thinkfan.conf")
        else:
            QMessageBox.warning(self, "Warning", "Could not load curves from /etc/thinkfan.conf. Check logs for details.")

    def save_curve(self):
        print("Saving curve to thinkfan.conf...")
        if backend.save_curve_to_thinkfan(self.model.get_all_curves()):
            QMessageBox.information(self, "Success", "Successfully saved curve to /etc/thinkfan.conf.\nRestart thinkfan service to apply changes.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save to /etc/thinkfan.conf. Run the app with sudo or check file permissions.")

    def _set_fan_mode_auto(self):
        self.app.setFanSpeed("auto")
        self.slider.setEnabled(False)

    def _set_fan_mode_full(self):
        self.app.setFanSpeed("full-speed")
        self.slider.setEnabled(False)

    def _set_fan_mode_manual(self):
        self.slider.setEnabled(True)
        self.app.setFanSpeed(self.slider.value())

    def _slider_value_changed(self, value):
        self.button_set.setChecked(True)
        self._set_fan_mode_manual()

    def closeEvent(self, event):
        if self.app.useIndicator:
            event.ignore()
            self.hide()
        else:
            self.app.app.quit()

    def showErrorMSG(self, msg_str: str, title_msg="ERROR", detail: str = None):
        self.appear()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(msg_str)
        if detail:
            msg.setDetailedText(detail)
        msg.setWindowTitle(title_msg)
        msg.setDefaultButton(QMessageBox.StandardButton.Close)
        msg.exec()

    def showAbout(self):
        about = f"""
        <h3>{APP_NAME} - v{APP_VERSION}</h3>
        <p>A simple GUI for controlling ThinkPad fan speeds.</p>
        <p>Made by zocker_160 and contributors, licensed under GPLv3.</p>
        <a href=\"{GITHUB_URL}\">{GITHUB_URL}</a>
        """
        QMessageBox.about(self, f"About {APP_NAME}", about)

    def toggleAppear(self):
        if self.isVisible():
            self.hide()
        else:
            self.appear()

    def appear(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def updatePermissions():
    try:
        command = ["pkexec", "chown", os.getlogin(), PROC_FAN]
        subprocess.run(command)
    except OSError:
        command = ["pkexec", "chmod", "777", PROC_FAN]
        subprocess.run(command)

def checkPermissions() -> bool:
    if not os.path.isfile(PROC_FAN):
        return True
    return os.access(PROC_FAN, os.W_OK)

def openGitHub():
    subprocess.Popen(["xdg-open", GITHUB_URL])

if __name__ == "__main__":
    app = QSingleApplicationTCP(APP_UUID, sys.argv)
    if app.isRunning:
        print("Another instance is already running. Exiting.")
        sys.exit()

    fan_ui = ThinkFanUI(app, sys.argv)
    sys.exit(app.exec())
