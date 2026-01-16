# Synastry (Relationship Astrology) Module
# Compares aspects between two natal charts

from typing import Dict, List, Any
from aspects_math import MAJOR_ASPECTS, MINOR_ASPECTS

def calculate_synastry_aspects(
    natal1_planets: Dict[str, float],
    natal2_planets: Dict[str, float],
    include_minor: bool = True,
    min_orb: float = 1.0
) -> List[Dict[str, Any]]:
    """Calculate aspects between two natal charts (synastry).
    
    Compares each planet from chart 1 with each planet from chart 2.
    This is different from traditional aspects (planet-to-planet in same chart).
    
    Args:
        natal1_planets: Dict of planet names to longitudes from person 1
        natal2_planets: Dict of planet names to longitudes from person 2
        include_minor: If True, include minor aspects
        min_orb: Filter out aspects with orb smaller than this
        
    Returns:
        List of dicts with keys: planet1, person1, planet2, person2, 
                                  aspect, orb, type, category
    """
    result = []
    
    # Select aspects to check
    aspects_to_check = MAJOR_ASPECTS.copy()
    if include_minor:
        aspects_to_check.update(MINOR_ASPECTS)
    
    for p1_name, p1_lon in natal1_planets.items():
        for p2_name, p2_lon in natal2_planets.items():
            angle = abs(p1_lon - p2_lon) % 360
            
            for asp_name, asp_config in aspects_to_check.items():
                asp_angle = asp_config["angle"]
                asp_orb = asp_config["orb"]
                asp_type = asp_config["type"]
                
                # Calculate shortest distance to aspect angle
                diff = min(abs(angle - asp_angle), abs(360 - angle - asp_angle))
                
                # Check if within orb and above minimum threshold
                if diff <= asp_orb and diff >= min_orb:
                    aspect_category = "major" if asp_name in MAJOR_ASPECTS else "minor"
                    
                    result.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "aspect": asp_name,
                        "orb": round(diff, 2),
                        "type": asp_type,  # "hard" or "soft"
                        "category": aspect_category,  # "major" or "minor"
                        "angle": round(angle, 2)
                    })
    
    return result


def calculate_composite_chart(
    natal1: Dict[str, Any],
    natal2: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate composite (midpoint) chart from two natal charts.
    
    Composite chart: Average the planets and angles between two charts.
    Used to understand the relationship as its own entity.
    
    Args:
        natal1: Natal calculation dict with planets, houses
        natal2: Natal calculation dict with planets, houses
        
    Returns:
        Composite chart with averaged planets and houses
    """
    composite = {}
    
    # Average planets
    composite_planets = {}
    for planet_name, lon1 in natal1["planets"].items():
        if planet_name in natal2["planets"]:
            lon2 = natal2["planets"][planet_name]
            # Average angle (handle circular nature)
            avg = (lon1 + lon2) / 2
            if abs(lon1 - lon2) > 180:
                avg = (avg + 180) % 360
            composite_planets[planet_name] = avg
    
    # Average houses
    composite_houses = []
    for i in range(12):
        lon1 = natal1["houses"][i]
        lon2 = natal2["houses"][i]
        # Average angle
        avg = (lon1 + lon2) / 2
        if abs(lon1 - lon2) > 180:
            avg = (avg + 180) % 360
        composite_houses.append(avg)
    
    composite = {
        "planets": composite_planets,
        "houses": composite_houses,
        "natal1_jd": natal1.get("jd"),
        "natal2_jd": natal2.get("jd"),
        "coords": {
            "lat": (natal1["coords"]["lat"] + natal2["coords"]["lat"]) / 2,
            "lon": (natal1["coords"]["lon"] + natal2["coords"]["lon"]) / 2
        }
    }
    
    return composite


def calculate_davison_chart(
    natal1: Dict[str, Any],
    natal2: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate Davison chart (midpoint in space and time).
    
    Davison chart: Midpoint chart calculated at midpoint location.
    Advanced relationship indicator, rarely used.
    
    Args:
        natal1: Natal calculation dict with planets, houses, jd
        natal2: Natal calculation dict with planets, houses, jd
        
    Returns:
        Davison chart
    """
    # Time midpoint (average JD)
    midpoint_jd = (natal1["jd"] + natal2["jd"]) / 2
    
    # Location midpoint
    midpoint_lat = (natal1["coords"]["lat"] + natal2["coords"]["lat"]) / 2
    midpoint_lon = (natal1["coords"]["lon"] + natal2["coords"]["lon"]) / 2
    
    davison = {
        "jd": midpoint_jd,
        "planets": {},  # Would need to recalculate from midpoint_jd
        "houses": {},   # Would need to recalculate from midpoint_jd
        "coords": {
            "lat": midpoint_lat,
            "lon": midpoint_lon
        },
        "note": "Requires recalculation at midpoint JD using astro_adapter.natal_calculation()"
    }
    
    return davison


def categorize_synastry_aspect(aspect: str, ast_type: str) -> str:
    """Categorize synastry aspect for interpretation.
    
    Args:
        aspect: Aspect name (e.g., "opposition")
        aspect_type: Aspect type ("hard" or "soft")
        
    Returns:
        Interpretation category
    """
    hard_aspects = ["opposition", "square", "semisquare", "sesquiquadrate"]
    soft_aspects = ["trine", "sextile", "semisextile"]
    conjunction_aspects = ["conjunction", "quincunx"]
    
    if aspect in hard_aspects:
        return "challenging"
    elif aspect in soft_aspects:
        return "harmonious"
    elif aspect in conjunction_aspects:
        return "intense"
    return "neutral"


def get_synastry_interpretation(planet1: str, planet2: str, aspect: str) -> str:
    """Get simple interpretation of a synastry aspect.
    
    Args:
        planet1: Planet from chart 1
        planet2: Planet from chart 2
        aspect: Aspect name
        
    Returns:
        Brief interpretation text
    """
    # Examples of interpretations (simplified)
    interpretations = {
        ("Sun", "Moon", "conjunction"): "Deep emotional connection and resonance",
        ("Sun", "Moon", "opposition"): "Polarities attract, potential for growth through differences",
        ("Venus", "Mars", "conjunction"): "Strong sexual attraction and chemistry",
        ("Venus", "Mars", "square"): "Sexual tension and frustration",
        ("Moon", "Moon", "conjunction"): "Emotional understanding and empathy",
        ("Venus", "Venus", "conjunction"): "Similar values and aesthetics",
        ("Saturn", "Venus", "conjunction"): "Commitment and responsibility in relationship",
        ("Jupiter", "Jupiter", "trine"): "Mutual support and growth",
    }
    
    # Try exact match
    key = (planet1, planet2, aspect)
    if key in interpretations:
        return interpretations[key]
    
    # Try planet pair (ignoring aspect)
    key = (planet1, planet2)
    pair_meanings = {
        ("Sun", "Moon"): "Core personality and emotional needs",
        ("Venus", "Mars"): "Attraction and sexual compatibility",
        ("Moon", "Moon"): "Emotional rapport",
        ("Venus", "Venus"): "Values and aesthetic alignment",
        ("Mercury", "Mercury"): "Communication style",
    }
    
    if key in pair_meanings:
        return pair_meanings[key]
    
    return f"{planet1} {aspect} {planet2} in synastry"
