# Astro Adapter Layer: Swiss Ephemeris → Core (tuple unwrapping, normalization)
import swisseph as swe
from datetime import datetime
from typing import Dict, Any, List
from modules.house_systems import calc_houses


def calc_planets_raw(jd: float) -> Dict[str, float]:
    """Get planet longitudes (float only) from Swiss Ephemeris."""
    planets = {}
    for p in [
        swe.SUN,
        swe.MOON,
        swe.MERCURY,
        swe.VENUS,
        swe.MARS,
        swe.JUPITER,
        swe.SATURN,
    ]:
        result = swe.calc_ut(jd, p)  # Returns ((lon, lat, ...), flags)
        pos_tuple = result[0]  # Get the position tuple
        planets[swe.get_planet_name(p)] = float(
            pos_tuple[0]
        )  # Extract longitude only, ensure float
    return planets


def calc_houses_raw(
    jd: float, lat: float, lon: float, method: str = "Placidus"
) -> List[float]:
    """Get house cusps (floats only) from house_systems module.

    Args:
        jd: Julian Day number
        lat: Observer latitude
        lon: Observer longitude
        method: House system name (Placidus, Koch, Regiomontanus, Campanus,
                Topocentric, Equal, Porphyry, Alcabitius, Whole Sign)

    Returns:
        List of 12 house cusp longitudes (floats)
    """
    return calc_houses(jd, lat, lon, method=method)


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

    dt_utc = utc_dt.astimezone(tz=ZoneInfo("UTC"))
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def natal_calculation(
    utc_dt: datetime, lat: float, lon: float, house_method: str = "Placidus"
) -> Dict[str, Any]:
    """Perform complete natal calculation: unwrap Swiss Ephemeris → return floats.

    Args:
        utc_dt: timezone-aware datetime in UTC (from normalize_input)
        lat: latitude in decimal degrees (from normalize_input)
        lon: longitude in decimal degrees (from normalize_input)
        house_method: House system to use (default: Placidus)

    Returns:
        Dict with jd, planets, houses, coords, house_method

    Note: Coordinates should be pre-computed by normalize_input to avoid double-geocoding
    """
    jd = julian_day(utc_dt)
    planets = calc_planets_raw(jd)
    houses = calc_houses_raw(jd, lat, lon, method=house_method)

    return {
        "jd": jd,
        "planets": planets,
        "houses": houses,
        "coords": {"lon": lon, "lat": lat},
        "house_method": house_method,
    }
