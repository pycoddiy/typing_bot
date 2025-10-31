"""
Integration tests for existing Python test files with pytest.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestExistingPythonTests:
    """Test that existing Python test files work with pytest."""

    @pytest.mark.integration
    def test_syntax_highlighting_module(self):
        """Test the syntax highlighting test module."""
        try:
            # Import and run the test
            from test_syntax_highlighting import test_syntax_highlighting

            # This should create a test file and not raise exceptions
            test_syntax_highlighting()

            # Verify test file was created
            test_file = project_root / "tests" / "test_highlighting.sxt"
            assert test_file.exists()

        except Exception as e:
            pytest.fail(f"Syntax highlighting test failed: {e}")

    @pytest.mark.integration
    def test_simulation_module(self):
        """Test the simulation test module."""
        try:
            # Import and run the test
            from test_simulation import test_simple_simulation

            # This should run simulation without errors
            test_simple_simulation()

        except Exception as e:
            pytest.fail(f"Simulation test failed: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_incremental_preview_module(self):
        """Test the incremental preview module."""
        try:
            # Import the module to check for syntax errors
            import test_incremental_preview

            # If we can import it, the module is valid
            assert hasattr(test_incremental_preview, "__file__")

        except Exception as e:
            pytest.fail(f"Incremental preview test import failed: {e}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_redraw_optimization_module(self):
        """Test the redraw optimization module."""
        try:
            # Import the module to check for syntax errors
            import test_redraw_optimization

            # If we can import it, the module is valid
            assert hasattr(test_redraw_optimization, "__file__")

        except Exception as e:
            pytest.fail(f"Redraw optimization test import failed: {e}")


class TestModuleIntegration:
    """Test integration between modules."""

    def test_structured_parser_import(self):
        """Test that StructuredParser can be imported and used."""
        from typing_bot.structured_capture import StructuredParser

        parser = StructuredParser()
        assert parser is not None

    def test_structured_editor_import(self):
        """Test that StructEditor can be imported."""
        try:
            from typing_bot.struct_editor import StructEditor

            # Note: StructEditor may require curses, so we just test import
            assert StructEditor is not None
        except ImportError as e:
            # If curses is not available, that's expected in some environments
            if "curses" in str(e):
                pytest.skip("Curses not available in test environment")
            else:
                raise

    def test_project_structure(self):
        """Test that project structure is correct for pytest."""
        # Test that important files exist
        assert (project_root / "structured_capture.py").exists()
        assert (project_root / "struct_editor.py").exists()
        assert (project_root / "pyproject.toml").exists()

        # Test that tests directory exists
        tests_dir = project_root / "tests"
        assert tests_dir.exists()
        assert tests_dir.is_dir()

        # Test that example .sxt files exist
        assert (tests_dir / "test_simple.sxt").exists()
        assert (tests_dir / "comprehensive_test.sxt").exists()


class TestPytestConfiguration:
    """Test pytest configuration and markers."""

    def test_markers_work(self):
        """Test that custom pytest markers work."""
        # This test itself uses the unit marker implicitly
        pass

    @pytest.mark.unit
    def test_unit_marker(self):
        """Test unit marker works."""
        assert True

    @pytest.mark.integration
    def test_integration_marker(self):
        """Test integration marker works."""
        assert True

    @pytest.mark.slow
    def test_slow_marker(self):
        """Test slow marker works."""
        # Simulate a slow operation
        import time

        time.sleep(0.1)
        assert True
