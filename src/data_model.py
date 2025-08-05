# src/data_model.py

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
    Manages a dictionary of fan curves, where each key is a sensor
    name and each value is a list of TempRange objects.
    """
    modelChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._curves = {}
        self._active_curve_key = None
        self.create_default_curve()

    def create_default_curve(self):
        """ Creates a default single fan curve. """
        default_ranges = [
            TempRange(min_temp=0, max_temp=55, level=0),
            TempRange(min_temp=50, max_temp=65, level=2),
            TempRange(min_temp=60, max_temp=75, level=4),
            TempRange(min_temp=70, max_temp=85, level=7),
            TempRange(min_temp=80, max_temp=120, level='Disengaged'),
        ]
        self._curves = {"Default": default_ranges}
        self._active_curve_key = "Default"
        self.modelChanged.emit()

    def get_ranges(self):
        """ Returns the ranges for the currently active curve. """
        if self._active_curve_key and self._active_curve_key in self._curves:
            return sorted(self._curves[self._active_curve_key], key=lambda r: r.min_temp)
        return []

    def get_all_curves(self):
        """ Returns the entire dictionary of curves. """
        return self._curves

    def get_curve_keys(self):
        """ Returns a list of sensor names for the available curves. """
        return sorted(self._curves.keys())

    def get_active_curve_key(self):
        """ Returns the key for the currently active curve. """
        return self._active_curve_key

    def set_active_curve(self, key):
        """ Sets the active curve and notifies the view to update. """
        if key in self._curves:
            self._active_curve_key = key
            self.modelChanged.emit()

    def set_curves(self, new_curves_dict):
        """ Replaces the entire set of curves with a new dictionary. """
        if not new_curves_dict:
            self.create_default_curve()
            return
        self._curves = new_curves_dict
        # Set the first key as the default active one
        self._active_curve_key = list(self._curves.keys())[0]
        self.modelChanged.emit()

    def update_range(self, range_to_update, new_min, new_max, new_level):
        """ Universal update function for a TempRange in the active curve. """
        active_curve = self._curves.get(self._active_curve_key, [])
        if range_to_update in active_curve:
            range_to_update.min_temp = new_min
            range_to_update.max_temp = new_max
            range_to_update.level = new_level
            self.modelChanged.emit()

    def add_range(self):
        """ Adds a new, generic range to the active curve. """
        active_curve = self._curves.get(self._active_curve_key, [])
        if active_curve:
            last_range = sorted(active_curve, key=lambda r: r.min_temp)[-1]
            new_min = min(max(last_range.max_temp - 5, 0), 115)
            new_max = min(new_min + 10, 120)
            new_level = (last_range.level + 1) if isinstance(last_range.level, int) and last_range.level < 7 else 7
        else:
            new_min, new_max, new_level = (40, 50, 1)
        
        new_range = TempRange(min_temp=new_min, max_temp=new_max, level=new_level)
        active_curve.append(new_range)
        self.modelChanged.emit()

    def remove_range(self, range_to_remove):
        """ Removes a range from the active curve. """
        active_curve = self._curves.get(self._active_curve_key, [])
        if range_to_remove in active_curve:
            active_curve.remove(range_to_remove)
            self.modelChanged.emit()
