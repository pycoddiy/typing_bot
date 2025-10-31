"""
Test debugging features and advanced functionality using pytest.
"""

import pytest
from conftest import load_sxt_test_content


class TestDebugging:
    """Test debugging and error handling features."""

    def test_debug_basic(self, mock_editor):
        """Test basic debugging functionality - based on debug_test.sxt"""
        content = load_sxt_test_content("debug_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle debug content
        assert isinstance(result, list)
        assert len(result) > 0

    def test_debug_cursor_position(self, mock_editor):
        """Test cursor position debugging - based on debug_cursor_test.sxt"""
        content = load_sxt_test_content("debug_cursor_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should track cursor position
        assert isinstance(result, list)
        assert len(result) > 0
        # Result should contain cursor indicator
        result_text = "\n".join(result)
        assert "│" in result_text  # Cursor indicator

    def test_clean_debug(self, mock_editor):
        """Test clean debug output - based on clean_debug_test.sxt"""
        content = load_sxt_test_content("clean_debug_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should produce clean output
        assert isinstance(result, list)
        assert len(result) > 0


class TestAdvancedFeatures:
    """Test advanced editor features."""

    def test_highlighting_features(self, mock_editor):
        """Test syntax highlighting - based on test_highlighting.sxt"""
        content = load_sxt_test_content("test_highlighting.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle highlighting content
        assert isinstance(result, list)
        assert len(result) > 0

    def test_redraw_optimization(self, mock_editor):
        """Test redraw optimization - based on test_redraw.sxt"""
        content = load_sxt_test_content("test_redraw.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle redraw operations
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.slow
    def test_shape_bug_handling(self, mock_editor):
        """Test shape bug handling - based on shape_bug_test.sxt"""
        content = load_sxt_test_content("shape_bug_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle shape-related bugs without crashing
        assert isinstance(result, list)
        # Test passes if no exceptions are raised


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_malformed_sxt_content(self, mock_editor):
        """Test handling of malformed .sxt content."""
        content = """<CODE>
    Incomplete content
<COMMANDS>
    INVALID_COMMAND
</INVALID>"""  # Intentionally malformed

        result = mock_editor.simulate_execution(content)

        # Should handle errors gracefully
        assert isinstance(result, list)
        # May contain error message or partial result

    def test_empty_code_block(self, mock_editor):
        """Test handling of empty code blocks."""
        content = """<CODE>
</CODE>

<COMMANDS>
    ARROW_LEFT 1
</COMMANDS>"""

        result = mock_editor.simulate_execution(content)

        # Should handle empty blocks
        assert isinstance(result, list)
        assert len(result) >= 1  # At least cursor line

    def test_no_commands_section(self, mock_editor):
        """Test content with only CODE section."""
        content = """<CODE>
    Just some text content
    No commands following
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should handle content without commands
        assert isinstance(result, list)
        assert len(result) > 0
        result_text = "\n".join(result)
        assert (
            "text content" in result_text or "│" in result_text
        )  # Either content or cursor

    def test_multiple_consecutive_commands(self, mock_editor):
        """Test multiple consecutive command blocks."""
        content = """<CODE>
    Start text
</CODE>

<COMMANDS>
    ARROW_RIGHT 5
</COMMANDS>

<COMMANDS>
    BACKSPACE 2
</COMMANDS>

<CODE>
    End text
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should handle multiple command blocks
        assert isinstance(result, list)
        assert len(result) > 0


class TestPerformance:
    """Test performance-related functionality."""

    @pytest.mark.slow
    def test_large_content_handling(self, mock_editor):
        """Test handling of large content blocks."""
        large_content = "\n".join([f"    Line {i}" for i in range(100)])
        content = f"""<CODE>
{large_content}
</CODE>

<COMMANDS>
    ARROW_UP 50
    ARROW_RIGHT 5
</COMMANDS>"""

        result = mock_editor.simulate_execution(content)

        # Should handle large content efficiently
        assert isinstance(result, list)
        assert len(result) > 0

    def test_many_small_operations(self, mock_editor):
        """Test many small editing operations."""
        commands = []
        for i in range(20):
            commands.extend(["ARROW_RIGHT 1", "BACKSPACE 1"])

        command_str = "\n    ".join(commands)
        content = f"""<CODE>
    {'x' * 50}
</CODE>

<COMMANDS>
    {command_str}
</COMMANDS>"""

        result = mock_editor.simulate_execution(content)

        # Should handle many operations
        assert isinstance(result, list)
        assert len(result) > 0
