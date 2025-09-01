#shift rightclick->long right click
import time, threading
from pynput import mouse, keyboard
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import QTimer

HOLD_DURATION = 0.5


class LongRightClick(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Hold Right-Click → Auto Shift+Right-Click"))

        self.status = QLabel("Status: Stopped")
        self.layout().addWidget(self.status)

        self.start_btn = QPushButton("Start Listener")
        self.stop_btn = QPushButton("Stop Listener")
        self.layout().addWidget(self.start_btn)
        self.layout().addWidget(self.stop_btn)

        self._press_time = None
        self._action_triggered = False
        self._running = False
        self._listener = None

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(200)

    def _monitor(self):
        kbd = keyboard.Controller()
        ms = mouse.Controller()
        while self._running:
            if self._press_time and not self._action_triggered:
                if time.time() - self._press_time >= HOLD_DURATION:
                    self._action_triggered = True
                    kbd.press(keyboard.Key.shift)
                    time.sleep(0.05)
                    ms.press(mouse.Button.right)
                    ms.release(mouse.Button.right)
                    time.sleep(0.05)
                    kbd.release(keyboard.Key.shift)
            time.sleep(0.01)

    def _on_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            if pressed:
                self._press_time = time.time()
                self._action_triggered = False
            else:
                self._press_time = None
                self._action_triggered = False

    def start(self):
        if self._running:
            return
        self._running = True
        threading.Thread(target=self._monitor, daemon=True).start()
        self._listener = mouse.Listener(on_click=self._on_click)
        self._listener.start()

    def stop(self):
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _refresh(self):
        self.status.setText(f"Status: {'Running' if self._running else 'Stopped'}")

    def closeEvent(self, e):
        self.stop()
        return super().closeEvent(e)


def main():
    return LongRightClick()
