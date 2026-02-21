"""
Performance Regression Test Suite

Автоматическое обнаружение деградации производительности путем сравнения
текущих результатов с baseline метриками из Stage 2 Task 2.2.

Использование:
    # Запустить regression tests и сравнить с baseline
    pytest tests/test_performance_regression.py --benchmark-only --benchmark-compare=stage2_baseline

    # Сохранить новый baseline (только после code review)
    pytest tests/test_performance_regression.py --benchmark-only --benchmark-save=new_baseline

    # Генерировать HTML отчет
    pytest tests/test_performance_regression.py --benchmark-only --benchmark-histogram

Требования:
    - pytest-benchmark>=5.0
    - .benchmarks/stage2_baseline.json (создан в Task 2.2)
    - config/performance_thresholds.yaml
"""

import pytest
import yaml
from pathlib import Path
from src.dsl.lexer import tokenize
from src.dsl.parser import parse
from src.dsl.evaluator import evaluate


# Load performance thresholds
def load_thresholds():
    """Load performance thresholds from config file"""
    threshold_file = (
        Path(__file__).parent.parent / "config" / "performance_thresholds.yaml"
    )
    with open(threshold_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


THRESHOLDS = load_thresholds()


# Sample chart data for testing
SAMPLE_CHART = {
    "planets": {
        "Sun": {
            "Sign": "Aries",
            "House": 1,
            "Degree": 15.5,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Moon": {
            "Sign": "Taurus",
            "House": 2,
            "Degree": 23.2,
            "Dignity": "Exaltation",
            "Retrograde": False,
        },
        "Mercury": {
            "Sign": "Pisces",
            "House": 12,
            "Degree": 8.7,
            "Dignity": "Detriment",
            "Retrograde": True,
        },
        "Venus": {
            "Sign": "Pisces",
            "House": 12,
            "Degree": 18.3,
            "Dignity": "Exaltation",
            "Retrograde": False,
        },
        "Mars": {
            "Sign": "Cancer",
            "House": 4,
            "Degree": 10.1,
            "Dignity": "Fall",
            "Retrograde": False,
        },
        "Jupiter": {
            "Sign": "Cancer",
            "House": 4,
            "Degree": 25.6,
            "Dignity": "Exaltation",
            "Retrograde": False,
        },
        "Saturn": {
            "Sign": "Libra",
            "House": 7,
            "Degree": 12.4,
            "Dignity": "Exaltation",
            "Retrograde": False,
        },
    },
    "houses": {
        1: {"Sign": "Aries", "Degree": 0.0},
        2: {"Sign": "Taurus", "Degree": 30.0},
        4: {"Sign": "Cancer", "Degree": 90.0},
        7: {"Sign": "Libra", "Degree": 180.0},
        10: {"Sign": "Capricorn", "Degree": 270.0},
    },
}


def get_threshold_us(component: str, complexity: str, level: str = "warning") -> float:
    """Get threshold in microseconds from config

    Args:
        component: 'lexer', 'parser', 'evaluator', 'end_to_end'
        complexity: 'simple', 'medium', 'complex'
        level: 'target', 'warning', 'critical'

    Returns:
        Threshold time in microseconds
    """
    return float(THRESHOLDS[component][complexity][level])


# ============================================================================
# LEXER REGRESSION TESTS
# ============================================================================


class TestLexerRegression:
    """Regression tests for Lexer performance"""

    def test_lexer_simple_regression(self, benchmark):
        """Lexer simple formula should not regress beyond warning threshold"""
        formula = "Sun.Sign"

        result = benchmark(tokenize, formula)
        warning_us = get_threshold_us("lexer", "simple", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000  # Convert s to μs

        assert mean_us < warning_us, (
            f"Lexer simple performance regression detected: "
            f"{mean_us:.2f}μs > {warning_us:.2f}μs (warning threshold)"
        )

    def test_lexer_medium_regression(self, benchmark):
        """Lexer medium formula should not regress beyond warning threshold"""
        formula = "Sun.Sign == Aries AND Moon.House IN [1,2,3]"

        result = benchmark(tokenize, formula)

        warning_us = get_threshold_us("lexer", "medium", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Lexer medium performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_lexer_complex_regression(self, benchmark):
        """Lexer complex formula should not regress beyond warning threshold"""
        formula = "(Sun.Sign == Aries OR Moon.Sign == Taurus) AND (Jupiter.House IN [1,4,7,10])"

        result = benchmark(tokenize, formula)

        warning_us = get_threshold_us("lexer", "complex", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Lexer complex performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )


# ============================================================================
# PARSER REGRESSION TESTS
# ============================================================================


class TestParserRegression:
    """Regression tests for Parser performance"""

    def test_parser_simple_regression(self, benchmark):
        """Parser simple formula should not regress beyond warning threshold"""
        formula = "Sun.Sign"

        result = benchmark(parse, formula)

        warning_us = get_threshold_us("parser", "simple", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Parser simple performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_parser_medium_regression(self, benchmark):
        """Parser medium formula should not regress beyond warning threshold"""
        formula = "Sun.Sign == Aries AND Moon.House > 5"

        result = benchmark(parse, formula)

        warning_us = get_threshold_us("parser", "medium", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Parser medium performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_parser_complex_regression(self, benchmark):
        """Parser complex formula should not regress beyond warning threshold"""
        formula = "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity"

        result = benchmark(parse, formula)

        warning_us = get_threshold_us("parser", "complex", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Parser complex performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )


# ============================================================================
# EVALUATOR REGRESSION TESTS
# ============================================================================


class TestEvaluatorRegression:
    """Regression tests for Evaluator performance"""

    def test_evaluator_simple_regression(self, benchmark):
        """Evaluator simple formula should not regress beyond warning threshold"""
        formula = "Sun.Sign"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("evaluator", "simple", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Evaluator simple performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_evaluator_medium_regression(self, benchmark):
        """Evaluator medium formula should not regress beyond warning threshold"""
        formula = "Sun.House IN [1,4,7,10] AND Moon.Dignity == Exaltation"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("evaluator", "medium", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Evaluator medium performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_evaluator_complex_regression(self, benchmark):
        """Evaluator complex formula should not regress beyond warning threshold"""
        formula = "Rulership IN planets.Dignity AND Sun.House IN [1,4,7,10]"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("evaluator", "complex", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"Evaluator complex performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )


# ============================================================================
# END-TO-END REGRESSION TESTS
# ============================================================================


class TestEndToEndRegression:
    """Regression tests for full pipeline performance"""

    def test_e2e_simple_regression(self, benchmark):
        """End-to-end simple formula should not regress beyond warning threshold"""
        formula = "Sun.Sign == Aries"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("end_to_end", "simple", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"End-to-end simple performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_e2e_medium_regression(self, benchmark):
        """End-to-end medium formula should not regress beyond warning threshold"""
        formula = "Sun.Sign == Aries AND Moon.House >= 1"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("end_to_end", "medium", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"End-to-end medium performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )

    def test_e2e_complex_regression(self, benchmark):
        """End-to-end complex formula should not regress beyond warning threshold"""
        formula = "(Sun.House IN [1,4,7,10] OR Moon.House IN [1,4,7,10]) AND (Rulership IN planets.Dignity OR Exaltation IN planets.Dignity)"

        result = benchmark(evaluate, formula, SAMPLE_CHART)

        warning_us = get_threshold_us("end_to_end", "complex", "warning")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < warning_us, (
            f"End-to-end complex performance regression: {mean_us:.2f}μs > {warning_us:.2f}μs"
        )


# ============================================================================
# CRITICAL THRESHOLD TESTS (CI/CD Failures)
# ============================================================================


class TestCriticalThresholds:
    """Tests that FAIL the build if critical performance thresholds exceeded

    These tests ensure that severe performance regressions are caught
    immediately and prevent deployment of broken code.
    """

    def test_critical_lexer_simple(self, benchmark):
        """CRITICAL: Lexer simple must stay under critical threshold"""
        result = benchmark(tokenize, "Sun.Sign")

        critical_us = get_threshold_us("lexer", "simple", "critical")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < critical_us, (
            f"❌ CRITICAL THRESHOLD EXCEEDED: Lexer simple {mean_us:.2f}μs > {critical_us:.2f}μs"
        )

    def test_critical_parser_complex(self, benchmark):
        """CRITICAL: Parser complex must stay under critical threshold"""
        result = benchmark(
            parse, "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity"
        )

        critical_us = get_threshold_us("parser", "complex", "critical")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < critical_us, (
            f"❌ CRITICAL THRESHOLD EXCEEDED: Parser complex {mean_us:.2f}μs > {critical_us:.2f}μs"
        )

    def test_critical_evaluator_complex(self, benchmark):
        """CRITICAL: Evaluator complex must stay under critical threshold"""
        result = benchmark(
            evaluate,
            "Rulership IN planets.Dignity AND (Sun.House IN [1,4,7,10] OR Moon.House IN [1,4,7,10])",
            SAMPLE_CHART,
        )

        critical_us = get_threshold_us("evaluator", "complex", "critical")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < critical_us, (
            f"❌ CRITICAL THRESHOLD EXCEEDED: Evaluator complex {mean_us:.2f}μs > {critical_us:.2f}μs"
        )

    def test_critical_e2e_complex(self, benchmark):
        """CRITICAL: End-to-end complex must stay under critical threshold"""
        formula = "(Sun.House IN [1,4,7,10]) AND (Moon.House IN [1,4,7,10]) AND (Rulership IN planets.Dignity)"
        result = benchmark(evaluate, formula, SAMPLE_CHART)

        critical_us = get_threshold_us("end_to_end", "complex", "critical")
        mean_us = benchmark.stats["mean"] * 1_000_000

        assert mean_us < critical_us, (
            f"❌ CRITICAL THRESHOLD EXCEEDED: End-to-end complex {mean_us:.2f}μs > {critical_us:.2f}μs"
        )


# ============================================================================
# THROUGHPUT REGRESSION TESTS
# ============================================================================


class TestThroughputRegression:
    """Regression tests for system throughput"""

    def test_throughput_batch_10_formulas(self, benchmark):
        """Throughput should handle 10 different formulas efficiently"""
        formulas = [
            "Sun.Sign == Aries",
            "Moon.House > 5",
            "Mercury.Retrograde == True",
            "Venus.Dignity == Exaltation",
            "Mars.House IN [1,4,7,10]",
            "Jupiter.Degree >= 20",
            "Saturn.Sign == Libra",
            "Retrograde IN planets.Retrograde",
            "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity",
            "(Sun.House == 1 OR Moon.House == 1) AND Mars.House == 4",
        ]

        def batch_eval():
            return [evaluate(f, SAMPLE_CHART) for f in formulas]

        result = benchmark(batch_eval)

        # Throughput check: should process 10 formulas quickly
        mean_us = benchmark.stats["mean"] * 1_000_000
        avg_per_formula = mean_us / 10

        # Use stress.different_formulas threshold
        warning_us = THRESHOLDS["stress"]["different_formulas"]["warning"]

        assert avg_per_formula < warning_us, (
            f"Throughput regression: avg {avg_per_formula:.2f}μs/formula > {warning_us:.2f}μs"
        )


# ============================================================================
# BASELINE COMPARISON UTILITIES
# ============================================================================


@pytest.fixture
def baseline_comparison():
    """Fixture to compare current run against baseline

    Usage:
        def test_my_performance(benchmark, baseline_comparison):
            result = benchmark(my_function)
            baseline_comparison.assert_no_regression(benchmark, 'my_test_name')
    """

    class BaselineComparison:
        def assert_no_regression(
            self, benchmark_result, test_name: str, threshold: float = 1.20
        ):
            """Assert that performance has not regressed by more than threshold

            Args:
                benchmark_result: pytest-benchmark result object
                test_name: Name of the test for reporting
                threshold: Max allowed regression factor (1.20 = 20% slower)
            """
            # pytest-benchmark automatically compares to saved baseline
            # This is a placeholder for custom comparison logic if needed
            pass

    return BaselineComparison()


if __name__ == "__main__":
    print("Performance Regression Test Suite")
    print("=" * 50)
    print()
    print("Run with:")
    print("  pytest tests/test_performance_regression.py --benchmark-only")
    print()
    print("Compare to baseline:")
    print(
        "  pytest tests/test_performance_regression.py --benchmark-only --benchmark-compare=stage2_baseline"
    )
    print()
    print("Generate HTML report:")
    print(
        "  pytest tests/test_performance_regression.py --benchmark-only --benchmark-histogram"
    )
