# Relocation calculation - integrated with input_pipeline
import sys
from pathlib import Path

# Add input_pipeline to path if not already available
input_pipeline_path = Path(__file__).parent.parent.parent / "input_pipeline"
if str(input_pipeline_path) not in sys.path:
    sys.path.insert(0, str(input_pipeline_path))

# Imports must be after path setup to find input_pipeline
# pyright: reportMissingModuleSource=false
from input_pipeline import resolve_city, get_global_cache  # noqa: E402
from input_pipeline.models import ResolvedPlace  # noqa: E402


def relocate_coords(place: str) -> dict:
    """
    Resolve place name to coordinates using input_pipeline.

    Uses cached geocoding with 100+ city aliases (Moscow, Tokyo, etc.)
    Falls back to Nominatim API for unknown cities.

    Args:
        place: City name (English or Cyrillic, e.g., "Moscow", "Москва", "Tokyo")

    Returns:
        dict: {"lat": float, "lon": float, "timezone": str, "confidence": float}

    Raises:
        ValueError: If place cannot be resolved

    Example:
        >>> coords = relocate_coords("Moscow")
        >>> coords
        {"lat": 55.7558, "lon": 37.6173, "timezone": "Europe/Moscow", "confidence": 0.95}
    """
    cache = get_global_cache()
    resolved: ResolvedPlace = resolve_city(place, cache)

    if resolved.confidence < 0.3:
        raise ValueError(
            f"Could not reliably resolve place '{place}'. "
            f"Confidence: {resolved.confidence:.0%}. "
            f"Try using a major city name or coordinates directly."
        )

    return {
        "lat": resolved.lat,
        "lon": resolved.lon,
        "timezone": resolved.tz_name,  # Fixed: was 'timezone', should be 'tz_name'
        "confidence": resolved.confidence,
    }
