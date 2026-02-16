# Interpretation Layer: Core results → Facts/Signals/Decisions (no calculations)
from models.facts_models import Fact
from models.signals_models import Signal
from models.decisions_models import Decision
from core.core_geometry import (
    calculate_aspects,
    calculate_house_positions,
    planet_in_sign,
)
from typing import List, Dict, Any

ASPECTS_CONFIG = {
    "conjunction": 0,
    "opposition": 180,
    "trine": 120,
    "square": 90,
    "sextile": 60,
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
    from core.core_geometry import calculate_aspects_to_angles

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
