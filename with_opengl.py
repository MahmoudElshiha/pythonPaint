import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QSlider, QLabel, QSpinBox, QButtonGroup, QRadioButton, QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *

class Canvas(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self._brush_color = [0.0, 0.0, 0.0]
        self._brush_size = 5
        self._drawing = False
        self._points = []
        self._start_point = None
        self._current_tool = "pen"

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glColor3f(*self._brush_color)
        glPointSize(self._brush_size)

        for item in self._points:
            tool, data = item
            if tool == "pen":
                glBegin(GL_POINTS)
                for x, y in data:
                    glVertex2f(x, y)
                glEnd()
            elif tool == "line":
                glBegin(GL_LINES)
                glVertex2f(*data[0])
                glVertex2f(*data[1])
                glEnd()
            elif tool == "rectangle":
                x0, y0 = data[0]
                x1, y1 = data[1]
                glBegin(GL_LINE_LOOP)
                glVertex2f(x0, y0)
                glVertex2f(x1, y0)
                glVertex2f(x1, y1)
                glVertex2f(x0, y1)
                glEnd()
            elif tool == "ellipse":
                x0, y0 = data[0]
                x1, y1 = data[1]
                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                rx = abs(x1 - x0) / 2
                ry = abs(y1 - y0) / 2
                glBegin(GL_LINE_LOOP)
                for i in range(360):
                    angle = i * 3.14159 / 180
                    x = cx + rx * cos(angle)
                    y = cy + ry * sin(angle)
                    glVertex2f(x, y)
                glEnd()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._start_point = (event.x(), event.y())
            if self._current_tool == "pen":
                self._points.append(("pen", [(event.x(), event.y())]))
            self.update()

    def mouseMoveEvent(self, event):
        if self._drawing and self._current_tool == "pen":
            self._points[-1][1].append((event.x(), event.y()))
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drawing:
            end_point = (event.x(), event.y())
            if self._current_tool != "pen":
                self._points.append((self._current_tool, [self._start_point, end_point]))
            self._drawing = False
            self.update()

    def clear_canvas(self):
        self._points = []
        self.update()

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, color):
        self._brush_color = [color.redF(), color.greenF(), color.blueF()]

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

from math import sin, cos

class PythonPaint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonPaint OpenGL")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.canvas = Canvas()
        main_layout.addWidget(self.canvas)

        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.choose_color)
        sidebar_layout.addWidget(self.color_btn)

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

        sidebar_layout.addWidget(QLabel("Tools:"))
        self.tool_group = QButtonGroup()
        tools = ["Pen", "Rectangle", "Ellipse", "Line"]
        for i, tool in enumerate(tools):
            btn = QRadioButton(tool)
            if i == 0:
                btn.setChecked(True)
            self.tool_group.addButton(btn, i)
            sidebar_layout.addWidget(btn)

        self.tool_group.buttonClicked[int].connect(self.set_tool)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.canvas.clear_canvas)
        sidebar_layout.addWidget(clear_btn)

        sidebar_layout.addStretch()
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
