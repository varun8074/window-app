# record_n_replay_mouse events
import tkinter as tk
from tkinter import messagebox
from pynput import mouse
from pynput.mouse import Button, Controller
import threading, time, os

file_path = "click_positions.txt"
listener = None
mouse_controller = Controller()

def start_recording():
    global listener
    if listener is not None:
        messagebox.showinfo("Info", "Already recording!")
        return
    def on_click(x, y, button, pressed):
        if pressed:
            with open(file_path, "a") as f:
                f.write(f"{x},{y}\n")
            print(f"Recorded click at ({x}, {y})")
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    messagebox.showinfo("Recording", "Click recording started!")

def stop_recording():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
        messagebox.showinfo("Stopped", "Recording stopped.")
    else:
        messagebox.showinfo("Info", "No session running.")

def replay_clicks():
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No click positions recorded yet.")
        return
    def replay():
        with open(file_path, "r") as f:
            positions = [tuple(map(int, line.strip().split(","))) for line in f.readlines()]
        if len(positions) < 3:
            messagebox.showinfo("Info", "Need at least 3 positions.")
            return
        positions = positions[1:-1]
        messagebox.showinfo("Replay", "Replaying clicks in 3 seconds...")
        time.sleep(3)
        for pos in positions:
            x, y = pos
            mouse_controller.position = (x, y)
            time.sleep(0.5)
            mouse_controller.click(Button.left, 1)
            print(f"Clicked at ({x}, {y})")
        messagebox.showinfo("Done", "Replay finished.")
    threading.Thread(target=replay).start()

def clear_recording():
    if os.path.exists(file_path):
        os.remove(file_path)
        messagebox.showinfo("Cleared", "Recordings cleared.")

def main():
    window = tk.Tk()
    window.title("Mouse Recorder & Replayer")
    window.geometry("350x250")
    window.resizable(False, False)

    tk.Button(window, text="Start Recording", command=start_recording, height=2, width=20, bg="#4CAF50", fg="white").pack(pady=10)
    tk.Button(window, text="Stop Recording", command=stop_recording, height=2, width=20, bg="#f44336", fg="white").pack(pady=10)
    tk.Button(window, text="Replay Clicks", command=replay_clicks, height=2, width=20, bg="#2196F3", fg="white").pack(pady=10)
    tk.Button(window, text="Clear Recording", command=clear_recording, height=2, width=20, bg="#9E9E9E", fg="white").pack(pady=10)

    window.mainloop()
