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
        # This is the key change: update the menu right before it is shown.
        self.menu.aboutToShow.connect(self.updateIndicatorMenu)

        self.buildIndicatorMenu() # Build the static parts of the menu once.

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

        # This section will be dynamically populated by updateIndicatorMenu
        self.menu.addSection("Sensor Values")
        # Add a single separator that we will insert actions before
        self.sensor_separator = self.menu.addSeparator()

        self.menu.addSection("Controls")
        self.menu.addMenu(self.fanSpeedMenu)
        self.menu.addAction("Show/Hide", self.mainWindow.toggleAppear)
        self.menu.addSeparator()

        self.menu.addAction("Exit", self.app.quit)

    def updateIndicatorMenu(self):
        """Clears old sensor data and populates the menu with fresh data."""
        # --- Clear old dynamic entries ---
        for action in self.dynamic_actions:
            self.menu.removeAction(action)
        self.dynamic_actions.clear()


        # --- Populate with new data ---
        temp_info = self.getTempInfo()
        fan_info = self.getFanInfo()
        all_info = {**temp_info, **fan_info}
        
        # Insert new sensor actions before the separator
        if all_info:
            for label, value in sorted(all_info.items()):
                action_text = f"{label}: {value}"
                new_action = QAction(action_text, self)
                new_action.triggered.connect(self.mainWindow.appear)
                self.menu.insertAction(self.sensor_separator, new_action)
                self.dynamic_actions.append(new_action) # Keep track of the new action
        else:
            # Show a placeholder if no data is available
            no_data_action = QAction("No sensor data", self)
            no_data_action.setEnabled(False)
            self.menu.insertAction(self.sensor_separator, no_data_action)
            self.dynamic_actions.append(no_data_action)
