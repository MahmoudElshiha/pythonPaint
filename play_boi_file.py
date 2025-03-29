# import sys
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
#                             QHBoxLayout, QPushButton, QColorDialog, QSlider, 
#                             QLabel, QSpinBox)
# from PyQt5.QtGui import QPainter, QPen, QPainterPath, QImage
# from PyQt5.QtCore import Qt, QPoint


# class Canvas(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setAttribute(Qt.WA_StaticContents)
#         self._image = None
#         self._brush_color = Qt.black
#         self._brush_size = 5
#         self._last_point = QPoint()
#         self._path = QPainterPath()
#         self.clear_canvas()

#     def clear_canvas(self):
#         self._image = self._create_blank_image()
#         self.update()

#     def _create_blank_image(self):
#         image = None
#         if image is None or image.size() != self.size():
#             if self.size().width() > 0 and self.size().height() > 0:
#                 image = QImage(self.size(), QImage.Format_RGB32)
#                 image.fill(Qt.white)
#         return image

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.drawImage(self.rect(), self._image, self._image.rect())

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self._last_point = event.pos()
#             self._path.moveTo(self._last_point)

#     def mouseMoveEvent(self, event):
#         if event.buttons() & Qt.LeftButton:
#             painter = QPainter(self._image)
#             painter.setPen(QPen(self._brush_color, self._brush_size, 
#                                 Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
#             painter.drawLine(self._last_point, event.pos())
#             self._last_point = event.pos()
#             self.update()

#     def resizeEvent(self, event):
#         if self._image is None or self._image.size() != self.size():
#             self.clear_canvas()
#         super().resizeEvent(event)

#     @property
#     def brush_color(self):
#         return self._brush_color

#     @brush_color.setter
#     def brush_color(self, color):
#         self._brush_color = color

#     @property
#     def brush_size(self):
#         return self._brush_size

#     @brush_size.setter
#     def brush_size(self, size):
#         self._brush_size = size


# class PythonPaint(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PythonPaint")
#         self.setGeometry(100, 100, 800, 600)

#         # Create central widget and main layout
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         main_layout = QHBoxLayout(central_widget)  # Horizontal layout

#         # Create canvas
#         self.canvas = Canvas()
#         main_layout.addWidget(self.canvas)

#         # Create sidebar widget
#         sidebar = QWidget()
#         sidebar.setFixedWidth(200)  # Set the width of the sidebar
#         sidebar_layout = QVBoxLayout(sidebar)

#         # Color button
#         self.color_btn = QPushButton("Color")
#         self.color_btn.clicked.connect(self.choose_color)
#         sidebar_layout.addWidget(self.color_btn)

#         # Brush size controls
#         sidebar_layout.addWidget(QLabel("Brush Size:"))

#         self.brush_slider = QSlider(Qt.Horizontal)  # Vertical slider
#         self.brush_slider.setMinimum(1)
#         self.brush_slider.setMaximum(50)
#         self.brush_slider.setValue(5)
#         self.brush_slider.valueChanged.connect(self.update_brush_size)
#         sidebar_layout.addWidget(self.brush_slider)

#         self.brush_spin = QSpinBox()
#         self.brush_spin.setMinimum(1)
#         self.brush_spin.setMaximum(50)
#         self.brush_spin.setValue(5)
#         self.brush_spin.valueChanged.connect(self.update_brush_size)
#         sidebar_layout.addWidget(self.brush_spin)

#         # Clear button
#         clear_btn = QPushButton("Clear")
#         clear_btn.clicked.connect(self.canvas.clear_canvas)
#         sidebar_layout.addWidget(clear_btn)

#         # Add stretch to push elements to the top
#         sidebar_layout.addStretch()

#         # Add sidebar to the main layout
#         main_layout.addWidget(sidebar)

#     def choose_color(self):
#         color = QColorDialog.getColor()
#         if color.isValid():
#             self.canvas.brush_color = color

#     def update_brush_size(self, size):
#         self.canvas.brush_size = size
#         self.brush_slider.setValue(size)
#         self.brush_spin.setValue(size)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = PythonPaint()
#     window.show()
#     sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QColorDialog, QSlider, 
                            QLabel, QSpinBox, QButtonGroup, QRadioButton)
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QImage
from PyQt5.QtCore import Qt, QPoint, QRect


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
        self._current_tool = "pen"  # "pen", "rectangle", "ellipse", "line"
        self._start_point = QPoint()
        self.clear_canvas()

    def clear_canvas(self):
        self._image = self._create_blank_image()
        self.update()

    def _create_blank_image(self):
        image = None
        if image is None or image.size() != self.size():
            if self.size().width() > 0 and self.size().height() > 0:
                image = QImage(self.size(), QImage.Format_RGB32)
                image.fill(Qt.white)
        return image

    def save_state(self):
        buffer = self._image.bits().asarray(self._image.width() * self._image.height() * 4)  # Assuming RGBA format
        saved = list(buffer)
        print(saved[-10:])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self._image, self._image.rect())
        
        # Draw preview of the current shape if drawing
        if self._drawing and self._current_tool != "pen":
            painter.setPen(QPen(self._brush_color, self._brush_size, 
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            rect = QRect(self._start_point, self._last_point)
            
            if self._current_tool == "rectangle":
                painter.drawRect(rect)
            elif self._current_tool == "ellipse":
                painter.drawEllipse(rect)
            elif self._current_tool == "line":
                painter.drawLine(self._start_point, self._last_point)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._start_point = event.pos()
            self._last_point = event.pos()
            
            if self._current_tool == "pen":
                # Create a temporary painter just for the initial point
                painter = QPainter(self._image)
                painter.setPen(QPen(self._brush_color, self._brush_size, 
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawPoint(self._last_point)
                painter.end()
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
                
                painter.end()
            
            self._drawing = False
            self.update()

    def resizeEvent(self, event):
        if self._image is None or self._image.size() != self.size():
            self.clear_canvas()
        super().resizeEvent(event)

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
        
        pen_radio = QRadioButton("Pen")
        pen_radio.setChecked(True)
        self.tool_group.addButton(pen_radio, 0)
        sidebar_layout.addWidget(pen_radio)
        
        rect_radio = QRadioButton("Rectangle")
        self.tool_group.addButton(rect_radio, 1)
        sidebar_layout.addWidget(rect_radio)
        
        ellipse_radio = QRadioButton("Ellipse")
        self.tool_group.addButton(ellipse_radio, 2)
        sidebar_layout.addWidget(ellipse_radio)
        
        line_radio = QRadioButton("Line")
        self.tool_group.addButton(line_radio, 3)
        sidebar_layout.addWidget(line_radio)
        
        self.tool_group.buttonClicked[int].connect(self.set_tool)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.canvas.clear_canvas)
        sidebar_layout.addWidget(clear_btn)

        # Save button
        clear_btn = QPushButton("Save")
        clear_btn.clicked.connect(self.canvas.save_state)
        sidebar_layout.addWidget(clear_btn)

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
        tools = ["pen", "rectangle", "ellipse", "line"]
        if 0 <= id < len(tools):
            self.canvas.current_tool = tools[id]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PythonPaint()
    window.show()
    sys.exit(app.exec_())