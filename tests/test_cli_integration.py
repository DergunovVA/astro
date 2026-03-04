"""
Integration tests for CLI verbose/quiet modes with natal command

Tests the --verbose and --quiet flags in the actual CLI commands
"""

import sys
import pytest
import subprocess
import json
from pathlib import Path


# Skip these tests if main.py cannot be run
try:
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        timeout=15,
        cwd=Path(__file__).parent.parent,
    )
    MAIN_AVAILABLE = result.returncode == 0
except Exception:
    MAIN_AVAILABLE = False

pytestmark = pytest.mark.skipif(not MAIN_AVAILABLE, reason="main.py not available")


class TestNatalCommandVerboseQuiet:
    """Test natal command with --verbose and --quiet flags"""

    @pytest.fixture
    def base_command(self):
        """Base natal command with minimal working parameters"""
        return [
            sys.executable,
            "main.py",
            "natal",
            "2000-01-01",
            "12:00",
            "London",
        ]

    def test_natal_default_output(self, base_command):
        """Test natal command with default output level (NORMAL)"""
        result = subprocess.run(
            base_command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should output JSON
        output = json.loads(result.stdout)
        assert "input_metadata" in output
        assert "facts" in output

    def test_natal_quiet_mode(self, base_command):
        """Test natal command with --quiet flag"""
        cmd = base_command + ["--quiet"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should output compact JSON (no indentation)
        output = json.loads(result.stdout)
        assert "input_metadata" in output
        # Compact JSON has no newlines except at end
        assert result.stdout.count("\n") <= 2

    def test_natal_verbose_mode(self, base_command):
        """Test natal command with --verbose flag"""
        cmd = base_command + ["--verbose"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Verbose mode prepends text logs to stdout, extract JSON part
        lines = result.stdout.split("\n")
        json_start = next(i for i, line in enumerate(lines) if line.startswith("{"))
        output = json.loads("\n".join(lines[json_start:]))
        assert "input_metadata" in output
        # Full stdout has many newlines (text + JSON)
        assert result.stdout.count("\n") > 10

    def test_natal_quiet_precedence(self, base_command):
        """Test that --quiet takes precedence over --verbose"""
        cmd = base_command + ["--verbose", "--quiet"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should be quiet (compact JSON)
        assert result.stdout.count("\n") <= 2


class TestDSLCheckWithVerboseQuiet:
    """Test DSL --check flag with different verbosity levels"""

    @pytest.fixture
    def dsl_command_base(self):
        """Base command for DSL formula checking"""
        return [
            sys.executable,
            "main.py",
            "natal",
            "1982-01-08",
            "12:00",
            "Tel Aviv",
            "--check=Sun.Sign == Capricorn",
        ]

    def test_dsl_check_normal_mode(self, dsl_command_base):
        """Test DSL check with normal output"""
        result = subprocess.run(
            dsl_command_base,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should show formula and result
        assert "Sun.Sign == Capricorn" in result.stdout
        assert "→" in result.stdout or "True" in result.stdout

    def test_dsl_check_quiet_mode(self, dsl_command_base):
        """Test DSL check with --quiet"""
        cmd = dsl_command_base + ["--quiet"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should output minimal result (just True/False)
        output = result.stdout.strip()
        assert output == "True" or "True" in output

    def test_dsl_check_verbose_mode(self, dsl_command_base):
        """Test DSL check with --verbose"""
        cmd = dsl_command_base + ["--verbose"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should show detailed output
        output = result.stdout
        assert "Sun.Sign == Capricorn" in output
        assert "DSL Formula Evaluation" in output or "Step 1" in output
        # Should have verbose steps
        assert "Step" in output or "Planet Positions" in output

    def test_dsl_check_false_result_quiet(self):
        """Test DSL check with formula that evaluates to False in quiet mode"""
        cmd = [
            sys.executable,
            "main.py",
            "natal",
            "1982-01-08",
            "12:00",
            "Tel Aviv",
            "--check=Sun.Sign == Aries",  # False for this date
            "--quiet",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should output False
        output = result.stdout.strip()
        assert output == "False" or "False" in output


class TestErrorOutputWithVerboseQuiet:
    """Test error output at different verbosity levels"""

    def test_error_output_quiet_mode(self):
        """Test error output in quiet mode"""
        cmd = [
            sys.executable,
            "main.py",
            "natal",
            "invalid",
            "12:00",
            "London",
            "--quiet",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should fail
        assert result.returncode != 0
        # Should output error to stderr
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_error_output_verbose_mode(self):
        """Test error output in verbose mode (may include traceback)"""
        cmd = [
            sys.executable,
            "main.py",
            "natal",
            "invalid",
            "12:00",
            "London",
            "--verbose",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should fail
        assert result.returncode != 0
        # Should output error
        assert "Error" in result.stderr or "error" in result.stderr.lower()


class TestFormatOutputWithVerboseQuiet:
    """Test different output formats with verbosity levels"""

    @pytest.fixture
    def format_command_base(self):
        """Base command for format testing"""
        return [
            sys.executable,
            "main.py",
            "natal",
            "2000-01-01",
            "12:00",
            "London",
        ]

    def test_json_format_quiet(self, format_command_base):
        """Test JSON format with --quiet"""
        cmd = format_command_base + ["--format=json", "--quiet"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Should be compact JSON
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_json_format_verbose(self, format_command_base):
        """Test JSON format with --verbose"""
        cmd = format_command_base + ["--format=json", "--verbose"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            cwd=Path(__file__).parent.parent,
        )

        # Should succeed
        assert result.returncode == 0
        # Verbose mode prepends text logs to stdout, extract JSON part
        lines = result.stdout.split("\n")
        json_start = next(i for i, line in enumerate(lines) if line.startswith("{"))
        data = json.loads("\n".join(lines[json_start:]))
        assert isinstance(data, dict)
        # Full stdout has indented JSON and verbose text
        assert "  " in result.stdout  # Check for indentation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
