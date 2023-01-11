# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

class Ui_SysTrayIndicator(object):
    def setupSysTrayIndicator(self):
        self.icon = QSystemTrayIcon(QtGui.QIcon(":/icons/linux_packaging/thinkfan-ui.svg"), self)
        self.menu = QMenu()
        self.buildSysTrayIndicatorMenu()
        self.updateSysTrayIndicatorMenu()
        self.icon.show()
        self.icon.setContextMenu(self.menu)

    def buildSysTrayIndicatorMenu(self):
        self.menu.addAction("Fan Full", lambda: self.setFanSpeed("full-speed"))
        self.menu.addAction("Fan 7", lambda: self.setFanSpeed("7"))
        self.menu.addAction("Fan 6", lambda: self.setFanSpeed("6"))
        self.menu.addAction("Fan 5", lambda: self.setFanSpeed("5"))
        self.menu.addAction("Fan 4", lambda: self.setFanSpeed("4"))
        self.menu.addAction("Fan 3", lambda: self.setFanSpeed("3"))
        self.menu.addAction("Fan 2", lambda: self.setFanSpeed("2"))
        self.menu.addAction("Fan 1", lambda: self.setFanSpeed("1"))
        self.menu.addAction("Fan Off", lambda: self.setFanSpeed("0"))
        self.menu.addAction("Fan Auto", lambda: self.setFanSpeed("auto"))
        self.menu.addSeparator()

    def updateSysTrayIndicatorMenu(self):
        fan_info = self.getFanInfo()
        if not fan_info or not fan_info.strip():
            return

        for action in self.menu.actions():
            if ":" in action.text() or "Quit" in action.text() or "ThinkFan UI" in action.text():
                self.menu.removeAction(action)

        tempInfo = self.getTempInfo()
        tempCount = 0
        for line in tempInfo.split("\n"):
            if not line or not line.strip():
                continue
            temp_reading = line.replace(" ", "").replace(":", ":  ")
            self.menu.addAction(temp_reading, self.mainWindow.appear)
            tempCount += 1

        for line in fan_info.split("\n"):
            if "level:" in line:
                fan_level = line.split("level:")[-1].strip()
            if "speed:" in line:
                fan_speed = line.split("speed:")[-1].strip()
        if fan_speed:
            self.menu.addAction(f"Fan RPM: {fan_speed}", self.mainWindow.appear)
        if fan_level:
            self.menu.addAction(f"Fan Level: {fan_level}", self.mainWindow.appear)


        if tempCount == 0:
            self.menu.addAction("ThinkFan UI", self.mainWindow.appear)
        self.menu.addAction("Quit", self.quit)

class Ui_MainWindow(object):
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(543, 334)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/linux_packaging/thinkfan-ui.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setIconSize(QtCore.QSize(32, 32))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMinimumSize(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(50)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.label_temp = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_temp.sizePolicy().hasHeightForWidth())
        self.label_temp.setSizePolicy(sizePolicy)
        self.label_temp.setObjectName("label_temp")
        self.horizontalLayout_3.addWidget(self.label_temp)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setMinimumSize(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setUnderline(True)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.label_fan = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_fan.sizePolicy().hasHeightForWidth())
        self.label_fan.setSizePolicy(sizePolicy)
        self.label_fan.setObjectName("label_fan")
        self.horizontalLayout_4.addWidget(self.label_fan)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setMaximum(7)
        self.slider.setPageStep(1)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.horizontalLayout.addWidget(self.slider)
        self.slider_value = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.slider_value.setFont(font)
        self.slider_value.setObjectName("slider_value")
        self.horizontalLayout.addWidget(self.slider_value)
        self.button_set = QtWidgets.QPushButton(self.centralwidget)
        self.button_set.setObjectName("button_set")
        self.horizontalLayout.addWidget(self.button_set)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.button_auto = QtWidgets.QPushButton(self.centralwidget)
        self.button_auto.setObjectName("button_auto")
        self.horizontalLayout_2.addWidget(self.button_auto)
        self.button_full = QtWidgets.QPushButton(self.centralwidget)
        self.button_full.setObjectName("button_full")
        self.horizontalLayout_2.addWidget(self.button_full)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 543, 34))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.retranslateUi()
        self.slider.valueChanged['int'].connect(self.slider_value.setNum)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "ThinkFan UI"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p>CPU temp info:</p></body></html>"))
        self.label_temp.setText(_translate("MainWindow", "missing data"))
        self.label_2.setText(_translate("MainWindow", "FAN info:"))
        self.label_fan.setText(_translate("MainWindow", "missing data"))
        self.slider_value.setText(_translate("MainWindow", "0"))
        self.button_set.setText(_translate("MainWindow", "set"))
        self.button_auto.setText(_translate("MainWindow", "auto (recommended)"))
        self.button_full.setText(_translate("MainWindow", "FULL THROTTLE"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p>ThinkFan UI by zocker_160 | <a href=\"https://github.com/zocker-160/thinkfan-ui\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/zocker-160/thinkfan-ui</span></a><span style=\" color:#000000;\"> | $$$</span></p></body></html>"))
import ui.qt_ressources_rc
