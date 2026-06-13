"""
Accidental Dignities - Positional Strength in the Chart

Unlike essential dignities (based on zodiac sign), accidental dignities
measure planetary strength based on chart position and motion.

Based on:
- William Lilly's "Christian Astrology" (1647)
- Traditional Medieval astrology
- Ptolemaic doctrine
"""

from typing import Dict, Any, Optional, List

# HOUSE STRENGTH
# Angular houses (1, 4, 7, 10) = strongest (+MODIFIER points)
# Succedent houses (2, 5, 8, 11) = moderate power (+2)
# Cadent houses (3, 6, 9, 12) = weakest (-2)
HOUSE_STRENGTH = {
    1: 5,  # Ascendant - most powerful angle (self, vitality)
    10: 5,  # Midheaven - career, reputation, most elevated
    7: 4,  # Descendant - partnerships, others (slightly less than ASC)
    4: 4,  # IC - roots, home, foundation (slightly less than MC)
    2: 2,  # Succedent - resources, values
    5: 2,  # Succedent - creativity, children
    8: 2,  # Succedent - transformation, shared resources
    11: 2,  # Succedent - community, hopes
    3: -2,  # Cadent - communication, siblings (weak)
    6: -2,  # Cadent - health, service (traditionally "bad house")
    9: -2,  # Cadent - philosophy, travel
    12: -2,  # Cadent - hidden, subconscious (traditionally "bad house")
}

# MOTION STRENGTH
# Direct = normal, healthy motion (+4)
# Retrograde = reversed, weakened (-5)
# Note: Sun and Moon are never retrograde
MOTION_STRENGTH = {
    "direct": 4,
    "retrograde": -5,
    "stationary": 0,  # About to change direction (neither good nor bad)
}

# SPEED VARIATIONS
# Planets moving faster than average = vigorous, active (+2)
# Planets moving slower than average = sluggish, weak (-2)
# Average speeds (degrees per day) from ephemeris observations:
AVERAGE_SPEEDS = {
    "Sun": 0.9856,  # ~1°/day, very regular
    "Moon": 13.176,  # ~13°/day, fastest visible body
    "Mercury": 1.0,  # Varies widely: 0-2.2°/day (retrograde to swift)
    "Venus": 1.0,  # Varies: 0-1.25°/day
    "Mars": 0.524,  # Varies: 0-0.8°/day
    "Jupiter": 0.083,  # ~5'/day = 0.083°/day
    "Saturn": 0.033,  # ~2'/day = 0.033°/day
    "Uranus": 0.0117,  # Very slow
    "Neptune": 0.0067,  # Very slow
    "Pluto": 0.0039,  # Extremely slow
}

# ORIENTAL/OCCIDENTAL (only for classical planets)
# Mercury & Venus: Oriental (rising before Sun) = +2
# Mars, Jupiter, Saturn: Occidental (setting after Sun) = +2
# "Oriental" = East of Sun (rises before Sun)
# "Occidental" = West of Sun (sets after Sun)


def calculate_accidental_dignity(
    planet: str,
    house: int,
    is_retrograde: bool,
    speed: float,
    longitude: Optional[float] = None,
    sun_longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate accidental dignity score for a planet.

    Args:
        planet: Planet name
        house: House number (1-12)
        is_retrograde: Whether planet is in retrograde motion
        speed: Planet's speed in degrees/day
        longitude: Planet's longitude (optional, for oriental/occidental)
        sun_longitude: Sun's longitude (optional, for oriental/occidental)

    Returns:
        dict with:
        {
            "score": int (-7 to +11),
            "house_strength": int,
            "motion_strength": int,
            "speed_strength": int,
            "oriental_occidental": int,
            "strength_level": str
        }
    """
    result = {
        "score": 0,
        "house_strength": 0,
        "motion_strength": 0,
        "speed_strength": 0,
        "oriental_occidental": 0,
        "strength_level": "Neutral",
    }

    # 1. House Strength
    result["house_strength"] = HOUSE_STRENGTH.get(house, 0)
    result["score"] += result["house_strength"]

    # 2. Motion Strength (Direct vs Retrograde)
    # Sun, Moon, and North Node are never retrograde
    if planet in ["Sun", "Moon", "North Node"]:
        result["motion_strength"] = MOTION_STRENGTH["direct"]
    else:
        if is_retrograde:
            result["motion_strength"] = MOTION_STRENGTH["retrograde"]
        else:
            result["motion_strength"] = MOTION_STRENGTH["direct"]

    result["score"] += result["motion_strength"]

    # 3. Speed Strength (Swift vs Slow)
    if planet in AVERAGE_SPEEDS:
        avg_speed = AVERAGE_SPEEDS[planet]
        abs_speed = abs(speed)  # Use absolute value (retrograde = negative)

        # Swift in motion (+2): Moving > 120% of average
        if abs_speed > avg_speed * 1.2:
            result["speed_strength"] = 2
        # Slow in motion (-2): Moving < 80% of average
        elif abs_speed < avg_speed * 0.8:
            result["speed_strength"] = -2
        else:
            result["speed_strength"] = 0

        result["score"] += result["speed_strength"]

    # 4. Oriental/Occidental (only if both longitudes provided)
    if longitude is not None and sun_longitude is not None:
        # diff = how many degrees the planet is AHEAD of the Sun in zodiac order
        diff = (longitude - sun_longitude) % 360

        # Oriental = rises before Sun = planet is BEHIND the Sun in zodiac
        # (diff near 270-360°, i.e., planet has lower ecliptic longitude)
        # Occidental = sets after Sun = planet is AHEAD of the Sun
        # (diff near 0-90°, i.e., planet has higher ecliptic longitude)

        if planet in ["Mercury", "Venus"]:
            # Inner planets: Oriental (morning star, behind Sun) is favorable per Lilly
            if diff >= 270:
                result["oriental_occidental"] = 2  # Oriental
        elif planet in ["Mars", "Jupiter", "Saturn"]:
            # Outer classical planets: Oriental (0-180° ahead of Sun) is favorable per Lilly
            if 0 < diff < 180:
                result["oriental_occidental"] = 2  # Oriental

        result["score"] += result["oriental_occidental"]

    # 5. Determine strength level
    score = result["score"]
    if score >= 8:
        result["strength_level"] = "Very Strong"
    elif score >= 4:
        result["strength_level"] = "Strong"
    elif score >= -2:
        result["strength_level"] = "Neutral"
    elif score >= -6:
        result["strength_level"] = "Weak"
    else:
        result["strength_level"] = "Very Weak"

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CAZIMI / COMBUST / UNDER BEAMS  (Lilly, CA p.113-116)
# ─────────────────────────────────────────────────────────────────────────────

CAZIMI_ORB   = 17 / 60   # 0°17' in degrees
COMBUST_ORB  = 8.5       # 8°30'
BEAMS_ORB    = 17.0      # 17°00'

SOLAR_CONDITION_SCORES = {
    "cazimi":      +5,
    "combust":     -5,
    "under_beams": -4,
    "free":         0,
}


def calc_solar_condition(
    planet: str,
    planet_longitude: float,
    sun_longitude: float,
) -> Dict[str, Any]:
    """Determine if a planet is Cazimi, Combust, Under Beams, or Free.

    Returns:
        {"condition": str, "orb": float, "score": int}
    """
    if planet in ("Sun", "Moon"):
        return {"condition": "free", "orb": 0.0, "score": 0}

    diff = abs(planet_longitude - sun_longitude)
    if diff > 180:
        diff = 360 - diff

    if diff <= CAZIMI_ORB:
        condition = "cazimi"
    elif diff <= COMBUST_ORB:
        condition = "combust"
    elif diff <= BEAMS_ORB:
        condition = "under_beams"
    else:
        condition = "free"

    return {
        "condition": condition,
        "orb": round(diff, 4),
        "score": SOLAR_CONDITION_SCORES[condition],
    }


# ─────────────────────────────────────────────────────────────────────────────
# PEREGRINE  (Lilly CA p.114)
# ─────────────────────────────────────────────────────────────────────────────

# Import here to avoid circular module dependency
from core.dignities import (  # noqa: E402
    DOMICILE, EXALTATION, TRIPLICITY, SIGN_TO_ELEMENT,
    get_planet_sign,
)

# Ptolemaic Terms (Chaldean order per Lilly)
TERMS: Dict[str, List] = {
    "Aries":       [{"p":"Jupiter","f":0,"t":6}, {"p":"Venus","f":6,"t":14},
                    {"p":"Mercury","f":14,"t":21},{"p":"Mars","f":21,"t":26},
                    {"p":"Saturn","f":26,"t":30}],
    "Taurus":      [{"p":"Venus","f":0,"t":8},   {"p":"Mercury","f":8,"t":15},
                    {"p":"Jupiter","f":15,"t":22},{"p":"Saturn","f":22,"t":26},
                    {"p":"Mars","f":26,"t":30}],
    "Gemini":      [{"p":"Mercury","f":0,"t":7}, {"p":"Jupiter","f":7,"t":14},
                    {"p":"Venus","f":14,"t":21},  {"p":"Saturn","f":21,"t":25},
                    {"p":"Mars","f":25,"t":30}],
    "Cancer":      [{"p":"Mars","f":0,"t":6},    {"p":"Jupiter","f":6,"t":13},
                    {"p":"Mercury","f":13,"t":20},{"p":"Venus","f":20,"t":27},
                    {"p":"Saturn","f":27,"t":30}],
    "Leo":         [{"p":"Jupiter","f":0,"t":6}, {"p":"Venus","f":6,"t":11},
                    {"p":"Saturn","f":11,"t":18},{"p":"Mercury","f":18,"t":24},
                    {"p":"Mars","f":24,"t":30}],
    "Virgo":       [{"p":"Mercury","f":0,"t":7}, {"p":"Venus","f":7,"t":17},
                    {"p":"Jupiter","f":17,"t":21},{"p":"Mars","f":21,"t":28},
                    {"p":"Saturn","f":28,"t":30}],
    "Libra":       [{"p":"Saturn","f":0,"t":6},  {"p":"Mercury","f":6,"t":14},
                    {"p":"Jupiter","f":14,"t":21},{"p":"Venus","f":21,"t":28},
                    {"p":"Mars","f":28,"t":30}],
    "Scorpio":     [{"p":"Mars","f":0,"t":7},    {"p":"Jupiter","f":7,"t":11},
                    {"p":"Venus","f":11,"t":19},  {"p":"Saturn","f":19,"t":24},
                    {"p":"Mercury","f":24,"t":30}],
    "Sagittarius": [{"p":"Jupiter","f":0,"t":12},{"p":"Venus","f":12,"t":17},
                    {"p":"Mercury","f":17,"t":21},{"p":"Saturn","f":21,"t":26},
                    {"p":"Mars","f":26,"t":30}],
    "Capricorn":   [{"p":"Mercury","f":0,"t":7}, {"p":"Jupiter","f":7,"t":14},
                    {"p":"Venus","f":14,"t":22},  {"p":"Saturn","f":22,"t":26},
                    {"p":"Mars","f":26,"t":30}],
    "Aquarius":    [{"p":"Mercury","f":0,"t":7}, {"p":"Venus","f":7,"t":13},
                    {"p":"Jupiter","f":13,"t":20},{"p":"Mars","f":20,"t":25},
                    {"p":"Saturn","f":25,"t":30}],
    "Pisces":      [{"p":"Venus","f":0,"t":12},  {"p":"Jupiter","f":12,"t":16},
                    {"p":"Mercury","f":16,"t":19},{"p":"Mars","f":19,"t":28},
                    {"p":"Saturn","f":28,"t":30}],
}

# Chaldean face (decanate) sequence, repeating every 7
_CHALDEAN = ["Mars","Sun","Venus","Mercury","Moon","Saturn","Jupiter"]


def _get_term_ruler(longitude: float) -> Optional[str]:
    sign = get_planet_sign(longitude)
    deg  = longitude % 30
    for t in TERMS.get(sign, []):
        if t["f"] <= deg < t["t"]:
            return t["p"]
    return None


def _get_face_ruler(longitude: float) -> str:
    return _CHALDEAN[int(longitude / 10) % 7]


def is_peregrine(planet: str, longitude: float, is_day: bool = True) -> bool:
    """Return True if planet has NO essential dignity at this longitude.

    Checks: Rulership, Exaltation (whole sign), Triplicity, Term, Face.
    Only applies to classical 7 planets.
    """
    if planet not in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"):
        return False

    sign = get_planet_sign(longitude)

    if sign in DOMICILE.get(planet, []):
        return False
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return False

    element = SIGN_TO_ELEMENT.get(sign)
    if element:
        trip = TRIPLICITY[element]
        ruler_key = "day" if is_day else "night"
        if trip.get(ruler_key) == planet or trip.get("participatory") == planet:
            return False

    if _get_term_ruler(longitude) == planet:
        return False
    if _get_face_ruler(longitude) == planet:
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# HAYZ  (Lilly CA p.115)
# ─────────────────────────────────────────────────────────────────────────────

_MASCULINE_SIGNS = {"Aries","Gemini","Leo","Libra","Sagittarius","Aquarius"}
_FEMININE_SIGNS  = {"Taurus","Cancer","Virgo","Scorpio","Capricorn","Pisces"}
_DIURNAL  = {"Sun","Jupiter","Saturn"}
_NOCTURNAL = {"Moon","Venus","Mars"}


def is_in_hayz(
    planet: str,
    longitude: float,
    is_above_horizon: bool,
    is_day: bool,
    sun_longitude: Optional[float] = None,
) -> bool:
    """Return True if planet is in hayz (all three sect conditions met).

    Conditions (all required):
    1. Planet sect matches chart sect (diurnal/day or nocturnal/night)
    2. Diurnal planet above horizon; nocturnal planet below horizon
    3. Diurnal planet in masculine sign; nocturnal in feminine sign
    """
    if planet not in _DIURNAL | _NOCTURNAL | {"Mercury"}:
        return False

    sign = get_planet_sign(longitude)

    if planet == "Mercury":
        if sun_longitude is not None:
            diff = (longitude - sun_longitude) % 360
            planet_diurnal = diff >= 270  # oriental = morning star = diurnal
        else:
            planet_diurnal = True
    else:
        planet_diurnal = planet in _DIURNAL

    if planet_diurnal != is_day:
        return False
    if planet_diurnal and not is_above_horizon:
        return False
    if not planet_diurnal and is_above_horizon:
        return False
    if planet_diurnal and sign not in _MASCULINE_SIGNS:
        return False
    if not planet_diurnal and sign not in _FEMININE_SIGNS:
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED TOTAL DIGNITY
# ─────────────────────────────────────────────────────────────────────────────


def get_total_dignity(essential: Dict, accidental: Dict) -> Dict[str, Any]:
    """Combine essential and accidental dignities for total planetary strength.

    Args:
        essential: Result from calculate_essential_dignity()
        accidental: Result from calculate_accidental_dignity()

    Returns:
        dict with combined score and overall assessment
    """
    total_score = essential.get("score", 0) + accidental.get("score", 0)

    if total_score >= 15:
        overall = "Extremely Powerful"
    elif total_score >= 8:
        overall = "Very Strong"
    elif total_score >= 3:
        overall = "Strong"
    elif total_score >= -2:
        overall = "Neutral"
    elif total_score >= -7:
        overall = "Weak"
    elif total_score >= -12:
        overall = "Very Weak"
    else:
        overall = "Extremely Debilitated"

    return {
        "essential_score": essential.get("score", 0),
        "accidental_score": accidental.get("score", 0),
        "total_score": total_score,
        "overall_strength": overall,
        "essential_details": essential,
        "accidental_details": accidental,
    }
