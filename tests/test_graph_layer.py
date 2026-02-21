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


class TestDispositorChains:
    """Test dispositor chain functionality (Task 4.1.2)"""

    def test_basic_chain(self):
        """Basic chain: Moon in Gemini → Mercury"""
        chart_data = {
            "planets": {
                "Moon": {"Sign": "Gemini", "Degree": 10.0},
                "Mercury": {"Sign": "Virgo", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("Moon")

        # Moon in Gemini → Mercury (rules Gemini)
        # Mercury in Virgo → Mercury (rules its own sign)
        assert len(chain) == 2
        assert chain[0] == "Moon"
        assert chain[1] == "Mercury"

    def test_final_dispositor_in_own_sign(self):
        """Planet in its own sign is final dispositor"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Leo", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("Sun")

        # Sun in Leo → Sun (rules its own sign)
        assert len(chain) == 1
        assert chain[0] == "Sun"

        final = graph.find_final_dispositor("Sun")
        assert final == "Sun"

    def test_three_level_chain(self):
        """Three-level chain: Moon → Mercury → Jupiter"""
        chart_data = {
            "planets": {
                "Moon": {"Sign": "Gemini", "Degree": 10.0},
                "Mercury": {"Sign": "Pisces", "Degree": 15.0},
                "Jupiter": {"Sign": "Sagittarius", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="traditional")
        chain = graph.build_dispositor_chain("Moon")

        # Moon in Gemini → Mercury (rules Gemini)
        # Mercury in Pisces → Jupiter (traditional ruler)
        # Jupiter in Sagittarius → Jupiter (rules its own sign)
        assert len(chain) == 3
        assert chain == ["Moon", "Mercury", "Jupiter"]

        final = graph.find_final_dispositor("Moon")
        assert final == "Jupiter"

    def test_mutual_reception_loop(self):
        """Mutual reception creates loop in chain"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("Venus")

        # Venus in Aries → Mars (rules Aries)
        # Mars in Taurus → Venus (rules Taurus) - loop!
        assert len(chain) == 3
        assert chain[0] == "Venus"
        assert chain[1] == "Mars"
        assert "(loop)" in chain[2]
        assert "Venus" in chain[2]

    def test_analyze_dispositor_tree(self):
        """Analyze complete dispositor tree for chart"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Leo", "Degree": 15.0},
                "Moon": {"Sign": "Gemini", "Degree": 10.0},
                "Mercury": {"Sign": "Virgo", "Degree": 20.0},
                "Venus": {"Sign": "Aries", "Degree": 5.0},
                "Mars": {"Sign": "Taurus", "Degree": 8.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        analysis = graph.analyze_dispositor_tree()

        # Check structure
        assert "final_dispositors" in analysis
        assert "chains" in analysis
        assert "loops" in analysis

        # Sun in Leo → Sun (final)
        # Mercury in Virgo → Mercury (final)
        assert "Sun" in analysis["final_dispositors"]
        assert "Mercury" in analysis["final_dispositors"]

        # Venus-Mars mutual reception loop
        assert len(analysis["loops"]) == 1
        assert ("Mars", "Venus") in analysis["loops"] or ("Venus", "Mars") in analysis[
            "loops"
        ]

        # Check all planets have chains
        assert len(analysis["chains"]) == 5
        assert "Sun" in analysis["chains"]
        assert "Moon" in analysis["chains"]

    def test_traditional_vs_modern_rulers(self):
        """Traditional and modern modes produce different chains"""
        chart_data = {
            "planets": {
                "Moon": {"Sign": "Pisces", "Degree": 10.0},
                "Jupiter": {"Sign": "Sagittarius", "Degree": 15.0},
                "Neptune": {"Sign": "Capricorn", "Degree": 20.0},
            }
        }

        # Traditional: Pisces ruled by Jupiter
        graph_trad = ChartGraph(chart_data, mode="traditional")
        chain_trad = graph_trad.build_dispositor_chain("Moon")
        # Moon in Pisces → Jupiter → Jupiter (final)
        assert chain_trad[-1] == "Jupiter"

        # Modern: Pisces ruled by Neptune
        graph_mod = ChartGraph(chart_data, mode="modern")
        chain_mod = graph_mod.build_dispositor_chain("Moon")
        # Moon in Pisces → Neptune → Saturn → ...
        assert "Neptune" in chain_mod

    def test_complex_tree_analysis(self):
        """Full 10-planet chart dispositor analysis"""
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
        analysis = graph.analyze_dispositor_tree()

        # All 10 planets should have chains
        assert len(analysis["chains"]) == 10

        # Each chain should start with the planet itself
        for planet, chain in analysis["chains"].items():
            assert chain[0] == planet

        # This chart creates complex loops with no final dispositors
        # (Jupiter → Pluto → Venus → Jupiter creates 3-way loop)
        # Total final dispositors + loops should be > 0
        assert len(analysis["final_dispositors"]) + len(analysis["loops"]) > 0

    def test_missing_planet_data(self):
        """Handle planet with missing sign data"""
        chart_data = {
            "planets": {
                "Sun": {"Degree": 15.0},  # Missing Sign
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("Sun")

        # Should return just the planet itself
        assert chain == ["Sun"]

    def test_unknown_planet(self):
        """Handle unknown planet gracefully"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Leo", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("UnknownPlanet")

        # Should return just the planet name
        assert chain == ["UnknownPlanet"]

    def test_find_final_dispositor_no_loop(self):
        """Find final dispositor for normal chain"""
        chart_data = {
            "planets": {
                "Moon": {"Sign": "Gemini", "Degree": 10.0},
                "Mercury": {"Sign": "Virgo", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        final = graph.find_final_dispositor("Moon")

        # Moon → Mercury (final)
        assert final == "Mercury"

    def test_find_final_dispositor_with_loop(self):
        """Find final dispositor when chain has loop"""
        chart_data = {
            "planets": {
                "Venus": {"Sign": "Aries", "Degree": 15.0},
                "Mars": {"Sign": "Taurus", "Degree": 20.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        final = graph.find_final_dispositor("Venus")

        # Venus → Mars → Venus (loop) - final should be Venus without "(loop)"
        assert final == "Venus"
        assert "(loop)" not in final


class TestDispositorEdgeCases:
    """Edge cases for dispositor chains"""

    def test_empty_chart(self):
        """Empty chart analysis"""
        chart_data = {"planets": {}}

        graph = ChartGraph(chart_data, mode="modern")
        analysis = graph.analyze_dispositor_tree()

        assert analysis["final_dispositors"] == []
        assert analysis["chains"] == {}
        assert analysis["loops"] == []

    def test_single_planet_analysis(self):
        """Single planet in own sign"""
        chart_data = {
            "planets": {
                "Sun": {"Sign": "Leo", "Degree": 15.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        analysis = graph.analyze_dispositor_tree()

        assert "Sun" in analysis["final_dispositors"]
        assert len(analysis["loops"]) == 0
        assert analysis["chains"]["Sun"] == ["Sun"]

    def test_chain_safety_limit(self):
        """Chain building has safety limit to prevent infinite loops"""
        # This shouldn't happen in real charts, but test the safety mechanism
        chart_data = {
            "planets": {
                "Planet1": {"Sign": "Aries", "Degree": 10.0},
                "Mars": {"Sign": "Taurus", "Degree": 15.0},
                "Venus": {"Sign": "Gemini", "Degree": 20.0},
                "Mercury": {"Sign": "Cancer", "Degree": 25.0},
                "Moon": {"Sign": "Leo", "Degree": 30.0},
                "Sun": {"Sign": "Virgo", "Degree": 5.0},
            }
        }

        graph = ChartGraph(chart_data, mode="modern")
        chain = graph.build_dispositor_chain("Planet1")

        # Should stop at safety limit or find final dispositor
        assert len(chain) <= 13  # Max 12 iterations + original planet


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
