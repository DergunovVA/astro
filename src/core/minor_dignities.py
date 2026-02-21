"""
Minor Essential Dignities for Traditional Astrology.

Implements the three lesser dignities:
1. Triplicities (elemental rulers by day/night)
2. Egyptian Terms (degree boundaries with planetary rulers)
3. Faces/Decans (10-degree divisions using Chaldean order)

Based on classical sources:
- William Lilly's "Christian Astrology" (1647)
- Ptolemy's "Tetrabiblos"
- Dorotheus of Sidon
"""

from typing import Dict, List, Optional, Tuple


# ============================================================================
# TRIPLICITIES - Elemental Rulers (Day/Night/Participating)
# ============================================================================
# Each element has three rulers based on time of day and participation
# Day ruler: used when Sun is above horizon
# Night ruler: used when Sun is below horizon
# Participating ruler: used in both day and night (lesser dignity)

TRIPLICITIES = {
    "Fire": {  # Aries, Leo, Sagittarius
        "signs": ["Aries", "Leo", "Sagittarius"],
        "day_ruler": "Sun",
        "night_ruler": "Jupiter",
        "participating": "Saturn",
    },
    "Earth": {  # Taurus, Virgo, Capricorn
        "signs": ["Taurus", "Virgo", "Capricorn"],
        "day_ruler": "Venus",
        "night_ruler": "Moon",
        "participating": "Mars",
    },
    "Air": {  # Gemini, Libra, Aquarius
        "signs": ["Gemini", "Libra", "Aquarius"],
        "day_ruler": "Saturn",
        "night_ruler": "Mercury",
        "participating": "Jupiter",
    },
    "Water": {  # Cancer, Scorpio, Pisces
        "signs": ["Cancer", "Scorpio", "Pisces"],
        "day_ruler": "Venus",
        "night_ruler": "Mars",
        "participating": "Moon",
    },
}


def get_triplicity_rulers(sign: str) -> Optional[Dict[str, str]]:
    """
    Get triplicity rulers for a zodiac sign.

    Args:
        sign: Zodiac sign name (e.g., "Aries", "Taurus")

    Returns:
        Dictionary with day_ruler, night_ruler, participating or None if invalid sign

    Example:
        >>> get_triplicity_rulers("Aries")
        {'day_ruler': 'Sun', 'night_ruler': 'Jupiter', 'participating': 'Saturn'}
    """
    for element, data in TRIPLICITIES.items():
        if sign in data["signs"]:
            return {
                "element": element,
                "day_ruler": data["day_ruler"],
                "night_ruler": data["night_ruler"],
                "participating": data["participating"],
            }
    return None


def get_triplicity_ruler(sign: str, is_day_chart: bool) -> Optional[str]:
    """
    Get the primary triplicity ruler for a sign based on day/night chart.

    Args:
        sign: Zodiac sign name
        is_day_chart: True if Sun is above horizon (day chart), False if below (night)

    Returns:
        Planet name of the triplicity ruler, or None if invalid sign

    Example:
        >>> get_triplicity_ruler("Leo", is_day_chart=True)
        'Sun'
        >>> get_triplicity_ruler("Leo", is_day_chart=False)
        'Jupiter'
    """
    rulers = get_triplicity_rulers(sign)
    if not rulers:
        return None

    return rulers["day_ruler"] if is_day_chart else rulers["night_ruler"]


# ============================================================================
# EGYPTIAN TERMS (Bounds) - Degree Boundaries
# ============================================================================
# Each sign divided into 5 unequal segments, each ruled by a planet
# Format: (start_degree, end_degree, planet)
# Ptolemaic terms (most commonly used)

EGYPTIAN_TERMS = {
    "Aries": [
        (0, 6, "Jupiter"),
        (6, 14, "Venus"),
        (14, 21, "Mercury"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Taurus": [
        (0, 8, "Venus"),
        (8, 15, "Mercury"),
        (15, 22, "Jupiter"),
        (22, 26, "Saturn"),
        (26, 30, "Mars"),
    ],
    "Gemini": [
        (0, 7, "Mercury"),
        (7, 14, "Jupiter"),
        (14, 21, "Venus"),
        (21, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
    "Cancer": [
        (0, 7, "Mars"),
        (7, 13, "Venus"),
        (13, 19, "Mercury"),
        (19, 26, "Jupiter"),
        (26, 30, "Saturn"),
    ],
    "Leo": [
        (0, 6, "Jupiter"),
        (6, 13, "Venus"),
        (13, 19, "Mercury"),
        (19, 25, "Saturn"),
        (25, 30, "Mars"),
    ],
    "Virgo": [
        (0, 7, "Mercury"),
        (7, 13, "Venus"),
        (13, 18, "Jupiter"),
        (18, 24, "Mars"),
        (24, 30, "Saturn"),
    ],
    "Libra": [
        (0, 6, "Saturn"),
        (6, 11, "Venus"),
        (11, 19, "Jupiter"),
        (19, 24, "Mercury"),
        (24, 30, "Mars"),
    ],
    "Scorpio": [
        (0, 6, "Mars"),
        (6, 14, "Venus"),
        (14, 21, "Mercury"),
        (21, 27, "Jupiter"),
        (27, 30, "Saturn"),
    ],
    "Sagittarius": [
        (0, 8, "Jupiter"),
        (8, 14, "Venus"),
        (14, 19, "Mercury"),
        (19, 25, "Saturn"),
        (25, 30, "Mars"),
    ],
    "Capricorn": [
        (0, 6, "Venus"),
        (6, 12, "Mercury"),
        (12, 19, "Jupiter"),
        (19, 25, "Mars"),
        (25, 30, "Saturn"),
    ],
    "Aquarius": [
        (0, 6, "Saturn"),
        (6, 12, "Mercury"),
        (12, 20, "Venus"),
        (20, 25, "Jupiter"),
        (25, 30, "Mars"),
    ],
    "Pisces": [
        (0, 8, "Venus"),
        (8, 14, "Jupiter"),
        (14, 20, "Mercury"),
        (20, 26, "Mars"),
        (26, 30, "Saturn"),
    ],
}


def get_term_ruler(sign: str, degree: float) -> Optional[str]:
    """
    Get the term (bounds) ruler for a specific degree in a sign.

    Args:
        sign: Zodiac sign name
        degree: Degree within sign (0.0 to 29.999...)

    Returns:
        Planet name ruling that term, or None if invalid

    Example:
        >>> get_term_ruler("Aries", 10.5)
        'Venus'  # Venus rules 6-14 degrees of Aries
    """
    if sign not in EGYPTIAN_TERMS:
        return None

    # Normalize degree to 0-30 range
    degree = degree % 30

    for start, end, planet in EGYPTIAN_TERMS[sign]:
        if start <= degree < end:
            return planet

    return None


def get_all_terms(sign: str) -> Optional[List[Tuple[float, float, str]]]:
    """
    Get all term boundaries for a sign.

    Args:
        sign: Zodiac sign name

    Returns:
        List of (start_degree, end_degree, planet) tuples, or None if invalid

    Example:
        >>> get_all_terms("Aries")
        [(0, 6, 'Jupiter'), (6, 14, 'Venus'), (14, 21, 'Mercury'), ...]
    """
    return EGYPTIAN_TERMS.get(sign)


# ============================================================================
# FACES/DECANS - 10-Degree Divisions (Chaldean Order)
# ============================================================================
# Each sign divided into 3 decans of 10 degrees each
# Uses Chaldean order: Mars, Sun, Venus, Mercury, Moon, Saturn, Jupiter
# Starting from Aries and cycling through

# Chaldean planetary order (from slowest to fastest in ancient astronomy)
CHALDEAN_ORDER = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]

# Decans start with Mars for Aries 0-10, then cycle through Chaldean order
DECANS = {
    "Aries": [
        (0, 10, "Mars"),    # 1st decan
        (10, 20, "Sun"),    # 2nd decan
        (20, 30, "Venus"),  # 3rd decan
    ],
    "Taurus": [
        (0, 10, "Mercury"),
        (10, 20, "Moon"),
        (20, 30, "Saturn"),
    ],
    "Gemini": [
        (0, 10, "Jupiter"),
        (10, 20, "Mars"),
        (20, 30, "Sun"),
    ],
    "Cancer": [
        (0, 10, "Venus"),
        (10, 20, "Mercury"),
        (20, 30, "Moon"),
    ],
    "Leo": [
        (0, 10, "Saturn"),
        (10, 20, "Jupiter"),
        (20, 30, "Mars"),
    ],
    "Virgo": [
        (0, 10, "Sun"),
        (10, 20, "Venus"),
        (20, 30, "Mercury"),
    ],
    "Libra": [
        (0, 10, "Moon"),
        (10, 20, "Saturn"),
        (20, 30, "Jupiter"),
    ],
    "Scorpio": [
        (0, 10, "Mars"),
        (10, 20, "Sun"),
        (20, 30, "Venus"),
    ],
    "Sagittarius": [
        (0, 10, "Mercury"),
        (10, 20, "Moon"),
        (20, 30, "Saturn"),
    ],
    "Capricorn": [
        (0, 10, "Jupiter"),
        (10, 20, "Mars"),
        (20, 30, "Sun"),
    ],
    "Aquarius": [
        (0, 10, "Venus"),
        (10, 20, "Mercury"),
        (20, 30, "Moon"),
    ],
    "Pisces": [
        (0, 10, "Saturn"),
        (10, 20, "Jupiter"),
        (20, 30, "Mars"),
    ],
}


def get_decan_ruler(sign: str, degree: float) -> Optional[str]:
    """
    Get the decan (face) ruler for a specific degree in a sign.

    Args:
        sign: Zodiac sign name
        degree: Degree within sign (0.0 to 29.999...)

    Returns:
        Planet name ruling that decan, or None if invalid

    Example:
        >>> get_decan_ruler("Aries", 5.5)
        'Mars'  # Mars rules 0-10 degrees of Aries
        >>> get_decan_ruler("Aries", 15.0)
        'Sun'   # Sun rules 10-20 degrees of Aries
    """
    if sign not in DECANS:
        return None

    # Normalize degree to 0-30 range
    degree = degree % 30

    for start, end, planet in DECANS[sign]:
        if start <= degree < end:
            return planet

    return None


def get_all_decans(sign: str) -> Optional[List[Tuple[float, float, str]]]:
    """
    Get all decan boundaries for a sign.

    Args:
        sign: Zodiac sign name

    Returns:
        List of (start_degree, end_degree, planet) tuples, or None if invalid

    Example:
        >>> get_all_decans("Aries")
        [(0, 10, 'Mars'), (10, 20, 'Sun'), (20, 30, 'Venus')]
    """
    return DECANS.get(sign)


# ============================================================================
# MINOR DIGNITY SCORING
# ============================================================================
# Traditional scoring:
# - Triplicity: +3 points (day/night ruler), +1 point (participating)
# - Term: +2 points
# - Face/Decan: +1 point

def calculate_minor_dignities(
    planet: str, sign: str, degree: float, is_day_chart: bool
) -> Dict[str, any]:
    """
    Calculate all minor dignities for a planet at a specific position.

    Args:
        planet: Planet name (e.g., "Mars", "Venus")
        sign: Zodiac sign name
        degree: Degree within sign (0.0 to 29.999...)
        is_day_chart: True if Sun above horizon (day), False if below (night)

    Returns:
        Dictionary with minor dignity details and total score

    Example:
        >>> calculate_minor_dignities("Sun", "Aries", 5.0, True)
        {
            'triplicity': {'has': True, 'type': 'day_ruler', 'score': 3},
            'term': {'has': False, 'ruler': 'Jupiter', 'score': 0},
            'decan': {'has': False, 'ruler': 'Mars', 'score': 0},
            'total_score': 3
        }
    """
    result = {
        "triplicity": {"has": False, "type": None, "score": 0},
        "term": {"has": False, "ruler": None, "score": 0},
        "decan": {"has": False, "ruler": None, "score": 0},
        "total_score": 0,
    }

    # Check triplicity
    triplicity_rulers = get_triplicity_rulers(sign)
    if triplicity_rulers:
        if planet == triplicity_rulers["day_ruler"] and is_day_chart:
            result["triplicity"] = {"has": True, "type": "day_ruler", "score": 3}
        elif planet == triplicity_rulers["night_ruler"] and not is_day_chart:
            result["triplicity"] = {"has": True, "type": "night_ruler", "score": 3}
        elif planet == triplicity_rulers["participating"]:
            result["triplicity"] = {
                "has": True,
                "type": "participating",
                "score": 1,
            }

    # Check term
    term_ruler = get_term_ruler(sign, degree)
    result["term"]["ruler"] = term_ruler
    if term_ruler == planet:
        result["term"]["has"] = True
        result["term"]["score"] = 2

    # Check decan
    decan_ruler = get_decan_ruler(sign, degree)
    result["decan"]["ruler"] = decan_ruler
    if decan_ruler == planet:
        result["decan"]["has"] = True
        result["decan"]["score"] = 1

    # Calculate total
    result["total_score"] = (
        result["triplicity"]["score"]
        + result["term"]["score"]
        + result["decan"]["score"]
    )

    return result
