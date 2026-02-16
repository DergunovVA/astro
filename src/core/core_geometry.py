# Core Layer: Pure Math (only floats, no tuples, no strings)
from typing import List, Tuple


def ensure_float(value) -> float:
    """Strict type guard: convert to float or raise error. Never allow tuple/str in arithmetic."""
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, (tuple, list, dict, str)):
        raise TypeError(
            f"ensure_float: received {type(value).__name__}, expected float. Value: {value}"
        )
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise TypeError(
            f"ensure_float: cannot convert {type(value).__name__} to float. Error: {e}"
        )


def angle_diff(lon1: float, lon2: float) -> float:
    """Calculate minimum angle difference between two longitudes."""
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def aspect_match(
    lon1: float, lon2: float, aspect_angle: float, orb: float
) -> Tuple[bool, float]:
    """Check if two longitudes form an aspect within orb."""
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    aspect_angle = ensure_float(aspect_angle)
    orb = ensure_float(orb)
    diff = angle_diff(lon1, lon2)
    error = abs(diff - aspect_angle)
    if error <= orb:
        return True, error
    # Check 360 - angle variant for opposite aspects
    alt_error = abs((360 - diff) - aspect_angle)
    if alt_error <= orb:
        return True, alt_error
    return False, min(error, alt_error)


def normalize_longitude(lon: float) -> float:
    """Normalize longitude to 0-360 range."""
    lon = ensure_float(lon)
    return lon % 360


def planet_in_sign(lon: float) -> int:
    """Return zodiac sign (0-11) for a given longitude."""
    lon = ensure_float(lon)
    return int(normalize_longitude(lon) // 30)


def planet_in_house(lon: float, house_cusps: List[float]) -> int:
    """Return house (1-12) for a given longitude."""
    lon = ensure_float(lon)
    house_cusps = [ensure_float(c) for c in house_cusps]
    lon = normalize_longitude(lon)
    for i in range(12):
        cusp = normalize_longitude(house_cusps[i])
        next_cusp = normalize_longitude(house_cusps[(i + 1) % 12])
        if i == 11:  # Last house wraps around
            if lon >= cusp or lon < next_cusp:
                return i + 1
        else:
            if lon >= cusp and lon < next_cusp:
                return i + 1
    return 1  # Default fallback


def is_aspect_applying(
    lon1: float,
    speed1: float,
    lon2: float,
    speed2: float,
    aspect_angle: float,
    current_orb: float,
) -> str:
    """Determine if aspect is applying (converging) or separating (diverging).

    Args:
        lon1: Longitude of planet 1 (0-360°)
        speed1: Speed of planet 1 (degrees/day, negative if retrograde)
        lon2: Longitude of planet 2
        speed2: Speed of planet 2
        aspect_angle: Target aspect angle (e.g., 0, 60, 90, 120, 180)
        current_orb: Current orb (distance from exact aspect)

    Returns:
        "applying" if planets are moving towards exact aspect
        "separating" if planets are moving away from exact aspect
        "stationary" if aspect is nearly stable (both planets similar speeds)

    Method:
    - Simulate positions after 1 day
    - Compare future orb with current orb
    - Decreasing orb = applying, increasing orb = separating
    """
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    speed1 = ensure_float(speed1)
    speed2 = ensure_float(speed2)
    aspect_angle = ensure_float(aspect_angle)

    # If speeds are nearly identical, aspect is stationary
    if abs(speed1 - speed2) < 0.01:  # Less than 0.01°/day difference
        return "stationary"

    # Calculate positions after 1 day
    future_lon1 = normalize_longitude(lon1 + speed1)
    future_lon2 = normalize_longitude(lon2 + speed2)

    # Calculate future angular separation
    future_diff = angle_diff(future_lon1, future_lon2)
    future_orb = abs(future_diff - aspect_angle)

    # Also check wrapped variant (for aspects near 360°)
    future_orb_alt = abs((360 - future_diff) - aspect_angle)
    future_orb = min(future_orb, future_orb_alt)

    # Compare: is future orb smaller (applying) or larger (separating)?
    if future_orb < current_orb - 0.001:  # Small threshold to avoid floating point
        return "applying"
    elif future_orb > current_orb + 0.001:
        return "separating"
    else:
        return "stationary"


def calculate_aspects(
    planets: dict, aspects_config: dict
) -> List[Tuple[str, str, str, float, str, str]]:
    """Calculate all aspects between planets.

    Returns tuples: (planet1, planet2, aspect_name, orb, aspect_category, motion)
    where:
    - aspect_category is "major" or "minor"
    - motion is "applying", "separating", or "stationary" (if extended data available)
      or None if speed data not available

    Supports both simple format (Dict[str, float]) and extended format
    (Dict[str, dict]) with planet metadata including speeds.
    """
    result = []
    names = list(planets.keys())

    # Import MAJOR_ASPECTS to classify aspects
    from core.aspects_math import MAJOR_ASPECTS, MINOR_ASPECTS

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]

            # Handle both float and dict format
            p1_data = planets[p1]
            p2_data = planets[p2]

            if isinstance(p1_data, dict):
                lon1 = ensure_float(p1_data.get("longitude", p1_data))
                speed1 = p1_data.get("speed", None)
            else:
                lon1 = ensure_float(p1_data)
                speed1 = None

            if isinstance(p2_data, dict):
                lon2 = ensure_float(p2_data.get("longitude", p2_data))
                speed2 = p2_data.get("speed", None)
            else:
                lon2 = ensure_float(p2_data)
                speed2 = None

            for asp_name, asp_angle in aspects_config.items():
                asp_angle = ensure_float(asp_angle)
                match, orb_error = aspect_match(lon1, lon2, asp_angle, orb=8.0)
                if match:
                    # Determine if aspect is major or minor
                    if asp_name in MAJOR_ASPECTS:
                        category = "major"
                    elif asp_name in MINOR_ASPECTS:
                        category = "minor"
                    else:
                        category = "major"  # Default to major if not found

                    # Determine applying/separating if speed data available
                    motion = None
                    if speed1 is not None and speed2 is not None:
                        motion = is_aspect_applying(
                            lon1, speed1, lon2, speed2, asp_angle, orb_error
                        )

                    result.append((p1, p2, asp_name, orb_error, category, motion))
    return result


def calculate_house_positions(cusps: List[float], planets: dict) -> dict:
    """Map each planet to its house. Returns {planet_name: house_number}.

    Supports both simple format (Dict[str, float]) and extended format
    (Dict[str, dict]) with planet metadata.
    """
    result = {}
    cusps = [ensure_float(c) for c in cusps]
    for planet, data in planets.items():
        # Handle both float and dict format
        if isinstance(data, dict):
            lon = ensure_float(data.get("longitude", data))
        else:
            lon = ensure_float(data)
        result[planet] = planet_in_house(lon, cusps)
    return result


def calculate_aspects_to_angles(
    planets: dict, houses: List[float], aspects_config: dict, orb: float = 8.0
) -> List[Tuple[str, str, str, float, str]]:
    """Calculate aspects from planets to chart angles (ASC, DESC, MC, IC).

    Args:
        planets: Dict of planet positions (supports both float and dict format)
        houses: List of 12 house cusps
        aspects_config: Dict of aspect names to angles (e.g., {"conjunction": 0})
        orb: Maximum orb in degrees (default: 8.0)

    Returns:
        List of tuples: (planet_name, angle_name, aspect_name, orb, aspect_category)

    Note: Angles are the four cardinal points of the chart:
        - Ascendant (ASC): 1st house cusp - self, appearance, how others see you
        - Descendant (DESC): 7th house cusp (opposite ASC) - partnerships, relationships
        - Midheaven (MC): 10th house cusp - career, public image, achievements
        - Imum Coeli (IC): 4th house cusp (opposite MC) - home, family, roots
    """
    result = []

    # Import MAJOR_ASPECTS to classify aspects
    from core.aspects_math import MAJOR_ASPECTS, MINOR_ASPECTS

    # Define the four angles
    angles = {
        "Ascendant": ensure_float(houses[0]),  # 1st house cusp
        "Midheaven": ensure_float(houses[9]),  # 10th house cusp
        "Descendant": (ensure_float(houses[0]) + 180) % 360,  # Opposite of ASC
        "IC": (ensure_float(houses[9]) + 180) % 360,  # Opposite of MC (4th house)
    }

    # Check each planet against each angle
    for planet_name, planet_data in planets.items():
        # Handle both float and dict format
        if isinstance(planet_data, dict):
            planet_lon = ensure_float(planet_data.get("longitude", planet_data))
        else:
            planet_lon = ensure_float(planet_data)

        for angle_name, angle_lon in angles.items():
            for asp_name, asp_angle in aspects_config.items():
                asp_angle = ensure_float(asp_angle)
                match, orb_error = aspect_match(
                    planet_lon, angle_lon, asp_angle, orb=orb
                )

                if match:
                    # Determine if aspect is major or minor
                    if asp_name in MAJOR_ASPECTS:
                        category = "major"
                    elif asp_name in MINOR_ASPECTS:
                        category = "minor"
                    else:
                        category = "major"

                    result.append(
                        (planet_name, angle_name, asp_name, orb_error, category)
                    )

    return result


def calculate_aspects_to_house_cusps(
    planets: dict, houses: List[float], aspects_config: dict, orb: float = 6.0
) -> List[Tuple[str, int, str, float, str]]:
    """Calculate aspects from planets to all 12 house cusps.

    Args:
        planets: Dict of planet positions (supports both float and dict format)
        houses: List of 12 house cusps
        aspects_config: Dict of aspect names to angles (e.g., {"conjunction": 0})
        orb: Maximum orb in degrees (default: 6.0, tighter than planet-planet)

    Returns:
        List of tuples: (planet_name, house_number, aspect_name, orb, aspect_category)

    Note: Aspects to house cusps show where planetary energy manifests in life areas.
    Angular houses (1,4,7,10) are most significant.
    Conjunction to a cusp is most important (planet "coloring" that house).
    """
    result = []

    # Import MAJOR_ASPECTS to classify aspects
    from core.aspects_math import MAJOR_ASPECTS, MINOR_ASPECTS

    # Check each planet against each house cusp
    for planet_name, planet_data in planets.items():
        # Handle both float and dict format
        if isinstance(planet_data, dict):
            planet_lon = ensure_float(planet_data.get("longitude", planet_data))
        else:
            planet_lon = ensure_float(planet_data)

        for house_num in range(1, 13):  # Houses 1-12
            cusp_lon = ensure_float(houses[house_num - 1])  # 0-indexed list

            for asp_name, asp_angle in aspects_config.items():
                asp_angle = ensure_float(asp_angle)
                match, orb_error = aspect_match(
                    planet_lon, cusp_lon, asp_angle, orb=orb
                )

                if match:
                    # Determine if aspect is major or minor
                    if asp_name in MAJOR_ASPECTS:
                        category = "major"
                    elif asp_name in MINOR_ASPECTS:
                        category = "minor"
                    else:
                        category = "major"

                    result.append(
                        (planet_name, house_num, asp_name, orb_error, category)
                    )

    return result
