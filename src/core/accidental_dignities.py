"""
Accidental Dignities - Positional Strength in the Chart

Unlike essential dignities (based on zodiac sign), accidental dignities
measure planetary strength based on chart position and motion.

Based on:
- William Lilly's "Christian Astrology" (1647)
- Traditional Medieval astrology
- Ptolemaic doctrine
"""

from typing import Dict, Any, Optional

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
        # Calculate angular distance (shortest path in zodiac)
        diff = (longitude - sun_longitude) % 360

        # Oriental: planet rises before Sun (90° to 180° behind Sun in zodiac)
        # Occidental: planet sets after Sun (90° to 180° ahead of Sun)

        if planet in ["Mercury", "Venus"]:
            # Inner planets: Oriental is favorable
            if 90 <= diff <= 180:
                result["oriental_occidental"] = 2  # Oriental (rising before Sun)
        elif planet in ["Mars", "Jupiter", "Saturn"]:
            # Outer classical planets: Occidental is favorable
            if 180 <= diff <= 270:
                result["oriental_occidental"] = 2  # Occidental (setting after Sun)

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


def get_total_dignity(essential: Dict, accidental: Dict) -> Dict[str, Any]:
    """
    Combine essential and accidental dignities for total planetary strength.

    Args:
        essential: Result from calculate_essential_dignity()
        accidental: Result from calculate_accidental_dignity()

    Returns:
        dict with combined score and overall assessment
    """
    total_score = essential.get("score", 0) + accidental.get("score", 0)

    # Total dignity scale:
    # +15 to +28: Extremely Powerful (domicile + angular + direct + swift)
    # +8 to +14: Very Strong
    # +3 to +7: Strong
    # -2 to +2: Neutral
    # -7 to -3: Weak
    # -12 to -8: Very Weak
    # Below -12: Extremely Debilitated

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
