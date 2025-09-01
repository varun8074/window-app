#key counter
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea
from PyQt6.QtCore import QTimer
from pynput import keyboard
import threading
import string


class KeyCounter(QWidget):
    def __init__(self):
        super().__init__()

        # counts for all alphabets
        self.counts = {ch: 0 for ch in string.ascii_uppercase}

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🔤 Alphabet Key Counter"))

        # scrollable area (in case window is small)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QGridLayout(container)

        # label dictionary for quick updating
        self.labels = {}
        row, col = 0, 0
        for ch in string.ascii_uppercase:
            lbl = QLabel(f"{ch}: 0")
            lbl.setStyleSheet("font-size: 16px; padding: 4px;")
            self.grid.addWidget(lbl, row, col)
            self.labels[ch] = lbl
            col += 1
            if col >= 6:  # 6 columns layout
                col = 0
                row += 1

        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # start background listener
        self._stop = False
        self.listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        self.listener_thread.start()

        # GUI refresher
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(200)

    def _start_listener(self):
        def on_press(key):
            try:
                if key.char and key.char.isalpha():
                    self.counts[key.char.upper()] += 1
            except AttributeError:
                pass

        with keyboard.Listener(on_press=on_press) as listener:
            while not self._stop:
                listener.join(0.1)

    def _refresh(self):
        for ch, lbl in self.labels.items():
            lbl.setText(f"{ch}: {self.counts[ch]}")

    def closeEvent(self, e):
        self._stop = True
        return super().closeEvent(e)


def main():
    return KeyCounter()
