import random
import time
from pynput.keyboard import Controller, Key

NO_DELAY = False

# Delays
NORMAL_DELAY = 0.08
BACKSPACE_DELAY = 0.6
NEWLINE_DELAY = 0.8
SP_CHAR_DELAY = 0.25
SPACE_DELAY = 0.5
ARROWS_DELAY = 0.05

# Initialize the keyboard controller
keyboard = Controller()

code_to_type = """# GEMM: d = alpha*a*b\b\b@b + beta*c
# Implement GEMM using CuPy
import cupy as cp

# Define matrix dimensions m, n, k
m, n, k = 40, 10, 1000\b\b\b_000_000

# Create random matrices
a = cp.random.rand(m, k, dtype=cp.float32)
b = cp.random.rand(k, n, dtype=cp.float32)
c = cp.random.rand(m, n, dtype=cp.float32)

alpha = 1.5
beta = 0.5

# Compute GEMM
d = alpha * a @ b + beta * c
\azBdbseSQ# Implement GEMM using nvmath-python
import nvmath\aEsbSQd = nvmath.linalg.advanced.matmul(a, b, c, alpha=alhpa,\b\b\b\bpha, beta=beta)
\azsuuubSQ
# Now benchmark with cupyx.profiler.benchmark()
\aBddddeQfrom cupyx.profiler import benchmark

\aEQbenchmark(lambda: alpha * a @ a + beta * a, n_repeat=5, n_warmup=1)
benchmark(lambda: nvmath.linalg.advanced.matmul(a, b, c, alpha=alpha, beta=beta), n_repeat=5, n_warmup=1)\abQprint(\aeQ)\auQ)\abQprint("""


def generate_random_delay(average_delay = NORMAL_DELAY):
    # Delays can be faster for consecutive letters and slower for punctuation
    # or before starting a new word.
    if NO_DELAY:
        return 0.0
    else:
        return random.uniform(0.8 * average_delay, 1.2 * average_delay)

def simulate_typing(text):
    arrows_flag = False
    for char in text:
        delay = generate_random_delay()

        if arrows_flag:
            # u - up arrow
            # d - down arrow
            # l - left arrow
            # r - right arraw
            # s - press shift
            # S - release shift
            # e - end of line
            # b - beginning of line
            # E - end of file
            # B - beginning of file
            # U - page up
            # D - page down
            # z - delay for 5 sec
            # Q - exit arrows mode

            if char == 'Q':
                arrows_flag = False
            elif char == 'u':
                keyboard.press(Key.up)
                keyboard.release(Key.up)
            elif char == 'd':
                keyboard.press(Key.down)
                keyboard.release(Key.down)
            elif char == 'l':
                keyboard.press(Key.left)
                keyboard.release(Key.right)
            elif char == 'r':
                keyboard.press(Key.right)
                keyboard.release(Key.right)
            elif char == 's':
                keyboard.press(Key.shift)
            elif char == 'S':
                keyboard.release(Key.shift)
            elif char == 'e':
                keyboard.press(Key.end)
                keyboard.release(Key.end)
            elif char == 'b':
                keyboard.press(Key.home)
                keyboard.release(Key.home)
            elif char == 'E':
                with keyboard.pressed(Key.ctrl):
                    keyboard.press(Key.end)
                    keyboard.release(Key.end)
            elif char == 'B':
                with keyboard.pressed(Key.ctrl):
                    keyboard.press(Key.home)
                    keyboard.release(Key.home)
            elif char == 'U':
                keyboard.press(Key.page_up)
                keyboard.release(Key.page_up)
            elif char == 'D':
                keyboard.press(Key.page_down)
                keyboard.release(Key.page_down)
            elif char == 'z':
                time.sleep(5)
            else:
                raise ValueError
        else:             
            if char.isupper():
                # For uppercase characters, press and hold Shift.
                with keyboard.pressed(Key.shift):
                    keyboard.press(char.lower())
                    keyboard.release(char.lower())
            elif char in '`~!@#$%^&*()_+{}|:"<>?':
                # For special characters that require Shift, press Shift.
                with keyboard.pressed(Key.shift):
                    delay = generate_random_delay(SP_CHAR_DELAY)
                    keyboard.press(char)
                    keyboard.release(char)
            elif char == '\n':
                # Handle newlines as pressing the Enter key.
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
                # Add a slightly longer delay after a newline.
                delay = generate_random_delay(NEWLINE_DELAY)
            elif char == '\b':
                # Introduce greater delay when removing symbols
                delay = generate_random_delay(BACKSPACE_DELAY)
                keyboard.press(Key.backspace)
                keyboard.release(Key.backspace)
            elif char == ' ':
                # When pressing word delimiter, increase delay
                delay = generate_random_delay(SPACE_DELAY)
                keyboard.press(Key.space)
                keyboard.release(Key.space)
            elif char == '\a':
                # Enter arrows mode. Next sequence of characters interpreted as arrow controls
                delay = generate_random_delay(ARROWS_DELAY)
                arrows_flag = True
            else:
                # For all other characters, just press and release.
                keyboard.press(char)
                keyboard.release(char)

        # Introduce a sleep after every keypress.
        time.sleep(delay)

# Wait a few seconds to give you time to switch to the target window
# (e.g., a text editor, IDE, or terminal).
print("Switch to the target window in 10 seconds...")
time.sleep(10)

# Execute the function to type the code
simulate_typing(code_to_type)

print("Typing complete.")
