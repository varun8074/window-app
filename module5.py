#scroll count
from pynput.mouse import Listener

def main():
    scroll_up_count = 0
    scroll_down_count = 0
    def on_scroll(x, y, dx, dy):
        nonlocal scroll_up_count, scroll_down_count
        if dy > 0:
            scroll_up_count += 1
            print(f"Scrolled up {scroll_up_count} times")
        elif dy < 0:
            scroll_down_count += 1
            print(f"Scrolled down {scroll_down_count} times")
    with Listener(on_scroll=on_scroll) as listener:
        listener.join()
