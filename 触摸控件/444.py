from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 获取系统默认的音频设备
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 获取系统音量
current_volume = volume.GetMasterVolumeLevelScalar()

# 将音量转换为百分比
current_volume_percentage = round(current_volume * 100)

# 输出当前系统音量
print(f"当前系统音量为：{current_volume_percentage}%")
