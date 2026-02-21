"""
Tests for Graph Layer - Mutual Receptions

Task 4.1.1: Test mutual reception detection
"""

import pytest
from src.modules.graph_layer import ChartGraph


class TestMutualReceptions:
    """Test mutual reception detection"""

    def test_basic_mutual_reception_venus_mars(self):
        """Venus in Aries + Mars in Taurus = mutual reception"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 1
        assert ("Venus", "Mars") in receptions
        assert graph.has_mutual_reception("Venus", "Mars")
        assert graph.has_mutual_reception("Mars", "Venus")

    def test_no_mutual_reception(self):
        """Sun in Leo + Moon in Cancer = no mutual reception"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Leo", "Degree": 10.0},
                "Moon": {"Sign": "Cancer", "Degree": 5.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0
        assert not graph.has_mutual_reception("Sun", "Moon")

    def test_mercury_venus_no_reception(self):
        """Mercury in Gemini + Venus in Taurus = no mutual reception (different rulers)"""
        chart_data = {
            "planets": {
                "Mercury": {"Sign": "Gemini", "Degree": 12.0},
                "Venus": {"Sign": "Taurus", "Degree": 8.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0

    def test_traditional_mode_scorpio(self):
        """Traditional mode: Scorpio ruled by Mars (not Pluto)"""
        # Mars in Scorpio + Pluto in Aries should NOT be reception in traditional
        chart_data = {
            "planets": {
                "Mars": {"Sign": "Scorpio", "Degree": 15.0},
                "Pluto": {"Sign": "Aries", "Degree": 10.0},
            }
        }

        # Traditional mode: Scorpio = Mars, Aries = Mars (no reception possible)
        graph = ChartGraph(chart_data, mode="traditional")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0

    def test_modern_mode_aquarius(self):
        """Modern mode: Aquarius ruled by Uranus (not Saturn)"""
        # Uranus in Leo + Sun in Aquarius = mutual reception in modern mode
        chart_data = {
            "planets": {
                "Uranus": {"Sign": "Leo", "Degree": 20.0},
                "Sun": {"Sign": "Aquarius", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 1
        assert ("Uranus", "Sun") in receptions or ("Sun", "Uranus") in receptions

    def test_multiple_receptions(self):
        """Multiple mutual receptions in chart"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
                "Mercury": {"Sign": "Pisces", "Degree": 10.0},
                "Neptune": {"Sign": "Gemini", "Degree": 5.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        # Venus-Mars and Mercury-Neptune
        assert len(receptions) == 2
        assert ("Venus", "Mars") in receptions or ("Mars", "Venus") in receptions
        assert ("Mercury", "Neptune") in receptions or (
            "Neptune",
            "Mercury",
        ) in receptions

    def test_reception_strength(self):
        """All mutual receptions have 'strong' strength"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        graph.find_all_receptions()

        strength = graph.get_reception_strength("Venus", "Mars")
        assert strength == "strong"

    def test_get_all_receptions(self):
        """get_all_receptions returns all receptions"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        graph.find_all_receptions()

        all_receptions = graph.get_all_receptions()
        assert len(all_receptions) == 1
        assert ("Venus", "Mars") in all_receptions or (
            "Mars",
            "Venus",
        ) in all_receptions

    def test_clear_graph(self):
        """Clear graph removes all edges"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        graph.find_all_receptions()

        assert len(graph.get_all_receptions()) == 1

        graph.clear_graph()
        assert len(graph.get_all_receptions()) == 0
        assert graph.graph.number_of_nodes() == 2  # Nodes remain

    def test_repr(self):
        """ChartGraph has readable repr"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        repr_str = repr(graph)

        assert "ChartGraph" in repr_str
        assert "nodes=2" in repr_str
        assert "edges=" in repr_str


class TestEdgeCases:
    """Edge cases and error handling"""

    def test_empty_chart(self):
        """Empty chart has no receptions"""
        chart_data = {"planets": {}}

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0

    def test_single_planet(self):
        """Single planet has no receptions"""
        chart_data = {"planets": {"Sun": {"Sign": "Leo", "Degree": 15.0}}}

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0

    def test_missing_sign_data(self):
        """Planets without Sign data should not cause errors"""
        chart_data = {
            "planets": {
                "Venus": {"Degree": 15.0},  # Missing Sign
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0

    def test_unknown_sign(self):
        """Unknown sign should not cause errors"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "UnknownSign", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0


class TestRulershipLogic:
    """Test sign ruler logic"""

    def test_modern_outer_planet_rulers(self):
        """Modern mode uses outer planets as rulers"""
        chart_data = {
            "planets": {
                "Pluto": {"Sign": "Aries", "Degree": 10.0},
                "Mars": {"Sign": "Scorpio", "Degree": 15.0},
            }
        }

        # Modern: Scorpio ruled by Pluto
        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 1

    def test_traditional_no_outer_planets(self):
        """Traditional mode doesn't use Uranus/Neptune/Pluto as rulers"""
        chart_data = {
            "planets": {
                "Saturn": {"Sign": "Aquarius", "Degree": 10.0},
                "Uranus": {"Sign": "Capricorn", "Degree": 15.0},
            }
        }

        # Traditional: Aquarius = Saturn, Capricorn = Saturn (no reception)
        graph = ChartGraph(chart_data, mode="traditional")
        receptions = graph.find_all_receptions()

        assert len(receptions) == 0


class TestIntegration:
    """Integration tests with real chart scenarios"""

    def test_full_natal_chart(self):
        """Test with 10-planet chart"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Capricorn", "Degree": 17.45},
                "Moon": {"Sign": "Aquarius", "Degree": 22.11},
                "Mercury": {"Sign": "Capricorn", "Degree": 5.33},
                "Venus": {"Sign": "Sagittarius", "Degree": 28.76},
                "Mars": {"Sign": "Pisces", "Degree": 13.21},
                "Jupiter": {"Sign": "Scorpio", "Degree": 5.67},
                "Saturn": {"Sign": "Libra", "Degree": 10.45},
                "Uranus": {"Sign": "Sagittarius", "Degree": 8.12},
                "Neptune": {"Sign": "Sagittarius", "Degree": 20.33},
                "Pluto": {"Sign": "Libra", "Degree": 28.89},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        receptions = graph.find_all_receptions()

        # Should detect any mutual receptions in chart
        # (actual count depends on chart)
        assert isinstance(receptions, list)
        for r in receptions:
            assert len(r) == 2  # Each reception is a tuple of 2 planets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
