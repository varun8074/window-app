#scroll count
import threading
from pynput import mouse
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import QTimer


class ScrollCounter(QWidget):
    def __init__(self):
        super().__init__()
        self.up = 0
        self.down = 0

        layout = QVBoxLayout()
        self.title = QLabel("🖱️ Scroll Counter")
        self.label_up = QLabel("Scrolled up: 0")
        self.label_down = QLabel("Scrolled down: 0")
        self.reset_btn = QPushButton("Reset Counter")

        layout.addWidget(self.title)
        layout.addWidget(self.label_up)
        layout.addWidget(self.label_down)
        layout.addWidget(self.reset_btn)
        self.setLayout(layout)

        self.reset_btn.clicked.connect(self.reset)

        self._stop = False
        threading.Thread(target=self._listen, daemon=True).start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(150)

    def _listen(self):
        def on_scroll(x, y, dx, dy):
            if dy > 0:
                self.up += 1
            elif dy < 0:
                self.down += 1

        with mouse.Listener(on_scroll=on_scroll) as listener:
            while not self._stop:
                listener.join(0.1)

    def _refresh(self):
        self.label_up.setText(f"Scrolled up: {self.up}")
        self.label_down.setText(f"Scrolled down: {self.down}")

    def reset(self):
        self.up = 0
        self.down = 0
        self._refresh()

    def closeEvent(self, e):
        self._stop = True
        return super().closeEvent(e)


def main():
    return ScrollCounter()
