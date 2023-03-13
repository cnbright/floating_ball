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

from math import *
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import win32gui
import win32con
import time

def get_system_volume():
    # 获取系统默认的音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # 获取系统音量
    current_volume = volume.GetMasterVolumeLevelScalar()

    # 将音量转换为百分比
    current_volume_percentage = round(current_volume * 100)
    return current_volume_percentage

def set_system_volume(vol):
    # 获取系统默认的音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(vol/100, None)


# Slider类
class CircularSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRange(0, 360)  # 设置范围
        self.setSingleStep(1)  # 设置步长
        self.setPageStep(15)  # 设置页面步长
        
        # 转换当前音量到角度
        if get_system_volume()/100*270<100/6:
            self.last_angle=get_system_volume()/100*270+315
        else:
            self.last_angle=get_system_volume()/100*270-45
        
        self.setValue(self.last_angle)

        # 设置标签
        self.label = QLabel(self)
        self.label.raise_()
        # 设置字体和颜色
        font = QFont("Comic Sans MS", 60, QFont.Bold)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.red)
        temp_val = get_system_volume()
        palette = QPalette()
        r = 40 + int((145 - 40) * temp_val / 100)
        g = 50 + int((150 - 50) * temp_val / 100)
        b = 59 + int((156 - 59) * temp_val / 100)
        color = QColor(r, g, b)
        palette.setColor(QPalette.WindowText, color)
        self.label.setFont(font)
        self.label.setPalette(palette)
        # 将文本垂直和水平居中显示
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText('{}'.format(temp_val))

        # 将滑块的 valueChanged 信号连接到更新标签的槽函数
        self.valueChanged.connect(self.updateLabel)


        # 设置定时器，定时更新音量
        self.timer = QTimer(self)
        self.timer.setInterval(100) # 每100毫秒更新一次音量
        self.timer.timeout.connect(self.timer_update_volume)
        self.timer.start()

        # 上一次鼠标事件发生在音量调节范围以内，则为0
        # 上一次鼠标事件发生在音量调节范围外，则为1
        # 每次鼠标释放事件后重新置为2
        self.mouse_event_flag = 2

        # 鼠标点击后是否拖动标志位，True则未发生拖动
        self.mouse_drag_flag = False


    def timer_update_volume(self):
        # 转换当前音量到角度
        if get_system_volume()/100*270<100/6:
            self.last_angle=get_system_volume()/100*270+315
        else:
            self.last_angle=get_system_volume()/100*270-45
        
        self.setValue(self.last_angle)
        self.vol = round(get_system_volume())
        self.updateLabel(0)

    def updateLabel(self, value):
        # 根据音量更新标签字体颜色
        temp_val = round(self.vol)
        palette = QPalette()
        r = 40 + int((145 - 40) * temp_val / 100)
        g = 50 + int((150 - 50) * temp_val / 100)
        b = 59 + int((156 - 59) * temp_val / 100)
        color = QColor(r, g, b)
        palette.setColor(QPalette.WindowText, color)
        self.label.setPalette(palette)
        # 更新标签的文本为滑块的值
        self.label.setText('{}'.format(temp_val))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿

        width = self.width()
        height = self.height()
        rect_size = min(width, height)
        rect = QRectF((width - rect_size) / 2, (height - rect_size) / 2, rect_size, rect_size)

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(rect)

        # 绘制弧形
        center = rect.center()
        gradient = QConicalGradient(center, -270)
        gradient.setColorAt(0, QColor(145, 150, 156))
        # gradient.setColorAt(0.5, QColor(255, 255, 0))
        gradient.setColorAt(1, QColor(40, 50, 59))
        painter.setBrush(QBrush(gradient))
        # startAngle和spanAngle必须以1/16度指定

        pen = QPen(QBrush(gradient), 30)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        rect_size = min(width, height)-50
        rect = QRectF((width - rect_size) / 2, (height - rect_size) / 2, rect_size, rect_size)

        # 限制旋转角度-绘制部分
        if -self.value()*16 < -270*16:
            painter.drawArc(rect, 45*16,-self.value()*16+315*16)
        else:
            painter.drawArc(rect, 45*16, -self.value()*16-45*16)

        # 因为重绘有控件大小改变，所以在这里重新设置标签大小位置
        self.label.setGeometry(self.width()/2-150/2,
                                self.height()/2-150/2, 150, 150)


    def mousePressEvent(self, event):
        # 若未鼠标事件未发生在靠近滑动条的位置，则该事件忽略，上报父窗口，实现拖动窗口
        center = self.rect().center()
        x = event.pos().x() - center.x()
        y = event.pos().y() - center.y()
        # print(sqrt(x**2+y**2))
        if 150**2 >= x**2+y**2 >= (102)**2:
            self.setValue(self.angle(event))
            self.mouse_event_flag = 0
        else:
            self.mouse_event_flag = 1
            event.ignore()
            self.parent().mousePressEvent(event)
                

    def mouseMoveEvent(self, event):
        self.mouse_drag_flag = True
        if self.mouse_event_flag == 1:
            event.ignore()
            self.parent().mousePressEvent(event)
        else:
            self.setValue(self.angle(event))
            if self.value()>=315:
                self.vol = (self.value()-315)/270*100
            else:
                self.vol = (self.value()+45)/270*100
            set_system_volume(self.vol)

    def mouseReleaseEvent(self, event):
        if self.mouse_event_flag == 1:
            event.ignore()
            self.parent().mousePressEvent(event)
            if not self.mouse_drag_flag:
                pyautogui.press('playpause')
        else:
            pass
        self.mouse_event_flag = 2
        self.mouse_drag_flag = False

    def angle(self, event):
        self.last_angle = self.value()
        center = self.rect().center()
        x = event.pos().x() - center.x()
        y = event.pos().y() - center.y()
        ag = round((180 / 3.14159 * (atan2(y, x)) ) % 360)
        if 315>ag>225:
            ag=self.last_angle
        return ag


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
            # 范围判定用
            self.mouse_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        global app
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.mouse_flag = False
            # 根据四周有无屏幕，哪些方向的拖动时允许的
            screens = app.screens()
            # 首先判断焦点屏幕
            # 判断激活的屏幕的序号
            for index, screen in enumerate(screens):
                screen_geometry = screen.geometry()
                x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
                scale_factor = screen.devicePixelRatio()
                cursor_pos = QCursor.pos()
                # 判断鼠标在不在该屏幕内
                if x<=cursor_pos.x()<x+width*scale_factor and y<=cursor_pos.y()<y+height*scale_factor:
                    break

            # print("激活屏幕为：",index)

            # 将焦点屏幕从screens列表取出
            focus_screen = screens.pop(index)
            # 获取焦点屏幕的参数
            f_screen_geometry = focus_screen.geometry()
            f_x, f_y, f_width, f_height = f_screen_geometry.x(), f_screen_geometry.y(), f_screen_geometry.width(), f_screen_geometry.height()
            f_scale_factor = focus_screen.devicePixelRatio()
            # 考虑缩放后要四舍五入，系统问题，不一定是整数
            f_xrb = round(f_x+f_width*f_scale_factor)
            f_yrb = round(f_y+f_height*f_scale_factor)

            # 对新位置进行范围限制,如果拖动到另一块屏幕，则会改变焦点屏幕从而直接跳到另一屏幕，所以不需要进行上下左右有无屏幕的判断了
            max_x = focus_screen.geometry().right() - self.width()
            max_y = focus_screen.geometry().bottom() - self.height()

            diff = event.globalPos() - self.mouse_pos
            new_pos = self.window_pos + diff

            if new_pos.x() < focus_screen.geometry().left():
                new_pos.setX(focus_screen.geometry().left())
            elif new_pos.x() > max_x:
                new_pos.setX(max_x)

            if new_pos.y() < focus_screen.geometry().top():
                new_pos.setY(focus_screen.geometry().top())
            elif new_pos.y() > max_y:
                new_pos.setY(max_y)
            
            self.move(new_pos)
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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.Tool )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setGeometry(200, 200, window_b_width, window_b_height)

        self.add_buttons()


    def add_buttons(self):
        # 设置布局

        # 一个垂直布局，第一层、第三层套两个网格布局，第二层放Slider

        layout = QVBoxLayout()
        # 设置布局为垂直居中对齐
        layout.setAlignment(Qt.AlignVCenter)
        # 将布局应用到父控件
        self.setLayout(layout)

        self.widget1 = QWidget()
        self.widget1.setLayout(QGridLayout())

        self.widget2 = QWidget()
        self.widget2.setLayout(QGridLayout())

        self.layout().addWidget(self.widget1)

        self.slider = CircularSlider()
        self.slider.setFixedSize(300, 300)
        self.layout().addWidget(self.slider)

        self.layout().addWidget(self.widget2)

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
        self.widget1.layout().addWidget(self.button1, 0, 0)
        self.button1.setStyleSheet(button_style)

        self.button2 = QPushButton(self)
        self.button2.setIcon(QIcon("./images/flash.png"))
        self.button2.setIconSize(QSize(50, 50))
        self.button2.setFixedSize(50, 50)
        self.button2.clicked.connect(self.open_quicker)
        self.widget1.layout().addWidget(self.button2, 0, 1)
        self.button2.setStyleSheet(button_style)

        self.button3 = QPushButton(self)
        self.button3.setIcon(QIcon("./images/screen.png"))
        self.button3.setIconSize(QSize(50, 50))
        self.button3.setFixedSize(50, 50)
        self.button3.clicked.connect(self.change_screen)
        self.widget1.layout().addWidget(self.button3, 0, 2)
        self.button3.setStyleSheet(button_style)


        self.button5 = QPushButton(self)
        self.button5.setIcon(QIcon("./images/closemenu.png"))
        self.button5.setIconSize(QSize(50, 50))
        self.button5.setFixedSize(50, 50)
        self.button5.clicked.connect(self.switch_to_window_a)
        self.widget1.layout().addWidget(self.button5, 0 ,3)
        self.button5.setStyleSheet(button_style)

        self.button6 = QPushButton(self)
        self.button6.setIcon(QIcon("./images/desktop.png"))
        self.button6.setIconSize(QSize(50, 50))
        self.button6.setFixedSize(50, 50)
        self.button6.clicked.connect(self.back_desktop)
        self.widget2.layout().addWidget(self.button6, 0, 0)
        self.button6.setStyleSheet(button_style)

        self.button7 = QPushButton(self)
        self.button7.setIcon(QIcon("./images/taskmgr.png"))
        self.button7.setIconSize(QSize(50, 50))
        self.button7.setFixedSize(50, 50)
        self.button7.clicked.connect(self.open_taskmgr)
        self.widget2.layout().addWidget(self.button7, 0, 1)
        self.button7.setStyleSheet(button_style)

        self.button8 = QPushButton(self)
        self.button8.setIcon(QIcon("./images/utools.png"))
        self.button8.setIconSize(QSize(45, 45))
        self.button8.setFixedSize(50, 50)
        self.button8.clicked.connect(self.open_utools)
        self.widget2.layout().addWidget(self.button8, 0, 2)
        self.button8.setStyleSheet(button_style)

        self.button9 = QPushButton(self)
        self.button9.setIcon(QIcon("./images/screenshot.png"))
        self.button9.setIconSize(QSize(50, 50))
        self.button9.setFixedSize(50, 50)
        self.button9.clicked.connect(self.take_screenshot)
        self.widget2.layout().addWidget(self.button9, 0, 3)
        self.button9.setStyleSheet(button_style)

        # 设置布局为垂直居中对齐
        layout.setAlignment(Qt.AlignCenter)
        # 将布局应用到父控件
        self.setLayout(layout)


    '''
    鼠标事件
    '''
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_flag = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # 范围判定用
            self.mouse_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        global app
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.mouse_flag = False
            # 根据四周有无屏幕，哪些方向的拖动时允许的
            screens = app.screens()
            # 首先判断焦点屏幕
            # 判断激活的屏幕的序号
            for index, screen in enumerate(screens):
                screen_geometry = screen.geometry()
                x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
                scale_factor = screen.devicePixelRatio()
                cursor_pos = QCursor.pos()
                # 判断鼠标在不在该屏幕内
                if x<=cursor_pos.x()<x+width*scale_factor and y<=cursor_pos.y()<y+height*scale_factor:
                    break

            # print("激活屏幕为：",index)

            # 将焦点屏幕从screens列表取出
            focus_screen = screens.pop(index)
            # 获取焦点屏幕的参数
            f_screen_geometry = focus_screen.geometry()
            f_x, f_y, f_width, f_height = f_screen_geometry.x(), f_screen_geometry.y(), f_screen_geometry.width(), f_screen_geometry.height()
            f_scale_factor = focus_screen.devicePixelRatio()
            # 考虑缩放后要四舍五入，系统问题，不一定是整数
            f_xrb = round(f_x+f_width*f_scale_factor)
            f_yrb = round(f_y+f_height*f_scale_factor)

            # 对新位置进行范围限制,如果拖动到另一块屏幕，则会改变焦点屏幕从而直接跳到另一屏幕，所以不需要进行上下左右有无屏幕的判断了
            max_x = focus_screen.geometry().right() - self.width()
            max_y = focus_screen.geometry().bottom() - self.height()

            diff = event.globalPos() - self.mouse_pos
            new_pos = self.window_pos + diff

            if new_pos.x() < focus_screen.geometry().left():
                new_pos.setX(focus_screen.geometry().left())
            elif new_pos.x() > max_x:
                new_pos.setX(max_x)

            if new_pos.y() < focus_screen.geometry().top():
                new_pos.setY(focus_screen.geometry().top())
            elif new_pos.y() > max_y:
                new_pos.setY(max_y)
            
            self.move(new_pos)
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
        pyautogui.hotkey('ctrl', 'shift', 'esc')

    def open_quicker(self):
        pyautogui.middleClick(x=self.pos().x() + self.width()/2, y=self.pos().y() + self.height()/2)
        # 查找窗口句柄
        hwnd = win32gui.FindWindow(0, "Quicker面板窗口")

        win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
        # 判断窗口是否可见
        time.sleep(0.5)
        if win32gui.IsWindowVisible(hwnd):
            self.hide()
            # 获取窗口位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # 计算宽度和高度
            width = right - left
            height = bottom - top
            
            while win32gui.IsWindowVisible(hwnd):
                pass

            self.move(left+width/2-self.width()/2, top+height/2-self.height()/2)
            self.show()

    def change_screen(self):
        global app
        # 首先判断焦点屏幕
        screens = app.screens()
        # 判断激活的屏幕的序号
        for index, screen in enumerate(screens):
            screen_geometry = screen.geometry()
            x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
            scale_factor = screen.devicePixelRatio()
            cursor_pos = QCursor.pos()
            # 判断鼠标在不在该屏幕内
            if x<=cursor_pos.x()<x+width*scale_factor and y<=cursor_pos.y()<y+height*scale_factor:
                break

        num_screens = len(screens)-1

        if index+1 > num_screens:
            index = 0
        else:
            index += 1

        # 将下一块屏幕取出
        to_screen = screens.pop(index)

        # 获取焦点屏幕的参数
        to_screen_geometry = to_screen.geometry()
        f_x, f_y, f_width, f_height = to_screen_geometry.x(), to_screen_geometry.y(), to_screen_geometry.width(), to_screen_geometry.height()
        f_scale_factor = to_screen.devicePixelRatio()
        # 考虑缩放后要四舍五入，系统问题，不一定是整数
        f_xrb = round(f_x+f_width*f_scale_factor)
        f_yrb = round(f_y+f_height*f_scale_factor)

        self.move((f_x+f_xrb)/2-self.width()/2, (f_y+f_yrb)/2-self.height()/2)


            
    def back_desktop(self):
        pyautogui.hotkey('winleft', 'd')

    def open_utools(self):
        pyautogui.hotkey('alt', 'space')
        subprocess.Popen("TabTip")

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
