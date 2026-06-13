"""
Tests for src/core/constants.py and src/modules/interpretation_texts.py.

Validates:
  - Constants: completeness, uniqueness, correct values
  - Interpretation texts: all public functions return valid dicts
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.constants import (
    ZODIAC_SIGNS,
    SIGN_SYMBOLS,
    SIGN_TO_ELEMENT,
    SIGN_TO_MODALITY,
    SIGN_TO_POLARITY,
    CLASSICAL_PLANETS,
    MODERN_PLANETS,
    ALL_PLANETS,
    PLANET_SYMBOLS,
    AVERAGE_SPEEDS,
    MAJOR_ASPECTS,
    MINOR_ASPECTS,
    ALL_ASPECTS,
    DEFAULT_ORBS,
    HOUSE_NAMES,
    ANGULAR_HOUSES,
    SUCCEDENT_HOUSES,
    CADENT_HOUSES,
    J2000_JD,
    CAZIMI_ORB_DEG,
    COMBUST_ORB_DEG,
    BEAMS_ORB_DEG,
)

from modules.interpretation_texts import (
    planet_in_sign_text,
    aspect_text,
    dignity_level_text,
    solar_condition_text,
    house_text,
    profection_year_text,
    generate_chart_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# ZODIAC SIGNS
# ─────────────────────────────────────────────────────────────────────────────


class TestZodiacConstants:
    def test_twelve_signs(self):
        assert len(ZODIAC_SIGNS) == 12

    def test_sign_order(self):
        expected = [
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
        assert ZODIAC_SIGNS == expected

    def test_sign_symbols_complete(self):
        for sign in ZODIAC_SIGNS:
            assert sign in SIGN_SYMBOLS, f"Symbol missing for {sign}"

    def test_all_elements_covered(self):
        elements = set(SIGN_TO_ELEMENT.values())
        assert elements == {"Fire", "Earth", "Air", "Water"}
        assert set(SIGN_TO_ELEMENT.keys()) == set(ZODIAC_SIGNS)

    def test_each_element_has_three_signs(self):
        from collections import Counter

        counts = Counter(SIGN_TO_ELEMENT.values())
        assert all(v == 3 for v in counts.values())

    def test_modalities_complete(self):
        modalities = set(SIGN_TO_MODALITY.values())
        assert modalities == {"Cardinal", "Fixed", "Mutable"}
        assert set(SIGN_TO_MODALITY.keys()) == set(ZODIAC_SIGNS)

    def test_polarities_complete(self):
        polarities = set(SIGN_TO_POLARITY.values())
        assert polarities == {"Positive", "Negative"}
        assert set(SIGN_TO_POLARITY.keys()) == set(ZODIAC_SIGNS)

    def test_fire_signs(self):
        fire = [s for s, e in SIGN_TO_ELEMENT.items() if e == "Fire"]
        assert set(fire) == {"Aries", "Leo", "Sagittarius"}

    def test_cardinal_signs(self):
        cardinal = [s for s, m in SIGN_TO_MODALITY.items() if m == "Cardinal"]
        assert set(cardinal) == {"Aries", "Cancer", "Libra", "Capricorn"}


# ─────────────────────────────────────────────────────────────────────────────
# PLANETS
# ─────────────────────────────────────────────────────────────────────────────


class TestPlanetConstants:
    def test_seven_classical_planets(self):
        assert len(CLASSICAL_PLANETS) == 7
        assert "Sun" in CLASSICAL_PLANETS
        assert "Moon" in CLASSICAL_PLANETS
        assert "Saturn" in CLASSICAL_PLANETS

    def test_three_modern_planets(self):
        assert len(MODERN_PLANETS) == 3
        assert set(MODERN_PLANETS) == {"Uranus", "Neptune", "Pluto"}

    def test_all_planets_concatenation(self):
        assert ALL_PLANETS == CLASSICAL_PLANETS + MODERN_PLANETS
        assert len(ALL_PLANETS) == 10

    def test_planet_symbols_for_all(self):
        for planet in ALL_PLANETS:
            assert planet in PLANET_SYMBOLS, f"Symbol missing for {planet}"

    def test_average_speeds_positive(self):
        for planet, speed in AVERAGE_SPEEDS.items():
            assert speed > 0, f"Speed for {planet} should be positive"

    def test_moon_fastest(self):
        assert AVERAGE_SPEEDS["Moon"] > AVERAGE_SPEEDS["Sun"]
        assert AVERAGE_SPEEDS["Moon"] > AVERAGE_SPEEDS["Mars"]

    def test_pluto_slowest(self):
        assert AVERAGE_SPEEDS["Pluto"] < AVERAGE_SPEEDS["Saturn"]
        assert AVERAGE_SPEEDS["Pluto"] < AVERAGE_SPEEDS["Jupiter"]


# ─────────────────────────────────────────────────────────────────────────────
# ASPECTS
# ─────────────────────────────────────────────────────────────────────────────


class TestAspectConstants:
    def test_five_major_aspects(self):
        assert len(MAJOR_ASPECTS) == 5

    def test_major_aspect_angles(self):
        assert MAJOR_ASPECTS["Conjunction"] == 0
        assert MAJOR_ASPECTS["Opposition"] == 180
        assert MAJOR_ASPECTS["Trine"] == 120
        assert MAJOR_ASPECTS["Square"] == 90
        assert MAJOR_ASPECTS["Sextile"] == 60

    def test_all_aspects_is_union(self):
        for name in MAJOR_ASPECTS:
            assert name in ALL_ASPECTS
        for name in MINOR_ASPECTS:
            assert name in ALL_ASPECTS

    def test_default_orbs_for_all_aspects(self):
        for name in ALL_ASPECTS:
            assert name in DEFAULT_ORBS, f"No default orb for {name}"
            assert DEFAULT_ORBS[name] > 0

    def test_quincunx_angle(self):
        assert MINOR_ASPECTS["Quincunx"] == 150

    def test_septile_angle(self):
        assert abs(MINOR_ASPECTS["Septile"] - 360 / 7) < 0.001


# ─────────────────────────────────────────────────────────────────────────────
# HOUSES
# ─────────────────────────────────────────────────────────────────────────────


class TestHouseConstants:
    def test_twelve_house_names(self):
        assert len(HOUSE_NAMES) == 12
        for i in range(1, 13):
            assert i in HOUSE_NAMES

    def test_house_1_is_ascendant(self):
        assert "Ascendant" in HOUSE_NAMES[1]

    def test_house_10_is_mc(self):
        assert "MC" in HOUSE_NAMES[10]

    def test_angular_succedent_cadent_partition(self):
        all_houses = set(range(1, 13))
        partition = set(ANGULAR_HOUSES) | set(SUCCEDENT_HOUSES) | set(CADENT_HOUSES)
        assert partition == all_houses
        # No overlap
        assert len(ANGULAR_HOUSES) + len(SUCCEDENT_HOUSES) + len(CADENT_HOUSES) == 12

    def test_angular_houses(self):
        assert set(ANGULAR_HOUSES) == {1, 4, 7, 10}

    def test_succedent_houses(self):
        assert set(SUCCEDENT_HOUSES) == {2, 5, 8, 11}

    def test_cadent_houses(self):
        assert set(CADENT_HOUSES) == {3, 6, 9, 12}


# ─────────────────────────────────────────────────────────────────────────────
# THRESHOLDS
# ─────────────────────────────────────────────────────────────────────────────


class TestThresholdConstants:
    def test_j2000(self):
        assert abs(J2000_JD - 2451545.0) < 0.1

    def test_cazimi_smaller_than_combust(self):
        assert CAZIMI_ORB_DEG < COMBUST_ORB_DEG

    def test_combust_smaller_than_beams(self):
        assert COMBUST_ORB_DEG < BEAMS_ORB_DEG

    def test_cazimi_approx_17_arcmin(self):
        # 17 arcminutes = 17/60 degrees ≈ 0.2833
        assert abs(CAZIMI_ORB_DEG - 17 / 60) < 0.001

    def test_combust_approx_8_5_deg(self):
        assert abs(COMBUST_ORB_DEG - 8.5) < 0.01

    def test_beams_17_deg(self):
        assert abs(BEAMS_ORB_DEG - 17.0) < 0.01


# ─────────────────────────────────────────────────────────────────────────────
# planet_in_sign_text
# ─────────────────────────────────────────────────────────────────────────────


class TestPlanetInSignText:
    def test_sun_aries_has_ru_en_keywords(self):
        result = planet_in_sign_text("Sun", "Aries")
        assert "ru" in result and "en" in result and "keywords" in result
        assert len(result["ru"]) > 10
        assert len(result["en"]) > 10
        assert isinstance(result["keywords"], list)

    def test_sun_all_twelve_signs(self):
        for sign in ZODIAC_SIGNS:
            r = planet_in_sign_text("Sun", sign)
            assert r["ru"], f"Missing RU text for Sun/{sign}"
            assert r["en"], f"Missing EN text for Sun/{sign}"

    def test_moon_all_twelve_signs(self):
        for sign in ZODIAC_SIGNS:
            r = planet_in_sign_text("Moon", sign)
            assert r["ru"], f"Missing RU text for Moon/{sign}"
            assert r["en"], f"Missing EN text for Moon/{sign}"

    def test_unknown_planet_fallback(self):
        r = planet_in_sign_text("Chiron", "Aries")
        assert "ru" in r and "en" in r
        assert isinstance(r["keywords"], list)

    def test_moon_cancer_domicile_mentioned(self):
        r = planet_in_sign_text("Moon", "Cancer")
        assert "domicile" in r["en"].lower() or "домициль" in r["ru"].lower()

    def test_moon_scorpio_fall_mentioned(self):
        r = planet_in_sign_text("Moon", "Scorpio")
        assert "fall" in r["en"].lower() or "падение" in r["ru"].lower()

    def test_venus_pisces_exaltation_mentioned(self):
        r = planet_in_sign_text("Venus", "Pisces")
        assert "exaltation" in r["en"].lower() or "экзальтация" in r["ru"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# aspect_text
# ─────────────────────────────────────────────────────────────────────────────


class TestAspectText:
    KNOWN_ASPECTS = [
        "Conjunction",
        "Opposition",
        "Trine",
        "Square",
        "Sextile",
        "Quincunx",
        "Semi-sextile",
        "Semi-square",
        "Sesquiquadrate",
        "Quintile",
        "Biquintile",
        "Septile",
    ]

    def test_all_known_aspects_have_text(self):
        for asp in self.KNOWN_ASPECTS:
            r = aspect_text(asp)
            assert r["ru"] and r["en"], f"Missing text for {asp}"

    def test_aspect_has_nature_field(self):
        for asp in self.KNOWN_ASPECTS:
            r = aspect_text(asp)
            assert "nature" in r, f"Missing 'nature' for {asp}"

    def test_trine_is_harmonious(self):
        r = aspect_text("Trine")
        assert r["nature"] == "harmonious"

    def test_square_is_challenging(self):
        r = aspect_text("Square")
        assert r["nature"] == "challenging"

    def test_unknown_aspect_fallback(self):
        r = aspect_text("Octile")
        assert "ru" in r and "en" in r
        assert r["nature"] == "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# dignity_level_text
# ─────────────────────────────────────────────────────────────────────────────


class TestDignityLevelText:
    LEVELS = [
        "Domicile",
        "Exaltation",
        "Triplicity",
        "Term",
        "Face",
        "Peregrine",
        "Detriment",
        "Fall",
        "Neutral",
    ]

    def test_all_levels_have_text(self):
        for lvl in self.LEVELS:
            r = dignity_level_text(lvl)
            assert r["ru"] and r["en"], f"Missing text for {lvl}"

    def test_has_score_hint(self):
        for lvl in self.LEVELS:
            r = dignity_level_text(lvl)
            assert "score_hint" in r, f"Missing score_hint for {lvl}"

    def test_domicile_positive_score(self):
        r = dignity_level_text("Domicile")
        assert "+" in r["score_hint"]

    def test_fall_negative_score(self):
        r = dignity_level_text("Fall")
        assert "-" in r["score_hint"]

    def test_unknown_level_fallback(self):
        r = dignity_level_text("Almuten")
        assert "ru" in r and "en" in r
        assert r["score_hint"] == "?"


# ─────────────────────────────────────────────────────────────────────────────
# solar_condition_text
# ─────────────────────────────────────────────────────────────────────────────


class TestSolarConditionText:
    CONDITIONS = ["cazimi", "combust", "under_beams", "free"]

    def test_all_conditions_have_text(self):
        for c in self.CONDITIONS:
            r = solar_condition_text(c)
            assert r["ru"] and r["en"]

    def test_cazimi_mentions_plus5(self):
        r = solar_condition_text("cazimi")
        assert "+5" in r["ru"] or "+5" in r["en"]

    def test_combust_mentions_minus5(self):
        r = solar_condition_text("combust")
        assert "-5" in r["ru"] or "-5" in r["en"]

    def test_free_keywords_not_empty(self):
        r = solar_condition_text("free")
        assert isinstance(r["keywords"], list) and len(r["keywords"]) > 0

    def test_unknown_condition_fallback(self):
        r = solar_condition_text("hayz")
        assert "ru" in r and "en" in r


# ─────────────────────────────────────────────────────────────────────────────
# house_text
# ─────────────────────────────────────────────────────────────────────────────


class TestHouseText:
    def test_all_twelve_houses_have_text(self):
        for i in range(1, 13):
            r = house_text(i)
            assert r["ru"] and r["en"], f"Missing text for house {i}"

    def test_house_1_mentions_ascendant(self):
        r = house_text(1)
        assert "Ascendant" in r["en"] or "Асцендент" in r["ru"]

    def test_house_10_mentions_mc(self):
        r = house_text(10)
        assert "MC" in r["en"] or "МС" in r["ru"]

    def test_house_7_mentions_partnership(self):
        r = house_text(7)
        assert "partnership" in r["en"].lower() or "партнёрств" in r["ru"].lower()

    def test_house_keywords_list(self):
        for i in range(1, 13):
            r = house_text(i)
            assert isinstance(r["keywords"], list)

    def test_out_of_range_fallback(self):
        r = house_text(13)
        assert "ru" in r and "en" in r


# ─────────────────────────────────────────────────────────────────────────────
# profection_year_text
# ─────────────────────────────────────────────────────────────────────────────


class TestProfectionYearText:
    def test_all_twelve_profection_houses(self):
        for i in range(1, 13):
            r = profection_year_text(i)
            assert r["ru"] and r["en"], f"Missing profection text for house {i}"

    def test_house1_mentions_ascendant_or_self(self):
        r = profection_year_text(1)
        text = r["en"].lower()
        assert "self" in text or "ascendant" in text or "renewal" in text

    def test_house10_mentions_career(self):
        r = profection_year_text(10)
        assert "career" in r["en"].lower() or "карьер" in r["ru"].lower()

    def test_out_of_range_fallback(self):
        r = profection_year_text(0)
        assert "ru" in r and "en" in r


# ─────────────────────────────────────────────────────────────────────────────
# generate_chart_summary
# ─────────────────────────────────────────────────────────────────────────────


class TestGenerateChartSummary:
    def test_basic_summary_returns_ru_en(self):
        r = generate_chart_summary("Aries", "Aries", "Leo")
        assert "ru" in r and "en" in r
        assert len(r["ru"]) > 30
        assert len(r["en"]) > 30

    def test_asc_sign_in_summary(self):
        r = generate_chart_summary("Scorpio", "Libra", "Taurus")
        assert "Scorpio" in r["en"]
        assert "Scorpio" in r["ru"]

    def test_day_chart_label(self):
        r = generate_chart_summary("Leo", "Leo", "Aquarius", is_day_chart=True)
        assert "diurnal" in r["en"].lower() or "дневного" in r["ru"].lower()

    def test_night_chart_label(self):
        r = generate_chart_summary("Leo", "Capricorn", "Cancer", is_day_chart=False)
        assert "nocturnal" in r["en"].lower() or "ночного" in r["ru"].lower()

    def test_dominant_element_included(self):
        r = generate_chart_summary(
            "Aries", "Leo", "Sagittarius", dominant_element="Fire"
        )
        assert "Fire" in r["en"]
        assert "огонь" in r["ru"].lower()

    def test_stellium_included(self):
        r = generate_chart_summary("Cancer", "Cancer", "Cancer", stelliums=["Cancer"])
        assert "Cancer" in r["en"]
        assert "Cancer" in r["ru"]

    def test_multiple_stelliums(self):
        r = generate_chart_summary(
            "Libra", "Libra", "Aries", stelliums=["Libra", "7th house"]
        )
        assert "Libra" in r["en"]
        assert "7th house" in r["en"]
