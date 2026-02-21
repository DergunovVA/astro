"""
CLI output management with verbosity levels

Provides centralized output management for the CLI with support for:
- Verbose mode: Educational output with detailed explanations
- Normal mode: Standard informational output
- Quiet mode: Minimal output (only results and errors)
"""

from enum import Enum
from typing import Optional, Any
import typer


class OutputLevel(Enum):
    """Output verbosity levels"""

    QUIET = 0  # Only results and critical errors
    NORMAL = 1  # Standard informational messages
    VERBOSE = 2  # Detailed explanations and debug info


class CLIOutput:
    """
    Manages CLI output with configurable verbosity levels

    Usage:
        output = CLIOutput(level=OutputLevel.VERBOSE)
        output.verbose("Detailed debug information")
        output.info("Standard message")
        output.quiet("Result: 42")
        output.error("Error occurred")
    """

    def __init__(self, level: OutputLevel = OutputLevel.NORMAL):
        """
        Initialize CLI output manager

        Args:
            level: Output verbosity level (QUIET, NORMAL, VERBOSE)
        """
        self.level = level

    def verbose(self, message: str, **kwargs):
        """Output message only in VERBOSE mode"""
        if self.level == OutputLevel.VERBOSE:
            typer.echo(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Output message in NORMAL and VERBOSE modes"""
        if self.level in (OutputLevel.NORMAL, OutputLevel.VERBOSE):
            typer.echo(message, **kwargs)

    def quiet(self, message: str, **kwargs):
        """Output message in all modes (including QUIET)"""
        typer.echo(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Output error message in all modes"""
        kwargs.setdefault("err", True)
        typer.echo(message, **kwargs)

    def success(self, message: str, **kwargs):
        """Output success message in NORMAL and VERBOSE modes"""
        if self.level in (OutputLevel.NORMAL, OutputLevel.VERBOSE):
            typer.echo(message, **kwargs)

    def section(self, title: str, **kwargs):
        """Output section header in VERBOSE mode"""
        if self.level == OutputLevel.VERBOSE:
            typer.echo(f"\n{'=' * 60}", **kwargs)
            typer.echo(f"{title}", **kwargs)
            typer.echo(f"{'=' * 60}", **kwargs)

    def subsection(self, title: str, **kwargs):
        """Output subsection header in VERBOSE mode"""
        if self.level == OutputLevel.VERBOSE:
            typer.echo(f"\n{title}", **kwargs)
            typer.echo(f"{'-' * len(title)}", **kwargs)

    def bullet(self, message: str, indent: int = 0, **kwargs):
        """Output bulleted item in VERBOSE mode"""
        if self.level == OutputLevel.VERBOSE:
            prefix = "  " * indent + "• "
            typer.echo(f"{prefix}{message}", **kwargs)

    def json_result(self, data: Any, **kwargs):
        """Output JSON result in QUIET mode, formatted in VERBOSE mode"""
        import json

        if self.level == OutputLevel.QUIET:
            # Minimal output: compact JSON
            typer.echo(
                json.dumps(data, ensure_ascii=False, separators=(",", ":")), **kwargs
            )
        else:
            # Normal/Verbose: pretty-printed JSON
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False), **kwargs)

    def format_dsl_result(
        self,
        formula: str,
        result: bool,
        chart_data: Optional[dict] = None,
        explanation: Optional[str] = None,
    ) -> str:
        """
        Format DSL formula evaluation result based on verbosity level

        Args:
            formula: The DSL formula that was evaluated
            result: Boolean result of evaluation
            chart_data: Optional chart data for verbose output
            explanation: Optional explanation for verbose output

        Returns:
            Formatted string for output
        """
        if self.level == OutputLevel.QUIET:
            # Minimal: just True/False
            return str(result)

        elif self.level == OutputLevel.NORMAL:
            # Standard: formula + result
            status = "✓" if result else "✗"
            return f"{status} {formula} → {result}"

        else:  # VERBOSE
            # Detailed: formula + result + explanation + chart details
            lines = []
            lines.append("\n" + "=" * 60)
            lines.append("DSL Formula Evaluation")
            lines.append("=" * 60)
            lines.append(f"\nFormula: {formula}")
            lines.append(f"Result:  {'✓ True' if result else '✗ False'}")

            if explanation:
                lines.append("\nExplanation:")
                lines.append(f"  {explanation}")

            if chart_data:
                lines.append("\nChart Data:")
                lines.append(f"  Planets: {len(chart_data.get('planets', {}))}")
                lines.append(f"  Houses: {len(chart_data.get('houses', {}))}")
                lines.append(f"  Aspects: {len(chart_data.get('aspects', []))}")

                # Show planet positions in verbose mode
                if "planets" in chart_data:
                    lines.append("\n  Planet Positions:")
                    for planet, data in chart_data["planets"].items():
                        sign = data.get("Sign", "?")
                        house = data.get("House", "?")
                        degree = data.get("Degree", 0)
                        lines.append(
                            f"    {planet:10s} → {sign:12s} {degree:6.2f}° (House {house})"
                        )

            lines.append("=" * 60)
            return "\n".join(lines)

    def format_validation_result(
        self,
        formula: str,
        is_valid: bool,
        errors: Optional[list] = None,
        warnings: Optional[list] = None,
        suggestions: Optional[list] = None,
    ) -> str:
        """
        Format DSL formula validation result based on verbosity level

        Args:
            formula: The DSL formula that was validated
            is_valid: Whether the formula is valid
            errors: List of validation errors
            warnings: List of validation warnings
            suggestions: List of suggestions for improvement

        Returns:
            Formatted string for output
        """
        if self.level == OutputLevel.QUIET:
            # Minimal: just valid/invalid
            return "valid" if is_valid else "invalid"

        elif self.level == OutputLevel.NORMAL:
            # Standard: formula + status + error count
            status = "✓ Valid" if is_valid else "✗ Invalid"
            error_count = len(errors) if errors else 0
            warning_count = len(warnings) if warnings else 0

            parts = [f"{status}: {formula}"]
            if error_count > 0:
                parts.append(f" ({error_count} errors)")
            if warning_count > 0:
                parts.append(f" ({warning_count} warnings)")

            return "".join(parts)

        else:  # VERBOSE
            # Detailed: everything
            lines = []
            lines.append("\n" + "=" * 60)
            lines.append("DSL Formula Validation")
            lines.append("=" * 60)
            lines.append(f"\nFormula: {formula}")
            lines.append(f"Status:  {'✓ Valid' if is_valid else '✗ Invalid'}")

            if errors:
                lines.append(f"\n❌ Errors ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    lines.append(f"  {i}. {error}")

            if warnings:
                lines.append(f"\n⚠ Warnings ({len(warnings)}):")
                for i, warning in enumerate(warnings, 1):
                    lines.append(f"  {i}. {warning}")

            if suggestions:
                lines.append(f"\n💡 Suggestions ({len(suggestions)}):")
                for i, suggestion in enumerate(suggestions, 1):
                    lines.append(f"  {i}. {suggestion}")

            if not errors and not warnings:
                lines.append("\n✓ No issues found")

            lines.append("=" * 60)
            return "\n".join(lines)


# Global output instance (can be configured at startup)
_output: Optional[CLIOutput] = None


def get_output() -> CLIOutput:
    """Get global CLI output instance"""
    global _output
    if _output is None:
        _output = CLIOutput()
    return _output


def set_output_level(level: OutputLevel):
    """Set global CLI output level"""
    global _output
    _output = CLIOutput(level)


def configure_output(verbose: bool = False, quiet: bool = False) -> CLIOutput:
    """
    Configure CLI output based on verbosity flags

    Args:
        verbose: Enable verbose output (detailed explanations)
        quiet: Enable quiet output (minimal messages)

    Returns:
        Configured CLIOutput instance

    Note:
        If both verbose and quiet are True, quiet takes precedence
    """
    if quiet:
        level = OutputLevel.QUIET
    elif verbose:
        level = OutputLevel.VERBOSE
    else:
        level = OutputLevel.NORMAL

    set_output_level(level)
    return get_output()
