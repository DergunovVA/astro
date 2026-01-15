from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import ParseWarning


def resolve_tz_name(lat: float, lon: float, hint: Optional[str] = None) -> tuple[str, list[ParseWarning], float]:
    """
    Resolve timezone name from coordinates or hint.
    Returns: (tz_name, warnings, confidence)
    """
    warnings: list[ParseWarning] = []
    
    # 1) Use hint if provided (highest priority)
    if hint:
        try:
            from zoneinfo import ZoneInfo
            # Verify it's a valid IANA timezone
            _ = ZoneInfo(hint)
            return hint, warnings, 0.99
        except Exception:
            warnings.append(ParseWarning(
                code="INVALID_TZ_HINT",
                message=f"Invalid timezone name: '{hint}'; falling back to coordinates"
            ))
    
    # 2) Try timezonefinder for coordinates
    try:
        from timezonefinder import TimezoneFinder  # type: ignore
        tf = TimezoneFinder()
        tz = tf.timezone_at(lat=lat, lng=lon)
        
        if tz:
            try:
                from zoneinfo import ZoneInfo
                _ = ZoneInfo(tz)  # Verify validity
                return tz, warnings, 0.90
            except Exception as e:
                warnings.append(ParseWarning(
                    code="INVALID_TZ_FROM_COORDS",
                    message=f"TimezoneFinder returned invalid tz '{tz}': {e}"
                ))
        else:
            warnings.append(ParseWarning(
                code="TZ_COORDS_NOT_FOUND",
                message=f"TimezoneFinder returned None for ({lat}, {lon})"
            ))
    
    except ImportError:
        warnings.append(ParseWarning(
            code="TIMEZONEFINDER_MISSING",
            message="timezonefinder not installed; defaulting to UTC"
        ))
    except Exception as e:
        warnings.append(ParseWarning(
            code="TZ_LOOKUP_FAILED",
            message=f"TimezoneFinder lookup failed: {type(e).__name__}"
        ))
    
    # 3) Fallback to UTC
    return "UTC", warnings, 0.30


def make_aware(local_naive: datetime, tz_name: str) -> tuple[datetime, datetime, int]:
    """
    Create timezone-aware datetimes from naive local datetime and timezone name.
    Returns: (local_aware, utc_aware, utc_offset_minutes)
    
    Raises:
        ValueError: If tz_name is invalid or local_naive is ambiguous (DST)
    """
    from zoneinfo import ZoneInfo
    
    try:
        tz = ZoneInfo(tz_name)
    except Exception as e:
        raise ValueError(f"Invalid timezone name '{tz_name}': {e}") from e
    
    try:
        # Attach timezone info to naive datetime
        # Note: This may raise exception if datetime is ambiguous (DST transition)
        local = local_naive.replace(tzinfo=tz)
        
        # Check if this is an ambiguous time (DST fold)
        # During fall-back, the same local time occurs twice
        if hasattr(local_naive, 'fold'):
            # Try both interpretations if ambiguous
            try:
                utc = local.astimezone(timezone.utc)
            except Exception:
                # If ambiguous, prefer fold=1 (post-transition)
                local = local_naive.replace(tzinfo=tz, fold=1)
                utc = local.astimezone(timezone.utc)
        else:
            utc = local.astimezone(timezone.utc)
        
        offset = int(local.utcoffset().total_seconds() // 60)  # minutes
        return local, utc, offset
    
    except ValueError as e:
        # Re-raise with more context
        raise ValueError(f"Cannot make aware datetime {local_naive} in timezone '{tz_name}': {e}") from e
