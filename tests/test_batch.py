"""
Tests for DSL batch processing module

Tests batch evaluation, performance optimizations,
and statistics tracking.
"""

import pytest
from src.dsl.batch import (
    BatchEvaluator,
    batch_evaluate,
    evaluate_all_true,
    evaluate_any_true,
)
from src.dsl.cache import clear_cache


# Sample chart data
SAMPLE_CHART = {
    "planets": {
        "Sun": {"Sign": "Aries", "House": 1, "Dignity": "Exaltation", "Degree": 15},
        "Moon": {"Sign": "Taurus", "House": 2, "Dignity": "Exaltation", "Degree": 20},
        "Mars": {"Sign": "Leo", "House": 5, "Dignity": "Neutral", "Retrograde": False},
        "Venus": {
            "Sign": "Pisces",
            "House": 12,
            "Dignity": "Exaltation",
            "Retrograde": False,
        },
    },
    "houses": {
        1: {"Sign": "Aries", "Ruler": "Mars"},
        2: {"Sign": "Taurus", "Ruler": "Venus"},
    },
    "aspects": [
        {"Planet1": "Sun", "Planet2": "Moon", "Type": "Sextile"},
        {"Planet1": "Mars", "Planet2": "Venus", "Type": "Trine"},
    ],
}


class TestBatchEvaluator:
    """Test BatchEvaluator class"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_create_evaluator(self):
        """Test creating batch evaluator"""
        evaluator = BatchEvaluator(SAMPLE_CHART)
        assert evaluator.chart_data == SAMPLE_CHART
        assert evaluator.evaluator is not None

    def test_evaluate_batch_simple(self):
        """Test batch evaluation of simple formulas"""
        evaluator = BatchEvaluator(SAMPLE_CHART)
        formulas = [
            "Sun.Sign == Aries",  # True
            "Moon.Sign == Taurus",  # True
            "Mars.Sign == Aries",  # False
        ]

        results = evaluator.evaluate_batch(formulas)
        assert results == [True, True, False]

    def test_evaluate_batch_complex(self):
        """Test batch evaluation of complex formulas"""
        evaluator = BatchEvaluator(SAMPLE_CHART)
        formulas = [
            "Sun.Sign == Aries AND Sun.House == 1",  # True
            "Moon.Dignity == Exaltation OR Mars.Retrograde == True",  # True
            "Sun.Degree > 10 AND Moon.Degree < 25",  # True
        ]

        results = evaluator.evaluate_batch(formulas)
        assert results == [True, True, True]

    def test_evaluate_batch_with_cache(self):
        """Test that batch evaluator uses cache"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        # Evaluate with repeated formulas
        formulas = ["Sun.Sign == Aries"] * 5
        results = evaluator.evaluate_batch(formulas, use_cache=True)

        assert results == [True] * 5

        # Check stats
        stats = evaluator.get_stats()
        assert stats["total_formulas"] == 5

    def test_evaluate_batch_without_cache(self):
        """Test batch evaluation with cache disabled"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus"]
        results = evaluator.evaluate_batch(formulas, use_cache=False)

        assert results == [True, True]
        assert not evaluator.get_stats()["cache_enabled"]

    def test_evaluate_single(self):
        """Test single formula evaluation"""
        evaluator = BatchEvaluator(SAMPLE_CHART)
        result = evaluator.evaluate_single("Sun.Sign == Aries")

        assert result

    def test_get_stats(self):
        """Test statistics tracking"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus"]
        evaluator.evaluate_batch(formulas)

        stats = evaluator.get_stats()
        assert stats["total_formulas"] == 2
        assert stats["total_time_ms"] > 0
        assert stats["avg_time_ms"] > 0
        assert stats["cache_enabled"]

    def test_reset_stats(self):
        """Test resetting statistics"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        formulas = ["Sun.Sign == Aries"]
        evaluator.evaluate_batch(formulas)

        evaluator.reset_stats()
        stats = evaluator.get_stats()
        assert stats["total_formulas"] == 0
        assert stats["total_time_ms"] == 0.0


class TestBatchEvaluateFunction:
    """Test batch_evaluate convenience function"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_batch_evaluate_basic(self):
        """Test basic batch_evaluate usage"""
        formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus"]
        results = batch_evaluate(formulas, SAMPLE_CHART)

        assert results == [True, True]

    def test_batch_evaluate_empty_list(self):
        """Test batch_evaluate with empty list"""
        results = batch_evaluate([], SAMPLE_CHART)
        assert results == []

    def test_batch_evaluate_single_formula(self):
        """Test batch_evaluate with single formula"""
        results = batch_evaluate(["Sun.Sign == Aries"], SAMPLE_CHART)
        assert results == [True]

    def test_batch_evaluate_mixed_results(self):
        """Test batch_evaluate with mixed True/False results"""
        formulas = [
            "Sun.Sign == Aries",  # True
            "Sun.Sign == Leo",  # False
            "Moon.Dignity == Exaltation",  # True
            "Mars.Retrograde == True",  # False
        ]

        results = batch_evaluate(formulas, SAMPLE_CHART)
        assert results == [True, False, True, False]


class TestEvaluateAllTrue:
    """Test evaluate_all_true function"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_all_true(self):
        """Test when all formulas are true"""
        formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus", "Mars.Sign == Leo"]

        result = evaluate_all_true(formulas, SAMPLE_CHART)
        assert result

    def test_not_all_true(self):
        """Test when not all formulas are true"""
        formulas = ["Sun.Sign == Aries", "Moon.Sign == Leo"]  # Second is False

        result = evaluate_all_true(formulas, SAMPLE_CHART)
        assert not result

    def test_all_false(self):
        """Test when all formulas are false"""
        formulas = ["Sun.Sign == Leo", "Moon.Sign == Aries"]

        result = evaluate_all_true(formulas, SAMPLE_CHART)
        assert not result

    def test_empty_list(self):
        """Test with empty list (vacuously true)"""
        result = evaluate_all_true([], SAMPLE_CHART)
        assert result  # all([]) == True in Python


class TestEvaluateAnyTrue:
    """Test evaluate_any_true function"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_any_true(self):
        """Test when at least one formula is true"""
        formulas = ["Sun.Sign == Leo", "Moon.Sign == Taurus"]  # Second is True

        result = evaluate_any_true(formulas, SAMPLE_CHART)
        assert result

    def test_all_true(self):
        """Test when all formulas are true"""
        formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus"]

        result = evaluate_any_true(formulas, SAMPLE_CHART)
        assert result

    def test_none_true(self):
        """Test when no formulas are true"""
        formulas = ["Sun.Sign == Leo", "Moon.Sign == Aries"]

        result = evaluate_any_true(formulas, SAMPLE_CHART)
        assert not result

    def test_empty_list(self):
        """Test with empty list"""
        result = evaluate_any_true([], SAMPLE_CHART)
        assert not result  # any([]) == False in Python


class TestBatchPerformance:
    """Test batch processing performance benefits"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_repeated_formulas_use_cache(self):
        """Test that repeated formulas benefit from cache"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        # Same formula repeated many times
        formulas = ["Sun.Sign == Aries"] * 100

        results = evaluator.evaluate_batch(formulas)
        assert all(results)

        stats = evaluator.get_stats()
        # With cache, should be very fast
        assert stats["avg_time_ms"] < 1.0  # Less than 1ms per formula

    def test_large_batch(self):
        """Test batch processing of many different formulas"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        # 50 different formulas
        formulas = []
        for i in range(50):
            formulas.append(f"Sun.Degree > {i}")

        results = evaluator.evaluate_batch(formulas)
        assert len(results) == 50

    def test_cumulative_stats(self):
        """Test that stats accumulate across multiple batches"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        # First batch
        evaluator.evaluate_batch(["Sun.Sign == Aries"])
        stats1 = evaluator.get_stats()

        # Second batch
        evaluator.evaluate_batch(["Moon.Sign == Taurus"])
        stats2 = evaluator.get_stats()

        assert stats2["total_formulas"] == stats1["total_formulas"] + 1
        assert stats2["total_time_ms"] > stats1["total_time_ms"]


class TestErrorHandling:
    """Test error handling in batch processing"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_invalid_formula_in_batch(self):
        """Test that invalid formula raises error"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        formulas = ["Sun.Sign == Aries", "invalid !!!"]

        with pytest.raises(Exception):  # Should raise parser error
            evaluator.evaluate_batch(formulas)

    def test_invalid_property_in_formula(self):
        """Test formula with invalid property"""
        evaluator = BatchEvaluator(SAMPLE_CHART)

        # NonExistentPlanet doesn't exist in chart
        formulas = ["NonExistentPlanet.Sign == Aries"]

        with pytest.raises(Exception):  # Should raise evaluator error
            evaluator.evaluate_batch(formulas)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
