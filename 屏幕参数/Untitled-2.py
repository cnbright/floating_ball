# -*- coding: utf-8 -*-

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6 import QtWidgets, QtGui, QtCore

class DragWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 200)

        # 获取屏幕信息
        app = QtWidgets.QApplication.instance()
        self.screen = app.primaryScreen()
        self.screen_rect = self.screen.geometry()
        self.screens = app.screens()

        # 初始化鼠标位置和窗口位置
        self.mouse_pos = None
        self.window_pos = self.pos()

        # 设置窗口的背景颜色
        self.setStyleSheet('background-color: red;')

    def mousePressEvent(self, event):
        # 记录鼠标位置和窗口位置
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        # 计算窗口新位置，并进行范围限制
        if event.buttons() == QtCore.Qt.LeftButton:
            diff = event.globalPos() - self.mouse_pos
            new_pos = self.window_pos + diff

            # 判断当前屏幕
            current_screen = self.screen
            for screen in self.screens:
                if screen.geometry().contains(self.mouse_pos):
                    current_screen = screen
                    break

            # 对新位置进行范围限制
            max_x = current_screen.geometry().right() - self.width()
            max_y = current_screen.geometry().bottom() - self.height()

            if new_pos.x() < current_screen.geometry().left():
                new_pos.setX(current_screen.geometry().left())
            elif new_pos.x() > max_x:
                new_pos.setX(max_x)

            if new_pos.y() < current_screen.geometry().top():
                new_pos.setY(current_screen.geometry().top())
            elif new_pos.y() > max_y:
                new_pos.setY(max_y)

            self.move(new_pos)
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 200)

        # 获取主屏幕信息
        app = QtWidgets.QApplication.instance()
        self.screen = app.primaryScreen()
        self.screen_rect = self.screen.geometry()

        # 初始化鼠标位置和窗口位置
        self.mouse_pos = None
        self.window_pos = self.pos()

        # 设置窗口的背景颜色
        self.setStyleSheet('background-color: red;')

    def mousePressEvent(self, event):
        # 记录鼠标位置和窗口位置
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        # 计算窗口新位置，并进行范围限制
        if event.buttons() == QtCore.Qt.LeftButton:
            diff = event.globalPos() - self.mouse_pos
            new_pos = self.window_pos + diff

            # 对新位置进行范围限制
            max_x = self.screen_rect.right() - self.width()
            max_y = self.screen_rect.bottom() - self.height()

            if new_pos.x() < self.screen_rect.left():
                new_pos.setX(self.screen_rect.left())
            elif new_pos.x() > max_x:
                new_pos.setX(max_x)

            if new_pos.y() < self.screen_rect.top():
                new_pos.setY(self.screen_rect.top())
            elif new_pos.y() > max_y:
                new_pos.setY(max_y)

            self.move(new_pos)

app = QtWidgets.QApplication([])
window = DragWindow()
window.show()
app.exec_()
