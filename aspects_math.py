# Aspects calculation with major and minor aspects
from typing import Dict, List, Tuple

# Major aspects (most significant)
MAJOR_ASPECTS = {
    "conjunction": {"angle": 0, "orb": 8, "type": "hard"},
    "opposition": {"angle": 180, "orb": 8, "type": "hard"},
    "trine": {"angle": 120, "orb": 8, "type": "soft"},
    "square": {"angle": 90, "orb": 8, "type": "hard"},
    "sextile": {"angle": 60, "orb": 6, "type": "soft"}
}

# Minor aspects (secondary significance)
MINOR_ASPECTS = {
    "semisextile": {"angle": 30, "orb": 2, "type": "soft"},
    "semisquare": {"angle": 45, "orb": 2, "type": "hard"},
    "sesquiquadrate": {"angle": 135, "orb": 2, "type": "hard"},
    "quincunx": {"angle": 150, "orb": 2, "type": "hard"}
}

# All aspects combined (major first for priority)
ASPECTS = {**MAJOR_ASPECTS, **MINOR_ASPECTS}

# For backward compatibility
ORB = 8  # degrees (default for major aspects)

def calc_aspects(
    planets: Dict[str, float],
    include_minor: bool = True,
    min_orb: float = 1.0
) -> List[Tuple[str, str, str, float, str]]:
    """Calculate aspects between planets.
    
    Args:
        planets: Dict of planet names to longitudes (degrees)
        include_minor: If True, include minor aspects. If False, major only.
        min_orb: Filter out aspects with orb smaller than this (helps with noise)
        
    Returns:
        List of (planet1, planet2, aspect_name, orb, aspect_type) tuples
        where aspect_type is "major" or "minor"
    """
    result = []
    names = list(planets.keys())
    
    # Select aspects to check
    aspects_to_check = MAJOR_ASPECTS.copy()
    if include_minor:
        aspects_to_check.update(MINOR_ASPECTS)
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            angle = abs(planets[a] - planets[b]) % 360
            
            for asp_name, asp_config in aspects_to_check.items():
                asp_angle = asp_config["angle"]
                asp_orb = asp_config["orb"]
                asp_type = asp_config["type"]
                
                # Calculate shortest distance to aspect angle
                diff = min(abs(angle - asp_angle), abs(360 - angle - asp_angle))
                
                # Check if within orb and above minimum threshold
                if diff <= asp_orb and diff >= min_orb:
                    # Determine if aspect is major or minor
                    aspect_category = "major" if asp_name in MAJOR_ASPECTS else "minor"
                    result.append((a, b, asp_name, diff, aspect_category))
    
    return result


def classify_aspect_strength(aspect_name: str) -> str:
    """Classify aspect by strength: hard (challenging) or soft (harmonious)."""
    if aspect_name in MAJOR_ASPECTS:
        return MAJOR_ASPECTS[aspect_name]["type"]
    elif aspect_name in MINOR_ASPECTS:
        return MINOR_ASPECTS[aspect_name]["type"]
    return "neutral"


def get_aspect_meaning(aspect_name: str) -> str:
    """Get simple meaning of an aspect."""
    meanings = {
        "conjunction": "Fusion of energies",
        "opposition": "Tension and polarities",
        "trine": "Harmony and ease",
        "square": "Challenge and friction",
        "sextile": "Support and opportunity",
        "semisextile": "Minor adjustment needed",
        "semisquare": "Minor tension",
        "sesquiquadrate": "Minor struggle",
        "quincunx": "Adjustment and adaptation required"
    }
    return meanings.get(aspect_name, "Unknown aspect")
