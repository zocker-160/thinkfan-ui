#!/usr/bin/env python3

import os
import sys
import subprocess
import re

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QButtonGroup,
    QVBoxLayout,
    QSplitter
)

from ui.gui import Ui_MainWindow
from ui.systray import QApp_SysTrayIndicator
from ui.curve_editor import FanCurveEditor
from ui.range_controls import RangeControls
from data_model import FanCurveModel
import backend # <-- IMPORT BACKEND
from QSingleApplication import QSingleApplicationTCP

APP_NAME = "ThinkFan UI"
APP_VERSION = "1.0.0"
APP_DESKTOP_NAME = "thinkfan-ui"
APP_UUID = "587dedfb-19f2-4b2a-bc74-3d656e80966a"

GITHUB_URL = "https://github.com/zocker-160/thinkfan-ui"

PROC_FAN = "/proc/acpi/ibm/fan"

SENSOR_TOOLTIPS = {
    "Tctl": "Control Temperature: Used by the CPU to manage cooling.",
    "Tdie": "Die Temperature: The actual measured temperature of the CPU die.",
    "Composite": "SSD Composite Temperature: Main temperature reading for the NVMe drive.",
    "temp": "Motherboard Sensor: A generic sensor for the chipset, VRMs, or case.",
    "fan": "Fan Speed in Revolutions Per Minute (RPM).",
    "level": "Current power level setting for the fan (0-7)."
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
        if self.mainWindow.isVisible():
            self._clear_layout(self.mainWindow.tempGridLayout)
            self._clear_layout(self.mainWindow.fanGridLayout)

            temp_data = self.getTempInfo()
            self._populate_grid(self.mainWindow.tempGridLayout, temp_data)

            fan_data = self.getFanInfo()
            self._populate_grid(self.mainWindow.fanGridLayout, fan_data, is_fan_info=True)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_grid(self, grid_layout, data, is_fan_info=False):
        row = 0
        palette = self.app.palette()
        base_color = palette.color(QPalette.ColorRole.Base).name()
        alternate_color = palette.color(QPalette.ColorRole.AlternateBase).name()
        
        for label_text, value_text in sorted(data.items()):
            label = QLabel(f"{label_text}:")
            value = QLabel(str(value_text))
            tooltip_key = label_text.lower()
            tooltip_text = "No additional information available."
            if "temp" in tooltip_key:
                tooltip_text = SENSOR_TOOLTIPS.get("temp")
            elif tooltip_key in SENSOR_TOOLTIPS:
                 tooltip_text = SENSOR_TOOLTIPS.get(tooltip_key)
            elif is_fan_info and 'speed' in tooltip_key:
                 tooltip_text = SENSOR_TOOLTIPS.get("fan")
            if label_text == "Fan1":
                highlight_style = "font-weight: bold; color: #87CEEB;"
                label.setStyleSheet(highlight_style)
                value.setStyleSheet(highlight_style)
                tooltip_text = "This is the primary fan controlled by this application."
            label.setToolTip(tooltip_text)
            value.setToolTip(tooltip_text)
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

    def getTempInfo(self):
        temps = {}
        allowed_keywords = ["cpu", "gpu"]
        try:
            proc = subprocess.Popen(["sensors", "thinkpad-isa-0000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sOut, sErr = proc.communicate(timeout=2)
            if not sErr:
                lines = sOut.decode().strip().split("\n")
                tempRE = re.compile(r"^(.*?):\s*\+?([^ ]+°C)")
                for line in lines:
                    match = tempRE.match(line)
                    if match:
                        label, value = match.groups()
                        if any(keyword in label.lower() for keyword in allowed_keywords):
                            clean_label = label.strip()
                            if clean_label not in temps:
                                temps[clean_label] = value.strip()
            else:
                temps["Error"] = sErr.decode()
        except (subprocess.TimeoutExpired, FileNotFoundError):
             temps["Error"] = "'sensors' command failed."
        except Exception as e:
            temps["Error"] = str(e)
        return temps

    def getFanInfo(self):
        fan_data = {}
        try:
            with open(PROC_FAN, "r") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        if key in ["status", "level"]:
                            fan_data[key] = value.strip()
                        elif key == "speed":
                            fan_data["Fan1"] = f"{value.strip()} RPM"
        except FileNotFoundError:
            fan_data["Error"] = f"{PROC_FAN} not found."
        except Exception as e:
            fan_data["Error"] = str(e)
        try:
            proc = subprocess.Popen(["sensors", "thinkpad-isa-0000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sOut, sErr = proc.communicate(timeout=2)
            if not sErr:
                lines = sOut.decode().strip().split("\n")
                fanRE = re.compile(r"^(fan2.*?):\s*(\d+\s*RPM)")
                for line in lines:
                    match = fanRE.match(line)
                    if match:
                        label, value = match.groups()
                        fan_data[label.strip()] = value.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return fan_data

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
                f"\"thinkpad_acpi\" does not seem to be set up correctly!",
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

        # --- Connect Save/Load buttons to backend logic ---
        self.controls_pane.load_button.clicked.connect(self.load_curve)
        self.controls_pane.save_button.clicked.connect(self.save_curve)

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

    def load_curve(self):
        """ Handles the Load button click. """
        print("Loading curve from thinkfan.conf...")
        new_ranges = backend.load_curve_from_thinkfan()
        if new_ranges:
            self.model.set_new_ranges(new_ranges)
            QMessageBox.information(self, "Success", "Successfully loaded curve from /etc/thinkfan.conf")
        else:
            QMessageBox.warning(self, "Warning", "Could not load levels from /etc/thinkfan.conf. Check logs for details.")

    def save_curve(self):
        """ Handles the Save button click. """
        print("Saving curve to thinkfan.conf...")
        # A real app would ask for pkexec/sudo password here
        if backend.save_curve_to_thinkfan(self.model.get_ranges()):
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
