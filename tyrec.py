import argparse
import os
import random
import threading
import time

# Optional: For window focus checking (pygetwindow)
try:
    import pygetwindow as gw
except Exception:
    gw = None

# Try to import real pynput; if it's not available provide dry-run dummies so the
# module can be imported and exercised in CI/dev without GUI access.
try:
    from pynput.keyboard import Controller, Key, Listener

    PYNPUT_AVAILABLE = True
except Exception:
    PYNPUT_AVAILABLE = False

    class Key:
        enter = "enter"
        backspace = "backspace"
        space = "space"
        up = "up"
        down = "down"
        left = "left"
        right = "right"
        ctrl = "ctrl"
        shift = "shift"
        end = "end"
        home = "home"
        page_up = "page_up"
        page_down = "page_down"
        esc = "esc"

    class Controller:
        def press(self, k):
            print(f"[dry-run] press: {k}")

        def release(self, k):
            print(f"[dry-run] release: {k}")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        # Provide a context manager compatible with pynput's Controller.pressed(key)
        class _PressedContext:
            def __init__(self, controller, key):
                self._controller = controller
                self._key = key

            def __enter__(self):
                self._controller.press(self._key)
                return None

            def __exit__(self, exc_type, exc, tb):
                self._controller.release(self._key)
                return False

        def pressed(self, key):
            return Controller._PressedContext(self, key)


# Event set when live input recording is active (Pause/Break toggles it)
LIVE_INPUT_MODE = threading.Event()


def start_pause_listener():
    """Start a background listener that toggles LIVE_INPUT_MODE when Pause/Break is pressed.

    Returns the Listener instance or None if pynput is unavailable.
    """
    if not PYNPUT_AVAILABLE:
        print("Pause/Break toggle not available: pynput not installed.")
        return None

    def _on_press(key):
        try:
            if key == Key.pause:
                if LIVE_INPUT_MODE.is_set():
                    LIVE_INPUT_MODE.clear()
                    print("[tyrec] Pause pressed: resuming file processing...")
                else:
                    LIVE_INPUT_MODE.set()
                    print(
                        "[tyrec] Pause pressed: pausing file processing. Recording live keyboard input. Press Pause again to resume."
                    )
        except Exception:
            pass

    listener = Listener(on_press=_on_press)
    listener.daemon = True
    listener.start()
    return listener


# For testing purposes, set this to True to disable delays
NO_DELAY = False  # Set to True to disable all delays for testing

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
        return raw.encode("utf-8").decode("unicode_escape")


def generate_random_delay(average_delay=NORMAL_DELAY):
    # Delays can be faster for consecutive letters and slower for punctuation
    # or before starting a new word.
    if NO_DELAY:
        return 0.02
    else:
        return random.uniform(0.8 * average_delay, 1.2 * average_delay)


def simulate_typing(text):
    arrows_flag = False
    live_recorded = []  # collected live input while paused

    def handle_arrow_command(char):
        arrow_actions = {
            "u": lambda: (keyboard.press(Key.up), keyboard.release(Key.up)),
            "d": lambda: (keyboard.press(Key.down), keyboard.release(Key.down)),
            "l": lambda: (keyboard.press(Key.left), keyboard.release(Key.left)),
            "r": lambda: (keyboard.press(Key.right), keyboard.release(Key.right)),
            "s": lambda: keyboard.press(Key.shift),
            "S": lambda: keyboard.release(Key.shift),
            "e": lambda: (keyboard.press(Key.end), keyboard.release(Key.end)),
            "b": lambda: (keyboard.press(Key.home), keyboard.release(Key.home)),
            "E": lambda: (
                keyboard.press(Key.ctrl),
                keyboard.press(Key.end),
                keyboard.release(Key.end),
                keyboard.release(Key.ctrl),
            ),
            "B": lambda: (
                keyboard.press(Key.ctrl),
                keyboard.press(Key.home),
                keyboard.release(Key.home),
                keyboard.release(Key.ctrl),
            ),
            "U": lambda: (keyboard.press(Key.page_up), keyboard.release(Key.page_up)),
            "D": lambda: (
                keyboard.press(Key.page_down),
                keyboard.release(Key.page_down),
            ),
            "C": lambda: (keyboard.press(Key.esc), keyboard.release(Key.esc)),
            "z": lambda: time.sleep(5),
        }
        if char == "Q":
            return "exit"
        elif char in arrow_actions:
            arrow_actions[char]()
        else:
            raise ValueError(f"Unknown escape command: {char}")

    special_key_actions = {
        "\n": lambda: (keyboard.press(Key.enter), keyboard.release(Key.enter)),
        "\b": lambda: (keyboard.press(Key.backspace), keyboard.release(Key.backspace)),
        " ": lambda: (keyboard.press(Key.space), keyboard.release(Key.space)),
    }

    def get_delay(char):
        if char == "\n":
            return generate_random_delay(NEWLINE_DELAY)
        elif char == "\b":
            return generate_random_delay(BACKSPACE_DELAY)
        elif char == " ":
            return generate_random_delay(SPACE_DELAY)
        elif char == "\a":
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

        if LIVE_INPUT_MODE.is_set():
            # Recording live input until Pause/Break toggles again
            if not PYNPUT_AVAILABLE:
                print("Live input recording unavailable: pynput not installed.")
            else:
                print(
                    "Recording live input — press Pause/Break to stop recording and resume file processing."
                )

                # Use a listener to record keys until LIVE_INPUT_MODE cleared
                recorded = []

                def _on_press(k):
                    try:
                        recorded.append(k)
                    except Exception:
                        pass

                with Listener(on_press=_on_press) as rec_listener:
                    # Block here until LIVE_INPUT_MODE cleared by pause listener
                    while LIVE_INPUT_MODE.is_set():
                        time.sleep(0.1)
                    # stop listener
                    rec_listener.stop()

                live_recorded.extend(recorded)
                print(f"Recorded {len(recorded)} live key events.")

            # After recording, continue processing the next character from the file
            continue

        if arrows_flag:
            result = handle_arrow_command(char)
            if result == "exit":
                arrows_flag = False
            if char == "z":
                continue
        else:
            if char == "\a":
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
    print(
        f"Active window is '{win.title if win else None}'. Waiting for '{expected_title_substring}' window..."
    )
    return False


# Check if target window is focused before typing
def main():
    parser = argparse.ArgumentParser(description="Typing recorder TyRec.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to the input file containing text/commands to type",
    )
    parser.add_argument(
        "--active_window_title",
        "-t",
        dest="active_window_title",
        default="PowerShell",
        help="Expected window title substring to wait for before typing (default: PowerShell). This works on Windows only.",
    )
    parser.add_argument(
        "--no-delay",
        action="store_true",
        help="Disable random delays for faster testing",
    )

    args = parser.parse_args()

    # Allow overriding NO_DELAY from CLI
    global NO_DELAY
    if args.no_delay:
        NO_DELAY = True

    expected_title = args.active_window_title

    # Start the Pause/Break listener to allow toggling live input recording
    pause_listener = start_pause_listener()

    # Wait until target window is focused (if pygetwindow is available)
    while not is_target_window_focused(expected_title):
        print("Please focus the target application window...")
        time.sleep(2)

    # Require an explicit input file to avoid accidental typing of a default file
    if args.input_file is None:
        print(
            "No input file provided. Please specify an input file to type (e.g. ./tyrec input.txt). Use --help for details."
        )
        return

    # Read code from the requested input file
    code_to_type = read_code_to_type(args.input_file)
    if not code_to_type:
        print("No code to type. Exiting.")
        return

    # Always print the processed input to stdout so users can capture or pipe it.
    print(code_to_type)

    simulate_typing(code_to_type)
    print("Typing complete.")


if __name__ == "__main__":
    main()
