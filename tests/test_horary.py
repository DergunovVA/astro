"""
Tests for Horary Astrology Analyzer

Task 4.2.3: Test horary question analysis methods
"""

import pytest
from src.modules.horary import HoraryAnalyzer


class TestHoraryYesNoAnalysis:
    """Test Yes/No question analysis"""

    def test_applying_aspect_yes(self):
        """Applying aspect between significators = YES"""
        chart_data = {
            "planets": {
                "Mars": {
                    "Sign": "Aries",
                    "House": 1,
                    "longitude": 15.0,
                    "Speed": 0.5,
                    "Retrograde": False,
                },
                "Venus": {
                    "Sign": "Leo",
                    "House": 7,
                    "longitude": 135.0,
                    "Speed": 1.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 10.0},  # Mars rules 1st
                "House7": {"Sign": "Libra", "Degree": 10.0},  # Venus rules 7th
            },
            "aspects": [
                {
                    "planet1": "Mars",
                    "planet2": "Venus",
                    "type": "trine",
                    "orb": 0.0,  # Exact
                    "category": "major",
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=7)

        assert result["answer"] == "yes"
        assert result["confidence"] > 0.5
        assert "Applying trine aspect" in str(result["factors"])
        assert result["querent_planet"] == "Mars"
        assert result["quesited_planet"] == "Venus"

    def test_separating_aspect_no(self):
        """Separating aspect = NO (opportunity passed)"""
        chart_data = {
            "planets": {
                "Sun": {
                    "Sign": "Leo",
                    "House": 1,
                    "longitude": 120.0,
                    "Speed": 1.0,
                    "Retrograde": False,
                },
                "Moon": {
                    "Sign": "Cancer",
                    "House": 10,
                    "longitude": 100.0,
                    "Speed": 13.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Leo", "Degree": 0.0},
                "House10": {"Sign": "Cancer", "Degree": 0.0},  # Moon rules 10th
            },
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "type": "sextile",
                    "orb": 2.0,
                    "category": "major",
                }
            ],
        }

        # Mock: make aspect separating by setting Moon retrograde
        chart_data["planets"]["Moon"]["Retrograde"] = True

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=10)

        assert result["answer"] == "no"
        assert "Separating" in str(result["factors"])

    def test_mutual_reception_yes(self):
        """Mutual reception can indicate YES even without aspect"""
        chart_data = {
            "planets": {
                "Venus": {
                    "Sign": "Aries",
                    "House": 1,
                    "longitude": 15.0,  # Venus in Mars' sign
                    "Speed": 1.0,
                },
                "Mars": {
                    "Sign": "Taurus",
                    "House": 7,
                    "longitude": 45.0,  # Mars in Venus' sign
                    "Speed": 0.5,
                },
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House7": {"Sign": "Libra", "Degree": 0.0},
            },
            "aspects": [],  # No direct aspect
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=7)

        assert result["answer"] == "yes"
        assert "Mutual reception" in str(result["factors"])
        assert result["confidence"] > 0.3

    def test_no_connection_no(self):
        """No aspect and no reception = NO"""
        chart_data = {
            "planets": {
                "Sun": {
                    "Sign": "Leo",
                    "House": 1,
                    "longitude": 120.0,
                },
                "Saturn": {
                    "Sign": "Capricorn",
                    "House": 10,
                    "longitude": 280.0,
                },
            },
            "houses": {
                "House1": {"Sign": "Leo", "Degree": 0.0},
                "House10": {"Sign": "Capricorn", "Degree": 0.0},
            },
            "aspects": [],  # No aspect
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=10)

        assert result["answer"] == "no"
        assert "No aspect" in str(result["factors"])
        assert result["confidence"] < 0.5

    def test_translation_of_light(self):
        """Translation of light can connect significators"""
        chart_data = {
            "planets": {
                "Mars": {"Sign": "Aries", "House": 1, "longitude": 10.0},
                "Venus": {"Sign": "Libra", "House": 7, "longitude": 190.0},
                "Mercury": {
                    "Sign": "Cancer",
                    "House": 4,
                    "longitude": 100.0,
                },  # Translator
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House7": {"Sign": "Libra", "Degree": 0.0},
            },
            "aspects": [
                # No direct aspect between Mars-Venus
                # Mercury aspects both
                {
                    "planet1": "Mercury",
                    "planet2": "Mars",
                    "type": "square",
                    "orb": 0.0,
                },
                {
                    "planet1": "Mercury",
                    "planet2": "Venus",
                    "type": "square",
                    "orb": 0.0,
                },
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=7)

        assert "Translation of light" in str(result["factors"])
        assert result["answer"] == "yes"

    def test_collection_of_light(self):
        """Collection of light (both apply to 3rd planet)"""
        chart_data = {
            "planets": {
                "Mars": {"Sign": "Aries", "House": 1, "longitude": 10.0, "Speed": 0.5},
                "Venus": {
                    "Sign": "Libra",
                    "House": 7,
                    "longitude": 190.0,
                    "Speed": 1.0,
                },
                "Jupiter": {
                    "Sign": "Cancer",
                    "House": 4,
                    "longitude": 100.0,
                    "Speed": 0.1,
                },  # Collector
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House7": {"Sign": "Libra", "Degree": 0.0},
            },
            "aspects": [
                # Both Mars and Venus apply to Jupiter
                {
                    "planet1": "Mars",
                    "planet2": "Jupiter",
                    "type": "square",
                    "orb": 0.5,
                },
                {
                    "planet1": "Venus",
                    "planet2": "Jupiter",
                    "type": "square",
                    "orb": 0.5,
                },
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=7)

        assert "Collection of light" in str(result["factors"])


class TestHoraryTiming:
    """Test timing predictions"""

    def test_angular_house_fast_timing(self):
        """Angular houses = days (fast)"""
        chart_data = {
            "planets": {
                "Sun": {
                    "Sign": "Leo",
                    "House": 1,  # Angular
                    "longitude": 120.0,
                    "Speed": 1.0,
                },
                "Moon": {
                    "Sign": "Cancer",
                    "House": 10,
                    "longitude": 100.0,
                    "Speed": 13.0,
                },
            },
            "houses": {
                "House1": {"Sign": "Leo", "Degree": 0.0},
                "House10": {"Sign": "Cancer", "Degree": 0.0},  # Moon rules 10th
            },
            "aspects": [
                {"planet1": "Sun", "planet2": "Moon", "type": "sextile", "orb": 5.0}
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=10)

        assert result["time_units"] == "days"
        assert "Angular house" in str(result["factors"])
        assert result["time_value"] == 5.0

    def test_succedent_house_moderate_timing(self):
        """Succedent houses = weeks (moderate)"""
        chart_data = {
            "planets": {
                "Venus": {
                    "Sign": "Taurus",
                    "House": 2,  # Succedent
                    "longitude": 45.0,
                    "Retrograde": False,
                },
                "Pluto": {
                    "Sign": "Scorpio",
                    "House": 8,
                    "longitude": 225.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Taurus", "Degree": 0.0},  # Venus rules
                "House2": {"Sign": "Taurus", "Degree": 0.0},
                "House8": {"Sign": "Scorpio", "Degree": 0.0},
            },
            "aspects": [
                {
                    "planet1": "Venus",
                    "planet2": "Pluto",
                    "type": "opposition",
                    "orb": 3.0,
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=8)

        assert result["time_units"] == "weeks"
        assert "Succedent house" in str(result["factors"])

    def test_cadent_house_slow_timing(self):
        """Cadent houses = months (slow)"""
        chart_data = {
            "planets": {
                "Mercury": {
                    "Sign": "Gemini",
                    "House": 3,  # Cadent
                    "longitude": 75.0,
                    "Retrograde": False,
                },
                "Neptune": {
                    "Sign": "Pisces",
                    "House": 9,
                    "longitude": 345.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Gemini", "Degree": 0.0},  # Mercury rules
                "House3": {"Sign": "Gemini", "Degree": 0.0},
                "House9": {"Sign": "Pisces", "Degree": 0.0},  # Neptune rules (modern)
            },
            "aspects": [
                {
                    "planet1": "Mercury",
                    "planet2": "Neptune",
                    "type": "square",
                    "orb": 2.0,
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=9)

        assert result["time_units"] == "months"
        assert "Cadent house" in str(result["factors"])

    def test_cardinal_sign_speeds_up(self):
        """Cardinal signs speed things up"""
        chart_data = {
            "planets": {
                "Mars": {
                    "Sign": "Aries",  # Cardinal
                    "House": 1,
                    "longitude": 15.0,
                },
                "Venus": {"Sign": "Libra", "House": 7, "longitude": 195.0},
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House7": {"Sign": "Libra", "Degree": 0.0},
            },
            "aspects": [
                {
                    "planet1": "Mars",
                    "planet2": "Venus",
                    "type": "opposition",
                    "orb": 0.0,
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=7)

        assert "Cardinal sign" in str(result["factors"])

    def test_fixed_sign_delays(self):
        """Fixed signs delay/stabilize"""
        chart_data = {
            "planets": {
                "Sun": {
                    "Sign": "Leo",
                    "House": 1,
                    "longitude": 120.0,
                    "Retrograde": False,
                },  # Fixed
                "Uranus": {
                    "Sign": "Aquarius",
                    "House": 7,
                    "longitude": 300.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Leo", "Degree": 0.0},
                "House7": {"Sign": "Aquarius", "Degree": 0.0},
            },
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Uranus",
                    "type": "opposition",
                    "orb": 0.0,
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=7)

        assert "Fixed sign" in str(result["factors"])

    def test_no_applying_aspect_uncertain_timing(self):
        """No applying aspect = uncertain timing"""
        chart_data = {
            "planets": {
                "Mars": {"Sign": "Aries", "House": 1, "longitude": 15.0},
                "Venus": {"Sign": "Libra", "House": 7, "longitude": 195.0},
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House7": {"Sign": "Libra", "Degree": 0.0},
            },
            "aspects": [],  # No aspect
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("when", house_number=7)

        assert result["timing"] == "unknown"
        assert "No applying aspect" in str(result["factors"])


class TestLostObjectAnalysis:
    """Test lost object location analysis"""

    def test_lost_object_likely_found(self):
        """2nd house ruler strong = likely found"""
        chart_data = {
            "planets": {
                "Venus": {
                    "Sign": "Taurus",  # Domicile = strong
                    "House": 1,
                    "longitude": 45.0,
                    "Speed": 1.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House2": {"Sign": "Taurus", "Degree": 0.0},  # Venus rules 2nd
            },
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("lost_object")

        assert result["likely_found"] is True
        assert "Sign: Taurus" in result["location_hints"]
        assert "House: 1" in result["location_hints"]
        assert "likely found" in str(result["factors"])

    def test_lost_object_unlikely_found(self):
        """2nd house ruler weak = unlikely found"""
        chart_data = {
            "planets": {
                "Venus": {
                    "Sign": "Scorpio",  # Detriment = weak
                    "House": 12,  # Cadent, hidden
                    "longitude": 225.0,
                    "Speed": 0.2,
                    "Retrograde": True,
                },
            },
            "houses": {
                "House1": {"Sign": "Aries", "Degree": 0.0},
                "House2": {"Sign": "Taurus", "Degree": 0.0},  # Venus rules 2nd
            },
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("lost_object")

        assert result["likely_found"] is False
        assert "may not be found" in str(result["factors"])


class TestSignificators:
    """Test significator identification"""

    def test_querent_is_first_house_ruler(self):
        """Querent = 1st house ruler"""
        chart_data = {
            "planets": {"Mars": {"Sign": "Aries"}},
            "houses": {"House1": {"Sign": "Aries", "Degree": 0.0}},
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        querent = analyzer._get_querent_significator()

        assert querent == "Mars"  # Mars rules Aries

    def test_quesited_is_house_ruler(self):
        """Quesited = specified house ruler"""
        chart_data = {
            "planets": {"Venus": {"Sign": "Libra"}},
            "houses": {"House7": {"Sign": "Libra", "Degree": 0.0}},
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        quesited = analyzer._get_quesited_significator(7)

        assert quesited == "Venus"  # Venus rules Libra

    def test_house_ruler_mercury(self):
        """Mercury rules Gemini and Virgo"""
        chart_data = {
            "planets": {},
            "houses": {"House3": {"Sign": "Gemini"}},
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        ruler = analyzer._get_house_ruler(3)

        assert ruler == "Mercury"


class TestDignityIntegration:
    """Test dignity calculation integration"""

    def test_total_dignity_calculation(self):
        """Calculate total dignity (essential + accidental)"""
        chart_data = {
            "planets": {
                "Sun": {
                    "Sign": "Leo",  # Domicile
                    "House": 1,  # Angular
                    "longitude": 120.0,
                    "Speed": 1.0,
                    "Retrograde": False,
                }
            },
            "houses": {
                "House1": {"Sign": "Leo", "Degree": 0.0},
            },
            "aspects": [],
        }

        analyzer = HoraryAnalyzer(chart_data)
        dignity = analyzer._get_planet_total_dignity("Sun")

        assert dignity is not None
        assert dignity["total_score"] > 5  # Strong position
        assert dignity["overall_strength"] in ["Very Strong", "Extremely Powerful"]

    def test_weak_dignity_affects_confidence(self):
        """Weak dignity can affect analysis but applying aspect still gives YES"""
        chart_data = {
            "planets": {
                "Uranus": {
                    "Sign": "Aquarius",  # Domicile (modern ruler)
                    "House": 1,  # Angular
                    "longitude": 300.0,
                    "Speed": 0.05,
                    "Retrograde": False,
                },
                "Moon": {
                    "Sign": "Cancer",  # Domicile (strong)
                    "House": 10,
                    "longitude": 100.0,
                    "Speed": 13.0,
                    "Retrograde": False,
                },
            },
            "houses": {
                "House1": {"Sign": "Aquarius", "Degree": 0.0},  # Uranus rules (modern)
                "House10": {"Sign": "Cancer", "Degree": 0.0},  # Moon rules
            },
            "aspects": [
                {"planet1": "Uranus", "planet2": "Moon", "type": "trine", "orb": 2.0}
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=10)

        # Should be YES (applying trine aspect)
        assert result["answer"] == "yes"
        assert result["confidence"] > 0.5
        assert "Applying trine" in str(result["factors"])


class TestEdgeCases:
    """Test edge cases"""

    def test_missing_significator(self):
        """Missing house data = cannot identify significator"""
        chart_data = {"planets": {}, "houses": {}, "aspects": []}

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("will_it_happen", house_number=7)

        assert result["answer"] == "uncertain"
        assert "Cannot identify significators" in result["factors"]

    def test_unknown_question_type(self):
        """Unknown question type returns error"""
        chart_data = {"planets": {}, "houses": {}, "aspects": []}

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("unknown_type")

        assert "error" in result
        assert "Unknown question type" in result["error"]

    def test_relationship_question_uses_7th_house(self):
        """Relationship question defaults to 7th house"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Libra", "House": 7, "longitude": 195.0},
                "Mars": {"Sign": "Aries", "House": 1, "longitude": 15.0},
            },
            "houses": {
                "House1": {"Sign": "Aries"},
                "House7": {"Sign": "Libra"},
            },
            "aspects": [
                {
                    "planet1": "Venus",
                    "planet2": "Mars",
                    "type": "opposition",
                    "orb": 0.0,
                }
            ],
        }

        analyzer = HoraryAnalyzer(chart_data)
        result = analyzer.analyze_question("relationship")

        assert result["quesited_planet"] == "Venus"  # 7th house ruler


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
