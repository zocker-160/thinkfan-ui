#! /usr/bin/env python3
import os
import sys
import subprocess
import json
import re

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QGraphicsScene, QListWidget, QMainWindow, QMessageBox

from ui.gui import Ui_MainWindow
from ui.systray import QApp_SysTrayIndicator

VERSION = "v0.8.1"

PROC_FAN = "/proc/acpi/ibm/fan"

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.setupUi(self)

        self.label_3.setText(self.label_3.text().replace("$$$", VERSION))

        # buttons
        self.button_set.clicked.connect(lambda: app.setFanSpeed(self.slider.value()))
        self.button_auto.clicked.connect(lambda: app.setFanSpeed("auto"))
        self.button_full.clicked.connect(lambda: app.setFanSpeed("full-speed"))

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def showErrorMSG(self, msg_str: str, title_msg="ERROR"):
        self.appear()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(msg_str)
        msg.setWindowTitle(title_msg)
        msg.setDefaultButton(QMessageBox.Close)
        msg.exec_()

    def appear(self):
        self.center()
        self.show()
        self.raise_()
        self.activateWindow()

    def center(self):
        qr = self.frameGeometry()
        qr.moveCenter(
            self.app.primaryScreen().availableGeometry().center())
        self.move(qr.topLeft())


class ThinkFanUI(QApplication, QApp_SysTrayIndicator):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationVersion(VERSION)

        self.mainWindow = MainWindow(self)
        self.setupSysTrayIndicator()

        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateUI)
        self.updateTimer.start(1000)
        self.updateTimer.timeout.emit()

        # self.mainWindow.appear()

    def updateUI(self):
        temp_info = self.getTempInfo()
        fan_info = self.getFanInfo()
        self.mainWindow.label_temp.setText(temp_info)
        self.mainWindow.label_fan.setText(fan_info)
        self.updateSysTrayIndicatorMenu()

    def getTempInfo_json(self):
        """ Reads output of the "sensors" command """

        proc = subprocess.Popen(["sensors", "-j"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sOut, sErr = proc.communicate()

        #print(sOut, sErr)

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

        #print(sOut, sErr)

        if not sErr:
            lines = sOut.decode().split("\n")
            result = ""
            tempRE = re.compile(r"^(\w+):\s+\+.*(°|C|F| +)$")

            for i, line in enumerate(lines):
                line = line.strip()
                # print(line)
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

    def setFanSpeed(self, speed="auto"):
        """
        Set speed of fan by changing level at /proc/acpi/ibm/fan
        possible values: 0-7, auto, disengaged, full-speed
        """

        print("set speed:", speed)

        try:
            with open(PROC_FAN, "w+") as soc:
                soc.write(f"level {speed}")
        except PermissionError:
            cmd = [f"pkexec python -c \"with open('{PROC_FAN}', 'w+') as soc: soc.write('level {speed}')\""]
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode not in [0, 126]: # 126 is pkexec dismissed, 0 is success
                print(result.returncode, result.stdout, result.stderr)
                self.mainWindow.showErrorMSG("Missing permissions! Please run as root.")

            # Relaunch as root - doesnt solve Qt env problems some root accounts have
            # os.execvpe(f"pkexec", [os.path.realpath(__file__)] + sys.argv, os.environ)
        except FileNotFoundError:
            self.mainWindow.showErrorMSG(f"{PROC_FAN} does not exist!")

if __name__ == "__main__":
    app = ThinkFanUI(sys.argv)
    sys.exit(app.exec_())
