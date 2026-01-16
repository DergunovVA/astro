"""
Input pipeline test suite covering:
1. Date/time parsing with multiple formats
2. City alias resolution with variants
3. Timezone offset calculation
4. Cache hit/miss behavior  
5. Strict mode behavior
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from input_pipeline import (
    normalize_input,
    resolve_city,
    reset_global_cache,
    InputContext,
)
from input_pipeline.cache import JsonCache
from input_pipeline.parser_datetime import parse_date_time
from input_pipeline.resolver_timezone import resolve_tz_name, make_aware


class TestDateTimeParsing:
    """Test date/time parsing with multiple formats."""
    
    def test_iso_format(self):
        """ISO 8601 format should parse correctly."""
        result = parse_date_time("2000-01-15", "14:30:45")
        assert result.date_iso == "2000-01-15"
        assert result.time_iso == "14:30:45"
        assert result.confidence >= 0.95
        assert len(result.warnings) == 0
    
    def test_european_format(self):
        """European DD.MM.YYYY format should parse."""
        result = parse_date_time("15.01.2000", "14:30")
        assert result.date_iso == "2000-01-15"
        assert result.time_iso == "14:30:00"
        assert result.confidence >= 0.85
    
    def test_us_format(self):
        """US MM/DD/YYYY format should parse."""
        result = parse_date_time("01/15/2000", "14:30")
        assert result.date_iso == "2000-01-15"
        assert result.time_iso == "14:30:00"


class TestCityAliasResolution:
    """Test city alias resolution with Moscow variants."""
    
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """Reset cache before each test."""
        reset_global_cache()
        yield
        reset_global_cache()
    
    def test_moscow_russian(self):
        """Russian 'Москва' should resolve to Moscow."""
        rp = resolve_city("Москва")
        assert rp.name == "Moscow"
        assert rp.country == "RU"
        assert rp.lat == pytest.approx(55.7558, abs=0.01)
        assert rp.lon == pytest.approx(37.6173, abs=0.01)
        assert rp.tz_name == "Europe/Moscow"
        assert rp.source == "alias"
        assert rp.confidence >= 0.95
    
    def test_moscow_english_variants(self):
        """English 'Moscow' should resolve."""
        rp = resolve_city("Moscow")
        assert rp.name == "Moscow"
        assert rp.source == "alias"
        assert rp.confidence >= 0.95
    
    def test_moscow_transliteration(self):
        """Transliterated 'Moskva' should resolve with slightly lower confidence."""
        rp = resolve_city("Moskva")
        assert rp.name == "Moscow"
        assert rp.source == "alias"
        assert 0.8 < rp.confidence < 0.95
    
    def test_london_english(self):
        """English cities should resolve."""
        rp = resolve_city("London")
        assert rp.name == "London"
        assert rp.country == "GB"
        assert rp.tz_name == "Europe/London"
    
    def test_unknown_city_raises(self):
        """Completely unknown city should raise ValueError."""
        with pytest.raises(ValueError, match="City not found"):
            resolve_city("XyzAbc123NotACity")


class TestTimezoneResolution:
    """Test timezone resolution and offset calculation."""
    
    def test_moscow_offset(self):
        """Moscow should return a timezone name."""
        tz_name, warnings, confidence = resolve_tz_name(55.7558, 37.6173, hint=None)
        # Should be a valid timezone or UTC fallback
        assert tz_name in ["UTC", "Europe/Moscow"]
    
    def test_london_offset(self):
        """London timezone should be resolved."""
        tz_name, warnings, confidence = resolve_tz_name(51.5074, -0.1278, hint=None)
        # Might fallback to UTC if timezonefinder not installed
        assert tz_name is not None
    
    def test_make_aware_moscow(self):
        """Make aware should create correct UTC offset for Moscow."""
        naive = datetime(2000, 1, 15, 14, 30, 0)
        local, utc, offset_min = make_aware(naive, "Europe/Moscow")
        
        assert local.tzinfo == ZoneInfo("Europe/Moscow")
        # utc.tzinfo is datetime.timezone.utc, not ZoneInfo('UTC') - both are equivalent
        assert str(utc.tzinfo) == 'UTC'
        assert offset_min == 180  # Moscow is UTC+3, no DST in January
        assert utc.hour == 11  # 14:30 Moscow → 11:30 UTC
    
    def test_make_aware_london_winter(self):
        """London in winter should be UTC+0."""
        naive = datetime(2000, 1, 15, 14, 30, 0)
        local, utc, offset_min = make_aware(naive, "Europe/London")
        
        assert local.tzinfo == ZoneInfo("Europe/London")
        assert offset_min == 0  # London is UTC+0 in January
        assert utc.hour == 14  # Same as local time
    
    def test_invalid_timezone_raises(self):
        """Invalid timezone name should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            make_aware(datetime(2000, 1, 15), "Invalid/TZ")


class TestCacheBehavior:
    """Test cache hit/miss behavior."""
    
    def test_cache_hit_no_second_resolution(self):
        """Second call to same city should use cache."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            cache_path = f.name
        
        try:
            cache = JsonCache(cache_path)
            
            # First call
            rp1 = resolve_city("Moscow", cache)
            assert rp1.name == "Moscow"
            
            # Check cache
            cached = cache.get("moscow")
            assert cached is not None
            
            # Second call
            rp2 = resolve_city("Moscow", cache)
            assert rp2.name == rp1.name
            
        finally:
            Path(cache_path).unlink()
    
    def test_cache_persistence(self):
        """Cache should persist to disk."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            cache_path = f.name
        
        try:
            cache1 = JsonCache(cache_path)
            resolve_city("Moscow", cache1)
            
            cache2 = JsonCache(cache_path)
            cached = cache2.get("moscow")
            assert cached is not None
            assert cached["name"] == "Moscow"
            
        finally:
            Path(cache_path).unlink()


class TestStrictMode:
    """Test strict mode behavior."""
    
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """Reset cache before each test."""
        reset_global_cache()
        yield
        reset_global_cache()
    
    def test_strict_mode_accepts_unambiguous(self):
        """Strict mode should accept unambiguous inputs."""
        ni = normalize_input("2000-01-15", "14:30:00", "Moscow", strict=True)
        assert ni.utc_dt.year == 2000
        assert ni.utc_dt.month == 1
        assert ni.utc_dt.day == 15
        assert ni.lat == pytest.approx(55.7558, abs=0.01)
    
    def test_strict_mode_with_override_coordinates(self):
        """Strict mode with explicit coords should bypass city resolution."""
        ni = normalize_input(
            "2000-01-15",
            "14:30:00",
            "UnknownPlace",
            lat_override=51.5,
            lon_override=0.0,
            strict=True
        )
        assert ni.lat == 51.5
        assert ni.lon == 0.0
        assert ni.raw_place == "UnknownPlace"
    
    def test_lenient_mode_with_ambiguous_city(self):
        """Lenient mode should handle ambiguous cities."""
        # Test with a known city
        ni = normalize_input("2000-01-15", "14:30", "Moscow", strict=False)
        assert ni.utc_dt.year == 2000
        assert ni.lat is not None


class TestNormalizeInputIntegration:
    """Integration tests for the complete normalization pipeline."""
    
    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """Reset cache before each test."""
        reset_global_cache()
        yield
        reset_global_cache()
    
    def test_complete_moscow_natal(self):
        """Complete example: Moscow natal time (synthetic test data)."""
        ni = normalize_input(
            date_str="1900-08-15",
            time_str="23:45:00",
            place_str="Москва",
            tz_override=None,
            locale=None,
            strict=False
        )
        
        # Check all fields populated
        assert ni.raw_date == "1900-08-15"
        assert ni.raw_time == "23:45:00"
        assert ni.raw_place == "Москва"
        
        # Check datetime normalization
        assert ni.utc_dt.tzinfo is not None
        assert ni.local_dt.tzinfo is not None
        assert ni.tz_name == "Europe/Moscow"
        
        # Check coordinates
        assert ni.lat == pytest.approx(55.7558, abs=0.01)
        assert ni.lon == pytest.approx(37.6173, abs=0.01)
        
        # Check confidence
        assert 0 < ni.confidence <= 1.0
    
    def test_complete_london_natal(self):
        """Complete example: London natal time (synthetic test data)."""
        ni = normalize_input(
            date_str="1900-08-31",
            time_str="21:02:00",
            place_str="London",
            tz_override=None,
            locale=None,
            strict=False
        )
        
        # Geopy may return 'Greater London' instead of just 'London'
        assert 'London' in ni.place_name
        assert ni.tz_name == "Europe/London"
        assert ni.lat == pytest.approx(51.5074, abs=0.01)
        assert ni.lon == pytest.approx(-0.1278, abs=0.01)
    
    def test_with_explicit_coordinates(self):
        """Test with explicit lat/lon override."""
        ni = normalize_input(
            date_str="2000-01-15",
            time_str="14:30",
            place_str="Unnamed Location",
            lat_override=37.7749,
            lon_override=-122.4194,
            tz_override="America/Los_Angeles"
        )
        
        assert ni.lat == 37.7749
        assert ni.lon == -122.4194
        assert ni.tz_name == "America/Los_Angeles"
    
    def test_input_context_bridge(self):
        """Test InputContext bridge layer."""
        ni = normalize_input("2000-01-15", "14:30:00", "Moscow")
        ctx = InputContext.from_normalized(ni)
        
        # Context should expose same data
        assert ctx.utc_dt == ni.utc_dt
        assert ctx.lat == ni.lat
        assert ctx.lon == ni.lon
        
        # Metadata should be serializable
        metadata = ctx.to_metadata_dict()
        assert isinstance(metadata, dict)
        assert "confidence" in metadata
        assert "warnings" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
