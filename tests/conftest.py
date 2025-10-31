"""
Pytest configuration and fixtures for typing_bot tests.
"""

import os

# Add the project root to Python path for imports
import sys
import tempfile
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing_bot.struct_editor import StructEditor
from typing_bot.structured_capture import StructuredParser


@pytest.fixture
def temp_sxt_file():
    """Create a temporary .sxt file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sxt", delete=False, encoding="utf-8"
    ) as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def parser():
    """Provide a StructuredParser instance."""
    return StructuredParser()


@pytest.fixture
def editor():
    """Provide a StructEditor instance."""
    return StructEditor()


@pytest.fixture
def mock_editor():
    """Provide a MockEditor for simulation testing."""
    return MockEditor()


class MockEditor:
    """Mock editor for testing without requiring full curses interface."""

    def __init__(self):
        self.parser = StructuredParser()
        self.text_buffer = [""]
        self.cursor_line = 0
        self.cursor_col = 0

    def reset(self):
        """Reset the editor state."""
        self.text_buffer = [""]
        self.cursor_line = 0
        self.cursor_col = 0

    def load_sxt_file(self, filepath: str):
        """Load and parse an .sxt file."""
        return self.parser.parse_structured_file(filepath)

    def simulate_execution(self, content: str, up_to_line: int = None) -> list:
        """Simulate execution of structured content."""
        try:
            if up_to_line is not None:
                lines_up_to_cursor = content.split("\n")[: up_to_line + 1]
                partial_content = "\n".join(lines_up_to_cursor)
            else:
                partial_content = content

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
        self.reset()

        i = 0
        while i < len(commands):
            char = commands[i]

            # Ensure we have enough lines in buffer
            while len(self.text_buffer) <= self.cursor_line:
                self.text_buffer.append("")

            if char == "\x07":  # Arrow command mode (\a)
                if i + 1 < len(commands):
                    arrow_cmd = commands[i + 1]
                    self._handle_arrow_command(arrow_cmd)
                    i += 2
                    continue
                else:
                    i += 1
                    continue
            elif char == "\n":
                self._handle_newline()
            elif char == "\b":  # Backspace
                self._handle_backspace()
            elif 32 <= ord(char) <= 126:  # Printable characters
                self._insert_char(char)

            i += 1

        # Add cursor indicator
        if self.cursor_line < len(self.text_buffer):
            line = self.text_buffer[self.cursor_line]
            self.text_buffer[self.cursor_line] = (
                line[: self.cursor_col] + "│" + line[self.cursor_col :]
            )
        else:
            self.text_buffer.append("│")

        # Remove empty lines at the end
        while len(self.text_buffer) > 1 and self.text_buffer[-1] == "":
            self.text_buffer.pop()

        return self.text_buffer.copy()

    def _handle_newline(self):
        """Handle newline insertion."""
        current_line = (
            self.text_buffer[self.cursor_line]
            if self.cursor_line < len(self.text_buffer)
            else ""
        )
        before_cursor = current_line[: self.cursor_col]
        after_cursor = current_line[self.cursor_col :]

        self.text_buffer[self.cursor_line] = before_cursor
        self.text_buffer.insert(self.cursor_line + 1, after_cursor)
        self.cursor_line += 1
        self.cursor_col = 0

    def _handle_backspace(self):
        """Handle backspace."""
        if self.cursor_col > 0:
            line = self.text_buffer[self.cursor_line]
            self.text_buffer[self.cursor_line] = (
                line[: self.cursor_col - 1] + line[self.cursor_col :]
            )
            self.cursor_col -= 1
        elif self.cursor_line > 0:
            prev_line = self.text_buffer[self.cursor_line - 1]
            current_line = (
                self.text_buffer[self.cursor_line]
                if self.cursor_line < len(self.text_buffer)
                else ""
            )
            self.text_buffer[self.cursor_line - 1] = prev_line + current_line
            if self.cursor_line < len(self.text_buffer):
                del self.text_buffer[self.cursor_line]
            self.cursor_line -= 1
            self.cursor_col = len(prev_line)

    def _insert_char(self, char):
        """Insert a character at cursor position."""
        line = self.text_buffer[self.cursor_line]
        self.text_buffer[self.cursor_line] = (
            line[: self.cursor_col] + char + line[self.cursor_col :]
        )
        self.cursor_col += 1

    def _handle_arrow_command(self, cmd):
        """Handle arrow key movements."""
        if cmd == "l":  # Left
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = (
                    len(self.text_buffer[self.cursor_line])
                    if self.cursor_line < len(self.text_buffer)
                    else 0
                )
        elif cmd == "r":  # Right
            line_len = (
                len(self.text_buffer[self.cursor_line])
                if self.cursor_line < len(self.text_buffer)
                else 0
            )
            if self.cursor_col < line_len:
                self.cursor_col += 1
            elif self.cursor_line < len(self.text_buffer) - 1:
                self.cursor_line += 1
                self.cursor_col = 0
        elif cmd == "u":  # Up
            if self.cursor_line > 0:
                self.cursor_line -= 1
                line_len = (
                    len(self.text_buffer[self.cursor_line])
                    if self.cursor_line < len(self.text_buffer)
                    else 0
                )
                self.cursor_col = min(self.cursor_col, line_len)
        elif cmd == "d":  # Down
            if self.cursor_line < len(self.text_buffer) - 1:
                self.cursor_line += 1
                line_len = (
                    len(self.text_buffer[self.cursor_line])
                    if self.cursor_line < len(self.text_buffer)
                    else 0
                )
                self.cursor_col = min(self.cursor_col, line_len)


def load_sxt_test_content(filename: str) -> str:
    """Load content from an .sxt test file."""
    test_dir = Path(__file__).parent
    filepath = test_dir / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
