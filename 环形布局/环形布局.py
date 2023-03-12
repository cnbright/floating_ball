# -*- coding: utf-8 -*-

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QBrush, QColor,QPixmap, QRegion
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
import math




class CircleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题、大小、样式
        self.setWindowTitle("Circular Window")
        self.resize(400, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        # 设置主窗口为圆形
        # self.setMask(self.getMask())

        # 添加按钮
        self.addButtons()

    # def getMask(self):
    #     # 获取主窗口的宽度和高度
    #     width = self.width()
    #     height = self.height()

    #     # 创建一个QPixmap对象，并将其填充为白色
    #     pixmap = QPixmap(width, height)
    #     pixmap.fill(Qt.white)

    #     # 创建一个QPainter对象，用于绘制圆形
    #     painter = QPainter(pixmap)
    #     painter.setRenderHint(QPainter.Antialiasing)

    #     # 创建一个QBrush对象，用于设置圆形的背景颜色
    #     brush = QBrush(QColor("#f5f5f5"))
    #     painter.setBrush(brush)

    #     # 绘制圆形
    #     painter.drawEllipse(0, 0, width - 1, height - 1)

    #     # 返回一个圆形的QRegion对象
    #     return QRegion(pixmap.toImage().mask(QColor(Qt.white)))

    def addButtons(self):
        # 获取主窗口的宽度和高度
        width = self.width()
        height = self.height()

        # 设置按钮的大小和样式
        buttonSize = 60
        buttonStyle = (
            "QPushButton {"
            "   background-color: #ff8364;"
            "   color: white;"
            "   border-radius: %dpx;"
            "   font-size: 16px;"
            "   font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "   background-color: #ff7b52;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #ff7053;"
            "}" % (buttonSize / 2)
        )

        # 创建6个按钮，并设置它们的位置和样式
        for i in range(6):
            button = QPushButton(self)
            button.setText(str(i + 1))
            button.setGeometry(
                (width - buttonSize) / 2 + buttonSize / 2 * math.cos(math.pi / 3 * i) - buttonSize / 2,
                (height - buttonSize) / 2 + buttonSize / 2 * math.sin(math.pi / 3 * i) - buttonSize / 2,
                buttonSize,
                buttonSize,
            )
            button.setStyleSheet(buttonStyle)


if __name__ == "__main__":
    app = QApplication([])
    window = CircleWindow()
    window.show()
    app.exec()
