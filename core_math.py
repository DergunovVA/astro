# Core Math Engine: Swiss Ephemeris integration
import swisseph as swe
from datetime import datetime
from typing import Dict, Any
from relocation_math import relocate_coords

def calc_natal(date: str, time: str, place: str) -> Dict[str, Any]:
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    coords = relocate_coords(place)
    lon, lat = coords["lon"], coords["lat"]
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)
    planets = {}
    for p in [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]:
        pos = swe.calc_ut(jd, p)
        planets[swe.get_planet_name(p)] = pos[0]  # только долгота
    return {
        "jd": jd,
        "planets": planets,
        "coords": {"lon": lon, "lat": lat}
    }
