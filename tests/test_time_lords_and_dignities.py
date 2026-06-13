"""
Tests for:
  - Cazimi / Combust / Under Beams (accidental_dignities)
  - Peregrine detection (accidental_dignities)
  - Hayz detection (accidental_dignities)
  - Arabic Lots expansion (astro_adapter.calc_special_points)
  - Annual Profections (time_lords)
  - Firdaria (time_lords)
"""

import sys
from pathlib import Path
from datetime import date

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.accidental_dignities import (
    calc_solar_condition,
    is_peregrine,
    is_in_hayz,
    get_total_dignity,
    calculate_accidental_dignity,
)
from professional.time_lords import (
    annual_profections,
    profection_timeline,
    firdaria,
)


# ─────────────────────────────────────────────────────────────────────────────
# CAZIMI / COMBUST / UNDER BEAMS
# ─────────────────────────────────────────────────────────────────────────────


class TestSolarCondition:
    def test_cazimi_exactly_conjunct(self):
        """Planet at 0° separation from Sun → Cazimi."""
        r = calc_solar_condition("Mars", 45.0, 45.0)
        assert r["condition"] == "cazimi"
        assert r["score"] == 5

    def test_cazimi_within_17_arcmin(self):
        """Less than 17' from Sun → Cazimi."""
        r = calc_solar_condition("Venus", 100.20, 100.0)  # 0.20° < 0.2833°
        assert r["condition"] == "cazimi"

    def test_combust_within_8_5_degrees(self):
        """8° from Sun → Combust."""
        r = calc_solar_condition("Mercury", 28.0, 20.0)
        assert r["condition"] == "combust"
        assert r["score"] == -5

    def test_under_beams_9_to_17_degrees(self):
        """10° from Sun → Under Beams."""
        r = calc_solar_condition("Saturn", 30.0, 20.0)
        assert r["condition"] == "under_beams"
        assert r["score"] == -4

    def test_free_beyond_17_degrees(self):
        """20° from Sun → Free."""
        r = calc_solar_condition("Jupiter", 40.0, 20.0)
        assert r["condition"] == "free"
        assert r["score"] == 0

    def test_sun_always_free(self):
        """Sun itself is exempt."""
        r = calc_solar_condition("Sun", 100.0, 100.0)
        assert r["condition"] == "free"

    def test_moon_always_free(self):
        """Moon is exempt from combustion rules."""
        r = calc_solar_condition("Moon", 25.0, 20.0)
        assert r["condition"] == "free"

    def test_angular_wrap_around_360(self):
        """Separation wrapping at 0°/360° is handled correctly."""
        # Sun at 359°, Mars at 2° → separation = 3°, combust
        r = calc_solar_condition("Mars", 2.0, 359.0)
        assert r["orb"] == pytest.approx(3.0, abs=0.001)
        assert r["condition"] == "combust"

    def test_cazimi_boundary_just_inside(self):
        """Exactly at 0°17' = Cazimi (inclusive boundary)."""
        orb = 17 / 60  # 0.2833...°
        r = calc_solar_condition("Venus", 100.0 + orb, 100.0)
        assert r["condition"] == "cazimi"

    def test_combust_boundary_just_outside_cazimi(self):
        """Just past 17' → combust, not cazimi."""
        r = calc_solar_condition("Mercury", 100.0 + 0.30, 100.0)  # 0.30° > 0.2833°
        assert r["condition"] == "combust"


# ─────────────────────────────────────────────────────────────────────────────
# PEREGRINE
# ─────────────────────────────────────────────────────────────────────────────


class TestPeregrine:
    def test_sun_in_leo_not_peregrine(self):
        """Sun in Leo (domicile) = NOT peregrine."""
        sun_leo = 30 * 4 + 15.0  # Leo 15°
        assert not is_peregrine("Sun", sun_leo)

    def test_saturn_in_aries_no_dignity(self):
        """Saturn in Aries: check a spot where Saturn truly has no dignity.
        Fire signs: Saturn is participatory triplicity ruler, so it IS dignified in Aries.
        Find a sign where Saturn has nothing — e.g. Cancer (Water sign: day=Venus, night=Mars, part=Moon).
        At 1° Cancer, Saturn has: no rulership (Cancer=Moon), no exaltation (Libra),
        no triplicity ruler, term ruler at 0-6°=Mars → peregrine expected."""
        saturn_cancer_1 = 30 * 3 + 1.0  # Cancer 1°
        assert is_peregrine("Saturn", saturn_cancer_1, is_day=True)

    def test_mars_in_aries_domicile_not_peregrine(self):
        """Mars in Aries = domicile → NOT peregrine."""
        mars_aries = 10.0
        assert not is_peregrine("Mars", mars_aries)

    def test_moon_in_taurus_exaltation_not_peregrine(self):
        """Moon in Taurus = exaltation → NOT peregrine."""
        moon_taurus = 30 + 10.0  # Taurus 10°
        assert not is_peregrine("Moon", moon_taurus)

    def test_venus_in_virgo_term_ruler(self):
        """Venus in Virgo 7-17° is in its own term → NOT peregrine."""
        venus_virgo_term = 30 * 5 + 10.0  # Virgo 10° → Venus term 7-17
        assert not is_peregrine("Venus", venus_virgo_term)

    def test_uranus_not_classical_exempt(self):
        """Outer planets (Uranus) are exempt from peregrine rule → False."""
        assert not is_peregrine("Uranus", 100.0)


# ─────────────────────────────────────────────────────────────────────────────
# HAYZ
# ─────────────────────────────────────────────────────────────────────────────


class TestHayz:
    def test_sun_in_hayz_day_chart_above_horizon_masculine_sign(self):
        """Sun: diurnal planet, day chart, above horizon, Aries (masculine) → Hayz."""
        sun_aries = 15.0  # Aries = masculine
        assert is_in_hayz("Sun", sun_aries, is_above_horizon=True, is_day=True)

    def test_sun_not_hayz_night_chart(self):
        """Sun in night chart → wrong sect → NOT hayz."""
        assert not is_in_hayz("Sun", 15.0, is_above_horizon=True, is_day=False)

    def test_moon_in_hayz_night_below_horizon_feminine(self):
        """Moon: nocturnal, night chart, below horizon, Taurus (feminine) → Hayz."""
        moon_taurus = 30 + 15.0  # Taurus = feminine
        assert is_in_hayz("Moon", moon_taurus, is_above_horizon=False, is_day=False)

    def test_moon_not_hayz_above_horizon(self):
        """Moon above horizon in night chart → NOT hayz (below is required)."""
        assert not is_in_hayz("Moon", 45.0, is_above_horizon=True, is_day=False)

    def test_mars_hayz_night_below_horizon_feminine_sign(self):
        """Mars: nocturnal planet, night chart, below horizon, Scorpio (feminine) → Hayz."""
        mars_scorpio = 30 * 7 + 15.0  # Scorpio = feminine
        assert is_in_hayz("Mars", mars_scorpio, is_above_horizon=False, is_day=False)

    def test_saturn_hayz_day_above_horizon_masculine(self):
        """Saturn: diurnal, day chart, above horizon, Gemini (masculine) → Hayz."""
        sat_gemini = 30 * 2 + 10.0  # Gemini = masculine
        assert is_in_hayz("Saturn", sat_gemini, is_above_horizon=True, is_day=True)

    def test_outer_planet_never_hayz(self):
        """Uranus not in classical set → False."""
        assert not is_in_hayz("Uranus", 100.0, is_above_horizon=True, is_day=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANNUAL PROFECTIONS
# ─────────────────────────────────────────────────────────────────────────────


class TestAnnualProfections:
    def test_birth_year_is_first_house(self):
        """Age 0 → profected house = 1."""
        r = annual_profections("1990-01-01", target_date="1990-06-01", asc_sign="Aries")
        assert r["profected_house"] == 1
        assert r["age"] == 0

    def test_age_1_is_second_house(self):
        r = annual_profections("1990-01-01", "1991-06-01", asc_sign="Aries")
        assert r["profected_house"] == 2

    def test_age_12_wraps_back_to_first(self):
        r = annual_profections("1990-01-01", "2002-06-01", asc_sign="Aries")
        assert r["profected_house"] == 1

    def test_age_24_wraps_to_first(self):
        r = annual_profections("1990-01-01", "2014-06-01", asc_sign="Aries")
        assert r["profected_house"] == 1

    def test_aries_asc_age_0_lord_is_mars(self):
        """Aries ASC, age 0 → H1 = Aries → Lord = Mars."""
        r = annual_profections("1990-01-01", "1990-06-01", asc_sign="Aries")
        assert r["profected_sign"] == "Aries"
        assert r["lord_of_year"] == "Mars"

    def test_aries_asc_age_1_lord_is_venus(self):
        """Aries ASC, age 1 → H2 = Taurus → Lord = Venus."""
        r = annual_profections("1990-01-01", "1991-06-01", asc_sign="Aries")
        assert r["profected_sign"] == "Taurus"
        assert r["lord_of_year"] == "Venus"

    def test_profection_degree_increases_by_30_per_year(self):
        r0 = annual_profections("1990-01-01", "1990-06-01")
        r1 = annual_profections("1990-01-01", "1991-06-01")
        # Each completed year adds 30°
        assert r1["profection_degree"] == pytest.approx(r0["profection_degree"] + 30.0, abs=0.01)

    def test_house_themes_present(self):
        r = annual_profections("1990-01-01", "1995-06-01", asc_sign="Aries")
        assert isinstance(r["house_themes"], str)
        assert len(r["house_themes"]) > 10

    def test_next_birthday_after_target(self):
        r = annual_profections("1990-01-15", "2024-06-01")
        from datetime import date as _date
        nb = _date.fromisoformat(r["next_birthday"])
        assert nb > _date(2024, 6, 1)


class TestProfectionTimeline:
    def test_timeline_length(self):
        tl = profection_timeline("1990-01-01", years=12, asc_sign="Aries")
        assert len(tl) == 12

    def test_timeline_repeats_lord_every_12(self):
        tl = profection_timeline("1990-01-01", years=24, asc_sign="Aries")
        # Year 0 and year 12 should have same house
        assert tl[0]["profected_house"] == tl[12]["profected_house"]
        assert tl[0]["lord_of_year"] == tl[12]["lord_of_year"]


# ─────────────────────────────────────────────────────────────────────────────
# FIRDARIA
# ─────────────────────────────────────────────────────────────────────────────


class TestFirdaria:
    def test_day_chart_first_period_is_sun(self):
        """Day chart: first major period = Sun (10 years)."""
        r = firdaria("1990-01-01", is_day_chart=True, target_date="1993-01-01")
        assert r["major_period"] == "Sun"
        assert r["major_years"] == 10.0

    def test_night_chart_first_period_is_moon(self):
        """Night chart: first major period = Moon (9 years)."""
        r = firdaria("1990-01-01", is_day_chart=False, target_date="1993-01-01")
        assert r["major_period"] == "Moon"
        assert r["major_years"] == 9.0

    def test_full_sequence_sums_to_70_years(self):
        r = firdaria("1990-01-01", is_day_chart=True)
        total = sum(p["years"] for p in r["full_sequence"])
        assert total == pytest.approx(70.0, abs=0.001)

    def test_age_11_day_chart_transitions_to_venus(self):
        """Day chart, age 11 → Sun period ended (10y), now Venus."""
        r = firdaria("1990-01-01", is_day_chart=True, target_date="2001-06-01")
        assert r["major_period"] == "Venus"

    def test_sub_period_lord_present(self):
        r = firdaria("1990-01-01", is_day_chart=True, target_date="1993-01-01")
        assert r["sub_period"] in {"Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"}

    def test_returns_start_end_dates(self):
        r = firdaria("1990-01-01", is_day_chart=True, target_date="1993-01-01")
        assert "major_start_date" in r
        assert "major_end_date" in r
        assert "sub_start_date" in r
        assert "sub_end_date" in r

    def test_age_decimal_positive(self):
        r = firdaria("1990-01-01", is_day_chart=True, target_date="2000-01-01")
        assert r["age_decimal"] == pytest.approx(10.0, abs=0.05)
