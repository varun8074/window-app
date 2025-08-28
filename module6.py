#transparent
import ctypes, pygetwindow as gw
from pywinauto import Application
import time

def set_window_transparency(window_title, transparency):
    try:
        all_titles = gw.getAllTitles()
        if window_title not in all_titles:
            print(f"Window '{window_title}' not found. Available: {all_titles}")
            return
        app = Application(backend="win32").connect(title=window_title)
        window = app.window(title=window_title)
        if window.is_minimized():
            window.restore()
        window.set_focus()
        hwnd = window.handle
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(transparency * 255), 2)
        print(f"Transparency of '{window_title}' set to {transparency*100}%")
    except Exception as e:
        print(f"Error: {e}")

def main():
    window_title = "Blocked In"  # Change as needed
    set_window_transparency(window_title, 0.5)
    time.sleep(5)
