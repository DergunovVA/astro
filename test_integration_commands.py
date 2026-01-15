"""Integration tests for all 6 CLI commands."""

import json
import sys
from pathlib import Path
from subprocess import run, PIPE, STDOUT
import pytest


class TestIntegrationAllCommands:
    """Integration tests for all 6 commands."""

    def run_command(self, *args) -> dict:
        """Run main.py command and parse JSON output using current Python environment."""
        # Use the same Python executable as the test
        result = run(
            [sys.executable, "-m", "main"] + list(args),
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stdout}")
        
        # Parse JSON output (skip warnings/other output)
        lines = result.stdout.strip().split('\n')
        json_start = next((i for i, line in enumerate(lines) if line.startswith('{')), None)
        if json_start is None:
            raise RuntimeError(f"No JSON output found: {result.stdout}")
        json_str = '\n'.join(lines[json_start:])
        return json.loads(json_str)

    def test_natal_moscow(self):
        """Test natal command with Moscow (cached alias)."""
        result = self.run_command("natal", "1990-01-01", "12:00", "Moscow")
        
        # Check input_metadata
        assert "input_metadata" in result
        assert result["input_metadata"]["confidence"] == 0.95
        assert result["input_metadata"]["timezone"] == "Europe/Moscow"
        assert result["input_metadata"]["coordinates"]["lat"] == 55.7558
        assert result["input_metadata"]["coordinates"]["lon"] == 37.6173
        
        # Check results
        assert "facts" in result
        assert len(result["facts"]) > 0
        assert result["facts"][0]["type"] in ["planet_in_sign", "house_cusp", "aspect"]

    def test_natal_new_city_alias(self):
        """Test natal command with new city alias (New York)."""
        result = self.run_command("natal", "1990-01-01", "12:00", "New York")
        
        # Check coordinates are correct
        assert result["input_metadata"]["coordinates"]["lat"] == 40.7128
        assert result["input_metadata"]["coordinates"]["lon"] == -74.006
        assert result["input_metadata"]["timezone"] == "America/New_York"

    def test_transit_london(self):
        """Test transit command with London."""
        result = self.run_command("transit", "2025-01-15", "12:00", "London")
        
        # Check minimal metadata
        assert "input_metadata" in result
        assert "coordinates" in result["input_metadata"]
        assert result["input_metadata"]["timezone"] == "Europe/London"
        
        # Check results exist
        assert "facts" in result
        assert "signals" in result
        assert "decisions" in result

    def test_solar_tokyo(self):
        """Test solar command with Tokyo."""
        result = self.run_command("solar", "2025", "1990-01-01", "12:00", "Tokyo")
        
        # Check Tokyo coordinates (with some tolerance for precision)
        assert abs(result["input_metadata"]["coordinates"]["lat"] - 35.6762) < 0.001
        assert result["input_metadata"]["timezone"] == "Asia/Tokyo"

    def test_rectify_sydney(self):
        """Test rectify command with Sydney."""
        result = self.run_command("rectify", "1990-01-01", "12:00", "Sydney")
        
        # Check Sydney data
        assert result["input_metadata"]["timezone"] == "Australia/Sydney"
        assert result["input_metadata"]["coordinates"]["lat"] == -33.8688

    def test_devils_paris(self):
        """Test devils command with Paris."""
        result = self.run_command("devils", "1990-01-01", "12:00", "Paris")
        
        # Check full metadata with place info
        assert result["input_metadata"]["place"]["country"] == "FR"
        assert result["input_metadata"]["place"]["name"] == "Paris"
        
        # Check devils output
        assert "devils" in result
        assert result["devils"]["raw"] is True

    def test_relocate_new_city(self):
        """Test relocate command with new city."""
        result = self.run_command("relocate", "Berlin")
        
        # Check coordinates
        assert result["coords"]["lat"] == 52.52
        assert result["coords"]["lon"] == 13.405
        assert result["country"] == "DE"

    def test_tz_override_parameter(self):
        """Test --tz parameter to override auto-detection."""
        result = self.run_command("natal", "1990-01-01", "12:00", "Moscow", "--tz", "UTC")
        
        # Timezone should be overridden to UTC
        assert result["input_metadata"]["timezone"] == "UTC"

    def test_cyrillic_input(self):
        """Test with Cyrillic city names."""
        result = self.run_command("natal", "1990-01-01", "12:00", "москва")
        
        # Should resolve to Moscow
        assert result["input_metadata"]["timezone"] == "Europe/Moscow"
        assert result["input_metadata"]["coordinates"]["lat"] == 55.7558

    def test_explain_flag(self):
        """Test --explain flag adds explanations."""
        result = self.run_command("natal", "1990-01-01", "12:00", "Moscow", "--explain")
        
        # Should have explain and fix sections
        assert "explain" in result
        assert "fix" in result
        assert len(result["explain"]) > 0

    def test_devils_flag(self):
        """Test --devils flag adds raw calculation data."""
        result = self.run_command("natal", "1990-01-01", "12:00", "Moscow", "--devils")
        
        # Should have devils section with calc data
        assert "devils" in result
        assert "calc" in result["devils"]
        assert "jd" in result["devils"]["calc"]

    def test_european_date_format(self):
        """Test European date format (DD.MM.YYYY)."""
        result = self.run_command("natal", "01.01.1990", "12:00", "Moscow")
        
        # Should parse correctly
        assert "facts" in result
        assert len(result["facts"]) > 0

    def test_confidence_and_warnings(self):
        """Test that confidence and warnings are returned."""
        result = self.run_command("natal", "1990-01-01", "12:00", "Moscow")
        
        # Should have confidence
        assert "confidence" in result["input_metadata"]
        assert 0 <= result["input_metadata"]["confidence"] <= 1.0
        
        # May or may not have warnings (Moscow is cached, no warnings)
        assert "warnings" in result["input_metadata"]


class TestGlobalCache:
    """Test global cache functionality."""

    def test_global_cache_persistent(self):
        """Test that global cache persists across calls."""
        from input_pipeline import get_global_cache, reset_global_cache, resolve_city
        
        # Reset cache
        reset_global_cache()
        
        # First call
        cache1 = get_global_cache()
        resolve_city("Moscow", cache1)
        
        # Second call should return same instance
        cache2 = get_global_cache()
        assert cache1 is cache2
        
        # Moscow should be in cache
        resolve_city("Moscow", cache2)

    def test_reset_cache(self):
        """Test cache reset function."""
        from input_pipeline import get_global_cache, reset_global_cache
        
        cache1 = get_global_cache()
        reset_global_cache()
        cache2 = get_global_cache()
        
        # Should be different instances after reset
        assert cache1 is not cache2


class TestInputContext:
    """Test InputContext bridge class."""

    def test_input_context_from_normalized(self):
        """Test InputContext factory method."""
        from input_pipeline import normalize_input, InputContext
        
        ni = normalize_input("1990-01-01", "12:00", "Moscow")
        ctx = InputContext.from_normalized(ni)
        
        # Should have all fields
        assert ctx.tz_name == "Europe/Moscow"
        assert ctx.lat == 55.7558
        assert ctx.lon == 37.6173

    def test_input_context_to_metadata(self):
        """Test InputContext metadata dict generation."""
        from input_pipeline import normalize_input, InputContext
        
        ni = normalize_input("1990-01-01", "12:00", "Moscow")
        ctx = InputContext.from_normalized(ni)
        
        metadata = ctx.to_metadata_dict()
        assert "confidence" in metadata
        assert "timezone" in metadata
        assert "coordinates" in metadata
        assert "place" in metadata

    def test_input_context_helpers(self):
        """Test InputContext helper methods."""
        from input_pipeline import normalize_input, InputContext
        
        ni = normalize_input("1990-01-01", "12:00", "Moscow")
        ctx = InputContext.from_normalized(ni)
        
        # Test helper methods
        assert ctx.get_coordinates() == (55.7558, 37.6173)
        assert ctx.get_utc_datetime() is not None
        assert ctx.get_local_datetime() is not None
        assert not ctx.has_warnings()  # Moscow has no warnings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
