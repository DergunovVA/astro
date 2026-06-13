# Astro Adapter Layer: Swiss Ephemeris → Core (tuple unwrapping, normalization)
import logging
import swisseph as swe
import os
from datetime import datetime
from typing import Dict, Any, List
from modules.house_systems import calc_houses

logger = logging.getLogger(__name__)

# Set ephemeris path for fictitious bodies (Proserpina requires seorbel.txt)
ephe_path = os.environ.get("SWEPH_PATH", r"C:\sweph\ephe")
if os.path.exists(ephe_path):
    swe.set_ephe_path(ephe_path)


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
    except Exception as e:
        logger.debug("Chiron not available (missing ephemeris): %s", e)

    # Proserpina - ⚸ Hypothetical trans-Plutonian planet
    # Swiss Ephemeris ID 57 (requires seorbel.txt)
    try:
        result = swe.calc_ut(jd, 57)  # Proserpina (Abramov version)
        planets["Proserpina"] = float(result[0][0])
    except Exception as e:
        logger.debug("Proserpina not available (seorbel.txt missing): %s", e)

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
        57,  # Proserpina (Swiss Ephemeris, requires seorbel.txt)
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
            elif body_id == 57:
                name = "Proserpina"
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
    except Exception as e:
        logger.debug("Osculating Lilith failed, trying Mean: %s", e)
        try:
            result = swe.calc_ut(jd, swe.MEAN_APOG)
            special["Lilith"] = float(result[0][0])
        except Exception as e2:
            logger.warning("Lilith (both osculating and mean) unavailable: %s", e2)

    # 2. VERTEX and EAST POINT
    try:
        _, ascmc = swe.houses(jd, lat, lon)
        special["Vertex"] = float(ascmc[3])
        special["East Point"] = float(ascmc[4])
    except Exception as e:
        logger.warning("Vertex/East Point calculation failed: %s", e)

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

    except Exception as e:
        logger.warning("Part of Fortune calculation failed: %s", e)

    # 5. PART OF SPIRIT (Pars Spiritus)
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

    except Exception as e:
        logger.warning("Part of Spirit calculation failed: %s", e)

    # ── Additional Classical Arabic Lots (Hermes / Bonatti / Lilly) ──────────
    # All formulas: (ASC + A - B) % 360, reversed by day/night for some lots.
    # Reference: "Liber Astronomiae" (Bonatti, 1277), "CA" (Lilly, 1647)
    try:
        asc = houses[0]

        def _lon(name: str) -> float:
            v = planets.get(name)
            return v["longitude"] if isinstance(v, dict) else float(v or 0.0)

        sun_lon    = _lon("Sun")
        moon_lon   = _lon("Moon")
        venus_lon  = _lon("Venus")
        mars_lon   = _lon("Mars")
        jupiter_lon = _lon("Jupiter")
        saturn_lon = _lon("Saturn")
        mercury_lon = _lon("Mercury")

        # Re-determine is_diurnal using same logic as PoF above
        _desc = (asc + 180.0) % 360.0
        if _desc > asc:
            _day = sun_lon >= _desc or sun_lon <= asc
        else:
            _day = sun_lon >= _desc and sun_lon <= asc

        # Convenient helpers for lots with day/night reversal
        pof_lon = special.get("Part of Fortune", (asc + moon_lon - sun_lon) % 360.0)
        pos_lon = special.get("Part of Spirit", (asc + sun_lon - moon_lon) % 360.0)

        # Part of Eros (Love / Desire) — Hermes
        # Day: ASC + Venus - Spirit   Night: ASC + Spirit - Venus
        if _day:
            special["Part of Eros"] = (asc + venus_lon - pos_lon) % 360.0
        else:
            special["Part of Eros"] = (asc + pos_lon - venus_lon) % 360.0

        # Part of Necessity (Constraint) — Hermes
        # Day: ASC + Fortune - Mercury   Night: ASC + Mercury - Fortune
        if _day:
            special["Part of Necessity"] = (asc + pof_lon - mercury_lon) % 360.0
        else:
            special["Part of Necessity"] = (asc + mercury_lon - pof_lon) % 360.0

        # Part of Courage (Bravery) — Hermes
        # Day: ASC + Mars - Fortune   Night: ASC + Fortune - Mars
        if _day:
            special["Part of Courage"] = (asc + mars_lon - pof_lon) % 360.0
        else:
            special["Part of Courage"] = (asc + pof_lon - mars_lon) % 360.0

        # Part of Victory (Success) — Hermes
        # Day: ASC + Jupiter - Spirit   Night: ASC + Spirit - Jupiter
        if _day:
            special["Part of Victory"] = (asc + jupiter_lon - pos_lon) % 360.0
        else:
            special["Part of Victory"] = (asc + pos_lon - jupiter_lon) % 360.0

        # Part of Nemesis (Retribution / Hidden Enemies) — Hermes
        # Day: ASC + Saturn - Fortune   Night: ASC + Fortune - Saturn
        if _day:
            special["Part of Nemesis"] = (asc + saturn_lon - pof_lon) % 360.0
        else:
            special["Part of Nemesis"] = (asc + pof_lon - saturn_lon) % 360.0

        # Part of Marriage (Venus / 7th house) — Lilly
        # Day: ASC + Venus - Saturn   Night: ASC + Saturn - Venus
        if _day:
            special["Part of Marriage"] = (asc + venus_lon - saturn_lon) % 360.0
        else:
            special["Part of Marriage"] = (asc + saturn_lon - venus_lon) % 360.0

        # Part of Death — Lilly (always nocturnal formula)
        # House 8 cusp + Moon - Saturn
        h8_cusp = houses[7] if len(houses) >= 8 else (asc + 210.0) % 360.0
        special["Part of Death"] = (h8_cusp + moon_lon - saturn_lon) % 360.0

    except Exception as e:
        logger.warning("Arabic Lots calculation failed: %s", e)

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
