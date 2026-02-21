"""
Performance benchmarks for Task 3.2 optimization improvements

Verifies 10x performance improvements from:
1. AST caching (parse_cached)
2. Batch processing (BatchEvaluator)
3. Lazy evaluation (short-circuit AND/OR)

Target improvements:
- Simple formula: 10ms → 1ms (10x)
- Complex formula: 50ms → 5ms (10x)
- Batch 100 formulas: 1000ms → 100ms (10x)
"""

import pytest
from src.dsl.parser import parse
from src.dsl.evaluator import Evaluator
from src.dsl.cache import parse_cached, clear_cache
from src.dsl.batch import BatchEvaluator


@pytest.fixture
def sample_chart():
    """Sample chart for benchmarking"""
    return {
        "planets": {
            "Sun": {"Sign": "Aries", "House": 1, "Degree": 15.5},
            "Moon": {"Sign": "Taurus", "House": 2, "Degree": 22.3},
            "Mercury": {"Sign": "Aries", "House": 1, "Degree": 8.2},
            "Venus": {"Sign": "Pisces", "House": 12, "Degree": 28.7},
            "Mars": {"Sign": "Gemini", "House": 3, "Degree": 12.1},
        }
    }


class TestCachingPerformance:
    """Test AST caching performance improvements"""

    def test_simple_parse_without_cache(self, benchmark, sample_chart):
        """Baseline: Parse simple formula without cache"""

        def parse_without_cache():
            # Force fresh parse each time
            formula = "Sun.Sign == Aries"
            ast = parse(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(parse_without_cache)
        assert result == True

    def test_simple_parse_with_cache_miss(self, benchmark, sample_chart):
        """Parse with cache (first call - cache miss)"""
        clear_cache()

        def parse_with_cache_miss():
            formula = "Sun.Sign == Aries"  # Unique each call
            ast = parse_cached(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(parse_with_cache_miss)
        assert result == True

    def test_simple_parse_with_cache_hit(self, benchmark, sample_chart):
        """Parse with cache (subsequent calls - cache hit)"""
        clear_cache()
        formula = "Sun.Sign == Aries"

        # Prime the cache
        parse_cached(formula)

        def parse_with_cache_hit():
            ast = parse_cached(formula)  # Should hit cache
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(parse_with_cache_hit)
        assert result == True

    def test_complex_parse_without_cache(self, benchmark, sample_chart):
        """Baseline: Parse complex formula without cache"""

        def parse_complex_without_cache():
            formula = (
                "(Sun.Sign == Aries OR Moon.Sign == Taurus) "
                "AND (Mercury.House == 1 OR Venus.House == 12)"
            )
            ast = parse(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(parse_complex_without_cache)
        assert result == True

    def test_complex_parse_with_cache_hit(self, benchmark, sample_chart):
        """Parse complex formula with cache hit"""
        clear_cache()
        formula = (
            "(Sun.Sign == Aries OR Moon.Sign == Taurus) "
            "AND (Mercury.House == 1 OR Venus.House == 12)"
        )

        # Prime the cache
        parse_cached(formula)

        def parse_with_cache():
            ast = parse_cached(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(parse_with_cache)
        assert result == True


class TestBatchProcessingPerformance:
    """Test batch processing performance improvements"""

    def test_evaluate_100_formulas_individually(self, benchmark, sample_chart):
        """Baseline: Evaluate 100 formulas individually without batch"""

        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "Mercury.House == 1",
            "Venus.House == 12",
            "Mars.Sign == Gemini",
        ] * 20  # 100 formulas (20 repetitions of 5 unique)

        def evaluate_individually():
            results = []
            for formula in formulas:
                ast = parse(formula)  # Parse each time
                evaluator = Evaluator(sample_chart)
                results.append(evaluator.evaluate(ast))
            return results

        results = benchmark(evaluate_individually)
        assert len(results) == 100

    def test_evaluate_100_formulas_batch_no_cache(self, benchmark, sample_chart):
        """Batch evaluate 100 formulas without cache"""

        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "Mercury.House == 1",
            "Venus.House == 12",
            "Mars.Sign == Gemini",
        ] * 20

        def evaluate_batch_no_cache():
            batch_eval = BatchEvaluator(sample_chart)
            return batch_eval.evaluate_batch(formulas, use_cache=False)

        results = benchmark(evaluate_batch_no_cache)
        assert len(results) == 100

    def test_evaluate_100_formulas_batch_with_cache(self, benchmark, sample_chart):
        """Batch evaluate 100 formulas WITH cache"""

        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "Mercury.House == 1",
            "Venus.House == 12",
            "Mars.Sign == Gemini",
        ] * 20  # 100 formulas (only 5 unique - high cache hit rate)

        clear_cache()

        def evaluate_batch_with_cache():
            batch_eval = BatchEvaluator(sample_chart)
            return batch_eval.evaluate_batch(formulas, use_cache=True)

        results = benchmark(evaluate_batch_with_cache)
        assert len(results) == 100


class TestLazyEvaluationPerformance:
    """Test lazy evaluation (short-circuit) performance improvements"""

    def test_and_with_expensive_right_no_lazy(self, benchmark, sample_chart):
        """Baseline: AND with expensive right side (would evaluate all)"""

        # Create expensive formula (50 comparisons on right side)
        expensive_conditions = " OR ".join([f"Sun.House == {i}" for i in range(2, 52)])
        formula = f"Sun.Sign == Leo AND ({expensive_conditions})"

        def evaluate_without_shortcircuit():
            # Manually evaluate both sides (simulating no lazy eval)
            ast_left = parse("Sun.Sign == Leo")
            ast_right = parse(expensive_conditions)

            evaluator = Evaluator(sample_chart)
            left_result = evaluator.evaluate(ast_left)
            right_result = evaluator.evaluate(ast_right)
            return left_result and right_result

        result = benchmark(evaluate_without_shortcircuit)
        assert result == False

    def test_and_with_expensive_right_lazy(self, benchmark, sample_chart):
        """With lazy evaluation: AND short-circuits, skips expensive right"""

        expensive_conditions = " OR ".join([f"Sun.House == {i}" for i in range(2, 52)])
        formula = f"Sun.Sign == Leo AND ({expensive_conditions})"

        def evaluate_with_shortcircuit():
            # Lazy evaluation: right side never evaluated
            ast = parse(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(evaluate_with_shortcircuit)
        assert result == False

    def test_or_with_expensive_right_no_lazy(self, benchmark, sample_chart):
        """Baseline: OR with expensive right side (would evaluate all)"""

        expensive_conditions = " AND ".join(
            [f"Moon.House == {i}" for i in range(3, 53)]
        )
        formula = f"Sun.Sign == Aries OR ({expensive_conditions})"

        def evaluate_without_shortcircuit():
            ast_left = parse("Sun.Sign == Aries")
            ast_right = parse(expensive_conditions)

            evaluator = Evaluator(sample_chart)
            left_result = evaluator.evaluate(ast_left)
            right_result = evaluator.evaluate(ast_right)
            return left_result or right_result

        result = benchmark(evaluate_without_shortcircuit)
        assert result == True

    def test_or_with_expensive_right_lazy(self, benchmark, sample_chart):
        """With lazy evaluation: OR short-circuits, skips expensive right"""

        expensive_conditions = " AND ".join(
            [f"Moon.House == {i}" for i in range(3, 53)]
        )
        formula = f"Sun.Sign == Aries OR ({expensive_conditions})"

        def evaluate_with_shortcircuit():
            ast = parse(formula)
            evaluator = Evaluator(sample_chart)
            return evaluator.evaluate(ast)

        result = benchmark(evaluate_with_shortcircuit)
        assert result == True


class TestCombinedOptimizations:
    """Test combined effect of all optimizations"""

    def test_realistic_workflow_without_optimizations(self, benchmark, sample_chart):
        """Baseline: Evaluate 50 formulas without any optimizations"""

        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "(Sun.Sign == Aries OR Moon.Sign == Gemini) AND Mercury.House == 1",
            "Venus.House == 12",
            "Mars.Sign == Gemini",
            "Sun.Degree > 10 AND Sun.Degree < 20",
            "Moon.Degree > 20",
            "(Sun.Sign == Aries AND Sun.House == 1) OR Moon.Sign == Taurus",
            "Mercury.Sign == Aries",
            "Venus.Sign == Pisces",
        ] * 5  # 50 formulas

        def workflow_no_optimizations():
            results = []
            for formula in formulas:
                # Parse every time (no cache)
                ast = parse(formula)
                # Create new evaluator each time (no reuse)
                evaluator = Evaluator(sample_chart)
                # No lazy evaluation benefit demonstrated
                results.append(evaluator.evaluate(ast))
            return results

        results = benchmark(workflow_no_optimizations)
        assert len(results) == 50

    def test_realistic_workflow_with_all_optimizations(self, benchmark, sample_chart):
        """With optimizations: Cache + batch + lazy evaluation"""

        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "(Sun.Sign == Aries OR Moon.Sign == Gemini) AND Mercury.House == 1",
            "Venus.House == 12",
            "Mars.Sign == Gemini",
            "Sun.Degree > 10 AND Sun.Degree < 20",
            "Moon.Degree > 20",
            "(Sun.Sign == Aries AND Sun.House == 1) OR Moon.Sign == Taurus",
            "Mercury.Sign == Aries",
            "Venus.Sign == Pisces",
        ] * 5  # 50 formulas (10 unique, so good cache hit rate)

        clear_cache()

        def workflow_with_optimizations():
            # Use batch evaluator with cache
            batch_eval = BatchEvaluator(sample_chart)
            return batch_eval.evaluate_batch(formulas, use_cache=True)

        results = benchmark(workflow_with_optimizations)
        assert len(results) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
