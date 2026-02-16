# Astro Adapter Layer: Swiss Ephemeris → Core (tuple unwrapping, normalization)
import swisseph as swe
from datetime import datetime
from typing import Dict, Any, List
from modules.house_systems import calc_houses


def calc_planets_raw(jd: float) -> Dict[str, float]:
    """Get planet longitudes (float only) from Swiss Ephemeris.

    Now includes:
    - 7 classical planets (Sun through Saturn)
    - 3 outer planets (Uranus, Neptune, Pluto)
    - Mean North Node
    - Chiron

    Total: 12 bodies
    """
    planets = {}

    # Classical planets (Sun through Saturn)
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

    # Outer planets (modern astrology, discovered 1781-1930)
    for p in [
        swe.URANUS,  # ♅ Discovered 1781 - revolution, sudden change, innovation
        swe.NEPTUNE,  # ♆ Discovered 1846 - illusion, spirituality, dissolution
        swe.PLUTO,  # ♇ Discovered 1930 - transformation, power, depth psychology
    ]:
        result = swe.calc_ut(jd, p)
        pos_tuple = result[0]
        planets[swe.get_planet_name(p)] = float(pos_tuple[0])

    # Special points
    # North Node (Mean) - ☊ Karmic direction, soul's purpose
    result = swe.calc_ut(jd, swe.MEAN_NODE)
    planets["North Node"] = float(result[0][0])

    # Chiron - ⚷ The wounded healer, discovered 1977
    # Note: Requires asteroid ephemeris files (seas_18.se1)
    try:
        result = swe.calc_ut(jd, swe.CHIRON)
        planets["Chiron"] = float(result[0][0])
    except Exception:
        # Chiron calculation failed (missing ephemeris files)
        # This is not critical, continue without it
        pass

    return planets


def calc_planets_extended(jd: float) -> Dict[str, Dict[str, Any]]:
    """Get extended planet information including retrograde status.

    Returns dict with structure:
    {
        "Sun": {
            "longitude": 295.27,
            "latitude": 0.0,
            "speed": 1.0141,
            "retrograde": False
        },
        ...
    }

    Speed is in degrees per day. Negative speed indicates retrograde motion.
    Note: Sun and Moon are never retrograde.
    """
    planets = {}

    # All bodies to calculate
    body_ids = [
        # Classical
        swe.SUN,
        swe.MOON,
        swe.MERCURY,
        swe.VENUS,
        swe.MARS,
        swe.JUPITER,
        swe.SATURN,
        # Outer
        swe.URANUS,
        swe.NEPTUNE,
        swe.PLUTO,
        # Special
        swe.MEAN_NODE,
        swe.CHIRON,
    ]

    for body_id in body_ids:
        try:
            result = swe.calc_ut(jd, body_id)
            pos_tuple = result[
                0
            ]  # (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)

            # Get planet name
            if body_id == swe.MEAN_NODE:
                name = "North Node"
            else:
                name = swe.get_planet_name(body_id)

            # Extract data
            longitude = float(pos_tuple[0])
            latitude = float(pos_tuple[1]) if len(pos_tuple) > 1 else 0.0
            speed = (
                float(pos_tuple[3]) if len(pos_tuple) > 3 else 0.0
            )  # Speed in longitude (degrees/day)

            # Determine retrograde status
            # Negative speed = retrograde motion
            # Note: Sun, Moon, and North Node are never technically retrograde
            is_retrograde = speed < 0 and body_id not in [
                swe.SUN,
                swe.MOON,
                swe.MEAN_NODE,
            ]

            planets[name] = {
                "longitude": longitude,
                "latitude": latitude,
                "speed": speed,
                "retrograde": is_retrograde,
            }
        except Exception:
            # Skip planets that fail (e.g., Chiron without asteroid ephemeris)
            continue

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
    utc_dt: datetime,
    lat: float,
    lon: float,
    house_method: str = "Placidus",
    extended: bool = False,
) -> Dict[str, Any]:
    """Perform complete natal calculation: unwrap Swiss Ephemeris → return floats.

    Args:
        utc_dt: timezone-aware datetime in UTC (from normalize_input)
        lat: latitude in decimal degrees (from normalize_input)
        lon: longitude in decimal degrees (from normalize_input)
        house_method: House system to use (default: Placidus)
        extended: If True, include retrograde status and additional data

    Returns:
        Dict with jd, planets, houses, coords, house_method

        If extended=False (default):
            planets: Dict[str, float] - just longitudes

        If extended=True:
            planets: Dict[str, dict] - full data with retrograde status

    Note: Coordinates should be pre-computed by normalize_input to avoid double-geocoding
    """
    jd = julian_day(utc_dt)

    if extended:
        planets = calc_planets_extended(jd)
    else:
        planets = calc_planets_raw(jd)

    houses = calc_houses_raw(jd, lat, lon, method=house_method)

    return {
        "jd": jd,
        "planets": planets,
        "houses": houses,
        "coords": {"lon": lon, "lat": lat},
        "house_method": house_method,
    }
