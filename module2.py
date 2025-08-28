#minimize app
import pygetwindow as gw
import keyboard
import pythoncom
import psutil, os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

EXCLUDED_APPS = ["mail - google chrome", "Visual Studio Code"]
CLOSE_APPS = ["BlockedIn"]

def minimize_all_windows():
    close_specified_apps()
    windows = gw.getWindowsWithTitle("")
    for window in windows:
        if not window.isMinimized and not any(app.lower() in window.title.lower() for app in EXCLUDED_APPS):
            window.minimize()

def mute_system_volume():
    pythoncom.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)

def close_specified_apps():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if any(app.lower() in process.info['name'].lower() for app in CLOSE_APPS):
                os.kill(process.info['pid'], 9)
                print(f"Closed {process.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def main():
    keyboard.add_hotkey("numlock", minimize_all_windows)
    print("Press Num Lock to minimize all windows (except Chrome & VS Code). Press ESC to exit.")
    keyboard.wait("esc")
