#! /usr/bin/env python3

import sys
import subprocess
import json
import re

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QGraphicsScene, QListWidget, QMainWindow, QMessageBox

from ui.gui import Ui_MainWindow

VERSION = "v0.8.1"

PROC_FAN = "/proc/acpi/ibm/fan"

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

        self.setupUi(self)
        self.label_3.setText(self.label_3.text().replace("$$$", VERSION))

        # buttons
        self.button_set.clicked.connect(lambda: self.setFanSpeed(self.slider.value()))
        self.button_auto.clicked.connect(lambda: self.setFanSpeed("auto"))
        self.button_full.clicked.connect(lambda: self.setFanSpeed("full-speed"))

        # timer
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.getTempInfo)
        self.updateTimer.timeout.connect(self.getFanInfo)
        self.updateTimer.start(1000)
        self.updateTimer.timeout.emit()

    def showErrorMSG(self, msg_str: str, title_msg="ERROR"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(msg_str)
        msg.setWindowTitle(title_msg)
        msg.setDefaultButton(QMessageBox.Close)
        msg.exec_()

    def getTempInfo_old(self):
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

        self.label_temp.setText(result)

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
                    if "pci" not in line and "0.0" not in line:
                        result += line + "\n"
        else:
            result = sErr.decode()

        self.label_temp.setText(result)
        #print(result)

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

        self.label_fan.setText(result)

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
            self.showErrorMSG("Missing permissions! Please run as root.")
        except FileNotFoundError:
            self.showErrorMSG(f"{PROC_FAN} does not exist!")

    def center(self):
        qr = self.frameGeometry()
        qr.moveCenter(
            self.app.primaryScreen().availableGeometry().center())
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationVersion(VERSION)

    mainWindow = MainWindow(app)
    mainWindow.center()
    mainWindow.show()

    sys.exit(app.exec_())
