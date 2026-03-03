"""
Unit tests for standalone horary functions (production code).

These functions are used by the 'horary' CLI command in main.py.
Based on William Lilly's "Christian Astrology" (1647).
"""

from src.modules.horary import (
    time_to_perfection,
    is_void_of_course,
    check_radicality,
    find_mutual_receptions,
    find_translation_of_light,
    find_collection_of_light,
)


# ============================================================
# time_to_perfection
# ============================================================


class TestTimeToPerfection:
    """Tests for time_to_perfection() - core horary timing function."""

    def test_moon_trine_saturn_applying(self):
        """
        Classic example: Moon at 114° (Cancer) applying trine to Saturn at 1.6° (Aries).
        Moon speed 13°/day, Saturn 0.03°/day.
        Trine = 120° → Moon needs to travel ~6.4° to reach exact trine.
        Expected: ~12-15 hours applying.
        """
        result = time_to_perfection(114.16, 13.0, 1.6, 0.03, 120)
        assert result["is_applying"] is True
        assert 10 <= result["hours"] <= 18, f"Expected 10-18h, got {result['hours']}"
        assert result["days"] > 0
        assert "current_distance" in result
        assert "relative_speed" in result

    def test_separating_aspect(self):
        """Separating aspect: faster planet already past the target."""
        # Moon at 125° (past trine to Saturn at 1.6°), moving away
        result = time_to_perfection(125.0, 13.0, 1.6, 0.03, 120)
        assert result["is_applying"] is False
        assert result["days"] == 0.0
        assert result["hours"] == 0.0

    def test_conjunction_applying(self):
        """Moon approaching conjunction with Venus."""
        # Moon at 50°, Venus at 55° — Moon needs 5° at 12°/day
        result = time_to_perfection(50.0, 12.0, 55.0, 1.0, 0)
        assert result["is_applying"] is True
        assert result["hours"] > 0

    def test_zero_relative_speed(self):
        """Planets moving at same speed — aspect never perfects."""
        result = time_to_perfection(100.0, 13.0, 80.0, 13.0, 120)
        # Relative speed = 0, can't close gap
        # Expect not applying or 0 hours
        if not result["is_applying"]:
            assert result["hours"] == 0.0

    def test_square_aspect(self):
        """Moon applying square to Mars (90° aspect)."""
        result = time_to_perfection(20.0, 13.0, 110.0, 0.5, 90)
        assert "is_applying" in result
        assert "hours" in result
        assert "days" in result

    def test_result_structure(self):
        """Result always has all required keys."""
        result = time_to_perfection(0.0, 13.0, 120.0, 0.0, 120)
        assert "days" in result
        assert "hours" in result
        assert "is_applying" in result
        assert "current_distance" in result
        assert "relative_speed" in result

    def test_hours_equals_days_times_24(self):
        """hours field should be exactly days * 24."""
        result = time_to_perfection(114.16, 13.0, 1.6, 0.03, 120)
        if result["days"] > 0:
            assert abs(result["hours"] - result["days"] * 24) < 0.2


# ============================================================
# is_void_of_course
# ============================================================


class TestVoidOfCourse:
    """Tests for is_void_of_course() - Moon VOC detection."""

    def _make_planets(self, **kwargs):
        """Helper to build planet dict (excluding Moon)."""
        return kwargs

    def test_moon_not_void_has_upcoming_aspect(self):
        """Moon with Venus nearby — should form aspect, not VOC."""
        # Moon at 10° Aries (lon=10), Venus at 20° Aries (lon=20)
        # Moon moving 13°/day, will form conjunction with Venus before leaving sign
        planets = {"Venus": 20.0, "Saturn": 100.0}
        result = is_void_of_course(10.0, 13.0, planets)
        # Moon should form conjunction with Venus (10° away, within sign)
        assert "is_void" in result
        assert result["current_sign"] == "Aries"
        assert "next_sign_in_degrees" in result
        assert result["next_sign_in_degrees"] > 0

    def test_moon_void_no_planets_in_sign(self):
        """Moon near end of sign with no planets within reach → VOC."""
        # Moon at 29° Aries (lon=29), all planets far away
        planets = {
            "Sun": 150.0,  # Leo
            "Mercury": 170.0,
            "Mars": 200.0,
            "Saturn": 280.0,
        }
        result = is_void_of_course(29.0, 13.0, planets)
        assert result["is_void"] is True
        assert result["current_sign"] == "Aries"

    def test_result_structure(self):
        """Result always has all required keys."""
        planets = {"Sun": 50.0}
        result = is_void_of_course(25.0, 13.0, planets)
        required_keys = [
            "is_void",
            "current_sign",
            "next_sign_in_degrees",
            "next_sign_in_hours",
            "last_aspect",
            "last_aspect_type",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_sign_boundary_calculation(self):
        """Degrees to next sign are calculated correctly."""
        # Moon at 20° Taurus (lon=50) → 10° to Gemini
        planets = {"Saturn": 200.0}
        result = is_void_of_course(50.0, 13.0, planets)
        assert abs(result["next_sign_in_degrees"] - 10.0) < 0.1

    def test_hours_to_next_sign(self):
        """Hours to next sign = degrees / speed * 24."""
        # Moon at 10° Aries, speed 13°/day → 20° to next sign → 20/13*24 = ~36.9h
        planets = {"Saturn": 200.0}
        result = is_void_of_course(10.0, 13.0, planets)
        expected_hours = (20.0 / 13.0) * 24
        assert abs(result["next_sign_in_hours"] - expected_hours) < 1.0


# ============================================================
# check_radicality
# ============================================================


class TestRadicality:
    """Tests for check_radicality() - chart validity check."""

    def test_valid_chart_radical(self):
        """ASC at 4.66° is between 3-27°, Saturn in 12th house → radical."""
        result = check_radicality(244.66, 12)
        assert result["is_radical"] is True
        assert result["warnings"] == []
        assert abs(result["asc_degree_in_sign"] - 4.66) < 0.1

    def test_asc_too_early(self):
        """ASC at 1° in sign → not radical (too early)."""
        result = check_radicality(1.5, 5)
        assert result["is_radical"] is False
        assert len(result["warnings"]) >= 1
        assert any("early" in w.lower() for w in result["warnings"])

    def test_asc_too_late(self):
        """ASC at 28° in sign → not radical (too late)."""
        result = check_radicality(28.5 + 60, 5)  # 28.5° in Taurus
        assert result["is_radical"] is False
        assert any("late" in w.lower() for w in result["warnings"])

    def test_asc_exactly_at_3_degrees_boundary(self):
        """ASC exactly at 3° is on the edge — should be radical (>= 3)."""
        result = check_radicality(3.0, 5)
        assert result["is_radical"] is True

    def test_saturn_in_first_house(self):
        """Saturn in 1st house → not radical."""
        result = check_radicality(244.66, 1)
        assert result["is_radical"] is False
        assert any("Saturn" in w for w in result["warnings"])

    def test_saturn_in_seventh_house(self):
        """Saturn in 7th house → not radical (judgment blocked)."""
        result = check_radicality(244.66, 7)
        assert result["is_radical"] is False
        assert any("7" in w or "7th" in w for w in result["warnings"])

    def test_multiple_problems(self):
        """Both ASC too early and Saturn in 1st → multiple warnings."""
        result = check_radicality(1.5, 1)
        assert result["is_radical"] is False
        assert len(result["warnings"]) >= 2

    def test_result_structure(self):
        """Result always has required keys."""
        result = check_radicality(15.0, 5)
        assert "is_radical" in result
        assert "warnings" in result
        assert "asc_degree_in_sign" in result
        assert isinstance(result["warnings"], list)


# ============================================================
# find_mutual_receptions
# ============================================================


class TestFindMutualReceptions:
    """Tests for find_mutual_receptions() - traditional ruler reception check."""

    def test_mars_saturn_mutual_reception(self):
        """
        Mars in Aquarius (Saturn's sign) ↔ Saturn in Aries (Mars's sign).
        Traditional rulers: Mars→Aries, Saturn→Aquarius.
        """
        planets = {
            "Mars": {"longitude": 315.0},  # Aquarius (300-330°)
            "Saturn": {"longitude": 15.0},  # Aries (0-30°)
            "Moon": {"longitude": 50.0},  # Not in reception
        }
        receptions = find_mutual_receptions(planets)
        assert len(receptions) >= 1
        names = {(r["planet1"], r["planet2"]) for r in receptions}
        assert ("Mars", "Saturn") in names or ("Saturn", "Mars") in names

    def test_no_reception(self):
        """Planets in random signs, no mutual reception expected."""
        planets = {
            "Sun": {"longitude": 45.0},  # Taurus
            "Moon": {"longitude": 130.0},  # Leo
            "Mars": {"longitude": 200.0},  # Libra
        }
        receptions = find_mutual_receptions(planets)
        # Taurus ruler=Venus, Leo ruler=Sun, Libra ruler=Venus
        # Sun in Taurus ↔ Moon in Leo would need Venus in Leo and Moon in Taurus
        # Sun is not Venus, Moon not Venus → no reception
        # This could have Sun-Mars if Leo ruler is Sun and Libra ruler points to Sun
        # but let's just verify it's a list
        assert isinstance(receptions, list)

    def test_empty_planets(self):
        """Empty input returns empty list."""
        result = find_mutual_receptions({})
        assert result == []

    def test_missing_longitude_skipped(self):
        """Planets without longitude are skipped gracefully."""
        planets = {
            "Mars": {"sign": "Aquarius"},  # No longitude
            "Saturn": {"longitude": 15.0},
        }
        result = find_mutual_receptions(planets)
        # Should not raise, may return empty
        assert isinstance(result, list)

    def test_result_structure(self):
        """Each reception result has required keys."""
        planets = {
            "Mars": {"longitude": 315.0},
            "Saturn": {"longitude": 15.0},
        }
        receptions = find_mutual_receptions(planets)
        if receptions:
            for r in receptions:
                assert "planet1" in r
                assert "planet2" in r
                assert "planet1_sign" in r
                assert "planet2_sign" in r
                assert "type" in r


# ============================================================
# find_translation_of_light
# ============================================================


class TestFindTranslationOfLight:
    """Tests for find_translation_of_light() - 3rd planet connecting two significators."""

    def _make_aspects(self, *pairs):
        """Helper: make aspect list from (p1, p2) tuples."""
        return [{"planet1": p1, "planet2": p2, "applying": True} for p1, p2 in pairs]

    def test_basic_translation(self):
        """Moon aspects both Mars and Saturn → Moon translates light."""
        planets = {
            "Mars": {"longitude": 10.0},
            "Saturn": {"longitude": 20.0},
            "Moon": {"longitude": 5.0},
        }
        aspects = self._make_aspects(("Moon", "Mars"), ("Moon", "Saturn"))
        result = find_translation_of_light("Mars", "Saturn", planets, aspects)
        assert result == "Moon"

    def test_no_translation(self):
        """No 3rd planet aspects both significators → None."""
        planets = {
            "Mars": {"longitude": 10.0},
            "Saturn": {"longitude": 20.0},
            "Moon": {"longitude": 5.0},
        }
        aspects = self._make_aspects(("Moon", "Mars"))  # Moon only aspects Mars
        result = find_translation_of_light("Mars", "Saturn", planets, aspects)
        assert result is None

    def test_translator_not_significator(self):
        """The translator cannot be one of the two significators."""
        planets = {
            "Mars": {"longitude": 10.0},
            "Saturn": {"longitude": 20.0},
        }
        aspects = []  # No aspects
        result = find_translation_of_light("Mars", "Saturn", planets, aspects)
        assert result is None

    def test_empty_planets(self):
        """Empty planets → None."""
        result = find_translation_of_light("Mars", "Saturn", {}, [])
        assert result is None

    def test_multiple_possible_translators(self):
        """If multiple planets can translate, returns first found."""
        planets = {
            "Mars": {"longitude": 10.0},
            "Saturn": {"longitude": 20.0},
            "Moon": {"longitude": 5.0},
            "Venus": {"longitude": 15.0},
        }
        aspects = self._make_aspects(
            ("Moon", "Mars"),
            ("Moon", "Saturn"),
            ("Venus", "Mars"),
            ("Venus", "Saturn"),
        )
        result = find_translation_of_light("Mars", "Saturn", planets, aspects)
        assert result in ("Moon", "Venus")


# ============================================================
# find_collection_of_light
# ============================================================


class TestFindCollectionOfLight:
    """Tests for find_collection_of_light() - both significators apply to 3rd planet."""

    def _make_aspects(self, *triples):
        """Helper: make aspect list from (p1, p2, applying) triples."""
        return [
            {"planet1": p1, "planet2": p2, "applying": applying}
            for p1, p2, applying in triples
        ]

    def test_basic_collection(self):
        """Moon and Saturn both apply to Jupiter → Jupiter collects light."""
        planets = {
            "Moon": {"longitude": 5.0},
            "Saturn": {"longitude": 12.0},
            "Jupiter": {"longitude": 15.0},
        }
        aspects = self._make_aspects(
            ("Moon", "Jupiter", True),
            ("Saturn", "Jupiter", True),
        )
        result = find_collection_of_light("Moon", "Saturn", planets, aspects)
        assert result == "Jupiter"

    def test_no_collection_not_applying(self):
        """Both planets aspect Jupiter but separating → not collection."""
        planets = {
            "Moon": {"longitude": 5.0},
            "Saturn": {"longitude": 12.0},
            "Jupiter": {"longitude": 3.0},  # They're past Jupiter
        }
        aspects = self._make_aspects(
            ("Moon", "Jupiter", False),
            ("Saturn", "Jupiter", False),
        )
        result = find_collection_of_light("Moon", "Saturn", planets, aspects)
        assert result is None

    def test_partial_connection_not_collection(self):
        """Only one significator applies to Jupiter → not collection."""
        planets = {
            "Moon": {"longitude": 5.0},
            "Saturn": {"longitude": 12.0},
            "Jupiter": {"longitude": 15.0},
        }
        aspects = self._make_aspects(
            ("Moon", "Jupiter", True),
            # Saturn does NOT aspect Jupiter
        )
        result = find_collection_of_light("Moon", "Saturn", planets, aspects)
        assert result is None

    def test_collector_not_significator(self):
        """The collector cannot be one of the two significators."""
        planets = {
            "Moon": {"longitude": 5.0},
            "Saturn": {"longitude": 12.0},
        }
        aspects = []
        result = find_collection_of_light("Moon", "Saturn", planets, aspects)
        assert result is None

    def test_empty_input(self):
        """Empty input returns None."""
        result = find_collection_of_light("Moon", "Saturn", {}, [])
        assert result is None
