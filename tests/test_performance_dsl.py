"""
DSL Performance Benchmarks - Stage 2 Task 2.2

Benchmark tests using pytest-benchmark для измерения
производительности DSL компонентов.

Запуск:
    pytest tests/test_performance_dsl.py --benchmark-only -v
    pytest tests/test_performance_dsl.py --benchmark-only --benchmark-save=baseline
    pytest-benchmark compare baseline --csv=performance_comparison.csv

Результаты:
    - .benchmarks/ directory
    - performance_comparison.csv
"""

import pytest
from src.dsl.lexer import tokenize
from src.dsl.parser import parse
from src.dsl.evaluator import evaluate


# ============================================================================
# TEST DATA
# ============================================================================

SAMPLE_CHART = {
    "planets": {
        "Sun": {
            "Sign": "Leo",
            "House": 5,
            "Degree": 15.5,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Moon": {
            "Sign": "Cancer",
            "House": 4,
            "Degree": 10.2,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Mercury": {
            "Sign": "Virgo",
            "House": 6,
            "Degree": 20.0,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Venus": {
            "Sign": "Libra",
            "House": 7,
            "Degree": 5.8,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Mars": {
            "Sign": "Aries",
            "House": 1,
            "Degree": 25.3,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Jupiter": {
            "Sign": "Pisces",
            "House": 12,
            "Degree": 12.7,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Saturn": {
            "Sign": "Capricorn",
            "House": 10,
            "Degree": 22.1,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Uranus": {
            "Sign": "Taurus",
            "House": 2,
            "Degree": 8.9,
            "Dignity": "Peregrine",
            "Retrograde": True,
        },
        "Neptune": {
            "Sign": "Pisces",
            "House": 12,
            "Degree": 18.4,
            "Dignity": "Rulership",
            "Retrograde": False,
        },
        "Pluto": {
            "Sign": "Capricorn",
            "House": 10,
            "Degree": 15.6,
            "Dignity": "Peregrine",
            "Retrograde": False,
        },
    }
}


# ============================================================================
# LEXER BENCHMARKS
# ============================================================================


@pytest.mark.benchmark(group="lexer-simple")
def test_lexer_simple_property(benchmark):
    """Benchmark: Simple property access tokenization"""
    result = benchmark(tokenize, "Sun.Sign")
    assert len(result) > 0


@pytest.mark.benchmark(group="lexer-simple")
def test_lexer_simple_comparison(benchmark):
    """Benchmark: Simple comparison tokenization"""
    result = benchmark(tokenize, "Sun.Sign == Aries")
    assert len(result) > 0


@pytest.mark.benchmark(group="lexer-medium")
def test_lexer_medium_and_operator(benchmark):
    """Benchmark: AND operator tokenization"""
    result = benchmark(tokenize, "Sun.Sign == Aries AND Moon.House == 1")
    assert len(result) > 0


@pytest.mark.benchmark(group="lexer-medium")
def test_lexer_medium_in_operator(benchmark):
    """Benchmark: IN operator with list tokenization"""
    result = benchmark(tokenize, "Mercury.House IN [3, 6, 9, 12]")
    assert len(result) > 0


@pytest.mark.benchmark(group="lexer-complex")
def test_lexer_complex_nested(benchmark):
    """Benchmark: Complex nested formula tokenization"""
    result = benchmark(
        tokenize, "Sun.Sign == Leo AND Moon.Sign == Cancer AND Mercury.House == 3"
    )
    assert len(result) > 0


@pytest.mark.benchmark(group="lexer-complex")
def test_lexer_complex_aggregator(benchmark):
    """Benchmark: Aggregator formula tokenization"""
    result = benchmark(
        tokenize, "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity"
    )
    assert len(result) > 0


# ============================================================================
# PARSER BENCHMARKS
# ============================================================================


@pytest.mark.benchmark(group="parser-simple")
def test_parser_simple_property(benchmark):
    """Benchmark: Simple property parsing"""
    result = benchmark(parse, "Sun.Sign")
    assert result is not None


@pytest.mark.benchmark(group="parser-simple")
def test_parser_simple_comparison(benchmark):
    """Benchmark: Simple comparison parsing"""
    result = benchmark(parse, "Sun.Sign == Aries")
    assert result is not None


@pytest.mark.benchmark(group="parser-medium")
def test_parser_medium_and_operator(benchmark):
    """Benchmark: AND operator parsing"""
    result = benchmark(parse, "Sun.Sign == Aries AND Moon.House == 1")
    assert result is not None


@pytest.mark.benchmark(group="parser-medium")
def test_parser_medium_in_operator(benchmark):
    """Benchmark: IN operator with list parsing"""
    result = benchmark(parse, "Mercury.House IN [3, 6, 9, 12]")
    assert result is not None


@pytest.mark.benchmark(group="parser-complex")
def test_parser_complex_nested(benchmark):
    """Benchmark: Complex nested formula parsing"""
    result = benchmark(
        parse, "Sun.Sign == Leo AND Moon.Sign == Cancer AND Mercury.House == 3"
    )
    assert result is not None


@pytest.mark.benchmark(group="parser-complex")
def test_parser_complex_aggregator(benchmark):
    """Benchmark: Aggregator formula parsing"""
    result = benchmark(
        parse, "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity"
    )
    assert result is not None


# ============================================================================
# EVALUATOR BENCHMARKS
# ============================================================================


@pytest.mark.benchmark(group="evaluator-simple")
def test_evaluator_simple_property(benchmark):
    """Benchmark: Simple property evaluation"""
    result = benchmark(evaluate, "Sun.Sign == Leo", SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="evaluator-simple")
def test_evaluator_simple_comparison(benchmark):
    """Benchmark: Simple comparison evaluation"""
    result = benchmark(evaluate, "Mars.Degree > 20", SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="evaluator-medium")
def test_evaluator_medium_and_operator(benchmark):
    """Benchmark: AND operator evaluation"""
    result = benchmark(
        evaluate, "Sun.Sign == Leo AND Moon.Sign == Cancer", SAMPLE_CHART
    )
    assert result is True


@pytest.mark.benchmark(group="evaluator-medium")
def test_evaluator_medium_in_operator(benchmark):
    """Benchmark: IN operator evaluation"""
    result = benchmark(evaluate, "Jupiter.House IN [9, 10, 11, 12]", SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="evaluator-complex")
def test_evaluator_complex_nested(benchmark):
    """Benchmark: Complex nested formula evaluation"""
    formula = "Sun.Sign == Leo AND Moon.Sign == Cancer AND Mercury.Sign == Virgo"
    result = benchmark(evaluate, formula, SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="evaluator-complex")
def test_evaluator_complex_aggregator(benchmark):
    """Benchmark: Aggregator formula evaluation"""
    formula = "Rulership IN planets.Dignity"
    result = benchmark(evaluate, formula, SAMPLE_CHART)
    assert result is True


# ============================================================================
# END-TO-END BENCHMARKS
# ============================================================================


@pytest.mark.benchmark(group="end-to-end")
def test_e2e_simple(benchmark):
    """Benchmark: Simple formula end-to-end"""
    result = benchmark(evaluate, "Sun.Sign == Leo", SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="end-to-end")
def test_e2e_medium(benchmark):
    """Benchmark: Medium complexity formula end-to-end"""
    result = benchmark(evaluate, "Sun.Sign == Leo AND Moon.House == 4", SAMPLE_CHART)
    assert result is True


@pytest.mark.benchmark(group="end-to-end")
def test_e2e_complex(benchmark):
    """Benchmark: Complex formula end-to-end"""
    formula = "Sun.Sign == Leo AND Moon.Sign == Cancer AND Mercury.Sign == Virgo AND Venus.Sign == Libra"
    result = benchmark(evaluate, formula, SAMPLE_CHART)
    assert result is True


# ============================================================================
# STRESS TESTS
# ============================================================================


@pytest.mark.benchmark(group="stress")
def test_stress_multiple_evaluations(benchmark):
    """Benchmark: 100 evaluations of same formula"""

    def run_multiple():
        for _ in range(100):
            evaluate("Sun.Sign == Leo", SAMPLE_CHART)

    benchmark(run_multiple)


@pytest.mark.benchmark(group="stress")
def test_stress_different_formulas(benchmark):
    """Benchmark: 10 evaluations of different formulas"""
    formulas = [
        "Sun.Sign == Leo",
        "Moon.House == 4",
        "Mars.Retrograde == False",
        "Venus.Degree < 10",
        "Jupiter.Dignity == Rulership",
        "Saturn.House == 10",
        "Uranus.Retrograde == True",
        "Neptune.Sign == Pisces",
        "Pluto.Degree > 15",
        "Mercury.House == 6",
    ]

    def run_different():
        for formula in formulas:
            evaluate(formula, SAMPLE_CHART)

    benchmark(run_different)


# ============================================================================
# CACHE SIMULATION
# ============================================================================

# Cache для симуляции AST caching
_AST_CACHE = {}


def evaluate_with_cache(formula: str, chart_data):
    """Simulate AST caching"""
    if formula not in _AST_CACHE:
        _AST_CACHE[formula] = parse(formula)

    from src.dsl.evaluator import Evaluator

    return Evaluator(chart_data).evaluate(_AST_CACHE[formula])


@pytest.mark.benchmark(group="optimization")
def test_with_caching(benchmark):
    """Benchmark: Evaluation with AST caching"""
    _AST_CACHE.clear()
    result = benchmark(
        evaluate_with_cache, "Sun.Sign == Leo AND Moon.House == 4", SAMPLE_CHART
    )
    assert result is True


@pytest.mark.benchmark(group="optimization")
def test_without_caching(benchmark):
    """Benchmark: Evaluation without AST caching"""
    result = benchmark(evaluate, "Sun.Sign == Leo AND Moon.House == 4", SAMPLE_CHART)
    assert result is True
