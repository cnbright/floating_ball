# -*- coding: utf-8 -*-

'''
查询当前聚焦屏幕上下左右有没有屏幕
'''

import os, PySide6 
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

from PySide6 import QtWidgets, QtGui

app = QtWidgets.QApplication([])
screens = app.screens()

# 上下左右四个方向有没有屏幕的标志位
screen_flag = [False, False, False, False]

# 判断激活的屏幕的序号
for index, screen in enumerate(screens):
    screen_geometry = screen.geometry()
    x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
    scale_factor = screen.devicePixelRatio()
    cursor_pos = QtGui.QCursor.pos()
    # 判断鼠标在不在该屏幕内
    if x<=cursor_pos.x()<x+width*scale_factor and y<=cursor_pos.y()<y+height*scale_factor:
        break

print("激活屏幕为：",index)
# 将焦点屏幕从screens列表取出
focus_screen = screens.pop(index)
# 获取焦点屏幕的参数
f_screen_geometry = focus_screen.geometry()
f_x, f_y, f_width, f_height = f_screen_geometry.x(), f_screen_geometry.y(), f_screen_geometry.width(), f_screen_geometry.height()
f_scale_factor = focus_screen.devicePixelRatio()
# 考虑缩放后要四舍五入，系统问题，不一定是整数
f_xrb = round(f_x+f_width*f_scale_factor)
f_yrb = round(f_y+f_height*f_scale_factor)


for screen in screens:
    # 获取每个屏幕的左上角坐标和分辨率、获取缩放系数
    screen_geometry = screen.geometry()
    x, y, width, height = screen_geometry.x(), screen_geometry.y(), screen_geometry.width(), screen_geometry.height()
    scale_factor = screen.devicePixelRatio()

    # 判读屏幕左上角
    if x==f_xrb:
        # 右侧
        screen_flag[3] = True
    elif y==f_yrb:
        # 下侧
        screen_flag[1] = True
    # 判断屏幕右下角
    elif round(x+width*scale_factor) == f_x:
        # 左侧
        screen_flag[2] = True
    elif round(y+height*scale_factor) == f_y:
        # 上方
        screen_flag[0] = True


print(screen_flag)


