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


def calc_special_points(
    jd: float, lat: float, lon: float, houses: List[float], planets: Dict[str, Any]
) -> Dict[str, float]:
    """Calculate special astrological points.

    Args:
        jd: Julian day
        lat: latitude in decimal degrees
        lon: longitude in decimal degrees
        houses: List of 12 house cusps
        planets: Planet positions (either float or dict format)

    Returns:
        Dict with special points:
        - Lilith: True Black Moon (osculating lunar apogee)
        - Vertex: Point of fated encounters (intersection of prime vertical with ecliptic)
        - East Point: Point on eastern horizon at ecliptic
        - Part of Fortune: Traditional lot (diurnal/nocturnal formula)
        - Part of Spirit: Inverse of Part of Fortune
    """
    special = {}

    # 1. LILITH (TRUE BLACK MOON) - Osculating Lunar Apogee
    # Swiss Ephemeris has multiple Lilith options:
    # - MEAN_APOG = Mean Black Moon (smoothed)
    # - OSCU_APOG = True/Osculating Black Moon (wobbles, more accurate)
    try:
        result = swe.calc_ut(jd, swe.OSCU_APOG)
        special["Lilith"] = float(result[0][0])
    except Exception:
        # Fallback to Mean Lilith if osculating fails
        try:
            result = swe.calc_ut(jd, swe.MEAN_APOG)
            special["Lilith"] = float(result[0][0])
        except Exception:
            pass

    # 2. VERTEX - Fated encounters, others' impact on us
    # Formula: Intersection of Prime Vertical with the Ecliptic in Western hemisphere
    # Simplified: Vertex is typically near the Descendant (7th house cusp)
    # More accurate calculation requires ARMC (Right Ascension of MC)
    try:
        # Approximate formula using latitude
        # Vertex longitude ≈ similar to Descendant but adjusted for latitude
        # For now, use simplified approach: DESC + small offset based on latitude
        asc = houses[0]
        desc = (asc + 180.0) % 360.0

        # Vertex is typically 5-20° from Descendant depending on latitude
        # Simplified offset (this is an approximation)
        lat_offset = lat * 0.2  # Rough adjustment
        vertex_lon = (desc + lat_offset) % 360.0

        special["Vertex"] = vertex_lon

    except Exception:
        # Vertex calculation failed
        pass
        # Vertex calculation failed
        pass

    # 3. EAST POINT - Ecliptic degree rising at due east
    # This is the point on the ecliptic at the eastern horizon
    # Simplified: EP ≈ ASC + 90° (rough approximation)
    try:
        asc = houses[0]  # Ascendant
        east_point = (asc + 90.0) % 360.0
        special["East Point"] = east_point

    except Exception:
        pass

    # 4. PART OF FORTUNE (Pars Fortunae) - Material fortune, body, health
    # Diurnal (day) chart: ASC + Moon - Sun
    # Nocturnal (night) chart: ASC + Sun - Moon
    try:
        asc = houses[0]

        # Get Sun and Moon longitudes (handle both float and dict formats)
        if isinstance(planets.get("Sun"), dict):
            sun_lon = planets["Sun"]["longitude"]
        else:
            sun_lon = planets.get("Sun", 0.0)

        if isinstance(planets.get("Moon"), dict):
            moon_lon = planets["Moon"]["longitude"]
        else:
            moon_lon = planets.get("Moon", 0.0)

        # Determine if chart is diurnal or nocturnal
        # Diurnal = Sun above horizon (houses 7-12, or more precisely: sun in houses 7,8,9,10,11,12)
        # Simplified: check if Sun is in houses 7-12 by comparing to DESC (houses[6])
        desc = (asc + 180.0) % 360.0

        # Check if Sun is above horizon (between DESC and ASC going counterclockwise)
        # If Sun > DESC or Sun < ASC (wrapping around 0°)
        if desc > asc:
            # Normal case: DESC at 180°, ASC at 0°
            is_diurnal = sun_lon >= desc or sun_lon <= asc
        else:
            # Wrapped case: DESC at 350°, ASC at 170°
            is_diurnal = sun_lon >= desc and sun_lon <= asc

        if is_diurnal:
            # Day chart: ASC + Moon - Sun
            pof = (asc + moon_lon - sun_lon) % 360.0
        else:
            # Night chart: ASC + Sun - Moon
            pof = (asc + sun_lon - moon_lon) % 360.0

        special["Part of Fortune"] = pof

    except Exception:
        pass

    # 5. PART OF SPIRIT (Pars Spiritus) - Spiritual purpose, soul
    # Inverse of Part of Fortune:
    # Diurnal: ASC + Sun - Moon
    # Nocturnal: ASC + Moon - Sun
    try:
        asc = houses[0]

        if isinstance(planets.get("Sun"), dict):
            sun_lon = planets["Sun"]["longitude"]
        else:
            sun_lon = planets.get("Sun", 0.0)

        if isinstance(planets.get("Moon"), dict):
            moon_lon = planets["Moon"]["longitude"]
        else:
            moon_lon = planets.get("Moon", 0.0)

        # Same diurnal/nocturnal check as above
        desc = (asc + 180.0) % 360.0
        if desc > asc:
            is_diurnal = sun_lon >= desc or sun_lon <= asc
        else:
            is_diurnal = sun_lon >= desc and sun_lon <= asc

        if is_diurnal:
            # Day chart: ASC + Sun - Moon (inverse of PoF)
            pos = (asc + sun_lon - moon_lon) % 360.0
        else:
            # Night chart: ASC + Moon - Sun (inverse of PoF)
            pos = (asc + moon_lon - sun_lon) % 360.0

        special["Part of Spirit"] = pos

    except Exception:
        pass

    return special


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
        Dict with jd, planets, houses, coords, house_method, special_points

        If extended=False (default):
            planets: Dict[str, float] - just longitudes

        If extended=True:
            planets: Dict[str, dict] - full data with retrograde status

        special_points: Dict[str, float] - Lilith, Vertex, East Point, Parts

    Note: Coordinates should be pre-computed by normalize_input to avoid double-geocoding
    """
    jd = julian_day(utc_dt)

    if extended:
        planets = calc_planets_extended(jd)
    else:
        planets = calc_planets_raw(jd)

    houses = calc_houses_raw(jd, lat, lon, method=house_method)

    # Calculate special points (always included now)
    special_points = calc_special_points(jd, lat, lon, houses, planets)

    return {
        "jd": jd,
        "planets": planets,
        "houses": houses,
        "special_points": special_points,
        "coords": {"lon": lon, "lat": lat},
        "house_method": house_method,
    }
