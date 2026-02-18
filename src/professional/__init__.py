"""
Professional astrology tools.
Optional advanced features for professional astrologers.

Modules:
- formula_validator: Verify astrological formulas and calculations
- event_finder: Find significant patterns and configurations
"""

from .event_finder import (
    find_conjunctions,
    find_aspect_patterns,
    find_stelliums,
    find_critical_degrees,
)
from .formula_validator import (
    validate_aspect_orbs,
    validate_dignities,
    check_formula_exists,
)

__all__ = [
    "find_conjunctions",
    "find_aspect_patterns",
    "find_stelliums",
    "find_critical_degrees",
    "validate_aspect_orbs",
    "validate_dignities",
    "check_formula_exists",
]
