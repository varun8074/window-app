#click count
from pynput.keyboard import Listener

def main():
    key_count = 0

    def on_press(key):
        nonlocal key_count
        try:
            if key.char == 'a':
                key_count += 1
                print(f"'a' key pressed {key_count} times")
        except AttributeError:
            pass

    def on_release(key):
        if key == 'esc':
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
