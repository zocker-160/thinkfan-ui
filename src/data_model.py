# This file defines the data model for the fan curve.

from PyQt6.QtCore import QObject, pyqtSignal

class TempRange(QObject):
    """
    Holds the data for a single temperature range (level) from thinkfan.conf.
    """
    def __init__(self, min_temp=0, max_temp=0, level='auto', parent=None):
        super().__init__(parent)
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.level = level

    def __repr__(self):
        return f"TempRange(Level {self.level}: {self.min_temp}-{self.max_temp}°C)"

class FanCurveModel(QObject):
    """
    Manages the list of TempRange objects that make up the fan curve.
    """
    modelChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ranges = []
        self.create_default_curve()

    def create_default_curve(self):
        """ Creates a default fan curve based on thinkfan.conf format. """
        self._ranges = [
            TempRange(min_temp=0, max_temp=55, level=0),
            TempRange(min_temp=50, max_temp=65, level=2),
            TempRange(min_temp=60, max_temp=75, level=4),
            TempRange(min_temp=70, max_temp=85, level=7),
            TempRange(min_temp=80, max_temp=120, level='Disengaged'),
        ]
        self.modelChanged.emit()

    def get_ranges(self):
        return sorted(self._ranges, key=lambda r: r.min_temp)

    def set_new_ranges(self, new_ranges):
        """ Replaces the entire curve with a new set of ranges. """
        self._ranges = new_ranges
        self.modelChanged.emit()

    def update_range(self, range_to_update, new_min, new_max, new_level):
        """ Universal update function for a TempRange. """
        if range_to_update in self._ranges:
            range_to_update.min_temp = new_min
            range_to_update.max_temp = new_max
            range_to_update.level = new_level
            self.modelChanged.emit()

    def add_range(self):
        """ Adds a new, generic range to the curve, clamped within bounds. """
        if self._ranges:
            last_range = self.get_ranges()[-1]
            new_min = min(max(last_range.max_temp - 5, 0), 115)
            new_max = min(new_min + 10, 120)
            new_level = (last_range.level + 1) if isinstance(last_range.level, int) and last_range.level < 7 else 7
        else:
            new_min, new_max, new_level = (40, 50, 1)
        
        new_range = TempRange(min_temp=new_min, max_temp=new_max, level=new_level)
        self._ranges.append(new_range)
        self.modelChanged.emit()

    def remove_range(self, range_to_remove):
        """ Removes a range from the curve. """
        if range_to_remove in self._ranges:
            self._ranges.remove(range_to_remove)
            self.modelChanged.emit()
