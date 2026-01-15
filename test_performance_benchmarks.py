"""
Performance benchmarks for input pipeline operations.

Run with: python -m pytest test_performance_benchmarks.py -v
"""

from datetime import datetime
from input_pipeline import normalize_input
from input_pipeline.parser_datetime import parse_date_time
from input_pipeline.resolver_city import resolve_city
from input_pipeline.resolver_timezone import make_aware, resolve_tz_name
from input_pipeline.cache import JsonCache
import tempfile
import os


class TestPerformanceBenchmarks:
    """Baseline performance benchmarks."""

    def test_parse_date_time_iso(self, benchmark):
        """ISO date parsing should be <1ms."""
        def parse():
            return parse_date_time("2000-01-15", "14:30:00")

        result = benchmark(parse)
        assert result.date_iso == "2000-01-15"

    def test_parse_date_time_european(self, benchmark):
        """European date parsing should be <1ms."""
        def parse():
            return parse_date_time("15.01.2000", "14:30:00")

        result = benchmark(parse)
        assert result.date_iso == "2000-01-15"

    def test_parse_date_time_text(self, benchmark):
        """Text date parsing should be <2ms."""
        def parse():
            return parse_date_time("15 Jan 2000", "14:30:00")

        result = benchmark(parse)
        assert result.date_iso == "2000-01-15"

    def test_resolve_city_alias_hit(self, benchmark):
        """City alias lookup (cache hit) should be <1ms."""
        def resolve():
            return resolve_city("Moscow")

        result = benchmark(resolve)
        assert result.name == "Moscow"

    def test_resolve_city_typo_correction(self, benchmark):
        """Typo detection should be <10ms."""
        def resolve():
            return resolve_city("Moskow")  # Typo correction via fuzzy match

        result = benchmark(resolve)
        assert result.name == "Moscow"

    def test_make_aware_timezone(self, benchmark):
        """Timezone localization should be <5ms."""
        naive = datetime(2000, 1, 15, 14, 30, 0)

        def localize():
            return make_aware(naive, "Europe/Moscow")

        local, utc, offset = benchmark(localize)
        assert utc.hour == 11  # Moscow UTC+3 in January

    def test_resolve_tz_name(self, benchmark):
        """Timezone name resolution should be <10ms."""
        def resolve():
            return resolve_tz_name(55.7558, 37.6173)

        result = benchmark(resolve)
        assert result == "Europe/Moscow"

    def test_cache_set_and_get(self, benchmark):
        """Cache operations should be <5ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "test_cache.json")
            cache = JsonCache(filepath=cache_file)

            def cache_ops():
                cache.set("moscow", {"name": "Moscow", "lat": 55.7558})
                return cache.get("moscow")

            result = benchmark(cache_ops)
            assert result["name"] == "Moscow"

    def test_normalize_input_full_pipeline_alias(self, benchmark):
        """Full pipeline with alias lookup should be <10ms."""
        def normalize():
            return normalize_input(
                date_str="2000-01-15",
                time_str="14:30",
                place_str="Moscow",
            )

        result = benchmark(normalize)
        assert result.place_name == "Moscow"

    def test_normalize_input_full_pipeline_with_warnings(self, benchmark):
        """Full pipeline with warnings should still be <10ms."""
        def normalize():
            return normalize_input(
                date_str="15.01.2000",  # European format (low confidence)
                time_str="14:30",
                place_str="Moscow",
                locale="de_DE",  # Hint for EU format
            )

        result = benchmark(normalize)
        assert result.place_name == "Moscow"
        assert len(result.warnings) >= 1  # Should have low confidence warning


# Manual baseline measurements (for reference)
BASELINE_TARGETS = {
    "parse_date_time (ISO)": "<1ms",
    "parse_date_time (EU)": "<2ms",
    "parse_date_time (Text)": "<5ms",
    "resolve_city (alias)": "<1ms",
    "resolve_city (typo)": "<50ms",  # fuzzy match slower but acceptable
    "make_aware (timezone)": "<10ms",
    "resolve_tz_name": "<10ms",
    "cache (set+get)": "<5ms",
    "normalize_input (full)": "<20ms",
}


def test_print_baselines():
    """Print baseline targets for documentation."""
    print("\n=== PERFORMANCE BASELINES ===\n")
    for operation, target in BASELINE_TARGETS.items():
        print(f"  {operation:<40} {target:>8}")
    print()
