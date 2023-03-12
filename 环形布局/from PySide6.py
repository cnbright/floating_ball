import ctypes
import win32gui

# 定义输入事件结构体
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("union", ctypes.c_ulong * 3)]

# 定义输入事件类型
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# 定义触控事件常量
TOUCH_COORD_TO_PIXEL = 100 / 255
TOUCH_COORD_TO_ABSOLUTE = 65535 / 255

# 定义输入事件常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

# 获取桌面窗口句柄
desktop = ctypes.windll.user32.GetDesktopWindow()

# 获取触摸板窗口句柄
touchpad = ctypes.windll.user32.FindWindowW("IPTip_Main_Window", None)

win32gui.MoveWindow(touchpad, 100, 100, 800, 600, True)