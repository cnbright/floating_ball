# -*- coding: utf-8 -*-

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QScrollArea, QVBoxLayout, QScrollBar,QGridLayout

import sys

class MyScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def wheelEvent(self, event):
        # 忽略滚轮事件
        event.accept()  

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



class mainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.slider = ScrollableButtonGrid()
        
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.slider)
        self.setLayout(self.h_layout)

        # 创建 6 个按钮
        self.button1 = MyQPushButton("1")
        self.button2 = MyQPushButton("2")
        self.button3 = MyQPushButton("3")
        self.button4 = MyQPushButton("4")
        self.button5 = MyQPushButton("5")
        self.button6 = MyQPushButton("6")
        self.button7 = MyQPushButton("7")
        self.button8 = MyQPushButton("8")
        self.button9 = MyQPushButton("9")
        
        self.button1.clicked.connect(self.print_message)

        self.button1.setFixedSize(50, 50)
        self.button2.setFixedSize(50, 50)
        self.button3.setFixedSize(50, 50)
        self.button4.setFixedSize(50, 50)
        self.button5.setFixedSize(50, 50)
        self.button6.setFixedSize(50, 50)
        self.button7.setFixedSize(50, 50)
        self.button8.setFixedSize(50, 50)
        self.button9.setFixedSize(50, 50)

        self.slider.g_layout.addWidget(self.button1,0,0)
        self.slider.g_layout.addWidget(self.button2,0,1)
        self.slider.g_layout.addWidget(self.button3,0,2)
        self.slider.g_layout.addWidget(self.button4,0,3)
        self.slider.g_layout.addWidget(self.button5,0,4)
        self.slider.g_layout.addWidget(self.button6,0,5)
        self.slider.g_layout.addWidget(self.button7,0,6)
        self.slider.g_layout.addWidget(self.button8,0,7)
        self.slider.g_layout.addWidget(self.button9,0,8)

        self.slider.resize(300,300)
        self.resize(300,300)

    def print_message(self):
        print("按钮点击")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainWindow()
    window.setWindowTitle('环形滑块')  # 设置窗口标题
    window.show()
    sys.exit(app.exec())

