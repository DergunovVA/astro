"""
Comparative charts for the same date/time across multiple cities.

Use cases:
- Relocation astrology: same birth time, different cities
- Transit charts: current date/time in different locations
- Solar returns: same event, observed from different places
"""

from typing import Optional, List
from pathlib import Path
from datetime import datetime
from input_pipeline import normalize_input, InputContext
from modules.astro_adapter import natal_calculation
from modules.interpretation_layer import (
    facts_from_calculation,
    signals_from_facts,
    decisions_from_signals,
)


def load_cities_from_file(filepath: str) -> List[str]:
    """
    Load city names from file (one city per line).

    Args:
        filepath: Path to file with city names

    Returns:
        List of city names (stripped, non-empty lines only)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Cities file not found: {filepath}")

    cities = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            city = line.strip()
            if city and not city.startswith("#"):  # Skip empty lines and comments
                cities.append(city)

    if not cities:
        raise ValueError(f"No cities found in {filepath}")

    return cities


def calculate_chart(
    date_str: str,
    time_str: str,
    place_str: str,
    chart_type: str = "natal",
    tz_override: Optional[str] = None,
    lat_override: Optional[float] = None,
    lon_override: Optional[float] = None,
) -> dict:
    """
    Calculate astrological chart for a single location.

    Args:
        date_str: Date (any supported format)
        time_str: Time (any supported format)
        place_str: City name
        chart_type: Type of chart (natal, transit, solar, relocation)
        tz_override: Optional timezone override
        lat_override: Optional latitude override
        lon_override: Optional longitude override

    Returns:
        Chart dict with input metadata, facts, signals, decisions
    """
    # Normalize input
    ni = normalize_input(
        date_str=date_str,
        time_str=time_str,
        place_str=place_str,
        tz_override=tz_override,
        lat_override=lat_override,
        lon_override=lon_override,
    )
    ctx = InputContext.from_normalized(ni)

    # Calculate
    calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)

    # Interpret
    facts = facts_from_calculation(calc_result)
    signals = signals_from_facts(facts)
    decisions = decisions_from_signals(signals)

    return {
        "place": place_str,
        "chart_type": chart_type,
        "input_metadata": ctx.to_metadata_dict(),
        "facts": [f.model_dump() for f in facts],
        "signals": [s.model_dump() for s in signals],
        "decisions": [d.model_dump() for d in decisions],
        "planets": calc_result["planets"],
        "houses": calc_result["houses"],
    }


def comparative_charts(
    date_str: str,
    time_str: str,
    cities: List[str],
    chart_type: str = "natal",
    tz_override: Optional[str] = None,
) -> dict:
    """
    Calculate astrological charts for the same date/time in multiple cities.

    Args:
        date_str: Date
        time_str: Time
        cities: List of city names
        chart_type: Type of chart (natal, transit, solar, relocation)
        tz_override: Optional timezone override (applies to all cities)

    Returns:
        Dict with metadata and array of charts

    Raises:
        ValueError: If any city cannot be resolved
    """
    charts = []
    errors = []

    for place in cities:
        try:
            chart = calculate_chart(
                date_str=date_str,
                time_str=time_str,
                place_str=place,
                chart_type=chart_type,
                tz_override=tz_override,
            )
            charts.append(chart)
        except Exception as e:
            errors.append({"place": place, "error": str(e)})

    if not charts:
        raise ValueError(f"Could not calculate charts for any cities: {errors}")

    return {
        "comparative_data": {
            "chart_type": chart_type,
            "date": date_str,
            "time": time_str,
            "cities_count": len(cities),
            "successful": len(charts),
            "failed": len(errors),
            "timestamp": datetime.now().isoformat(),
        },
        "charts": charts,
        "errors": errors if errors else None,
    }
