from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu


class QApp_SysTrayIndicator(QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamic_actions = [] # List to keep track of sensor actions

    def setupSysTrayIndicator(self):
        self.icon = QSystemTrayIcon(QIcon.fromTheme("thinkfan-ui"), self)
        self.icon.activated.connect(self.mainWindow.toggleAppear)

        self.menu = QMenu()
        self.menu.aboutToShow.connect(self.updateIndicatorMenu)

        self.buildIndicatorMenu()

        self.icon.setContextMenu(self.menu)
        self.icon.show()

    def buildIndicatorMenu(self):
        """Builds the static parts of the menu that don't need updates."""
        self.fanSpeedMenu = QMenu(title="Fan Level")
        self.fanSpeedMenu.addAction("Auto", lambda: self.setFanSpeed("auto"))
        self.fanSpeedMenu.addAction("Full-speed", lambda: self.setFanSpeed("full-speed"))
        for i in range(7, -1, -1):
            level = str(i)
            label = f"Level {level}" if i > 0 else "Off (Level 0)"
            self.fanSpeedMenu.addAction(label, lambda l=level: self.setFanSpeed(l))

        self.menu.addSection("Sensor Values")
        self.sensor_separator = self.menu.addSeparator()

        self.menu.addSection("Controls")
        self.menu.addMenu(self.fanSpeedMenu)
        self.menu.addAction("Show/Hide", self.mainWindow.toggleAppear)
        self.menu.addSeparator()

        self.menu.addAction("Exit", self.app.quit)

    def updateIndicatorMenu(self):
        """
        Clears old sensor data and populates the menu with fresh data
        using the unified data collection method.
        """
        for action in self.dynamic_actions:
            self.menu.removeAction(action)
        self.dynamic_actions.clear()

        all_data = self.get_all_sensor_data()
        
        display_info = {}
        display_info.update(all_data.get('temps', {}))
        display_info.update(all_data.get('fans', {}))
        display_info.update(all_data.get('fan_state', {}))

        if display_info and not display_info.get("Error"):
            for label, value in sorted(display_info.items()):
                # Add units for display
                if label in all_data.get('temps', {}):
                    action_text = f"{label}: {value}°C"
                elif label in all_data.get('fans', {}):
                    # --- FIX --- Cast fan speed value to int to remove decimal
                    action_text = f"{label}: {int(value)} RPM"
                else:
                    action_text = f"{label}: {value}"

                new_action = QAction(action_text, self)
                new_action.triggered.connect(self.mainWindow.appear)
                self.menu.insertAction(self.sensor_separator, new_action)
                self.dynamic_actions.append(new_action)
        else:
            error_msg = display_info.get("Error", "No sensor data")
            no_data_action = QAction(error_msg, self)
            no_data_action.setEnabled(False)
            self.menu.insertAction(self.sensor_separator, no_data_action)
            self.dynamic_actions.append(no_data_action)
