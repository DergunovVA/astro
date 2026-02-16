# ⚠️ DEPRECATED: This file is OBSOLETE and not used in production
#
# Status: DEPRECATED (kept for reference only)
# Replaced by: src/modules/astro_adapter.py
# Reason: Old implementation with string-based API, replaced with datetime-based
#
# TODO: Remove in v0.2 cleanup
#
# Core Math Engine: Swiss Ephemeris integration (DEPRECATED)
import swisseph as swe
from datetime import datetime
from typing import Dict, Any
from relocation_math import relocate_coords


def calc_natal(date: str, time: str, place: str) -> Dict[str, Any]:
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    coords = relocate_coords(place)
    lon, lat = coords["lon"], coords["lat"]
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
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
        pos = swe.calc_ut(jd, p)
        planets[swe.get_planet_name(p)] = pos[0]  # только долгота
    return {"jd": jd, "planets": planets, "coords": {"lon": lon, "lat": lat}}
