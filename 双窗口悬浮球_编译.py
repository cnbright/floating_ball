# -*- coding: utf-8 -*-

import os
import sys
# 获取打包后的程序运行时所在的临时目录
tempdir = sys._MEIPASS
# 在临时目录中构造文件夹的完整路径
data_dir = os.path.join(tempdir, 'images')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(tempdir, 'platforms')


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
window_b_height = 498

from math import *
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import win32gui
import win32con
import win32api
import time
import copy

def get_system_volume():
    # 获取系统默认的音频设备

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # 获取系统音量
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
    except:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
    # 将音量转换为百分比
    current_volume_percentage = round(current_volume * 100)
    return current_volume_percentage

def set_system_volume(vol):
    # 获取系统默认的音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(vol/100, None)

# 渐变透明度
def anime_WindowOpacity(window):
    window.setWindowOpacity(0)
    n = 0.0
    for i in range(15):
        time.sleep(0.01)
        n+=0.06
        window.setWindowOpacity(n)

# devicePixelRatio不能正确获得缩放系数，因此重新计算缩放系数
def get_devicePixelRatio(screen):
    logicalDpi = screen.logicalDotsPerInch()
    physicalDpi = screen.physicalDotsPerInch()

    # 计算缩放比例
    devicePixelRatio = logicalDpi / physicalDpi
    return devicePixelRatio

# 获得焦点屏幕
def get_focus_screen():
    global app

    # 根据四周有无屏幕，哪些方向的拖动时允许的
    screens = app.screens()
    # 首先判断焦点屏幕
    # 判断激活的屏幕的序号
    for index, screen in enumerate(screens):
        screen_geometry = screen.geometry()
        x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
        scale_factor = get_devicePixelRatio(screen)
        # scale_factor = screen.devicePixelRatio()
        cursor_pos = QCursor.pos()
        # 判断鼠标在不在该屏幕内
        if x<=cursor_pos.x()<x+width*scale_factor and y<=cursor_pos.y()<y+height*scale_factor:
            break

    # print("激活屏幕为：",index)

    # 将焦点屏幕从screens列表取出
    focus_screen = screens.pop(index)

    return focus_screen

# 自定义滚动控件
class MyScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.accept()  

# 自定义按钮
class MyQPushButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mouse_drag_flag = False
        self._drag_start_pos = None


    def mousePressEvent(self, event):
        self.mouse_drag_flag = False
        event.ignore()
        self.setDown(True)

    def mouseMoveEvent(self, event):
        self.mouse_drag_flag = True
        event.ignore()
        # super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mouse_drag_flag:
            event.ignore()
            self.setDown(False)
        else:
            self.click()
        
# 滚动区域控件
class ScrollableButtonGrid(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个网格布局，用于添加按钮
        self.g_layout = QGridLayout()
        self.g_layout.setSpacing(20)

        # 创建一个滚动区域，将水平布局添加到其中
        self.scroll_area = MyScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(QWidget())
        self.scroll_area.widget().setLayout(self.g_layout)

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background-color: transparent;")

        # 设定初始位置
        self.scroll_area.horizontalScrollBar().setValue(0)

        # 创建一个垂直布局，将滚动区域添加到其中
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.scroll_area)

        # 将垂直布局设置为主窗口的布局
        self.setLayout(self.v_layout)

        self.mouse_pos = None

    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.accept()

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        self.mouse_pos = QCursor.pos()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            # 计算鼠标拖动的距离
            delta = QCursor.pos() - self.mouse_pos

            # 计算滚动条应该滚动到的位置
            scrollbar = self.scroll_area.horizontalScrollBar()
            value = scrollbar.value() - delta.x()

            # 设置滚动条的位置
            scrollbar.setValue(value)

            # 更新鼠标位置
            self.mouse_pos = QCursor.pos()

    def mouseReleaseEvent(self, event):
        # 清除已经记录的鼠标位置
        self.mouse_pos = None

        # 保证位置是60的整数倍
        scrollbar = self.scroll_area.horizontalScrollBar()
        value = scrollbar.value()
        scrollbar.setValue(value)
        scrollbar.setValue(round(value/70)*70)


    def __init__(self):
        super().__init__()

        # self.setStyleSheet('''QScrollArea {border: none;}''')
        # self.setStyleSheet("background-color: transparent;")

        # 创建一个网格布局，用于添加按钮
        self.g_layout = QGridLayout()
        self.g_layout.setSpacing(20)

        # 创建一个滚动区域，将水平布局添加到其中
        self.scroll_area = MyScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(QWidget())
        self.scroll_area.widget().setLayout(self.g_layout)

        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background-color: transparent;")

        # 创建一个垂直布局，将滚动区域添加到其中
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.scroll_area)

        # 将垂直布局设置为主窗口的布局
        self.setLayout(self.v_layout)

        self.mouse_pos = None

    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.accept()

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        self.mouse_pos = QCursor.pos()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            # 计算鼠标拖动的距离
            delta = QCursor.pos() - self.mouse_pos

            # 计算滚动条应该滚动到的位置
            scrollbar = self.scroll_area.horizontalScrollBar()
            value = scrollbar.value() - delta.x()

            # 设置滚动条的位置
            scrollbar.setValue(value)

            # 更新鼠标位置
            self.mouse_pos = QCursor.pos()

    def mouseReleaseEvent(self, event):
        # 清除已经记录的鼠标位置
        self.mouse_pos = None
        # 保证位置是60的整数倍
        scrollbar = self.scroll_area.horizontalScrollBar()
        value = scrollbar.value()
        scrollbar.setValue(value)
        scrollbar.setValue(round(value/70)*70)

# Slider类
class CircularSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setRange(0, 360)  # 设置范围
        self.setSingleStep(1)  # 设置步长
        self.setPageStep(15)  # 设置页面步长
        
        # 转换当前音量到角度
        vol = get_system_volume()
        if vol/100*270<100/6:
            self.last_angle=vol/100*270+315
        else:
            self.last_angle=vol/100*270-45
        
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
        if get_system_volume()<100/6:
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
        self.setWindowOpacity(0.9)
        
        # 窗口B
        self.window_b = WindowB()
        self.window_b.resize(window_b_width, window_b_height)
        

        # 系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.config_tray()

        # 真则表示鼠标在本次点击后为发生拖动
        self.mouse_flag = True

    def config_tray(self):
        self.tray_icon.setIcon(QIcon(os.path.join(data_dir, 'assistive.png')))
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

            focus_screen = get_focus_screen()
            # 获取焦点屏幕的参数
            f_screen_geometry = focus_screen.geometry()
            f_x, f_y, f_width, f_height = f_screen_geometry.x(), f_screen_geometry.y(), f_screen_geometry.width(), f_screen_geometry.height()
            f_scale_factor = get_devicePixelRatio(focus_screen)
            # f_scale_factor = focus_screen.devicePixelRatio()
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

                focus_screen = get_focus_screen()
                f_screen_geometry = focus_screen.geometry()

                # 获取焦点屏幕的参数
                f_screen_geometry = focus_screen.geometry()
                f_x, f_y, f_width, f_height = f_screen_geometry.x(), f_screen_geometry.y(), f_screen_geometry.width(), f_screen_geometry.height()
                f_scale_factor = get_devicePixelRatio(focus_screen)
                # f_scale_factor = focus_screen.devicePixelRatio()
                # 考虑缩放后要四舍五入，系统问题，不一定是整数
                f_xrb = round(f_x+f_width*f_scale_factor)
                f_yrb = round(f_y+f_height*f_scale_factor)

                # 约束新生成的windwosB的位置，防止windowB部分直接生成在不可见区域
                max_x = focus_screen.geometry().right() - self.width()
                max_y = focus_screen.geometry().bottom() - self.height()

                n_pos = [self.geometry().center().x() - self.window_b.width()/2,
                         self.geometry().center().y() - self.window_b.height()/2]
                

                if n_pos[0] < focus_screen.geometry().left():
                    n_pos[0] = focus_screen.geometry().left()
                elif n_pos[0]+window_b_width > max_x:
                    n_pos[0] = max_x - window_b_width

                if n_pos[1] < focus_screen.geometry().top():
                    n_pos[1] = focus_screen.geometry().top()
                elif n_pos[1]+window_b_height > max_y:
                    n_pos[1] = max_y + self.height() - window_b_height
                
                

                self.window_b.setGeometry(QRect(n_pos[0],n_pos[1],window_b_width, window_b_height))

                threading.Thread(target=anime_WindowOpacity, args=(self.window_b,)).start()
        
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



class WindowB(QWidget):
    def __init__(self):
        global window_b_width, window_b_height
        super().__init__()
        self.setWindowTitle("Window B")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.Tool )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setGeometry(200, 200, window_b_width, window_b_height)
        self.setWindowOpacity(0.9)

        self.add_buttons()


    def add_buttons(self):
        # 设置布局

        # 一个垂直布局，第一层、第三层套两个网格布局，第二层放Slider

        layout = QVBoxLayout()
        # 设置布局为垂直居中对齐
        layout.setAlignment(Qt.AlignVCenter)
        # 将布局应用到父控件
        self.setLayout(layout)

        self.scroll1 = ScrollableButtonGrid()
        # self.scroll1.resize(300,20)

        self.scroll2 = ScrollableButtonGrid()
        # self.scroll2.resize(300,20)

        self.layout().addWidget(self.scroll1)

        self.slider = CircularSlider()
        self.slider.setFixedSize(300, 300)
        self.layout().addWidget(self.slider)

        self.layout().addWidget(self.scroll2)

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

        self.button1 = MyQPushButton(self)
        self.button1.setIcon(QIcon(os.path.join(data_dir, 'mission.png')))
        self.button1.setIconSize(QSize(50, 50))
        self.button1.setFixedSize(50, 50)
        self.button1.clicked.connect(self.mission_view)
        self.scroll1.g_layout.addWidget(self.button1, 0, 0)
        self.button1.setStyleSheet(button_style)

        self.button2 = MyQPushButton(self)
        self.button2.setIcon(QIcon(os.path.join(data_dir, 'flash.png')))
        self.button2.setIconSize(QSize(50, 50))
        self.button2.setFixedSize(50, 50)
        self.button2.clicked.connect(self.open_quicker)
        self.scroll1.g_layout.addWidget(self.button2, 0, 1)
        self.button2.setStyleSheet(button_style)

        self.button3 = MyQPushButton(self)
        self.button3.setIcon(QIcon(os.path.join(data_dir, 'screen.png')))
        self.button3.setIconSize(QSize(50, 50))
        self.button3.setFixedSize(50, 50)
        self.button3.clicked.connect(self.change_screen)
        self.scroll1.g_layout.addWidget(self.button3, 0, 2)
        self.button3.setStyleSheet(button_style)


        self.button5 = MyQPushButton(self)
        self.button5.setIcon(QIcon(os.path.join(data_dir, 'closemenu.png')))
        self.button5.setIconSize(QSize(50, 50))
        self.button5.setFixedSize(50, 50)
        self.button5.clicked.connect(self.switch_to_window_a)
        self.scroll1.g_layout.addWidget(self.button5, 0 ,3)
        self.button5.setStyleSheet(button_style)

        self.button52 = MyQPushButton(self)
        self.button52.setIcon(QIcon(os.path.join(data_dir, 'closemenu.png')))
        self.button52.setIconSize(QSize(50, 50))
        self.button52.setFixedSize(50, 50)
        self.button52.clicked.connect(self.switch_to_window_a)
        self.scroll1.g_layout.addWidget(self.button52, 0 ,4)
        self.button52.setStyleSheet(button_style)

        self.button53 = MyQPushButton(self)
        self.button53.setIcon(QIcon(os.path.join(data_dir, 'closemenu.png')))
        self.button53.setIconSize(QSize(50, 50))
        self.button53.setFixedSize(50, 50)
        self.button53.clicked.connect(self.switch_to_window_a)
        self.scroll1.g_layout.addWidget(self.button53, 0 ,5)
        self.button53.setStyleSheet(button_style)

        self.button54 = MyQPushButton(self)
        self.button54.setIcon(QIcon(os.path.join(data_dir, 'closemenu.png')))
        self.button54.setIconSize(QSize(50, 50))
        self.button54.setFixedSize(50, 50)
        self.button54.clicked.connect(self.switch_to_window_a)
        self.scroll1.g_layout.addWidget(self.button54, 0 ,6)
        self.button54.setStyleSheet(button_style)

        self.button55 = MyQPushButton(self)
        self.button55.setIcon(QIcon(os.path.join(data_dir, 'closemenu.png')))
        self.button55.setIconSize(QSize(50, 50))
        self.button55.setFixedSize(50, 50)
        self.button55.clicked.connect(self.switch_to_window_a)
        self.scroll1.g_layout.addWidget(self.button55, 0 ,7)
        self.button55.setStyleSheet(button_style)

        self.button6 = MyQPushButton(self)
        self.button6.setIcon(QIcon(os.path.join(data_dir, 'desktop.png')))
        self.button6.setIconSize(QSize(50, 50))
        self.button6.setFixedSize(50, 50)
        self.button6.clicked.connect(self.back_desktop)
        self.scroll2.g_layout.addWidget(self.button6, 0, 0)
        self.button6.setStyleSheet(button_style)

        self.button7 = MyQPushButton(self)
        self.button7.setIcon(QIcon(os.path.join(data_dir, 'taskmgr.png')))
        self.button7.setIconSize(QSize(50, 50))
        self.button7.setFixedSize(50, 50)
        self.button7.clicked.connect(self.open_taskmgr)
        self.scroll2.g_layout.addWidget(self.button7, 0, 1)
        self.button7.setStyleSheet(button_style)

        self.button8 = MyQPushButton(self)
        self.button8.setIcon(QIcon(os.path.join(data_dir, 'utools.png')))
        self.button8.setIconSize(QSize(45, 45))
        self.button8.setFixedSize(50, 50)
        self.button8.clicked.connect(self.open_utools)
        self.scroll2.g_layout.addWidget(self.button8, 0, 2)
        self.button8.setStyleSheet(button_style)

        self.button9 = MyQPushButton(self)
        self.button9.setIcon(QIcon(os.path.join(data_dir, 'screenshot.png')))
        self.button9.setIconSize(QSize(50, 50))
        self.button9.setFixedSize(50, 50)
        self.button9.clicked.connect(self.take_screenshot)
        self.scroll2.g_layout.addWidget(self.button9, 0, 3)
        self.button9.setStyleSheet(button_style)

        self.button91 = MyQPushButton(self)
        self.button91.setIcon(QIcon(os.path.join(data_dir, 'screenshot.png')))
        self.button91.setIconSize(QSize(50, 50))
        self.button91.setFixedSize(50, 50)
        self.button91.clicked.connect(self.take_screenshot)
        self.scroll2.g_layout.addWidget(self.button91, 0, 4)
        self.button91.setStyleSheet(button_style)

        self.button92 = MyQPushButton(self)
        self.button92.setIcon(QIcon(os.path.join(data_dir, 'screenshot.png')))
        self.button92.setIconSize(QSize(50, 50))
        self.button92.setFixedSize(50, 50)
        self.button92.clicked.connect(self.take_screenshot)
        self.scroll2.g_layout.addWidget(self.button92, 0, 5)
        self.button92.setStyleSheet(button_style)

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
        # print(self.width(),self.height())
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.mouse_flag = False

            # 获取焦点屏幕
            focus_screen = get_focus_screen()
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
        
        self.window_a.setGeometry(self.geometry().center().x() - self.window_a.width()/2,
                                     self.geometry().center().y() - self.window_a.height()/2,
                                     window_a_width, window_a_height)

        threading.Thread(target=anime_WindowOpacity, args=(self.window_a,)).start()

        self.window_a.show()

    def mission_view(self):
        pyautogui.hotkey('winleft', 'tab')

    def open_taskmgr(self):
        pyautogui.hotkey('ctrl', 'shift', 'esc')

    def open_quicker(self):
        hwnd = win32gui.FindWindow(0, "Quicker面板窗口")
        
        if hwnd != 0:
            self.hide()
            focus_screen = get_focus_screen()
            # 获取焦点屏幕的参数
            f_screen_geometry = focus_screen.geometry()
            # 这里需要获取主屏幕的缩放系数，这个函数恰好只能获取主屏幕的，正好用这个
            f_scale_factor = focus_screen.devicePixelRatio()

            # 这个的输入是未缩放坐标
            # 这个关系是缩放坐标到未缩放坐标的变换关系
            pyautogui.middleClick(x=f_screen_geometry.left() + (self.geometry().center().x() - f_screen_geometry.left())*f_scale_factor,
                                y=f_screen_geometry.top() + (self.geometry().center().y() - f_screen_geometry.top())*f_scale_factor)
        
            # win32gui.ShowWindow(hwnd,win32con.SW_SHOW)

            # 判断窗口是否可见
            # 本来判断了这个win32gui.IsWindowVisible(hwnd)，会导致不能短时间响应
            if True:
                # print("================================================")
                # time.sleep(0.1)
                while win32gui.IsWindowVisible(hwnd):
                    pass
                # 获取窗口位置和大小, 这里返回的是未经缩放的坐标
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)

                # 计算缩放后的宽度和高度
                # width = (right - left)
                # height = (bottom - top)
                width = (right - left)/f_scale_factor
                height = (bottom - top)/f_scale_factor

                # 此处的0.44是quicker窗口的上面部分的高度，目前无法直接通过win32api获取到这个高度，因此测量了比例为0.44
                # 这个变换
                # 如存在问题，修改主显示器
                time.sleep(0.1)
                self.move( f_screen_geometry.left()+(left - f_screen_geometry.left() )/f_scale_factor + width/2 - self.width()/2,
                          f_screen_geometry.top()+(top - f_screen_geometry.top())/f_scale_factor + height*0.44 - self.height()/2
                          )
                
                # QT坐标为缩放坐标，WIN32坐标为未缩放坐标，把设计WIN32坐标的操作全用win32api完成就没问题了
                # 获取本窗口句柄
                # time.sleep(0.1)
                # hwnd = self.winId()
                # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, int(left+width/2-self.width()/2),
                #                     int(top+height/2-self.height()/2), self.width(), self.height(), win32con.SWP_SHOWWINDOW)

                threading.Thread(target=anime_WindowOpacity, args=(self,)).start()
                self.show()
            else:
                pass

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
        # f_scale_factor = to_screen.devicePixelRatio()
        # 考虑缩放后要四舍五入，系统问题，不一定是整数
        # f_xrb = round(f_x+f_width*f_scale_factor)
        # f_yrb = round(f_y+f_height*f_scale_factor)
        f_xrb = round(f_x+f_width)
        f_yrb = round(f_y+f_height)


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
