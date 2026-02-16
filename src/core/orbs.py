"""
Variable Orbs for Aspects - Traditional Astrology Values

Different planets have different "influence spheres" based on:
1. Brightness and visibility (luminaries have larger orbs)
2. Speed of motion (faster = tighter orbs)
3. Traditional astrological significance

Based on:
- William Lilly's "Christian Astrology"
- Robert Hand's recommendations
- Modern astrological consensus
"""

# PLANET ORBS (for major aspects)
# Values in degrees - maximum distance from exact aspect
PLANET_ORBS = {
    # Luminaries (largest orbs - most visible, most significant)
    "Sun": 17.0,  # Ancient: 15°, Modern: 17° (brightest object)
    "Moon": 12.0,  # Fast mover, highly visible
    # Personal planets
    "Mercury": 7.0,  # Fast, but small
    "Venus": 7.0,  # Moderately bright
    "Mars": 7.0,  # Visible, but slower than inner planets
    # Social planets
    "Jupiter": 9.0,  # Large, slow-moving, significant
    "Saturn": 9.0,  # Traditional boundary of visible planets
    # Outer planets (smaller orbs - slower, less personal)
    "Uranus": 5.0,  # Modern planet, generational
    "Neptune": 5.0,  # Discovered 1846, spiritual/illusion
    "Pluto": 5.0,  # Discovered 1930, transformational
    # Special points (medium orbs)
    "North Node": 6.0,  # Karmic axis
    "South Node": 6.0,  # Calculated opposite of North Node
    "Chiron": 3.0,  # Minor body, wounded healer
    "Lilith": 2.0,  # Calculated point (Black Moon)
    "Vertex": 3.0,  # Calculated point (fate/destiny)
    "East Point": 2.0,  # Calculated (Ascendant of zero latitude)
    "Part of Fortune": 3.0,  # Arabic part
    "Part of Spirit": 3.0,  # Arabic part
    "Part of Eros": 2.0,  # Arabic part
}

# ASPECT TYPE MULTIPLIERS
# Minor aspects use smaller orbs (typically 50-70% of major aspect orbs)
ASPECT_ORB_MULTIPLIERS = {
    # Major aspects (Ptolemaic + opposition)
    "conjunction": 1.0,  # 100% of base orb
    "opposition": 1.0,
    "trine": 1.0,
    "square": 1.0,
    "sextile": 1.0,
    # Minor aspects - basic (70% of base)
    "semisextile": 0.6,  # 30° aspect
    "quincunx": 0.7,  # 150° aspect (important minor aspect)
    "semisquare": 0.6,  # 45° aspect
    "sesquiquadrate": 0.6,  # 135° aspect
    # Harmonic aspects (50-60% of base)
    "quintile": 0.5,  # 72° - 5th harmonic (talent, creativity)
    "biquintile": 0.5,  # 144° - 5th harmonic
    "septile": 0.4,  # 51.43° - 7th harmonic (fate, spiritual)
    "novile": 0.4,  # 40° - 9th harmonic (completion, wisdom)
}

# DEFAULT ORBS (fallback values)
DEFAULT_PLANET_ORB = 6.0  # If planet not found in table
DEFAULT_MAJOR_ORB = 8.0  # Traditional general orb for major aspects
DEFAULT_MINOR_ORB = 3.0  # Traditional general orb for minor aspects


def get_aspect_orb(planet1: str, planet2: str, aspect_type: str) -> float:
    """
    Calculate appropriate orb for an aspect between two planets.

    Uses the SMALLER of the two planet orbs (moiety method).
    Then applies aspect type multiplier for minor aspects.

    Args:
        planet1: Name of first planet
        planet2: Name of second planet
        aspect_type: Type of aspect (e.g., "conjunction", "trine")

    Returns:
        Orb in degrees (float)

    Examples:
        Sun-Moon conjunction: min(17, 12) * 1.0 = 12°
        Mercury-Saturn trine: min(7, 9) * 1.0 = 7°
        Venus-Mars quintile: min(7, 7) * 0.5 = 3.5°
        Sun-Pluto opposition: min(17, 5) * 1.0 = 5°
    """
    # Get base orbs for each planet
    orb1 = PLANET_ORBS.get(planet1, DEFAULT_PLANET_ORB)
    orb2 = PLANET_ORBS.get(planet2, DEFAULT_PLANET_ORB)

    # Use smaller orb (moiety/half-sum method)
    base_orb = min(orb1, orb2)

    # Apply aspect type multiplier
    multiplier = ASPECT_ORB_MULTIPLIERS.get(aspect_type, 0.5)

    return base_orb * multiplier


def get_orb_for_angle(planet: str, aspect_type: str) -> float:
    """
    Calculate orb for aspect from planet to angle (ASC, MC, DESC, IC).

    Angles are treated as having orbs similar to luminaries (high significance).

    Args:
        planet: Planet name
        aspect_type: Type of aspect

    Returns:
        Orb in degrees
    """
    # Angles have fixed orb (treated like luminaries)
    angle_orb = 10.0  # Angles are critical, but not as wide as Sun
    planet_orb = PLANET_ORBS.get(planet, DEFAULT_PLANET_ORB)

    base_orb = min(angle_orb, planet_orb)
    multiplier = ASPECT_ORB_MULTIPLIERS.get(aspect_type, 0.5)

    return base_orb * multiplier
