# Core Layer: Pure Math (only floats, no tuples, no strings)
from typing import List, Tuple

def ensure_float(value) -> float:
    """Strict type guard: convert to float or raise error. Never allow tuple/str in arithmetic."""
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, (tuple, list, dict, str)):
        raise TypeError(f"ensure_float: received {type(value).__name__}, expected float. Value: {value}")
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise TypeError(f"ensure_float: cannot convert {type(value).__name__} to float. Error: {e}")

def angle_diff(lon1: float, lon2: float) -> float:
    """Calculate minimum angle difference between two longitudes."""
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)

def aspect_match(lon1: float, lon2: float, aspect_angle: float, orb: float) -> Tuple[bool, float]:
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

def calculate_aspects(planets: dict, aspects_config: dict) -> List[Tuple[str, str, str, float, str]]:
    """Calculate all aspects between planets.
    
    Returns tuples: (planet1, planet2, aspect_name, orb, aspect_category)
    where aspect_category is "major" or "minor"
    """
    result = []
    names = list(planets.keys())
    
    # Import MAJOR_ASPECTS to classify aspects
    from aspects_math import MAJOR_ASPECTS, MINOR_ASPECTS
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            lon1 = ensure_float(planets[p1])
            lon2 = ensure_float(planets[p2])
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
                    
                    result.append((p1, p2, asp_name, orb_error, category))
    return result

def calculate_house_positions(cusps: List[float], planets: dict) -> dict:
    """Map each planet to its house. Returns {planet_name: house_number}."""
    result = {}
    cusps = [ensure_float(c) for c in cusps]
    for planet, lon in planets.items():
        lon = ensure_float(lon)
        result[planet] = planet_in_house(lon, cusps)
    return result
