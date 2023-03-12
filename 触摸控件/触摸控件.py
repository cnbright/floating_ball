# -*- coding: utf-8 -*-

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


from PySide6.QtCore import Qt, QRectF, QPoint, QPointF, QSizeF, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QWidget, QLabel
from math import *
import sys


class CircularSlider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置默认值
        self._value = 0
        self._minValue = 0
        self._maxValue = 100
        self._sliderWidth = 30
        self._sliderColor = QColor(0, 255, 0)
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self.update)
        self._label = QLabel(self)
        self._label.setGeometry(QRectF(20, 20, 50, 30))

    def paintEvent(self, event):
        painter = QPainter(self)

        # 绘制圆形背景
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawEllipse(QRectF(10, 10, 200, 200))

        # 绘制弧形滑块
        painter.setPen(QPen(QBrush(self._sliderColor), self._sliderWidth))
        painter.drawArc(QRectF(10, 10, 200, 200), 60 * 16, -self._value * 3.6 * 16)

        # 绘制滑块中心的小圆形
        painter.setBrush(QBrush(self._sliderColor))
        painter.setPen(Qt.NoPen)
        x = 100 + 90 * cos((self._value - 90) * pi / 180)
        y = 100 - 90 * sin((self._value - 90) * pi / 180)
        painter.drawEllipse(QRectF(x - 5, y - 5, 10, 10))


    # 设置/获取当前滑块值
    def setValue(self, value):
        if value < self._minValue:
            value = self._minValue
        elif value > self._maxValue:
            value = self._maxValue
        if self._value != value:
            self._value = value
            self.valueChanged.emit(value)
            self.update()

    def getValue(self):
        return self._value

    # 鼠标点击事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x() - 110
            y = 110 - event.y()
            angle = atan2(y, x) * 180 / pi + 90
            if angle < 0:
                angle += 360
            value = int(angle / 3.6)
            self.setValue(value)
            self._label.setText(str(value))

    # 大小调整事件
    def resizeEvent(self, event):
        size = min(event.size().width(), event.size().height())
        self._radius = size / 2 - self._padding
        self._sliderRect = QRectF(-self._radius, -self._radius, 2 * self._radius, 2 * self._radius)
        self._textRect = QRectF(-self._radius, -self._radius, 2 * self._radius, 2 * self._radius / 3)
        self.update()

    # 绘制事件
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._bgColor)
        painter.drawEllipse(QPointF(0, 0), self._radius, self._radius)

        # 绘制滑块
        angle = self._value * 3.6 - 90
        painter.setPen(self._sliderColor)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(self._sliderRect, angle * 16, 180 * 16)

        # 绘制当前值
        painter.setPen(self._textColor)
        painter.setFont(self._font)
        painter.drawText(self._textRect, Qt.AlignCenter, str(self._value))

    # 鼠标按下事件
    def mousePressEvent(self, event):
        pos = event.pos()
        if self._sliderRect.contains(pos):
            self._mousePressValue = self._value
            self._mousePressPos = self.getSliderPosition(pos)
            self.update()

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self._mousePressValue is not None:
            pos = event.pos()
            pos = self.getSliderPosition(pos)
            value = self.getValueFromPos(pos)
            if value != self._mousePressValue:
                self._value = value
                self.valueChanged.emit(self._value)
                self.update()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self._mousePressValue is not None:
            self._mousePressValue = None
            self.update()


if __name__ == "__main__":
    app = PySide6.QtWidgets.QApplication(sys.argv)

    widget = PySide6.QtWidgets.QWidget()
    layout = PySide6.QtWidgets.QVBoxLayout(widget)

    slider = CircularSlider()
    slider.valueChanged.connect(lambda val: print(f"Current value: {val}"))

    layout.addWidget(slider)
    layout.addStretch()

    widget.show()
    sys.exit(app.exec())

