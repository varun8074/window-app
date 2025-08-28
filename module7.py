#shift rightclick->long right click
import time, threading
from pynput import mouse, keyboard

HOLD_DURATION = 0.5
keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()
press_time = None
action_triggered = False

def monitor_hold():
    global press_time, action_triggered
    while True:
        if press_time and not action_triggered:
            if time.time() - press_time >= HOLD_DURATION:
                print("Hold exceeded, performing Shift+Right-click")
                action_triggered = True
                keyboard_controller.press(keyboard.Key.shift)
                time.sleep(0.05)
                mouse_controller.press(mouse.Button.right)
                mouse_controller.release(mouse.Button.right)
                time.sleep(0.05)
                keyboard_controller.release(keyboard.Key.shift)
        time.sleep(0.01)

def on_click(x, y, button, pressed):
    global press_time, action_triggered
    if button == mouse.Button.right:
        if pressed:
            press_time = time.time()
            action_triggered = False
        else:
            press_time = None
            action_triggered = False

def main():
    threading.Thread(target=monitor_hold, daemon=True).start()
    with mouse.Listener(on_click=on_click) as listener:
        print("Hold right-click to auto Shift+Right-click...")
        listener.join()
