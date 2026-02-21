"""Sidereal zodiac calculations and conversions.

This module provides support for sidereal astrology systems, including:
- Ayanamsa calculations (precession correction)
- Tropical to sidereal conversions
- Nakshatra (lunar mansion) calculations
- Vimshottari Dasa period system

Sidereal vs Tropical:
- Tropical zodiac: Fixed to seasons (Aries at spring equinox)
- Sidereal zodiac: Fixed to stars (accounts for precession)
- Ayanamsa: The current angular distance between them (~24° in 2000 CE)

Used primarily in Vedic (Jyotish) astrology traditions.
"""

import swisseph as swe
from typing import Dict, List, Any, Optional
from datetime import datetime


# Supported ayanamsa systems
AYANAMSAS = {
    "lahiri": {
        "name": "Lahiri (Chitrapaksha)",
        "constant": swe.SIDM_LAHIRI,
        "description": "Official ayanamsa of Indian Government (1956)",
    },
    "raman": {
        "name": "B.V. Raman",
        "constant": swe.SIDM_RAMAN,
        "description": "Based on B.V. Raman's calculations",
    },
    "krishnamurti": {
        "name": "Krishnamurti",
        "constant": swe.SIDM_KRISHNAMURTI,
        "description": "KP System ayanamsa (Krishnamurti Paddhati)",
    },
    "fagan_bradley": {
        "name": "Fagan-Bradley",
        "constant": swe.SIDM_FAGAN_BRADLEY,
        "description": "Western sidereal astrology (Cyril Fagan)",
    },
}


def calculate_ayanamsa(jd: float, ayanamsa_type: str = "lahiri") -> float:
    """Calculate ayanamsa (precession correction) for given Julian Day.

    The ayanamsa represents the angular distance between the tropical and
    sidereal zodiacs due to the precession of the equinoxes. It increases
    approximately 1° every 72 years.

    Args:
        jd: Julian Day (use datetime_to_jd() for conversion)
        ayanamsa_type: Type of ayanamsa system to use
            - 'lahiri': Official Indian Government (default)
            - 'raman': B.V. Raman system
            - 'krishnamurti': KP System
            - 'fagan_bradley': Western sidereal

    Returns:
        Ayanamsa value in degrees (e.g., 24.15° for year 2000)

    Raises:
        ValueError: If ayanamsa_type is not supported

    Example:
        >>> from input_pipeline.parser_datetime import datetime_to_jd
        >>> jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        >>> ayanamsa = calculate_ayanamsa(jd, 'lahiri')
        >>> print(f"Lahiri ayanamsa: {ayanamsa:.2f}°")
        Lahiri ayanamsa: 23.85°
    """
    if ayanamsa_type not in AYANAMSAS:
        supported = ", ".join(AYANAMSAS.keys())
        raise ValueError(
            f"Unsupported ayanamsa type: '{ayanamsa_type}'. "
            f"Supported types: {supported}"
        )

    ayanamsa_constant = AYANAMSAS[ayanamsa_type]["constant"]
    swe.set_sid_mode(ayanamsa_constant)
    return swe.get_ayanamsa(jd)


def tropical_to_sidereal(
    tropical_long: float, jd: float, ayanamsa_type: str = "lahiri"
) -> float:
    """Convert tropical longitude to sidereal longitude.

    Subtracts the ayanamsa from the tropical position to get the fixed-star
    position. This is the primary conversion for Vedic astrology.

    Args:
        tropical_long: Tropical longitude in degrees (0-360)
        jd: Julian Day (needed to calculate current ayanamsa)
        ayanamsa_type: Ayanamsa system to use (default: 'lahiri')

    Returns:
        Sidereal longitude in degrees (0-360)

    Example:
        >>> # Sun at 0° Aries tropical on March 20, 2000
        >>> jd = datetime_to_jd(datetime(2000, 3, 20, 12, 0))
        >>> tropical_sun = 0.0  # 0° Aries
        >>> sidereal_sun = tropical_to_sidereal(tropical_sun, jd)
        >>> print(f"Sun in sidereal zodiac: {sidereal_sun:.2f}°")
        Sun in sidereal zodiac: 336.15° (late Pisces)
    """
    ayanamsa = calculate_ayanamsa(jd, ayanamsa_type)
    sidereal_long = (tropical_long - ayanamsa) % 360
    return sidereal_long


def sidereal_to_tropical(
    sidereal_long: float, jd: float, ayanamsa_type: str = "lahiri"
) -> float:
    """Convert sidereal longitude to tropical longitude.

    Adds the ayanamsa to the sidereal position to get the seasonal position.
    This is the reverse of tropical_to_sidereal().

    Args:
        sidereal_long: Sidereal longitude in degrees (0-360)
        jd: Julian Day (needed to calculate current ayanamsa)
        ayanamsa_type: Ayanamsa system to use (default: 'lahiri')

    Returns:
        Tropical longitude in degrees (0-360)

    Example:
        >>> # Planet at 15° sidereal Aries
        >>> jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        >>> sidereal_pos = 15.0
        >>> tropical_pos = sidereal_to_tropical(sidereal_pos, jd)
        >>> print(f"Tropical position: {tropical_pos:.2f}°")
        Tropical position: 38.85° (8° Taurus)
    """
    ayanamsa = calculate_ayanamsa(jd, ayanamsa_type)
    tropical_long = (sidereal_long + ayanamsa) % 360
    return tropical_long


def convert_chart_to_sidereal(
    tropical_chart: Dict[str, float], jd: float, ayanamsa_type: str = "lahiri"
) -> Dict[str, float]:
    """Convert entire chart (all planets and points) to sidereal positions.

    Convenience function for bulk conversion of all chart positions.

    Args:
        tropical_chart: Dict mapping planet names to tropical longitudes
            e.g., {"Sun": 295.27, "Moon": 145.83, ...}
        jd: Julian Day for ayanamsa calculation
        ayanamsa_type: Ayanamsa system to use (default: 'lahiri')

    Returns:
        Dict mapping planet names to sidereal longitudes

    Example:
        >>> tropical_positions = {"Sun": 0.0, "Moon": 90.0, "Mars": 180.0}
        >>> jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        >>> sidereal_positions = convert_chart_to_sidereal(tropical_positions, jd)
        >>> for planet, position in sidereal_positions.items():
        ...     print(f"{planet}: {position:.2f}°")
        Sun: 336.15°
        Moon: 66.15°
        Mars: 156.15°
    """
    sidereal_chart = {}
    for planet, tropical_long in tropical_chart.items():
        sidereal_chart[planet] = tropical_to_sidereal(tropical_long, jd, ayanamsa_type)
    return sidereal_chart


def get_ayanamsa_info(ayanamsa_type: str = "lahiri") -> Dict[str, str]:
    """Get information about a specific ayanamsa system.

    Args:
        ayanamsa_type: Type of ayanamsa to get info for

    Returns:
        Dict with name and description of the ayanamsa system

    Raises:
        ValueError: If ayanamsa_type is not supported

    Example:
        >>> info = get_ayanamsa_info('lahiri')
        >>> print(info['name'])
        Lahiri (Chitrapaksha)
        >>> print(info['description'])
        Official ayanamsa of Indian Government (1956)
    """
    if ayanamsa_type not in AYANAMSAS:
        supported = ", ".join(AYANAMSAS.keys())
        raise ValueError(
            f"Unsupported ayanamsa type: '{ayanamsa_type}'. "
            f"Supported types: {supported}"
        )

    return {
        "name": AYANAMSAS[ayanamsa_type]["name"],
        "description": AYANAMSAS[ayanamsa_type]["description"],
    }


def list_ayanamsas() -> List[Dict[str, str]]:
    """List all supported ayanamsa systems.

    Returns:
        List of dicts, each containing type, name, and description

    Example:
        >>> systems = list_ayanamsas()
        >>> for system in systems:
        ...     print(f"{system['type']}: {system['name']}")
        lahiri: Lahiri (Chitrapaksha)
        raman: B.V. Raman
        krishnamurti: Krishnamurti
        fagan_bradley: Fagan-Bradley
    """
    return [
        {
            "type": key,
            "name": value["name"],
            "description": value["description"],
        }
        for key, value in AYANAMSAS.items()
    ]


# ============================================================================
# NAKSHATRA CALCULATIONS (27 Lunar Mansions)
# ============================================================================

# 27 Nakshatras (lunar mansions) - each 13°20' (360° / 27)
NAKSHATRAS = [
    "Ashwini",  # 0°00' - 13°20' Aries
    "Bharani",  # 13°20' - 26°40' Aries
    "Krittika",  # 26°40' Aries - 10°00' Taurus
    "Rohini",  # 10°00' - 23°20' Taurus
    "Mrigashira",  # 23°20' Taurus - 6°40' Gemini
    "Ardra",  # 6°40' - 20°00' Gemini
    "Punarvasu",  # 20°00' Gemini - 3°20' Cancer
    "Pushya",  # 3°20' - 16°40' Cancer
    "Ashlesha",  # 16°40' - 30°00' Cancer
    "Magha",  # 0°00' - 13°20' Leo
    "Purva Phalguni",  # 13°20' - 26°40' Leo
    "Uttara Phalguni",  # 26°40' Leo - 10°00' Virgo
    "Hasta",  # 10°00' - 23°20' Virgo
    "Chitra",  # 23°20' Virgo - 6°40' Libra
    "Swati",  # 6°40' - 20°00' Libra
    "Vishakha",  # 20°00' Libra - 3°20' Scorpio
    "Anuradha",  # 3°20' - 16°40' Scorpio
    "Jyeshtha",  # 16°40' - 30°00' Scorpio
    "Mula",  # 0°00' - 13°20' Sagittarius
    "Purva Ashadha",  # 13°20' - 26°40' Sagittarius
    "Uttara Ashadha",  # 26°40' Sagittarius - 10°00' Capricorn
    "Shravana",  # 10°00' - 23°20' Capricorn
    "Dhanishta",  # 23°20' Capricorn - 6°40' Aquarius
    "Shatabhisha",  # 6°40' - 20°00' Aquarius
    "Purva Bhadrapada",  # 20°00' Aquarius - 3°20' Pisces
    "Uttara Bhadrapada",  # 3°20' - 16°40' Pisces
    "Revati",  # 16°40' - 30°00' Pisces
]

# Nakshatra lords (planetary rulers) in order
NAKSHATRA_LORDS = [
    "Ketu",  # Ashwini
    "Venus",  # Bharani
    "Sun",  # Krittika
    "Moon",  # Rohini
    "Mars",  # Mrigashira
    "Rahu",  # Ardra
    "Jupiter",  # Punarvasu
    "Saturn",  # Pushya
    "Mercury",  # Ashlesha
    "Ketu",  # Magha (cycle repeats)
    "Venus",  # Purva Phalguni
    "Sun",  # Uttara Phalguni
    "Moon",  # Hasta
    "Mars",  # Chitra
    "Rahu",  # Swati
    "Jupiter",  # Vishakha
    "Saturn",  # Anuradha
    "Mercury",  # Jyeshtha
    "Ketu",  # Mula
    "Venus",  # Purva Ashadha
    "Sun",  # Uttara Ashadha
    "Moon",  # Shravana
    "Mars",  # Dhanishta
    "Rahu",  # Shatabhisha
    "Jupiter",  # Purva Bhadrapada
    "Saturn",  # Uttara Bhadrapada
    "Mercury",  # Revati
]


def get_nakshatra(sidereal_longitude: float) -> Dict[str, Any]:
    """Get nakshatra (lunar mansion) for a sidereal longitude.

    Each nakshatra spans 13°20' (360° / 27 = 13.333...°).
    Each nakshatra is divided into 4 padas (quarters) of 3°20' each.

    Args:
        sidereal_longitude: Sidereal longitude in degrees (0-360)
            Must be SIDEREAL, not tropical

    Returns:
        Dict containing:
            - nakshatra: Name of the nakshatra
            - index: Index (0-26)
            - lord: Ruling planet of the nakshatra
            - pada: Quarter within nakshatra (1-4)
            - degree_in_nakshatra: Degrees into this nakshatra (0-13.33)
            - start_degree: Starting degree of nakshatra in zodiac

    Example:
        >>> # Moon at 10° sidereal Aries
        >>> nakshatra = get_nakshatra(10.0)
        >>> print(f"Nakshatra: {nakshatra['nakshatra']}")
        Nakshatra: Ashwini
        >>> print(f"Pada: {nakshatra['pada']}")
        Pada: 4
    """
    # Normalize to 0-360
    sidereal_longitude = sidereal_longitude % 360

    # Each nakshatra = 13°20' = 13.333...°
    nakshatra_width = 360.0 / 27

    # Find which nakshatra (0-26)
    # Add small epsilon to handle floating point precision at boundaries
    nakshatra_index = int((sidereal_longitude + 1e-9) / nakshatra_width)
    # Ensure we don't exceed index 26 due to rounding
    nakshatra_index = min(nakshatra_index, 26)

    nakshatra_name = NAKSHATRAS[nakshatra_index]
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_index]

    # Degree within this nakshatra (0-13.333...)
    nakshatra_degree = sidereal_longitude % nakshatra_width

    # Pada (quarter): each pada = 3°20' = 3.333...°
    pada_width = nakshatra_width / 4
    pada = int((nakshatra_degree + 1e-9) / pada_width) + 1  # 1-4
    # Ensure pada is in range 1-4
    pada = min(pada, 4)

    # Starting degree of this nakshatra
    start_degree = nakshatra_index * nakshatra_width

    return {
        "nakshatra": nakshatra_name,
        "index": nakshatra_index,
        "lord": nakshatra_lord,
        "pada": pada,
        "degree_in_nakshatra": nakshatra_degree,
        "start_degree": start_degree,
    }


def get_moon_nakshatra(
    tropical_moon_long: float, jd: float, ayanamsa_type: str = "lahiri"
) -> Dict[str, Any]:
    """Get nakshatra for Moon position (convenience function).

    Converts tropical Moon position to sidereal and calculates nakshatra.
    The Moon's nakshatra is especially important in Vedic astrology for
    determining the Vimshottari Dasa starting point.

    Args:
        tropical_moon_long: Moon's tropical longitude
        jd: Julian Day (for ayanamsa calculation)
        ayanamsa_type: Ayanamsa system to use

    Returns:
        Nakshatra information dict (see get_nakshatra)

    Example:
        >>> # Moon at 145° tropical (25° Leo)
        >>> jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        >>> moon_nak = get_moon_nakshatra(145.0, jd)
        >>> print(f"Moon in {moon_nak['nakshatra']}")
        Moon in Purva Phalguni
    """
    sidereal_moon = tropical_to_sidereal(tropical_moon_long, jd, ayanamsa_type)
    return get_nakshatra(sidereal_moon)


# ============================================================================
# VIMSHOTTARI DASA SYSTEM (120-year planetary period system)
# ============================================================================

# Dasa lords and their periods in years (total 120 years)
DASA_LORDS = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]
DASA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Total = 120 years


def calculate_vimshottari_dasa(
    moon_nakshatra_index: int, birth_jd: float
) -> List[Dict[str, Any]]:
    """Calculate Vimshottari Dasa periods for a birth chart.

    The Vimshottari Dasa is a 120-year cycle of planetary periods based on
    the Moon's nakshatra at birth. Each planet rules for a specific number
    of years in a fixed sequence.

    Dasa periods:
        Ketu: 7 years, Venus: 20 years, Sun: 6 years, Moon: 10 years,
        Mars: 7 years, Rahu: 18 years, Jupiter: 16 years,
        Saturn: 19 years, Mercury: 17 years

    Args:
        moon_nakshatra_index: Index of Moon's nakshatra at birth (0-26)
        birth_jd: Julian Day of birth

    Returns:
        List of dasa periods, each dict containing:
            - lord: Planet ruling this period
            - start_date: Start of period (datetime)
            - end_date: End of period (datetime)
            - start_jd: Start Julian Day
            - end_jd: End Julian Day
            - years: Duration in years

    Example:
        >>> # Moon in Ashwini (index 0) at birth
        >>> jd = datetime_to_jd(datetime(1982, 1, 8, 12, 0))
        >>> dasas = calculate_vimshottari_dasa(0, jd)
        >>> for dasa in dasas[:3]:  # First 3 periods
        ...     print(f"{dasa['lord']}: {dasa['years']} years")
        Ketu: 7 years
        Venus: 20 years
        Sun: 6 years
    """
    # Starting dasa lord based on birth nakshatra
    # Each lord rules 3 nakshatras (27 / 9 = 3)
    start_lord_index = moon_nakshatra_index % 9

    periods = []
    current_jd = birth_jd

    # Generate all 9 dasa periods (120 years total)
    for i in range(9):
        lord_index = (start_lord_index + i) % 9
        lord = DASA_LORDS[lord_index]
        years = DASA_YEARS[lord_index]

        # Calculate end date (1 year = 365.25 days average)
        days = years * 365.25
        end_jd = current_jd + days

        # Convert Julian Days to datetime for readability
        start_date = jd_to_datetime(current_jd)
        end_date = jd_to_datetime(end_jd)

        periods.append(
            {
                "lord": lord,
                "start_date": start_date,
                "end_date": end_date,
                "start_jd": current_jd,
                "end_jd": end_jd,
                "years": years,
            }
        )

        current_jd = end_jd

    return periods


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to datetime object.

    Helper function for converting JD back to Python datetime.

    Args:
        jd: Julian Day

    Returns:
        datetime object (UTC)

    Example:
        >>> jd = 2451545.0  # J2000.0
        >>> dt = jd_to_datetime(jd)
        >>> print(dt)
        2000-01-01 12:00:00
    """
    # Swiss Ephemeris provides this conversion
    year, month, day, hour = swe.revjul(jd)
    # Convert decimal hour to hour, minute, second
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)

    return datetime(year, month, day, hours, minutes, seconds)


def get_current_dasa(
    moon_nakshatra_index: int, birth_jd: float, current_jd: float
) -> Optional[Dict[str, Any]]:
    """Get the currently active Vimshottari Dasa period.

    Args:
        moon_nakshatra_index: Index of Moon's nakshatra at birth (0-26)
        birth_jd: Julian Day of birth
        current_jd: Current Julian Day

    Returns:
        Dict containing current dasa period info (or None if beyond 120 years)

    Example:
        >>> birth_jd = datetime_to_jd(datetime(1982, 1, 8, 12, 0))
        >>> now_jd = datetime_to_jd(datetime(2026, 2, 21, 12, 0))
        >>> moon_nak_index = 10  # Purva Phalguni
        >>> current = get_current_dasa(moon_nak_index, birth_jd, now_jd)
        >>> if current:
        ...     print(f"Current Dasa: {current['lord']}")
        Current Dasa: Venus
    """
    dasas = calculate_vimshottari_dasa(moon_nakshatra_index, birth_jd)

    for dasa in dasas:
        if dasa["start_jd"] <= current_jd < dasa["end_jd"]:
            return dasa

    # Beyond the 120-year cycle
    return None
