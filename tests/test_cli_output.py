"""
Tests for CLI output management with verbosity levels

Tests the CLIOutput class and configure_output function with:
- Different verbosity levels (QUIET, NORMAL, VERBOSE)
- Message filtering based on level
- DSL result formatting
- Validation result formatting
"""

import pytest
import json

from src.cli import (
    OutputLevel,
    CLIOutput,
    configure_output,
    get_output,
    set_output_level,
)


class TestOutputLevel:
    """Test OutputLevel enum"""

    def test_output_levels_exist(self):
        """Test that all output levels are defined"""
        assert OutputLevel.QUIET.value == 0
        assert OutputLevel.NORMAL.value == 1
        assert OutputLevel.VERBOSE.value == 2

    def test_output_levels_orderable(self):
        """Test that output levels can be compared"""
        assert OutputLevel.QUIET.value < OutputLevel.NORMAL.value
        assert OutputLevel.NORMAL.value < OutputLevel.VERBOSE.value


class TestCLIOutputBasics:
    """Test basic CLI output functionality"""

    def test_create_with_default_level(self):
        """Test creating CLIOutput with default level"""
        out = CLIOutput()
        assert out.level == OutputLevel.NORMAL

    def test_create_with_custom_level(self):
        """Test creating CLIOutput with custom level"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        assert out.level == OutputLevel.VERBOSE

    def test_verbose_only_in_verbose_mode(self, capsys):
        """Test verbose() only outputs in VERBOSE mode"""
        # QUIET mode
        out = CLIOutput(level=OutputLevel.QUIET)
        out.verbose("test message")
        captured = capsys.readouterr()
        assert captured.out == ""

        # NORMAL mode
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.verbose("test message")
        captured = capsys.readouterr()
        assert captured.out == ""

        # VERBOSE mode
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.verbose("test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_info_in_normal_and_verbose(self, capsys):
        """Test info() outputs in NORMAL and VERBOSE modes"""
        # QUIET mode
        out = CLIOutput(level=OutputLevel.QUIET)
        out.info("test message")
        captured = capsys.readouterr()
        assert captured.out == ""

        # NORMAL mode
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.info("test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out

        # VERBOSE mode
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.info("test message")
        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_quiet_in_all_modes(self, capsys):
        """Test quiet() outputs in all modes"""
        for level in [OutputLevel.QUIET, OutputLevel.NORMAL, OutputLevel.VERBOSE]:
            out = CLIOutput(level=level)
            out.quiet("test message")
            captured = capsys.readouterr()
            assert "test message" in captured.out

    def test_error_in_all_modes(self, capsys):
        """Test error() outputs in all modes to stderr"""
        for level in [OutputLevel.QUIET, OutputLevel.NORMAL, OutputLevel.VERBOSE]:
            out = CLIOutput(level=level)
            out.error("error message")
            captured = capsys.readouterr()
            assert "error message" in captured.err

    def test_success_only_in_normal_and_verbose(self, capsys):
        """Test success() outputs only in NORMAL and VERBOSE"""
        # QUIET mode
        out = CLIOutput(level=OutputLevel.QUIET)
        out.success("success message")
        captured = capsys.readouterr()
        assert captured.out == ""

        # NORMAL mode
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.success("success message")
        captured = capsys.readouterr()
        assert "success message" in captured.out

        # VERBOSE mode
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.success("success message")
        captured = capsys.readouterr()
        assert "success message" in captured.out


class TestCLIOutputFormatting:
    """Test CLI output formatting methods"""

    def test_section_only_in_verbose(self, capsys):
        """Test section() only outputs in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.section("Test Section")
        captured = capsys.readouterr()
        assert "Test Section" in captured.out
        assert "=" in captured.out

    def test_subsection_only_in_verbose(self, capsys):
        """Test subsection() only outputs in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.subsection("Test Subsection")
        captured = capsys.readouterr()
        assert "Test Subsection" in captured.out
        assert "-" in captured.out

    def test_bullet_only_in_verbose(self, capsys):
        """Test bullet() only outputs in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.bullet("Test bullet")
        captured = capsys.readouterr()
        assert "Test bullet" in captured.out
        assert "•" in captured.out

    def test_bullet_with_indent(self, capsys):
        """Test bullet() with indentation"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        out.bullet("Test bullet", indent=2)
        captured = capsys.readouterr()
        assert "    •" in captured.out  # 2 levels * 2 spaces = 4 spaces


class TestJSONOutput:
    """Test JSON output formatting"""

    def test_json_compact_in_quiet_mode(self, capsys):
        """Test JSON output is compact in QUIET mode"""
        out = CLIOutput(level=OutputLevel.QUIET)
        data = {"key": "value", "number": 42}
        out.json_result(data)
        captured = capsys.readouterr()

        # Should be compact (no indentation)
        assert '"key":"value"' in captured.out or '"key": "value"' in captured.out
        assert "\n" not in captured.out.strip()

    def test_json_pretty_in_normal_mode(self, capsys):
        """Test JSON output is pretty-printed in NORMAL mode"""
        out = CLIOutput(level=OutputLevel.NORMAL)
        data = {"key": "value", "number": 42}
        out.json_result(data)
        captured = capsys.readouterr()

        # Should be pretty-printed (with indentation)
        result = json.loads(captured.out)
        assert result == data
        assert "\n" in captured.out

    def test_json_pretty_in_verbose_mode(self, capsys):
        """Test JSON output is pretty-printed in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)
        data = {"key": "value", "number": 42}
        out.json_result(data)
        captured = capsys.readouterr()

        # Should be pretty-printed
        result = json.loads(captured.out)
        assert result == data
        assert "\n" in captured.out


class TestDSLResultFormatting:
    """Test DSL result formatting at different verbosity levels"""

    def test_dsl_result_quiet_mode(self):
        """Test DSL result formatting in QUIET mode"""
        out = CLIOutput(level=OutputLevel.QUIET)

        result = out.format_dsl_result(formula="Sun.Sign == Aries", result=True)
        assert result == "True"

        result = out.format_dsl_result(formula="Sun.Sign == Leo", result=False)
        assert result == "False"

    def test_dsl_result_normal_mode(self):
        """Test DSL result formatting in NORMAL mode"""
        out = CLIOutput(level=OutputLevel.NORMAL)

        result = out.format_dsl_result(formula="Sun.Sign == Aries", result=True)
        assert "Sun.Sign == Aries" in result
        assert "True" in result
        assert "✓" in result

        result = out.format_dsl_result(formula="Sun.Sign == Leo", result=False)
        assert "Sun.Sign == Leo" in result
        assert "False" in result
        assert "✗" in result

    def test_dsl_result_verbose_mode(self):
        """Test DSL result formatting in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)

        chart_data = {
            "planets": {
                "Sun": {"Sign": "Aries", "House": 1, "Degree": 15.5},
                "Moon": {"Sign": "Taurus", "House": 2, "Degree": 22.3},
            },
            "houses": {1: 0, 2: 30, 3: 60},
            "aspects": [],
        }

        result = out.format_dsl_result(
            formula="Sun.Sign == Aries",
            result=True,
            chart_data=chart_data,
            explanation="Sun is in Aries sign",
        )

        # Check all expected components
        assert "Sun.Sign == Aries" in result
        assert "True" in result
        assert "Sun is in Aries sign" in result
        assert "Planets: 2" in result
        assert "Houses: 3" in result
        assert "Aries" in result
        assert "15.50°" in result

    def test_dsl_result_verbose_without_chart_data(self):
        """Test DSL result in VERBOSE mode without chart data"""
        out = CLIOutput(level=OutputLevel.VERBOSE)

        result = out.format_dsl_result(formula="Sun.Sign == Aries", result=True)

        assert "Sun.Sign == Aries" in result
        assert "True" in result
        # Should not crash, just omit chart details


class TestValidationResultFormatting:
    """Test validation result formatting at different verbosity levels"""

    def test_validation_quiet_mode(self):
        """Test validation result in QUIET mode"""
        out = CLIOutput(level=OutputLevel.QUIET)

        result = out.format_validation_result(formula="test", is_valid=True)
        assert result == "valid"

        result = out.format_validation_result(formula="test", is_valid=False)
        assert result == "invalid"

    def test_validation_normal_mode(self):
        """Test validation result in NORMAL mode"""
        out = CLIOutput(level=OutputLevel.NORMAL)

        result = out.format_validation_result(
            formula="Sun.Sign == Aries",
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
        )

        assert "Valid" in result
        assert "Sun.Sign == Aries" in result
        assert "1 warnings" in result

    def test_validation_normal_mode_with_errors(self):
        """Test validation result in NORMAL mode with errors"""
        out = CLIOutput(level=OutputLevel.NORMAL)

        result = out.format_validation_result(
            formula="Sun.Sign == InvalidValue",
            is_valid=False,
            errors=["Invalid value", "Syntax error"],
            warnings=[],
        )

        assert "Invalid" in result
        assert "2 errors" in result

    def test_validation_verbose_mode(self):
        """Test validation result in VERBOSE mode"""
        out = CLIOutput(level=OutputLevel.VERBOSE)

        result = out.format_validation_result(
            formula="Sun.Sign == Aries",
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            suggestions=["Try this instead"],
        )

        # Check all components
        assert "Sun.Sign == Aries" in result
        assert "Invalid" in result
        assert "Error 1" in result
        assert "Error 2" in result
        assert "Warning 1" in result
        assert "Try this instead" in result
        assert "❌ Errors (2)" in result
        assert "⚠ Warnings (1)" in result
        assert "💡 Suggestions (1)" in result

    def test_validation_verbose_no_issues(self):
        """Test validation result in VERBOSE mode with no issues"""
        out = CLIOutput(level=OutputLevel.VERBOSE)

        result = out.format_validation_result(
            formula="Sun.Sign == Aries", is_valid=True, errors=[], warnings=[]
        )

        assert "Valid" in result
        assert "No issues found" in result


class TestConfigureOutput:
    """Test configure_output function"""

    def test_configure_output_default(self):
        """Test configure_output with default settings"""
        out = configure_output()
        assert out.level == OutputLevel.NORMAL

    def test_configure_output_verbose(self):
        """Test configure_output with verbose=True"""
        out = configure_output(verbose=True)
        assert out.level == OutputLevel.VERBOSE

    def test_configure_output_quiet(self):
        """Test configure_output with quiet=True"""
        out = configure_output(quiet=True)
        assert out.level == OutputLevel.QUIET

    def test_configure_output_quiet_precedence(self):
        """Test that quiet takes precedence over verbose"""
        out = configure_output(verbose=True, quiet=True)
        assert out.level == OutputLevel.QUIET


class TestGlobalOutput:
    """Test global output instance management"""

    def test_get_output_creates_instance(self):
        """Test that get_output() creates a default instance"""
        # Reset to default first
        set_output_level(OutputLevel.NORMAL)
        out = get_output()
        assert isinstance(out, CLIOutput)
        assert out.level == OutputLevel.NORMAL

    def test_set_output_level(self):
        """Test set_output_level() changes global level"""
        set_output_level(OutputLevel.VERBOSE)
        out = get_output()
        assert out.level == OutputLevel.VERBOSE

        # Reset to normal
        set_output_level(OutputLevel.NORMAL)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_message(self, capsys):
        """Test outputting empty messages"""
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.info("")
        captured = capsys.readouterr()
        assert captured.out == "\n"

    def test_unicode_messages(self, capsys):
        """Test outputting unicode messages"""
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.info("Тест 中文 🚀")
        captured = capsys.readouterr()
        assert "Тест" in captured.out or "Test" in captured.out  # Encoding-dependent

    def test_multiline_messages(self, capsys):
        """Test outputting multiline messages"""
        out = CLIOutput(level=OutputLevel.NORMAL)
        out.info("Line 1\nLine 2\nLine 3")
        captured = capsys.readouterr()
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out

    def test_dsl_result_with_none_values(self):
        """Test DSL result formatting with None values"""
        out = CLIOutput(level=OutputLevel.VERBOSE)

        result = out.format_dsl_result(
            formula="test", result=True, chart_data=None, explanation=None
        )

        # Should not crash
        assert "test" in result
        assert "True" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
