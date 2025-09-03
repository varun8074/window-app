#transparent_fixed.py
import ctypes
import pygetwindow as gw
from pywinauto import Application

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QSlider, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer


# --- Constants and helpers ---
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
LWA_ALPHA = 0x00000002

def _get_set_window_long_ptr():
    """Return proper Get/SetWindowLong function depending on platform (32/64-bit)."""
    if ctypes.sizeof(ctypes.c_void_p) == 8:
        GetWindowLongPtr = ctypes.windll.user32.GetWindowLongPtrW
        SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW
    else:
        GetWindowLongPtr = ctypes.windll.user32.GetWindowLongW
        SetWindowLongPtr = ctypes.windll.user32.SetWindowLongW
    return GetWindowLongPtr, SetWindowLongPtr


def set_window_transparency(window_title: str, alpha_0_1: float, click_through: bool = False):
    """Apply transparency to the given window title, preserving interactivity unless click-through enabled."""
    try:
        all_titles = [t for t in gw.getAllTitles() if t]
        match = [t for t in all_titles if window_title.lower() in t.lower()]
        if not match:
            raise RuntimeError(
                f"No matching window found for '{window_title}'.\n\n"
                f"Available: {all_titles[:10]}…"
            )

        title_to_use = match[0]
        app = Application(backend="win32").connect(title=title_to_use)
        window = app.window(title=title_to_use)
        if window.is_minimized():
            window.restore()
        window.set_focus()
        hwnd = window.handle

        # Preserve existing extended styles and add/remove flags safely
        GetWindowLongPtr, SetWindowLongPtr = _get_set_window_long_ptr()
        exstyle = GetWindowLongPtr(hwnd, GWL_EXSTYLE)

        # Always layered for alpha
        exstyle |= WS_EX_LAYERED

        # Only make click-through if explicitly requested
        if click_through:
            exstyle |= WS_EX_TRANSPARENT
        else:
            exstyle &= ~WS_EX_TRANSPARENT

        SetWindowLongPtr(hwnd, GWL_EXSTYLE, exstyle)

        # Apply alpha (0..1 -> 0..255)
        a = max(0, min(1, float(alpha_0_1)))
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(a * 255), LWA_ALPHA)

        # Nudge the window so the new style is honored immediately
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
        )

        # If fully opaque and not click-through, drop LAYERED to avoid edge cases
        if a >= 0.995 and not click_through:
            exstyle &= ~WS_EX_LAYERED
            SetWindowLongPtr(hwnd, GWL_EXSTYLE, exstyle)

    except Exception as e:
        raise RuntimeError(str(e))


# --- GUI Widget ---
class TransparencyWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🪟 Window Transparency Setter"))

        # Title input
        row = QHBoxLayout()
        row.addWidget(QLabel("Window Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter part of the window title (e.g. 'Notepad')")
        row.addWidget(self.title_edit)
        layout.addLayout(row)

        # Transparency slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(100)
        self.slider.setValue(70)

        layout.addWidget(QLabel("Transparency (%)"))
        layout.addWidget(self.slider)

        # Click-through option
        self.clickthrough_cb = QCheckBox("Click-through (ignore mouse & keyboard)")
        layout.addWidget(self.clickthrough_cb)

        # Apply button
        self.apply_btn = QPushButton("Apply Transparency")
        layout.addWidget(self.apply_btn)

        # Running apps list
        layout.addWidget(QLabel("Currently Running Windows:"))
        self.apps_list = QListWidget()
        layout.addWidget(self.apps_list)

        self.setLayout(layout)
        self.apply_btn.clicked.connect(self.apply)

        # Timer to refresh running apps
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_apps_list)
        self.timer.start(2000)  # refresh every 2 seconds
        self.update_apps_list()

        # Allow double-click to set title
        self.apps_list.itemDoubleClicked.connect(self.set_title_from_list)

    def update_apps_list(self):
        self.apps_list.clear()
        titles = [t for t in gw.getAllTitles() if t.strip()]
        for t in titles:
            self.apps_list.addItem(t)

    def set_title_from_list(self, item):
        """When user double-clicks an item, copy it to input"""
        self.title_edit.setText(item.text())

    def apply(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Please enter or select a window title.")
            return

        alpha = self.slider.value() / 100.0
        click_through = self.clickthrough_cb.isChecked()
        try:
            set_window_transparency(title, alpha, click_through)
            msg = f"Transparency set to {self.slider.value()}% for '{title}'."
            if click_through:
                msg += "\n(Note: Window is now click-through!)"
            QMessageBox.information(self, "Done", msg)
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))


def main():
    return TransparencyWidget()
