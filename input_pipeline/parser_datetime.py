from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
