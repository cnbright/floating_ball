import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from math import *


from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

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

        # 绘制滑块
        # painter.setPen(Qt.NoPen)
        # painter.setBrush(QColor(50, 50, 50))
        # r = rect_size / 2 -20
        # x = center.x() + r * cos(self.value() * 3.14159 / 180)
        # y = center.y() + r * sin(self.value() * 3.14159 / 180)
        # painter.drawEllipse(QPointF(x, y), 25, 25)


    def mousePressEvent(self, event):
        self.setValue(self.angle(event))

    def mouseMoveEvent(self, event):
        self.setValue(self.angle(event))
        if self.value()>=315:
            self.vol = (self.value()-315)/270*100
        else:
            self.vol = (self.value()+45)/270*100
        set_system_volume(self.vol)

    def angle(self, event):
        self.last_angle = self.value()
        center = self.rect().center()
        x = event.pos().x() - center.x()
        y = event.pos().y() - center.y()
        ag = round((180 / 3.14159 * (atan2(y, x)) ) % 360)
        if 315>ag>225:
            ag=self.last_angle
        return ag


class CircularSliderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.slider = CircularSlider(Qt.Horizontal, self)
        self.slider.setGeometry(50, 50, 300, 300)
        # 将滑块的 valueChanged 信号连接到更新标签的槽函数
        self.slider.valueChanged.connect(self.updateLabel)


        self.label = QLabel(self)
        self.label.setGeometry(self.slider.x()+self.slider.width()/2-150/2,
                                self.slider.y()+self.slider.height()/2-150/2, 150, 150)
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


    def updateLabel(self, value):
        # 根据音量更新标签字体颜色
        temp_val = round(self.slider.vol)
        palette = QPalette()
        r = 40 + int((145 - 40) * temp_val / 100)
        g = 50 + int((150 - 50) * temp_val / 100)
        b = 59 + int((156 - 59) * temp_val / 100)
        color = QColor(r, g, b)
        palette.setColor(QPalette.WindowText, color)
        self.label.setPalette(palette)
        # 更新标签的文本为滑块的值
        self.label.setText('{}'.format(temp_val))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircularSliderWindow()
    window.setGeometry(500, 300, 400, 400)  # 设置窗口位置和大小
    window.setWindowTitle('环形滑块')  # 设置窗口标题
    window.show()
    sys.exit(app.exec())
