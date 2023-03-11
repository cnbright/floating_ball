# -*- coding: utf-8 -*-

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import subprocess
import pyautogui
import threading


window_a_width = 120
window_a_height = window_a_width

window_b_width = 202
window_b_height = window_b_width

class WindowA(QWidget):
    def __init__(self):
        global window_a_width, window_a_height
        super().__init__()
        self.setWindowTitle("Window A")
        # 后两个使得该窗口不在任务视图内显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setGeometry(100, 100, window_a_width, window_a_height)

        # 窗口B
        self.window_b = WindowB()

        # 系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.config_tray()

        # 真则表示鼠标在本次点击后为发生拖动
        self.mouse_flag = True

    def config_tray(self):
        self.tray_icon.setIcon(QIcon("./images/assistive.png"))
        self.tray_icon.activated.connect(self.tray_icon_activated)
        # self.tray_icon.show()

        # 创建右键菜单
        self.tray_menu = QMenu(self)
        self.close_action = QAction("退出", self)
        self.close_action.triggered.connect(QCoreApplication.quit)
        self.tray_menu.addAction(self.close_action)

        # 将右键菜单添加到系统托盘图标
        self.tray_icon.setContextMenu(self.tray_menu)

        # 显示系统托盘图标
        self.tray_icon.show()
        # 指示窗口状态，True表示仅显示A窗口，False表示仅显示B窗口
        self.tray_flag = True

    '''
    系统托盘
    '''
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                if self.tray_flag:
                    self.show()
                else:
                    if self.window_b.isVisible():
                        self.window_b.hide()
                    else:
                        self.window_b.show()


    '''
    鼠标事件
    '''
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_flag = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.mouse_flag = False
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        global window_b_width, window_b_height
        if event.button() == Qt.LeftButton:
            # 若菜单已经显示则隐藏
            if self.mouse_flag:
                self.tray_flag = False
                self.hide()
                self.window_b.setGeometry(QRect(self.pos().x() + self.width()/2 - self.window_b.width()/2,
                                     self.pos().y() + self.height()/2 - self.window_b.height()/2,
                                     window_b_width, window_b_height))
        
                self.window_b.show()
            else:
                self.drag_position = None
                event.accept()

    '''
    重绘
    '''
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 25, 25)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QBrush(QColor("#28323B")))

        # 计算三个圆形的圆心坐标
        radius1 = 52
        radius2 = 44
        radius3 = 36
        x = self.width() // 2
        y = self.height() // 2
        center1 = (x, y)

        gradient = QRadialGradient(self.rect().center(), self.rect().width() / 2)
        gradient.setColorAt(0, QColor(255, 255, 255, 255))
        gradient.setColorAt(1, QColor(200, 200, 200, 255))
        # 绘制三个圆形
        brush1 = QBrush(QColor("#525F65"))
        brush2 = QBrush(QColor("#91969C"))
        brush3 = QBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.NoPen)# 设置画笔避免边缘黑色

        painter.setBrush(brush1)
        painter.drawEllipse(center1[0] - radius1, center1[1] - radius1, 2 * radius1, 2 * radius1)
        painter.setBrush(brush2)
        painter.drawEllipse(center1[0] - radius2, center1[1] - radius2, 2 * radius2, 2 * radius2)
        painter.setBrush(brush3)
        painter.drawEllipse(center1[0] - radius3, center1[1] - radius3, 2 * radius3, 2 * radius3)

        self.setWindowOpacity(0.9)



class WindowB(QWidget):
    def __init__(self):
        global window_b_width, window_b_height
        super().__init__()
        self.setWindowTitle("Window B")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setGeometry(200, 200, window_b_width, window_b_height)

        self.add_buttons()


    def add_buttons(self):
        # 设置布局
        self.setLayout(QGridLayout())
        self.layout().setSpacing(15)
        # 按钮样式
        button_style = '''
        QPushButton {
            background-color: #FFFFFF;
            border: 2px;
            border-radius: 10px;
            color: #FFFFFF;
            font-size: 16px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #91969C;
        }
        QPushButton:pressed {
            background-color: #525F65;
        }
        '''

        self.button1 = QPushButton(self)
        self.button1.setIcon(QIcon("./images/mission.png"))
        self.button1.setIconSize(QSize(50, 50))
        self.button1.setFixedSize(50, 50)
        self.button1.clicked.connect(self.mission_view)
        self.layout().addWidget(self.button1, 1, 1)
        self.button1.setStyleSheet(button_style)

        self.button2 = QPushButton(self)
        self.button2.setIcon(QIcon("./images/taskmgr.png"))
        self.button2.setIconSize(QSize(50, 50))
        self.button2.setFixedSize(50, 50)
        self.button2.clicked.connect(self.open_taskmgr)
        self.layout().addWidget(self.button2, 1, 2)
        self.button2.setStyleSheet(button_style)

        self.button4 = QPushButton(self)
        self.button4.setIcon(QIcon("./images/voldown.png"))
        self.button4.setIconSize(QSize(50, 50))
        self.button4.setFixedSize(50, 50)
        self.button4.clicked.connect(self.vol_down)
        self.layout().addWidget(self.button4, 2, 1)
        self.button4.setStyleSheet(button_style)

        self.button5 = QPushButton(self)
        self.button5.setIcon(QIcon("./images/closemenu.png"))
        self.button5.setIconSize(QSize(50, 50))
        self.button5.setFixedSize(50, 50)
        self.button5.clicked.connect(self.switch_to_window_a)
        self.layout().addWidget(self.button5, 2, 2)
        self.button5.setStyleSheet(button_style)

        self.button6 = QPushButton(self)
        self.button6.setIcon(QIcon("./images/volup.png"))
        self.button6.setIconSize(QSize(50, 50))
        self.button6.setFixedSize(50, 50)
        self.button6.clicked.connect(self.vol_up)
        self.layout().addWidget(self.button6, 2, 3)
        self.button6.setStyleSheet(button_style)

        self.button9 = QPushButton(self)
        self.button9.setIcon(QIcon("./images/screenshot.png"))
        self.button9.setIconSize(QSize(50, 50))
        self.button9.setFixedSize(50, 50)
        self.button9.clicked.connect(self.take_screenshot)
        self.layout().addWidget(self.button9, 3, 3)
        self.button9.setStyleSheet(button_style)


    '''
    鼠标事件
    '''
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_flag = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.mouse_flag = False
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

    '''
    重绘
    '''
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔避免边缘黑色
        painter.setPen(Qt.NoPen)
        # Draw rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 25, 25)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QBrush(QColor("#28323B")))

        self.setWindowOpacity(0.9)

    '''
    按钮槽函数
    '''
    def switch_to_window_a(self):
        global window_a
        # print(self.rect())
        global window_a_width, window_a_height
        self.hide()
        self.window_a = window_a
        self.window_a.tray_flag = True
        self.window_a.setGeometry(self.pos().x() + self.width()/2 - self.window_a.width()/2,
                                     self.pos().y() + self.height()/2 - self.window_a.height()/2,
                                     window_a_width, window_a_height)
        self.window_a.show()

    def mission_view(self):
        pyautogui.hotkey('winleft', 'tab')

    def open_taskmgr(self):
        pyautogui.hotkey('ctrlleft', 'altleft','delete')

    def vol_down(self):
        pyautogui.hotkey('volumedown')

    def vol_up(self):
        pyautogui.hotkey('volumeup')

    def take_screenshot(self):
        # 模拟按下win+shift+s
        pyautogui.hotkey('winleft', 'shift', 's')
        # 创建新线程等待0.5秒后显示窗口
        t = threading.Timer(1., self.show)
        t.start()
        # 隐藏悬浮球窗口
        self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window_a = WindowA()
    window_a.show()
    sys.exit(app.exec())
