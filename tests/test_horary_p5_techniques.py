"""
Tests for P5 horary techniques:
- check_combust_cazimi()
- calculate_part_of_fortune()
- check_frustration()
"""

import pytest

from src.modules.horary import (
    check_combust_cazimi,
    calculate_part_of_fortune,
    check_frustration,
)


# ============================================================
# check_combust_cazimi
# ============================================================


class TestCheckCombustCazimi:
    """Tests for solar proximity states: cazimi / combust / under beams / free."""

    def test_cazimi(self):
        """Planet within 17 arcminutes (0.2833°) of Sun → cazimi."""
        result = check_combust_cazimi("Venus", planet_lon=5.0, sun_lon=5.1)

        assert result["state"] == "cazimi"
        assert result["strength_modifier"] == 5
        assert result["is_strengthened"] is True
        assert result["is_impaired"] is False
        assert result["distance"] == pytest.approx(0.1, abs=0.0001)

    def test_combust(self):
        """Planet 7° from Sun → combust (within 8.5°)."""
        result = check_combust_cazimi("Mars", planet_lon=10.0, sun_lon=17.0)

        assert result["state"] == "combust"
        assert result["strength_modifier"] == -5
        assert result["is_impaired"] is True
        assert result["is_strengthened"] is False
        assert result["distance"] == pytest.approx(7.0, abs=0.001)

    def test_combust_boundary_exactly_8_5(self):
        """Planet exactly 8.5° from Sun → still combust (boundary inclusive)."""
        result = check_combust_cazimi("Saturn", planet_lon=0.0, sun_lon=8.5)

        assert result["state"] == "combust"
        assert result["distance"] == pytest.approx(8.5, abs=0.001)

    def test_under_beams(self):
        """Planet 12° from Sun → under beams (8.5° < d ≤ 17°)."""
        result = check_combust_cazimi("Jupiter", planet_lon=0.0, sun_lon=12.0)

        assert result["state"] == "under_beams"
        assert result["strength_modifier"] == -2
        assert result["is_impaired"] is True
        assert result["is_strengthened"] is False

    def test_free(self):
        """Planet 25° from Sun → free of solar impediment."""
        result = check_combust_cazimi("Jupiter", planet_lon=0.0, sun_lon=25.0)

        assert result["state"] == "free"
        assert result["strength_modifier"] == 0
        assert result["is_impaired"] is False
        assert result["is_strengthened"] is False

    def test_sun_exempt_from_combustion(self):
        """The Sun itself cannot be combust — always returns free."""
        result = check_combust_cazimi("Sun", planet_lon=45.0, sun_lon=45.0)

        assert result["state"] == "free"
        assert result["strength_modifier"] == 0

    def test_crosses_zero_degrees(self):
        """Planet at 358°, Sun at 3° → shortest arc 5° → combust."""
        result = check_combust_cazimi("Venus", planet_lon=358.0, sun_lon=3.0)

        assert result["state"] == "combust"
        assert result["distance"] == pytest.approx(5.0, abs=0.001)

    def test_result_keys(self):
        """Return dict must contain all 6 expected keys."""
        result = check_combust_cazimi("Mars", planet_lon=20.0, sun_lon=30.0)

        expected_keys = {
            "state",
            "distance",
            "strength_modifier",
            "is_impaired",
            "is_strengthened",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())

    def test_explanation_is_string(self):
        """Explanation must be a non-empty string."""
        result = check_combust_cazimi("Mercury", planet_lon=0.0, sun_lon=5.0)

        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_opposite_side_not_combust(self):
        """Planet 180° from Sun → shortest arc is 180 → free (not combust)."""
        result = check_combust_cazimi("Saturn", planet_lon=0.0, sun_lon=180.0)

        assert result["state"] == "free"
        assert result["distance"] == pytest.approx(180.0, abs=0.001)


# ============================================================
# calculate_part_of_fortune
# ============================================================


class TestCalculatePartOfFortune:
    """Tests for Part of Fortune (Pars Fortunae) calculation."""

    def test_day_chart_simple(self):
        """Day chart: ASC=0, Moon=90, Sun=45 → (0+90-45)%360=45 = Taurus 15°."""
        result = calculate_part_of_fortune(
            asc_lon=0.0, sun_lon=45.0, moon_lon=90.0, is_day_chart=True
        )

        assert result["longitude"] == pytest.approx(45.0, abs=0.001)
        assert result["sign"] == "Taurus"
        assert result["degree_in_sign"] == pytest.approx(15.0, abs=0.001)
        assert result["ruler"] == "Venus"

    def test_night_chart_simple(self):
        """Night chart: ASC=0, Moon=90, Sun=45 → (0+45-90)%360=315 = Aquarius 15°."""
        result = calculate_part_of_fortune(
            asc_lon=0.0, sun_lon=45.0, moon_lon=90.0, is_day_chart=False
        )

        assert result["longitude"] == pytest.approx(315.0, abs=0.001)
        assert result["sign"] == "Aquarius"
        assert result["degree_in_sign"] == pytest.approx(15.0, abs=0.001)
        assert result["ruler"] == "Saturn"

    def test_result_always_0_to_360(self):
        """Longitude is always in [0, 360)."""
        # This combination could underflow without correct modulo handling
        result = calculate_part_of_fortune(
            asc_lon=10.0, sun_lon=200.0, moon_lon=50.0, is_day_chart=True
        )

        assert 0.0 <= result["longitude"] < 360.0

    def test_wraps_around_360(self):
        """Result wraps correctly when raw sum exceeds 360°."""
        result = calculate_part_of_fortune(
            asc_lon=350.0, sun_lon=10.0, moon_lon=40.0, is_day_chart=True
        )
        # 350 + 40 - 10 = 380 → 380 % 360 = 20 → Aries 20°
        assert result["longitude"] == pytest.approx(20.0, abs=0.001)
        assert result["sign"] == "Aries"

    def test_formula_day_chart(self):
        """Day chart formula string mentions Moon and Sun in correct order."""
        result = calculate_part_of_fortune(
            asc_lon=0.0, sun_lon=45.0, moon_lon=90.0, is_day_chart=True
        )

        assert "Moon" in result["formula"]
        assert "Sun" in result["formula"]
        # Verify Moon comes before Sun (day formula is ASC + Moon - Sun)
        assert result["formula"].index("Moon") < result["formula"].index("Sun")

    def test_formula_night_chart(self):
        """Night chart formula string mentions Sun before Moon."""
        result = calculate_part_of_fortune(
            asc_lon=0.0, sun_lon=45.0, moon_lon=90.0, is_day_chart=False
        )

        assert "Sun" in result["formula"]
        assert "Moon" in result["formula"]
        assert result["formula"].index("Sun") < result["formula"].index("Moon")

    def test_result_keys(self):
        """Return dict must contain all 6 expected keys."""
        result = calculate_part_of_fortune(
            asc_lon=15.0, sun_lon=100.0, moon_lon=200.0, is_day_chart=True
        )

        expected_keys = {
            "longitude",
            "sign",
            "degree_in_sign",
            "ruler",
            "formula",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())

    def test_sign_boundary_exactly_60(self):
        """Longitude exactly 60° → start of Gemini (0° Gemini)."""
        result = calculate_part_of_fortune(
            asc_lon=60.0, sun_lon=0.0, moon_lon=0.0, is_day_chart=True
        )
        # Day: 60 + 0 - 0 = 60 → Gemini 0°
        assert result["longitude"] == pytest.approx(60.0, abs=0.001)
        assert result["sign"] == "Gemini"
        assert result["degree_in_sign"] == pytest.approx(0.0, abs=0.001)

    def test_cancer_ruler_is_moon(self):
        """Part of Fortune in Cancer → ruler is Moon."""
        # Day: ASC=90, Moon=0, Sun=0 → 90 → Cancer 0°
        result = calculate_part_of_fortune(
            asc_lon=90.0, sun_lon=0.0, moon_lon=0.0, is_day_chart=True
        )

        assert result["sign"] == "Cancer"
        assert result["ruler"] == "Moon"

    def test_degree_in_sign_range(self):
        """degree_in_sign is always in [0, 30)."""
        for lon in [0.0, 29.9, 30.0, 59.9, 180.0, 359.9]:
            result = calculate_part_of_fortune(
                asc_lon=lon, sun_lon=0.0, moon_lon=0.0, is_day_chart=True
            )
            assert 0.0 <= result["degree_in_sign"] < 30.0, (
                f"degree_in_sign={result['degree_in_sign']} for lon={lon}"
            )


# ============================================================
# check_frustration
# ============================================================


class TestCheckFrustration:
    """Tests for Frustration — planet crosses sign boundary before perfecting aspect."""

    # ----------------------------------------------------------
    # Setup helpers
    # ----------------------------------------------------------

    @staticmethod
    def _moon_params_gemini_near_end():
        """
        Moon at 28° Gemini (lon=88°), speed=13.0°/day.
        Degrees left in Gemini: 30-28 = 2° → days to sign change = 2/13 ≈ 0.154.
        """
        return dict(planet1_lon=88.0, planet1_speed=13.0)

    # ----------------------------------------------------------
    # Frustrated cases
    # ----------------------------------------------------------

    def test_frustrated_moon_sextile(self):
        """
        Moon at 28° Gemini (88°) applies to Venus at 14° Leo (134°) via sextile (60°).

        diff = (134-88)%360 = 46
        arc to sextile (60°): (60-46)=14 → days=14/11.8≈1.19
        sign change in 2°: days=2/13≈0.154
        0.154 < 1.19 → FRUSTRATED
        """
        result = check_frustration(
            planet1_lon=88.0,  # Moon 28° Gemini
            planet1_speed=13.0,
            planet2_lon=134.0,  # Venus 14° Leo
            planet2_speed=1.2,
            aspect_angle=60.0,  # sextile
        )

        assert result["is_applying"] is True
        assert result["is_frustrated"] is True
        assert result["planet1_sign_now"] == "Gemini"
        assert result["planet1_sign_after_change"] == "Cancer"
        # Sign change faster than aspect perfection
        assert result["days_to_sign_change"] < result["days_to_perfection"]

    def test_frustrated_moon_conjunction_end_of_sign(self):
        """
        Moon at 29° Taurus (59°), speed=13.0, Mercury at 62° (2° Gemini), speed=1.4.
        Conjunction (0°): diff=(62-59)=3, arc=−3 → days=−3/11.6 < 0 → separating!
        Use Mercury at 56° (26° Taurus) instead:
        diff=(56-59)%360=357, target=0: arc=(0-357)%360=3, days=3/11.6≈0.26
        sign change: 30-29=1°, days=1/13≈0.077
        0.077 < 0.26 → FRUSTRATED
        """
        result = check_frustration(
            planet1_lon=59.0,  # Moon 29° Taurus
            planet1_speed=13.0,
            planet2_lon=56.0,  # Mercury 26° Taurus
            planet2_speed=1.4,
            aspect_angle=0.0,  # conjunction
        )

        assert result["is_applying"] is True
        assert result["is_frustrated"] is True
        assert result["days_to_sign_change"] < result["days_to_perfection"]

    # ----------------------------------------------------------
    # Not-frustrated cases
    # ----------------------------------------------------------

    def test_not_frustrated_plenty_of_room(self):
        """
        Moon at 15° Gemini (75°), speed=13.0, Saturn at 133° (13° Leo), speed=0.03.
        Sextile (60°): diff=(133-75)=58, arc=(60-58)=2, days=2/12.97≈0.154
        sign change: 30-15=15°, days=15/13≈1.154
        0.154 < 1.154 → NOT frustrated (aspect perfects first)
        """
        result = check_frustration(
            planet1_lon=75.0,  # Moon 15° Gemini
            planet1_speed=13.0,
            planet2_lon=133.0,  # Saturn 13° Leo
            planet2_speed=0.03,
            aspect_angle=60.0,
        )

        assert result["is_applying"] is True
        assert result["is_frustrated"] is False
        assert result["days_to_perfection"] < result["days_to_sign_change"]

    def test_not_applying_separating(self):
        """
        Moon at 88° (28° Gemini), Venus at 152° (2° Virgo): diff=64, sextile=60.
        arc_to_perfection = (60-64) = -4 → days_raw < 0 → NOT applying.
        Frustration cannot occur.
        """
        result = check_frustration(
            planet1_lon=88.0,
            planet1_speed=13.0,
            planet2_lon=152.0,
            planet2_speed=1.2,
            aspect_angle=60.0,
        )

        assert result["is_applying"] is False
        assert result["is_frustrated"] is False

    # ----------------------------------------------------------
    # Edge cases
    # ----------------------------------------------------------

    def test_stationary_planet1_with_retrograde_planet2(self):
        """
        planet1 stationary (speed=0), planet2 retrograde → relative_speed > 0.
        planet1 at 88° (28° Gemini), planet2 at 145° (25° Leo) rx speed=-1.0.
        Sextile: diff=(145-88)=57, arc=(60-57)=3, rel_speed=0-(-1)=1.0, days=3 > 0.
        is_applying = True, planet1_speed = 0 → stationary branch.
        """
        result = check_frustration(
            planet1_lon=88.0,
            planet1_speed=0.0,
            planet2_lon=145.0,
            planet2_speed=-1.0,
            aspect_angle=60.0,
        )

        assert result["is_applying"] is True
        assert result["is_frustrated"] is False
        assert "stationary" in result["explanation"].lower()

    def test_result_keys(self):
        """Return dict must contain all 8 expected keys."""
        result = check_frustration(
            planet1_lon=75.0,
            planet1_speed=13.0,
            planet2_lon=133.0,
            planet2_speed=0.03,
            aspect_angle=60.0,
        )

        expected_keys = {
            "is_frustrated",
            "is_applying",
            "days_to_perfection",
            "degrees_to_perfection",
            "degrees_to_sign_change",
            "days_to_sign_change",
            "planet1_sign_now",
            "planet1_sign_after_change",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())

    def test_sign_names_correct(self):
        """Sign names must be valid zodiac sign strings."""
        valid_signs = {
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
        }
        result = check_frustration(
            planet1_lon=75.0,
            planet1_speed=13.0,
            planet2_lon=133.0,
            planet2_speed=0.03,
            aspect_angle=60.0,
        )

        assert result["planet1_sign_now"] in valid_signs
        assert result["planet1_sign_after_change"] in valid_signs

    def test_days_to_perfection_positive_when_applying(self):
        """days_to_perfection is a positive float when aspect is applying."""
        result = check_frustration(
            planet1_lon=75.0,
            planet1_speed=13.0,
            planet2_lon=133.0,
            planet2_speed=0.03,
            aspect_angle=60.0,
        )

        assert result["is_applying"] is True
        assert result["days_to_perfection"] > 0

    def test_none_values_when_not_applying(self):
        """days_to_perfection and degrees_to_perfection are None when not applying."""
        result = check_frustration(
            planet1_lon=88.0,
            planet1_speed=13.0,
            planet2_lon=152.0,
            planet2_speed=1.2,
            aspect_angle=60.0,
        )

        assert result["is_applying"] is False
        assert result["days_to_perfection"] is None
        assert result["degrees_to_perfection"] is None

    def test_retrograde_planet1_sign_change_backward(self):
        """
        Retrograde planet1 moves toward previous sign.
        Mars RX at 2° Scorpio (212°), speed=-0.5 → sign change back to Libra in 2°.
        Saturn at 208° (Libra 28°), speed=0.03.

        diff=(208-212)%360=356, target=0: arc=(0-356)%360=4, > 180? No.
        4 → rel_speed=-0.5-0.03=-0.53 → days_raw=4/-0.53≈−7.5 < 0.

        Try: Saturn at 215° (Scorpio 5°): diff=(215-212)=3, arc=(0-3)%360=357>180→-3
        rel_speed=-0.53, days_raw=-3/-0.53≈5.66 > 0 → applying ✓
        sign_change: 212%30=2° → 2° back to Libra boundary, days=2/0.5=4
        4 < 5.66 → FRUSTRATED (retrograde crosses back to Libra) ✓
        """
        result = check_frustration(
            planet1_lon=212.0,  # Mars RX at 2° Scorpio
            planet1_speed=-0.5,
            planet2_lon=215.0,  # Saturn at 5° Scorpio
            planet2_speed=0.03,
            aspect_angle=0.0,  # conjunction
        )

        assert result["is_applying"] is True
        assert result["is_frustrated"] is True
        assert result["planet1_sign_now"] == "Scorpio"
        assert result["planet1_sign_after_change"] == "Libra"
        assert result["days_to_sign_change"] < result["days_to_perfection"]
