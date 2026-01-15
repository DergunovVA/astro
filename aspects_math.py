# Aspects calculation
from typing import Dict, List, Tuple

ASPECTS = {
    "conjunction": 0,
    "opposition": 180,
    "trine": 120,
    "square": 90,
    "sextile": 60
}
ORB = 8  # degrees

def calc_aspects(planets: Dict[str, float]) -> List[Tuple[str, str, str, float]]:
    result = []
    names = list(planets.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            angle = abs(planets[a] - planets[b]) % 360
            for asp_name, asp_angle in ASPECTS.items():
                diff = min(abs(angle - asp_angle), abs(360 - angle - asp_angle))
                if diff <= ORB:
                    result.append((a, b, asp_name, diff))
    return result
