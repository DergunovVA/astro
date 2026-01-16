# Houses calculation (Placidus, Whole Sign)
import swisseph as swe
from typing import Dict

def calc_houses(jd: float, lat: float, lon: float, method: str = "Placidus") -> Dict[str, float]:
    if method == "Placidus":
        houses = swe.houses(jd, lat, lon)[0]
    elif method == "WholeSign":
        # Whole Sign: 12 equal houses from Ascendant
        asc = swe.houses(jd, lat, lon)[0][0]
        houses = [(asc + i * 30) % 360 for i in range(12)]
    else:
        raise ValueError("Unknown house method")
    return {f"house_{i+1}": h for i, h in enumerate(houses)}
