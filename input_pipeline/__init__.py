from __future__ import annotations

from datetime import datetime
from typing import Optional

from .cache import JsonCache
from .models import NormalizedInput, ParseWarning
from .parser_datetime import parse_date_time
from .resolver_city import resolve_city
from .resolver_timezone import resolve_tz_name, make_aware
from .context import InputContext

# Export public API
__all__ = [
    "NormalizedInput",
    "InputContext",
    "ParseWarning",
    "normalize_input",
    "resolve_city",
    "get_global_cache",
    "reset_global_cache",
]

# Global cache singleton
_global_cache: Optional[JsonCache] = None


def get_global_cache() -> JsonCache:
    """
    Get or create global cache singleton.
    
    Thread-safe lazy initialization. Multiple calls return the same instance.
    
    Returns:
        JsonCache instance shared across the application
        
    Example:
        cache = get_global_cache()
        resolved = resolve_city("Moscow", cache)
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = JsonCache()
    return _global_cache


def reset_global_cache() -> None:
    """
    Reset (clear) global cache. Useful for testing.
    
    After calling this, next call to get_global_cache() creates new instance.
    """
    global _global_cache
    _global_cache = None


def normalize_input(date_str: str, time_str: str, place_str: str, tz_override: str | None = None, lat_override: float | None = None, lon_override: float | None = None, locale: str | None = None, strict: bool = False, use_global_cache: bool = True) -> NormalizedInput:
    """
    Normalize raw input (date, time, place) into structured NormalizedInput.
    
    Args:
        date_str: Date in any common format (ISO, European, flexible)
        time_str: Time in HH:MM or HH:MM:SS format
        place_str: City/place name in any language or format
        tz_override: Optional timezone name to override auto-detection
        lat_override: Optional latitude (degrees, -90 to 90) to override place resolution
        lon_override: Optional longitude (degrees, -180 to 180) to override place resolution
        locale: Optional locale for date parsing (e.g., 'en_US')
        strict: If True, fail on any ambiguity/warning instead of fallback
        use_global_cache: If True, use shared global cache (recommended)
                         If False, create local cache for this call
        
    Returns:
        NormalizedInput with all fields populated
        
    Raises:
        ValueError: If date/time/place cannot be parsed, or if strict=True and warnings present
    """
    cache = get_global_cache() if use_global_cache else JsonCache()

    parsed = parse_date_time(date_str, time_str, locale=locale)
    
    # Check strict mode for date/time parsing
    if strict and parsed.warnings:
        warn_msgs = ", ".join([f"{w.code}: {w.message}" for w in parsed.warnings])
        raise ValueError(f"Strict mode: ambiguous date/time: {warn_msgs}")
    
    # Resolve place/coordinates
    if lat_override is not None and lon_override is not None:
        # Use provided coordinates, skip city resolution
        from .models import ResolvedPlace
        rp = ResolvedPlace(
            query=place_str,
            name=place_str,
            country=None,
            lat=lat_override,
            lon=lon_override,
            tz_name=None,
            source="override",
            confidence=1.0,
            warnings=[],
        )
    else:
        # Standard city resolution
        rp = resolve_city(place_str, cache=cache)
    
    # Check strict mode for city resolution
    if strict and rp.warnings:
        warn_msgs = ", ".join([f"{w.code}: {w.message}" for w in rp.warnings])
        raise ValueError(f"Strict mode: ambiguous location: {warn_msgs}")

    tz_hint = tz_override or rp.tz_name
    tz_name, tz_warn, tz_conf = resolve_tz_name(rp.lat, rp.lon, hint=tz_hint)
    
    # Check strict mode for timezone
    if strict and tz_warn:
        warn_msgs = ", ".join([f"{w.code}: {w.message}" for w in tz_warn])
        raise ValueError(f"Strict mode: ambiguous timezone: {warn_msgs}")

    local_naive = datetime.fromisoformat(f"{parsed.date_iso}T{parsed.time_iso}")
    local_dt, utc_dt, offset_min = make_aware(local_naive, tz_name)

    warnings = []
    warnings.extend(parsed.warnings)
    warnings.extend(rp.warnings)
    warnings.extend(tz_warn)

    confidence = min(parsed.confidence, rp.confidence, tz_conf)

    return NormalizedInput(
        raw_date=date_str,
        raw_time=time_str,
        raw_place=place_str,
        local_dt=local_dt,
        utc_dt=utc_dt,
        tz_name=tz_name,
        lat=rp.lat,
        lon=rp.lon,
        place_name=rp.name,
        country=rp.country,
        confidence=confidence,
        warnings=warnings,
    )
