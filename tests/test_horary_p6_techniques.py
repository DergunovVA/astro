"""
Tests for P6 horary techniques:
- calculate_antiscia()
- find_antiscia_aspects()
- check_besieging()
- is_via_combusta()
"""

import pytest

from src.modules.horary import (
    calculate_antiscia,
    check_besieging,
    find_antiscia_aspects,
    is_via_combusta,
)


# ============================================================
# calculate_antiscia
# ============================================================


class TestCalculateAntiscia:
    """Tests for antiscion / contra-antiscion calculation."""

    def test_aries_15_maps_to_virgo_15(self):
        """
        Classic pair: Aries 15° (lon=15°) ↔ Virgo 15° (lon=165°).
        Same solar declination on both sides of the Cancer solstice.
        antiscion = (180 − 15) % 360 = 165°
        """
        result = calculate_antiscia(15.0)

        assert result["antiscion"] == pytest.approx(165.0, abs=0.001)
        assert result["sign_antiscion"] == "Virgo"

    def test_gemini_0_maps_to_leo_0(self):
        """
        0° Gemini (60°) → antiscion at 120° = 0° Leo.
        Both are equidistant (30°) from 0° Cancer solstice.
        """
        result = calculate_antiscia(60.0)

        assert result["antiscion"] == pytest.approx(120.0, abs=0.001)
        assert result["sign_antiscion"] == "Leo"

    def test_cancer_0_is_self_antiscion(self):
        """
        0° Cancer (90°) is exactly on the solstice axis → antiscion = self (90°).
        antiscion = (180 − 90) % 360 = 90°
        """
        result = calculate_antiscia(90.0)

        assert result["antiscion"] == pytest.approx(90.0, abs=0.001)
        assert result["sign_antiscion"] == "Cancer"

    def test_capricorn_0_is_self_antiscion(self):
        """
        0° Capricorn (270°) is on the other solstice → antiscion = self.
        antiscion = (180 − 270) % 360 = (−90) % 360 = 270°
        """
        result = calculate_antiscia(270.0)

        assert result["antiscion"] == pytest.approx(270.0, abs=0.001)
        assert result["sign_antiscion"] == "Capricorn"

    def test_gemini_15_maps_to_cancer_15(self):
        """
        Gemini 15° (75°) ↔ Cancer 15° (105°): equidistant from 0°Cancer.
        antiscion = 180 − 75 = 105°
        """
        result = calculate_antiscia(75.0)

        assert result["antiscion"] == pytest.approx(105.0, abs=0.001)
        assert result["sign_antiscion"] == "Cancer"

    def test_contra_antiscion_is_opposition_of_antiscion(self):
        """
        Contra-antiscion = antiscion + 180°.
        For Aries 15° (15°): contra = (360 − 15) % 360 = 345° = Pisces 15°
        """
        result = calculate_antiscia(15.0)

        expected_contra = (result["antiscion"] + 180.0) % 360.0
        assert result["contra_antiscion"] == pytest.approx(expected_contra, abs=0.001)
        assert result["sign_contra_antiscion"] == "Pisces"

    def test_normalises_longitude_over_360(self):
        """Input longitude > 360 is normalised before calculation."""
        result_normal = calculate_antiscia(15.0)
        result_over = calculate_antiscia(375.0)  # 375 % 360 = 15

        assert result_normal["antiscion"] == pytest.approx(
            result_over["antiscion"], abs=0.001
        )

    def test_result_keys(self):
        """Return dict must contain the four expected keys."""
        result = calculate_antiscia(45.0)

        expected_keys = {
            "antiscion",
            "contra_antiscion",
            "sign_antiscion",
            "sign_contra_antiscion",
        }
        assert expected_keys.issubset(result.keys())

    def test_both_values_in_0_to_360(self):
        """Antiscion and contra-antiscion are always in [0, 360)."""
        for lon in [0.0, 45.0, 90.0, 180.0, 270.0, 359.0]:
            r = calculate_antiscia(lon)
            assert 0.0 <= r["antiscion"] < 360.0
            assert 0.0 <= r["contra_antiscion"] < 360.0


# ============================================================
# find_antiscia_aspects
# ============================================================


class TestFindAntisciaAspects:
    """Tests for antiscia connection detection between two planets."""

    def test_exact_antiscion_connection(self):
        """
        Planet1 at Aries 15° (15°), Planet2 at Virgo 15° (165°).
        antiscion(15°) = 165° → exact match → has_antiscia=True, type='antiscion'.
        """
        result = find_antiscia_aspects(15.0, 165.0)

        assert result["has_antiscia"] is True
        assert result["type"] == "antiscion"
        assert result["orb"] == pytest.approx(0.0, abs=0.001)

    def test_exact_contra_antiscion_connection(self):
        """
        Planet1 at 15°, contra-antiscion = 345° = Pisces 15°.
        Planet2 at 345° → exact contra-antiscion.
        """
        result = find_antiscia_aspects(15.0, 345.0)

        assert result["has_antiscia"] is True
        assert result["type"] == "contra-antiscion"
        assert result["orb"] == pytest.approx(0.0, abs=0.001)

    def test_within_orb_antiscion(self):
        """
        Planet1=15°, antiscion=165°. Planet2=165.7° → orb=0.7° ≤ 1° → has_antiscia.
        """
        result = find_antiscia_aspects(15.0, 165.7)

        assert result["has_antiscia"] is True
        assert result["type"] == "antiscion"
        assert result["orb"] == pytest.approx(0.7, abs=0.001)

    def test_outside_orb_no_connection(self):
        """
        Planet1=15°, antiscion=165°. Planet2=166.5° → orb=1.5° > 1° → no connection.
        """
        result = find_antiscia_aspects(15.0, 166.5)

        assert result["has_antiscia"] is False
        assert result["type"] is None
        assert result["orb"] is None

    def test_no_antiscia_unrelated_planets(self):
        """
        Planet1=0°, Planet2=90°: antiscion=180°, contra=0°. Neither matches 90°.
        """
        result = find_antiscia_aspects(0.0, 90.0)

        assert result["has_antiscia"] is False

    def test_custom_orb_respected(self):
        """
        With orb=2°: Planet2=166.5° (1.5° from antiscion of 15°) → should connect.
        With orb=1°: same Planet2 → should not connect.
        """
        result_wide = find_antiscia_aspects(15.0, 166.5, orb=2.0)
        result_narrow = find_antiscia_aspects(15.0, 166.5, orb=1.0)

        assert result_wide["has_antiscia"] is True
        assert result_narrow["has_antiscia"] is False

    def test_result_keys(self):
        """Return dict must contain the six expected keys."""
        result = find_antiscia_aspects(15.0, 165.0)

        expected_keys = {
            "has_antiscia",
            "type",
            "orb",
            "antiscion_lon",
            "contra_lon",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())

    def test_antiscion_lon_matches_calculate_antiscia(self):
        """antiscion_lon in result matches calculate_antiscia() output."""
        base = calculate_antiscia(30.0)
        result = find_antiscia_aspects(30.0, 0.0)  # unrelated planet2

        assert result["antiscion_lon"] == pytest.approx(base["antiscion"], abs=0.001)
        assert result["contra_lon"] == pytest.approx(
            base["contra_antiscion"], abs=0.001
        )

    def test_prefers_smaller_orb_type(self):
        """
        When planet2 is within orb of BOTH antiscion and contra-antiscion
        (unlikely for tight orbs, but verify ordering: smallest orb wins).
        antiscion(90°)=90° and contra(90°)=270°.
        Planet2=89.5°: orb_antiscion=0.5°, orb_contra=180.5° → antiscion wins.
        """
        result = find_antiscia_aspects(90.0, 89.5, orb=1.0)

        assert result["has_antiscia"] is True
        assert result["type"] == "antiscion"
        assert result["orb"] == pytest.approx(0.5, abs=0.001)


# ============================================================
# check_besieging
# ============================================================


class TestCheckBesieging:
    """Tests for besieging detection (planet enclosed between Mars and Saturn)."""

    @staticmethod
    def _planets(venus_lon, mars_lon, saturn_lon):
        """Helper to build all_planets dict."""
        return {
            "Venus": {"lon": venus_lon},
            "Mars": {"lon": mars_lon},
            "Saturn": {"lon": saturn_lon},
        }

    def test_besieged_equal_arcs(self):
        """
        Venus at 135° (Leo 15°), Mars at 130° (5° behind), Saturn at 140° (5° ahead).
        Both within 8° default orb → BESIEGED.
        """
        result = check_besieging("Venus", 135.0, self._planets(135.0, 130.0, 140.0))

        assert result["is_besieged"] is True
        assert result["arc_ahead"] == pytest.approx(5.0, abs=0.001)
        assert result["arc_behind"] == pytest.approx(5.0, abs=0.001)
        assert result["malefic_ahead"] == "Saturn"
        assert result["malefic_behind"] == "Mars"

    def test_besieged_tight_orb(self):
        """
        Venus at 135°, Mars at 134° (1° behind), Saturn at 136° (1° ahead).
        1° << 8° → besieged ✓
        """
        result = check_besieging("Venus", 135.0, self._planets(135.0, 134.0, 136.0))

        assert result["is_besieged"] is True

    def test_not_besieged_both_malefics_ahead(self):
        """
        Both malefics ahead of Venus → not enclosed.
        Venus at 135°, Mars at 140°, Saturn at 145°.
        """
        result = check_besieging("Venus", 135.0, self._planets(135.0, 140.0, 145.0))

        assert result["is_besieged"] is False

    def test_not_besieged_both_malefics_behind(self):
        """Both malefics behind Venus (same side)."""
        result = check_besieging("Venus", 135.0, self._planets(135.0, 128.0, 122.0))

        assert result["is_besieged"] is False

    def test_not_besieged_orb_exceeded(self):
        """
        Venus at 135°, Mars at 126° (9° behind), Saturn at 144° (9° ahead).
        9° > 8° default orb → not besieged.
        """
        result = check_besieging("Venus", 135.0, self._planets(135.0, 126.0, 144.0))

        assert result["is_besieged"] is False
        assert result["arc_ahead"] == pytest.approx(9.0, abs=0.001)
        assert result["arc_behind"] == pytest.approx(9.0, abs=0.001)

    def test_custom_orb_allows_wider_besieging(self):
        """
        With orb=10° the same 9° case becomes besieged.
        """
        result = check_besieging(
            "Venus", 135.0, self._planets(135.0, 126.0, 144.0), orb=10.0
        )

        assert result["is_besieged"] is True

    def test_missing_one_malefic(self):
        """
        Only Mars present (no Saturn) → fewer than 2 malefics → not besieged.
        """
        planets = {"Venus": {"lon": 135.0}, "Mars": {"lon": 130.0}}
        result = check_besieging("Venus", 135.0, planets)

        assert result["is_besieged"] is False
        assert "Less than two" in result["explanation"]

    def test_planet_is_mars(self):
        """
        When the tested planet IS Mars, Mars is excluded from malefics list.
        Only Saturn remains → not besieged.
        """
        planets = {
            "Mars": {"lon": 135.0},
            "Saturn": {"lon": 140.0},
            "Jupiter": {"lon": 130.0},
        }
        result = check_besieging("Mars", 135.0, planets)

        assert result["is_besieged"] is False

    def test_wraps_around_0_degrees(self):
        """
        Venus at 2°, Mars at 357° (5° behind across 0°), Saturn at 7° (5° ahead).
        signed_arc(2,357): (357-2)%360=355 → >180 → 355-360=-5° (behind ✓)
        signed_arc(2,7): 5° (ahead ✓) → BESIEGED.
        """
        planets = {
            "Venus": {"lon": 2.0},
            "Mars": {"lon": 357.0},
            "Saturn": {"lon": 7.0},
        }
        result = check_besieging("Venus", 2.0, planets)

        assert result["is_besieged"] is True

    def test_result_keys(self):
        """Return dict must contain all 6 expected keys."""
        result = check_besieging("Venus", 135.0, self._planets(135.0, 130.0, 140.0))

        expected_keys = {
            "is_besieged",
            "malefic_ahead",
            "malefic_behind",
            "arc_ahead",
            "arc_behind",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())


# ============================================================
# is_via_combusta
# ============================================================


class TestIsViaCombusta:
    """Tests for Via Combusta (Moon 15° Libra – 15° Scorpio, 195°–225°)."""

    def test_middle_of_zone(self):
        """Moon at 210° (Scorpio 0°) is firmly in Via Combusta."""
        result = is_via_combusta(210.0)

        assert result["is_via_combusta"] is True
        assert result["moon_sign"] == "Scorpio"
        assert result["degrees_into_zone"] == pytest.approx(15.0, abs=0.001)

    def test_exact_start_boundary(self):
        """Moon at exactly 195° (15° Libra) → IN zone (boundary inclusive)."""
        result = is_via_combusta(195.0)

        assert result["is_via_combusta"] is True
        assert result["degrees_into_zone"] == pytest.approx(0.0, abs=0.001)

    def test_exact_end_boundary(self):
        """Moon at exactly 225° (15° Scorpio) → IN zone (boundary inclusive)."""
        result = is_via_combusta(225.0)

        assert result["is_via_combusta"] is True
        assert result["degrees_into_zone"] == pytest.approx(30.0, abs=0.001)

    def test_just_before_zone(self):
        """Moon at 194.9° → NOT in Via Combusta."""
        result = is_via_combusta(194.9)

        assert result["is_via_combusta"] is False
        assert result["degrees_into_zone"] is None

    def test_just_after_zone(self):
        """Moon at 225.1° → NOT in Via Combusta."""
        result = is_via_combusta(225.1)

        assert result["is_via_combusta"] is False
        assert result["degrees_into_zone"] is None

    def test_aries_not_via_combusta(self):
        """Moon at 0° (Aries) → not in zone."""
        result = is_via_combusta(0.0)

        assert result["is_via_combusta"] is False

    def test_libra_early_not_via_combusta(self):
        """Moon at 180° (Libra 0°) → not in zone (zone starts at Libra 15°)."""
        result = is_via_combusta(180.0)

        assert result["is_via_combusta"] is False

    def test_zone_constants_in_result(self):
        """zone_start and zone_end are always correct."""
        result = is_via_combusta(200.0)

        assert result["zone_start"] == 195.0
        assert result["zone_end"] == 225.0

    def test_normalises_over_360(self):
        """Longitude > 360 is normalised (e.g. 555° = 195° = zone start)."""
        result = is_via_combusta(555.0)  # 555 % 360 = 195

        assert result["is_via_combusta"] is True
        assert result["moon_longitude"] == pytest.approx(195.0, abs=0.001)

    def test_result_keys(self):
        """Return dict must contain all 7 expected keys."""
        result = is_via_combusta(200.0)

        expected_keys = {
            "is_via_combusta",
            "moon_longitude",
            "moon_sign",
            "zone_start",
            "zone_end",
            "degrees_into_zone",
            "explanation",
        }
        assert expected_keys.issubset(result.keys())

    def test_explanation_is_string(self):
        """Explanation is always a non-empty string."""
        for lon in [180.0, 200.0, 230.0]:
            result = is_via_combusta(lon)
            assert isinstance(result["explanation"], str)
            assert len(result["explanation"]) > 0
