#move cursor
import threading, time, random
import pyautogui
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QDoubleSpinBox, QHBoxLayout
from PyQt6.QtCore import QTimer


class AutoClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.running = False
        self.interval = 1.0

        layout = QVBoxLayout()
        layout.addWidget(QLabel("🖱️ Auto Mouse Clicker (with small movements)"))

        row = QHBoxLayout()
        row.addWidget(QLabel("Interval (sec):"))
        self.spin = QDoubleSpinBox()
        self.spin.setDecimals(2)
        self.spin.setMinimum(0.05)
        self.spin.setMaximum(60.0)
        self.spin.setValue(1.0)
        row.addWidget(self.spin)
        layout.addLayout(row)

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.status = QLabel("Status: Stopped")
        layout.addWidget(self.status)
        self.setLayout(layout)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(200)

    def start(self):
        if not self.running:
            self.interval = float(self.spin.value())
            self.running = True
            threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            # get current position
            x, y = pyautogui.position()
            # move slightly (random offset within ±5 px)
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            pyautogui.moveTo(x + dx, y + dy, duration=0.05)
            # click
            pyautogui.click()
            time.sleep(self.interval)

    def _refresh(self):
        self.status.setText(f"Status: {'Running' if self.running else 'Stopped'}")

    def closeEvent(self, e):
        self.running = False
        return super().closeEvent(e)


def main():
    return AutoClicker()
