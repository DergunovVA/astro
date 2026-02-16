"""
Essential and Accidental Dignities for Classical Astrology.

Based on traditional dignities (Ptolemy, Lilly) and modern rulerships.

References:
- William Lilly's "Christian Astrology" (1647)
- Ptolemy's "Tetrabiblos"
"""

from typing import Dict

# Zodiac signs (0-11 index)
ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


# ESSENTIAL DIGNITIES TABLES
# ===========================

# Domicile (Rulership) - планета "дома", сильная позиция (+5 points)
# Modern rulerships include Uranus, Neptune, Pluto
DOMICILE = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"],
    "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"],  # Traditional + modern co-ruler
    "Jupiter": ["Sagittarius", "Pisces"],  # Traditional + modern co-ruler
    "Saturn": ["Capricorn", "Aquarius"],  # Traditional + modern co-ruler
    "Uranus": ["Aquarius"],  # Modern ruler
    "Neptune": ["Pisces"],  # Modern ruler
    "Pluto": ["Scorpio"],  # Modern ruler
}

# Exaltation - планета возвышена, очень сильна (+4 points)
# Traditional exaltations with specific degrees
EXALTATION = {
    "Sun": ("Aries", 19),  # (sign, degree)
    "Moon": ("Taurus", 3),
    "Mercury": ("Virgo", 15),  # Some say Aquarius 15°
    "Venus": ("Pisces", 27),
    "Mars": ("Capricorn", 28),
    "Jupiter": ("Cancer", 15),
    "Saturn": ("Libra", 21),
    "Uranus": ("Scorpio", 0),  # Modern
    "Neptune": ("Cancer", 0),  # Modern (disputed)
    "Pluto": ("Aries", 0),  # Modern (disputed)
}

# Detriment (Exile) - планета в изгнании, слаба (-5 points)
# Opposite sign of domicile
DETRIMENT = {
    "Sun": ["Aquarius"],
    "Moon": ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"],
    "Venus": ["Aries", "Scorpio"],
    "Mars": ["Libra", "Taurus"],
    "Jupiter": ["Gemini", "Virgo"],
    "Saturn": ["Cancer", "Leo"],
    "Uranus": ["Leo"],
    "Neptune": ["Virgo"],
    "Pluto": ["Taurus"],
}

# Fall - планета в падении, очень слаба (-4 points)
# Opposite sign of exaltation
FALL = {
    "Sun": ("Libra", 19),
    "Moon": ("Scorpio", 3),
    "Mercury": ("Pisces", 15),
    "Venus": ("Virgo", 27),
    "Mars": ("Cancer", 28),
    "Jupiter": ("Capricorn", 15),
    "Saturn": ("Aries", 21),
    "Uranus": ("Taurus", 0),
    "Neptune": ("Capricorn", 0),
    "Pluto": ("Libra", 0),
}

# Triplicity (Element rulerships) - by day/night
# +3 points for participating ruler
TRIPLICITY = {
    # Fire signs (Aries, Leo, Sagittarius)
    "Fire": {"day": "Sun", "night": "Jupiter", "participatory": "Saturn"},
    # Earth signs (Taurus, Virgo, Capricorn)
    "Earth": {"day": "Venus", "night": "Moon", "participatory": "Mars"},
    # Air signs (Gemini, Libra, Aquarius)
    "Air": {"day": "Saturn", "night": "Mercury", "participatory": "Jupiter"},
    # Water signs (Cancer, Scorpio, Pisces)
    "Water": {"day": "Venus", "night": "Mars", "participatory": "Moon"},
}

SIGN_TO_ELEMENT = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}


# HELPER FUNCTIONS
# ================


def get_planet_sign(longitude: float) -> str:
    """Get zodiac sign from ecliptic longitude (0-360°)."""
    sign_index = int(longitude / 30)
    return ZODIAC_SIGNS[sign_index % 12]


def get_planet_degree_in_sign(longitude: float) -> float:
    """Get degree within sign (0-30°)."""
    return longitude % 30


def is_day_chart(sun_longitude: float, asc_longitude: float) -> bool:
    """
    Determine if chart is diurnal (day) or nocturnal (night).

    Day chart: Sun above horizon (between ASC and DESC)
    Night chart: Sun below horizon

    Args:
        sun_longitude: Sun's ecliptic longitude (0-360°)
        asc_longitude: Ascendant longitude (0-360°)

    Returns:
        True if day chart, False if night chart
    """
    desc_longitude = (asc_longitude + 180) % 360

    # Check if Sun is in upper hemisphere (above horizon)
    if asc_longitude < desc_longitude:
        # Normal case: ASC < DESC (e.g., 30° to 210°)
        return asc_longitude <= sun_longitude <= desc_longitude
    else:
        # Wrapping case: ASC > DESC (e.g., 330° to 150°)
        return sun_longitude >= asc_longitude or sun_longitude <= desc_longitude


def calculate_essential_dignity(
    planet: str, longitude: float, is_day_chart: bool = True
) -> Dict:
    """
    Calculate essential dignity score for a planet.

    Args:
        planet: Planet name (e.g., "Sun", "Moon", "Mars")
        longitude: Ecliptic longitude (0-360°)
        is_day_chart: Whether it's a day chart (Sun above horizon)

    Returns:
        dict with dignity information:
        {
            "sign": "Aries",
            "degree_in_sign": 15.5,
            "domicile": True/False,
            "exaltation": True/False,
            "detriment": True/False,
            "fall": True/False,
            "triplicity": "day"/"night"/"participatory"/None,
            "score": int (-5 to +5),
            "dignity_level": "Very Strong"/"Strong"/"Neutral"/"Weak"/"Very Weak"
        }
    """
    sign = get_planet_sign(longitude)
    degree = get_planet_degree_in_sign(longitude)

    dignity_info = {
        "sign": sign,
        "degree_in_sign": round(degree, 2),
        "domicile": False,
        "exaltation": False,
        "detriment": False,
        "fall": False,
        "triplicity": None,
        "score": 0,
        "dignity_level": "Neutral",
    }

    # Check Domicile (+5)
    if planet in DOMICILE and sign in DOMICILE[planet]:
        dignity_info["domicile"] = True
        dignity_info["score"] += 5

    # Check Exaltation (+4)
    # Exact degree gives full points, within 5° gives partial
    if planet in EXALTATION:
        exalt_sign, exalt_degree = EXALTATION[planet]
        if sign == exalt_sign:
            degree_diff = abs(degree - exalt_degree)
            if degree_diff <= 5:  # Within 5° orb
                dignity_info["exaltation"] = True
                # Full points if exact, scaled down by distance
                dignity_info["score"] += max(2, 4 - int(degree_diff))

    # Check Detriment (-5)
    if planet in DETRIMENT and sign in DETRIMENT[planet]:
        dignity_info["detriment"] = True
        dignity_info["score"] -= 5

    # Check Fall (-4)
    if planet in FALL:
        fall_sign, fall_degree = FALL[planet]
        if sign == fall_sign:
            degree_diff = abs(degree - fall_degree)
            if degree_diff <= 5:
                dignity_info["fall"] = True
                dignity_info["score"] -= max(2, 4 - int(degree_diff))

    # Check Triplicity (+3 day ruler, +2 night ruler, +1 participatory)
    element = SIGN_TO_ELEMENT.get(sign)
    if element and element in TRIPLICITY:
        trip = TRIPLICITY[element]
        if planet == trip["day"] and is_day_chart:
            dignity_info["triplicity"] = "day"
            dignity_info["score"] += 3
        elif planet == trip["night"] and not is_day_chart:
            dignity_info["triplicity"] = "night"
            dignity_info["score"] += 2
        elif planet == trip["participatory"]:
            dignity_info["triplicity"] = "participatory"
            dignity_info["score"] += 1

    # Determine dignity level
    score = dignity_info["score"]
    if score >= 5:
        dignity_info["dignity_level"] = "Very Strong"
    elif score >= 3:
        dignity_info["dignity_level"] = "Strong"
    elif score >= -2:
        dignity_info["dignity_level"] = "Neutral"
    elif score >= -4:
        dignity_info["dignity_level"] = "Weak"
    else:
        dignity_info["dignity_level"] = "Very Weak"

    return dignity_info


def get_dispositor(planet_sign: str) -> str:
    """
    Get the dispositor (ruler) of a sign.
    Returns modern ruler by default.

    Args:
        planet_sign: Sign name (e.g., "Aries", "Scorpio")

    Returns:
        Dispositor planet name (e.g., "Mars", "Pluto")
    """
    # Build reverse lookup: sign -> ruler
    sign_rulers = {}

    for planet, signs in DOMICILE.items():
        for sign in signs:
            # Prefer modern rulers (they come later in iteration)
            sign_rulers[sign] = planet

    return sign_rulers.get(planet_sign, "Unknown")


def get_dispositor_chain(
    planets_data: Dict[str, float], max_depth: int = 10
) -> Dict[str, list]:
    """
    Calculate dispositor chains for all planets.

    Args:
        planets_data: Dict of {planet_name: longitude}
        max_depth: Maximum chain depth (to avoid infinite loops)

    Returns:
        Dict of {planet_name: [dispositor1, dispositor2, ...]}

    Example:
        Mars in Cancer -> Moon (dispositor)
        Moon in Capricorn -> Saturn (dispositor)
        Saturn in Aries -> Mars (back to start - mutual reception!)
    """
    chains = {}

    for planet, longitude in planets_data.items():
        chain = []
        current_planet = planet
        visited = set()

        for _ in range(max_depth):
            if current_planet in visited:
                # Cycle detected (mutual reception or final dispositor)
                chain.append(f"{current_planet} (cycle)")
                break

            visited.add(current_planet)
            current_sign = get_planet_sign(planets_data.get(current_planet, longitude))
            dispositor = get_dispositor(current_sign)

            if dispositor == "Unknown" or dispositor == current_planet:
                # Planet in its own sign (final dispositor)
                break

            chain.append(dispositor)
            current_planet = dispositor

        chains[planet] = chain

    return chains


def find_mutual_receptions(planets_data: Dict[str, float]) -> list:
    """
    Find mutual receptions (planets in each other's signs).

    Args:
        planets_data: Dict of {planet_name: longitude}

    Returns:
        List of tuples: [(planet1, planet2, reception_type), ...]
        reception_type: "mutual" (both in domicile) or "mixed" (one in domicile)

    Example:
        Venus in Aries (ruled by Mars) + Mars in Taurus (ruled by Venus)
        = Mutual Reception by domicile
    """
    receptions = []
    planet_signs = {p: get_planet_sign(lon) for p, lon in planets_data.items()}

    planets_list = list(planets_data.keys())

    for i, planet1 in enumerate(planets_list):
        for planet2 in planets_list[i + 1 :]:
            sign1 = planet_signs[planet1]
            sign2 = planet_signs[planet2]

            # Check if planet1 rules sign2 AND planet2 rules sign1
            ruler_of_sign1 = get_dispositor(sign1)
            ruler_of_sign2 = get_dispositor(sign2)

            if ruler_of_sign1 == planet2 and ruler_of_sign2 == planet1:
                # Determine type
                p1_in_domicile = planet1 in DOMICILE and sign1 in DOMICILE[planet1]
                p2_in_domicile = planet2 in DOMICILE and sign2 in DOMICILE[planet2]

                if p1_in_domicile and p2_in_domicile:
                    reception_type = "mutual_domicile"
                else:
                    reception_type = "mixed"

                receptions.append((planet1, planet2, reception_type))

    return receptions
