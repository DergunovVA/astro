"""
Horary Astrology - Standalone Functions

Traditional horary methods for answering specific questions.
Based on William Lilly's "Christian Astrology" (1647).

Techniques implemented:
- Time to perfection (applying/separating aspect timing)
- Void of Course Moon (no major aspects before sign change)
- Radicality check (ASC degree 3-27°, Saturn restrictions)
- Mutual receptions (domicile, traditional rulers)
- Translation of light (3rd planet connects two significators)
- Collection of light (both significators apply to 3rd planet)
"""

from typing import Dict, Optional, Any, List

from src.core.dignities import (
    get_planet_sign,
    get_dispositor,
)
from src.core.aspects_math import MAJOR_ASPECTS


# ============================================================
# TRANSLATION & COLLECTION OF LIGHT
# ============================================================


def find_translation_of_light(
    planet1: str,
    planet2: str,
    planets: Dict[str, Dict],
    aspects: List[Dict],
) -> Optional[str]:
    """
    Find translation of light.

    Translation: a 3rd planet aspects both significators, connecting them
    when they don't aspect each other directly. The translator separates
    from one significator and applies to the other.

    Args:
        planet1: First significator name
        planet2: Second significator name
        planets: Dict of all planet names to planet data
        aspects: List of pre-calculated aspects (each dict with planet1/planet2 keys)

    Returns:
        Translator planet name or None

    Example:
        >>> # Moon @ 10° Aries, Mars @ 20° Aries, Saturn @ 5° Gemini
        >>> # Moon separates from Mars, then applies to Saturn
        >>> translator = find_translation_of_light('Mars', 'Saturn', planets, aspects)
        >>> print(translator)  # 'Moon'
    """

    def has_aspect(p1: str, p2: str) -> bool:
        for asp in aspects:
            if not isinstance(asp, dict):
                continue
            a1, a2 = asp.get("planet1"), asp.get("planet2")
            if (a1 == p1 and a2 == p2) or (a1 == p2 and a2 == p1):
                return True
        return False

    for planet in planets:
        if planet == planet1 or planet == planet2:
            continue
        if has_aspect(planet, planet1) and has_aspect(planet, planet2):
            return planet

    return None


def find_collection_of_light(
    planet1: str,
    planet2: str,
    planets: Dict[str, Dict],
    aspects: List[Dict],
) -> Optional[str]:
    """
    Find collection of light.

    Collection: both significators apply to a 3rd (slower/more dignified) planet,
    which collects their light and brings them together.

    Args:
        planet1: First significator name
        planet2: Second significator name
        planets: Dict of all planet names to planet data
        aspects: List of pre-calculated aspects

    Returns:
        Collector planet name or None

    Example:
        >>> # Moon @ 5° Aries → Jupiter @ 15° Aries (applying)
        >>> # Saturn @ 12° Aries → Jupiter @ 15° Aries (applying)
        >>> collector = find_collection_of_light('Moon', 'Saturn', planets, aspects)
        >>> print(collector)  # 'Jupiter'
    """

    def get_aspect(p1: str, p2: str) -> Optional[Dict]:
        for asp in aspects:
            if not isinstance(asp, dict):
                continue
            a1, a2 = asp.get("planet1"), asp.get("planet2")
            if (a1 == p1 and a2 == p2) or (a1 == p2 and a2 == p1):
                return asp
        return None

    for planet in planets:
        if planet == planet1 or planet == planet2:
            continue
        asp1 = get_aspect(planet1, planet)
        asp2 = get_aspect(planet2, planet)
        if asp1 and asp2:
            # Both should be applying to the collector
            if asp1.get("applying", True) and asp2.get("applying", True):
                return planet

    return None


# ============================================================
# STANDALONE HORARY UTILITY FUNCTIONS (used in CLI)
# ============================================================


# NOTE: HoraryAnalyzer class was removed (was unused in CLI).
# Translation of light and collection of light are now standalone functions above.
# Old class was archived in git history (commit 81398f9).


def time_to_perfection(
    planet1_lon: float,
    planet1_speed: float,
    planet2_lon: float,
    planet2_speed: float,
    aspect_angle: float,
) -> Dict[str, Any]:
    """
    Calculate time until aspect reaches perfection (exact).

    This is crucial for horary timing predictions.

    Args:
        planet1_lon: Longitude of first planet (degrees)
        planet1_speed: Daily speed of first planet (degrees/day)
        planet2_lon: Longitude of second planet (degrees/day)
        planet2_speed: Daily speed of second planet (degrees/day)
        aspect_angle: Target aspect angle (0, 60, 90, 120, 180, etc.)

    Returns:
        dict with:
        {
            'days': float,
            'hours': float,
            'is_applying': bool,
            'current_distance': float,
            'relative_speed': float
        }

    Example:
        >>> # Moon at 114° moving 13°/day, Saturn at 1.6° moving 0.03°/day
        >>> # Trine = 120° apart
        >>> result = time_to_perfection(114.16, 13.0, 1.6, 0.03, 120)
        >>> print(result['days'])  # ~0.57 days
        >>> print(result['hours'])  # ~14 hours
    """
    # Normalize longitudes to 0-360
    planet1_lon = planet1_lon % 360
    planet2_lon = planet2_lon % 360

    # Calculate where planet1 needs to be for the aspect
    # Two possible positions: planet2 + aspect_angle or planet2 - aspect_angle
    target1 = (planet2_lon + aspect_angle) % 360
    target2 = (planet2_lon - aspect_angle) % 360

    # Calculate distances to each target (shortest arc)
    def shortest_arc(from_lon, to_lon):
        """Calculate shortest arc distance from from_lon to to_lon"""
        diff = (to_lon - from_lon) % 360
        if diff > 180:
            diff = diff - 360
        return diff

    dist1 = shortest_arc(planet1_lon, target1)
    dist2 = shortest_arc(planet1_lon, target2)

    # Choose the target that planet1 is moving toward
    if abs(dist1) < abs(dist2):
        distance_to_aspect = dist1
    else:
        distance_to_aspect = dist2

    # Net relative speed (how fast gap is closing)
    relative_speed = planet1_speed - planet2_speed

    # Determine if applying (closing) or separating
    is_applying = False

    if distance_to_aspect > 0:
        # Planet1 needs to move forward
        is_applying = relative_speed > 0
    elif distance_to_aspect < 0:
        # Planet1 needs to move backward (or planet2 needs to move forward)
        is_applying = relative_speed < 0

    # Calculate time to perfection
    days = 0.0
    hours = 0.0

    if is_applying and abs(relative_speed) > 0.001:
        days = abs(distance_to_aspect) / abs(relative_speed)
        hours = days * 24

    return {
        "days": round(days, 2),
        "hours": round(hours, 1),
        "is_applying": is_applying,
        "current_distance": round(distance_to_aspect, 2),
        "relative_speed": round(relative_speed, 2),
    }


def is_void_of_course(
    moon_lon: float, moon_speed: float, planets: Dict[str, float]
) -> Dict[str, Any]:
    """
    Check if Moon is Void of Course.

    VOC Moon: Moon makes no major aspects before leaving current sign.
    This is considered unfavorable for horary questions.

    Args:
        moon_lon: Moon's longitude (degrees)
        moon_speed: Moon's speed (degrees/day, typically 12-15)
        planets: Dict of planet names to longitudes

    Returns:
        dict with:
        {
            'is_void': bool,
            'last_aspect': str or None,  # Planet name of last aspect
            'last_aspect_type': str or None,  # Aspect type
            'next_sign_in_degrees': float,  # Degrees until next sign
            'next_sign_in_hours': float,  # Hours until sign change
            'current_sign': str
        }

    Example:
        >>> planets = {'Sun': 339.3, 'Mercury': 352.3, 'Venus': 351.9}
        >>> result = is_void_of_course(114.16, 13.0, planets)
        >>> print(result['is_void'])  # True or False
    """

    current_sign = get_planet_sign(moon_lon)

    # Calculate degree within sign (0-30)
    degree_in_sign = moon_lon % 30

    # Degrees until next sign
    degrees_to_next_sign = 30 - degree_in_sign
    hours_to_next_sign = (degrees_to_next_sign / moon_speed) * 24

    # Check for major aspects within current sign
    future_aspects = []

    for planet_name, planet_lon in planets.items():
        if planet_name == "Moon":
            continue

        # Calculate future position of Moon before sign change
        for aspect_name, aspect_config in MAJOR_ASPECTS.items():
            aspect_angle = aspect_config["angle"]

            # Calculate when Moon will form this aspect
            target_lon = (planet_lon + aspect_angle) % 360
            distance = (target_lon - moon_lon) % 360

            # Check if Moon will reach this aspect before leaving sign
            if distance <= degrees_to_next_sign and distance / moon_speed <= 2:
                # Aspect is within reach
                future_aspects.append(
                    {
                        "planet": planet_name,
                        "aspect": aspect_name,
                        "distance": distance,
                        "hours": (distance / moon_speed) * 24,
                    }
                )

    # Moon is VOC if no future major aspects before sign change
    is_void = len(future_aspects) == 0

    return {
        "is_void": is_void,
        "last_aspect": None,  # Would need historical data
        "last_aspect_type": None,
        "next_sign_in_degrees": round(degrees_to_next_sign, 2),
        "next_sign_in_hours": round(hours_to_next_sign, 1),
        "current_sign": current_sign,
        "upcoming_aspects": future_aspects if not is_void else [],
    }


def check_radicality(asc_lon: float, saturn_house: int) -> Dict[str, Any]:
    """
    Check if horary chart is "radical" (valid to judge).

    Traditional rules:
    1. ASC must be between 3° and 27° of sign (not too early/late)
    2. Saturn NOT in 1st or 7th house (blocks judgment)
    3. Moon NOT Void of Course (requires is_void_of_course() result)

    Args:
        asc_lon: Ascendant longitude (degrees)
        saturn_house: House number where Saturn is located (1-12)

    Returns:
        dict with:
        {
            'is_radical': bool,
            'warnings': [list of warning strings],
            'asc_degree_in_sign': float
        }

    Example:
        >>> result = check_radicality(244.66, 12)
        >>> print(result['is_radical'])  # True or False
        >>> print(result['warnings'])  # ['ASC too late in sign', ...]
    """
    warnings = []
    is_radical = True

    # Check Ascendant degree within sign
    asc_degree_in_sign = asc_lon % 30

    if asc_degree_in_sign < 3:
        warnings.append(
            f"ASC too early in sign ({asc_degree_in_sign:.1f}°) - question may be premature"
        )
        is_radical = False
    elif asc_degree_in_sign > 27:
        warnings.append(
            f"ASC too late in sign ({asc_degree_in_sign:.1f}°) - question may be too late"
        )
        is_radical = False

    # Check Saturn in 1st or 7th house
    if saturn_house in [1, 7]:
        warnings.append(
            f"Saturn in {saturn_house}{'st' if saturn_house == 1 else 'th'} house - judgment blocked or difficult"
        )
        is_radical = False

    return {
        "is_radical": is_radical,
        "warnings": warnings,
        "asc_degree_in_sign": round(asc_degree_in_sign, 1),
    }


def find_mutual_receptions(planets: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Find all mutual receptions in the chart.

    Mutual reception: Two planets in each other's ruling signs.
    This creates a strong connection and mutual help.

    Args:
        planets: Dict of planet names to planet data containing 'longitude'

    Returns:
        List of mutual reception pairs:
        [
            {
                'planet1': 'Saturn',
                'planet2': 'Mars',
                'planet1_sign': 'Aries',
                'planet2_sign': 'Aquarius',
                'type': 'domicile'  # or 'exaltation'
            },
            ...
        ]

    Example:
        >>> planets = {
        ...     'Saturn': {'longitude': 1.6},  # Aries
        ...     'Mars': {'longitude': 327.9}   # Aquarius
        ... }
        >>> receptions = find_mutual_receptions(planets)
        >>> print(receptions[0])  # {'planet1': 'Saturn', 'planet2': 'Mars', ...}
    """

    mutual_receptions = []

    planet_names = list(planets.keys())

    for i, p1_name in enumerate(planet_names):
        for p2_name in planet_names[i + 1 :]:
            p1_data = planets[p1_name]
            p2_data = planets[p2_name]

            if "longitude" not in p1_data or "longitude" not in p2_data:
                continue

            p1_lon = p1_data["longitude"]
            p2_lon = p2_data["longitude"]

            p1_sign = get_planet_sign(p1_lon)
            p2_sign = get_planet_sign(p2_lon)

            # Check domicile mutual reception (use traditional rulers for horary)
            p1_ruler = get_dispositor(p1_sign, traditional=True)
            p2_ruler = get_dispositor(p2_sign, traditional=True)

            if p1_ruler == p2_name and p2_ruler == p1_name:
                mutual_receptions.append(
                    {
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "planet1_sign": p1_sign,
                        "planet2_sign": p2_sign,
                        "type": "domicile",
                    }
                )

            # Check exaltation mutual reception (less common)
            # This is more complex as exaltation can be by domicile ruler
            # We'll skip this for now or implement if needed

    return mutual_receptions
