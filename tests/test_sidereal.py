"""Tests for sidereal zodiac calculations.

Testing:
- Ayanamsa calculations (Lahiri, Raman, Krishnamurti, Fagan-Bradley)
- Tropical to sidereal conversions
- Nakshatra (lunar mansion) calculations
- Vimshottari Dasa period system
"""

import pytest
import swisseph as swe
from datetime import datetime
from src.calc.sidereal import (
    calculate_ayanamsa,
    tropical_to_sidereal,
    sidereal_to_tropical,
    convert_chart_to_sidereal,
    get_ayanamsa_info,
    list_ayanamsas,
    get_nakshatra,
    get_moon_nakshatra,
    calculate_vimshottari_dasa,
    get_current_dasa,
    jd_to_datetime,
    AYANAMSAS,
    NAKSHATRAS,
    NAKSHATRA_LORDS,
    DASA_LORDS,
    DASA_YEARS,
)


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day (helper for tests)."""
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)


# ============================================================================
# TEST AYANAMSA CALCULATIONS (Task 4.3.1)
# ============================================================================


class TestAyanamsaCalculations:
    """Test ayanamsa calculations for different systems."""

    def test_lahiri_ayanamsa_year_2000(self):
        """Test Lahiri ayanamsa for Jan 1, 2000 (J2000.0)."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        ayanamsa = calculate_ayanamsa(jd, "lahiri")

        # Lahiri ayanamsa ~23.85° in year 2000
        assert 23.0 < ayanamsa < 24.5, f"Expected ~23.85°, got {ayanamsa:.2f}°"

    def test_lahiri_ayanamsa_year_2026(self):
        """Test Lahiri ayanamsa for current year 2026."""
        jd = datetime_to_jd(datetime(2026, 1, 1, 12, 0))
        ayanamsa = calculate_ayanamsa(jd, "lahiri")

        # Lahiri ayanamsa ~24.2° in year 2026
        # (increases ~50" per year, ~0.36° in 26 years)
        assert 24.0 < ayanamsa < 25.0, f"Expected ~24.2°, got {ayanamsa:.2f}°"

    def test_raman_ayanamsa(self):
        """Test B.V. Raman ayanamsa."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        ayanamsa = calculate_ayanamsa(jd, "raman")

        # Raman ayanamsa similar to Lahiri but slightly different
        assert 20.0 < ayanamsa < 25.0, f"Got {ayanamsa:.2f}°"

    def test_krishnamurti_ayanamsa(self):
        """Test Krishnamurti (KP) ayanamsa."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        ayanamsa = calculate_ayanamsa(jd, "krishnamurti")

        # KP ayanamsa close to Lahiri
        assert 20.0 < ayanamsa < 25.0, f"Got {ayanamsa:.2f}°"

    def test_fagan_bradley_ayanamsa(self):
        """Test Fagan-Bradley (Western sidereal) ayanamsa."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        ayanamsa = calculate_ayanamsa(jd, "fagan_bradley")

        # Fagan-Bradley ayanamsa ~24.7° in 2000 (slightly different)
        assert 20.0 < ayanamsa < 28.0, f"Got {ayanamsa:.2f}°"

    def test_unsupported_ayanamsa_raises_error(self):
        """Test that unsupported ayanamsa type raises ValueError."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))

        with pytest.raises(ValueError, match="Unsupported ayanamsa type"):
            calculate_ayanamsa(jd, "nonexistent")

    def test_ayanamsa_increases_over_time(self):
        """Test that ayanamsa increases as time progresses (precession)."""
        jd_1900 = datetime_to_jd(datetime(1900, 1, 1, 12, 0))
        jd_2000 = datetime_to_jd(datetime(2000, 1, 1, 12, 0))

        ayanamsa_1900 = calculate_ayanamsa(jd_1900, "lahiri")
        ayanamsa_2000 = calculate_ayanamsa(jd_2000, "lahiri")

        # Ayanamsa should increase (precession moves backwards)
        # ~1° every 72 years, so ~1.4° in 100 years
        assert ayanamsa_2000 > ayanamsa_1900, (
            f"Ayanamsa should increase over time: "
            f"1900={ayanamsa_1900:.2f}°, 2000={ayanamsa_2000:.2f}°"
        )
        assert 1.0 < (ayanamsa_2000 - ayanamsa_1900) < 2.0, (
            f"Expected ~1.4° increase in 100 years, "
            f"got {ayanamsa_2000 - ayanamsa_1900:.2f}°"
        )


# ============================================================================
# TEST TROPICAL/SIDEREAL CONVERSIONS
# ============================================================================


class TestTropicalSiderealConversions:
    """Test conversions between tropical and sidereal zodiacs."""

    def test_tropical_to_sidereal_aries_point(self):
        """Test that 0° Aries tropical is ~336° sidereal (late Pisces)."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        tropical_aries = 0.0  # 0° Aries tropical

        sidereal = tropical_to_sidereal(tropical_aries, jd)

        # With Lahiri ayanamsa ~23.85° in 2000:
        # 0° - 23.85° = -23.85° → 336.15° (late Pisces)
        assert 330.0 < sidereal < 340.0, f"Expected ~336°, got {sidereal:.2f}°"

    def test_sidereal_to_tropical_conversion(self):
        """Test sidereal to tropical conversion (reverse)."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        sidereal_pos = 0.0  # 0° sidereal Aries

        tropical = sidereal_to_tropical(sidereal_pos, jd)

        # 0° sidereal + 23.85° ayanamsa = 23.85° tropical (late Aries)
        assert 20.0 < tropical < 27.0, f"Expected ~23.85°, got {tropical:.2f}°"

    def test_round_trip_conversion(self):
        """Test that tropical → sidereal → tropical returns same value."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        original_tropical = 145.5  # 25.5° Leo

        sidereal = tropical_to_sidereal(original_tropical, jd)
        back_to_tropical = sidereal_to_tropical(sidereal, jd)

        # Should be very close (within floating point precision)
        assert abs(back_to_tropical - original_tropical) < 0.001, (
            f"Round trip failed: {original_tropical:.2f}° → "
            f"{sidereal:.2f}° → {back_to_tropical:.2f}°"
        )

    def test_convert_chart_to_sidereal(self):
        """Test bulk conversion of entire chart."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        tropical_chart = {
            "Sun": 280.0,  # 10° Capricorn
            "Moon": 90.0,  # 0° Cancer
            "Mars": 180.0,  # 0° Libra
        }

        sidereal_chart = convert_chart_to_sidereal(tropical_chart, jd)

        # Each should be ~24° less (Lahiri ayanamsa)
        for planet in tropical_chart:
            tropical_pos = tropical_chart[planet]
            sidereal_pos = sidereal_chart[planet]
            difference = (tropical_pos - sidereal_pos) % 360

            # Difference should be close to ayanamsa (~23.85°)
            assert 22.0 < difference < 26.0, (
                f"{planet}: difference {difference:.2f}° (expected ~24°)"
            )

    def test_different_ayanamsa_systems_give_different_results(self):
        """Test that different ayanamsa systems produce different conversions."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        tropical_pos = 100.0  # 10° Cancer

        lahiri_sidereal = tropical_to_sidereal(tropical_pos, jd, "lahiri")
        raman_sidereal = tropical_to_sidereal(tropical_pos, jd, "raman")
        fagan_sidereal = tropical_to_sidereal(tropical_pos, jd, "fagan_bradley")

        # Different systems should give different results
        # (differences are typically small, ~1-2°)
        assert lahiri_sidereal != raman_sidereal, "Lahiri and Raman should differ"
        assert lahiri_sidereal != fagan_sidereal, (
            "Lahiri and Fagan-Bradley should differ"
        )


# ============================================================================
# TEST NAKSHATRA CALCULATIONS (Task 4.3.2)
# ============================================================================


class TestNakshatraCalculations:
    """Test nakshatra (lunar mansion) calculations."""

    def test_ashwini_nakshatra(self):
        """Test first nakshatra (Ashwini) at 0° sidereal Aries."""
        sidereal_pos = 5.0  # 5° sidereal Aries

        nakshatra = get_nakshatra(sidereal_pos)

        assert nakshatra["nakshatra"] == "Ashwini"
        assert nakshatra["index"] == 0
        assert nakshatra["lord"] == "Ketu"
        assert 0 <= nakshatra["degree_in_nakshatra"] < 13.333333

    def test_bharani_nakshatra(self):
        """Test Bharani nakshatra (13°20' - 26°40' Aries)."""
        sidereal_pos = 20.0  # 20° sidereal Aries

        nakshatra = get_nakshatra(sidereal_pos)

        assert nakshatra["nakshatra"] == "Bharani"
        assert nakshatra["index"] == 1
        assert nakshatra["lord"] == "Venus"

    def test_revati_nakshatra(self):
        """Test last nakshatra (Revati) at late Pisces."""
        sidereal_pos = 355.0  # 25° sidereal Pisces

        nakshatra = get_nakshatra(sidereal_pos)

        assert nakshatra["nakshatra"] == "Revati"
        assert nakshatra["index"] == 26  # Last nakshatra (0-indexed)
        assert nakshatra["lord"] == "Mercury"

    def test_pada_calculation(self):
        """Test pada (quarter) calculation within nakshatra."""
        # Each nakshatra = 13°20' = 13.333...°
        # Each pada = 3°20' = 3.333...°

        # Start of nakshatra (pada 1)
        nak1 = get_nakshatra(0.0)  # 0° Aries
        assert nak1["pada"] == 1

        # Second pada
        nak2 = get_nakshatra(5.0)  # 5° Aries (pada 2)
        assert nak2["pada"] == 2

        # Third pada
        nak3 = get_nakshatra(8.0)  # 8° Aries (pada 3)
        assert nak3["pada"] == 3

        # Fourth pada
        nak4 = get_nakshatra(12.0)  # 12° Aries (pada 4)
        assert nak4["pada"] == 4

    def test_all_27_nakshatras_covered(self):
        """Test that all 27 nakshatras are correctly mapped."""
        # Test one position in each nakshatra
        for i in range(27):
            # Middle of each nakshatra
            sidereal_pos = i * 13.33333 + 6.66666

            nakshatra = get_nakshatra(sidereal_pos)

            assert nakshatra["index"] == i, (
                f"Position {sidereal_pos:.2f}° should be nakshatra {i}, "
                f"got {nakshatra['index']}"
            )
            assert nakshatra["nakshatra"] == NAKSHATRAS[i]
            assert nakshatra["lord"] == NAKSHATRA_LORDS[i]

    def test_nakshatra_lords_cycle_repeats(self):
        """Test that nakshatra lords cycle every 9 nakshatras."""
        # Lords cycle: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury
        # This pattern repeats 3 times (9 × 3 = 27)

        # Calculate exact nakshatra width
        nakshatra_width = 360.0 / 27

        # Check first nakshatra of each cycle (use middle of nakshatra to avoid boundaries)
        nak0 = get_nakshatra(
            nakshatra_width * 0 + nakshatra_width / 2
        )  # Ashwini (index 0)
        nak9 = get_nakshatra(
            nakshatra_width * 9 + nakshatra_width / 2
        )  # Magha (index 9)
        nak18 = get_nakshatra(
            nakshatra_width * 18 + nakshatra_width / 2
        )  # Mula (index 18)

        # All should be ruled by Ketu
        assert nak0["lord"] == "Ketu"
        assert nak9["lord"] == "Ketu"
        assert nak18["lord"] == "Ketu"

    def test_get_moon_nakshatra_with_tropical_position(self):
        """Test convenience function for Moon nakshatra from tropical position."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        tropical_moon = 145.0  # 25° Leo tropical

        moon_nak = get_moon_nakshatra(tropical_moon, jd)

        # Should convert to sidereal and find nakshatra
        assert "nakshatra" in moon_nak
        assert "lord" in moon_nak
        assert "pada" in moon_nak

        # 145° tropical - ~24° ayanamsa = ~121° sidereal
        # 121° / 13.333 = ~9.075 → index 9 (Magha)
        assert moon_nak["index"] == 9
        assert moon_nak["nakshatra"] == "Magha"
        assert moon_nak["lord"] == "Ketu"

    def test_nakshatra_wraps_at_360(self):
        """Test that nakshatra calculation wraps correctly at 360°."""
        # Test position just before 360°
        nak_before = get_nakshatra(359.0)
        assert nak_before["nakshatra"] == "Revati"

        # Test position at 360° (should wrap to 0°)
        nak_wrapped = get_nakshatra(360.0)
        assert nak_wrapped["nakshatra"] == "Ashwini"

        # Test position beyond 360°
        nak_beyond = get_nakshatra(365.0)
        assert nak_beyond["nakshatra"] == "Ashwini"


# ============================================================================
# TEST VIMSHOTTARI DASA SYSTEM (Task 4.3.3)
# ============================================================================


class TestVimshottariDasa:
    """Test Vimshottari Dasa planetary period system."""

    def test_dasa_lords_and_years_total_120(self):
        """Test that dasa periods sum to 120 years."""
        total_years = sum(DASA_YEARS)
        assert total_years == 120, f"Expected 120 years, got {total_years}"

    def test_dasa_sequence_order(self):
        """Test that dasa lords are in correct order."""
        expected_lords = [
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
        assert DASA_LORDS == expected_lords

    def test_dasa_years_correct(self):
        """Test that each lord has correct number of years."""
        expected_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
        assert DASA_YEARS == expected_years

    def test_calculate_vimshottari_dasa_ashwini(self):
        """Test Vimshottari Dasa starting from Ashwini (Ketu)."""
        # Birth in Ashwini (index 0) → starts with Ketu
        birth_jd = datetime_to_jd(datetime(1982, 1, 8, 12, 0))
        moon_nak_index = 0  # Ashwini

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # Should have 9 periods
        assert len(dasas) == 9

        # First period should be Ketu (7 years)
        assert dasas[0]["lord"] == "Ketu"
        assert dasas[0]["years"] == 7

        # Second period should be Venus (20 years)
        assert dasas[1]["lord"] == "Venus"
        assert dasas[1]["years"] == 20

        # Check start date matches birth
        assert dasas[0]["start_date"].year == 1982
        assert dasas[0]["start_date"].month == 1

    def test_calculate_vimshottari_dasa_bharani(self):
        """Test Vimshottari Dasa starting from Bharani (Venus)."""
        # Birth in Bharani (index 1) → starts with Venus
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        moon_nak_index = 1  # Bharani

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # First period should be Venus (20 years)
        assert dasas[0]["lord"] == "Venus"
        assert dasas[0]["years"] == 20

        # Second should be Sun (6 years)
        assert dasas[1]["lord"] == "Sun"
        assert dasas[1]["years"] == 6

    def test_calculate_vimshottari_dasa_magha(self):
        """Test Vimshottari Dasa from Magha (cycle repeats at index 9)."""
        # Magha (index 9) → lord index 9 % 9 = 0 → Ketu
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        moon_nak_index = 9  # Magha

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # Should start with Ketu (same as Ashwini)
        assert dasas[0]["lord"] == "Ketu"
        assert dasas[0]["years"] == 7

    def test_dasa_periods_are_continuous(self):
        """Test that dasa periods are continuous (no gaps)."""
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        moon_nak_index = 0

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # Each period's end should be next period's start
        for i in range(len(dasas) - 1):
            assert abs(dasas[i]["end_jd"] - dasas[i + 1]["start_jd"]) < 0.01, (
                f"Gap between {dasas[i]['lord']} and {dasas[i + 1]['lord']}"
            )

    def test_dasa_total_duration_120_years(self):
        """Test that total dasa duration is 120 years."""
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        moon_nak_index = 0

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # Last period should end ~120 years after birth
        first_start = dasas[0]["start_jd"]
        last_end = dasas[-1]["end_jd"]

        total_days = last_end - first_start
        total_years = total_days / 365.25

        # Should be very close to 120 years
        assert 119.5 < total_years < 120.5, (
            f"Expected ~120 years, got {total_years:.2f}"
        )

    def test_get_current_dasa_at_birth(self):
        """Test current dasa at time of birth."""
        birth_jd = datetime_to_jd(datetime(1982, 1, 8, 12, 0))
        moon_nak_index = 0  # Ashwini → Ketu

        current = get_current_dasa(moon_nak_index, birth_jd, birth_jd)

        assert current is not None
        assert current["lord"] == "Ketu"
        assert current["years"] == 7

    def test_get_current_dasa_after_44_years(self):
        """Test current dasa 44 years after birth (in 2026)."""
        birth_jd = datetime_to_jd(datetime(1982, 1, 8, 12, 0))
        current_jd = datetime_to_jd(datetime(2026, 2, 21, 12, 0))
        moon_nak_index = 0  # Ashwini

        # After Ketu (7) + Venus (20) + Sun (6) + Moon (10) = 43 years
        # Should be in Mars period (started ~2025)
        current = get_current_dasa(moon_nak_index, birth_jd, current_jd)

        assert current is not None
        # After 44 years: Ketu(7) + Venus(20) + Sun(6) + Moon(10) = 43 years
        # So should be in Mars period (or possibly Moon if we're at 43.x years)
        assert current["lord"] in ["Moon", "Mars"], (
            f"Expected Moon or Mars, got {current['lord']}"
        )

    def test_get_current_dasa_beyond_120_years(self):
        """Test that get_current_dasa returns None beyond 120 years."""
        birth_jd = datetime_to_jd(datetime(1900, 1, 1, 12, 0))
        future_jd = datetime_to_jd(datetime(2030, 1, 1, 12, 0))  # 130 years later
        moon_nak_index = 0

        current = get_current_dasa(moon_nak_index, birth_jd, future_jd)

        assert current is None, "Should return None beyond 120-year cycle"

    def test_jd_to_datetime_conversion(self):
        """Test Julian Day to datetime conversion."""
        # J2000.0 = JD 2451545.0 = January 1, 2000, 12:00 UTC
        jd = 2451545.0
        dt = jd_to_datetime(jd)

        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12


# ============================================================================
# TEST AYANAMSA INFO AND UTILITY FUNCTIONS
# ============================================================================


class TestAyanamsaUtilities:
    """Test utility functions for ayanamsa information."""

    def test_get_ayanamsa_info_lahiri(self):
        """Test getting info for Lahiri ayanamsa."""
        info = get_ayanamsa_info("lahiri")

        assert "name" in info
        assert "description" in info
        assert info["name"] == "Lahiri (Chitrapaksha)"
        assert "Indian Government" in info["description"]

    def test_get_ayanamsa_info_unsupported(self):
        """Test that unsupported ayanamsa raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported ayanamsa type"):
            get_ayanamsa_info("nonexistent")

    def test_list_ayanamsas(self):
        """Test listing all supported ayanamsa systems."""
        systems = list_ayanamsas()

        # Should have 4 systems
        assert len(systems) == 4

        # Each should have type, name, description
        for system in systems:
            assert "type" in system
            assert "name" in system
            assert "description" in system

        # Check that all expected types are present
        types = [s["type"] for s in systems]
        assert "lahiri" in types
        assert "raman" in types
        assert "krishnamurti" in types
        assert "fagan_bradley" in types


# ============================================================================
# TEST EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_nakshatra_at_exact_boundary(self):
        """Test nakshatra calculation at exact boundary (13°20')."""
        # Exactly at boundary between Ashwini and Bharani
        sidereal_pos = 13.333333333  # 13°20'

        nakshatra = get_nakshatra(sidereal_pos)

        # Should be in Bharani (second nakshatra)
        assert nakshatra["nakshatra"] == "Bharani"
        assert nakshatra["index"] == 1

    def test_negative_longitude_wraps_correctly(self):
        """Test that negative longitudes wrap to 0-360 range."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))

        # -10° should wrap to 350°
        sidereal = tropical_to_sidereal(-10.0, jd)
        assert 0 <= sidereal < 360

    def test_longitude_above_360_wraps_correctly(self):
        """Test that longitudes above 360° wrap correctly."""
        jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))

        # 370° should wrap to 10°
        sidereal = tropical_to_sidereal(370.0, jd)
        assert 0 <= sidereal < 360

    def test_dasa_with_last_nakshatra_revati(self):
        """Test Vimshottari Dasa starting from last nakshatra (Revati)."""
        # Revati (index 26) → lord index 26 % 9 = 8 → Mercury
        birth_jd = datetime_to_jd(datetime(2000, 1, 1, 12, 0))
        moon_nak_index = 26  # Revati

        dasas = calculate_vimshottari_dasa(moon_nak_index, birth_jd)

        # Should start with Mercury (17 years)
        assert dasas[0]["lord"] == "Mercury"
        assert dasas[0]["years"] == 17

        # Next should wrap to Ketu
        assert dasas[1]["lord"] == "Ketu"
        assert dasas[1]["years"] == 7

    def test_all_ayanamsa_constants_defined(self):
        """Test that all ayanamsa systems have valid Swiss Ephemeris constants."""
        for ayanamsa_type in AYANAMSAS:
            info = AYANAMSAS[ayanamsa_type]
            assert "constant" in info
            assert isinstance(info["constant"], int)
