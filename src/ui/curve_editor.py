# This file will contain the implementation of the fan curve editor widget.

import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout

# Custom ViewBox to override the default mouse drag behavior (panning)
class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setMouseMode(self.RectMode) # Change mouse mode to rectangle selection

    # Override the mouse drag event to prevent panning
    def mouseDragEvent(self, ev, axis=None):
        ev.ignore() # Let child items handle the event

class FanCurveEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Main Layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- Create Plot Widget with our CustomViewBox ---
        self.graphWidget = pg.PlotWidget(viewBox=CustomViewBox())
        self.layout.addWidget(self.graphWidget)

        # --- Configure Plot Appearance ---
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Fan Curve", color="b", size="15pt")
        styles = {"color": "#000", "font-size": "12px"}
        self.graphWidget.setLabel("left", "Fan Speed (%)", **styles)
        self.graphWidget.setLabel("bottom", "Temperature (°C)", **styles)
        self.graphWidget.setXRange(30, 100)
        self.graphWidget.setYRange(0, 100)
        self.graphWidget.showGrid(x=True, y=True)

        # --- Create an interactive graph item using GraphItem ---
        pos = np.array([
            [40.0, 0.0], 
            [65.0, 50.0], 
            [85.0, 100.0]
        ], dtype=float)

        adj = np.array([[0, 1], [1, 2]], dtype=int)

        self.graph = pg.GraphItem(
            pos=pos, 
            adj=adj, 
            symbol='o', 
            size=15, 
            symbolBrush=pg.mkBrush(0, 0, 255, 120),
            movable=True
        )
        
        # Restore hover effect
        self.graph.scatter.opts['hoverable'] = True
        self.graph.scatter.opts['hoverBrush'] = pg.mkBrush(0, 0, 255)
        
        self.graphWidget.addItem(self.graph)

        # Connect a signal that fires after a point has been moved
        self.graph.scatter.sigPlotChanged.connect(self.points_moved)

    def points_moved(self, scatter_item):
        positions = self.graph.pos()
        print("Curve points updated:", positions.tolist())
