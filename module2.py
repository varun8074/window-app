#minimize app
import os, psutil
import pythoncom
import pygetwindow as gw
from ctypes import cast, POINTER

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLineEdit, QListWidget
)
from PyQt6.QtCore import QTimer

import keyboard
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def minimize_all_windows(excluded):
    windows = gw.getWindowsWithTitle("")
    for window in windows:
        try:
            if not window.isMinimized and not any(app.lower() in window.title.lower() for app in excluded):
                window.minimize()
        except Exception:
            pass


def mute_system_volume():
    pythoncom.CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)


def close_specified_apps(close_list):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if any(app.lower() in (process.info['name'] or "").lower() for app in close_list):
                os.kill(process.info['pid'], 9)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


class MinimizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(10)

        # Input fields
        self.excluded_edit = QLineEdit()
        self.excluded_edit.setPlaceholderText("Enter excluded apps (comma separated)")
        self.close_edit = QLineEdit()
        self.close_edit.setPlaceholderText("Enter apps to auto-close (comma separated)")

        self.layout().addWidget(QLabel("Excluded Apps:"))
        self.layout().addWidget(self.excluded_edit)
        self.layout().addWidget(QLabel("Apps to Close:"))
        self.layout().addWidget(self.close_edit)

        # Status
        self.status = QLabel("Hotkey: <b>NumLock</b> → Minimize All (except excluded)")
        self.layout().addWidget(self.status)

        # Running apps list
        self.layout().addWidget(QLabel("Currently Running Apps:"))
        self.apps_list = QListWidget()
        self.layout().addWidget(self.apps_list)

        # Control buttons
        row = QHBoxLayout()
        self.bind_btn = QPushButton("Bind NumLock Hotkey")
        self.unbind_btn = QPushButton("Unbind Hotkey")
        row.addWidget(self.bind_btn)
        row.addWidget(self.unbind_btn)
        self.layout().addLayout(row)

        self.min_btn = QPushButton("Minimize Now")
        self.mute_btn = QPushButton("Mute System Volume")
        self.close_btn = QPushButton("Close Specified Apps")
        self.layout().addWidget(self.min_btn)
        self.layout().addWidget(self.mute_btn)
        self.layout().addWidget(self.close_btn)

        # Connections
        self.bind_btn.clicked.connect(self.bind_hotkey)
        self.unbind_btn.clicked.connect(self.unbind_hotkey)
        self.min_btn.clicked.connect(lambda: minimize_all_windows(self._excluded_apps()))
        self.mute_btn.clicked.connect(mute_system_volume)
        self.close_btn.clicked.connect(lambda: close_specified_apps(self._close_apps()))

        # Double-click on running apps list to add directly to input fields
        self.apps_list.itemDoubleClicked.connect(self.add_to_inputs)

        self._hotkey_bound = False

        # Timer updates
        self._refresh = QTimer(self)
        self._refresh.timeout.connect(self._update_status)
        self._refresh.timeout.connect(self._update_apps_list)
        self._refresh.start(2000)  # update every 2 seconds
        self._update_apps_list()

    def _excluded_apps(self):
        return [x.strip().lower() for x in self.excluded_edit.text().split(",") if x.strip()]

    def _close_apps(self):
        return [x.strip().lower() for x in self.close_edit.text().split(",") if x.strip()]

    def bind_hotkey(self):
        if not self._hotkey_bound:
            keyboard.add_hotkey("numlock", lambda: minimize_all_windows(self._excluded_apps()))
            self._hotkey_bound = True
            self._update_status()
# need to change
    def unbind_hotkey(self):
        if self._hotkey_bound:
            try:
                keyboard.remove_hotkey("numlock")
            except KeyError:
                pass
            self._hotkey_bound = False
            self._update_status()

    def _update_status(self):
        self.status.setText(
            f"Hotkey status: {'<b>BOUND</b>' if self._hotkey_bound else '<b>UNBOUND</b>'} (NumLock)"
        )

    def _update_apps_list(self):
        self.apps_list.clear()
        titles = [t for t in gw.getAllTitles() if t.strip()]
        for t in titles:
            self.apps_list.addItem(t)


    def add_to_inputs(self, item):
        """Double-click adds app name to 'Apps to Close' input"""
        app = item.text()
        current = self.close_edit.text().strip()
        if current:
            self.close_edit.setText(current + ", " + app)
        else:
            self.close_edit.setText(app)

    def closeEvent(self, e):
        if self._hotkey_bound:
            self.unbind_hotkey()
        return super().closeEvent(e)


def main():
    return MinimizerWidget()
