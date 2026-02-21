"""
Tests for DSL cache module (AST caching)

Tests LRU cache functionality, performance improvements,
and cache statistics.
"""

import pytest
from src.dsl.cache import (
    ASTCache,
    parse_cached,
    clear_cache,
    get_cache_stats,
    set_cache_size,
)
from src.dsl.parser import NodeType


class TestASTCache:
    """Test ASTCache class"""

    def test_create_cache(self):
        """Test cache creation"""
        cache = ASTCache(maxsize=100)
        assert cache.maxsize == 100
        assert cache.stats()["size"] == 0

    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = ASTCache()
        result = cache.get("Sun.Sign == Aries")
        assert result is None
        assert cache.stats()["misses"] == 1
        assert cache.stats()["hits"] == 0

    def test_cache_hit(self):
        """Test cache hit returns cached AST"""
        cache = ASTCache()
        ast = parse_cached("Sun.Sign == Aries", use_cache=False)
        cache.set("Sun.Sign == Aries", ast)

        result = cache.get("Sun.Sign == Aries")
        assert result is not None
        assert result.type == NodeType.COMPARISON
        assert cache.stats()["hits"] == 1

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = ASTCache(maxsize=2)

        # Fill cache
        ast1 = parse_cached("Sun.Sign == Aries", use_cache=False)
        ast2 = parse_cached("Moon.Sign == Taurus", use_cache=False)
        cache.set("formula1", ast1)
        cache.set("formula2", ast2)
        assert cache.stats()["size"] == 2

        # Add third item - should evict oldest
        ast3 = parse_cached("Mars.Sign == Leo", use_cache=False)
        cache.set("formula3", ast3)

        assert cache.stats()["size"] == 2
        assert cache.get("formula1") is None  # Evicted
        assert cache.get("formula2") is not None  # Still there
        assert cache.get("formula3") is not None  # Just added

    def test_lru_update(self):
        """Test LRU updates when accessing cached items"""
        cache = ASTCache(maxsize=2)

        ast1 = parse_cached("Sun.Sign == Aries", use_cache=False)
        ast2 = parse_cached("Moon.Sign == Taurus", use_cache=False)
        cache.set("formula1", ast1)
        cache.set("formula2", ast2)

        # Access formula1 to make it most recent
        cache.get("formula1")

        # Add third item - should evict formula2 (least recent)
        ast3 = parse_cached("Mars.Sign == Leo", use_cache=False)
        cache.set("formula3", ast3)

        assert cache.get("formula1") is not None  # Most recent, not evicted
        assert cache.get("formula2") is None  # Evicted
        assert cache.get("formula3") is not None  # Just added

    def test_cache_clear(self):
        """Test cache clearing"""
        cache = ASTCache()
        ast = parse_cached("Sun.Sign == Aries", use_cache=False)
        cache.set("formula1", ast)

        cache.clear()
        assert cache.stats()["size"] == 0
        assert cache.stats()["hits"] == 0
        assert cache.stats()["misses"] == 0

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = ASTCache(maxsize=100)
        ast = parse_cached("Sun.Sign == Aries", use_cache=False)

        # Miss
        cache.get("formula1")
        # Hit
        cache.set("formula1", ast)
        cache.get("formula1")
        cache.get("formula1")

        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["maxsize"] == 100
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2 / 3)


class TestParseCached:
    """Test parse_cached function"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_parse_cached_first_call(self):
        """Test first parse is cached"""
        ast = parse_cached("Sun.Sign == Aries")
        assert ast is not None
        assert ast.type == NodeType.COMPARISON

        stats = get_cache_stats()
        assert stats["size"] == 1
        assert stats["misses"] == 1

    def test_parse_cached_subsequent_call(self):
        """Test subsequent parse uses cache"""
        ast1 = parse_cached("Sun.Sign == Aries")
        ast2 = parse_cached("Sun.Sign == Aries")

        # Should return same AST object (from cache)
        assert ast1 is ast2

        stats = get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_parse_cached_different_formulas(self):
        """Test different formulas create different cache entries"""
        ast1 = parse_cached("Sun.Sign == Aries")
        ast2 = parse_cached("Moon.Sign == Taurus")

        assert ast1 is not ast2
        assert get_cache_stats()["size"] == 2

    def test_parse_cached_with_cache_disabled(self):
        """Test parse_cached with use_cache=False"""
        ast1 = parse_cached("Sun.Sign == Aries", use_cache=False)
        ast2 = parse_cached("Sun.Sign == Aries", use_cache=False)

        # Should return different AST objects (no caching)
        assert ast1 is not ast2
        assert get_cache_stats()["size"] == 0


class TestCacheFunctions:
    """Test module-level cache functions"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_clear_cache(self):
        """Test global cache clearing"""
        parse_cached("Sun.Sign == Aries")
        assert get_cache_stats()["size"] == 1

        clear_cache()
        assert get_cache_stats()["size"] == 0

    def test_get_cache_stats(self):
        """Test cache statistics retrieval"""
        parse_cached("Sun.Sign == Aries")
        parse_cached("Sun.Sign == Aries")

        stats = get_cache_stats()
        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_set_cache_size(self):
        """Test changing cache size"""
        parse_cached("Sun.Sign == Aries")
        assert get_cache_stats()["maxsize"] == 1000

        set_cache_size(5000)
        assert get_cache_stats()["maxsize"] == 5000
        # Setting size clears cache
        assert get_cache_stats()["size"] == 0


class TestCachePerformance:
    """Test cache performance benefits"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_cache_hit_rate(self):
        """Test cache achieves high hit rate with repeated formulas"""
        formulas = [
            "Sun.Sign == Aries",
            "Moon.Sign == Taurus",
            "Mars.Sign == Leo",
        ]

        # Parse each formula 10 times
        for _ in range(10):
            for formula in formulas:
                parse_cached(formula)

        stats = get_cache_stats()
        # 3 formulas × 10 repetitions = 30 parses
        # First 3 are misses, remaining 27 are hits
        assert stats["misses"] == 3
        assert stats["hits"] == 27
        assert stats["hit_rate"] == pytest.approx(0.9)

    def test_cache_size_limit(self):
        """Test cache respects size limit"""
        set_cache_size(10)

        # Parse 20 different formulas
        for i in range(20):
            parse_cached(f"Sun.Degree == {i}")

        stats = get_cache_stats()
        # Cache should contain only last 10
        assert stats["size"] == 10


class TestEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Clear cache before each test"""
        clear_cache()

    def test_empty_formula(self):
        """Test caching empty formula"""
        with pytest.raises(Exception):  # Should raise parser error
            parse_cached("")

    def test_invalid_formula(self):
        """Test caching invalid formula"""
        with pytest.raises(Exception):  # Should raise parser error
            parse_cached("invalid formula !!!!")

    def test_very_long_formula(self):
        """Test caching very long formula"""
        formula = " OR ".join([f"Sun.Degree == {i}" for i in range(100)])
        ast = parse_cached(formula)
        assert ast is not None

        # Should be cached
        ast2 = parse_cached(formula)
        assert ast is ast2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
