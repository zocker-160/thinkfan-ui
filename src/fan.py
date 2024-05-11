#! /usr/bin/env python3

import os
import sys
import subprocess
import json
import re

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from ui.gui import Ui_MainWindow
from ui.systray import QApp_SysTrayIndicator
from QSingleApplication import QSingleApplicationTCP

APP_NAME = "ThinkFan UI"
APP_VERSION = "0.10.2"
APP_DESKTOP_NAME = "thinkfan-ui"
APP_UUID = "587dedfb-19f2-4b2a-bc74-3d656e80966a"

GITHUB_URL = "https://github.com/zocker-160/thinkfan-ui"

PROC_FAN = "/proc/acpi/ibm/fan"

class ThinkFanUI(QApp_SysTrayIndicator):

    def __init__(self, app: QSingleApplicationTCP, argv):
        super().__init__()

        self.app = app
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationDisplayName(APP_NAME)
        self.app.setDesktopFileName(APP_DESKTOP_NAME)

        self.mainWindow = MainWindow(self)
        self.mainWindow.center()
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
        temp_info, fan_info = None, None
        if self.mainWindow.isActiveWindow():
            temp_info, fan_info = self.getTempInfo(), self.getFanInfo()
            self.mainWindow.label_temp.setText(temp_info)
            self.mainWindow.label_fan.setText(fan_info)

        if self.useIndicator and self.menu_visible:
            temp_info = temp_info or self.getTempInfo()
            fan_info = fan_info or self.getFanInfo()
            self.updateIndicatorMenu(temp_info, fan_info)

    def getTempInfo_json(self):
        """ Reads output of the "sensors" command """

        proc = subprocess.Popen(["sensors", "-j"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sOut, sErr = proc.communicate()

        # print(sOut, sErr)

        if not sErr:
            data: dict = json.loads(sOut)

            result = ""

            for key, value in data.items():
                if "temp" in key:
                    for k, v in value.items():
                        if not "°C" in v:
                            continue

                        result += f"{k}:"
                        for name, data in v.items():
                            result += f"\t {name}: {data} \n"
        else:
            result = sErr.decode()

        return result

    def getTempInfo(self):
        """ Reads output of the "sensors" command """

        proc = subprocess.Popen(["sensors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sOut, sErr = proc.communicate()

        # print(sOut, sErr)

        if not sErr:
            lines = sOut.decode().split("\n")
            result = ""
            tempRE = re.compile(r"^([\w ]+:)\s+(\+.*)([°|C|F| +])(.)$")

            for i, line in enumerate(lines):
                line = line.strip()
                if tempRE.match(line):
                    # if "CPU" in line:
                    #     result = line
                    if "pci" not in line and "0.0" not in line:
                        result += line + "\n"
        else:
            result = sErr.decode()

        return result

    def getFanInfo(self):
        """ Parses the first 3 lines of output from /proc/acpi/ibm/fan """

        proc = subprocess.Popen(["cat", PROC_FAN], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sOut, sErr = proc.communicate()

        if not sErr:
            result = ""

            output = sOut.decode().split("\n")
            for i, line in enumerate(output):
                if i == 3: break

                result += line
                result += "\n"
        else:
            result = sErr.decode()

        return result

    def setFanSpeed(self, speed="auto", retry=False):
        """
        Set speed of fan by changing level at /proc/acpi/ibm/fan
        possible values: 0-7, auto, disengaged, full-speed
        """

        print("set speed:", speed)

        try:
            with open(PROC_FAN, "w") as soc:
                soc.write(f"level {speed}")

        except PermissionError:
            self.updatePermissions()

            if not retry:
                self.setFanSpeed(speed, True)
            else:
                self.mainWindow.showErrorMSG("Missing permissions! Failed to set fan speed.")

        except FileNotFoundError:
            self.mainWindow.showErrorMSG(f"{PROC_FAN} does not exist!")

        except OSError:
            self.mainWindow.showErrorMSG(
                f"\"thinkpad_acpi\" does not seem to be set up correctly!",
                detail="please check that /etc/modprobe.d/thinkpad_acpi.conf contains \"options thinkpad_acpi fan_control=1\"")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app: ThinkFanUI):
        super(QMainWindow, self).__init__()
        self.app = app
        self.setupUi(self)
        self.versionLabel.setText(f"v{APP_VERSION}")

        # menu
        self.actionClose.triggered.connect(self.close)
        self.actionExit.triggered.connect(self.app.app.quit)
        self.actionGitHub.triggered.connect(openGitHub)
        self.actionAbout.triggered.connect(self.showAbout)
        self.actionAbout_Qt.triggered.connect(lambda: QMessageBox.aboutQt(self))

        # buttons
        self.button_set.clicked.connect(lambda: app.setFanSpeed(self.slider.value()))
        self.button_auto.clicked.connect(lambda: app.setFanSpeed("auto"))
        self.button_full.clicked.connect(lambda: app.setFanSpeed("full-speed"))

    def closeEvent(self, event):
        if self.app.useIndicator:
            event.ignore()
            self.hide()

    def showErrorMSG(self, msg_str: str, title_msg="ERROR", detail: str = None):
        self.appear()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(msg_str)
        if detail:
            msg.setDetailedText(detail)
        msg.setWindowTitle(title_msg)
        msg.setDefaultButton(QMessageBox.StandardButton.Close)
        msg.exec_()

    def showAbout(self):
        about = f"""
        <h3>{APP_NAME} - v{APP_VERSION}</h3>

        made by zocker_160
        <br>
        licensed under GPLv3 | 2021 - 2024
        <br>
        <br>
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
        qr.moveCenter(
            self.app.app # yeah I know this is terriblem, pls just ignore
            .primaryScreen()
            .availableGeometry()
            .center())
        self.move(qr.topLeft())


# some helper functions

def updatePermissions():
    try:
        command = ["pkexec", "chown", os.getlogin(), PROC_FAN]
        result = subprocess.run(command)
    except OSError:
        command = ["pkexec", "chmod", "777", PROC_FAN]
        result = subprocess.run(command)
    print(result.returncode, result.stdout, result.stderr)

def checkPermissions() -> bool:
    try:
        with open(PROC_FAN, "w"):
            return True
    except PermissionError:
        return False
    except FileNotFoundError:
        # we ignore if the endpoint does not exist as it will show error in the UI later
        return True

def openGitHub():
    subprocess.Popen(["xdg-open", GITHUB_URL])

if __name__ == "__main__":
    app = QSingleApplicationTCP(APP_UUID, sys.argv)

    if app.isRunning:
        print("Other instance already running - exit")
        sys.exit()

    fan = ThinkFanUI(app, sys.argv)
    sys.exit(app.exec())
