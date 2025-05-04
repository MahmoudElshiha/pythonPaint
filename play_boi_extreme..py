import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QColorDialog, QFileDialog, QSlider, 
                            QLabel, QSpinBox, QButtonGroup, QRadioButton, QGridLayout)
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QImage, QIcon, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from collections import deque
import os

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StaticContents)
        self._image = None
        self._brush_color = Qt.black
        self._brush_size = 5
        self._last_point = QPoint()
        self._path = QPainterPath()
        self._drawing = False
        self._current_tool = "pen"  # "pen", "rectangle", "ellipse", "line", "fill"
        self._start_point = QPoint()
        self._undo_stack = []
        self._redo_stack = []
        self.clear_canvas()

    def clear_canvas(self):
        self._redo_stack.append(self._image)  # temporary fix
        self._image = self._create_blank_image()
        self.update()

    def save_undo_state(self):
        if self._image is None or self._image.isNull():
            return
        self._undo_stack.append(self._image.copy())
        self._redo_stack.clear()
        
    def is_image_blank(self):
        if self._image is None or self._image.isNull():
            return True
        white = QImage(self._image.size(), self._image.format())
        white.fill(Qt.white)
        return self._image == white

    def preview_draw_line_midpoint(self, painter, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            painter.drawPoint(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    def preview_draw_circle_midpoint(self, painter, xc, yc, r):
        if r <= 0:
            return

        x = 0
        y = r
        d = 1 - r

        self._draw_circle_points(painter, xc, yc, x, y)

        while x < y:
            x += 1
            if d < 0:
                d += 2 * x + 1
            else:
                y -= 1
                d += 2 * (x - y) + 1
            self._draw_circle_points(painter, xc, yc, x, y)

    def _draw_circle_points(self, painter, xc, yc, x, y):
        painter.drawPoint(xc + x, yc + y)
        painter.drawPoint(xc - x, yc + y)
        painter.drawPoint(xc + x, yc - y)
        painter.drawPoint(xc - x, yc - y)
        painter.drawPoint(xc + y, yc + x)
        painter.drawPoint(xc - y, yc + x)
        painter.drawPoint(xc + y, yc - x)
        painter.drawPoint(xc - y, yc - x)

    def preview_draw_ellipse_midpoint(self, painter, xc, yc, rx, ry):
        if rx <= 0 or ry <= 0:
            return
            
        x, y = 0, ry
        rx2, ry2 = rx * rx, ry * ry
        two_rx2 = 2 * rx2
        two_ry2 = 2 * ry2
        
        # Region 1
        p = (ry2 - (rx2 * ry) + (rx2 // 4))  # Scaled by 4 to avoid floats
        while (two_ry2 * x) <= (two_rx2 * y):
            painter.drawPoint(xc + x, yc + y)
            painter.drawPoint(xc - x, yc + y)
            painter.drawPoint(xc + x, yc - y)
            painter.drawPoint(xc - x, yc - y)
            x += 1
            if p < 0:
                p += two_ry2 * x + ry2
            else:
                y -= 1
                p += two_ry2 * x - two_rx2 * y + ry2

        # Region 2
        p = (ry2 * (x + 0.5)**2 + rx2 * (y - 1)**2 - rx2 * ry2)
        while y >= 0:
            painter.drawPoint(xc + x, yc + y)
            painter.drawPoint(xc - x, yc + y)
            painter.drawPoint(xc + x, yc - y)
            painter.drawPoint(xc - x, yc - y)
            y -= 1
            if p > 0:
                p -= two_rx2 * y + rx2
            else:
                x += 1
                p += two_ry2 * x - two_rx2 * y + rx2

    def preview_draw_rectangle(self, painter, x0, y0, x1, y1):
        x_min, x_max = min(x0, x1), max(x0, x1)
        y_min, y_max = min(y0, y1), max(y0, y1)
        # Draw the top and bottom borders
        for x in range(x_min, x_max + 1):
            painter.drawPoint(x, y_min)
            painter.drawPoint(x, y_max)
        # Draw the left and right borders
        for y in range(y_min, y_max + 1):
            painter.drawPoint(x_min, y)
            painter.drawPoint(x_max, y)


    def _create_blank_image(self):
        image = None
        if image is None or image.size() != self.size():
            if self.size().width() > 0 and self.size().height() > 0:
                image = QImage(self.size(), QImage.Format_RGB32)
                image.fill(Qt.white)
        return image

    def set_pixel(self, x, y):
        if 0 <= x < self._image.width() and 0 <= y < self._image.height():
            painter = QPainter(self._image)
            painter.setPen(self._brush_color)
            painter.drawPoint(x, y)
            painter.end()

    def save_state(self):
        if self._image and not self._image.isNull():
            path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
            if path:
                self._image.save(path, "PNG")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self._image, self._image.rect())

        if self._drawing and self._current_tool != "pen":
            preview_painter = painter  # using the same painter for preview
            preview_painter.setPen(QPen(self._brush_color, self._brush_size, 
                                        Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            if self._current_tool == "rectangle":
                self.preview_draw_rectangle(preview_painter,
                                            self._start_point.x(), self._start_point.y(),
                                            self._last_point.x(), self._last_point.y())
            elif self._current_tool == "ellipse":
                xc = (self._start_point.x() + self._last_point.x()) // 2
                yc = (self._start_point.y() + self._last_point.y()) // 2
                rx = abs(self._last_point.x() - self._start_point.x()) // 2
                ry = abs(self._last_point.y() - self._start_point.y()) // 2
                self.preview_draw_ellipse_midpoint(preview_painter, xc, yc, rx, ry)
            elif self._current_tool == "line":
                self.preview_draw_line_midpoint(preview_painter,
                                                self._start_point.x(), self._start_point.y(),
                                                self._last_point.x(), self._last_point.y())
            elif self._current_tool == "circle":
                xc = (self._start_point.x() + self._last_point.x()) // 2
                yc = (self._start_point.y() + self._last_point.y()) // 2
                r = int((abs(self._last_point.x() - self._start_point.x())**2 +
                        abs(self._last_point.y() - self._start_point.y())**2) ** 0.5) // 2
                self.preview_draw_circle_midpoint(preview_painter, xc, yc, r)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._start_point = event.pos()
            self._last_point = event.pos()
            
            if self._current_tool == "pen":
                self.save_undo_state()
                # Create a temporary painter just for the initial point
                painter = QPainter(self._image)
                painter.setPen(QPen(self._brush_color, self._brush_size, 
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPoint(self._last_point)
                painter.end()
                self.update()

            if self._current_tool == "fill":
                x, y = event.pos().x(), event.pos().y()
                target_color = self._image.pixelColor(x, y)
                self.flood_fill(x, y, target_color, self._brush_color)
                self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drawing:
            if self._current_tool == "pen":
                painter = QPainter(self._image)
                painter.setPen(QPen(self._brush_color, self._brush_size, 
                                  Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self._last_point, event.pos())
                painter.end()
                self._last_point = event.pos()
            else:
                self._last_point = event.pos()
            
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drawing:
            if self._current_tool != "pen":
                self.save_undo_state()
                painter = QPainter(self._image)
                painter.setPen(QPen(self._brush_color, self._brush_size, 
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                
                rect = QRect(self._start_point, event.pos())
                
                if self._current_tool == "rectangle":
                    painter.drawRect(rect)
                elif self._current_tool == "ellipse":
                    painter.drawEllipse(rect)
                elif self._current_tool == "line":
                    painter.drawLine(self._start_point, event.pos())
                elif self._current_tool == "circle":
                    xc = (self._start_point.x() + event.pos().x()) // 2
                    yc = (self._start_point.y() + event.pos().y()) // 2
                    r = int(((event.pos().x() - self._start_point.x())**2 +
                            (event.pos().y() - self._start_point.y())**2) ** 0.5) // 2
                    self.preview_draw_circle_midpoint(painter, xc, yc, r)

                painter.end()
            
            self._drawing = False
            self.update()

    # def resizeEvent(self, event):
    #     if self._image is not None:
    #         new_image = QImage(self.size(), QImage.Format_RGB32)
    #         new_image.fill(Qt.white)

    #         painter = QPainter(new_image)
    #         painter.drawImage(0, 0, self._image)
    #         painter.end()

    #         self._image = new_image
    #     else:
    #         self._image = self._create_blank_image()

    #     super().resizeEvent(event)

    def resizeEvent(self, event):
        if self._image is None or self._image.size() != self.size():
            self.clear_canvas()
        super().resizeEvent(event)

    def undo(self):
        if self.is_image_blank():
            return
        self._redo_stack.append(self._image.copy())
        self._image = self._undo_stack.pop()
        self.update()

    def redo(self):
        if not self._redo_stack or self._image is None:
            return
        self._undo_stack.append(self._image.copy())
        self._image = self._redo_stack.pop()
        self.update()

    def flood_fill(self, x, y, target_color, replacement_color):
        if target_color == replacement_color:
            return

        width = self._image.width()
        height = self._image.height()

        target_rgb = QColor(target_color).rgb()
        replacement_rgb = QColor(replacement_color).rgb()

        # quick escape if clicked pixel doesn’t match target
        if self._image.pixel(x, y) != target_rgb:
            return

        from collections import deque
        queue = deque()
        queue.append((x, y))

        while queue:
            cx, cy = queue.popleft()

            if not (0 <= cx < width and 0 <= cy < height):
                continue
            if self._image.pixel(cx, cy) != target_rgb:
                continue

            # move left as far as target_color goes
            west = cx
            while west >= 0 and self._image.pixel(west, cy) == target_rgb:
                west -= 1
            west += 1

            # move right as far as target_color goes
            east = cx
            while east < width and self._image.pixel(east, cy) == target_rgb:
                east += 1
            east -= 1

            for i in range(west, east + 1):
                self._image.setPixel(i, cy, replacement_rgb)

                # check above and below
                if cy > 0 and self._image.pixel(i, cy - 1) == target_rgb:
                    queue.append((i, cy - 1))
                if cy < height - 1 and self._image.pixel(i, cy + 1) == target_rgb:
                    queue.append((i, cy + 1))

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, color):
        self._brush_color = color

    @property
    def brush_size(self):
        return self._brush_size

    @brush_size.setter
    def brush_size(self, size):
        self._brush_size = size

    @property
    def current_tool(self):
        return self._current_tool

    @current_tool.setter
    def current_tool(self, tool):
        self._current_tool = tool


class PythonPaint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonPaint")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Horizontal layout

        # Create canvas
        self.canvas = Canvas()
        main_layout.addWidget(self.canvas)

        # Create sidebar widget
        sidebar = QWidget()
        sidebar.setFixedWidth(200)  # Set the width of the sidebar
        sidebar_layout = QVBoxLayout(sidebar)

        # Color button
        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.choose_color)
        sidebar_layout.addWidget(self.color_btn)

        # Brush size controls
        sidebar_layout.addWidget(QLabel("Brush Size:"))

        self.brush_slider = QSlider(Qt.Horizontal)
        self.brush_slider.setMinimum(1)
        self.brush_slider.setMaximum(50)
        self.brush_slider.setValue(5)
        self.brush_slider.valueChanged.connect(self.update_brush_size)
        sidebar_layout.addWidget(self.brush_slider)

        self.brush_spin = QSpinBox()
        self.brush_spin.setMinimum(1)
        self.brush_spin.setMaximum(50)
        self.brush_spin.setValue(5)
        self.brush_spin.valueChanged.connect(self.update_brush_size)
        sidebar_layout.addWidget(self.brush_spin)

        # Tool selection
        sidebar_layout.addWidget(QLabel("Tools:"))

        self.tool_group = QButtonGroup()
        self.tool_group.setExclusive(True)

        tool_icons = {
            "pen": "./pythonPaint/icons/pen.svg",
            "rectangle": "./pythonPaint/icons/rectangle.svg",
            "fill": "./pythonPaint/icons/fill.svg",
            "circle": "./pythonPaint/icons/circle.svg",
            "ellipse": "./pythonPaint/icons/ellipse.png",
            "line": "./pythonPaint/icons/line.png"
        }
        tools = ["pen", "rectangle", "ellipse", "line", "fill", "circle"]

        # Create a grid layout to hold the tool buttons
        tools_grid = QGridLayout()

        for i, tool in enumerate(tools):
            btn = QPushButton()
            btn.setIcon(QIcon(tool_icons[tool]))
            btn.setIconSize(QSize(35, 40))
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            self.tool_group.addButton(btn, i)

            # Calculate row and column for 3x2 grid
            row = i // 3
            col = i % 3
            tools_grid.addWidget(btn, row, col)

        # Wrap the grid layout in a QWidget to add it to the sidebar
        tools_widget = QWidget()
        tools_widget.setLayout(tools_grid)
        sidebar_layout.addWidget(tools_widget)

        self.tool_group.buttonClicked[int].connect(self.set_tool)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.canvas.clear_canvas)
        sidebar_layout.addWidget(clear_btn)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.canvas.save_state)
        sidebar_layout.addWidget(save_btn)

        # Undo button
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        sidebar_layout.addWidget(undo_btn)

        # Redo button
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        sidebar_layout.addWidget(redo_btn)

        # Add stretch to push elements to the top
        sidebar_layout.addStretch()

        # Add sidebar to the main layout
        main_layout.addWidget(sidebar)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.brush_color = color

    def update_brush_size(self, size):
        self.canvas.brush_size = size
        self.brush_slider.setValue(size)
        self.brush_spin.setValue(size)
        
    def set_tool(self, id):
        tools = ["pen", "rectangle", "ellipse", "line", "fill","circle"]
        if 0 <= id < len(tools):
            self.canvas.current_tool = tools[id]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PythonPaint()
    window.show()
    sys.exit(app.exec_())