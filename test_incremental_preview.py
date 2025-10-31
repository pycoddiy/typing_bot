#!/usr/bin/env python3
"""
Test script to verify incremental command preview.
"""

import os
import sys
import tempfile

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from struct_editor import StructEditor
from structured_capture import StructuredParser

class TestEditor(StructEditor):
    def __init__(self):
        self.parser = StructuredParser()

def test_incremental_preview():
    content = """<CODE: PYTHON>
    x.shape, y1.shape
    {{IF_NAME_MAIN}}
        {{PRINT_DEBUG}}
</CODE>"""

    editor = TestEditor()
    lines = content.split('\n')
    
    print("Testing incremental command preview:")
    print("=" * 50)
    
    for i in range(len(lines)):
        print(f"\nLine {i}: {lines[i]}")
        try:
            result = editor.simulate_execution(content, i)
            print(f"Preview ({len(result)} lines):")
            for j, line in enumerate(result):
                print(f"  {j+1}: {line}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_incremental_preview()