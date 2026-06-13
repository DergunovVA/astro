"""
Shared astrological constants for the entire codebase.

Single source of truth — import from here instead of redefining locally.
"""

from typing import Dict, List

# ── Zodiac ────────────────────────────────────────────────────────────────────

ZODIAC_SIGNS: List[str] = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

SIGN_SYMBOLS: Dict[str, str] = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

SIGN_TO_ELEMENT: Dict[str, str] = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}

SIGN_TO_MODALITY: Dict[str, str] = {
    "Aries": "Cardinal",
    "Cancer": "Cardinal",
    "Libra": "Cardinal",
    "Capricorn": "Cardinal",
    "Taurus": "Fixed",
    "Leo": "Fixed",
    "Scorpio": "Fixed",
    "Aquarius": "Fixed",
    "Gemini": "Mutable",
    "Virgo": "Mutable",
    "Sagittarius": "Mutable",
    "Pisces": "Mutable",
}

SIGN_TO_POLARITY: Dict[str, str] = {
    "Aries": "Positive",
    "Gemini": "Positive",
    "Leo": "Positive",
    "Libra": "Positive",
    "Sagittarius": "Positive",
    "Aquarius": "Positive",
    "Taurus": "Negative",
    "Cancer": "Negative",
    "Virgo": "Negative",
    "Scorpio": "Negative",
    "Capricorn": "Negative",
    "Pisces": "Negative",
}

# ── Planets ───────────────────────────────────────────────────────────────────

CLASSICAL_PLANETS: List[str] = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
]
MODERN_PLANETS: List[str] = ["Uranus", "Neptune", "Pluto"]
ALL_PLANETS: List[str] = CLASSICAL_PLANETS + MODERN_PLANETS
SPECIAL_BODIES: List[str] = ["North Node", "Chiron", "Lilith", "Proserpina"]

PLANET_SYMBOLS: Dict[str, str] = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "North Node": "☊",
    "Chiron": "⚷",
    "Lilith": "⚸",
}

# Average daily speeds (degrees/day) for motion evaluation
AVERAGE_SPEEDS: Dict[str, float] = {
    "Sun": 0.9856,
    "Moon": 13.176,
    "Mercury": 1.0,
    "Venus": 1.0,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.033,
    "Uranus": 0.0117,
    "Neptune": 0.0067,
    "Pluto": 0.0039,
}

# ── Aspects ───────────────────────────────────────────────────────────────────

MAJOR_ASPECTS: Dict[str, int] = {
    "Conjunction": 0,
    "Opposition": 180,
    "Trine": 120,
    "Square": 90,
    "Sextile": 60,
}

MINOR_ASPECTS: Dict[str, float] = {
    "Semi-sextile": 30,
    "Semi-square": 45,
    "Sesquiquadrate": 135,
    "Quincunx": 150,
    "Quintile": 72,
    "Biquintile": 144,
    "Septile": 360 / 7,
    "Novile": 40,
}

ALL_ASPECTS: Dict[str, float] = {**MAJOR_ASPECTS, **MINOR_ASPECTS}  # type: ignore[arg-type]

ASPECT_SYMBOLS: Dict[str, str] = {
    "Conjunction": "☌",
    "Opposition": "☍",
    "Trine": "△",
    "Square": "□",
    "Sextile": "⚹",
    "Quincunx": "⚻",
    "Semi-sextile": "⚺",
    "Semi-square": "∠",
    "Sesquiquadrate": "⊼",
}

# Default orbs (degrees) for major aspects
DEFAULT_ORBS: Dict[str, float] = {
    "Conjunction": 8.0,
    "Opposition": 8.0,
    "Trine": 7.0,
    "Square": 7.0,
    "Sextile": 5.0,
    "Semi-sextile": 2.0,
    "Semi-square": 2.0,
    "Sesquiquadrate": 2.0,
    "Quincunx": 3.0,
    "Quintile": 1.5,
    "Biquintile": 1.5,
    "Septile": 1.0,
    "Novile": 1.0,
}

# ── Houses ────────────────────────────────────────────────────────────────────

HOUSE_NAMES: Dict[int, str] = {
    1: "Ascendant",
    2: "Succedent II",
    3: "Cadent III",
    4: "IC",
    5: "Succedent V",
    6: "Cadent VI",
    7: "Descendant",
    8: "Succedent VIII",
    9: "Cadent IX",
    10: "MC",
    11: "Succedent XI",
    12: "Cadent XII",
}

ANGULAR_HOUSES: List[int] = [1, 4, 7, 10]
SUCCEDENT_HOUSES: List[int] = [2, 5, 8, 11]
CADENT_HOUSES: List[int] = [3, 6, 9, 12]

# ── Dates & JD ────────────────────────────────────────────────────────────────

# Julian Day for J2000.0 epoch
J2000_JD: float = 2451545.0

# ── Astrological Thresholds ──────────────────────────────────────────────────

CAZIMI_ORB_DEG: float = 17 / 60  # 0°17'
COMBUST_ORB_DEG: float = 8.5  # 8°30'
BEAMS_ORB_DEG: float = 17.0  # 17°00'
