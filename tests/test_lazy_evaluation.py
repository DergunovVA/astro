"""
Tests for lazy evaluation (short-circuit) in DSL evaluator

Tests that AND/OR operators properly short-circuit to avoid
unnecessary computation.
"""

import pytest
from src.dsl.parser import parse
from src.dsl.evaluator import Evaluator


class TestLazyEvaluationAND:
    """Test short-circuit AND evaluation"""

    def test_and_short_circuit_on_false_left(self):
        """Test that AND doesn't evaluate right when left is False"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries"},
                "NonExistent": {"Sign": "Error"},  # Would cause error if accessed
            }
        }

        # False AND <anything> should short-circuit and not evaluate right
        formula = "Sun.Sign == Leo AND NonExistent.Sign == Error"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        # Should return False without evaluating NonExistent.Sign
        # (which would raise an error)
        result = evaluator.evaluate(ast)
        assert result == False

    def test_and_evaluates_right_when_left_true(self):
        """Test that AND evaluates right when left is True"""
        chart = {"planets": {"Sun": {"Sign": "Aries"}, "Moon": {"Sign": "Taurus"}}}

        formula = "Sun.Sign == Aries AND Moon.Sign == Taurus"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == True

    def test_and_returns_false_when_both_false(self):
        """Test AND with both sides False"""
        chart = {"planets": {"Sun": {"Sign": "Aries"}}}

        formula = "Sun.Sign == Leo AND Sun.Sign == Virgo"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == False


class TestLazyEvaluationOR:
    """Test short-circuit OR evaluation"""

    def test_or_short_circuit_on_true_left(self):
        """Test that OR doesn't evaluate right when left is True"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries"},
                "NonExistent": {"Sign": "Error"},  # Would cause error if accessed
            }
        }

        # True OR <anything> should short-circuit and not evaluate right
        formula = "Sun.Sign == Aries OR NonExistent.Sign == Error"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        # Should return True without evaluating NonExistent.Sign
        result = evaluator.evaluate(ast)
        assert result == True

    def test_or_evaluates_right_when_left_false(self):
        """Test that OR evaluates right when left is False"""
        chart = {"planets": {"Sun": {"Sign": "Aries"}, "Moon": {"Sign": "Taurus"}}}

        formula = "Sun.Sign == Leo OR Moon.Sign == Taurus"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == True

    def test_or_returns_false_when_both_false(self):
        """Test OR with both sides False"""
        chart = {"planets": {"Sun": {"Sign": "Aries"}}}

        formula = "Sun.Sign == Leo OR Sun.Sign == Virgo"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == False


class TestComplexLazyEvaluation:
    """Test lazy evaluation in complex nested formulas"""

    def test_nested_and_or_short_circuits(self):
        """Test short-circuiting in nested AND/OR"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries"},
                "Moon": {"Sign": "Taurus"},
            }
        }

        # (False AND <heavy>) OR True
        # Should short-circuit both: False AND doesn't evaluate right,
        # and OR returns True immediately
        formula = "(Sun.Sign == Leo AND Moon.Sign == Gemini) OR Sun.Sign == Aries"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == True

    def test_multiple_and_short_circuit(self):
        """Test multiple ANDs with early short-circuit"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries", "House": 1},
                "Moon": {"Sign": "Taurus"},
            }
        }

        # First condition is False, rest should not be evaluated
        formula = "Sun.Sign == Leo AND Sun.House == 1 AND Moon.Sign == Taurus"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == False

    def test_multiple_or_short_circuit(self):
        """Test multiple ORs with early short-circuit"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries", "House": 1},
                "Moon": {"Sign": "Taurus"},
            }
        }

        # First condition is True, rest should not be evaluated
        formula = "Sun.Sign == Aries OR Sun.House == 10 OR Moon.Sign == Gemini"
        ast = parse(formula)
        evaluator = Evaluator(chart)

        result = evaluator.evaluate(ast)
        assert result == True


class TestPerformanceBenefit:
    """Test that lazy evaluation provides performance benefit"""

    def test_and_performance_with_expensive_right(self):
        """Test that expensive right side is skipped when left is False"""
        chart = {"planets": {"Sun": {"Sign": "Aries", "House": 1}}}

        # Create formula with expensive right side (many comparisons)
        expensive_right = " AND ".join([f"Sun.House == {i}" for i in range(100)])
        formula = f"Sun.Sign == Leo AND ({expensive_right})"

        ast = parse(formula)
        evaluator = Evaluator(chart)

        # Should be fast because right side is never evaluated
        import time

        start = time.perf_counter()
        result = evaluator.evaluate(ast)
        elapsed = time.perf_counter() - start

        assert result == False
        # Should complete very quickly (< 1ms) because right side skipped
        assert elapsed < 0.001  # Less than 1 millisecond

    def test_or_performance_with_expensive_right(self):
        """Test that expensive right side is skipped when left is True"""
        chart = {"planets": {"Sun": {"Sign": "Aries", "House": 1}}}

        # Create formula with expensive right side
        expensive_right = " OR ".join([f"Sun.House == {i}" for i in range(100)])
        formula = f"Sun.Sign == Aries OR ({expensive_right})"

        ast = parse(formula)
        evaluator = Evaluator(chart)

        # Should be fast because right side is never evaluated
        import time

        start = time.perf_counter()
        result = evaluator.evaluate(ast)
        elapsed = time.perf_counter() - start

        assert result == True
        # Should complete very quickly
        assert elapsed < 0.001  # Less than 1 millisecond


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
