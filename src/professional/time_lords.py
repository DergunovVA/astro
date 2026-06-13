"""
Time Lord Techniques: Annual Profections and Firdaria.

Annual Profections (Hellenistic, per Abu Ma'shar):
  - Each year of life the chart "profects" one house forward.
  - Year 0 (birth): 1st house is activated.
  - Year 1: 2nd house. Year 12: back to 1st. Cycle repeats every 12 years.
  - The ruling planet of the activated sign = Lord of the Year.

Firdaria (Medieval, per Abu Ma'shar / Lilly-era):
  - Chaldean planets rule sequential time periods from birth.
  - Day chart order: Sun 10y → Venus 8y → Mercury 13y → Moon 9y → Saturn 11y → Jupiter 12y → Mars 7y
  - Night chart order: Moon 9y → Saturn 11y → Jupiter 12y → Mars 7y → Sun 10y → Venus 8y → Mercury 13y
  - Each period is further subdivided into sub-periods (7 sub-lords × proportional months).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional

from core.dignities import DOMICILE, ZODIAC_SIGNS

# ─────────────────────────────────────────────────────────────────────────────
# SIGN RULERS (traditional 7 planets only)
# ─────────────────────────────────────────────────────────────────────────────

_SIGN_RULER: Dict[str, str] = {
    "Aries":       "Mars",
    "Taurus":      "Venus",
    "Gemini":      "Mercury",
    "Cancer":      "Moon",
    "Leo":         "Sun",
    "Virgo":       "Mercury",
    "Libra":       "Venus",
    "Scorpio":     "Mars",      # traditional (not Pluto)
    "Sagittarius": "Jupiter",
    "Capricorn":   "Saturn",
    "Aquarius":    "Saturn",    # traditional (not Uranus)
    "Pisces":      "Jupiter",   # traditional (not Neptune)
}

# Keywords per house (for interpretation)
_HOUSE_THEMES: Dict[int, str] = {
    1:  "Self, identity, vitality, new beginnings",
    2:  "Resources, money, values, possessions",
    3:  "Communication, siblings, short journeys, learning",
    4:  "Home, family, roots, property, endings",
    5:  "Creativity, children, romance, pleasures",
    6:  "Health, daily routine, service, illness, work",
    7:  "Partnerships, marriage, open enemies, contracts",
    8:  "Death, transformation, shared resources, occult",
    9:  "Travel, philosophy, religion, higher education",
    10: "Career, reputation, authority, public life",
    11: "Friends, allies, groups, hopes, social networks",
    12: "Hidden enemies, isolation, undoing, secret matters",
}

# ─────────────────────────────────────────────────────────────────────────────
# ANNUAL PROFECTIONS
# ─────────────────────────────────────────────────────────────────────────────


def annual_profections(
    birth_date: date | str,
    target_date: date | str | None = None,
    asc_sign: str | None = None,
    house_signs: List[str] | None = None,
) -> Dict[str, Any]:
    """Calculate Annual Profections.

    Each completed year of life activates the next house in sequence
    (1st → 2nd → … → 12th → 1st again).  The lord of the activated sign
    is the "Lord of the Year" whose transits and natal placement will be
    especially meaningful for the native throughout that birthday year.

    Args:
        birth_date: Date of birth (date object or ISO string "YYYY-MM-DD").
        target_date: The date to calculate for (defaults to today).
        asc_sign: Zodiac sign on the 1st house cusp (e.g. "Aries").
                  If provided and house_signs is None, signs are generated
                  in zodiac order starting from asc_sign.
        house_signs: Explicit list of 12 sign names for H1..H12
                     (overrides asc_sign auto-generation).

    Returns:
        {
            "age": int,                      # completed years at target_date
            "profected_house": int,          # 1-12
            "profected_sign": str | None,    # sign on that house (if known)
            "lord_of_year": str | None,      # ruler of profected sign
            "house_themes": str,             # interpretive keywords
            "profection_degree": float,      # exact degree reached (age * 30° mod 360°)
            "next_birthday": str,            # ISO date of next birthday (when profection changes)
        }
    """
    # Normalise dates
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)

    # Age in completed years
    age = _age_in_years(birth_date, target_date)

    # Profected house (0-indexed → 1-indexed)
    house_idx = age % 12           # 0-11
    profected_house = house_idx + 1

    # Exact zodiac degree: each year = 30°, each month ≈ 2.5°
    profection_degree = (age * 30.0) % 360.0

    # Determine sign on the profected house
    profected_sign: Optional[str] = None
    if house_signs:
        if len(house_signs) >= 12:
            profected_sign = house_signs[house_idx]
    elif asc_sign and asc_sign in ZODIAC_SIGNS:
        asc_idx = ZODIAC_SIGNS.index(asc_sign)
        sign_idx = (asc_idx + house_idx) % 12
        profected_sign = ZODIAC_SIGNS[sign_idx]

    lord_of_year: Optional[str] = None
    if profected_sign:
        lord_of_year = _SIGN_RULER.get(profected_sign)

    # Next birthday
    try:
        next_bday = birth_date.replace(year=target_date.year + (
            1 if (target_date.month, target_date.day) >= (birth_date.month, birth_date.day)
            else 0
        ))
    except ValueError:
        # Feb 29 edge case
        next_bday = birth_date.replace(year=target_date.year + 1, day=28)

    return {
        "age": age,
        "profected_house": profected_house,
        "profected_sign": profected_sign,
        "lord_of_year": lord_of_year,
        "house_themes": _HOUSE_THEMES[profected_house],
        "profection_degree": round(profection_degree, 4),
        "next_birthday": next_bday.isoformat(),
    }


def profection_timeline(
    birth_date: date | str,
    years: int = 72,
    asc_sign: str | None = None,
    house_signs: List[str] | None = None,
) -> List[Dict[str, Any]]:
    """Return profection data for each year of life up to `years`.

    Args:
        birth_date: Date of birth.
        years: Number of years to compute (default 72).
        asc_sign: Sign on 1st house (for sign/lord derivation).
        house_signs: Explicit list of 12 house signs.

    Returns:
        List of dicts, one per year, each matching the structure
        returned by annual_profections().
    """
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)

    timeline = []
    for yr in range(years):
        try:
            target = _add_years(birth_date, yr)
        except ValueError:
            target = birth_date.replace(year=birth_date.year + yr, day=28)
        row = annual_profections(birth_date, target, asc_sign, house_signs)
        row["year"] = target.isoformat()
        timeline.append(row)
    return timeline


# ─────────────────────────────────────────────────────────────────────────────
# FIRDARIA  (Medieval planetary periods)
# ─────────────────────────────────────────────────────────────────────────────

# Period lengths in years (Chaldean-order planetary rulership)
_FIRDARIA_YEARS: Dict[str, float] = {
    "Sun":     10.0,
    "Venus":    8.0,
    "Mercury": 13.0,
    "Moon":     9.0,
    "Saturn":  11.0,
    "Jupiter": 12.0,
    "Mars":     7.0,
}

# Sequence for day/night charts
_FIRDARIA_DAY_ORDER   = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]
_FIRDARIA_NIGHT_ORDER = ["Moon","Saturn","Jupiter","Mars","Sun","Venus","Mercury"]

# Chaldean order for sub-periods (same list, always)
_CHALDEAN_SUB = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]


def firdaria(
    birth_date: date | str,
    is_day_chart: bool = True,
    target_date: date | str | None = None,
) -> Dict[str, Any]:
    """Calculate the active Firdaria period and sub-period.

    Args:
        birth_date: Date of birth.
        is_day_chart: True if the Sun was above the horizon at birth.
        target_date: Date to calculate for (defaults to today).

    Returns:
        {
            "age_decimal": float,           # exact age in decimal years
            "major_period": str,            # name of major Firdaria lord
            "major_start_date": str,        # ISO date major period began
            "major_end_date": str,          # ISO date major period ends
            "major_years": float,           # total length of major period
            "sub_period": str,              # name of sub-period lord
            "sub_start_date": str,
            "sub_end_date": str,
            "sub_years": float,
            "full_sequence": list[dict],    # all periods for lifetime reference
        }
    """
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)

    order = _FIRDARIA_DAY_ORDER if is_day_chart else _FIRDARIA_NIGHT_ORDER
    total_cycle = sum(_FIRDARIA_YEARS[p] for p in order)  # 70 years, then repeats

    age_decimal = _age_decimal(birth_date, target_date)

    # Normalise age within the 70-year cycle
    age_in_cycle = age_decimal % total_cycle

    # Find major period
    cursor = 0.0
    major_lord = order[0]
    major_start_yr = 0.0
    for planet in order:
        period_len = _FIRDARIA_YEARS[planet]
        if cursor <= age_in_cycle < cursor + period_len:
            major_lord = planet
            major_start_yr = cursor
            break
        cursor += period_len

    major_len = _FIRDARIA_YEARS[major_lord]
    major_start_date = _add_fractional_years(birth_date, major_start_yr + (age_decimal - age_in_cycle))
    major_end_date   = _add_fractional_years(birth_date, major_start_yr + (age_decimal - age_in_cycle) + major_len)

    # Find sub-period within major period
    age_in_major = age_in_cycle - major_start_yr
    sub_len_each  = major_len / 7.0  # each sub-period = 1/7 of major
    sub_index     = int(age_in_major / sub_len_each)
    sub_index     = min(sub_index, 6)

    # Sub-lords follow Chaldean order starting from the major lord's position
    major_pos_in_chaldean = _CHALDEAN_SUB.index(major_lord) if major_lord in _CHALDEAN_SUB else 0
    sub_lord = _CHALDEAN_SUB[(major_pos_in_chaldean + sub_index) % 7]

    sub_start_offset = major_start_yr + (age_decimal - age_in_cycle) + sub_index * sub_len_each
    sub_start_date   = _add_fractional_years(birth_date, sub_start_offset)
    sub_end_date     = _add_fractional_years(birth_date, sub_start_offset + sub_len_each)

    # Full sequence for reference
    full_sequence = []
    yr_cursor = 0.0
    for planet in order:
        pl = _FIRDARIA_YEARS[planet]
        full_sequence.append({
            "planet": planet,
            "start_age": round(yr_cursor, 2),
            "end_age":   round(yr_cursor + pl, 2),
            "years":     pl,
        })
        yr_cursor += pl

    return {
        "age_decimal":       round(age_decimal, 4),
        "major_period":      major_lord,
        "major_start_date":  major_start_date.isoformat(),
        "major_end_date":    major_end_date.isoformat(),
        "major_years":       major_len,
        "sub_period":        sub_lord,
        "sub_start_date":    sub_start_date.isoformat(),
        "sub_end_date":      sub_end_date.isoformat(),
        "sub_years":         round(sub_len_each, 4),
        "full_sequence":     full_sequence,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────


def _age_in_years(birth: date, target: date) -> int:
    """Completed integer years between birth and target."""
    age = target.year - birth.year
    if (target.month, target.day) < (birth.month, birth.day):
        age -= 1
    return max(0, age)


def _age_decimal(birth: date, target: date) -> float:
    """Exact age as decimal years (365.25-day year)."""
    delta = (target - birth).days
    return delta / 365.25


def _add_years(d: date, years: int) -> date:
    """Add integer years to a date."""
    return d.replace(year=d.year + years)


def _add_fractional_years(d: date, years: float) -> date:
    """Add fractional years (365.25-day year) to a date."""
    days = int(years * 365.25)
    return d + timedelta(days=days)
