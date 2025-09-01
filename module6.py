#transparent
import ctypes
import pygetwindow as gw
from pywinauto import Application

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QSlider, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget
)
from PyQt6.QtCore import Qt, QTimer


def set_window_transparency(window_title: str, alpha_0_1: float):
    """Apply transparency to the given window title"""
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

        # WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(alpha_0_1 * 255), 2)
    except Exception as e:
        raise RuntimeError(str(e))


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
        try:
            set_window_transparency(title, alpha)
            QMessageBox.information(self, "Done", f"Transparency set to {self.slider.value()}% for '{title}'.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))


def main():
    return TransparencyWidget()
