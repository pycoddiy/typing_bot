"""
Test utilities and helper functions for typing_bot tests.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple


class SxtTestCase:
    """Represents a structured test case from an .sxt file."""

    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
        self.code_blocks = []
        self.command_blocks = []
        self.expected_results = []
        self._parse_content()

    def _parse_content(self):
        """Parse the .sxt content into structured components."""
        lines = self.content.split("\n")
        current_block_type = None
        current_block_content = []

        for line in lines:
            line = line.strip()
            if line.startswith("<CODE"):
                if current_block_type and current_block_content:
                    self._store_block(current_block_type, current_block_content)
                current_block_type = "CODE"
                current_block_content = []
            elif line.startswith("<COMMANDS>"):
                if current_block_type and current_block_content:
                    self._store_block(current_block_type, current_block_content)
                current_block_type = "COMMANDS"
                current_block_content = []
            elif line.startswith("</CODE>") or line.startswith("</COMMANDS>"):
                if current_block_type and current_block_content:
                    self._store_block(current_block_type, current_block_content)
                current_block_type = None
                current_block_content = []
            elif current_block_type:
                current_block_content.append(line)

        # Handle final block
        if current_block_type and current_block_content:
            self._store_block(current_block_type, current_block_content)

    def _store_block(self, block_type: str, content: List[str]):
        """Store a parsed block."""
        content_str = "\n".join(content)
        if block_type == "CODE":
            self.code_blocks.append(content_str)
        elif block_type == "COMMANDS":
            self.command_blocks.append(content_str)

    def get_initial_code(self) -> str:
        """Get the first code block (initial state)."""
        return self.code_blocks[0] if self.code_blocks else ""

    def get_expected_code(self) -> str:
        """Get the last code block (expected final state)."""
        return self.code_blocks[-1] if len(self.code_blocks) > 1 else ""

    def get_commands(self) -> List[str]:
        """Get all command blocks."""
        return self.command_blocks

    def has_expected_result(self) -> bool:
        """Check if this test case has an expected result."""
        return len(self.code_blocks) > 1


def load_all_sxt_tests(test_dir: Optional[Path] = None) -> List[SxtTestCase]:
    """Load all .sxt test files from the tests directory."""
    if test_dir is None:
        test_dir = Path(__file__).parent

    test_cases = []
    for sxt_file in test_dir.glob("*.sxt"):
        try:
            with open(sxt_file, "r", encoding="utf-8") as f:
                content = f.read()

            test_case = SxtTestCase(sxt_file.stem, content)
            test_cases.append(test_case)
        except Exception as e:
            print(f"Warning: Could not load {sxt_file}: {e}")

    return test_cases


def create_temp_sxt_file(content: str, suffix: str = ".sxt") -> str:
    """Create a temporary .sxt file with given content."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return f.name


def cleanup_temp_file(filepath: str):
    """Clean up a temporary file."""
    try:
        if os.path.exists(filepath):
            os.unlink(filepath)
    except Exception:
        pass  # Ignore cleanup errors


def assert_text_contains(
    actual: str, expected_parts: List[str], case_sensitive: bool = True
):
    """Assert that text contains all expected parts."""
    if not case_sensitive:
        actual = actual.lower()
        expected_parts = [part.lower() for part in expected_parts]

    for part in expected_parts:
        assert part in actual, f"Expected '{part}' not found in: {actual}"


def assert_text_excludes(
    actual: str, excluded_parts: List[str], case_sensitive: bool = True
):
    """Assert that text does not contain any excluded parts."""
    if not case_sensitive:
        actual = actual.lower()
        excluded_parts = [part.lower() for part in excluded_parts]

    for part in excluded_parts:
        assert part not in actual, f"Unexpected '{part}' found in: {actual}"


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    return " ".join(text.split())


def extract_cursor_position(result: List[str]) -> Tuple[int, int]:
    """Extract cursor position from result text (marked with │)."""
    for line_idx, line in enumerate(result):
        cursor_col = line.find("│")
        if cursor_col != -1:
            return line_idx, cursor_col
    return -1, -1


def remove_cursor_indicator(result: List[str]) -> List[str]:
    """Remove cursor indicator from result text."""
    return [line.replace("│", "") for line in result]


class TestResultAnalyzer:
    """Analyze test results and provide assertions."""

    def __init__(self, result: List[str]):
        self.result = result
        self.text = "\n".join(result)
        self.text_no_cursor = "\n".join(remove_cursor_indicator(result))
        self.cursor_line, self.cursor_col = extract_cursor_position(result)

    def assert_contains(self, *expected_parts):
        """Assert result contains all expected parts."""
        assert_text_contains(self.text_no_cursor, list(expected_parts))
        return self

    def assert_excludes(self, *excluded_parts):
        """Assert result excludes all specified parts."""
        assert_text_excludes(self.text_no_cursor, list(excluded_parts))
        return self

    def assert_line_count(self, expected_count: int, tolerance: int = 0):
        """Assert number of lines in result."""
        actual_count = len(self.result)
        assert (
            abs(actual_count - expected_count) <= tolerance
        ), f"Expected {expected_count} lines (±{tolerance}), got {actual_count}"
        return self

    def assert_cursor_at(self, line: int, col: int):
        """Assert cursor is at specific position."""
        assert (
            self.cursor_line == line
        ), f"Expected cursor at line {line}, got {self.cursor_line}"
        assert (
            self.cursor_col == col
        ), f"Expected cursor at column {col}, got {self.cursor_col}"
        return self

    def assert_has_cursor(self):
        """Assert that result has a cursor indicator."""
        assert self.cursor_line != -1, "No cursor indicator found in result"
        return self

    def assert_not_empty(self):
        """Assert that result is not empty."""
        assert len(self.result) > 0, "Result is empty"
        assert len(self.text_no_cursor.strip()) > 0, "Result contains no content"
        return self


def parametrize_sxt_tests(test_dir: Optional[Path] = None):
    """Decorator to parametrize tests with all .sxt test files."""
    test_cases = load_all_sxt_tests(test_dir)

    def decorator(func):
        import pytest

        return pytest.mark.parametrize(
            "sxt_test_case", test_cases, ids=[tc.name for tc in test_cases]
        )(func)

    return decorator
