# This file will contain the implementation of the fan curve editor widget.

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QPainter, QColor, QTransform, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer

class PointItem(QGraphicsEllipseItem):
    """ A draggable point on the graph. """
    def __init__(self, x, y, size=20): # Increased default size
        super().__init__(-size/2, -size/2, size, size)
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

    def itemChange(self, change, value):
        if self.scene():
            if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
                new_pos = value
                scene = self.scene()
                clamped_x = max(0, min(new_pos.x(), scene.scene_width))
                clamped_y = max(0, min(new_pos.y(), scene.scene_height))
                clamped_pos = QPointF(clamped_x, clamped_y)
                # Update the tooltip's text and position in real-time during a drag
                self.scene().update_tooltip(clamped_pos)
                return clamped_pos

            if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
                self.scene().update_lines()
        
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        # Show and update the tooltip instantly on hover
        self.scene().update_tooltip(self.pos())
        self.scene().tooltip.show()
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event):
        # Update tooltip in real-time as the mouse moves over the point
        self.scene().update_tooltip(self.pos())
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        # Hide the tooltip when the mouse leaves
        self.scene().tooltip.hide()
        super().hoverLeaveEvent(event)


class FanCurveScene(QGraphicsScene):
    """ A custom scene to manage points and lines. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []
        self.lines = []
        
        self.scene_width = 1000
        self.scene_height = 1000
        
        self.data_x_min, self.data_x_max = 30, 100
        self.data_y_min, self.data_y_max = 0, 100
        
        self.draw_chart_area()
        
        initial_points = [(40, 0), (65, 50), (85, 100)]
        for x, y in initial_points:
            scene_x, scene_y = self.map_data_to_coords(x, y)
            self.add_point(scene_x, scene_y)
            
        self.update_lines()

        # Create a single tooltip item for the scene, initially hidden
        self.tooltip = QGraphicsTextItem()
        self.tooltip.hide()
        self.addItem(self.tooltip)

    def map_data_to_coords(self, data_x, data_y):
        x_range = self.data_x_max - self.data_x_min
        y_range = self.data_y_max - self.data_y_min
        scene_x = ((data_x - self.data_x_min) / x_range) * self.scene_width
        scene_y = self.scene_height - (((data_y - self.data_y_min) / y_range) * self.scene_height)
        return scene_x, scene_y

    def map_coords_to_data(self, scene_x, scene_y):
        x_range = self.data_x_max - self.data_x_min
        y_range = self.data_y_max - self.data_y_min
        data_x = ((scene_x / self.scene_width) * x_range) + self.data_x_min
        data_y = ((self.scene_height - scene_y) / self.scene_height) * y_range + self.data_y_min
        return data_x, data_y

    def update_tooltip(self, scene_pos):
        data_x, data_y = self.map_coords_to_data(scene_pos.x(), scene_pos.y())
        tooltip_text = f"{int(data_x)}°C\n{int(round(data_y))}%"
        self.tooltip.setPlainText(tooltip_text)
        # Position the tooltip slightly above and to the right of the point
        self.tooltip.setPos(scene_pos.x() + 10, scene_pos.y() - 40)

    def draw_chart_area(self):
        pen_grid = QPen(QColor("#d0d0d0"))
        label_font = QFont()
        label_font.setPointSize(18)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        
        for i in range(self.data_y_min, self.data_y_max + 1, 10):
            _, y_scene = self.map_data_to_coords(self.data_x_min, i)
            self.addLine(0, y_scene, self.scene_width, y_scene, pen_grid)
            text = self.addText(f"{i}%")
            text.setFont(label_font)
            text.setPos(-80, y_scene - 15)

        for i in range(self.data_x_min, self.data_x_max + 1, 10):
            x_scene, _ = self.map_data_to_coords(i, self.data_y_min)
            self.addLine(x_scene, 0, x_scene, self.scene_height, pen_grid)
            text = self.addText(f"{i}°C")
            text.setFont(label_font)
            text.setPos(x_scene - 20, self.scene_height + 15)

        y_title = self.addText("Speed")
        y_title.setFont(title_font)
        y_title.setRotation(-90)
        y_title.setPos(-150, self.scene_height / 2 + 80)

        x_title = self.addText("Temperature")
        x_title.setFont(title_font)
        x_title.setPos(self.scene_width / 2 - 120, self.scene_height + 60)

    def add_point(self, x, y):
        point = PointItem(x, y)
        self.points.append(point)
        self.addItem(point)

    def update_lines(self):
        for line in self.lines:
            self.removeItem(line)
        self.lines.clear()
        if len(self.points) > 1:
            sorted_points = sorted(self.points, key=lambda p: p.pos().x())
            for i in range(len(sorted_points) - 1):
                p1 = sorted_points[i].pos()
                p2 = sorted_points[i+1].pos()
                line = self.addLine(p1.x(), p1.y(), p2.x(), p2.y(), QPen(Qt.GlobalColor.gray))
                self.lines.append(line)

class FanCurveEditor(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = FanCurveScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
    def fit_view(self):
        self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        self.fit_view()
        super().resizeEvent(event)

    def showEvent(self, event):
        QTimer.singleShot(0, self.fit_view)
        super().showEvent(event)
