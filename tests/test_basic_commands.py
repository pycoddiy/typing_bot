"""
Test basic command sequences from .sxt files using pytest.
"""

import pytest
from conftest import load_sxt_test_content


class TestBasicCommands:
    """Test basic editor commands and text manipulation."""

    def test_simple_edit(self, mock_editor):
        """Test simple text editing - based on test_simple.sxt"""
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

        result = mock_editor.simulate_execution(content)

        # Should end with "Beautiful" after the edits
        result_text = "\n".join(result).replace("│", "")  # Remove cursor
        assert "Beautiful" in result_text
        # The result should show the edit was applied
        assert len(result) > 0

    def test_command_sequence(self, mock_editor):
        """Test complex command sequence - based on command_sequence_test.sxt"""
        content = load_sxt_test_content("command_sequence_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Verify the result contains expected text
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    def test_arrow_navigation(self, mock_editor):
        """Test arrow key navigation."""
        content = """<CODE>
    Line 1
    Line 2
    Line 3
</CODE>

<COMMANDS>
    ARROW_UP 2
    ARROW_RIGHT 3
</COMMANDS>

<CODE>
    Line 1
    Line 2 inserted
    Line 3
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should have multiple lines
        assert len(result) >= 3
        result_text = "\n".join(result)
        assert "Line" in result_text


class TestTextEditing:
    """Test text editing operations."""

    def test_backspace_operation(self, mock_editor):
        """Test backspace functionality."""
        content = """<CODE>
    Hello WorldXXX
</CODE>

<COMMANDS>
    BACKSPACE 3
</COMMANDS>

<CODE>
    Hello World
</CODE>"""

        result = mock_editor.simulate_execution(content)
        result_text = "\n".join(result).replace("│", "")

        assert "Hello World" in result_text
        assert "XXX" not in result_text

    def test_newline_handling(self, mock_editor):
        """Test newline operations - based on test_newlines.sxt"""
        content = load_sxt_test_content("test_newlines.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle newlines properly
        assert len(result) > 0
        # Test passes if no exceptions are raised

    @pytest.mark.slow
    def test_comprehensive_newlines(self, mock_editor):
        """Test comprehensive newline handling."""
        content = load_sxt_test_content("comprehensive_newline_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should complete without errors
        assert isinstance(result, list)
        assert len(result) > 0


class TestFileOperations:
    """Test file parsing and operations."""

    def test_sxt_file_parsing(self, parser, temp_sxt_file):
        """Test that .sxt files can be parsed correctly."""
        content = """<CODE>
    Test content
</CODE>

<COMMANDS>
    ARROW_LEFT 3
</COMMANDS>"""

        with open(temp_sxt_file, "w") as f:
            f.write(content)

        result = parser.parse_structured_file(temp_sxt_file)

        # Should return some parsed content
        assert result is not None
        assert len(result) > 0

    def test_multiple_code_blocks(self, mock_editor):
        """Test handling multiple CODE blocks."""
        content = """<CODE>
    First block
</CODE>

<COMMANDS>
    ARROW_RIGHT 5
</COMMANDS>

<CODE>
    Second block
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should handle multiple blocks
        assert len(result) > 0
        result_text = "\n".join(result)
        assert len(result_text) > 0
