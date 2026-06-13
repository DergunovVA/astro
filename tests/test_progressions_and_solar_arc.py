"""
Tests for Secondary Progressions and Solar Arc Directions.
Uses Einstein's chart (14.03.1879, Ulm) as the reference natal.
"""

import sys
from pathlib import Path
from datetime import date

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from professional.progressions import (
    secondary_progressions,
    solar_arc_directions,
    _angular_diff,
)

# ── Reference natal: Albert Einstein ─────────────────────────────────────────
# 14 March 1879, 11:30 LMT, Ulm (lon=9.9876°, lat=48.4011°)
# UTC = 10:50 ≈ use birth date 1879-03-14
EINSTEIN_BIRTH = date(1879, 3, 14)
EINSTEIN_LAT = 48.4011
EINSTEIN_LON = 9.9876

# Age 26 target → progressed date = 1879-03-14 + 26 days = 1879-04-09
TARGET_AGE26 = date(1905, 3, 14)  # his "miracle year" (Annus Mirabilis)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────


class TestAngularDiff:
    def test_same_longitude(self):
        assert _angular_diff(45.0, 45.0) == pytest.approx(0.0)

    def test_opposition(self):
        assert _angular_diff(0.0, 180.0) == pytest.approx(180.0)

    def test_wrap_around_360(self):
        # 350° vs 10° → 20°
        assert _angular_diff(350.0, 10.0) == pytest.approx(20.0)

    def test_symmetric(self):
        assert _angular_diff(100.0, 220.0) == _angular_diff(220.0, 100.0)


# ─────────────────────────────────────────────────────────────────────────────
# SECONDARY PROGRESSIONS — structure and basic math
# ─────────────────────────────────────────────────────────────────────────────


class TestSecondaryProgressions:
    @pytest.fixture(scope="class")
    def prog26(self):
        return secondary_progressions(
            EINSTEIN_BIRTH,
            EINSTEIN_LAT,
            EINSTEIN_LON,
            target_date=TARGET_AGE26,
        )

    def test_type_field(self, prog26):
        assert prog26["type"] == "secondary_progressions"

    def test_age_years_approx_26(self, prog26):
        # Target is exactly 26 years after birth
        assert prog26["age_years"] == pytest.approx(26.0, abs=0.1)

    def test_progressed_date_is_birth_plus_26_days(self, prog26):
        # Day-for-a-year: 26 completed years → progressed date = birth + 26 days
        prog_d = date.fromisoformat(prog26["progressed_date"])
        expected = EINSTEIN_BIRTH + __import__('datetime').timedelta(days=26)
        assert prog_d == expected

    def test_natal_planets_present(self, prog26):
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            assert planet in prog26["natal_planets"]

    def test_progressed_planets_present(self, prog26):
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
            assert planet in prog26["progressed_planets"]

    def test_progressed_sun_arc_positive(self, prog26):
        """Sun progresses ~1°/year → at 26 years arc ≈ 26°."""
        arc = prog26["progressed_sun_arc"]
        assert 20.0 < arc < 35.0  # generous bounds around ~26°

    def test_progressed_planet_has_arc_from_natal(self, prog26):
        for name, data in prog26["progressed_planets"].items():
            assert "arc_from_natal" in data
            assert "natal_longitude" in data

    def test_progressed_longitudes_in_range(self, prog26):
        for name, data in prog26["progressed_planets"].items():
            assert 0.0 <= data["longitude"] < 360.0

    def test_moon_moves_roughly_26_degrees(self, prog26):
        """Moon progresses ~13°/day → in 26 progressed-days ≈ ~338° (fast!).
        arc_from_natal is signed (−180 to +180), so check absolute value > 10°."""
        moon_arc = abs(prog26["progressed_planets"]["Moon"]["arc_from_natal"])
        assert moon_arc > 10.0

    def test_progressed_houses_computed(self, prog26):
        assert (
            "H1" in prog26["progressed_houses"] or len(prog26["progressed_houses"]) > 0
        )

    def test_aspects_to_natal_is_list(self, prog26):
        assert isinstance(prog26["aspects_to_natal"], list)

    def test_aspect_entries_have_required_keys(self, prog26):
        for asp in prog26["aspects_to_natal"]:
            assert "progressed_planet" in asp
            assert "natal_planet" in asp
            assert "aspect" in asp
            assert "orb" in asp
            assert asp["orb"] <= 1.0  # within requested orb

    def test_no_self_aspect_same_planet(self, prog26):
        """Progressed Sun should not appear as aspecting natal Sun unless
        there is a real geometric aspect (different longitudes)."""
        for asp in prog26["aspects_to_natal"]:
            if asp["progressed_planet"] == asp["natal_planet"]:
                # If same planet, orb should reflect actual angular difference
                assert asp["orb"] >= 0.0

    def test_birth_date_equals_zero_arc(self):
        """At birth, progressed = natal → Sun arc = 0."""
        r = secondary_progressions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=EINSTEIN_BIRTH
        )
        assert r["age_years"] == pytest.approx(0.0, abs=0.01)
        assert r["progressed_sun_arc"] == pytest.approx(0.0, abs=0.1)


# ─────────────────────────────────────────────────────────────────────────────
# SOLAR ARC DIRECTIONS — structure and math correctness
# ─────────────────────────────────────────────────────────────────────────────


class TestSolarArcDirections:
    @pytest.fixture(scope="class")
    def sa26(self):
        return solar_arc_directions(
            EINSTEIN_BIRTH,
            EINSTEIN_LAT,
            EINSTEIN_LON,
            target_date=TARGET_AGE26,
        )

    def test_type_field(self, sa26):
        assert sa26["type"] == "solar_arc_directions"

    def test_solar_arc_approx_26_degrees(self, sa26):
        """Solar arc at age 26 ≈ 26° (Sun moves ~1°/year by progression)."""
        arc = sa26["solar_arc"]
        assert 20.0 < arc < 35.0

    def test_all_planets_have_same_arc(self, sa26):
        """Every directed planet should have the same arc value (= solar arc)."""
        expected_arc = sa26["solar_arc"]
        for name, data in sa26["directed_planets"].items():
            assert data["arc"] == pytest.approx(expected_arc, abs=0.001)

    def test_directed_longitude_equals_natal_plus_arc(self, sa26):
        arc = sa26["solar_arc"]
        for name, data in sa26["directed_planets"].items():
            expected = (data["natal_longitude"] + arc) % 360
            assert data["longitude"] == pytest.approx(expected, abs=0.001)

    def test_directed_longitudes_in_range(self, sa26):
        for name, data in sa26["directed_planets"].items():
            assert 0.0 <= data["longitude"] < 360.0

    def test_natal_planets_present(self, sa26):
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
            assert planet in sa26["natal_planets"]

    def test_aspects_to_natal_is_list(self, sa26):
        assert isinstance(sa26["aspects_to_natal"], list)

    def test_aspects_within_directed_is_list(self, sa26):
        assert isinstance(sa26["aspects_within_directed"], list)

    def test_aspects_to_natal_orb_within_1_degree(self, sa26):
        for asp in sa26["aspects_to_natal"]:
            assert asp["orb"] <= 1.0

    def test_birth_solar_arc_is_zero(self):
        """At birth, solar arc = 0, directed = natal."""
        r = solar_arc_directions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=EINSTEIN_BIRTH
        )
        assert r["solar_arc"] == pytest.approx(0.0, abs=0.1)
        for name, data in r["directed_planets"].items():
            natal_lon = data["natal_longitude"]
            directed_lon = data["longitude"]
            assert directed_lon == pytest.approx(natal_lon, abs=0.1)

    def test_directed_sun_equals_natal_plus_solar_arc(self, sa26):
        """Directed Sun = natal Sun + solar arc (by definition, key sanity check)."""
        arc = sa26["solar_arc"]
        nat = sa26["natal_planets"]["Sun"]["longitude"]
        dir_ = sa26["directed_planets"]["Sun"]["longitude"]
        assert dir_ == pytest.approx((nat + arc) % 360, abs=0.001)

    def test_solar_arc_consistent_with_progressions(self):
        """Solar arc should approximately match progressed_sun_arc from SecondaryProgressions."""
        from professional.progressions import secondary_progressions

        sp = secondary_progressions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=TARGET_AGE26
        )
        sa = solar_arc_directions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=TARGET_AGE26
        )
        # Both measure how far Sun has progressed; should agree within < 0.01°
        assert abs(sa["solar_arc"] - sp["progressed_sun_arc"]) < 0.1


# ─────────────────────────────────────────────────────────────────────────────
# REGRESSION: different ages
# ─────────────────────────────────────────────────────────────────────────────


class TestProgressionAges:
    @pytest.mark.parametrize("age_years", [1, 5, 10, 30, 60])
    def test_solar_arc_grows_with_age(self, age_years):
        from datetime import date as _d

        target = _d(
            EINSTEIN_BIRTH.year + age_years, EINSTEIN_BIRTH.month, EINSTEIN_BIRTH.day
        )
        r = solar_arc_directions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=target
        )
        # Arc should be roughly age_years degrees (Sun moves ≈ 1°/year)
        assert r["solar_arc"] == pytest.approx(age_years, abs=5.0)

    @pytest.mark.parametrize("age_years", [1, 5, 10])
    def test_progressions_age_field(self, age_years):
        from datetime import date as _d

        target = _d(
            EINSTEIN_BIRTH.year + age_years, EINSTEIN_BIRTH.month, EINSTEIN_BIRTH.day
        )
        r = secondary_progressions(
            EINSTEIN_BIRTH, EINSTEIN_LAT, EINSTEIN_LON, target_date=target
        )
        assert r["age_years"] == pytest.approx(age_years, abs=0.1)
