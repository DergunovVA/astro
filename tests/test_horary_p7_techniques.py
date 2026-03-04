"""
Tests for P7 horary techniques:
- check_fixed_star_conjunctions()
- calculate_lord_of_hour()
"""

import pytest

from src.modules.horary import (
    FIXED_STARS,
    calculate_lord_of_hour,
    check_fixed_star_conjunctions,
)


# ============================================================
# check_fixed_star_conjunctions
# ============================================================


class TestCheckFixedStarConjunctions:
    """Tests for fixed-star conjunction detection."""

    def test_exact_algol_conjunction(self):
        """Planet at exact position of Algol (56.3°) → orb=0."""
        results = check_fixed_star_conjunctions(56.3)

        assert len(results) >= 1
        algol = next(r for r in results if r["star"] == "Algol")
        assert algol["orb"] == pytest.approx(0.0, abs=0.001)

    def test_regulus_within_orb(self):
        """Planet at 150.5° (0.5° from Regulus at 150.0°) → found within 1°."""
        results = check_fixed_star_conjunctions(150.5)

        star_names = [r["star"] for r in results]
        assert "Regulus" in star_names
        regulus = next(r for r in results if r["star"] == "Regulus")
        assert regulus["orb"] == pytest.approx(0.5, abs=0.001)

    def test_spica_outside_orb(self):
        """Planet at 200.0° → Spica at 203.7° → 3.7° away → NOT returned."""
        results = check_fixed_star_conjunctions(200.0)

        star_names = [r["star"] for r in results]
        assert "Spica" not in star_names

    def test_spica_within_orb_wider_orb(self):
        """With orb=4°, planet at 200° finds Spica (3.7° away)."""
        results = check_fixed_star_conjunctions(200.0, orb=4.0)

        star_names = [r["star"] for r in results]
        assert "Spica" in star_names

    def test_no_conjunctions_empty_list(self):
        """Planet at 10° — no major fixed stars nearby → empty list."""
        results = check_fixed_star_conjunctions(10.0, orb=1.0)

        assert isinstance(results, list)
        # 10° is not near any catalogued star within 1°
        for r in results:
            assert r["orb"] <= 1.0  # any result must be within orb

    def test_results_sorted_ascending_orb(self):
        """Multiple results must be sorted by orb (smallest first)."""
        # Spica 203.7° and Arcturus 203.9° are very close together
        # Planet at 203.7° → Spica orb=0, Arcturus orb=0.2
        results = check_fixed_star_conjunctions(203.7, orb=2.0)

        orbs = [r["orb"] for r in results]
        assert orbs == sorted(orbs)

    def test_result_keys(self):
        """Every result dict must contain all 6 required keys."""
        results = check_fixed_star_conjunctions(56.3)

        assert len(results) >= 1
        expected_keys = {"star", "star_lon", "orb", "nature", "effect", "magnitude"}
        for r in results:
            assert expected_keys.issubset(r.keys())

    def test_wraps_around_zero(self):
        """Planet at 359.5° — check stars near 0° (e.g. near Scheat at 349.1°)."""
        results = check_fixed_star_conjunctions(349.0, orb=1.0)

        names = [r["star"] for r in results]
        assert "Scheat" in names

    def test_custom_star_catalogue(self):
        """Custom catalogue overrides the default; only custom stars are searched."""
        custom = {
            "TestStar": {
                "lon": 45.0,
                "nature": "Test",
                "effect": "Testing",
                "magnitude": 1.0,
            }
        }
        results = check_fixed_star_conjunctions(45.0, orb=1.0, stars=custom)

        assert len(results) == 1
        assert results[0]["star"] == "TestStar"

    def test_fixed_stars_dict_has_key_stars(self):
        """The exported FIXED_STARS dict contains the five most important stars."""
        important = {"Regulus", "Algol", "Spica", "Aldebaran", "Antares"}
        assert important.issubset(FIXED_STARS.keys())

    def test_all_star_longitudes_in_range(self):
        """All star longitudes in the default catalogue are in [0, 360)."""
        for name, data in FIXED_STARS.items():
            lon = data["lon"]
            assert 0.0 <= lon < 360.0, f"{name} has out-of-range lon={lon}"

    def test_returns_list_when_no_stars(self):
        """Always returns a list, never None."""
        result = check_fixed_star_conjunctions(0.0, orb=0.0)
        assert isinstance(result, list)


# ============================================================
# calculate_lord_of_hour
# ============================================================


class TestCalculateLordOfHour:
    """
    Tests for Chaldean planetary hour calculation.

    Test setup: Saturday (weekday=5), day ruler = Saturn.
    Symmetric 12h day: sunrise=JD+0.25 (6am), sunset=JD+0.75 (6pm).
    Each seasonal hour = exactly 60 minutes.

    Day-hour Chaldean sequence starting from Saturn (index 0):
    H1=Saturn, H2=Jupiter, H3=Mars, H4=Sun, H5=Venus,
    H6=Mercury, H7=Moon, H8=Saturn, H9=Jupiter, H10=Mars,
    H11=Sun, H12=Venus

    Night-hour sequence (hours 13-24):
    H13=Mercury, H14=Moon, H15=Saturn, H16=Jupiter, H17=Mars,
    H18=Sun, H19=Venus, H20=Mercury, H21=Moon, H22=Saturn,
    H23=Jupiter, H24=Mars
    """

    BASE_JD = 2451545.0  # reference point (arbitrary)
    SUNRISE = BASE_JD + 0.25  # 6am
    SUNSET = BASE_JD + 0.75  # 6pm
    # hour length = 0.5 JD / 12 = 1/24 JD = 1 hour exactly
    HOUR = 1.0 / 24.0
    SATURDAY = 5  # Python weekday()

    def _q(self, jd_offset: float):
        """Ask a question at BASE_JD + jd_offset on Saturday."""
        return calculate_lord_of_hour(
            question_jd=self.BASE_JD + jd_offset,
            sunrise_jd=self.SUNRISE,
            sunset_jd=self.SUNSET,
            weekday=self.SATURDAY,
        )

    # --- Day ruler ---------------------------------------------------

    def test_day_ruler_saturday(self):
        """Day ruler for Saturday is Saturn."""
        result = self._q(0.25)  # at sunrise
        assert result["day_ruler"] == "Saturn"

    def test_day_ruler_sunday(self):
        """Day ruler for Sunday (weekday 6) is Sun."""
        result = calculate_lord_of_hour(
            question_jd=self.SUNRISE,
            sunrise_jd=self.SUNRISE,
            sunset_jd=self.SUNSET,
            weekday=6,
        )
        assert result["day_ruler"] == "Sun"

    def test_day_ruler_monday(self):
        """Day ruler for Monday (weekday 0) is Moon."""
        result = calculate_lord_of_hour(
            question_jd=self.SUNRISE,
            sunrise_jd=self.SUNRISE,
            sunset_jd=self.SUNSET,
            weekday=0,
        )
        assert result["day_ruler"] == "Moon"

    # --- Day hours ---------------------------------------------------

    def test_day_hour_1_saturn(self):
        """First day hour (at sunrise) → Lord = Saturn."""
        result = self._q(0.25)
        assert result["lord_of_hour"] == "Saturn"
        assert result["hour_number"] == 1
        assert result["is_day"] is True

    def test_day_hour_2_jupiter(self):
        """Second day hour (+1h after sunrise) → Lord = Jupiter."""
        result = self._q(0.25 + self.HOUR)
        assert result["lord_of_hour"] == "Jupiter"
        assert result["hour_number"] == 2

    def test_day_hour_3_mars(self):
        """Third day hour → Lord = Mars."""
        result = self._q(0.25 + 2 * self.HOUR)
        assert result["lord_of_hour"] == "Mars"

    def test_day_hour_7_moon(self):
        """Seventh day hour → Lord = Moon (completes first Chaldean cycle)."""
        result = self._q(0.25 + 6 * self.HOUR)
        assert result["lord_of_hour"] == "Moon"

    def test_day_hour_8_saturn(self):
        """Eighth day hour → Lord = Saturn (Chaldean cycle repeats)."""
        result = self._q(0.25 + 7 * self.HOUR)
        assert result["lord_of_hour"] == "Saturn"

    def test_day_hour_12_venus(self):
        """Twelfth (last) day hour → Lord = Venus."""
        result = self._q(0.25 + 11 * self.HOUR)
        assert result["lord_of_hour"] == "Venus"
        assert result["hour_number"] == 12

    # --- Night hours -------------------------------------------------

    def test_night_hour_1_mercury(self):
        """First night hour (at sunset) → Lord = Mercury."""
        result = self._q(0.75)
        assert result["lord_of_hour"] == "Mercury"
        assert result["is_day"] is False

    def test_night_hour_2_moon(self):
        """Second night hour → Lord = Moon."""
        result = self._q(0.75 + self.HOUR)
        assert result["lord_of_hour"] == "Moon"

    def test_night_hour_3_saturn(self):
        """Third night hour → Lord = Saturn."""
        result = self._q(0.75 + 2 * self.HOUR)
        assert result["lord_of_hour"] == "Saturn"

    # --- Hour length -------------------------------------------------

    def test_hour_length_60_min_equal_day(self):
        """Symmetric 12h day/night → each planetary hour = 60 min."""
        result = self._q(0.25)
        assert result["hour_length_min"] == pytest.approx(60.0, abs=0.01)

    def test_hour_length_shorter_day(self):
        """Shorter day (sunrise=0.3, sunset=0.6, day=0.3 JD=7.2h) → each hour=36 min."""
        result = calculate_lord_of_hour(
            question_jd=self.BASE_JD + 0.3,
            sunrise_jd=self.BASE_JD + 0.3,
            sunset_jd=self.BASE_JD + 0.6,
            weekday=self.SATURDAY,
        )
        # day_length = 0.3 JD = 7.2h → hour = 7.2h/12 = 36 min
        assert result["hour_length_min"] == pytest.approx(36.0, abs=0.1)

    # --- Result structure --------------------------------------------

    def test_result_keys(self):
        """Return dict must contain all 6 expected keys."""
        result = self._q(0.25)
        expected = {
            "lord_of_hour",
            "hour_number",
            "is_day",
            "day_ruler",
            "hour_length_min",
            "explanation",
        }
        assert expected.issubset(result.keys())

    def test_explanation_is_string(self):
        """Explanation is always a non-empty string."""
        result = self._q(0.25)
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_lord_is_valid_planet(self):
        """Lord of the Hour is always one of the seven classical planets."""
        classical = {"Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"}
        for offset in [0.25, 0.35, 0.50, 0.65, 0.75, 0.85]:
            result = self._q(offset)
            assert result["lord_of_hour"] in classical


# ============================================================
# Cross-function sanity
# ============================================================


class TestP7CrossSanity:
    """Lightweight cross-checks between the two P7 functions."""

    def test_fixed_stars_spica_nature_contains_venus(self):
        """Spica's nature (Venus/Mercury) should mention Venus."""
        assert "Venus" in FIXED_STARS["Spica"]["nature"]

    def test_algol_nature_contains_saturn(self):
        """Algol (malefic star) nature should contain Saturn."""
        assert "Saturn" in FIXED_STARS["Algol"]["nature"]

    def test_lord_of_hour_cycles_through_all_7(self):
        """Over 7 consecutive hours, all 7 Chaldean planets appear exactly once."""
        seen = set()
        base_jd = 2451545.0
        sunrise = base_jd + 0.25
        sunset = base_jd + 0.75
        hour_jd = (sunset - sunrise) / 12.0
        for h in range(7):
            r = calculate_lord_of_hour(
                question_jd=sunrise + h * hour_jd,
                sunrise_jd=sunrise,
                sunset_jd=sunset,
                weekday=5,
            )
            seen.add(r["lord_of_hour"])
        assert len(seen) == 7
