from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

from .models import ParseWarning


@dataclass(frozen=True)
class ParsedDateTime:
    date_iso: str      # YYYY-MM-DD
    time_iso: str      # HH:MM:SS
    confidence: float
    warnings: list[ParseWarning]


def parse_date_time(date_str: str, time_str: str, locale: Optional[str] = None) -> ParsedDateTime:
    """
    Parse date/time from messy user input.
    Core rule: returns normalized ISO strings, not datetime yet.
    Validates date is within astrologically reasonable range: 1800-2300.
    """
    warnings: list[ParseWarning] = []

    # 1) fast path ISO
    try:
        d = datetime.fromisoformat(date_str).date()  # accepts YYYY-MM-DD
    except Exception:
        # 2) fallback - try common formats
        for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d.%m.%y", "%d/%m/%y"]:
            try:
                d = datetime.strptime(date_str.strip(), fmt).date()
                warnings.append(ParseWarning(
                    code="LOW_CONFIDENCE_DATE",
                    message=f"Date parsed with format {fmt} (not ISO)"
                ))
                break
            except ValueError:
                continue
        else:
            # If all formats failed, raise error (don't use dateparser to avoid strptime issues)
            raise ValueError(f"Cannot parse date: {date_str}")

    # 3) CRITICAL: Validate date is within reasonable astrological range
    MIN_DATE = date(1800, 1, 1)   # Earliest sensible birth date
    MAX_DATE = date(2300, 12, 31) # Far future predictions
    TODAY = date.today()

    if d < MIN_DATE:
        raise ValueError(
            f"Date too old: {d.strftime('%Y-%m-%d')} (before {MIN_DATE.strftime('%Y-%m-%d')}). "
            f"Historical dates before 1800 may not have reliable astrological interpretation."
        )
    
    if d > MAX_DATE:
        raise ValueError(
            f"Date too far in future: {d.strftime('%Y-%m-%d')} (after {MAX_DATE.strftime('%Y-%m-%d')}). "
            f"Predictions beyond 2300 are not supported."
        )

    # 4) MEDIUM: Warn if birth date is in the future
    if d > TODAY:
        warnings.append(ParseWarning(
            code="FUTURE_BIRTH_DATE",
            message=f"Birth date is {(d - TODAY).days} days in the future. Results are predictive only."
        ))

    # 5) MEDIUM: Warn if birth date is very old
    age_days = (TODAY - d).days
    if age_days > 70000:  # ~190 years
        warnings.append(ParseWarning(
            code="VERY_OLD_DATE",
            message="Birth date is more than 190 years in the past. Consider verifying accuracy."
        ))
    
    if d.year < 1850:
        warnings.append(ParseWarning(
            code="HISTORICAL_DATE",
            message="Birth before 1850 - astrological calculation reliability is uncertain."
        ))

    # time
    try:
        # allow HH:MM or HH:MM:SS
        time_parts = time_str.strip().split(":")
        if len(time_parts) == 2:
            t = datetime.strptime(time_str.strip(), "%H:%M").time()
        elif len(time_parts) == 3:
            t = datetime.strptime(time_str.strip(), "%H:%M:%S").time()
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    except Exception as e:
        raise ValueError(f"Cannot parse time: {time_str}") from e

    # normalize seconds
    time_iso = t.replace(microsecond=0).strftime("%H:%M:%S")
    date_iso = d.strftime("%Y-%m-%d")

    return ParsedDateTime(
        date_iso=date_iso,
        time_iso=time_iso,
        confidence=0.95,
        warnings=warnings,
    )
