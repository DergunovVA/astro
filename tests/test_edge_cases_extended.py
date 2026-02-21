"""
Extended Edge Case Tests: Stage 2 Task 2.1

Comprehensive testing for:
- Minor bodies (Chiron, Lilith, True Node)
- Outer planets with controversial dignities
- Boundary conditions (0°, 29°59', house cusps)
- Complex DSL formula edge cases
- Extreme coordinates and dates

Запуск:
    pytest tests/test_edge_cases_extended.py -v
"""

import pytest
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dsl.evaluator import evaluate
from src.dsl.validator import AstrologicalValidator


# ============================================================================
# MINOR BODIES TESTS
# ============================================================================


class TestMinorBodiesHandling:
    """Тесты для малых тел: Chiron, Lilith, True Node, etc."""

    def test_chiron_no_classical_dignities(self):
        """Chiron не имеет классических достоинств"""
        chart = {
            "planets": {
                "Chiron": {
                    "Sign": "Aries",
                    "House": 1,
                    "Dignity": "Peregrine",  # Нейтральное
                    "Degree": 15.5,
                }
            }
        }

        # Should not raise error
        result = evaluate("Chiron.Sign == Aries", chart)
        assert result is True

        # Chiron should work in house formulas
        result = evaluate("Chiron.House == 1", chart)
        assert result is True

    def test_chiron_dignity_peregrine(self):
        """Chiron всегда Peregrine (нет традиционных достоинств)"""
        validator = AstrologicalValidator(mode="modern")

        # Chiron in any sign should be Peregrine
        for sign in ["Aries", "Taurus", "Gemini", "Cancer"]:
            status = validator.get_dignity_status("Chiron", sign)
            assert status == "Peregrine", f"Chiron должен быть Peregrine в {sign}"

    def test_lilith_mean_vs_true(self):
        """Различие между Mean Lilith и True Lilith"""
        chart = {
            "planets": {
                "Lilith": {"Sign": "Scorpio", "Degree": 15.2, "House": 8},
                "TrueLilith": {"Sign": "Scorpio", "Degree": 16.8, "House": 8},
            }
        }

        # Both should be accessible
        result1 = evaluate("Lilith.Sign == Scorpio", chart)
        assert result1 is True

        result2 = evaluate("TrueLilith.Sign == Scorpio", chart)
        assert result2 is True

    def test_true_node_retrograde(self):
        """True Node может быть ретроградным"""
        chart = {
            "planets": {
                "TrueNode": {
                    "Sign": "Cancer",
                    "Degree": 15.5,
                    "Retrograde": True,
                }
            }
        }

        result = evaluate("TrueNode.Retrograde == True", chart)
        assert result is True

    def test_part_of_fortune_calculation(self):
        """Part of Fortune - вычисляемая точка"""
        chart = {
            "planets": {"PartOfFortune": {"Sign": "Libra", "Degree": 23.4, "House": 7}}
        }

        result = evaluate("PartOfFortune.Sign == Libra", chart)
        assert result is True

        result = evaluate("PartOfFortune.House == 7", chart)
        assert result is True

    def test_vertex_as_calculated_point(self):
        """Vertex - важная вычисляемая точка"""
        chart = {
            "planets": {"Vertex": {"Sign": "Aquarius", "Degree": 8.2, "House": 11}}
        }

        result = evaluate("Vertex.Sign == Aquarius", chart)
        assert result is True


# ============================================================================
# OUTER PLANETS CONTROVERSIAL DIGNITIES
# ============================================================================


class TestOuterPlanetsDignities:
    """Тесты для спорных достоинств внешних планет"""

    def test_uranus_exaltation_scorpio_modern(self):
        """Uranus экзальтирован в Scorpio (modern mode)"""
        validator = AstrologicalValidator(mode="modern")

        # В modern mode допускается экзальтация Uranus
        result = validator.check_exaltation("Uranus", "Scorpio")
        # Should not be error (может быть warning или None)
        assert result is None or (result and result.level != "ERROR")

    def test_uranus_not_in_traditional(self):
        """Uranus не рассматривается в traditional mode"""
        validator = AstrologicalValidator(mode="traditional")

        # В traditional mode Uranus may not have dignities
        rulers = validator.get_ruler("Aquarius")
        # Traditional: только Saturn
        assert "Saturn" in rulers

    def test_neptune_debated_exaltation(self):
        """Neptune экзальтация спорная (Pisces или Cancer)"""
        validator = AstrologicalValidator(mode="modern")

        # Проверяем, что Neptune обрабатывается без ошибок
        status = validator.get_dignity_status("Neptune", "Pisces")
        # Может быть Rulership или Exaltation или Peregrine
        assert status in ["Rulership", "Exaltation", "Peregrine"]

    def test_pluto_scorpio_rulership_modern(self):
        """Pluto управляет Scorpio в modern mode"""
        validator = AstrologicalValidator(mode="modern")

        rulers = validator.get_ruler("Scorpio")
        assert "Pluto" in rulers, "Pluto должен быть в управителях Scorpio (modern)"
        assert "Mars" in rulers, "Mars также остается управителем"

    def test_pluto_not_in_traditional_scorpio(self):
        """Pluto НЕ управляет Scorpio в traditional mode"""
        validator = AstrologicalValidator(mode="traditional")

        rulers = validator.get_ruler("Scorpio")
        assert "Mars" in rulers
        assert "Pluto" not in rulers, "Pluto не должен быть в traditional"


# ============================================================================
# BOUNDARY CONDITIONS TESTS
# ============================================================================


class TestBoundaryConditions:
    """Тесты граничных условий: 0°, 29°59', cusps"""

    def test_zero_degrees_aries(self):
        """0° Aries - начало зодиака"""
        chart = {
            "planets": {"Sun": {"Sign": "Aries", "Degree": 0.0, "AbsoluteDegree": 0.0}}
        }

        result = evaluate("Sun.Degree == 0", chart)
        assert result is True

        result = evaluate("Sun.Sign == Aries", chart)
        assert result is True

    def test_29_degrees_59_minutes_pisces(self):
        """29°59' Pisces - конец зодиака"""
        chart = {
            "planets": {
                "Moon": {
                    "Sign": "Pisces",
                    "Degree": 29.983333,  # 29°59'
                    "AbsoluteDegree": 359.983333,
                }
            }
        }

        # Должно быть Pisces, не Aries
        result = evaluate("Moon.Sign == Pisces", chart)
        assert result is True

        result = evaluate("Moon.Degree > 29", chart)
        assert result is True

    def test_exact_house_cusp(self):
        """Планета точно на куспиде дома"""
        chart = {
            "planets": {"Mercury": {"Sign": "Gemini", "Degree": 15.0, "House": 7}},
            "houses": {
                "House7": {"Sign": "Gemini", "Degree": 15.0}  # Exact cusp
            },
        }

        result = evaluate("Mercury.House == 7", chart)
        assert result is True

    def test_anaretic_degree_29(self):
        """Анаретический градус (29°) - критическая точка"""
        chart = {
            "planets": {
                "Saturn": {
                    "Sign": "Capricorn",
                    "Degree": 29.5,
                    "House": 10,
                }
            }
        }

        # Saturn at 29° - anaretic degree
        result = evaluate("Saturn.Degree > 29", chart)
        assert result is True

        result = evaluate("Saturn.Degree < 30", chart)
        assert result is True

    def test_critical_degrees_fire_signs(self):
        """Критические градусы в огненных знаках (0°, 13°, 26°)"""
        chart = {
            "planets": {
                "Mars": {"Sign": "Aries", "Degree": 13.0, "House": 1},
                "Jupiter": {"Sign": "Leo", "Degree": 26.0, "House": 5},
            }
        }

        # Mars at 13° Aries (critical degree)
        result = evaluate("Mars.Degree == 13", chart)
        assert result is True

        # Jupiter at 26° Leo (critical degree)
        result = evaluate("Jupiter.Degree == 26", chart)
        assert result is True

    def test_exact_sign_boundary_transition(self):
        """Переход через границу знака: 29°59'59\" -> 0°00'01\" """
        chart1 = {
            "planets": {
                "Venus": {
                    "Sign": "Taurus",
                    "Degree": 29.999722,  # 29°59'59"
                }
            }
        }

        chart2 = {
            "planets": {
                "Venus": {
                    "Sign": "Gemini",
                    "Degree": 0.000278,  # 0°00'01"
                }
            }
        }

        # First chart: still Taurus
        result1 = evaluate("Venus.Sign == Taurus", chart1)
        assert result1 is True

        # Second chart: now Gemini
        result2 = evaluate("Venus.Sign == Gemini", chart2)
        assert result2 is True


# ============================================================================
# COMPLEX DSL FORMULA EDGE CASES
# ============================================================================


class TestComplexDSLFormulas:
    """Тесты сложных DSL формул с edge cases"""

    def test_nested_parentheses_deep(self):
        """Глубоко вложенные скобки"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Leo", "House": 5},
                "Moon": {"Sign": "Cancer", "House": 4},
                "Mercury": {"Sign": "Virgo", "House": 6},
            }
        }

        formula = "((Sun.Sign == Leo AND Moon.Sign == Cancer) OR (Mercury.Sign == Virgo)) AND (Sun.House > 4)"
        result = evaluate(formula, chart)
        assert result is True

    def test_multiple_not_operators(self):
        """Множественные NOT операторы"""
        chart = {"planets": {"Mars": {"Sign": "Aries", "Retrograde": False}}}

        formula = "NOT (NOT (Mars.Sign == Aries))"
        result = evaluate(formula, chart)
        assert result is True  # Double NOT cancels out

    def test_complex_in_operator_with_houses(self):
        """IN оператор с множеством значений"""
        chart = {
            "planets": {
                "Jupiter": {"House": 9},
                "Saturn": {"House": 10},
                "Uranus": {"House": 11},
            }
        }

        formula = "Jupiter.House IN [9, 10, 11, 12]"
        result = evaluate(formula, chart)
        assert result is True

    def test_aggregator_with_empty_result(self):
        """Агрегатор когда результат пустой"""
        chart = {
            "planets": {
                "Sun": {"Dignity": "Rulership"},
                "Moon": {"Dignity": "Exaltation"},
            }
        }

        # Ни одна планета не в Fall
        formula = "Fall IN planets.Dignity"
        result = evaluate(formula, chart)
        assert result is False

    def test_mixed_operators_precedence(self):
        """Приоритет операторов: AND vs OR"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries", "House": 1},
                "Moon": {"Sign": "Taurus", "House": 2},
            }
        }

        # OR имеет меньший приоритет чем AND
        formula = "Sun.Sign == Aries AND Sun.House == 1 OR Moon.Sign == Gemini"
        result = evaluate(formula, chart)
        assert result is True  # (True AND True) OR False = True

    def test_comparison_with_zero(self):
        """Сравнение с нулем"""
        chart = {"planets": {"Mercury": {"Degree": 0.0, "House": 1}}}

        formula = "Mercury.Degree == 0"
        result = evaluate(formula, chart)
        assert result is True

        formula = "Mercury.House > 0"
        result = evaluate(formula, chart)
        assert result is True


# ============================================================================
# EXTREME COORDINATES AND DATES
# ============================================================================


class TestExtremeCoordinatesAndDates:
    """Тесты экстремальных координат и дат"""

    def test_north_pole_latitude(self):
        """Северный полюс: 90° N"""
        # Note: дома могут вести себя странно на полюсах
        chart = {
            "metadata": {
                "latitude": 90.0,
                "longitude": 0.0,
            },
            "planets": {"Sun": {"Sign": "Gemini", "Degree": 15.0}},
        }

        # Sun position should still be valid
        result = evaluate("Sun.Sign == Gemini", chart)
        assert result is True

    def test_south_pole_latitude(self):
        """Южный полюс: 90° S"""
        chart = {
            "metadata": {
                "latitude": -90.0,
                "longitude": 0.0,
            },
            "planets": {"Moon": {"Sign": "Cancer", "Degree": 10.0}},
        }

        result = evaluate("Moon.Sign == Cancer", chart)
        assert result is True

    def test_date_line_crossing(self):
        """Пересечение линии перемены дат (180°)"""
        chart = {
            "metadata": {
                "latitude": 0.0,
                "longitude": 179.99,  # Почти на линии
            },
            "planets": {"Venus": {"Sign": "Libra", "House": 7}},
        }

        result = evaluate("Venus.Sign == Libra", chart)
        assert result is True

    def test_equator_zero_latitude(self):
        """Экватор: 0° широты"""
        chart = {
            "metadata": {
                "latitude": 0.0,
                "longitude": 0.0,  # Null Island
            },
            "planets": {"Mars": {"Sign": "Scorpio", "House": 8}},
        }

        result = evaluate("Mars.House == 8", chart)
        assert result is True


# ============================================================================
# RETROGRADE EDGE CASES
# ============================================================================


class TestRetrogradeEdgeCases:
    """Тесты edge cases для ретроградности"""

    def test_all_outer_planets_retrograde(self):
        """Все внешние планеты одновременно ретроградны"""
        chart = {
            "planets": {
                "Jupiter": {"Retrograde": True, "Sign": "Pisces"},
                "Saturn": {"Retrograde": True, "Sign": "Aquarius"},
                "Uranus": {"Retrograde": True, "Sign": "Taurus"},
                "Neptune": {"Retrograde": True, "Sign": "Pisces"},
                "Pluto": {"Retrograde": True, "Sign": "Capricorn"},
            }
        }

        # All should work
        result = evaluate(
            "Jupiter.Retrograde == True AND Saturn.Retrograde == True",
            chart,
        )
        assert result is True

    def test_mercury_retrograde_in_dignity(self):
        """Mercury ретроградный в своем достоинстве"""
        chart = {
            "planets": {
                "Mercury": {
                    "Sign": "Gemini",  # Rulership
                    "Retrograde": True,
                    "Dignity": "Rulership",
                }
            }
        }

        result = evaluate(
            "Mercury.Retrograde == True AND Mercury.Dignity == Rulership",
            chart,
        )
        assert result is True

    def test_venus_stations_direct(self):
        """Venus станция (переход из R в D)"""
        chart = {
            "planets": {
                "Venus": {
                    "Retrograde": False,
                    "Sign": "Capricorn",
                    "Degree": 15.2,
                    "Speed": 0.01,  # Почти стоит
                }
            }
        }

        # Venus not retrograde but very slow (station)
        result = evaluate("Venus.Retrograde == False", chart)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
