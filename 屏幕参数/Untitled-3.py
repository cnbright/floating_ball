# -*- coding: utf-8 -*-

'''
根据物理分辨率和逻辑分辨率计算缩放系数
'''

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QWindow, QScreen
import sys

app = QApplication(sys.argv)

# 获取主窗口
window = QApplication.primaryScreen().availableGeometry()

screens = app.screens()
# 获取屏幕的物理分辨率和逻辑分辨率
screen = screens[1]

# screen = QWindow().screens()
logicalDpi = screen.logicalDotsPerInch()
physicalDpi = screen.physicalDotsPerInch()

# 计算缩放比例
devicePixelRatio = logicalDpi / physicalDpi

print(f"Screen device pixel ratio: {devicePixelRatio}")

# 获取屏幕的物理分辨率和逻辑分辨率
screen = screens[0]

# screen = QWindow().screens()
logicalDpi = screen.logicalDotsPerInch()
physicalDpi = screen.physicalDotsPerInch()

# 计算缩放比例
devicePixelRatio = logicalDpi / physicalDpi

print(f"Screen device pixel ratio: {devicePixelRatio}")

sys.exit(app.exec())
