"""
Parametrized tests that automatically test all .sxt files.
"""

import pytest
from test_utils import SxtTestCase, TestResultAnalyzer, parametrize_sxt_tests


class TestAllSxtFiles:
    """Automatically test all .sxt files in the tests directory."""

    @parametrize_sxt_tests()
    def test_sxt_file_parsing(self, sxt_test_case: SxtTestCase, parser):
        """Test that each .sxt file can be parsed without errors."""
        # This test verifies that the .sxt format is valid
        assert sxt_test_case.content is not None
        assert len(sxt_test_case.content) > 0

        # Should have at least one code block
        assert (
            len(sxt_test_case.code_blocks) > 0
        ), f"No code blocks found in {sxt_test_case.name}"

    @parametrize_sxt_tests()
    def test_sxt_file_execution(self, sxt_test_case: SxtTestCase, mock_editor):
        """Test that each .sxt file can be executed without crashing."""
        try:
            result = mock_editor.simulate_execution(sxt_test_case.content)

            # Basic validation - should produce some result
            analyzer = TestResultAnalyzer(result)
            analyzer.assert_not_empty()

        except Exception as e:
            pytest.fail(f"Execution failed for {sxt_test_case.name}: {e}")

    @parametrize_sxt_tests()
    def test_sxt_file_expected_results(self, sxt_test_case: SxtTestCase, mock_editor):
        """Test .sxt files that have expected results."""
        if not sxt_test_case.has_expected_result():
            pytest.skip(f"{sxt_test_case.name} has no expected result block")

        try:
            result = mock_editor.simulate_execution(sxt_test_case.content)
            expected = sxt_test_case.get_expected_code()

            # Basic check - result should be reasonable
            analyzer = TestResultAnalyzer(result)
            analyzer.assert_not_empty()

            # If expected result is provided, do some basic validation
            if expected.strip():
                # At minimum, check that we got some text output
                assert len(analyzer.text_no_cursor.strip()) > 0

        except Exception as e:
            pytest.fail(f"Expected result test failed for {sxt_test_case.name}: {e}")


class TestSxtFileCategories:
    """Test .sxt files grouped by categories."""

    def test_template_files(self, mock_editor):
        """Test files that contain templates."""
        template_files = [
            "if_name_test.sxt",
            "if_name_indented_test.sxt",
            "try_except_test.sxt",
            "both_templates_test.sxt",
            "comprehensive_test.sxt",
        ]

        for filename in template_files:
            try:
                from conftest import load_sxt_test_content

                content = load_sxt_test_content(filename)
                result = mock_editor.simulate_execution(content)

                analyzer = TestResultAnalyzer(result)
                analyzer.assert_not_empty()

            except FileNotFoundError:
                pytest.skip(f"Template file {filename} not found")
            except Exception as e:
                pytest.fail(f"Template test failed for {filename}: {e}")

    def test_command_files(self, mock_editor):
        """Test files that focus on command sequences."""
        command_files = [
            "test_simple.sxt",
            "command_sequence_test.sxt",
            "test_newlines.sxt",
        ]

        for filename in command_files:
            try:
                from conftest import load_sxt_test_content

                content = load_sxt_test_content(filename)
                result = mock_editor.simulate_execution(content)

                analyzer = TestResultAnalyzer(result)
                analyzer.assert_not_empty()
                analyzer.assert_has_cursor()

            except FileNotFoundError:
                pytest.skip(f"Command file {filename} not found")
            except Exception as e:
                pytest.fail(f"Command test failed for {filename}: {e}")

    def test_debug_files(self, mock_editor):
        """Test files that test debugging features."""
        debug_files = [
            "debug_test.sxt",
            "debug_cursor_test.sxt",
            "clean_debug_test.sxt",
        ]

        for filename in debug_files:
            try:
                from conftest import load_sxt_test_content

                content = load_sxt_test_content(filename)
                result = mock_editor.simulate_execution(content)

                analyzer = TestResultAnalyzer(result)
                analyzer.assert_not_empty()

            except FileNotFoundError:
                pytest.skip(f"Debug file {filename} not found")
            except Exception as e:
                pytest.fail(f"Debug test failed for {filename}: {e}")


class TestSxtValidation:
    """Test validation of .sxt file format and content."""

    def test_valid_sxt_structure(self):
        """Test that .sxt files have valid structure."""
        from test_utils import load_all_sxt_tests

        test_cases = load_all_sxt_tests()

        for test_case in test_cases:
            # Should have content
            assert test_case.content, f"{test_case.name} has no content"

            # Should have at least one code block
            assert (
                len(test_case.code_blocks) > 0
            ), f"{test_case.name} has no code blocks"

            # If it has commands, they should be valid
            for cmd_block in test_case.command_blocks:
                assert isinstance(
                    cmd_block, str
                ), f"Invalid command block in {test_case.name}"

    def test_sxt_file_completeness(self):
        """Test that important .sxt test files exist."""
        from pathlib import Path

        required_files = [
            "test_simple.sxt",
            "comprehensive_test.sxt",
            "if_name_test.sxt",
        ]

        test_dir = Path(__file__).parent

        for filename in required_files:
            filepath = test_dir / filename
            assert filepath.exists(), f"Required test file {filename} is missing"

            # Should have content
            with open(filepath, "r") as f:
                content = f.read()
            assert len(content.strip()) > 0, f"Test file {filename} is empty"
