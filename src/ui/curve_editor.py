# This file defines the interactive graphical components for the fan curve
# editor, including the draggable points, the graph scene, and the view
# that contains them.

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PyQt6.QtGui import QBrush, QPen, QPainter, QColor, QTransform, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer

class RangePointItem(QGraphicsEllipseItem):
    """ A draggable point representing either the min or max temp of a TempRange. """
    def __init__(self, range_data, point_type, size=15):
        super().__init__(-size/2, -size/2, size, size)
        self.range_data = range_data
        self.point_type = point_type
        
        self.setBrush(QBrush(Qt.GlobalColor.cyan))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

    def mouseReleaseEvent(self, event):
        """ On mouse release, finalize the position and update the model. """
        super().mouseReleaseEvent(event)
        scene = self.scene()
        if not scene: return
        
        new_temp, new_percent = scene.map_coords_to_data(self.pos().x(), self.pos().y())
        new_level = scene.map_y_percent_to_level(new_percent)
        min_temp, max_temp = self.range_data.min_temp, self.range_data.max_temp
        
        if self.point_type == 'min':
            new_min = int(round(new_temp))
            new_max = max_temp if new_min <= max_temp else new_min
            scene.model.update_range(self.range_data, new_min, new_max, new_level)
        else: # 'max'
            new_max = int(round(new_temp))
            new_min = min_temp if new_max >= min_temp else new_max
            scene.model.update_range(self.range_data, new_min, new_max, new_level)

    def itemChange(self, change, value):
        if self.scene() and change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            new_pos = value
            scene = self.scene()
            
            x_min_scene, y_max_scene = scene.map_data_to_coords(scene.data_x_min, scene.data_y_min)
            x_max_scene, y_min_scene = scene.map_data_to_coords(scene.data_x_max, scene.data_y_max)

            clamped_x = max(x_min_scene, min(new_pos.x(), x_max_scene))
            clamped_y = max(y_min_scene, min(new_pos.y(), y_max_scene))
            
            clamped_pos = QPointF(clamped_x, clamped_y)
            
            scene.update_tooltip(clamped_pos)
            scene.update_lines(dragged_item=self, new_pos=clamped_pos)
            return clamped_pos
        
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        scene = self.scene()
        if not scene: return
        y_percent = scene.level_to_y_percent(self.range_data.level)
        _, y_coord = scene.map_data_to_coords(0, y_percent)
        self.setY(y_coord)
        scene.update_tooltip(self.pos())
        scene.tooltip.show()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.scene().tooltip.hide()
        super().hoverLeaveEvent(event)

class FanCurveScene(QGraphicsScene):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.graph_items = []
        
        self.scene_width = 1000
        self.scene_height = 1000
        
        self.data_x_min, self.data_x_max = 0, 120 # CORRECTED: Start X-axis at 0
        self.data_y_min, self.data_y_max = 0, 120
        
        self.draw_chart_area()

        self.tooltip = QGraphicsTextItem()
        self.tooltip.hide()
        self.addItem(self.tooltip)

        self.model.modelChanged.connect(self.update_view_from_model)
        self.update_view_from_model()

    def level_to_y_percent(self, level):
        if str(level) == "Disengaged": return 120
        if str(level) == "auto": return 50
        return (int(level) / 7.0) * 100

    def map_y_percent_to_level(self, y_percent):
        if y_percent >= 110: return 'Disengaged'
        level = round((y_percent / 100) * 7)
        return min(int(level), 7)

    def map_data_to_coords(self, data_x, data_y_percent):
        x_range = self.data_x_max - self.data_x_min
        y_range = self.data_y_max - self.data_y_min
        if x_range == 0 or y_range == 0: return 0, 0
        
        scene_x = ((data_x - self.data_x_min) / x_range) * self.scene_width
        scene_y = self.scene_height - (((data_y_percent - self.data_y_min) / y_range) * self.scene_height)
        return scene_x, scene_y

    def map_coords_to_data(self, scene_x, scene_y):
        x_range = self.data_x_max - self.data_x_min
        y_range = self.data_y_max - self.data_y_min
        if self.scene_width == 0 or self.scene_height == 0: return 0, 0

        data_x = ((scene_x / self.scene_width) * x_range) + self.data_x_min
        data_y_percent = ((self.scene_height - scene_y) / self.scene_height) * y_range + self.data_y_min
        return data_x, data_y_percent

    def update_view_from_model(self):
        self.clear_graph_items()
        sorted_ranges = self.model.get_ranges()

        for range_data in sorted_ranges:
            self.create_graph_items_for_range(range_data)
        
        self.update_lines()

    def clear_graph_items(self):
        for min_pt, max_pt, line, connector in self.graph_items:
            if min_pt: self.removeItem(min_pt)
            if max_pt: self.removeItem(max_pt)
            if line: self.removeItem(line)
            if connector: self.removeItem(connector)
        self.graph_items.clear()

    def create_graph_items_for_range(self, range_data):
        y_percent = self.level_to_y_percent(range_data.level)
        min_x, y_scene = self.map_data_to_coords(range_data.min_temp, y_percent)
        max_x, _ = self.map_data_to_coords(range_data.max_temp, y_percent)

        min_point = RangePointItem(range_data, 'min')
        min_point.setPos(min_x, y_scene)
        
        max_point = RangePointItem(range_data, 'max')
        max_point.setPos(max_x, y_scene)
        
        line = self.addLine(min_x, y_scene, max_x, y_scene, QPen(QColor("darkCyan"), 2))
        
        self.addItem(min_point)
        self.addItem(max_point)
        self.graph_items.append([min_point, max_point, line, None])

    def update_lines(self, dragged_item=None, new_pos=None):
        sorted_items = sorted(self.graph_items, key=lambda item: item[0].pos().x())
        
        for i in range(len(sorted_items)):
             if sorted_items[i][3]:
                self.removeItem(sorted_items[i][3])
                sorted_items[i][3] = None

        for i in range(len(sorted_items) - 1):
            current_max_pt = sorted_items[i][1]
            next_min_pt = sorted_items[i+1][0]
            p1 = current_max_pt.pos()
            p2 = next_min_pt.pos()

            if dragged_item and current_max_pt == dragged_item: p1 = new_pos
            if dragged_item and next_min_pt == dragged_item: p2 = new_pos
            
            connector = self.addLine(p1.x(), p1.y(), p2.x(), p2.y(), QPen(QColor("darkCyan"), 2))
            sorted_items[i][3] = connector

    def update_tooltip(self, scene_pos, level=None):
        data_x, data_y = self.map_coords_to_data(scene_pos.x(), scene_pos.y())
        if level is None:
            level = self.map_y_percent_to_level(data_y)
        tooltip_text = f"{int(round(data_x))}°C\nLevel: {level}"
        self.tooltip.setPlainText(tooltip_text)
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

        # CORRECTED: Use the class attribute for the loop range
        for i in range(self.data_x_min, self.data_x_max + 1, 10):
            x_scene, _ = self.map_data_to_coords(i, self.data_y_min)
            self.addLine(x_scene, 0, x_scene, self.scene_height, pen_grid)
            text = self.addText(f"{i}°C")
            text.setFont(label_font)
            text.setPos(x_scene - 20, self.scene_height + 15)

        y_title = self.addText("Speed (%)")
        y_title.setFont(title_font)
        y_title.setRotation(-90)
        y_title.setPos(-150, self.scene_height / 2 + 100)

        x_title = self.addText("Temperature (°C)")
        x_title.setFont(title_font)
        x_title.setPos(self.scene_width / 2 - 120, self.scene_height + 60)

class FanCurveEditor(QGraphicsView):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.scene = FanCurveScene(self.model, self)
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
