"""
CLI utilities and output management

This module provides:
- Output verbosity management (verbose, normal, quiet)
- Formatted output for DSL results
- Validation result formatting
"""

from src.cli.output import (
    OutputLevel,
    CLIOutput,
    configure_output,
    get_output,
    set_output_level,
)

__all__ = [
    "OutputLevel",
    "CLIOutput",
    "configure_output",
    "get_output",
    "set_output_level",
]
