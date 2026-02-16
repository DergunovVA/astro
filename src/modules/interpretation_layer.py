# Interpretation Layer: Core results → Facts/Signals/Decisions (no calculations)
from models.facts_models import Fact
from models.signals_models import Signal
from models.decisions_models import Decision
from core.core_geometry import (
    calculate_aspects,
    calculate_house_positions,
    planet_in_sign,
)
from core.dignities import (
    calculate_essential_dignity,
    is_day_chart,
    get_dispositor_chain,
    find_mutual_receptions,
)
from typing import List, Dict, Any

ASPECTS_CONFIG = {
    # Major aspects
    "conjunction": 0,
    "opposition": 180,
    "trine": 120,
    "square": 90,
    "sextile": 60,
    # Minor aspects (basic)
    "semisextile": 30,
    "semisquare": 45,
    "sesquiquadrate": 135,
    "quincunx": 150,
    # Minor aspects (advanced)
    "quintile": 72,  # 5th harmonic - creativity, talent
    "biquintile": 144,  # 5th harmonic
    "septile": 51.43,  # 7th harmonic - fate, spiritual
    "novile": 40,  # 9th harmonic - completion, wisdom
}

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


def facts_from_calculation(calc_result: Dict[str, Any]) -> List[Fact]:
    """Transform core calculation (floats) into Fact objects (no math).

    Supports both simple planet data (Dict[str, float]) and extended data
    (Dict[str, dict]) with retrograde indicators.
    """
    facts = []

    # Planet positions (sign + house)
    planets = calc_result["planets"]
    houses = calc_result["houses"]

    # Normalize planets to dict format for uniform processing
    # Handle both old format (float) and new format (dict with "longitude")
    normalized_planets = {}
    planet_metadata = {}  # Store retrograde and other metadata

    for planet, data in planets.items():
        if isinstance(data, dict):
            # Extended format: {"longitude": 123.45, "retrograde": True, ...}
            normalized_planets[planet] = data["longitude"]
            planet_metadata[planet] = data
        else:
            # Simple format: just float
            normalized_planets[planet] = data
            planet_metadata[planet] = {"longitude": data, "retrograde": False}

    planet_houses = calculate_house_positions(houses, normalized_planets)

    for planet, lon in normalized_planets.items():
        sign_idx = planet_in_sign(lon)
        sign = ZODIAC_SIGNS[sign_idx]
        house = planet_houses[planet]

        # Get metadata
        metadata = planet_metadata.get(planet, {})
        is_retrograde = metadata.get("retrograde", False)

        # Build details
        details = {"longitude": lon, "house": house}

        # Add retrograde indicator if applicable
        if is_retrograde:
            details["retrograde"] = True
            details["symbol"] = f"{planet}℞"  # Add retrograde symbol

        facts.append(
            Fact(
                id=f"{planet}_position",
                type="planet_in_sign",
                object=planet,
                value=f"{sign}",
                details=details,
            )
        )

    # Essential Dignities
    # Determine if day or night chart
    sun_lon = normalized_planets.get("Sun", 0.0)
    asc_lon = houses[0]  # 1st house cusp = Ascendant
    is_day = is_day_chart(sun_lon, asc_lon)

    # Calculate dignities for each planet
    for planet, lon in normalized_planets.items():
        dignity = calculate_essential_dignity(planet, lon, is_day)

        facts.append(
            Fact(
                id=f"{planet}_dignity",
                type="essential_dignity",
                object=planet,
                value=dignity["dignity_level"],
                details={
                    "score": dignity["score"],
                    "domicile": dignity["domicile"],
                    "exaltation": dignity["exaltation"],
                    "detriment": dignity["detriment"],
                    "fall": dignity["fall"],
                    "triplicity": dignity["triplicity"],
                },
            )
        )

    # Dispositor chains
    dispositor_chains = get_dispositor_chain(normalized_planets)
    for planet, chain in dispositor_chains.items():
        if chain:  # Only if there's a chain
            facts.append(
                Fact(
                    id=f"{planet}_dispositor_chain",
                    type="dispositor",
                    object=planet,
                    value=chain[0] if chain else None,  # First dispositor
                    details={"chain": chain, "has_cycle": "(cycle)" in " ".join(chain)},
                )
            )

    # Mutual receptions
    mutual_receptions = find_mutual_receptions(normalized_planets)
    for p1, p2, rec_type in mutual_receptions:
        facts.append(
            Fact(
                id=f"{p1}_{p2}_reception",
                type="mutual_reception",
                object=f"{p1}-{p2}",
                value=rec_type,
                details={
                    "planets": [p1, p2],
                    "type": rec_type,  # "mutual_domicile" or "mixed"
                },
            )
        )

    # House cusps
    for i, cusp in enumerate(houses):
        facts.append(
            Fact(
                id=f"house_{i + 1}_cusp",
                type="house_cusp",
                object=f"House {i + 1}",
                value=str(round(cusp, 2)),
                details={},
            )
        )

    # Aspects (now returns 5-tuple with aspect category)
    aspects = calculate_aspects(planets, ASPECTS_CONFIG)
    for p1, p2, asp_name, orb, asp_category in aspects:
        facts.append(
            Fact(
                id=f"{p1}_{p2}_{asp_name}",
                type="aspect",
                object=f"{p1}-{p2}",
                value=asp_name,
                details={
                    "orb": round(orb, 2),
                    "category": asp_category,  # "major" or "minor"
                },
            )
        )

    # Aspects to angles (ASC, DESC, MC, IC)
    from core.core_geometry import (
        calculate_aspects_to_angles,
        calculate_aspects_to_house_cusps,
    )

    angle_aspects = calculate_aspects_to_angles(planets, houses, ASPECTS_CONFIG)
    for planet, angle, asp_name, orb, asp_category in angle_aspects:
        facts.append(
            Fact(
                id=f"{planet}_{angle}_{asp_name}",
                type="aspect_to_angle",
                object=f"{planet}-{angle}",
                value=asp_name,
                details={
                    "orb": round(orb, 2),
                    "category": asp_category,
                    "angle": angle,  # Which angle: Ascendant, Midheaven, etc.
                },
            )
        )

    # Aspects to house cusps (all 12 houses)
    cusp_aspects = calculate_aspects_to_house_cusps(
        planets, houses, ASPECTS_CONFIG, orb=6.0
    )
    for planet, house_num, asp_name, orb, asp_category in cusp_aspects:
        facts.append(
            Fact(
                id=f"{planet}_house{house_num}_{asp_name}",
                type="aspect_to_cusp",
                object=f"{planet}-House{house_num}",
                value=asp_name,
                details={
                    "orb": round(orb, 2),
                    "category": asp_category,
                    "house": house_num,
                },
            )
        )

    # Special points (Lilith, Vertex, East Point, Parts)
    special_points = calc_result.get("special_points", {})
    for point_name, longitude in special_points.items():
        sign_idx = planet_in_sign(longitude)
        sign = ZODIAC_SIGNS[sign_idx]

        # Calculate house position for special point
        house = None
        for h in range(12):
            next_h = (h + 1) % 12
            cusp = houses[h]
            next_cusp = houses[next_h]

            # Handle wrapping around 360°
            if cusp < next_cusp:
                if cusp <= longitude < next_cusp:
                    house = h + 1
                    break
            else:  # Wraps around 0°
                if longitude >= cusp or longitude < next_cusp:
                    house = h + 1
                    break

        if house is None:
            house = 1  # Fallback

        facts.append(
            Fact(
                id=f"{point_name}_position",
                type="special_point",
                object=point_name,
                value=f"{sign}",
                details={
                    "longitude": round(longitude, 2),
                    "house": house,
                },
            )
        )

    return facts


def signals_from_facts(facts: List[Fact]) -> List[Signal]:
    """Aggregate facts into signals (no calculations, just grouping)."""
    # Demo: simple aggregation
    has_hard_aspects = any(
        f.type == "aspect" and f.value in ["square", "opposition"] for f in facts
    )
    intensity = "high" if has_hard_aspects else "medium"

    return [
        Signal(
            id="chart_intensity",
            intensity=intensity,
            domain="general",
            period="natal",
            sources=[f.id for f in facts[:3]],
        )
    ]


def decisions_from_signals(signals: List[Signal]) -> List[Decision]:
    """Form decisions from signals (no calculations)."""
    return [
        Decision(
            id="general_assessment",
            summary="Chart is formed, ready for interpretation",
            signals=[s.id for s in signals],
            fatal=False,
        )
    ]
