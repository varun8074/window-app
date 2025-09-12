# minimize app (fixed with QThread)
import os, psutil
import pythoncom
import pygetwindow as gw
from ctypes import cast, POINTER

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal

import keyboard
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ----------------- Core functions -----------------
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
    close_list = [x.lower() for x in close_list]  # normalize

    for window in gw.getAllWindows():
        try:
            if not window.title.strip():
                continue

            title = window.title.lower()
            if any(app in title for app in close_list):  # match by title
                import win32process
                _, proc_id = win32process.GetWindowThreadProcessId(window._hWnd)
                if proc_id:
                    try:
                        proc = psutil.Process(proc_id)
                        proc.kill()  # force close
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except Exception:
            pass


# ----------------- Worker Thread -----------------
class Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, excluded, to_close):
        super().__init__()
        self.excluded = excluded
        self.to_close = to_close

    def run(self):
        try:
            minimize_all_windows(self.excluded)
            mute_system_volume()
            close_specified_apps(self.to_close)
        except Exception as e:
            print("Worker error:", e)
        self.finished.emit()


# ----------------- Main Widget -----------------
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
        self.min_btn.clicked.connect(self.run_worker_once)
        self.mute_btn.clicked.connect(mute_system_volume)
        self.close_btn.clicked.connect(lambda: close_specified_apps(self._close_apps()))

        # Double-click on running apps list to add directly to input fields
        self.apps_list.itemDoubleClicked.connect(self.add_to_inputs)

        self._hotkey_bound = False
        self._worker_running = False

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

    # ----------------- Hotkey -----------------
    def bind_hotkey(self):
        if not self._hotkey_bound:
            keyboard.add_hotkey("numlock", self._on_hotkey_triggered)
            self._hotkey_bound = True
            self._update_status()

    def unbind_hotkey(self):
        if self._hotkey_bound:
            try:
                keyboard.remove_hotkey("numlock")
            except KeyError:
                pass
            self._hotkey_bound = False
            self._update_status()

    def _on_hotkey_triggered(self):
        self.run_worker_once()

    def run_worker_once(self):
        if self._worker_running:
            print("Worker already running, skipping...")
            return
        self._worker_running = True
        self.worker = Worker(self._excluded_apps(), self._close_apps())
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_finished(self):
        self._worker_running = False
        print("Worker finished.")

    # ----------------- Status + Apps list -----------------
    def _update_status(self):
        self.status.setText(
            f"Hotkey status: {'<b>BOUND</b>' if self._hotkey_bound else '<b>UNBOUND</b>'} (NumLock)"
        )

    def _update_apps_list(self):
        self.apps_list.clear()
        titles = [t for t in gw.getAllTitles() if t.strip()]
        for t in titles:
            self.apps_list.addItem(t)

    # ----------------- Add to input -----------------
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