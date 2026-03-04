"""
Horary Astrology - Standalone Functions

Traditional horary methods for answering specific questions.
Based on William Lilly's "Christian Astrology" (1647).

Techniques implemented:
- Time to perfection (applying/separating aspect timing)
- Void of Course Moon (no major aspects before sign change)
- Radicality check (ASC degree 3-27°, Saturn restrictions)
- Mutual receptions (domicile, traditional rulers)
- Translation of light (3rd planet connects two significators)
- Collection of light (both significators apply to 3rd planet)
- Prohibition (3rd planet intercepts applying aspect)
- Refrenation (planet turns retrograde before perfecting aspect)
- Reception quality (friendly/hostile/neutral reception between planets)
- Combust / Cazimi / Under Beams (planet proximity to Sun)
- Part of Fortune (Arabic lot: ASC ± Moon ∓ Sun)
- Frustration (planet changes sign before perfecting aspect)
- Antiscia / Contra-antiscia (mirror aspects around Cancer/Capricorn axis)
- Besieging (planet enclosed between Mars and Saturn)
- Via Combusta (Moon in 15° Libra – 15° Scorpio)
- Fixed Stars (conjunctions to Regulus, Algol, Spica and 12 other stars)
- Lord of the Hour (Chaldean planetary hour ruler at time of question)
"""

from typing import Dict, Optional, Any, List

from src.core.dignities import (
    get_planet_sign,
    get_dispositor,
    calculate_essential_dignity,
)
from src.core.aspects_math import MAJOR_ASPECTS


# ============================================================
# TRANSLATION & COLLECTION OF LIGHT
# ============================================================


def find_translation_of_light(
    planet1: str,
    planet2: str,
    planets: Dict[str, Dict],
    aspects: List[Dict],
) -> Optional[str]:
    """
    Find translation of light.

    Translation: a 3rd planet aspects both significators, connecting them
    when they don't aspect each other directly. The translator separates
    from one significator and applies to the other.

    Args:
        planet1: First significator name
        planet2: Second significator name
        planets: Dict of all planet names to planet data
        aspects: List of pre-calculated aspects (each dict with planet1/planet2 keys)

    Returns:
        Translator planet name or None

    Example:
        >>> # Moon @ 10° Aries, Mars @ 20° Aries, Saturn @ 5° Gemini
        >>> # Moon separates from Mars, then applies to Saturn
        >>> translator = find_translation_of_light('Mars', 'Saturn', planets, aspects)
        >>> print(translator)  # 'Moon'
    """

    def has_aspect(p1: str, p2: str) -> bool:
        for asp in aspects:
            if not isinstance(asp, dict):
                continue
            a1, a2 = asp.get("planet1"), asp.get("planet2")
            if (a1 == p1 and a2 == p2) or (a1 == p2 and a2 == p1):
                return True
        return False

    for planet in planets:
        if planet == planet1 or planet == planet2:
            continue
        if has_aspect(planet, planet1) and has_aspect(planet, planet2):
            return planet

    return None


def find_collection_of_light(
    planet1: str,
    planet2: str,
    planets: Dict[str, Dict],
    aspects: List[Dict],
) -> Optional[str]:
    """
    Find collection of light.

    Collection: both significators apply to a 3rd (slower/more dignified) planet,
    which collects their light and brings them together.

    Args:
        planet1: First significator name
        planet2: Second significator name
        planets: Dict of all planet names to planet data
        aspects: List of pre-calculated aspects

    Returns:
        Collector planet name or None

    Example:
        >>> # Moon @ 5° Aries → Jupiter @ 15° Aries (applying)
        >>> # Saturn @ 12° Aries → Jupiter @ 15° Aries (applying)
        >>> collector = find_collection_of_light('Moon', 'Saturn', planets, aspects)
        >>> print(collector)  # 'Jupiter'
    """

    def get_aspect(p1: str, p2: str) -> Optional[Dict]:
        for asp in aspects:
            if not isinstance(asp, dict):
                continue
            a1, a2 = asp.get("planet1"), asp.get("planet2")
            if (a1 == p1 and a2 == p2) or (a1 == p2 and a2 == p1):
                return asp
        return None

    for planet in planets:
        if planet == planet1 or planet == planet2:
            continue
        asp1 = get_aspect(planet1, planet)
        asp2 = get_aspect(planet2, planet)
        if asp1 and asp2:
            # Both should be applying to the collector
            if asp1.get("applying", True) and asp2.get("applying", True):
                return planet

    return None


# ============================================================
# STANDALONE HORARY UTILITY FUNCTIONS (used in CLI)
# ============================================================


# NOTE: HoraryAnalyzer class was removed (was unused in CLI).
# Translation of light and collection of light are now standalone functions above.
# Old class was archived in git history (commit 81398f9).


def time_to_perfection(
    planet1_lon: float,
    planet1_speed: float,
    planet2_lon: float,
    planet2_speed: float,
    aspect_angle: float,
) -> Dict[str, Any]:
    """
    Calculate time until aspect reaches perfection (exact).

    This is crucial for horary timing predictions.

    Args:
        planet1_lon: Longitude of first planet (degrees)
        planet1_speed: Daily speed of first planet (degrees/day)
        planet2_lon: Longitude of second planet (degrees/day)
        planet2_speed: Daily speed of second planet (degrees/day)
        aspect_angle: Target aspect angle (0, 60, 90, 120, 180, etc.)

    Returns:
        dict with:
        {
            'days': float,
            'hours': float,
            'is_applying': bool,
            'current_distance': float,
            'relative_speed': float
        }

    Example:
        >>> # Moon at 114° moving 13°/day, Saturn at 1.6° moving 0.03°/day
        >>> # Trine = 120° apart
        >>> result = time_to_perfection(114.16, 13.0, 1.6, 0.03, 120)
        >>> print(result['days'])  # ~0.57 days
        >>> print(result['hours'])  # ~14 hours
    """
    # Normalize longitudes to 0-360
    planet1_lon = planet1_lon % 360
    planet2_lon = planet2_lon % 360

    # Calculate where planet1 needs to be for the aspect
    # Two possible positions: planet2 + aspect_angle or planet2 - aspect_angle
    target1 = (planet2_lon + aspect_angle) % 360
    target2 = (planet2_lon - aspect_angle) % 360

    # Calculate distances to each target (shortest arc)
    def shortest_arc(from_lon, to_lon):
        """Calculate shortest arc distance from from_lon to to_lon"""
        diff = (to_lon - from_lon) % 360
        if diff > 180:
            diff = diff - 360
        return diff

    dist1 = shortest_arc(planet1_lon, target1)
    dist2 = shortest_arc(planet1_lon, target2)

    # Choose the target that planet1 is moving toward
    if abs(dist1) < abs(dist2):
        distance_to_aspect = dist1
    else:
        distance_to_aspect = dist2

    # Net relative speed (how fast gap is closing)
    relative_speed = planet1_speed - planet2_speed

    # Determine if applying (closing) or separating
    is_applying = False

    if distance_to_aspect > 0:
        # Planet1 needs to move forward
        is_applying = relative_speed > 0
    elif distance_to_aspect < 0:
        # Planet1 needs to move backward (or planet2 needs to move forward)
        is_applying = relative_speed < 0

    # Calculate time to perfection
    days = 0.0
    hours = 0.0

    if is_applying and abs(relative_speed) > 0.001:
        days = abs(distance_to_aspect) / abs(relative_speed)
        hours = days * 24

    return {
        "days": round(days, 2),
        "hours": round(hours, 1),
        "is_applying": is_applying,
        "current_distance": round(distance_to_aspect, 2),
        "relative_speed": round(relative_speed, 2),
    }


def is_void_of_course(
    moon_lon: float, moon_speed: float, planets: Dict[str, float]
) -> Dict[str, Any]:
    """
    Check if Moon is Void of Course.

    VOC Moon: Moon makes no major aspects before leaving current sign.
    This is considered unfavorable for horary questions.

    Args:
        moon_lon: Moon's longitude (degrees)
        moon_speed: Moon's speed (degrees/day, typically 12-15)
        planets: Dict of planet names to longitudes

    Returns:
        dict with:
        {
            'is_void': bool,
            'last_aspect': str or None,  # Planet name of last aspect
            'last_aspect_type': str or None,  # Aspect type
            'next_sign_in_degrees': float,  # Degrees until next sign
            'next_sign_in_hours': float,  # Hours until sign change
            'current_sign': str
        }

    Example:
        >>> planets = {'Sun': 339.3, 'Mercury': 352.3, 'Venus': 351.9}
        >>> result = is_void_of_course(114.16, 13.0, planets)
        >>> print(result['is_void'])  # True or False
    """

    current_sign = get_planet_sign(moon_lon)

    # Calculate degree within sign (0-30)
    degree_in_sign = moon_lon % 30

    # Degrees until next sign
    degrees_to_next_sign = 30 - degree_in_sign
    hours_to_next_sign = (degrees_to_next_sign / moon_speed) * 24

    # Check for major aspects within current sign
    future_aspects = []

    for planet_name, planet_lon in planets.items():
        if planet_name == "Moon":
            continue

        # Calculate future position of Moon before sign change
        for aspect_name, aspect_config in MAJOR_ASPECTS.items():
            aspect_angle = aspect_config["angle"]

            # Calculate when Moon will form this aspect
            target_lon = (planet_lon + aspect_angle) % 360
            distance = (target_lon - moon_lon) % 360

            # Check if Moon will reach this aspect before leaving sign
            if distance <= degrees_to_next_sign and distance / moon_speed <= 2:
                # Aspect is within reach
                future_aspects.append(
                    {
                        "planet": planet_name,
                        "aspect": aspect_name,
                        "distance": distance,
                        "hours": (distance / moon_speed) * 24,
                    }
                )

    # Moon is VOC if no future major aspects before sign change
    is_void = len(future_aspects) == 0

    return {
        "is_void": is_void,
        "last_aspect": None,  # Would need historical data
        "last_aspect_type": None,
        "next_sign_in_degrees": round(degrees_to_next_sign, 2),
        "next_sign_in_hours": round(hours_to_next_sign, 1),
        "current_sign": current_sign,
        "upcoming_aspects": future_aspects if not is_void else [],
    }


def check_radicality(asc_lon: float, saturn_house: int) -> Dict[str, Any]:
    """
    Check if horary chart is "radical" (valid to judge).

    Traditional rules:
    1. ASC must be between 3° and 27° of sign (not too early/late)
    2. Saturn NOT in 1st or 7th house (blocks judgment)
    3. Moon NOT Void of Course (requires is_void_of_course() result)

    Args:
        asc_lon: Ascendant longitude (degrees)
        saturn_house: House number where Saturn is located (1-12)

    Returns:
        dict with:
        {
            'is_radical': bool,
            'warnings': [list of warning strings],
            'asc_degree_in_sign': float
        }

    Example:
        >>> result = check_radicality(244.66, 12)
        >>> print(result['is_radical'])  # True or False
        >>> print(result['warnings'])  # ['ASC too late in sign', ...]
    """
    warnings = []
    is_radical = True

    # Check Ascendant degree within sign
    asc_degree_in_sign = asc_lon % 30

    if asc_degree_in_sign < 3:
        warnings.append(
            f"ASC too early in sign ({asc_degree_in_sign:.1f}°) - question may be premature"
        )
        is_radical = False
    elif asc_degree_in_sign > 27:
        warnings.append(
            f"ASC too late in sign ({asc_degree_in_sign:.1f}°) - question may be too late"
        )
        is_radical = False

    # Check Saturn in 1st or 7th house
    if saturn_house in [1, 7]:
        warnings.append(
            f"Saturn in {saturn_house}{'st' if saturn_house == 1 else 'th'} house - judgment blocked or difficult"
        )
        is_radical = False

    return {
        "is_radical": is_radical,
        "warnings": warnings,
        "asc_degree_in_sign": round(asc_degree_in_sign, 1),
    }


def find_mutual_receptions(planets: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Find all mutual receptions in the chart.

    Mutual reception: Two planets in each other's ruling signs.
    This creates a strong connection and mutual help.

    Args:
        planets: Dict of planet names to planet data containing 'longitude'

    Returns:
        List of mutual reception pairs:
        [
            {
                'planet1': 'Saturn',
                'planet2': 'Mars',
                'planet1_sign': 'Aries',
                'planet2_sign': 'Aquarius',
                'type': 'domicile'  # or 'exaltation'
            },
            ...
        ]

    Example:
        >>> planets = {
        ...     'Saturn': {'longitude': 1.6},  # Aries
        ...     'Mars': {'longitude': 327.9}   # Aquarius
        ... }
        >>> receptions = find_mutual_receptions(planets)
        >>> print(receptions[0])  # {'planet1': 'Saturn', 'planet2': 'Mars', ...}
    """

    mutual_receptions = []

    planet_names = list(planets.keys())

    for i, p1_name in enumerate(planet_names):
        for p2_name in planet_names[i + 1 :]:
            p1_data = planets[p1_name]
            p2_data = planets[p2_name]

            if "longitude" not in p1_data or "longitude" not in p2_data:
                continue

            p1_lon = p1_data["longitude"]
            p2_lon = p2_data["longitude"]

            p1_sign = get_planet_sign(p1_lon)
            p2_sign = get_planet_sign(p2_lon)

            # Check domicile mutual reception (use traditional rulers for horary)
            p1_ruler = get_dispositor(p1_sign, traditional=True)
            p2_ruler = get_dispositor(p2_sign, traditional=True)

            if p1_ruler == p2_name and p2_ruler == p1_name:
                mutual_receptions.append(
                    {
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "planet1_sign": p1_sign,
                        "planet2_sign": p2_sign,
                        "type": "domicile",
                    }
                )

            # Check exaltation mutual reception (less common)
            # This is more complex as exaltation can be by domicile ruler
            # We'll skip this for now or implement if needed

    return mutual_receptions


# ============================================================
# PROHIBITION (Запрещение) — William Lilly CA Book II p.297-302
# ============================================================


def check_prohibition(
    planet1: str,
    planet1_lon: float,
    planet1_speed: float,
    planet2: str,
    planet2_lon: float,
    planet2_speed: float,
    aspect_angle: float,
    all_planets: Dict[str, Dict[str, Any]],
    orb: float = 8.0,
) -> Dict[str, Any]:
    """
    Check if an applying aspect between two significators is prohibited
    by a third planet that intercepts before perfection.

    Traditional rule (Lilly): When planet A applies to B, but planet C
    first aspects A or B before A-B perfects — the matter is PROHIBITED.

    Args:
        planet1: Significator 1 name (faster planet)
        planet1_lon: Longitude of planet1 (degrees)
        planet1_speed: Daily speed of planet1
        planet2: Significator 2 name
        planet2_lon: Longitude of planet2
        planet2_speed: Daily speed of planet2
        aspect_angle: Target aspect (0, 60, 90, 120, 180)
        all_planets: Dict of all planets {name: {longitude, Speed, ...}}
        orb: Max orb for intercepting aspect (default 8°)

    Returns:
        {
            'is_prohibited': bool,
            'prohibitor': str | None,
            'prohibitor_aspect': str | None,
            'prohibitor_target': str | None,  # 'planet1' or 'planet2' name
            'time_to_prohibition': float | None,  # days
            'time_to_perfection': float | None,   # days
            'explanation': str
        }
    """
    result: Dict[str, Any] = {
        "is_prohibited": False,
        "prohibitor": None,
        "prohibitor_aspect": None,
        "prohibitor_target": None,
        "time_to_prohibition": None,
        "time_to_perfection": None,
        "explanation": "No prohibition detected",
    }

    # Main aspect must be applying
    main_perf = time_to_perfection(
        planet1_lon,
        planet1_speed,
        planet2_lon,
        planet2_speed,
        aspect_angle,
    )

    if not main_perf["is_applying"]:
        result["explanation"] = "Main aspect is separating (not applying)"
        return result

    time_to_main = main_perf["days"]
    result["time_to_perfection"] = time_to_main

    # Check every other planet for earlier interception
    for other_name, other_data in all_planets.items():
        if other_name == planet1 or other_name == planet2:
            continue

        if "longitude" not in other_data or "Speed" not in other_data:
            continue

        other_lon = float(other_data["longitude"])
        other_speed = float(other_data.get("Speed", 0.0))

        for aspect_name, aspect_config in MAJOR_ASPECTS.items():
            check_angle = aspect_config["angle"]

            # Check aspect to planet1
            perf1 = time_to_perfection(
                other_lon,
                other_speed,
                planet1_lon,
                planet1_speed,
                check_angle,
            )
            if (
                perf1["is_applying"]
                and perf1["days"] < time_to_main
                and abs(perf1["current_distance"]) <= orb
            ):
                result["is_prohibited"] = True
                result["prohibitor"] = other_name
                result["prohibitor_aspect"] = aspect_name
                result["prohibitor_target"] = planet1
                result["time_to_prohibition"] = perf1["days"]
                result["explanation"] = (
                    f"{other_name} will {aspect_name} {planet1} in "
                    f"{perf1['days']:.2f} days, BEFORE {planet1} "
                    f"perfects {aspect_angle}\u00b0 with {planet2} "
                    f"(in {time_to_main:.2f} days). Matter is PROHIBITED."
                )
                return result

            # Check aspect to planet2
            perf2 = time_to_perfection(
                other_lon,
                other_speed,
                planet2_lon,
                planet2_speed,
                check_angle,
            )
            if (
                perf2["is_applying"]
                and perf2["days"] < time_to_main
                and abs(perf2["current_distance"]) <= orb
            ):
                result["is_prohibited"] = True
                result["prohibitor"] = other_name
                result["prohibitor_aspect"] = aspect_name
                result["prohibitor_target"] = planet2
                result["time_to_prohibition"] = perf2["days"]
                result["explanation"] = (
                    f"{other_name} will {aspect_name} {planet2} in "
                    f"{perf2['days']:.2f} days, BEFORE {planet1} "
                    f"perfects aspect with {planet2} "
                    f"(in {time_to_main:.2f} days). Matter is PROHIBITED."
                )
                return result

    result["explanation"] = "No planet intercepts the applying aspect"
    return result


# ============================================================
# REFRENATION (Отказ) — William Lilly CA Book II p.302-305
# ============================================================


def check_refrenation(
    planet_name: str,
    planet_lon: float,
    planet_speed: float,
    target_lon: float,
    target_speed: float,
    aspect_angle: float,
    ephemeris_jd_start: float,
    ephemeris_func: Any,
) -> Dict[str, Any]:
    """
    Check if an applying planet will turn retrograde before perfecting its aspect.

    Refrenation (refranation): a planet "changes its mind" by stationing
    retrograde before reaching exact aspect. Traditional interpretation:
    the matter will NOT happen, or the person will back out.

    Args:
        planet_name: Name of the applying planet (e.g., 'Venus')
        planet_lon: Current longitude (degrees)
        planet_speed: Current daily speed (positive = direct)
        target_lon: Longitude of target planet
        target_speed: Daily speed of target planet
        aspect_angle: Target aspect (0, 60, 90, 120, 180)
        ephemeris_jd_start: Julian Day for current date
        ephemeris_func: Callable(jd, planet_id) → sequence
                        where [0]=longitude, [3]=speed (e.g., swisseph.calc_ut)

    Returns:
        {
            'will_refrenate': bool,
            'is_currently_retrograde': bool,
            'station_jd': float | None,
            'station_longitude': float | None,
            'days_to_station': float | None,
            'days_to_perfection': float | None,
            'explanation': str
        }
    """
    result: Dict[str, Any] = {
        "will_refrenate": False,
        "is_currently_retrograde": planet_speed < 0,
        "station_jd": None,
        "station_longitude": None,
        "days_to_station": None,
        "days_to_perfection": None,
        "explanation": "",
    }

    # Already retrograde — no refrenation possible
    if planet_speed < 0:
        result["explanation"] = f"{planet_name} is already retrograde"
        return result

    # Calculate time to perfection
    perfection = time_to_perfection(
        planet_lon,
        planet_speed,
        target_lon,
        target_speed,
        aspect_angle,
    )

    if not perfection["is_applying"]:
        result["explanation"] = "Aspect is separating (not applying)"
        return result

    days_to_perfect = perfection["days"]
    result["days_to_perfection"] = days_to_perfect

    # Swiss Ephemeris planet IDs (classic planets only)
    _PLANET_IDS = {
        "Sun": 0,
        "Moon": 1,
        "Mercury": 2,
        "Venus": 3,
        "Mars": 4,
        "Jupiter": 5,
        "Saturn": 6,
        "Uranus": 7,
        "Neptune": 8,
        "Pluto": 9,
    }

    if planet_name not in _PLANET_IDS:
        result["explanation"] = f"Unknown planet for refrenation check: {planet_name}"
        return result

    planet_id = _PLANET_IDS[planet_name]

    # Sun and Moon never retrograde
    if planet_name in ("Sun", "Moon"):
        result["explanation"] = f"{planet_name} never goes retrograde"
        return result

    # Scan ephemeris day by day for Direct→Retrograde station
    max_days = min(int(days_to_perfect) + 10, 90)
    prev_speed = planet_speed

    for day_offset in range(1, max_days + 1):
        jd = ephemeris_jd_start + day_offset
        try:
            calc_result = ephemeris_func(jd, planet_id)
            # Handle both flat tuple and nested tuple from swisseph
            if hasattr(calc_result[0], "__iter__"):
                new_lon = float(calc_result[0][0])
                new_speed = float(calc_result[0][3])
            else:
                new_lon = float(calc_result[0])
                new_speed = float(calc_result[3])
        except Exception as exc:  # noqa: BLE001
            result["explanation"] = f"Ephemeris error on JD {jd}: {exc}"
            return result

        # Direct → Retrograde station detected
        if prev_speed > 0 and new_speed <= 0:
            result["station_jd"] = jd
            result["station_longitude"] = round(new_lon, 4)
            result["days_to_station"] = day_offset
            result["will_refrenate"] = day_offset < days_to_perfect

            if result["will_refrenate"]:
                result["explanation"] = (
                    f"{planet_name} stations RETROGRADE in {day_offset} days "
                    f"@ {new_lon:.2f}\u00b0, BEFORE perfecting {aspect_angle}\u00b0 aspect "
                    f"(needed {days_to_perfect:.2f} days). Matter is REFRENATED."
                )
            else:
                result["explanation"] = (
                    f"{planet_name} stations retrograde in {day_offset} days "
                    f"@ {new_lon:.2f}\u00b0, but AFTER perfection "
                    f"({days_to_perfect:.2f} days). No refrenation."
                )
            return result

        prev_speed = new_speed

    result["explanation"] = (
        f"{planet_name} will not station retrograde within "
        f"{max_days} days (perfection in {days_to_perfect:.2f} days)"
    )
    return result


# ============================================================
# RECEPTION QUALITY (Качество рецепции) — Lilly CA Book II p.112-118
# ============================================================


def analyze_reception_quality(
    planet1: str,
    planet1_lon: float,
    planet2: str,
    planet2_lon: float,
    traditional: bool = True,
) -> Dict[str, Any]:
    """
    Analyze quality of reception between two planets.

    Reception = planet occupies sign ruled by another planet.
    Quality depends on how dignified the received planet is in that sign.

    Args:
        planet1: First planet name
        planet1_lon: Longitude of first planet
        planet2: Second planet name
        planet2_lon: Longitude of second planet
        traditional: Use traditional rulerships (Saturn→Aquarius, Mars→Scorpio)

    Returns:
        {
            'planet1_receives_planet2': {
                'has_reception': bool,
                'type': 'domicile' | None,
                'quality': 'friendly' | 'hostile' | 'neutral',
                'score': int,
                'interpretation': str
            },
            'planet2_receives_planet1': { ... same ... },
            'is_mutual': bool,
            'overall_quality': 'friendly' | 'hostile' | 'mixed' | 'neutral'
        }
    """

    def _reception_entry(
        has_rec: bool,
        rec_type: Optional[str],
        quality: str,
        score: int,
        interpretation: str,
    ) -> Dict[str, Any]:
        return {
            "has_reception": has_rec,
            "type": rec_type,
            "quality": quality,
            "score": score,
            "interpretation": interpretation,
        }

    def _assess(
        receiver: str,
        received_planet: str,
        received_lon: float,
        sign_of_receiver: str,
    ) -> Dict[str, Any]:
        """Assess the quality of `receiver` receiving `received_planet`."""
        dignity = calculate_essential_dignity(received_planet, received_lon)
        score = dignity.get("score", 0)
        level = dignity.get("dignity_level", "Neutral")

        # Use dignity_level so that compound scores (domicile+triplicity etc.)
        # are evaluated correctly even when raw score is non-intuitive.
        if level in ("Very Strong", "Strong"):
            quality = "friendly"
            interpretation = (
                f"{receiver} receives {received_planet} in {sign_of_receiver} "
                f"(friendly \u2014 {received_planet} {level.lower()} here, score +{score})"
            )
        elif level in ("Very Weak", "Weak"):
            quality = "hostile"
            interpretation = (
                f"{receiver} receives {received_planet} in {sign_of_receiver} "
                f"(hostile \u2014 {received_planet} {level.lower()} here, score {score})"
            )
        else:
            quality = "neutral"
            interpretation = (
                f"{receiver} receives {received_planet} in {sign_of_receiver} "
                f"(neutral, score {score})"
            )

        return _reception_entry(True, "domicile", quality, score, interpretation)

    _empty = _reception_entry(False, None, "neutral", 0, "")

    p1_sign = get_planet_sign(planet1_lon)
    p2_sign = get_planet_sign(planet2_lon)

    p1_ruler = get_dispositor(p1_sign, traditional=traditional)
    p2_ruler = get_dispositor(p2_sign, traditional=traditional)

    # planet2 receives planet1 (planet1 is in planet2's sign)
    p2_receives_p1 = (
        _assess(planet2, planet1, planet1_lon, p1_sign)
        if p1_ruler == planet2
        else _empty.copy()
    )

    # planet1 receives planet2 (planet2 is in planet1's sign)
    p1_receives_p2 = (
        _assess(planet1, planet2, planet2_lon, p2_sign)
        if p2_ruler == planet1
        else _empty.copy()
    )

    is_mutual = p1_receives_p2["has_reception"] and p2_receives_p1["has_reception"]

    # Overall quality: collect all active reception qualities
    active_qualities = set()
    for side in (p1_receives_p2, p2_receives_p1):
        if side["has_reception"]:
            active_qualities.add(side["quality"])

    if not active_qualities:
        overall = "neutral"
    elif active_qualities == {"friendly"}:
        overall = "friendly"
    elif active_qualities == {"hostile"}:
        overall = "hostile"
    elif "hostile" in active_qualities:
        overall = "mixed"  # hostile + neutral, or hostile + friendly
    else:
        overall = "neutral"  # only neutral receptions present

    return {
        "planet1_receives_planet2": p1_receives_p2,
        "planet2_receives_planet1": p2_receives_p1,
        "is_mutual": is_mutual,
        "overall_quality": overall,
    }


# ============================================================
# COMBUST / CAZIMI / UNDER BEAMS
# ============================================================

# Thresholds (degrees) — traditional values from Lilly CA Book II
_CAZIMI_LIMIT = 17 / 60  # 17 arcminutes = 0.2833°
_COMBUST_LIMIT = 8.5  # 8°30'
_UNDER_BEAMS_LIMIT = 17.0  # 17°

# Strength modifiers (accidental dignity scale, Lilly)
_COMBUST_MODIFIER = -5
_UNDER_BEAMS_MODIFIER = -2
_CAZIMI_MODIFIER = +5

# Planets that cannot be combust (Sun itself; Moon rules differ — excluded)
_COMBUST_EXEMPT = {"Sun"}


def check_combust_cazimi(
    planet_name: str,
    planet_lon: float,
    sun_lon: float,
) -> Dict[str, Any]:
    """
    Check planet's accidental state relative to the Sun.

    Traditional rules (Lilly CA Book II):
    - Cazimi   (within 17'): planet in "heart of Sun" — greatly strengthened
    - Combust  (<8°30'):     planet "burned up" — very weak, cannot act
    - Under Beams (<17°):   planet weakened but less than combust
    - Free:                 no solar impediment

    The Sun cannot be combust. Moon combustion is noted but treated
    separately in traditional practice (different thresholds apply).

    Args:
        planet_name: Name of the planet to test.
        planet_lon:  Ecliptic longitude of the planet (degrees, 0–360).
        sun_lon:     Ecliptic longitude of the Sun (degrees, 0–360).

    Returns:
        {
            'state':             'cazimi' | 'combust' | 'under_beams' | 'free',
            'distance':          float,   # |planet − Sun| normalised 0–180
            'strength_modifier': int,     # accidental dignity points
            'is_impaired':       bool,    # True for combust / under_beams
            'is_strengthened':   bool,    # True for cazimi
            'explanation':       str,
        }
    """
    if planet_name in _COMBUST_EXEMPT:
        return {
            "state": "free",
            "distance": 0.0,
            "strength_modifier": 0,
            "is_impaired": False,
            "is_strengthened": False,
            "explanation": f"{planet_name} cannot be combust.",
        }

    # Shortest arc between the two longitudes
    raw = abs(planet_lon - sun_lon) % 360.0
    distance = raw if raw <= 180.0 else 360.0 - raw

    if distance <= _CAZIMI_LIMIT:
        state = "cazimi"
        modifier = _CAZIMI_MODIFIER
        explanation = (
            f"{planet_name} is Cazimi (within 17' of Sun, distance={distance:.2f}°). "
            "Planet is in the heart of the Sun — greatly strengthened."
        )
        impaired, strengthened = False, True
    elif distance <= _COMBUST_LIMIT:
        state = "combust"
        modifier = _COMBUST_MODIFIER
        explanation = (
            f"{planet_name} is Combust (within 8°30' of Sun, distance={distance:.2f}°). "
            "Planet is burned up — very weak, significator cannot act effectively."
        )
        impaired, strengthened = True, False
    elif distance <= _UNDER_BEAMS_LIMIT:
        state = "under_beams"
        modifier = _UNDER_BEAMS_MODIFIER
        explanation = (
            f"{planet_name} is Under the Beams (within 17° of Sun, distance={distance:.2f}°). "
            "Planet is weakened but less severely than combustion."
        )
        impaired, strengthened = True, False
    else:
        state = "free"
        modifier = 0
        explanation = (
            f"{planet_name} is free of solar impediment (distance={distance:.2f}°)."
        )
        impaired, strengthened = False, False

    return {
        "state": state,
        "distance": round(distance, 4),
        "strength_modifier": modifier,
        "is_impaired": impaired,
        "is_strengthened": strengthened,
        "explanation": explanation,
    }


# ============================================================
# PART OF FORTUNE
# ============================================================

# Traditional sign rulers (Chaldean, same as in dignities.py)
_SIGN_RULERS_LOT = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

_SIGNS_ORDER = [
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


def calculate_part_of_fortune(
    asc_lon: float,
    sun_lon: float,
    moon_lon: float,
    is_day_chart: bool,
) -> Dict[str, Any]:
    """
    Calculate the Part of Fortune (Pars Fortunae / Lot of Fortune).

    Traditional formula (Dorotheus, Lilly CA):
    - Day chart  (Sun above horizon): ASC + Moon − Sun
    - Night chart (Sun below horizon): ASC + Sun  − Moon

    Args:
        asc_lon:      Ascendant longitude (degrees, 0–360).
        sun_lon:      Sun longitude (degrees, 0–360).
        moon_lon:     Moon longitude (degrees, 0–360).
        is_day_chart: True when the Sun is above the horizon
                      (between ASC and DSC going through MC).

    Returns:
        {
            'longitude':  float,  # 0–360
            'sign':       str,
            'degree_in_sign': float,  # 0–30
            'ruler':      str,   # traditional sign ruler
            'formula':    str,   # formula used
            'explanation': str,
        }
    """
    if is_day_chart:
        raw = (asc_lon + moon_lon - sun_lon) % 360.0
        formula = "ASC + Moon − Sun  (day chart)"
    else:
        raw = (asc_lon + sun_lon - moon_lon) % 360.0
        formula = "ASC + Sun − Moon  (night chart)"

    lon = raw % 360.0  # ensure 0 ≤ lon < 360
    sign_index = int(lon // 30)
    sign = _SIGNS_ORDER[sign_index]
    degree_in_sign = lon % 30.0
    ruler = _SIGN_RULERS_LOT.get(sign, "Unknown")

    explanation = (
        f"Part of Fortune at {degree_in_sign:.2f}° {sign} "
        f"(lon={lon:.4f}°). Ruler: {ruler}. Formula: {formula}."
    )

    return {
        "longitude": round(lon, 4),
        "sign": sign,
        "degree_in_sign": round(degree_in_sign, 4),
        "ruler": ruler,
        "formula": formula,
        "explanation": explanation,
    }


# ============================================================
# FRUSTRATION
# ============================================================


def check_frustration(
    planet1_lon: float,
    planet1_speed: float,
    planet2_lon: float,
    planet2_speed: float,
    aspect_angle: float,
) -> Dict[str, Any]:
    """
    Check if an applying aspect will be frustrated by a sign change.

    Frustration (Bonatti "Liber Astronomiae", Lilly CA):
    A planet applies to an aspect, but crosses into the next sign
    BEFORE the aspect perfects. The matter is then "frustrated" —
    it begins but does not complete.

    Rule: only planet1 (the faster, applying planet) is checked for
    sign change, since it is the one "reaching out" to make the aspect.

    Args:
        planet1_lon:   Ecliptic longitude of the applying planet (°).
        planet1_speed: Daily velocity of planet1 (+/− degrees per day).
        planet2_lon:   Ecliptic longitude of the receiving planet (°).
        planet2_speed: Daily velocity of planet2 (degrees per day).
        aspect_angle:  Target aspect in degrees (0, 60, 90, 120, 180).

    Returns:
        {
            'is_frustrated':              bool,
            'is_applying':                bool,
            'days_to_perfection':         float | None,
            'degrees_to_perfection':      float | None,
            'degrees_to_sign_change':     float | None,
            'days_to_sign_change':        float | None,
            'planet1_sign_now':           str,
            'planet1_sign_after_change':  str,
            'explanation':                str,
        }
    """
    # -- Determine if the aspect is applying ---------------------------
    # Use the same angular-distance logic as time_to_perfection()
    diff = (planet2_lon - planet1_lon) % 360.0  # how far ahead planet2 is

    # Candidate perfection points: direct (diff to aspect_angle) and
    # retrograde (360 - aspect_angle)
    candidates = []
    for target in (aspect_angle % 360.0, (360.0 - aspect_angle) % 360.0):
        arc = (target - diff) % 360.0  # degrees planet1 must gain on planet2
        if arc > 180.0:
            arc -= 360.0  # negative → planet1 must lose ground (separating)
        candidates.append(arc)

    # Pick the smaller absolute arc
    arc_to_perfection = min(candidates, key=abs)

    relative_speed = planet1_speed - planet2_speed
    is_applying = False
    days_to_perfection = None
    degrees_to_perfection = None

    if relative_speed != 0 and abs(arc_to_perfection) <= 180:
        days_raw = arc_to_perfection / relative_speed
        if days_raw > 0:
            is_applying = True
            days_to_perfection = round(days_raw, 4)
            degrees_to_perfection = round(abs(arc_to_perfection), 4)

    if not is_applying:
        sign_now = get_planet_sign(planet1_lon)
        return {
            "is_frustrated": False,
            "is_applying": False,
            "days_to_perfection": None,
            "degrees_to_perfection": None,
            "degrees_to_sign_change": None,
            "days_to_sign_change": None,
            "planet1_sign_now": sign_now,
            "planet1_sign_after_change": sign_now,
            "explanation": "Aspect is not applying — frustration cannot occur.",
        }

    # -- Degrees until planet1 leaves its current sign -----------------
    sign_now = get_planet_sign(planet1_lon)
    sign_index_now = int(planet1_lon // 30)

    if planet1_speed > 0:
        # Moving direct: distance to next sign boundary
        degrees_to_sign_change = 30.0 - (planet1_lon % 30.0)
        next_sign_index = (sign_index_now + 1) % 12
    elif planet1_speed < 0:
        # Retrograde: distance back to previous sign boundary
        degrees_to_sign_change = planet1_lon % 30.0
        next_sign_index = (sign_index_now - 1) % 12
    else:
        # Stationary: no sign change possible
        sign_after = sign_now
        return {
            "is_frustrated": False,
            "is_applying": True,
            "days_to_perfection": days_to_perfection,
            "degrees_to_perfection": degrees_to_perfection,
            "degrees_to_sign_change": None,
            "days_to_sign_change": None,
            "planet1_sign_now": sign_now,
            "planet1_sign_after_change": sign_now,
            "explanation": (
                f"Planet1 is stationary — sign change impossible. "
                f"Aspect perfects in {days_to_perfection:.2f} days."
            ),
        }

    sign_after = _SIGNS_ORDER[next_sign_index]
    days_to_sign_change = round(degrees_to_sign_change / abs(planet1_speed), 4)
    is_frustrated = days_to_sign_change < days_to_perfection

    if is_frustrated:
        explanation = (
            f"FRUSTRATED: {sign_now} → {sign_after} in "
            f"{days_to_sign_change:.2f} days ({degrees_to_sign_change:.2f}°), "
            f"but aspect perfects in {days_to_perfection:.2f} days "
            f"({degrees_to_perfection:.2f}°). "
            "Planet crosses sign boundary before the aspect completes."
        )
    else:
        explanation = (
            f"Not frustrated: aspect perfects in {days_to_perfection:.2f} days "
            f"({degrees_to_perfection:.2f}°) before sign change "
            f"({sign_now} → {sign_after} in {days_to_sign_change:.2f} days)."
        )

    return {
        "is_frustrated": is_frustrated,
        "is_applying": True,
        "days_to_perfection": days_to_perfection,
        "degrees_to_perfection": degrees_to_perfection,
        "degrees_to_sign_change": round(degrees_to_sign_change, 4),
        "days_to_sign_change": days_to_sign_change,
        "planet1_sign_now": sign_now,
        "planet1_sign_after_change": sign_after,
        "explanation": explanation,
    }


# ============================================================
# ANTISCIA & CONTRA-ANTISCIA
# ============================================================

# Default orb for antiscia connections (traditional horary: 1°)
_ANTISCIA_DEFAULT_ORB = 1.0


def calculate_antiscia(longitude: float) -> Dict[str, Any]:
    """
    Calculate the antiscion and contra-antiscion of a point.

    Antiscia are mirror points reflected around the Cancer/Capricorn
    (summer/winter solstice) axis.  Points that are antiscia of each
    other share the same solar declination and act like a hidden
    conjunction in horary judgment.

    Formula (reflection around the 90°–270° axis):
        antiscion       = (180° − longitude) mod 360
        contra-antiscion = (360° − longitude) mod 360   [= antiscion + 180°]

    Traditional sign pairs (approximate):
        Aries ↔ Virgo   Taurus ↔ Leo    Gemini ↔ Cancer
        Libra ↔ Pisces  Scorpio ↔ Aquarius  Sagittarius ↔ Capricorn

    Args:
        longitude: Ecliptic longitude (degrees, 0–360).

    Returns:
        {
            'antiscion':            float,  # antiscion longitude 0–360
            'contra_antiscion':     float,  # contra-antiscion longitude 0–360
            'sign_antiscion':       str,    # zodiac sign of antiscion
            'sign_contra_antiscion': str,   # zodiac sign of contra-antiscion
        }
    """
    lon = longitude % 360.0
    antiscion = (180.0 - lon) % 360.0
    contra = (360.0 - lon) % 360.0

    return {
        "antiscion": round(antiscion, 4),
        "contra_antiscion": round(contra, 4),
        "sign_antiscion": get_planet_sign(antiscion),
        "sign_contra_antiscion": get_planet_sign(contra),
    }


def find_antiscia_aspects(
    planet1_lon: float,
    planet2_lon: float,
    orb: float = _ANTISCIA_DEFAULT_ORB,
) -> Dict[str, Any]:
    """
    Check whether two planets are connected via antiscia.

    Two planets are connected if planet2's longitude falls within *orb*
    degrees of either planet1's antiscion or planet1's contra-antiscion.

    Args:
        planet1_lon: Longitude of the first planet (degrees).
        planet2_lon: Longitude of the second planet (degrees).
        orb:         Maximum allowed separation (degrees). Default 1°.

    Returns:
        {
            'has_antiscia':     bool,
            'type':             'antiscion' | 'contra-antiscion' | None,
            'orb':              float | None,   # actual separation
            'antiscion_lon':    float,   # planet1's antiscion point
            'contra_lon':       float,   # planet1's contra-antiscion point
            'explanation':      str,
        }
    """
    p1_points = calculate_antiscia(planet1_lon)
    p2 = planet2_lon % 360.0

    def _arc(a: float, b: float) -> float:
        """Shortest unsigned arc between a and b (0–180)."""
        diff = abs(a - b) % 360.0
        return diff if diff <= 180.0 else 360.0 - diff

    orb_antiscion = _arc(p1_points["antiscion"], p2)
    orb_contra = _arc(p1_points["contra_antiscion"], p2)

    best_type: Optional[str] = None
    best_orb: Optional[float] = None

    if orb_antiscion <= orb and (best_orb is None or orb_antiscion < best_orb):
        best_type = "antiscion"
        best_orb = round(orb_antiscion, 4)
    if orb_contra <= orb and (best_orb is None or orb_contra < best_orb):
        best_type = "contra-antiscion"
        best_orb = round(orb_contra, 4)

    has = best_type is not None

    if has:
        explanation = (
            f"Planet1 ({planet1_lon:.2f}°) and Planet2 ({planet2_lon:.2f}°) "
            f"are connected via {best_type} (orb={best_orb:.2f}°)."
        )
    else:
        explanation = (
            f"No antiscia connection between {planet1_lon:.2f}° and "
            f"{planet2_lon:.2f}° within orb {orb}°."
        )

    return {
        "has_antiscia": has,
        "type": best_type,
        "orb": best_orb,
        "antiscion_lon": p1_points["antiscion"],
        "contra_lon": p1_points["contra_antiscion"],
        "explanation": explanation,
    }


# ============================================================
# BESIEGING
# ============================================================

# Traditional malefics that create besieging
_BESIEGING_MALEFICS = {"Mars", "Saturn"}


def check_besieging(
    planet_name: str,
    planet_lon: float,
    all_planets: Dict[str, Dict[str, Any]],
    orb: float = 8.0,
) -> Dict[str, Any]:
    """
    Check whether a planet is besieged between Mars and Saturn.

    Besieging (William Lilly CA Book II): a planet is enclosed between
    the two great malefics (Mars and Saturn) in the zodiac — one is
    *ahead* and the other *behind* the planet by direct motion, within a
    reasonable orb.  Being besieged is a strong accidental debility.

    Detection rules:
    - Find both malefics in *all_planets* (skip if either is absent or
      is the planet under test).
    - Express the signed arc from planet_lon to each malefic: positive =
      malefic ahead (later in zodiac), negative = malefic behind.
    - The planet is besieged when one malefic is ahead (+) AND the other
      is behind (−), both within *orb* degrees.

    Args:
        planet_name:  Name of the planet to test.
        planet_lon:   Ecliptic longitude of the planet (degrees).
        all_planets:  Dict mapping planet name → {'lon': float, ...}.
        orb:          Maximum distance (degrees) to each malefic.
                      Default 8° (Lilly's standard major-aspect orb).

    Returns:
        {
            'is_besieged':    bool,
            'malefic_ahead':  str | None,   # name of malefic ahead
            'malefic_behind': str | None,   # name of malefic behind
            'arc_ahead':      float | None, # degrees planet is ahead of trailing malefic
            'arc_behind':     float | None, # degrees planet is behind leading malefic
            'explanation':    str,
        }
    """
    malefic_data: Dict[str, float] = {}
    for name in _BESIEGING_MALEFICS:
        if name == planet_name:
            continue
        entry = all_planets.get(name)
        if entry is None:
            continue
        lon = entry.get("lon", entry.get("longitude"))
        if lon is not None:
            malefic_data[name] = float(lon) % 360.0

    if len(malefic_data) < 2:
        return {
            "is_besieged": False,
            "malefic_ahead": None,
            "malefic_behind": None,
            "arc_ahead": None,
            "arc_behind": None,
            "explanation": "Less than two distinct malefics available — besieging cannot occur.",
        }

    p_lon = planet_lon % 360.0

    def _signed_arc(from_lon: float, to_lon: float) -> float:
        """Signed shortest arc: positive = to_lon ahead of from_lon."""
        raw = (to_lon - from_lon) % 360.0
        return raw if raw <= 180.0 else raw - 360.0

    arcs = {name: _signed_arc(p_lon, lon) for name, lon in malefic_data.items()}
    names = list(arcs)

    m1_name, m2_name = names[0], names[1]
    arc1, arc2 = arcs[m1_name], arcs[m2_name]

    # One must be ahead (+) and the other behind (−) within orb
    if arc1 > 0 and arc2 < 0:
        ahead_name, behind_name = m1_name, m2_name
        arc_ahead, arc_behind = arc1, abs(arc2)
    elif arc2 > 0 and arc1 < 0:
        ahead_name, behind_name = m2_name, m1_name
        arc_ahead, arc_behind = arc2, abs(arc1)
    else:
        return {
            "is_besieged": False,
            "malefic_ahead": None,
            "malefic_behind": None,
            "arc_ahead": None,
            "arc_behind": None,
            "explanation": (
                f"{planet_name} is not enclosed: both malefics are on the same side "
                f"({m1_name}={arc1:+.2f}°, {m2_name}={arc2:+.2f}°)."
            ),
        }

    if arc_ahead > orb or arc_behind > orb:
        return {
            "is_besieged": False,
            "malefic_ahead": ahead_name,
            "malefic_behind": behind_name,
            "arc_ahead": round(arc_ahead, 4),
            "arc_behind": round(arc_behind, 4),
            "explanation": (
                f"{planet_name} is flanked by malefics but outside orb {orb}°: "
                f"{behind_name} {arc_behind:.2f}° behind, "
                f"{ahead_name} {arc_ahead:.2f}° ahead."
            ),
        }

    return {
        "is_besieged": True,
        "malefic_ahead": ahead_name,
        "malefic_behind": behind_name,
        "arc_ahead": round(arc_ahead, 4),
        "arc_behind": round(arc_behind, 4),
        "explanation": (
            f"{planet_name} is BESIEGED: {behind_name} {arc_behind:.2f}° behind, "
            f"{ahead_name} {arc_ahead:.2f}° ahead. Strong accidental debility."
        ),
    }


# ============================================================
# VIA COMBUSTA
# ============================================================

# Via Combusta: 15° Libra to 15° Scorpio
# 15° Libra = 180° + 15° = 195°
# 15° Scorpio = 210° + 15° = 225°
_VIA_COMBUSTA_START = 195.0  # 15° Libra
_VIA_COMBUSTA_END = 225.0  # 15° Scorpio


def is_via_combusta(moon_lon: float) -> Dict[str, Any]:
    """
    Check whether the Moon is in the Via Combusta (Burned Way).

    The Via Combusta spans 15° Libra to 15° Scorpio (195°–225°).
    According to medieval tradition (Al-Biruni, Bonatti), the Moon in
    this zone is greatly weakened and the chart is generally unfavourable
    for judgment.

    Exceptions noted by some authors:
    - Moon conjunct Spica (≈203.7°, 23° Libra) or Arcturus (≈203.9°)
      mitigates the via combusta.

    Args:
        moon_lon: Moon's ecliptic longitude (degrees, 0–360).

    Returns:
        {
            'is_via_combusta': bool,
            'moon_longitude':  float,
            'moon_sign':       str,
            'zone_start':      float,   # 195.0
            'zone_end':        float,   # 225.0
            'degrees_into_zone': float | None,  # None if not in zone
            'explanation':     str,
        }
    """
    lon = moon_lon % 360.0
    in_zone = _VIA_COMBUSTA_START <= lon <= _VIA_COMBUSTA_END
    sign = get_planet_sign(lon)

    degrees_into = round(lon - _VIA_COMBUSTA_START, 4) if in_zone else None

    if in_zone:
        explanation = (
            f"Moon at {lon:.2f}° ({sign}) is in Via Combusta "
            f"(15° Libra – 15° Scorpio, 195°–225°). "
            f"{degrees_into:.2f}° into the zone. Moon greatly weakened."
        )
    else:
        if lon < _VIA_COMBUSTA_START:
            dist = round(_VIA_COMBUSTA_START - lon, 4)
            explanation = (
                f"Moon at {lon:.2f}° ({sign}) is {dist:.2f}° before Via Combusta."
            )
        else:
            dist = round(lon - _VIA_COMBUSTA_END, 4)
            explanation = (
                f"Moon at {lon:.2f}° ({sign}) is {dist:.2f}° past Via Combusta."
            )

    return {
        "is_via_combusta": in_zone,
        "moon_longitude": round(lon, 4),
        "moon_sign": sign,
        "zone_start": _VIA_COMBUSTA_START,
        "zone_end": _VIA_COMBUSTA_END,
        "degrees_into_zone": degrees_into,
        "explanation": explanation,
    }


# ============================================================
# FIXED STARS
# ============================================================

# Tropical longitudes for epoch J2000.0 (precession ≈ 50.3"/yr from catalog).
# Values here are traditional / approximate positions used in classical horary,
# accurate to within ~1° for the early-21st-century window.
# Source: Robson "Fixed Stars and Constellations" (1923), updated for J2000.
FIXED_STARS: Dict[str, Dict[str, Any]] = {
    "Algol": {
        "lon": 56.3,  # 26°18' Taurus
        "nature": "Saturn/Mars",
        "effect": "Violence, losing one's head, misfortune",
        "magnitude": 2.1,
    },
    "Pleiades": {
        "lon": 60.0,  # 0° Gemini
        "nature": "Moon/Mars",
        "effect": "Injuries to the face or eyes, sorrow",
        "magnitude": 1.6,
    },
    "Aldebaran": {
        "lon": 69.9,  # 9°54' Gemini
        "nature": "Mars",
        "effect": "Honor, intelligence, courage — but danger",
        "magnitude": 0.9,
    },
    "Rigel": {
        "lon": 77.0,  # 17° Gemini
        "nature": "Jupiter/Saturn",
        "effect": "Honors, wealth, fortune",
        "magnitude": 0.1,
    },
    "Capella": {
        "lon": 81.9,  # 21°54' Gemini
        "nature": "Mercury/Mars",
        "effect": "Inquisitiveness, restlessness, success",
        "magnitude": 0.1,
    },
    "Sirius": {
        "lon": 104.0,  # 14° Cancer
        "nature": "Jupiter/Mars",
        "effect": "Success, renown, wealth, ardor",
        "magnitude": -1.5,
    },
    "Regulus": {
        "lon": 150.0,  # 0° Virgo (precessed from 29° Leo in earlier epoch)
        "nature": "Jupiter/Mars",
        "effect": "Royal success, honor, power — with risk of downfall",
        "magnitude": 1.3,
    },
    "Spica": {
        "lon": 203.7,  # 23°42' Libra
        "nature": "Venus/Mercury",
        "effect": "Protection, brilliance, fortune, success",
        "magnitude": 0.9,
    },
    "Arcturus": {
        "lon": 203.9,  # 23°54' Libra
        "nature": "Jupiter/Mars",
        "effect": "Riches and honor from the people",
        "magnitude": -0.1,
    },
    "Antares": {
        "lon": 249.7,  # 9°42' Sagittarius
        "nature": "Mars/Jupiter",
        "effect": "Recklessness, obstinacy, clashes — but success through courage",
        "magnitude": 1.0,
    },
    "Vega": {
        "lon": 285.2,  # 15°12' Capricorn
        "nature": "Venus/Mercury",
        "effect": "Luck in politics, music, and creative arts",
        "magnitude": 0.0,
    },
    "Deneb Algedi": {
        "lon": 323.3,  # 23°18' Aquarius
        "nature": "Saturn/Jupiter",
        "effect": "Justice, authority, sorrow and loss",
        "magnitude": 2.8,
    },
    "Fomalhaut": {
        "lon": 333.9,  # 3°54' Pisces
        "nature": "Venus/Mercury",
        "effect": "Fame, idealism, spiritual matters",
        "magnitude": 1.2,
    },
    "Scheat": {
        "lon": 349.1,  # 19°6' Pisces
        "nature": "Mars/Mercury",
        "effect": "Disasters, imprisonment, drowning",
        "magnitude": 2.4,
    },
}

_FIXED_STAR_DEFAULT_ORB = 1.0  # traditional horary: 1° orb for fixed stars


def check_fixed_star_conjunctions(
    planet_lon: float,
    orb: float = _FIXED_STAR_DEFAULT_ORB,
    stars: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Find fixed-star conjunctions for a given planetary longitude.

    Only conjunctions are meaningful in traditional horary (not trines etc.).
    The orb is typically 1° (strict) per Lilly and Frawley.

    Args:
        planet_lon: Ecliptic longitude of the planet (degrees, 0–360).
        orb:        Maximum conjunction orb in degrees (default 1°).
        stars:      Optional custom star catalogue.  Defaults to FIXED_STARS.

    Returns:
        List of dicts, one per conjunct star, sorted by ascending orb:
        [
            {
                'star':      str,   # star name
                'star_lon':  float, # star's longitude
                'orb':       float, # actual separation
                'nature':    str,   # planetary nature (e.g. 'Jupiter/Mars')
                'effect':    str,   # traditional interpretation
                'magnitude': float, # visual magnitude
            },
            ...
        ]
        Empty list if no stars are within orb.
    """
    catalog = stars if stars is not None else FIXED_STARS
    p = planet_lon % 360.0
    results = []

    for name, data in catalog.items():
        star_lon = data["lon"] % 360.0
        # shortest arc
        raw = abs(p - star_lon) % 360.0
        separation = raw if raw <= 180.0 else 360.0 - raw
        if separation <= orb:
            results.append(
                {
                    "star": name,
                    "star_lon": star_lon,
                    "orb": round(separation, 4),
                    "nature": data.get("nature", ""),
                    "effect": data.get("effect", ""),
                    "magnitude": data.get("magnitude", None),
                }
            )

    results.sort(key=lambda x: x["orb"])
    return results


# ============================================================
# LORD OF THE HOUR
# ============================================================

# Chaldean (descending) planetary order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
_CHALDEAN_ORDER: List[str] = [
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
]

# Day-of-week rulers (Monday=0 in Python weekday(); map to Chaldean planets)
# Traditional: Sunday=Sun, Monday=Moon, Tuesday=Mars, Wednesday=Mercury,
#              Thursday=Jupiter, Friday=Venus, Saturday=Saturn
_DAY_RULERS: List[str] = [
    "Moon",  # Monday   (weekday 0)
    "Mars",  # Tuesday  (weekday 1)
    "Mercury",  # Wednesday(weekday 2)
    "Jupiter",  # Thursday (weekday 3)
    "Venus",  # Friday   (weekday 4)
    "Saturn",  # Saturday (weekday 5)
    "Sun",  # Sunday   (weekday 6)
]


def calculate_lord_of_hour(
    question_jd: float,
    sunrise_jd: float,
    sunset_jd: float,
    weekday: int,
) -> Dict[str, Any]:
    """
    Calculate the Lord of the Hour using the Chaldean planetary-hour system.

    Planetary hours are unequal ("seasonal hours"): each half of the day is
    divided into 12 equal segments.  The ruler of hour 1 of each day is the
    day ruler; subsequent hours cycle through the Chaldean order.

    Rules (Lilly CA, Book I):
    - If question_jd is between sunrise and sunset: daytime hours.
    - If before sunrise or after sunset: nighttime hours.
    - Radicality: the chart is more radical if the Ascendant's ruler equals
      the Lord of the Hour, or is of the same triplicity.

    Args:
        question_jd:  Julian Day Number of the moment of the question.
        sunrise_jd:   Julian Day Number of sunrise on the same calendar day.
        sunset_jd:    Julian Day Number of sunset on the same calendar day.
        weekday:      Python weekday() of the question date (0=Mon … 6=Sun).

    Returns:
        {
            'lord_of_hour':     str,    # planet name
            'hour_number':      int,    # 1-based planetary hour index
            'is_day':           bool,   # True if question is in daytime hours
            'day_ruler':        str,    # ruler of the day
            'hour_length_min':  float,  # length of one planetary hour in minutes
            'explanation':      str,
        }
    """
    day_ruler = _DAY_RULERS[weekday % 7]
    day_ruler_idx = _CHALDEAN_ORDER.index(day_ruler)

    # Sunset itself is the first night hour, not the last day hour.
    is_day = sunrise_jd <= question_jd < sunset_jd

    if is_day:
        period_start = sunrise_jd
        period_length_jd = sunset_jd - sunrise_jd
    else:
        if question_jd < sunrise_jd:
            # Before today's sunrise: night period started at previous sunset.
            # Approximate: previous sunset ≈ sunset_jd − 1 day.
            period_start = sunset_jd - 1.0
        else:
            # After today's sunset: night period starts at today's sunset.
            period_start = sunset_jd
        period_length_jd = 1.0 - (sunset_jd - sunrise_jd)  # night fraction of day

    # Length of one planetary hour (in Julian Day fractions)
    hour_len_jd = period_length_jd / 12.0 if period_length_jd > 0 else 1.0 / 24.0
    hour_len_min = round(hour_len_jd * 24.0 * 60.0, 4)

    # Which planetary hour are we in? (0-based within period)
    elapsed = question_jd - period_start
    if hour_len_jd > 0:
        # Add tiny epsilon (≈8.6ms) to absorb floating-point cancellation error
        # that arises from subtracting large JD values.  The ULP at JD≈2451545
        # is ~4.7e-10; after dividing by hour_len, error scales to ~1e-8.
        # 1e-7 JD is astronomically negligible for horary purposes.
        hour_index_0 = int(elapsed / hour_len_jd + 1e-7)
    else:
        hour_index_0 = 0
    hour_index_0 = max(0, min(11, hour_index_0))  # clamp to 0–11

    # Daytime hours continue the Chaldean sequence from hour 1 of the day.
    # Night hours follow immediately after the 12th day hour.
    if is_day:
        offset = hour_index_0
    else:
        offset = 12 + hour_index_0  # night hours are 13th–24th of the 24-hour cycle

    lord_idx = (day_ruler_idx + offset) % 7
    lord = _CHALDEAN_ORDER[lord_idx]
    hour_number = 1 + (hour_index_0 if is_day else 12 + hour_index_0)

    period_name = "day" if is_day else "night"
    explanation = (
        f"Lord of the Hour: {lord} (#{hour_number}, {period_name} hour). "
        f"Day ruler: {day_ruler}. Hour length: {hour_len_min:.1f} min."
    )

    return {
        "lord_of_hour": lord,
        "hour_number": hour_number,
        "is_day": is_day,
        "day_ruler": day_ruler,
        "hour_length_min": hour_len_min,
        "explanation": explanation,
    }
