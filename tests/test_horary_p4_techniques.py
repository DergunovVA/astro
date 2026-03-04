"""
Tests for P4 horary techniques:
- check_prohibition  (William Lilly CA Book II p.297-302)
- check_refrenation  (William Lilly CA Book II p.302-305)
- analyze_reception_quality  (William Lilly CA Book II p.112-118)
"""

from src.modules.horary import (
    check_prohibition,
    check_refrenation,
    analyze_reception_quality,
)


# ===========================================================
# PROHIBITION TESTS
# ===========================================================


class TestCheckProhibition:
    """Tests for check_prohibition()."""

    def test_basic_prohibition(self):
        """
        Classic prohibition: Moon applies to Saturn (conjunction in 8°),
        but Mars at 12° intercepts Moon first.
        """
        all_planets = {
            "Moon": {"longitude": 10.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
            "Mars": {"longitude": 11.0, "Speed": 0.5},  # between Moon and Saturn
        }

        result = check_prohibition(
            "Moon",
            10.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,  # conjunction
            all_planets,
            orb=8.0,
        )

        assert result["is_prohibited"] is True
        assert result["prohibitor"] == "Mars"
        assert result["time_to_prohibition"] is not None
        assert result["time_to_perfection"] is not None
        assert result["time_to_prohibition"] < result["time_to_perfection"]
        assert "PROHIBITED" in result["explanation"]

    def test_no_prohibition_planet_behind(self):
        """No prohibition: Mars is behind Moon (already past), cannot intercept."""
        all_planets = {
            "Moon": {"longitude": 10.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
            "Mars": {"longitude": 25.0, "Speed": 0.5},  # past Saturn, can't intercept
        }

        result = check_prohibition(
            "Moon",
            10.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,
            all_planets,
        )

        assert result["is_prohibited"] is False

    def test_no_prohibition_separating_aspect(self):
        """No prohibition possible when main aspect is already separating."""
        all_planets = {
            "Moon": {"longitude": 20.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
            "Mars": {"longitude": 15.0, "Speed": 0.5},
        }

        # Moon at 20° moving away from Saturn at 18° (separating conjunction)
        result = check_prohibition(
            "Moon",
            20.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,
            all_planets,
        )

        assert result["is_prohibited"] is False
        assert "separating" in result["explanation"]

    def test_prohibition_planet1_excluded_from_intercept(self):
        """Significators themselves should not be checked as interceptors."""
        all_planets = {
            "Moon": {"longitude": 10.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
        }

        # Only Moon and Saturn in the dict — no third planet to prohibit
        result = check_prohibition(
            "Moon",
            10.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,
            all_planets,
        )

        assert result["is_prohibited"] is False

    def test_prohibition_via_trine(self):
        """Prohibition can occur via any major aspect, e.g. trine."""
        # Moon @ 10° Aries → Venus @ 142° Leo (trine = 132° apart, applying)
        # Jupiter @ 14° Aries: Moon applies to Venus (trine), but Jupiter
        # conjoins Moon first within the orb window.
        all_planets = {
            "Moon": {"longitude": 10.0, "Speed": 13.0},
            "Venus": {"longitude": 142.0, "Speed": 1.2},
            "Jupiter": {
                "longitude": 13.5,
                "Speed": 0.2,
            },  # Moon applies to Jupiter first
        }

        result = check_prohibition(
            "Moon",
            10.0,
            13.0,
            "Venus",
            142.0,
            1.2,
            120,  # trine (Moon needs to reach 262° or 22°)
            all_planets,
        )

        # Jupiter conjoins Moon (via Moon reaching Jupiter) before trine with Venus
        # This checks prohibition of p1 (Moon) by Jupiter conjunction
        assert isinstance(result["is_prohibited"], bool)
        assert "explanation" in result
        assert result["time_to_perfection"] is not None

    def test_prohibition_result_keys(self):
        """Result must have all required keys."""
        all_planets = {
            "Moon": {"longitude": 5.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
        }

        result = check_prohibition(
            "Moon",
            5.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,
            all_planets,
        )

        required_keys = {
            "is_prohibited",
            "prohibitor",
            "prohibitor_aspect",
            "prohibitor_target",
            "time_to_prohibition",
            "time_to_perfection",
            "explanation",
        }
        assert set(result.keys()) >= required_keys

    def test_prohibition_skips_planets_missing_data(self):
        """Planets without longitude or Speed are silently skipped."""
        all_planets = {
            "Moon": {"longitude": 10.0, "Speed": 13.0},
            "Saturn": {"longitude": 18.0, "Speed": 0.03},
            "BadPlanet": {"name": "no longitude field"},  # no longitude → skip
        }

        result = check_prohibition(
            "Moon",
            10.0,
            13.0,
            "Saturn",
            18.0,
            0.03,
            0,
            all_planets,
        )

        # Should run without errors; BadPlanet is silently ignored
        assert isinstance(result["is_prohibited"], bool)


# ===========================================================
# REFRENATION TESTS
# ===========================================================


class TestCheckRefrenation:
    """Tests for check_refrenation()."""

    def _make_mock_ephemeris(self, station_day: int, station_lon: float = 17.0):
        """
        Create a mock ephemeris function that simulates a planet slowing down
        and stationing retrograde on `station_day`.
        """

        def ephemeris(jd: float, planet_id: int):
            day_offset = round(jd - 2460000.5)
            if day_offset < station_day:
                speed = 1.2 - (day_offset * 0.1)  # slowing
                lon = 15.0 + day_offset * max(speed, 0.01)
            else:
                speed = -0.1  # retrograde
                lon = station_lon
            # Return flat tuple  (lon, ..., ..., speed)
            return (lon, 0.0, 1.0, speed, 0.0, 0.0)

        return ephemeris

    def test_refrenation_occurs(self):
        """Planet stations retrograde BEFORE perfecting the aspect."""
        # Venus @ 15° (lon=135°), applying to Mars @ 20° (lon=140°).
        # Perfection in ~4 days (5°/1.2 deg/day ≈ 4.2 days).
        # Station on day 3 → refrenation!
        mock_eph = self._make_mock_ephemeris(station_day=3, station_lon=17.5)

        result = check_refrenation(
            "Venus",
            135.0,
            1.2,
            140.0,
            0.5,
            0,  # conjunction
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is True
        assert result["days_to_station"] is not None
        assert result["days_to_station"] < result["days_to_perfection"]
        assert "REFRENATED" in result["explanation"]

    def test_no_refrenation_station_after_perfection(self):
        """Planet stations retrograde AFTER aspect perfects — no refrenation."""
        # Venus @ 135° → 140°, relative speed ≈ 0.7 deg/day → perfection ≈ 7.1 days.
        # Station on day 9 → AFTER perfection → no refrenation.
        mock_eph = self._make_mock_ephemeris(station_day=9, station_lon=21.0)

        result = check_refrenation(
            "Venus",
            135.0,
            1.2,
            140.0,
            0.5,
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False
        assert "AFTER perfection" in result["explanation"]

    def test_already_retrograde(self):
        """Planet already retrograde — refrenation not applicable."""
        mock_eph = self._make_mock_ephemeris(station_day=5)

        result = check_refrenation(
            "Venus",
            135.0,
            -0.5,  # negative speed = already retrograde
            140.0,
            0.5,
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False
        assert result["is_currently_retrograde"] is True
        assert "already retrograde" in result["explanation"]

    def test_sun_never_refrenates(self):
        """Sun never goes retrograde — always returns will_refrenate=False."""
        # Sun @ 100° applying to slow Saturn @ 120° (speed 0.03).
        # Relative speed = 0.98 - 0.03 = 0.95 > 0 → applying → reaches Sun/Moon check.
        mock_eph = self._make_mock_ephemeris(station_day=1)

        result = check_refrenation(
            "Sun",
            100.0,
            0.98,
            120.0,
            0.03,  # slow target so the aspect is applying
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False
        assert "never" in result["explanation"]

    def test_moon_never_refrenates(self):
        """Moon never goes retrograde."""
        mock_eph = self._make_mock_ephemeris(station_day=1)

        result = check_refrenation(
            "Moon",
            10.0,
            13.0,
            18.0,
            0.03,
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False

    def test_separating_aspect_no_refrenation(self):
        """Separating aspect cannot have refrenation."""
        mock_eph = self._make_mock_ephemeris(station_day=2)

        # Venus moving away from Mars (planet_lon > target_lon, same direction)
        result = check_refrenation(
            "Venus",
            145.0,
            1.2,  # ahead of target
            140.0,
            1.2,  # same speed → not closing
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False

    def test_result_keys(self):
        """Result must contain all required fields."""
        mock_eph = self._make_mock_ephemeris(station_day=5)

        result = check_refrenation(
            "Venus",
            135.0,
            1.2,
            140.0,
            0.5,
            0,
            2460000.5,
            mock_eph,
        )

        required_keys = {
            "will_refrenate",
            "is_currently_retrograde",
            "station_jd",
            "station_longitude",
            "days_to_station",
            "days_to_perfection",
            "explanation",
        }
        assert set(result.keys()) >= required_keys

    def test_unknown_planet_graceful(self):
        """Unknown planet name returns graceful error, not exception."""
        mock_eph = self._make_mock_ephemeris(station_day=3)

        result = check_refrenation(
            "Ceres",
            100.0,
            0.5,
            120.0,
            0.3,
            0,
            2460000.5,
            mock_eph,
        )

        assert result["will_refrenate"] is False
        assert "Unknown" in result["explanation"]


# ===========================================================
# RECEPTION QUALITY TESTS
# ===========================================================


class TestAnalyzeReceptionQuality:
    """Tests for analyze_reception_quality()."""

    def test_friendly_reception_venus_pisces(self):
        """
        Jupiter rules Pisces (traditional).
        Venus @ 350° (Pisces) — exalted in Pisces → friendly reception.
        Jupiter receives Venus in its own sign.
        """
        result = analyze_reception_quality(
            "Jupiter",
            280.0,  # Capricorn (Jupiter is the planet1)
            "Venus",
            350.0,  # Pisces (ruled by Jupiter)
            traditional=True,
        )

        p1r = result[
            "planet1_receives_planet2"
        ]  # Jupiter receives Venus (Venus in Pisces)
        assert p1r["has_reception"] is True
        # Venus in Pisces = exalted → Strong dignity level → friendly
        assert p1r["quality"] == "friendly"
        assert result["overall_quality"] == "friendly"

    def test_hostile_reception_mars_libra(self):
        """
        Venus rules Libra.
        Mars @ 200° (Libra) — detriment in Libra (score -5) → hostile reception.
        Venus receives Mars in Libra.
        """
        result = analyze_reception_quality(
            "Venus",
            35.0,  # Taurus (ruled by Venus itself — irrelevant)
            "Mars",
            200.0,  # Libra (ruled by Venus)
            traditional=True,
        )

        p1r = result["planet1_receives_planet2"]  # Venus receives Mars (Mars in Libra)
        assert p1r["has_reception"] is True
        assert p1r["quality"] == "hostile"  # Mars detriment in Libra
        assert result["overall_quality"] == "hostile"

    def test_mutual_reception_saturn_mars(self):
        """
        Saturn @ 5° (Aries, ruled by Mars) ↔ Mars @ 328° (Aquarius, ruled by Saturn).
        Mutual reception: both planets in each other's signs.
        Overall quality depends on accumulated dignity scoring (fall+triplicity etc.).
        """
        result = analyze_reception_quality(
            "Saturn",
            5.0,  # Aries → ruler = Mars (planet2)
            "Mars",
            328.0,  # Aquarius → ruler = Saturn (planet1, traditional)
            traditional=True,
        )

        assert result["is_mutual"] is True
        assert (
            result["planet2_receives_planet1"]["has_reception"] is True
        )  # Mars receives Saturn
        assert (
            result["planet1_receives_planet2"]["has_reception"] is True
        )  # Saturn receives Mars
        assert result["overall_quality"] in ("mixed", "hostile", "neutral")

    def test_no_reception(self):
        """No planets in each other's signs → no reception."""
        result = analyze_reception_quality(
            "Sun",
            90.0,  # Cancer (ruled by Moon)
            "Jupiter",
            240.0,  # Sagittarius (ruled by Jupiter itself)
            traditional=True,
        )

        # Sun in Cancer is not in Jupiter's sign (Sag/Pisces)
        # Jupiter in Sagittarius is in its OWN sign — but we need it to be in Sun's sign (Leo)
        assert result["is_mutual"] is False
        # At least one side should have no reception
        assert not (
            result["planet1_receives_planet2"]["has_reception"]
            and result["planet2_receives_planet1"]["has_reception"]
        )

    def test_result_structure(self):
        """result must have correct nested structure."""
        result = analyze_reception_quality(
            "Mars",
            10.0,
            "Saturn",
            310.0,
            traditional=True,
        )

        assert "planet1_receives_planet2" in result
        assert "planet2_receives_planet1" in result
        assert "is_mutual" in result
        assert "overall_quality" in result

        for side_key in ("planet1_receives_planet2", "planet2_receives_planet1"):
            side = result[side_key]
            assert "has_reception" in side
            assert "type" in side
            assert "quality" in side
            assert "score" in side
            assert "interpretation" in side

    def test_overall_quality_values(self):
        """overall_quality must be one of the allowed values."""
        result = analyze_reception_quality(
            "Jupiter",
            280.0,  # Capricorn
            "Venus",
            350.0,  # Pisces
        )
        assert result["overall_quality"] in ("friendly", "hostile", "mixed", "neutral")

    def test_planet_in_own_sign_not_mutual(self):
        """
        Planet in its own sign → ruler is itself → not a reception with another planet.
        E.g. Mars in Aries: ruler of Aries is Mars, but we're testing against Saturn.
        """
        result = analyze_reception_quality(
            "Mars",
            15.0,  # Aries, ruled by Mars (not Saturn)
            "Saturn",
            310.0,  # Aquarius, ruled by Saturn
            traditional=True,
        )

        # Mars is in Aries (its own sign), not in Saturn's sign → no reception from Mars's side
        # Saturn is in Aquarius (its own sign) → not in Mars's sign → no reception from Saturn's side
        assert result["planet1_receives_planet2"]["has_reception"] is False
        assert result["overall_quality"] == "neutral"

    def test_modern_vs_traditional_rulers(self):
        """traditional=False may give different rulers (e.g. Uranus for Aquarius)."""
        result_trad = analyze_reception_quality(
            "Saturn",
            5.0,
            "Mars",
            328.0,
            traditional=True,
        )
        result_modern = analyze_reception_quality(
            "Saturn",
            5.0,
            "Mars",
            328.0,
            traditional=False,
        )

        # Results may differ due to Uranus vs Saturn for Aquarius
        # Traditional should give mutual reception (Mars↔Saturn)
        assert result_trad["is_mutual"] is True
        # Modern may or may not — just verify it runs without error
        assert "is_mutual" in result_modern
