#!/usr/bin/env python3
"""Test script to verify syntax highlighting is working in the raw editor."""

import curses
import os
import sys

sys.path.append(os.path.dirname(__file__))
from struct_editor import StructEditor


def test_syntax_highlighting():
    """Quick test to verify syntax highlighting works."""

    # Create a test file with Python code
    test_content = """<CODE: PYTHON>
    import numpy as np
    import matplotlib.pyplot as plt

    def calculate(x, y):
        return x + y

    # This is a comment
    result = calculate(10, 20)
    print(f"Result: {result}")

    for i in range(5):
        print(i)
</CODE>

<COMMANDS>
    ARROW_LEFT 3
    ENTER 2
</COMMANDS>

<CODE>
    stats = {
        'mean': np.mean(data),
        'std': np.std(data)
    }
</CODE>"""

    # Write test content to a temporary file
    test_file = "tests/test_highlighting.sxt"
    with open(test_file, "w") as f:
        f.write(test_content)

    print(f"Created test file: {test_file}")
    print("Run: python struct_editor.py tests/test_highlighting.sxt")
    print("You should see Python syntax highlighting in the left pane:")
    print("- Keywords like 'import', 'def', 'for', 'if' in one color")
    print("- Strings in another color")
    print("- Functions like 'calculate', 'print', 'range' highlighted")
    print("- Numbers and operators highlighted")
    print("- Comments in a different color")
    print("- But COMMANDS section should use basic highlighting")


if __name__ == "__main__":
    test_syntax_highlighting()
