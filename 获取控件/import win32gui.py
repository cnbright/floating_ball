import win32gui

# 获取Quicker面板窗口句柄
hwnd = win32gui.FindWindow(None, "Quicker面板窗口")

print(hwnd)
