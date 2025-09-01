# record_n_replay_mouse events
import os, threading, time
from pynput import mouse
from pynput.mouse import Button, Controller

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox

file_path = "click_positions.txt"
mouse_controller = Controller()


class Recorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Mouse Recorder & Replayer"))

        self.start_btn = QPushButton("Start Recording")
        self.stop_btn = QPushButton("Stop Recording")
        self.replay_btn = QPushButton("Replay Clicks")
        self.clear_btn = QPushButton("Clear Recording")
        for b in (self.start_btn, self.stop_btn, self.replay_btn, self.clear_btn):
            self.layout().addWidget(b)

        self.listener = None

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
                    f.write(f"{x},{y}\n")

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

        def replay():
            with open(file_path, "r") as f:
                positions = [tuple(map(int, line.strip().split(","))) for line in f.readlines()]
            if len(positions) < 3:
                self._info("Need at least 3 positions.")
                return
            positions_use = positions[1:-1]
            self._info("Replaying clicks in 3 seconds…")
            time.sleep(3)
            for x, y in positions_use:
                mouse_controller.position = (x, y)
                time.sleep(0.5)
                mouse_controller.click(Button.left, 1)
            self._info("Replay finished.")

        threading.Thread(target=replay, daemon=True).start()

    def clear_recording(self):
        if os.path.exists(file_path):
            os.remove(file_path)
            QMessageBox.information(self, "Cleared", "Recordings cleared.")

    def _info(self, msg):
        # helper to show info from worker thread
        QMessageBox.information(self, "Info", msg)

    def closeEvent(self, e):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        return super().closeEvent(e)


def main():
    return Recorder()
