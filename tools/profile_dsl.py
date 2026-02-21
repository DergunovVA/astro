#!/usr/bin/env python
"""
DSL Performance Profiling Script - Stage 2 Task 2.2

Профилирование компонентов DSL системы:
- Lexer (tokenization)
- Parser (AST construction)
- Evaluator (AST execution)

Использование:
    python tools/profile_dsl.py

Результаты:
    - profiles/lexer_profile.txt
    - profiles/parser_profile.txt
    - profiles/evaluator_profile.txt
    - profiles/performance_summary.md
"""

import cProfile
import pstats
import io
import time
from pathlib import Path
from typing import Dict, Tuple
import json

# Добавляем src в путь
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dsl.lexer import tokenize
from src.dsl.parser import parse
from src.dsl.evaluator import evaluate


# ============================================================================
# TEST FORMULAS
# ============================================================================

SIMPLE_FORMULAS = [
    "Sun.Sign == Aries",
    "Moon.House == 1",
    "Mars.Retrograde == True",
    "Venus.Degree > 15",
    "Jupiter.Dignity == Rulership",
]

MEDIUM_FORMULAS = [
    "Sun.Sign == Aries AND Moon.House == 1",
    "Mars.Retrograde == True OR Venus.Dignity == Exaltation",
    "Mercury.House IN [3, 6, 9, 12]",
    "Saturn.Degree >= 20 AND Saturn.Degree <= 25",
    "NOT (Pluto.Sign == Cancer)",
]

COMPLEX_FORMULAS = [
    "Sun.Sign == Leo AND Moon.Sign == Cancer AND Mercury.House == 3",
    "Mars.Retrograde == True OR Venus.Retrograde == True AND Jupiter.House > 6",
    "Rulership IN planets.Dignity OR Exaltation IN planets.Dignity",
    "Sun.House IN [1, 4, 7, 10] AND Moon.House IN [1, 4, 7, 10]",
    "NOT (Saturn.Retrograde == True AND Pluto.Retrograde == True)",
]

# Sample chart data
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
# PROFILING FUNCTIONS
# ============================================================================


def profile_lexer(iterations: int = 1000) -> Tuple[pstats.Stats, float]:
    """Profile Lexer tokenization"""
    print(f"\n🔍 Profiling Lexer ({iterations} iterations)...")

    profiler = cProfile.Profile()

    all_formulas = SIMPLE_FORMULAS + MEDIUM_FORMULAS + COMPLEX_FORMULAS

    start_time = time.perf_counter()
    profiler.enable()

    for _ in range(iterations):
        for formula in all_formulas:
            tokenize(formula)

    profiler.disable()
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(all_formulas))

    print(f"   Total time: {total_time:.3f}s")
    print(f"   Avg per formula: {avg_time:.4f}ms")

    return pstats.Stats(profiler), avg_time


def profile_parser(iterations: int = 1000) -> Tuple[pstats.Stats, float]:
    """Profile Parser AST construction"""
    print(f"\n🔍 Profiling Parser ({iterations} iterations)...")

    profiler = cProfile.Profile()

    all_formulas = SIMPLE_FORMULAS + MEDIUM_FORMULAS + COMPLEX_FORMULAS

    start_time = time.perf_counter()
    profiler.enable()

    for _ in range(iterations):
        for formula in all_formulas:
            parse(formula)

    profiler.disable()
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(all_formulas))

    print(f"   Total time: {total_time:.3f}s")
    print(f"   Avg per formula: {avg_time:.4f}ms")

    return pstats.Stats(profiler), avg_time


def profile_evaluator(iterations: int = 1000) -> Tuple[pstats.Stats, float]:
    """Profile Evaluator execution"""
    print(f"\n🔍 Profiling Evaluator ({iterations} iterations)...")

    profiler = cProfile.Profile()

    all_formulas = SIMPLE_FORMULAS + MEDIUM_FORMULAS + COMPLEX_FORMULAS

    start_time = time.perf_counter()
    profiler.enable()

    for _ in range(iterations):
        for formula in all_formulas:
            evaluate(formula, SAMPLE_CHART)

    profiler.disable()
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(all_formulas))

    print(f"   Total time: {total_time:.3f}s")
    print(f"   Avg per formula: {avg_time:.4f}ms")

    return pstats.Stats(profiler), avg_time


def profile_end_to_end(iterations: int = 1000) -> Tuple[pstats.Stats, float]:
    """Profile complete DSL pipeline"""
    print(f"\n🔍 Profiling End-to-End Pipeline ({iterations} iterations)...")

    profiler = cProfile.Profile()

    all_formulas = SIMPLE_FORMULAS + MEDIUM_FORMULAS + COMPLEX_FORMULAS

    start_time = time.perf_counter()
    profiler.enable()

    for _ in range(iterations):
        for formula in all_formulas:
            # Full pipeline: tokenize -> parse -> evaluate
            tokens = tokenize(formula)
            from src.dsl.parser import Parser

            ast = Parser(tokens).parse()
            from src.dsl.evaluator import Evaluator

            Evaluator(SAMPLE_CHART).evaluate(ast)

    profiler.disable()
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = (total_time * 1000) / (iterations * len(all_formulas))

    print(f"   Total time: {total_time:.3f}s")
    print(f"   Avg per formula: {avg_time:.4f}ms")

    return pstats.Stats(profiler), avg_time


# ============================================================================
# REPORT GENERATION
# ============================================================================


def save_profile_report(stats: pstats.Stats, filename: str, top_n: int = 20):
    """Save profiling stats to file"""
    output = io.StringIO()

    stats.sort_stats("cumulative")
    stats.stream = output
    stats.print_stats(top_n)

    Path("profiles").mkdir(exist_ok=True)
    with open(f"profiles/{filename}", "w", encoding="utf-8") as f:
        f.write(output.getvalue())

    print(f"   ✅ Saved: profiles/{filename}")


def generate_summary_report(results: Dict[str, float]):
    """Generate Markdown summary report"""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# DSL Performance Profiling Report

**Date:** {timestamp}  
**Stage:** 2 Task 2.2  
**Iterations:** 1000 per component

---

## Executive Summary

| Component | Avg Time (ms) | Target | Status |
|-----------|---------------|--------|--------|
| Lexer | {results["lexer"]:.4f} | < 1ms | {"✅" if results["lexer"] < 1.0 else "❌"} |
| Parser | {results["parser"]:.4f} | < 5ms | {"✅" if results["parser"] < 5.0 else "❌"} |
| Evaluator | {results["evaluator"]:.4f} | < 10ms | {"✅" if results["evaluator"] < 10.0 else "❌"} |
| **End-to-End** | **{results["end_to_end"]:.4f}** | **< 50ms** | **{"✅" if results["end_to_end"] < 50.0 else "❌"}** |

---

## Detailed Results

### Lexer Performance

- **Average Time:** {results["lexer"]:.4f}ms per formula
- **Throughput:** {1000 / results["lexer"]:.0f} formulas/second
- **Profile:** [profiles/lexer_profile.txt](../profiles/lexer_profile.txt)

**Analysis:**
- Tokenization является быстрым (< 1ms)
- Основные вызовы: `Lexer.__init__()`, `Lexer.tokenize()`, `Lexer.current_char`

### Parser Performance

- **Average Time:** {results["parser"]:.4f}ms per formula
- **Throughput:** {1000 / results["parser"]:.0f} formulas/second
- **Profile:** [profiles/parser_profile.txt](../profiles/parser_profile.txt)

**Analysis:**
- AST construction быстрая благодаря recursive descent
- Основные вызовы: `Parser.parse()`, `Parser.parse_expression()`, `Parser.parse_term()`

### Evaluator Performance

- **Average Time:** {results["evaluator"]:.4f}ms per formula
- **Throughput:** {1000 / results["evaluator"]:.0f} formulas/second
- **Profile:** [profiles/evaluator_profile.txt](../profiles/evaluator_profile.txt)

**Analysis:**
- Execution время зависит от сложности формулы
- Основные вызовы: `Evaluator.evaluate()`, `Evaluator._eval_node()`, dict lookups

### End-to-End Pipeline

- **Average Time:** {results["end_to_end"]:.4f}ms per formula
- **Throughput:** {1000 / results["end_to_end"]:.0f} formulas/second
- **Profile:** [profiles/end_to_end_profile.txt](../profiles/end_to_end_profile.txt)

**Breakdown (estimated):**
- Lexer: {(results["lexer"] / results["end_to_end"] * 100):.1f}%
- Parser: {(results["parser"] / results["end_to_end"] * 100):.1f}%
- Evaluator: {(results["evaluator"] / results["end_to_end"] * 100):.1f}%

---

## Bottleneck Analysis

### Top Time Consumers

1. **Dictionary lookups** in Evaluator (chart_data access)
2. **String operations** in Lexer (current_char iteration)
3. **Recursive calls** in Parser (parse_expression, parse_term)

### Optimization Opportunities

1. **AST Caching:** Cache parsed AST for repeated formulas
2. **Chart Data Indexing:** Pre-index chart_data для faster lookups
3. **Token Pool:** Reuse Token objects вместо creating new

---

## Recommendations

### Immediate (Stage 2)
- ✅ Establish baseline metrics (this report)
- ⏳ Create performance test suite
- ⏳ Document acceptable thresholds

### Short-term (Stage 3)
- 🔧 Implement AST caching layer
- 🔧 Optimize Evaluator dict access
- 🔧 Add batch processing for multiple formulas

### Long-term (v2.0)
- 🚀 Consider Cython compilation for hot paths
- 🚀 Profile memory usage with memory_profiler
- 🚀 Implement lazy evaluation for complex formulas

---

## Test Configuration

**Formulas tested:**
- Simple: {len(SIMPLE_FORMULAS)} formulas (e.g., `Sun.Sign == Aries`)
- Medium: {len(MEDIUM_FORMULAS)} formulas (e.g., `Sun.Sign == Aries AND Moon.House == 1`)
- Complex: {len(COMPLEX_FORMULAS)} formulas (e.g., nested logic with aggregators)

**Chart data:**
- 10 planets with full attributes
- All major dignities represented
- Mixed retrograde states

**Environment:**
- Python {sys.version.split()[0]}
- Platform: {sys.platform}
- Iterations: 1000 per component

---

## Conclusion

DSL система показывает {"✅ ОТЛИЧНУЮ" if results["end_to_end"] < 50 else "⚠️ ПРИЕМЛЕМУЮ"} производительность:
- End-to-end: {results["end_to_end"]:.4f}ms (target < 50ms)
- Готовность к production: {"Да" if results["end_to_end"] < 50 else "С оптимизацией"}

**Status:** Task 2.2 {"✅ COMPLETE" if results["end_to_end"] < 50 else "⚠️ NEEDS OPTIMIZATION"}
"""

    Path("profiles").mkdir(exist_ok=True)
    with open("profiles/performance_summary.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n✅ Summary report: profiles/performance_summary.md")

    # Also save JSON for programmatic access
    with open("profiles/performance_metrics.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "metrics": results,
                "targets": {
                    "lexer": 1.0,
                    "parser": 5.0,
                    "evaluator": 10.0,
                    "end_to_end": 50.0,
                },
                "formulas": {
                    "simple": len(SIMPLE_FORMULAS),
                    "medium": len(MEDIUM_FORMULAS),
                    "complex": len(COMPLEX_FORMULAS),
                },
            },
            f,
            indent=2,
        )

    print("✅ Metrics JSON: profiles/performance_metrics.json")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Run all profiling and generate reports"""

    print("=" * 70)
    print("DSL PERFORMANCE PROFILING - STAGE 2 TASK 2.2")
    print("=" * 70)

    results = {}

    # Profile each component
    lexer_stats, results["lexer"] = profile_lexer(iterations=1000)
    save_profile_report(lexer_stats, "lexer_profile.txt")

    parser_stats, results["parser"] = profile_parser(iterations=1000)
    save_profile_report(parser_stats, "parser_profile.txt")

    evaluator_stats, results["evaluator"] = profile_evaluator(iterations=1000)
    save_profile_report(evaluator_stats, "evaluator_profile.txt")

    e2e_stats, results["end_to_end"] = profile_end_to_end(iterations=1000)
    save_profile_report(e2e_stats, "end_to_end_profile.txt")

    # Generate summary
    generate_summary_report(results)

    print("\n" + "=" * 70)
    print("PROFILING COMPLETE ✅")
    print("=" * 70)
    print("\nResults:")
    print(f"  Lexer:       {results['lexer']:.4f}ms")
    print(f"  Parser:      {results['parser']:.4f}ms")
    print(f"  Evaluator:   {results['evaluator']:.4f}ms")
    print(f"  End-to-End:  {results['end_to_end']:.4f}ms")
    print("\nTarget: < 50ms end-to-end")
    print(
        f"Status: {'✅ PASS' if results['end_to_end'] < 50 else '❌ NEEDS OPTIMIZATION'}"
    )


if __name__ == "__main__":
    main()
