"""
Tests for Minor Essential Dignities (Triplicities, Terms, Decans).

Testing the three lesser dignities in traditional astrology:
1. Triplicities - elemental rulers by day/night
2. Egyptian Terms - degree boundaries with planetary rulers
3. Faces/Decans - 10-degree divisions using Chaldean order
"""

from src.core.minor_dignities import (
    CHALDEAN_ORDER,
    DECANS,
    EGYPTIAN_TERMS,
    TRIPLICITIES,
    calculate_minor_dignities,
    get_all_decans,
    get_all_terms,
    get_decan_ruler,
    get_term_ruler,
    get_triplicity_ruler,
    get_triplicity_rulers,
)


# ============================================================================
# TRIPLICITY TESTS
# ============================================================================


class TestTriplicityRulers:
    """Test triplicity (elemental) rulers."""

    def test_fire_triplicity_aries(self):
        """Test Aries (Fire) triplicity rulers."""
        rulers = get_triplicity_rulers("Aries")
        assert rulers is not None
        assert rulers["element"] == "Fire"
        assert rulers["day_ruler"] == "Sun"
        assert rulers["night_ruler"] == "Jupiter"
        assert rulers["participating"] == "Saturn"

    def test_earth_triplicity_taurus(self):
        """Test Taurus (Earth) triplicity rulers."""
        rulers = get_triplicity_rulers("Taurus")
        assert rulers is not None
        assert rulers["element"] == "Earth"
        assert rulers["day_ruler"] == "Venus"
        assert rulers["night_ruler"] == "Moon"
        assert rulers["participating"] == "Mars"

    def test_air_triplicity_gemini(self):
        """Test Gemini (Air) triplicity rulers."""
        rulers = get_triplicity_rulers("Gemini")
        assert rulers is not None
        assert rulers["element"] == "Air"
        assert rulers["day_ruler"] == "Saturn"
        assert rulers["night_ruler"] == "Mercury"
        assert rulers["participating"] == "Jupiter"

    def test_water_triplicity_cancer(self):
        """Test Cancer (Water) triplicity rulers."""
        rulers = get_triplicity_rulers("Cancer")
        assert rulers is not None
        assert rulers["element"] == "Water"
        assert rulers["day_ruler"] == "Venus"
        assert rulers["night_ruler"] == "Mars"
        assert rulers["participating"] == "Moon"

    def test_all_fire_signs_same_triplicity(self):
        """Test all fire signs have same triplicity rulers."""
        aries = get_triplicity_rulers("Aries")
        leo = get_triplicity_rulers("Leo")
        sag = get_triplicity_rulers("Sagittarius")

        assert aries is not None
        assert aries == leo == sag
        assert aries["element"] == "Fire"

    def test_invalid_sign_returns_none(self):
        """Test invalid sign returns None."""
        assert get_triplicity_rulers("InvalidSign") is None
        assert get_triplicity_rulers("") is None

    def test_day_chart_ruler_selection(self):
        """Test day chart selects day ruler."""
        ruler = get_triplicity_ruler("Leo", is_day_chart=True)
        assert ruler == "Sun"  # Leo is Fire, day ruler is Sun

    def test_night_chart_ruler_selection(self):
        """Test night chart selects night ruler."""
        ruler = get_triplicity_ruler("Leo", is_day_chart=False)
        assert ruler == "Jupiter"  # Leo is Fire, night ruler is Jupiter


# ============================================================================
# EGYPTIAN TERMS TESTS
# ============================================================================


class TestEgyptianTerms:
    """Test Egyptian Terms (Bounds)."""

    def test_aries_first_term_jupiter(self):
        """Test Aries 0-6 degrees ruled by Jupiter."""
        assert get_term_ruler("Aries", 0.0) == "Jupiter"
        assert get_term_ruler("Aries", 3.5) == "Jupiter"
        assert get_term_ruler("Aries", 5.99) == "Jupiter"

    def test_aries_second_term_venus(self):
        """Test Aries 6-14 degrees ruled by Venus."""
        assert get_term_ruler("Aries", 6.0) == "Venus"
        assert get_term_ruler("Aries", 10.0) == "Venus"
        assert get_term_ruler("Aries", 13.99) == "Venus"

    def test_aries_all_terms_boundaries(self):
        """Test all term boundaries in Aries."""
        assert get_term_ruler("Aries", 0) == "Jupiter"    # 0-6
        assert get_term_ruler("Aries", 6) == "Venus"      # 6-14
        assert get_term_ruler("Aries", 14) == "Mercury"   # 14-21
        assert get_term_ruler("Aries", 21) == "Mars"      # 21-26
        assert get_term_ruler("Aries", 26) == "Saturn"    # 26-30

    def test_taurus_terms(self):
        """Test Taurus term rulers."""
        assert get_term_ruler("Taurus", 0) == "Venus"     # 0-8
        assert get_term_ruler("Taurus", 8) == "Mercury"   # 8-15
        assert get_term_ruler("Taurus", 15) == "Jupiter"  # 15-22
        assert get_term_ruler("Taurus", 22) == "Saturn"   # 22-26
        assert get_term_ruler("Taurus", 26) == "Mars"     # 26-30

    def test_all_signs_have_five_terms(self):
        """Test all 12 signs have exactly 5 terms."""
        for sign in EGYPTIAN_TERMS:
            terms = get_all_terms(sign)
            assert terms is not None
            assert len(terms) == 5, f"{sign} should have 5 terms"

    def test_terms_cover_full_30_degrees(self):
        """Test terms cover entire 0-30 degree range."""
        for sign in EGYPTIAN_TERMS:
            terms = get_all_terms(sign)
            assert terms is not None
            assert terms[0][0] == 0, f"{sign} first term should start at 0"
            assert terms[-1][1] == 30, f"{sign} last term should end at 30"

    def test_terms_no_gaps(self):
        """Test terms have no gaps between boundaries."""
        for sign in EGYPTIAN_TERMS:
            terms = get_all_terms(sign)
            assert terms is not None
            for i in range(len(terms) - 1):
                assert (
                    terms[i][1] == terms[i + 1][0]
                ), f"{sign} has gap between terms {i} and {i+1}"

    def test_invalid_sign_returns_none(self):
        """Test invalid sign returns None."""
        assert get_term_ruler("InvalidSign", 10.0) is None
        assert get_all_terms("InvalidSign") is None

    def test_pisces_terms_complete(self):
        """Test Pisces terms (last sign) are complete."""
        terms = get_all_terms("Pisces")
        assert terms is not None
        assert len(terms) == 5
        assert terms[0] == (0, 8, "Venus")
        assert terms[1] == (8, 14, "Jupiter")
        assert terms[2] == (14, 20, "Mercury")
        assert terms[3] == (20, 26, "Mars")
        assert terms[4] == (26, 30, "Saturn")


# ============================================================================
# DECANS/FACES TESTS
# ============================================================================


class TestDecans:
    """Test Decans (Faces) using Chaldean order."""

    def test_chaldean_order_seven_planets(self):
        """Test Chaldean order has 7 traditional planets."""
        assert len(CHALDEAN_ORDER) == 7
        assert "Mars" in CHALDEAN_ORDER
        assert "Sun" in CHALDEAN_ORDER
        assert "Venus" in CHALDEAN_ORDER
        assert "Mercury" in CHALDEAN_ORDER
        assert "Moon" in CHALDEAN_ORDER
        assert "Saturn" in CHALDEAN_ORDER
        assert "Jupiter" in CHALDEAN_ORDER

    def test_aries_first_decan_mars(self):
        """Test Aries 0-10 degrees ruled by Mars."""
        assert get_decan_ruler("Aries", 0.0) == "Mars"
        assert get_decan_ruler("Aries", 5.0) == "Mars"
        assert get_decan_ruler("Aries", 9.99) == "Mars"

    def test_aries_second_decan_sun(self):
        """Test Aries 10-20 degrees ruled by Sun."""
        assert get_decan_ruler("Aries", 10.0) == "Sun"
        assert get_decan_ruler("Aries", 15.0) == "Sun"
        assert get_decan_ruler("Aries", 19.99) == "Sun"

    def test_aries_third_decan_venus(self):
        """Test Aries 20-30 degrees ruled by Venus."""
        assert get_decan_ruler("Aries", 20.0) == "Venus"
        assert get_decan_ruler("Aries", 25.0) == "Venus"
        assert get_decan_ruler("Aries", 29.99) == "Venus"

    def test_all_signs_have_three_decans(self):
        """Test all 12 signs have exactly 3 decans."""
        for sign in DECANS:
            decans = get_all_decans(sign)
            assert decans is not None
            assert len(decans) == 3, f"{sign} should have 3 decans"

    def test_decans_are_10_degrees_each(self):
        """Test each decan is exactly 10 degrees."""
        for sign in DECANS:
            decans = get_all_decans(sign)
            assert decans is not None
            assert decans[0] == (0, 10, decans[0][2])
            assert decans[1] == (10, 20, decans[1][2])
            assert decans[2] == (20, 30, decans[2][2])

    def test_chaldean_sequence_across_signs(self):
        """Test Chaldean order continues across signs."""
        # Aries: Mars, Sun, Venus
        # Taurus: Mercury, Moon, Saturn (continuing the sequence)
        # Gemini: Jupiter, Mars, Sun (cycling back)
        assert get_decan_ruler("Aries", 0) == "Mars"
        assert get_decan_ruler("Aries", 10) == "Sun"
        assert get_decan_ruler("Aries", 20) == "Venus"

        assert get_decan_ruler("Taurus", 0) == "Mercury"
        assert get_decan_ruler("Taurus", 10) == "Moon"
        assert get_decan_ruler("Taurus", 20) == "Saturn"

        assert get_decan_ruler("Gemini", 0) == "Jupiter"
        assert get_decan_ruler("Gemini", 10) == "Mars"  # Cycle repeats
        assert get_decan_ruler("Gemini", 20) == "Sun"

    def test_invalid_sign_returns_none(self):
        """Test invalid sign returns None."""
        assert get_decan_ruler("InvalidSign", 10.0) is None
        assert get_all_decans("InvalidSign") is None

    def test_pisces_decans_complete_circle(self):
        """Test Pisces (last sign) decans complete the zodiac circle."""
        decans = get_all_decans("Pisces")
        assert decans is not None
        assert len(decans) == 3
        assert decans[0] == (0, 10, "Saturn")
        assert decans[1] == (10, 20, "Jupiter")
        assert decans[2] == (20, 30, "Mars")  # Ends with Mars (starts Aries)


# ============================================================================
# INTEGRATED MINOR DIGNITIES TESTS
# ============================================================================


class TestMinorDignitiesCalculation:
    """Test integrated minor dignity calculations."""

    def test_sun_in_aries_5_degrees_day_chart(self):
        """Test Sun at Aries 5° in day chart has triplicity dignity."""
        result = calculate_minor_dignities("Sun", "Aries", 5.0, is_day_chart=True)

        # Sun is day ruler of Fire triplicity (Aries)
        assert result["triplicity"]["has"] is True
        assert result["triplicity"]["type"] == "day_ruler"
        assert result["triplicity"]["score"] == 3

        # Jupiter rules Aries 0-6 term
        assert result["term"]["ruler"] == "Jupiter"
        assert result["term"]["has"] is False
        assert result["term"]["score"] == 0

        # Mars rules Aries 0-10 decan
        assert result["decan"]["ruler"] == "Mars"
        assert result["decan"]["has"] is False
        assert result["decan"]["score"] == 0

        assert result["total_score"] == 3

    def test_jupiter_in_aries_3_degrees_day_chart(self):
        """Test Jupiter at Aries 3° in day chart (term ruler only)."""
        result = calculate_minor_dignities("Jupiter", "Aries", 3.0, is_day_chart=True)

        # Jupiter is night ruler of Fire, so NO triplicity in day chart
        # (Participating ruler is Saturn, not Jupiter)
        assert result["triplicity"]["has"] is False
        assert result["triplicity"]["score"] == 0

        # Jupiter rules Aries 0-6 term
        assert result["term"]["has"] is True
        assert result["term"]["ruler"] == "Jupiter"
        assert result["term"]["score"] == 2

        # Mars rules Aries 0-10 decan
        assert result["decan"]["has"] is False
        assert result["decan"]["ruler"] == "Mars"

        assert result["total_score"] == 2  # Only term dignity

    def test_mars_in_aries_5_degrees_day_chart(self):
        """Test Mars at Aries 5° in day chart (decan ruler)."""
        result = calculate_minor_dignities("Mars", "Aries", 5.0, is_day_chart=True)

        # Mars is not Fire triplicity ruler
        assert result["triplicity"]["has"] is False

        # Jupiter rules Aries 0-6 term
        assert result["term"]["has"] is False

        # Mars rules Aries 0-10 decan
        assert result["decan"]["has"] is True
        assert result["decan"]["score"] == 1

        assert result["total_score"] == 1

    def test_saturn_in_leo_7_degrees_day_chart(self):
        """Test Saturn at Leo 7° in day chart (participating triplicity)."""
        result = calculate_minor_dignities("Saturn", "Leo", 7.0, is_day_chart=True)

        # Saturn is participating ruler of Fire triplicity
        assert result["triplicity"]["has"] is True
        assert result["triplicity"]["type"] == "participating"
        assert result["triplicity"]["score"] == 1

        # Check term and decan
        # Leo 7° should be in Venus term (6-13)
        assert result["term"]["ruler"] == "Venus"
        assert result["term"]["has"] is False

        # Leo 0-10 is Saturn decan
        assert result["decan"]["ruler"] == "Saturn"
        assert result["decan"]["has"] is True
        assert result["decan"]["score"] == 1

        assert result["total_score"] == 2  # 1 (triplicity participating) + 1 (decan)

    def test_venus_in_taurus_10_degrees_day_chart(self):
        """Test Venus at Taurus 10° in day chart (multiple dignities)."""
        result = calculate_minor_dignities("Venus", "Taurus", 10.0, is_day_chart=True)

        # Venus is day ruler of Earth triplicity
        assert result["triplicity"]["has"] is True
        assert result["triplicity"]["type"] == "day_ruler"
        assert result["triplicity"]["score"] == 3

        # Taurus 8-15 is Mercury term
        assert result["term"]["ruler"] == "Mercury"
        assert result["term"]["has"] is False

        # Taurus 10-20 is Moon decan
        assert result["decan"]["ruler"] == "Moon"
        assert result["decan"]["has"] is False

        assert result["total_score"] == 3

    def test_night_chart_uses_night_ruler(self):
        """Test night chart uses night ruler for triplicity."""
        # Jupiter is night ruler of Fire (Aries, Leo, Sagittarius)
        result = calculate_minor_dignities(
            "Jupiter", "Leo", 5.0, is_day_chart=False
        )

        assert result["triplicity"]["has"] is True
        assert result["triplicity"]["type"] == "night_ruler"
        assert result["triplicity"]["score"] == 3

    def test_no_dignities(self):
        """Test planet with no minor dignities."""
        # Mercury in Aries 5° (day chart) has no minor dignities
        result = calculate_minor_dignities("Mercury", "Aries", 5.0, is_day_chart=True)

        assert result["triplicity"]["has"] is False
        assert result["term"]["has"] is False
        assert result["decan"]["has"] is False
        assert result["total_score"] == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_degree_29_99(self):
        """Test degree at end of sign (29.99°)."""
        # Aries 29.99° should be in last term (Saturn 26-30)
        assert get_term_ruler("Aries", 29.99) == "Saturn"
        # And last decan (Venus 20-30)
        assert get_decan_ruler("Aries", 29.99) == "Venus"

    def test_degree_exactly_30(self):
        """Test degree exactly 30° (should wrap to 0°)."""
        # Degree 30 should wrap to 0 (next sign), so ruler of 0-10
        ruler = get_decan_ruler("Aries", 30.0)
        # Actually this will be modulo 30, so 0, which is Mars
        assert ruler == "Mars"

    def test_degree_normalization_over_30(self):
        """Test degrees over 30 are normalized."""
        # 35° should be same as 5° (35 % 30 = 5)
        assert get_term_ruler("Aries", 35.0) == get_term_ruler("Aries", 5.0)
        assert get_decan_ruler("Aries", 35.0) == get_decan_ruler("Aries", 5.0)

    def test_negative_degree(self):
        """Test negative degrees wrap correctly."""
        # -5° should wrap to 25° (-5 % 30 = 25 in Python)
        assert get_decan_ruler("Aries", -5.0) == get_decan_ruler("Aries", 25.0)

    def test_all_twelve_signs_complete(self):
        """Test all 12 zodiac signs have complete dignities."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        for sign in signs:
            # Every sign should have triplicity rulers
            assert get_triplicity_rulers(sign) is not None

            # Every sign should have 5 terms
            terms = get_all_terms(sign)
            assert terms is not None
            assert len(terms) == 5

            # Every sign should have 3 decans
            decans = get_all_decans(sign)
            assert decans is not None
            assert len(decans) == 3


# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================


class TestDataIntegrity:
    """Test data integrity of dignity tables."""

    def test_all_triplicities_have_three_rulers(self):
        """Test all triplicities have day, night, and participating rulers."""
        for element, data in TRIPLICITIES.items():
            assert "day_ruler" in data
            assert "night_ruler" in data
            assert "participating" in data
            assert len(data["signs"]) == 3  # Each element has 3 signs

    def test_all_terms_use_five_planets(self):
        """Test each sign's terms use exactly 5 different planets."""
        for sign, terms in EGYPTIAN_TERMS.items():
            planets = [planet for _, _, planet in terms]
            # Should be exactly 5 planets (one per term)
            assert len(planets) == 5
            # All should be unique
            assert len(set(planets)) == 5

    def test_decans_use_chaldean_planets_only(self):
        """Test all decans use only planets from Chaldean order."""
        chaldean_set = set(CHALDEAN_ORDER)
        for sign, decans in DECANS.items():
            for _, _, planet in decans:
                assert planet in chaldean_set, (
                    f"{sign} decan uses {planet} not in Chaldean order"
                )

    def test_thirty_six_decans_total(self):
        """Test 12 signs × 3 decans = 36 total decans."""
        total_decans = sum(len(decans) for decans in DECANS.values())
        assert total_decans == 36

    def test_sixty_terms_total(self):
        """Test 12 signs × 5 terms = 60 total terms."""
        total_terms = sum(len(terms) for terms in EGYPTIAN_TERMS.values())
        assert total_terms == 60
