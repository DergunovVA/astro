# Astro Adapter Layer: Swiss Ephemeris → Core (tuple unwrapping, normalization)
import swisseph as swe
from datetime import datetime
from typing import Dict, Any, List

def calc_planets_raw(jd: float) -> Dict[str, float]:
    """Get planet longitudes (float only) from Swiss Ephemeris."""
    planets = {}
    for p in [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]:
        result = swe.calc_ut(jd, p)  # Returns ((lon, lat, ...), flags)
        pos_tuple = result[0]  # Get the position tuple
        planets[swe.get_planet_name(p)] = float(pos_tuple[0])  # Extract longitude only, ensure float
    return planets

def calc_houses_raw(jd: float, lat: float, lon: float, method: str = "Placidus") -> List[float]:
    """Get house cusps (floats only) from Swiss Ephemeris."""
    if method == "Placidus":
        cusps_tuple = swe.houses(jd, lat, lon)
        return list(cusps_tuple[0])  # Unwrap to list of floats
    elif method == "WholeSign":
        asc = swe.houses(jd, lat, lon)[0][0]
        return [(asc + i * 30) % 360 for i in range(12)]
    else:
        raise ValueError("Unknown house method")

def julian_day(utc_dt: datetime) -> float:
    """Convert UTC datetime to Julian Day.
    
    Args:
        utc_dt: timezone-aware datetime in UTC
        
    Returns:
        Julian Day number
        
    Raises:
        ValueError: if datetime is not UTC-aware
    """
    if utc_dt.tzinfo is None:
        raise ValueError("datetime must be UTC-aware (have tzinfo)")
    # Extract UTC components (handle case where datetime might be in different TZ)
    from zoneinfo import ZoneInfo
    dt_utc = utc_dt.astimezone(tz=ZoneInfo('UTC'))
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                     dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)

def natal_calculation(utc_dt: datetime, lat: float, lon: float) -> Dict[str, Any]:
    """Perform complete natal calculation: unwrap Swiss Ephemeris → return floats.
    
    Args:
        utc_dt: timezone-aware datetime in UTC (from normalize_input)
        lat: latitude in decimal degrees (from normalize_input)
        lon: longitude in decimal degrees (from normalize_input)
        
    Returns:
        Dict with jd, planets, houses, coords
        
    Note: Coordinates should be pre-computed by normalize_input to avoid double-geocoding
    """
    jd = julian_day(utc_dt)
    planets = calc_planets_raw(jd)
    houses = calc_houses_raw(jd, lat, lon, method="Placidus")
    
    return {
        "jd": jd,
        "planets": planets,
        "houses": houses,
        "coords": {"lon": lon, "lat": lat}
    }
