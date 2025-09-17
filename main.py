import random
import time
import os
from pynput.keyboard import Controller, Key

try:
    import pygetwindow as gw
except ImportError:
    gw = None

NO_DELAY = False # Set to True to disable all delays for testing

# Delays
NORMAL_DELAY = 0.08
BACKSPACE_DELAY = 0.6
NEWLINE_DELAY = 0.8
SP_CHAR_DELAY = 0.25
SPACE_DELAY = 0.5
ARROWS_DELAY = 0.05

# Initialize the keyboard controller
keyboard = Controller()

# Read code_to_type from file
def read_code_to_type(filename="code_to_type.txt"):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return ""
    with open(filename, "r", encoding="utf-8") as f:
        raw = f.read()
        # Interpret backslash escapes (e.g., \n, \b, etc.)
        return raw.encode('utf-8').decode('unicode_escape')

def generate_random_delay(average_delay = NORMAL_DELAY):
    # Delays can be faster for consecutive letters and slower for punctuation
    # or before starting a new word.
    if NO_DELAY:
        return 0.02
    else:
        return random.uniform(0.8 * average_delay, 1.2 * average_delay)

def simulate_typing(text):
    arrows_flag = False

    def handle_arrow_command(char):
        arrow_actions = {
            'u': lambda: (keyboard.press(Key.up), keyboard.release(Key.up)),
            'd': lambda: (keyboard.press(Key.down), keyboard.release(Key.down)),
            'l': lambda: (keyboard.press(Key.left), keyboard.release(Key.left)),
            'r': lambda: (keyboard.press(Key.right), keyboard.release(Key.right)),
            's': lambda: keyboard.press(Key.shift),
            'S': lambda: keyboard.release(Key.shift),
            'e': lambda: (keyboard.press(Key.end), keyboard.release(Key.end)),
            'b': lambda: (keyboard.press(Key.home), keyboard.release(Key.home)),
            'E': lambda: (keyboard.press(Key.ctrl), keyboard.press(Key.end), keyboard.release(Key.end), keyboard.release(Key.ctrl)),
            'B': lambda: (keyboard.press(Key.ctrl), keyboard.press(Key.home), keyboard.release(Key.home), keyboard.release(Key.ctrl)),
            'U': lambda: (keyboard.press(Key.page_up), keyboard.release(Key.page_up)),
            'D': lambda: (keyboard.press(Key.page_down), keyboard.release(Key.page_down)),
            'C': lambda: (keyboard.press(Key.esc), keyboard.release(Key.esc)),
            'z': lambda: time.sleep(5),
        }
        if char == 'Q':
            return 'exit'
        elif char in arrow_actions:
            arrow_actions[char]()
        else:
            raise ValueError(f"Unknown escape command: {char}")

    special_key_actions = {
        '\n': lambda: (keyboard.press(Key.enter), keyboard.release(Key.enter)),
        '\b': lambda: (keyboard.press(Key.backspace), keyboard.release(Key.backspace)),
        ' ': lambda: (keyboard.press(Key.space), keyboard.release(Key.space)),
    }

    def get_delay(char):
        if char == '\n':
            return generate_random_delay(NEWLINE_DELAY)
        elif char == '\b':
            return generate_random_delay(BACKSPACE_DELAY)
        elif char == ' ':
            return generate_random_delay(SPACE_DELAY)
        elif char == '\a':
            return generate_random_delay(ARROWS_DELAY)
        elif char in '`~!@#$%^&*()_+{}|:"<>?':
            return generate_random_delay(SP_CHAR_DELAY)
        else:
            return generate_random_delay()

    def handle_regular_char(char):
        if char.isupper():
            with keyboard.pressed(Key.shift):
                keyboard.press(char.lower())
                keyboard.release(char.lower())
        elif char in '`~!@#$%^&*()_+{}|:"<>?':
            with keyboard.pressed(Key.shift):
                keyboard.press(char)
                keyboard.release(char)
        elif char in special_key_actions:
            special_key_actions[char]()
        else:
            keyboard.press(char)
            keyboard.release(char)

    text_iter = iter(text)
    while True:
        try:
            char = next(text_iter)
        except StopIteration:
            break

        delay = get_delay(char)

        if arrows_flag:
            result = handle_arrow_command(char)
            if result == 'exit':
                arrows_flag = False
            if char == 'z':
                continue
        else:
            if char == '\a':
                arrows_flag = True
            else:
                handle_regular_char(char)

        time.sleep(delay)

# Utility to check if expected window is focused
def is_target_window_focused(expected_title_substring):
    if gw is None:
        print("pygetwindow not installed. Skipping window focus check.")
        return True
    win = gw.getActiveWindow()
    if win and expected_title_substring.lower() in win.title.lower():
        return True
    print(f"Active window is '{win.title if win else None}'. Waiting for '{expected_title_substring}' window...")
    return False

# Check if target window is focused before typing
expected_title = "PowerShell"  # Change to your target application's window title substring
while not is_target_window_focused(expected_title):
    print("Please focus the target application window...")
    time.sleep(2)

# Read code from file and type it
code_to_type = read_code_to_type("code_to_type_vim.txt")
simulate_typing(code_to_type)

print("Typing complete.")