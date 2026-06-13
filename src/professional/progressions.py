"""
Predictive Techniques: Secondary Progressions and Solar Arc Directions.

SECONDARY PROGRESSIONS (Day-for-a-Year method):
  - Each day after birth = one year of life.
  - Progressed chart for age N = natal chart calculated for (birth_date + N days).
  - Technique dates to Ptolemy; codified by Placidus and later astrologers.
  - Used to assess inner development, personality evolution, timing of events.

SOLAR ARC DIRECTIONS:
  - The progressed Sun's arc (degrees it has moved from natal position) is
    applied uniformly to ALL natal planet positions.
  - Solar Arc = progressed_sun_longitude − natal_sun_longitude
  - Directed planet = natal_longitude + solar_arc
  - Developed by Reinhold Ebertin (Cosmobiology, 1940s-70s).
  - Gives same timing as Secondary Progressions but treats all planets equally.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Tuple

import swisseph as swe

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _jd_from_date(dt: date | datetime) -> float:
    """Julian Day from a date or datetime (always treated as UTC noon if date-only)."""
    if isinstance(dt, datetime):
        return swe.julday(dt.year, dt.month, dt.day,
                          dt.hour + dt.minute / 60.0 + dt.second / 3600.0)
    # date-only → use noon UTC
    return swe.julday(dt.year, dt.month, dt.day, 12.0)


def _normalise_dt(d: date | datetime | str) -> date:
    if isinstance(d, str):
        return date.fromisoformat(d[:10])
    if isinstance(d, datetime):
        return d.date()
    return d


def _age_days(birth: date, target: date) -> int:
    """Integer days elapsed since birth."""
    return max(0, (target - birth).days)


def _completed_years(birth: date, target: date) -> int:
    """Completed integer years (for day-for-a-year progressed date)."""
    age = target.year - birth.year
    if (target.month, target.day) < (birth.month, birth.day):
        age -= 1
    return max(0, age)


# ─────────────────────────────────────────────────────────────────────────────
# SECONDARY PROGRESSIONS
# ─────────────────────────────────────────────────────────────────────────────

# All planet IDs we calculate
_PLANET_IDS: List[Tuple[int | None, str]] = [
    (swe.SUN,     "Sun"),
    (swe.MOON,    "Moon"),
    (swe.MERCURY, "Mercury"),
    (swe.VENUS,   "Venus"),
    (swe.MARS,    "Mars"),
    (swe.JUPITER, "Jupiter"),
    (swe.SATURN,  "Saturn"),
    (swe.URANUS,  "Uranus"),
    (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO,   "Pluto"),
    (swe.MEAN_NODE, "North Node"),
]


def _calc_planets_at_jd(jd: float) -> Dict[str, Dict[str, Any]]:
    """Return planet longitudes, speeds, and retrograde flags at given JD."""
    result: Dict[str, Dict[str, Any]] = {}
    for pid, name in _PLANET_IDS:
        try:
            raw = swe.calc_ut(jd, pid)[0]
            lon   = float(raw[0])
            speed = float(raw[3]) if len(raw) > 3 else 0.0
            retro = speed < 0 and pid not in (swe.SUN, swe.MOON, swe.MEAN_NODE)
            result[name] = {"longitude": round(lon, 4), "speed": round(speed, 6),
                            "retrograde": retro}
        except Exception as e:
            logger.debug("Skipping planet %s at JD %.2f: %s", name, jd, e)
    return result


def _calc_houses_at_jd(jd: float, lat: float, lon_geo: float,
                        system: str = "P") -> Dict[str, Any]:
    """Return house cusps and angles at given JD."""
    try:
        cusps, ascmc = swe.houses(jd, lat, lon_geo, system.encode())
        houses = {f"H{i+1}": round(cusps[i], 4) for i in range(12)}
        houses["ASC"] = round(ascmc[0], 4)
        houses["MC"]  = round(ascmc[1], 4)
        return houses
    except Exception as e:
        logger.warning("House calculation failed at JD %.2f: %s", jd, e)
        return {}


def secondary_progressions(
    birth_date: date | datetime | str,
    birth_lat: float,
    birth_lon: float,
    target_date: date | datetime | str | None = None,
    house_system: str = "P",
    include_houses: bool = True,
) -> Dict[str, Any]:
    """Calculate Secondary Progressed chart for a target date.

    Method: birth_date + N_days → progressed JD (one day = one year).

    Args:
        birth_date: Exact birth date/datetime (UTC preferred).
        birth_lat: Birth place latitude.
        birth_lon: Birth place longitude.
        target_date: Date for which to calculate progressions (default: today).
        house_system: Swiss Ephemeris house system code ('P' = Placidus, etc.).
        include_houses: Whether to calculate progressed house cusps.

    Returns:
        {
            "type": "secondary_progressions",
            "birth_date": str,
            "target_date": str,
            "age_years": float,
            "progressed_date": str,      # actual calendar date used for SE calc
            "progressed_jd": float,
            "natal_planets": {planet: {longitude, speed, retrograde}},
            "progressed_planets": {planet: {longitude, speed, retrograde,
                                             arc_from_natal, direction}},
            "progressed_sun_arc": float,  # degrees Sun has progressed
            "progressed_houses": {...},   # if include_houses=True
            "aspects_to_natal": [...],    # tight aspects (orb ≤ 1°)
        }
    """
    birth  = _normalise_dt(birth_date)
    target = _normalise_dt(target_date) if target_date else date.today()

    age_days  = _age_days(birth, target)
    age_years = age_days / 365.25

    # Progressed date = birth + completed_years DAYS (1 day = 1 year method)
    progressed_date = birth + timedelta(days=_completed_years(birth, target))

    # Use noon UTC for both JDs to avoid time-zone ambiguity
    natal_jd      = _jd_from_date(birth)
    progressed_jd = _jd_from_date(progressed_date)
    natal_planets      = _calc_planets_at_jd(natal_jd)
    progressed_planets = _calc_planets_at_jd(progressed_jd)

    # Enrich progressed planets with arc and direction label
    for name, prog in progressed_planets.items():
        natal_lon = natal_planets.get(name, {}).get("longitude", prog["longitude"])
        arc = (prog["longitude"] - natal_lon) % 360
        if arc > 180:
            arc -= 360  # signed: positive = direct motion gain
        prog["arc_from_natal"] = round(arc, 4)
        prog["natal_longitude"] = natal_lon
        prog["direction"] = "Retrograde" if prog["retrograde"] else "Direct"

    # Progressed Sun arc (key timing indicator)
    prog_sun_lon  = progressed_planets.get("Sun", {}).get("longitude", 0.0)
    natal_sun_lon = natal_planets.get("Sun", {}).get("longitude", 0.0)
    _raw_arc = (prog_sun_lon - natal_sun_lon) % 360
    prog_sun_arc  = 0.0 if _raw_arc >= 360.0 else _raw_arc

    # Houses at progressed time (using natal location — standard practice)
    prog_houses: Dict[str, Any] = {}
    if include_houses:
        prog_houses = _calc_houses_at_jd(progressed_jd, birth_lat, birth_lon, house_system)

    # Tight aspects: progressed planet → natal planet (orb ≤ 1°)
    aspects_to_natal = _find_prog_natal_aspects(progressed_planets, natal_planets, orb=1.0)

    return {
        "type": "secondary_progressions",
        "birth_date": birth.isoformat(),
        "target_date": target.isoformat(),
        "age_years": round(age_years, 2),
        "progressed_date": progressed_date.isoformat(),
        "progressed_jd": round(progressed_jd, 4),
        "natal_planets": natal_planets,
        "progressed_planets": progressed_planets,
        "progressed_sun_arc": round(prog_sun_arc, 4),
        "progressed_houses": prog_houses,
        "aspects_to_natal": aspects_to_natal,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SOLAR ARC DIRECTIONS
# ─────────────────────────────────────────────────────────────────────────────

def solar_arc_directions(
    birth_date: date | datetime | str,
    birth_lat: float,
    birth_lon: float,
    target_date: date | datetime | str | None = None,
) -> Dict[str, Any]:
    """Calculate Solar Arc Directed chart.

    The Sun's secondary progressed arc is applied uniformly to all natal planets.
    Directed planet longitude = natal_longitude + solar_arc.

    This technique is equivalent to moving every natal planet by the same amount
    the Sun has progressed — treating the entire chart as a unified field.

    Args:
        birth_date: Birth date/datetime (UTC).
        birth_lat: Birth latitude.
        birth_lon: Birth longitude.
        target_date: Target date (default: today).

    Returns:
        {
            "type": "solar_arc_directions",
            "birth_date": str,
            "target_date": str,
            "age_years": float,
            "solar_arc": float,          # degrees the Sun has moved by progression
            "natal_planets": {...},
            "directed_planets": {planet: {longitude, arc, natal_longitude}},
            "aspects_to_natal": [...],   # tight aspects directed → natal (orb ≤ 1°)
            "aspects_between_directed": [...],  # tight aspects within directed chart
        }
    """
    birth  = _normalise_dt(birth_date)
    target = _normalise_dt(target_date) if target_date else date.today()

    age_days  = _age_days(birth, target)
    age_years = age_days / 365.25

    # Progressed date = birth + completed_years DAYS (1 day = 1 year method)
    progressed_date = birth + timedelta(days=_completed_years(birth, target))

    natal_jd      = _jd_from_date(birth)
    progressed_jd = _jd_from_date(progressed_date)

    natal_planets = _calc_planets_at_jd(natal_jd)

    # Solar arc = progressed Sun − natal Sun (always measured in direct direction)
    try:
        prog_sun_lon = round(float(swe.calc_ut(progressed_jd, swe.SUN)[0][0]), 4)
    except Exception as e:
        logger.warning("Could not compute progressed Sun at JD %.2f: %s", progressed_jd, e)
        prog_sun_lon = natal_planets.get("Sun", {}).get("longitude", 0.0)

    natal_sun_lon = natal_planets.get("Sun", {}).get("longitude", 0.0)
    _raw_arc = (prog_sun_lon - natal_sun_lon) % 360
    solar_arc = 0.0 if _raw_arc >= 360.0 else _raw_arc

    # Apply arc to every natal planet
    directed_planets: Dict[str, Dict[str, Any]] = {}
    for name, natal_data in natal_planets.items():
        natal_lon = natal_data["longitude"]
        directed_lon = (natal_lon + solar_arc) % 360
        directed_planets[name] = {
            "longitude": round(directed_lon, 4),
            "natal_longitude": natal_lon,
            "arc": round(solar_arc, 4),
        }

    # Aspects: directed → natal (orb ≤ 1°)
    aspects_to_natal = _find_directed_natal_aspects(directed_planets, natal_planets, orb=1.0)

    # Aspects within directed chart itself (orb ≤ 1°)
    aspects_within = _find_directed_internal_aspects(directed_planets, orb=1.0)

    return {
        "type": "solar_arc_directions",
        "birth_date": birth.isoformat(),
        "target_date": target.isoformat(),
        "age_years": round(age_years, 2),
        "solar_arc": round(solar_arc, 4),
        "natal_planets": natal_planets,
        "directed_planets": directed_planets,
        "aspects_to_natal": aspects_to_natal,
        "aspects_within_directed": aspects_within,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ASPECT FINDING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_ASPECT_ANGLES = {
    "Conjunction":  0,
    "Opposition":   180,
    "Trine":        120,
    "Square":       90,
    "Sextile":      60,
    "Quincunx":     150,
    "Semi-sextile": 30,
    "Semi-square":  45,
    "Sesquiquadrate": 135,
}


def _angular_diff(a: float, b: float) -> float:
    """Shortest arc between two longitudes (0–180°)."""
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def _find_aspects(
    from_planets: Dict[str, Dict[str, Any]],
    to_planets: Dict[str, Dict[str, Any]],
    orb: float,
    label_from: str = "prog",
    label_to: str = "natal",
) -> List[Dict[str, Any]]:
    aspects = []
    for p1, d1 in from_planets.items():
        lon1 = d1["longitude"]
        for p2, d2 in to_planets.items():
            if p1 == p2 and label_from == label_to:
                continue
            lon2 = d2["longitude"]
            diff = _angular_diff(lon1, lon2)
            for asp_name, angle in _ASPECT_ANGLES.items():
                delta = abs(diff - angle)
                if delta <= orb:
                    aspects.append({
                        f"{label_from}_planet": p1,
                        f"{label_to}_planet":   p2,
                        "aspect":  asp_name,
                        "angle":   angle,
                        "orb":     round(delta, 3),
                        f"{label_from}_longitude": round(lon1, 4),
                        f"{label_to}_longitude":   round(lon2, 4),
                    })
    return sorted(aspects, key=lambda x: x["orb"])


def _find_prog_natal_aspects(
    progressed: Dict[str, Dict], natal: Dict[str, Dict], orb: float
) -> List[Dict]:
    return _find_aspects(progressed, natal, orb, "progressed", "natal")


def _find_directed_natal_aspects(
    directed: Dict[str, Dict], natal: Dict[str, Dict], orb: float
) -> List[Dict]:
    return _find_aspects(directed, natal, orb, "directed", "natal")


def _find_directed_internal_aspects(
    directed: Dict[str, Dict], orb: float
) -> List[Dict]:
    planets = list(directed.items())
    aspects = []
    for i, (p1, d1) in enumerate(planets):
        for p2, d2 in planets[i+1:]:
            diff = _angular_diff(d1["longitude"], d2["longitude"])
            for asp_name, angle in _ASPECT_ANGLES.items():
                delta = abs(diff - angle)
                if delta <= orb:
                    aspects.append({
                        "planet_1": p1,
                        "planet_2": p2,
                        "aspect":   asp_name,
                        "angle":    angle,
                        "orb":      round(delta, 3),
                    })
    return sorted(aspects, key=lambda x: x["orb"])
