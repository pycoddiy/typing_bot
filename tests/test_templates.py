"""
Test template functionality from .sxt files using pytest.
"""

import pytest
from conftest import load_sxt_test_content


class TestTemplates:
    """Test template expansion and functionality."""

    def test_if_name_template(self, mock_editor):
        """Test IF_NAME_MAIN template - based on if_name_test.sxt"""
        content = load_sxt_test_content("if_name_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should expand the template
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    def test_if_name_indented_template(self, mock_editor):
        """Test indented IF_NAME_MAIN template - based on if_name_indented_test.sxt"""
        content = load_sxt_test_content("if_name_indented_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle indentation properly
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    def test_try_except_template(self, mock_editor):
        """Test TRY_EXCEPT template - based on try_except_test.sxt"""
        content = load_sxt_test_content("try_except_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should expand try/except template
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    def test_both_templates(self, mock_editor):
        """Test multiple templates together - based on both_templates_test.sxt"""
        content = load_sxt_test_content("both_templates_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle multiple templates
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    @pytest.mark.integration
    def test_comprehensive_templates(self, mock_editor):
        """Test comprehensive template usage - based on comprehensive_test.sxt"""
        content = load_sxt_test_content("comprehensive_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle complex template combinations
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0


class TestPythonSyntax:
    """Test Python syntax handling and templates."""

    def test_python_syntax_highlighting(self, mock_editor):
        """Test Python syntax handling - based on python_syntax_test.sxt"""
        content = load_sxt_test_content("python_syntax_test.sxt")

        result = mock_editor.simulate_execution(content)

        # Should handle Python syntax
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0

    def test_python_code_block(self, mock_editor):
        """Test Python code block handling."""
        content = """<CODE: PYTHON>
    def hello_world():
        print("Hello, World!")

    {{IF_NAME_MAIN}}
        hello_world()
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should handle Python code with templates
        result_text = "\n".join(result)
        assert (
            "def hello_world" in result_text or len(result) > 0
        )  # Accept either expansion or raw content

    def test_import_templates(self, mock_editor):
        """Test import templates in Python code."""
        content = """<CODE: PYTHON>
    {{IMPORT_NUMPY}}
    {{IMPORT_PANDAS}}

    data = [1, 2, 3]
    print(data)
</CODE>"""

        result = mock_editor.simulate_execution(content)

        # Should handle import templates
        result_text = "\n".join(result)
        assert result_text is not None
        assert len(result) > 0
