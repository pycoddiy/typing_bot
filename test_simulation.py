#!/usr/bin/env python3
"""
Test the simulation with a simple example.
"""

import os
import tempfile

from typing_bot.struct_editor import StructEditor
from typing_bot.structured_capture import StructuredParser


def test_simple_simulation():
    content = """<CODE>
    Hello World
</CODE>

<COMMANDS>
    ARROW_LEFT 5
    BACKSPACE 5
</COMMANDS>

<CODE>
    Beautiful
</CODE>"""

    parser = StructuredParser()
    editor = MockEditor()

    print("=== Simple Simulation Test ===\n")
    print("Content:")
    print(content)
    print("\n" + "=" * 50)

    # Test simulation at different lines
    lines = content.split("\n")
    for i in range(len(lines)):
        result = editor.simulate_execution(content, i)
        print(f"\nLine {i+1}: {lines[i][:50]}...")
        print("Result:", " ".join(result).replace("\n", "\\n"))


class MockEditor:
    def __init__(self):
        self.parser = StructuredParser()

    def simulate_execution(self, content: str, up_to_line: int) -> list:
        """Mock version of the simulation for testing."""
        try:
            lines_up_to_cursor = content.split("\n")[: up_to_line + 1]
            partial_content = "\n".join(lines_up_to_cursor)

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sxt", delete=False, encoding="utf-8"
            ) as f:
                f.write(partial_content)
                temp_filename = f.name

            try:
                converted = self.parser.parse_structured_file(temp_filename)
                result_lines = self._simulate_typing_result(converted)
                return result_lines
            finally:
                os.unlink(temp_filename)

        except Exception as e:
            return [f"Simulation Error: {e}"]

    def _simulate_typing_result(self, commands: str) -> list:
        """Simulate what text would appear after executing the typing commands."""
        text_buffer = [""]
        cursor_line = 0
        cursor_col = 0

        i = 0
        while i < len(commands):
            char = commands[i]

            while len(text_buffer) <= cursor_line:
                text_buffer.append("")

            if char == "\x07":  # Arrow command mode (\a)
                if i + 1 < len(commands):
                    arrow_cmd = commands[i + 1]
                    cursor_line, cursor_col = self._handle_arrow_command(
                        arrow_cmd, text_buffer, cursor_line, cursor_col
                    )
                    i += 2
                    continue
                else:
                    i += 1
                    continue
            elif char == "\n":
                current_line = (
                    text_buffer[cursor_line] if cursor_line < len(text_buffer) else ""
                )
                before_cursor = current_line[:cursor_col]
                after_cursor = current_line[cursor_col:]

                text_buffer[cursor_line] = before_cursor
                text_buffer.insert(cursor_line + 1, after_cursor)
                cursor_line += 1
                cursor_col = 0
            elif char == "\b":  # Backspace
                if cursor_col > 0:
                    line = text_buffer[cursor_line]
                    text_buffer[cursor_line] = (
                        line[: cursor_col - 1] + line[cursor_col:]
                    )
                    cursor_col -= 1
                elif cursor_line > 0:
                    prev_line = text_buffer[cursor_line - 1]
                    current_line = (
                        text_buffer[cursor_line]
                        if cursor_line < len(text_buffer)
                        else ""
                    )
                    text_buffer[cursor_line - 1] = prev_line + current_line
                    if cursor_line < len(text_buffer):
                        del text_buffer[cursor_line]
                    cursor_line -= 1
                    cursor_col = len(prev_line)
            elif 32 <= ord(char) <= 126:  # Printable characters
                line = text_buffer[cursor_line]
                text_buffer[cursor_line] = line[:cursor_col] + char + line[cursor_col:]
                cursor_col += 1

            i += 1

        # Add cursor indicator
        if cursor_line < len(text_buffer):
            line = text_buffer[cursor_line]
            text_buffer[cursor_line] = line[:cursor_col] + "│" + line[cursor_col:]
        else:
            text_buffer.append("│")

        # Remove empty lines at the end
        while len(text_buffer) > 1 and text_buffer[-1] == "":
            text_buffer.pop()

        return text_buffer

    def _handle_arrow_command(self, cmd, text_buffer, cursor_line, cursor_col):
        """Handle arrow key movements."""
        if cmd == "l":  # Left
            if cursor_col > 0:
                cursor_col -= 1
            elif cursor_line > 0:
                cursor_line -= 1
                cursor_col = (
                    len(text_buffer[cursor_line])
                    if cursor_line < len(text_buffer)
                    else 0
                )
        elif cmd == "r":  # Right
            line_len = (
                len(text_buffer[cursor_line]) if cursor_line < len(text_buffer) else 0
            )
            if cursor_col < line_len:
                cursor_col += 1
            elif cursor_line < len(text_buffer) - 1:
                cursor_line += 1
                cursor_col = 0
        elif cmd == "u":  # Up
            if cursor_line > 0:
                cursor_line -= 1
                line_len = (
                    len(text_buffer[cursor_line])
                    if cursor_line < len(text_buffer)
                    else 0
                )
                cursor_col = min(cursor_col, line_len)
        elif cmd == "d":  # Down
            if cursor_line < len(text_buffer) - 1:
                cursor_line += 1
                line_len = (
                    len(text_buffer[cursor_line])
                    if cursor_line < len(text_buffer)
                    else 0
                )
                cursor_col = min(cursor_col, line_len)

        return cursor_line, cursor_col


if __name__ == "__main__":
    test_simple_simulation()
