"""
DSL Batch Processing - efficient evaluation of multiple formulas

Provides batch evaluation for multiple formulas on the same chart,
with automatic AST caching and parallel-friendly design.

Performance benefits:
- Parse once, evaluate many times
- Automatic AST caching
- Reduced overhead for multiple formulas

Usage:
    from src.dsl.batch import batch_evaluate, BatchEvaluator

    chart = {...}  # Your chart data
    formulas = [
        "Sun.Sign == Aries",
        "Moon.House == 7",
        "Mars.Retrograde == True"
    ]

    # Simple API
    results = batch_evaluate(formulas, chart)
    # results = [True, False, True]

    # Advanced API with statistics
    evaluator = BatchEvaluator(chart)
    results = evaluator.evaluate_batch(formulas)
    stats = evaluator.get_stats()
"""

from typing import List, Dict, Any
from time import perf_counter
from src.dsl.cache import parse_cached
from src.dsl.evaluator import Evaluator


class BatchEvaluator:
    """
    Batch evaluator for multiple formulas on single chart

    Optimizations:
    - Reuses single Evaluator instance
    - Automatic AST caching via parse_cached
    - Tracks performance statistics

    Attributes:
        chart_data: Chart data for evaluation
        evaluator: Reusable Evaluator instance
        _stats: Performance statistics
    """

    def __init__(self, chart_data: Dict[str, Any]):
        """
        Initialize batch evaluator

        Args:
            chart_data: Natal chart data
        """
        self.chart_data = chart_data
        self.evaluator = Evaluator(chart_data)
        self._stats = {
            "total_formulas": 0,
            "total_time_ms": 0.0,
            "avg_time_ms": 0.0,
            "cache_enabled": True,
        }

    def evaluate_batch(self, formulas: List[str], use_cache: bool = True) -> List[Any]:
        """
        Evaluate multiple formulas in batch

        Args:
            formulas: List of formula strings
            use_cache: Whether to use AST cache (default: True)

        Returns:
            List of evaluation results (same order as input)

        Raises:
            ParserError: If any formula is invalid
            EvaluatorError: If evaluation fails

        Examples:
            >>> evaluator = BatchEvaluator(chart)
            >>> formulas = ["Sun.Sign == Aries", "Moon.House > 6"]
            >>> results = evaluator.evaluate_batch(formulas)
            >>> # results = [True, False]
        """
        start_time = perf_counter()

        # Parse all formulas (with caching)
        asts = [parse_cached(formula, use_cache=use_cache) for formula in formulas]

        # Evaluate all ASTs
        results = []
        for ast in asts:
            result = self.evaluator.evaluate(ast)
            results.append(result)

        # Update statistics
        elapsed_ms = (perf_counter() - start_time) * 1000
        self._stats["total_formulas"] += len(formulas)
        self._stats["total_time_ms"] += elapsed_ms

        # Avoid division by zero
        if self._stats["total_formulas"] > 0:
            self._stats["avg_time_ms"] = (
                self._stats["total_time_ms"] / self._stats["total_formulas"]
            )
        else:
            self._stats["avg_time_ms"] = 0.0

        self._stats["cache_enabled"] = use_cache

        return results

    def evaluate_single(self, formula: str, use_cache: bool = True) -> Any:
        """
        Evaluate single formula (convenience method)

        Args:
            formula: Formula string
            use_cache: Whether to use AST cache

        Returns:
            Evaluation result

        Examples:
            >>> result = evaluator.evaluate_single("Sun.Sign == Aries")
        """
        return self.evaluate_batch([formula], use_cache=use_cache)[0]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get evaluation statistics

        Returns:
            Dictionary with performance stats:
            - total_formulas: Number of formulas evaluated
            - total_time_ms: Total time in milliseconds
            - avg_time_ms: Average time per formula
            - cache_enabled: Whether cache was used

        Examples:
            >>> stats = evaluator.get_stats()
            >>> print(f"Avg: {stats['avg_time_ms']:.2f}ms per formula")
        """
        return self._stats.copy()

    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = {
            "total_formulas": 0,
            "total_time_ms": 0.0,
            "avg_time_ms": 0.0,
            "cache_enabled": self._stats["cache_enabled"],
        }


def batch_evaluate(
    formulas: List[str], chart_data: Dict[str, Any], use_cache: bool = True
) -> List[Any]:
    """
    Evaluate multiple formulas in batch (simple API)

    Args:
        formulas: List of formula strings
        chart_data: Natal chart data
        use_cache: Whether to use AST cache (default: True)

    Returns:
        List of evaluation results

    Examples:
        >>> chart = {...}
        >>> formulas = ["Sun.Sign == Aries", "Moon.House == 7"]
        >>> results = batch_evaluate(formulas, chart)
        >>> # results = [True, False]
    """
    evaluator = BatchEvaluator(chart_data)
    return evaluator.evaluate_batch(formulas, use_cache=use_cache)


def evaluate_all_true(
    formulas: List[str], chart_data: Dict[str, Any], use_cache: bool = True
) -> bool:
    """
    Check if ALL formulas evaluate to True

    Args:
        formulas: List of formula strings
        chart_data: Natal chart data
        use_cache: Whether to use cache

    Returns:
        True if all formulas are True, False otherwise

    Examples:
        >>> formulas = ["Sun.Sign == Aries", "Moon.House == 7"]
        >>> all_true = evaluate_all_true(formulas, chart)
    """
    results = batch_evaluate(formulas, chart_data, use_cache=use_cache)
    return all(results)


def evaluate_any_true(
    formulas: List[str], chart_data: Dict[str, Any], use_cache: bool = True
) -> bool:
    """
    Check if ANY formula evaluates to True

    Args:
        formulas: List of formula strings
        chart_data: Natal chart data
        use_cache: Whether to use cache

    Returns:
        True if any formula is True, False otherwise

    Examples:
        >>> formulas = ["Sun.Sign == Aries", "Moon.Sign == Taurus"]
        >>> any_true = evaluate_any_true(formulas, chart)
    """
    results = batch_evaluate(formulas, chart_data, use_cache=use_cache)
    return any(results)


__all__ = [
    "BatchEvaluator",
    "batch_evaluate",
    "evaluate_all_true",
    "evaluate_any_true",
]
