# record_n_replay_mouse events
import os, threading, time
from pynput import mouse
from pynput.mouse import Button, Controller

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox, QSlider, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt

file_path = "click_positions.txt"
mouse_controller = Controller()


class Recorder(QWidget):
    info_signal = pyqtSignal(str)   # 🔹 thread-safe message signal

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Mouse Recorder & Replayer"))

        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")
        self.replay_btn = QPushButton("Replay Clicks")
        self.clear_btn = QPushButton("Clear Recording")

        # 🔹 Speed control slider
        self.speed_label = QLabel("Replay Speed: 1.0x")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)    # 0.1x
        self.speed_slider.setMaximum(30)   # 3.0x
        self.speed_slider.setValue(10)     # default 1.0x
        self.speed_slider.valueChanged.connect(self._update_speed_label)

        # UI Layout
        for b in (self.start_btn, self.stop_btn, self.replay_btn, self.clear_btn):
            self.layout().addWidget(b)

        hbox = QHBoxLayout()
        hbox.addWidget(self.speed_label)
        hbox.addWidget(self.speed_slider)
        self.layout().addLayout(hbox)

        self.listener = None
        self.info_signal.connect(self._info)

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.replay_btn.clicked.connect(self.replay_clicks)
        self.clear_btn.clicked.connect(self.clear_recording)

    def start_recording(self):
        if self.listener is not None:
            QMessageBox.information(self, "Info", "Already recording!")
            return

        def on_click(x, y, button, pressed):
            if pressed:
                with open(file_path, "a") as f:
                    f.write(f"{x},{y},{time.time()}\n")   # 🔹 record timestamp

        self.listener = mouse.Listener(on_click=on_click)
        self.listener.start()
        QMessageBox.information(self, "Recording", "Click recording started!")

    def stop_recording(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
            QMessageBox.information(self, "Stopped", "Recording stopped.")
        else:
            QMessageBox.information(self, "Info", "No session running.")

    def replay_clicks(self):
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", "No click positions recorded yet.")
            return

        speed_factor = self.speed_slider.value() / 10.0   # 🔹 convert slider to multiplier

        def replay():
            with open(file_path, "r") as f:
                records = [line.strip().split(",") for line in f.readlines()]
                positions = [(int(x), int(y), float(t)) for x, y, t in records]

            if len(positions) < 3:
                self.info_signal.emit("Need at least 3 positions.")
                return

            positions_use = positions[1:-1]
            self.info_signal.emit(f"Replaying clicks at {speed_factor:.1f}x in 3 seconds…")
            time.sleep(3)

            for i, (x, y, t) in enumerate(positions_use):
                if i > 0:
                    delay = (t - positions_use[i - 1][2]) / speed_factor
                    time.sleep(max(0, delay))
                mouse_controller.position = (x, y)
                mouse_controller.click(Button.left, 1)

            self.info_signal.emit("Replay finished.")

        threading.Thread(target=replay, daemon=True).start()

    def clear_recording(self):
        if os.path.exists(file_path):
            os.remove(file_path)
            QMessageBox.information(self, "Cleared", "Recordings cleared.")

    def _update_speed_label(self):
        val = self.speed_slider.value() / 10.0
        self.speed_label.setText(f"Replay Speed: {val:.1f}x")

    def _info(self, msg):
        QMessageBox.information(self, "Info", msg)

    def closeEvent(self, e):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        return super().closeEvent(e)


def main():
    return Recorder()
