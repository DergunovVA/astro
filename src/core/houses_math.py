# Houses calculation (Placidus, Whole Sign)
import swisseph as swe
from typing import Dict

def calc_houses(jd: float, lat: float, lon: float, method: str = "Placidus") -> Dict[str, float]:
    if method == "Placidus":
        houses = swe.houses(jd, lat, lon)[0]
    elif method == "WholeSign":
        # Whole Sign: 12 equal 30° houses starting from 0° of the Ascendant's sign
        asc = swe.houses(jd, lat, lon)[0][0]
        asc_sign_start = int(asc / 30) * 30
        houses = [(asc_sign_start + i * 30) % 360 for i in range(12)]
    else:
        raise ValueError("Unknown house method")
    return {f"house_{i+1}": h for i, h in enumerate(houses)}
