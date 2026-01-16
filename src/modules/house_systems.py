# House Systems Implementation
# Supports: Placidus, Whole Sign, Koch, Regiomontanus, Campanus, Topocentric, Equal, Porphyry, Alcabitius

import swisseph as swe
from typing import List
from enum import Enum

class HouseSystem(Enum):
    """Enum of supported house systems."""
    PLACIDUS = "Placidus"           # Most popular (default)
    WHOLE_SIGN = "Whole Sign"       # Modern/Vedic alternative
    KOCH = "Koch"                   # Popular alternative
    REGIOMONTANUS = "Regiomontanus" # Classical
    CAMPANUS = "Campanus"           # Classical
    TOPOCENTRIC = "Topocentric"     # Rare, precise
    EQUAL = "Equal"                 # Simple 30° each
    PORPHYRY = "Porphyry"          # Classical division
    ALCABITIUS = "Alcabitius"      # Classical alternative


# Swiss Ephemeris codes for house systems
SWIEPH_CODES = {
    HouseSystem.PLACIDUS: 'P',           # Placidus
    HouseSystem.KOCH: 'K',               # Koch
    HouseSystem.REGIOMONTANUS: 'R',      # Regiomontanus
    HouseSystem.CAMPANUS: 'C',           # Campanus
    HouseSystem.TOPOCENTRIC: 'T',        # Topocentric
    HouseSystem.EQUAL: 'E',              # Equal
    HouseSystem.PORPHYRY: 'X',           # Porphyry
    HouseSystem.ALCABITIUS: 'A',         # Alcabitius
}


def calc_houses_placidus(jd: float, lat: float, lon: float) -> List[float]:
    """Placidus house system (default, most popular).
    
    Developed by Placidus de Titus (1603-1668).
    Respects geographical latitude, natural for observer location.
    Most widely used in Western astrology.
    """
    cusps_tuple = swe.houses(jd, lat, lon)[0]
    return list(cusps_tuple)


def calc_houses_whole_sign(jd: float, lat: float, lon: float) -> List[float]:
    """Whole Sign house system (modern/Vedic).
    
    Simple: 12 equal 30° houses starting from Ascendant.
    Ignores latitude effects.
    Popular in Vedic astrology and modern Western.
    """
    asc = swe.houses(jd, lat, lon)[0][0]
    return [(asc + i * 30) % 360 for i in range(12)]


def calc_houses_koch(jd: float, lat: float, lon: float) -> List[float]:
    """Koch house system.
    
    Time-based house division, developed in 1970s.
    Popular alternative to Placidus, smoother in high latitudes.
    Uses 'K' code in Swiss Ephemeris.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'K')[0]
    return list(cusps_tuple)


def calc_houses_regiomontanus(jd: float, lat: float, lon: float) -> List[float]:
    """Regiomontanus house system.
    
    Classical system used since 15th century.
    Uses equator division rather than ecliptic.
    Popular in classical astrology.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'R')[0]
    return list(cusps_tuple)


def calc_houses_campanus(jd: float, lat: float, lon: float) -> List[float]:
    """Campanus house system.
    
    Similar to Regiomontanus but vertical circle division.
    Classical system, less common today.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'C')[0]
    return list(cusps_tuple)


def calc_houses_topocentric(jd: float, lat: float, lon: float) -> List[float]:
    """Topocentric house system.
    
    Accounts for observer's altitude above sea level.
    Very precise but rarely used.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'T')[0]
    return list(cusps_tuple)


def calc_houses_equal(jd: float, lat: float, lon: float) -> List[float]:
    """Equal house system.
    
    12 equal 30° houses from Ascendant.
    Same as Whole Sign but with different starting point (some variations).
    Simple, mathematical approach.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'E')[0]
    return list(cusps_tuple)


def calc_houses_porphyry(jd: float, lat: float, lon: float) -> List[float]:
    """Porphyry house system.
    
    Classical system by Porphyry of Tyre (3rd century).
    Divides quadrants into thirds.
    Historical significance, rarely used today.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'X')[0]
    return list(cusps_tuple)


def calc_houses_alcabitius(jd: float, lat: float, lon: float) -> List[float]:
    """Alcabitius house system.
    
    Medieval system based on hour circles.
    Classical alternative, less common.
    """
    cusps_tuple = swe.houses(jd, lat, lon, hsys=b'A')[0]
    return list(cusps_tuple)


# Dispatch dictionary for all systems
HOUSE_SYSTEMS = {
    HouseSystem.PLACIDUS: calc_houses_placidus,
    HouseSystem.WHOLE_SIGN: calc_houses_whole_sign,
    HouseSystem.KOCH: calc_houses_koch,
    HouseSystem.REGIOMONTANUS: calc_houses_regiomontanus,
    HouseSystem.CAMPANUS: calc_houses_campanus,
    HouseSystem.TOPOCENTRIC: calc_houses_topocentric,
    HouseSystem.EQUAL: calc_houses_equal,
    HouseSystem.PORPHYRY: calc_houses_porphyry,
    HouseSystem.ALCABITIUS: calc_houses_alcabitius,
}


def calc_houses(
    jd: float,
    lat: float,
    lon: float,
    method: str = "Placidus"
) -> List[float]:
    """Calculate house cusps using specified system.
    
    Args:
        jd: Julian Day number
        lat: Observer latitude (-90 to 90)
        lon: Observer longitude (-180 to 180)
        method: House system name (see HouseSystem enum)
        
    Returns:
        List of 12 house cusps (ecliptic longitudes 0-360)
        
    Raises:
        ValueError: If house system not supported
    """
    try:
        house_system = HouseSystem(method)
    except ValueError:
        raise ValueError(
            f"Unknown house system '{method}'. "
            f"Supported: {', '.join([s.value for s in HouseSystem])}"
        )
    
    calc_func = HOUSE_SYSTEMS[house_system]
    return calc_func(jd, lat, lon)


def get_house_system_description(method: str) -> str:
    """Get description of a house system."""
    descriptions = {
        "Placidus": "Most popular (default). Respects geographical latitude.",
        "Whole Sign": "Modern/Vedic alternative. Simple 30° houses.",
        "Koch": "Popular alternative. Better in high latitudes.",
        "Regiomontanus": "Classical system from 15th century.",
        "Campanus": "Classical system using vertical circles.",
        "Topocentric": "Most precise. Accounts for observer altitude.",
        "Equal": "Simple mathematical 30° houses.",
        "Porphyry": "Classical division into thirds.",
        "Alcabitius": "Medieval hour-circle based system.",
    }
    return descriptions.get(method, "Unknown system")


def list_house_systems() -> List[str]:
    """List all supported house systems."""
    return [s.value for s in HouseSystem]
