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
    
    Supported formats:
    - ISO: 2000-01-15, 2000/01/15
    - European: 15.01.2000, 15-01-2000, 15/01/2000
    - US: 01-15-2000, 01/15/2000
    - Compact: 20000115
    - Text: 15 Jan 2000, Jan 15 2000, 15 January 2000
    - 2-digit year: 15.01.00, 01/15/00
    """
    warnings: list[ParseWarning] = []

    date_str = date_str.strip()
    
    # 1) fast path ISO
    try:
        d = datetime.fromisoformat(date_str).date()  # accepts YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
    except Exception:
        # 2) Try compact format YYYYMMDD
        try:
            if len(date_str) == 8 and date_str.isdigit():
                d = datetime.strptime(date_str, "%Y%m%d").date()
                warnings.append(ParseWarning(
                    code="LOW_CONFIDENCE_DATE",
                    message="Date parsed from compact format (YYYYMMDD)"
                ))
            else:
                raise ValueError("Not compact format")
        except ValueError:
            # 3) Try common formats (most to least preferred)
            formats = [
                ("%Y/%m/%d", "ISO with slashes"),          # 2000/01/15
                ("%d.%m.%Y", "DD.MM.YYYY"),                # 15.01.2000
                ("%d-%m-%Y", "DD-MM-YYYY"),                # 15-01-2000
                ("%d/%m/%Y", "DD/MM/YYYY"),                # 15/01/2000
                ("%m-%d-%Y", "MM-DD-YYYY (US)"),           # 01-15-2000
                ("%m/%d/%Y", "MM/DD/YYYY (US)"),           # 01/15/2000
                ("%d %b %Y", "DD Mon YYYY"),               # 15 Jan 2000
                ("%b %d %Y", "Mon DD YYYY"),               # Jan 15 2000
                ("%d %B %Y", "DD Month YYYY"),             # 15 January 2000
                ("%B %d %Y", "Month DD YYYY"),             # January 15 2000
                # 2-digit year variants
                ("%d.%m.%y", "DD.MM.YY"),                  # 15.01.00 → 1900 or 2000
                ("%d-%m.%y", "DD-MM-YY"),                  # 15-01-00
                ("%d/%m/%y", "DD/MM/YY"),                  # 15/01/00
                ("%m-%d-%y", "MM-DD-YY (US)"),             # 01-15-00
                ("%m/%d/%y", "MM/DD/YY (US)"),             # 01/15/00
            ]
            
            d = None
            matched_format = None
            for fmt, description in formats:
                try:
                    d = datetime.strptime(date_str, fmt).date()
                    matched_format = description
                    warnings.append(ParseWarning(
                        code="LOW_CONFIDENCE_DATE",
                        message=f"Date parsed as {description}"
                    ))
                    break
                except ValueError:
                    continue
            
            if d is None:
                raise ValueError(
                    f"Cannot parse date: {date_str}\n"
                    f"Supported formats:\n"
                    f"  ISO: 2000-01-15, 2000/01/15\n"
                    f"  EU: 15.01.2000, 15-01-2000, 15/01/2000\n"
                    f"  US: 01-15-2000, 01/15/2000\n"
                    f"  Compact: 20000115\n"
                    f"  Text: 15 Jan 2000, Jan 15 2000"
                )

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
