from PyQt5 import QtGui
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu

class QApp_SysTrayIndicator(object):
    def setupSysTrayIndicator(self):
        self.icon = QSystemTrayIcon(QtGui.QIcon(":/icons/linux_packaging/thinkfan-ui.svg"), self)
        self.menu = QMenu()
        self.buildSysTrayIndicatorMenu()
        self.updateSysTrayIndicatorMenu()
        self.icon.show()
        self.icon.setContextMenu(self.menu)

    def buildSysTrayIndicatorMenu(self):
        self.fanSpeedMenu = QMenu(title="Fan Level:")
        self.fanSpeedMenu.addAction("Fan Auto", lambda: self.setFanSpeed("auto"))
        self.fanSpeedMenu.addAction("Fan Full", lambda: self.setFanSpeed("full-speed"))
        self.fanSpeedMenu.addAction("Fan 7", lambda: self.setFanSpeed("7"))
        self.fanSpeedMenu.addAction("Fan 6", lambda: self.setFanSpeed("6"))
        self.fanSpeedMenu.addAction("Fan 5", lambda: self.setFanSpeed("5"))
        self.fanSpeedMenu.addAction("Fan 4", lambda: self.setFanSpeed("4"))
        self.fanSpeedMenu.addAction("Fan 3", lambda: self.setFanSpeed("3"))
        self.fanSpeedMenu.addAction("Fan 2", lambda: self.setFanSpeed("2"))
        self.fanSpeedMenu.addAction("Fan 1", lambda: self.setFanSpeed("1"))
        self.fanSpeedMenu.addAction("Fan Off", lambda: self.setFanSpeed("0"))

        self.menu.addMenu(self.fanSpeedMenu)
        self.menu.addAction("Set Fan Auto", lambda: self.setFanSpeed("auto"))

        self.menu.addSeparator()

        tempInfo = self.getTempInfo()
        for line in tempInfo.split("\n"):
            if not line or not line.strip():
                continue
            temp_reading = line.replace(" ", "").replace(":", ":  ")
            self.menu.addAction(temp_reading, self.mainWindow.appear)

        self.menu.addAction(f"Fan RPM: ", self.mainWindow.appear)
        self.menu.addAction("Quit", self.quit)

    def updateSysTrayIndicatorMenu(self):
        fan_info = self.getFanInfo()
        if not fan_info or not fan_info.strip():
            return

        actions = {action.text().split(":")[0]: action
                    for action in self.menu.actions()
                    if ":" in action.text()}

        tempInfo = self.getTempInfo()
        for line in tempInfo.split("\n"):
            if not line or not line.strip():
                continue
            temp_reading = line.replace(" ", "")
            reading_name, reading_value = temp_reading.split(":")
            if reading_name in actions:
                actions[reading_name].setText(f"{reading_name}: {reading_value}")

        for line in fan_info.split("\n"):
            if "level:" in line:
                fan_level = line.split("level:")[-1].strip()
            if "speed:" in line:
                fan_speed = line.split("speed:")[-1].strip()
        if fan_speed and "Fan RPM" in actions:
            actions["Fan RPM"].setText(f"Fan RPM: {fan_speed}")
        if fan_level and "Fan Level" in actions:
            actions["Fan Level"].setText(f"Fan Level: {fan_level}")