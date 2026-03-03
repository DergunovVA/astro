# 🛠️ RED TEAM REMEDIATION GUIDE

## Step-by-Step Solutions for All Critical Issues

**Date**: January 15, 2026  
**Phase**: Implementation Planning  
**Estimated Total Time**: 29 hours

---

## PART 1: CRITICAL FIXES (Week 1) - 9 Hours

### FIX #1: Unicode Encoding (CRITICAL) - 1 Hour

**Problem**: Windows cp1252 encoding crashes on Unicode characters

**File**: `main.py`

**Implementation**:

```python
# Add at the very top of main.py, before any other imports or output

import sys
import os
import io

# Force UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    # Redirect stdout and stderr to use UTF-8 encoding
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Alternative: Set environment variable before import
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Rest of imports
import typer
import json
...
```

**Test**:

```bash
# Should NOT crash
python -m main natal 1990-01-01 12:00 Москва
python -m main natal 1990-01-01 12:00 "São Paulo"
```

**Verify Fix**:

```python
# Add to test file
def test_unicode_output():
    result = run_command(['python', '-m', 'main', 'natal', '1990-01-01', '12:00', 'Москва'])
    assert result.returncode == 0
    assert 'Москва' in result.stdout or 'Moscow' in result.stdout
```

---

### FIX #2: Future Date Validation (CRITICAL) - 2 Hours

**Problem**: Parser accepts dates beyond reasonable range (2025+)

**File**: `input_pipeline/parser_datetime.py`

**Current Code**:

```python
def parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime:
    # ... existing parsing code ...
    d = datetime.fromisoformat(date_str).date()  # No validation!
    return ParsedDateTime(...)
```

**New Code**:

```python
from datetime import date, datetime, timedelta
import warnings

def parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime:
    """Parse date and time with validation."""

    # ... existing parsing code ...
    d = datetime.fromisoformat(date_str).date()

    # ADD: Date range validation
    min_date = date(1800, 1, 1)  # Earliest reasonable birth date
    max_date = date(2300, 12, 31)  # Farthest future prediction

    if d < min_date:
        raise ValueError(
            f"Date {d} is before {min_date}. "
            f"Please check that the year is correct."
        )

    if d > max_date:
        raise ValueError(
            f"Date {d} is after {max_date}. "
            f"Please check that the year is correct."
        )

    # ADD: Warning for future dates
    warnings_list = []
    today = date.today()

    if d > today:
        warnings_list.append(ParseWarning(
            code='FUTURE_DATE',
            message='Birth date is in the future - results are predictive only',
            details={'date': str(d), 'today': str(today)}
        ))

    # ADD: Warning for very old dates
    if d.year < 1900:
        warnings_list.append(ParseWarning(
            code='VERY_OLD_DATE',
            message='Birth date is before 1900 - interpretation may be unreliable',
            details={'date': str(d)}
        ))

    # ... rest of function ...
    return ParsedDateTime(..., warnings=warnings_list)
```

**Tests**:

```python
def test_date_validation():
    # Should reject: too old
    with pytest.raises(ValueError, match='before 1800'):
        parse_date_time('1799-01-01', '12:00')

    # Should reject: too far in future
    with pytest.raises(ValueError, match='after 2300'):
        parse_date_time('2301-01-01', '12:00')

    # Should accept with warning: slightly in future
    result = parse_date_time('2050-01-01', '12:00')
    assert any(w.code == 'FUTURE_DATE' for w in result.warnings)

    # Should accept with warning: historical
    result = parse_date_time('1850-01-01', '12:00')
    assert any(w.code == 'VERY_OLD_DATE' for w in result.warnings)
```

---

### FIX #3: Strict Date Format Parsing (CRITICAL) - 2 Hours

**Problem**: Accepts non-standard formats (YYYYMMDD, DD/MM/YY) ambiguously

**File**: `input_pipeline/parser_datetime.py`

**Current Code**:

```python
def parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime:
    date_str = date_str.strip()

    # Multiple fuzzy parsers - ambiguous!
    try:
        d = datetime.fromisoformat(date_str).date()
    except ValueError:
        d = dateutil.parser.parse(date_str).date()  # Fuzzy - could misinterpret!

    return ParsedDateTime(date=d, ...)
```

**New Code**:

```python
import re
from datetime import date, datetime

def parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime:
    """Parse date and time with strict format validation."""

    date_str = date_str.strip()
    warnings_list = []

    # ONLY accept these formats explicitly:
    # 1. ISO format: YYYY-MM-DD (preferred)
    # 2. European: DD.MM.YYYY (if locale specifies)
    # 3. US: MM/DD/YYYY (if locale specifies)

    d = None

    # Try ISO format first (YYYY-MM-DD)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        try:
            d = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise ValueError(
                f"Invalid date: {date_str}. "
                f"Expected ISO format YYYY-MM-DD (e.g., 1990-01-15)"
            )

    # Try European format (DD.MM.YYYY) if appropriate locale
    elif re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
        if locale and locale.startswith(('de_', 'ru_', 'fr_')):
            try:
                d = datetime.strptime(date_str, '%d.%m.%Y').date()
            except ValueError:
                raise ValueError(
                    f"Invalid date: {date_str}. "
                    f"Expected DD.MM.YYYY format (e.g., 15.01.1990)"
                )
        else:
            raise ValueError(
                f"Date format DD.MM.YYYY not standard for locale {locale or 'default'}. "
                f"Use ISO format: YYYY-MM-DD"
            )

    # Try US format (MM/DD/YYYY) if appropriate locale
    elif re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        if locale and locale.startswith('en_US'):
            try:
                d = datetime.strptime(date_str, '%m/%d/%Y').date()
                warnings_list.append(ParseWarning(
                    code='AMBIGUOUS_FORMAT',
                    message='Date format MM/DD/YYYY is ambiguous. Recommend using ISO format YYYY-MM-DD',
                    details={'format': 'MM/DD/YYYY', 'example': '01/15/1990 for January 15, 1990'}
                ))
            except ValueError:
                raise ValueError(
                    f"Invalid date: {date_str}. "
                    f"Expected MM/DD/YYYY format (e.g., 01/15/1990)"
                )
        else:
            raise ValueError(
                f"Ambiguous date format MM/DD/YYYY. Use ISO format instead: YYYY-MM-DD"
            )

    else:
        # Reject anything else
        raise ValueError(
            f"Unsupported date format: '{date_str}'. "
            f"Please use ISO format: YYYY-MM-DD (e.g., 1990-01-15)\n"
            f"Other accepted formats:\n"
            f"  - DD.MM.YYYY (European, requires locale=de_DE or ru_RU)\n"
            f"  - MM/DD/YYYY (US, requires locale=en_US)"
        )

    if d is None:
        raise ValueError(f"Could not parse date: {date_str}")

    # ... continue with existing validation and time parsing ...

    return ParsedDateTime(
        date=d,
        time=t,
        warnings=warnings_list,
        ...
    )
```

**Tests**:

```python
def test_strict_date_parsing():
    # ACCEPT: ISO format
    result = parse_date_time('1990-01-15', '12:00')
    assert result.date == date(1990, 1, 15)

    # REJECT: YYYYMMDD (no separators)
    with pytest.raises(ValueError, match='Unsupported date format'):
        parse_date_time('19900115', '12:00')

    # ACCEPT: European format with locale
    result = parse_date_time('15.01.1990', '12:00', locale='de_DE')
    assert result.date == date(1990, 1, 15)

    # WARN: US format (ambiguous)
    result = parse_date_time('01/15/1990', '12:00', locale='en_US')
    assert any(w.code == 'AMBIGUOUS_FORMAT' for w in result.warnings)

    # REJECT: US format without locale
    with pytest.raises(ValueError, match='Ambiguous'):
        parse_date_time('01/15/1990', '12:00', locale=None)
```

---

### FIX #4: DST Edge Case Handling (Critical for Accuracy) - 4 Hours

**File**: `input_pipeline/resolver_timezone.py`

**Current Code**:

```python
def make_aware(naive_dt: datetime, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    aware_dt = naive_dt.replace(tzinfo=tz)  # Silently accepts ambiguous times!
    return aware_dt
```

**New Code**:

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

def make_aware(naive_dt: datetime, tz_name: str, allow_ambiguous: bool = False) -> tuple[datetime, list]:
    """
    Convert naive datetime to timezone-aware, handling DST transitions.

    Args:
        naive_dt: Timezone-unaware datetime
        tz_name: Timezone name (e.g., 'America/New_York')
        allow_ambiguous: If True, use first occurrence of ambiguous times
                        If False, raise error on ambiguous/non-existent times

    Returns:
        (aware_dt, warnings) - Aware datetime and list of warnings
    """

    warnings = []

    try:
        tz = ZoneInfo(tz_name)
    except KeyError:
        raise ValueError(f"Unknown timezone: {tz_name}")

    # Python's fold parameter: 0 = first occurrence, 1 = second occurrence
    # Try with fold=0 first
    try:
        aware_fold0 = naive_dt.replace(tzinfo=tz, fold=0)
        aware_fold1 = naive_dt.replace(tzinfo=tz, fold=1)

        offset0 = aware_fold0.utcoffset()
        offset1 = aware_fold1.utcoffset()

        if offset0 == offset1:
            # Time is unambiguous - single valid interpretation
            return aware_fold0, warnings

        else:
            # Time is ambiguous (occurs twice during fall-back)
            # or non-existent (skipped during spring-forward)

            if offset0 is None or offset1 is None:
                # Non-existent time (spring-forward)
                error_msg = (
                    f"Requested time {naive_dt} does not exist in timezone {tz_name}\n"
                    f"(Clocks spring forward during DST transition)\n"
                    f"Provide time in UTC or clarify which offset you meant."
                )
                if not allow_ambiguous:
                    raise ValueError(error_msg)
                # Use earlier offset as fallback
                aware_dt = aware_fold0
                warnings.append(ParseWarning(
                    code='NON_EXISTENT_TIME',
                    message='Requested time does not exist (skipped during DST). Using earlier offset.',
                    details={'naive_time': str(naive_dt), 'timezone': tz_name}
                ))

            else:
                # Ambiguous time (occurs twice during fall-back)
                error_msg = (
                    f"Requested time {naive_dt} is ambiguous in {tz_name}\n"
                    f"(Clocks fall back during DST transition)\n"
                    f"This time occurs twice. Using FIRST occurrence (EDT).\n"
                    f"First (EDT) : {aware_fold0.isoformat()}\n"
                    f"Second (EST): {aware_fold1.isoformat()}\n"
                    f"To specify which, provide UTC time instead."
                )
                if not allow_ambiguous:
                    raise ValueError(error_msg)
                # Use first occurrence
                aware_dt = aware_fold0
                warnings.append(ParseWarning(
                    code='AMBIGUOUS_TIME',
                    message='Birth time is ambiguous (occurs twice during DST fall-back). Used first occurrence.',
                    details={
                        'naive_time': str(naive_dt),
                        'timezone': tz_name,
                        'utc_first': aware_fold0.isoformat(),
                        'utc_second': aware_fold1.isoformat(),
                    }
                ))

            return aware_dt, warnings

    except Exception as e:
        raise ValueError(f"Cannot localize {naive_dt} to {tz_name}: {e}")
```

**Update resolver_timezone.py to return warnings**:

```python
def resolve_tz_name(place: str, coords: tuple[float, float], hints: dict = None) -> tuple[str, list]:
    """
    Resolve timezone name from place and coordinates.

    Returns:
        (tz_name, warnings) - Timezone name and any warnings
    """
    # ... existing logic ...

    return tz_name, warnings  # Add warnings to return
```

**Update parser_datetime.py to use new warnings**:

```python
def parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime:
    # ... date parsing ...
    # ... time parsing ...

    # Will be updated with tz resolution in normalize_input
    return ParsedDateTime(
        date=d,
        time=t,
        tz_name=None,  # Set later in normalize_input
        aware_dt=None,
        warnings=warnings_list
    )
```

**Update normalize_input to handle DST warnings**:

```python
def normalize_input(...) -> NormalizedInput:
    # ... parse date/time ...
    parsed = parse_date_time(date_str, time_str, locale=locale)

    # ... resolve city ...
    rp = resolve_city(place_str, cache=cache)

    # Resolve timezone with warning handling
    tz_name, tz_warnings = resolve_tz_name(place_str, (rp.lat, rp.lon), hints={'tz_override': tz_override})
    parsed.warnings.extend(tz_warnings)

    # Make aware with DST handling
    local_dt, dst_warnings = make_aware(
        datetime.combine(parsed.date, parsed.time),
        tz_name,
        allow_ambiguous=True  # For now, allow with warning
    )
    parsed.warnings.extend(dst_warnings)

    # ... rest of function ...
    return NormalizedInput(..., warnings=parsed.warnings)
```

**Tests**:

```python
def test_dst_transitions():
    # Non-existent time (spring forward)
    with pytest.raises(ValueError, match='does not exist'):
        _, _ = make_aware(
            datetime(2024, 3, 10, 2, 30),  # 2:30 AM EST doesn't exist
            'America/New_York',
            allow_ambiguous=False
        )

    # Allow ambiguous - should return with warning
    result, warnings = make_aware(
        datetime(2024, 3, 10, 2, 30),
        'America/New_York',
        allow_ambiguous=True
    )
    assert any(w.code == 'NON_EXISTENT_TIME' for w in warnings)

    # Ambiguous time (fall back)
    with pytest.raises(ValueError, match='is ambiguous'):
        _, _ = make_aware(
            datetime(2024, 11, 3, 1, 30),  # 1:30 AM EST occurs twice
            'America/New_York',
            allow_ambiguous=False
        )

    # Allow ambiguous - use first occurrence
    result, warnings = make_aware(
        datetime(2024, 11, 3, 1, 30),
        'America/New_York',
        allow_ambiguous=True
    )
    assert any(w.code == 'AMBIGUOUS_TIME' for w in warnings)
```

---

## PART 2: HIGH SEVERITY FIXES (Week 2) - 14 Hours

### FIX #5: Extreme Coordinate Handling - 1 Hour

**File**: `astro_adapter.py`

```python
def calc_houses_raw(jd: float, lat: float, lon: float, method: str = "Placidus") -> List[float]:
    """Get house cusps from Swiss Ephemeris with boundary validation."""

    # Validate boundaries
    if not (-90 <= lat <= 90):
        raise ValueError(
            f"Latitude out of range: {lat}. "
            f"Must be between -90 (South Pole) and 90 (North Pole)."
        )

    if not (-180 <= lon <= 180):
        raise ValueError(
            f"Longitude out of range: {lon}. "
            f"Must be between -180 (West) and 180 (East)."
        )

    # Special handling for poles (house systems undefined at ±90°)
    if abs(lat) >= 89.99:  # Very close to pole
        raise ValueError(
            f"House calculation is undefined at extreme latitudes (|lat| > 89.99°). "
            f"Birth location {lat}° is too close to a pole. "
            f"Please verify birth coordinates are correct."
        )

    if method == "Placidus":
        try:
            cusps_tuple = swe.houses(jd, lat, lon)
            houses = list(cusps_tuple[0])
            if len(houses) != 12:
                raise ValueError(f"Expected 12 houses, got {len(houses)}")
            return houses
        except Exception as e:
            raise ValueError(f"House calculation failed at ({lat}°, {lon}°): {e}")

    elif method == "WholeSign":
        asc = swe.houses(jd, lat, lon)[0][0]
        return [(asc + i * 30) % 360 for i in range(12)]

    else:
        raise ValueError(f"Unknown house method: {method}")
```

---

### FIX #6: Cache File Resilience - 2 Hours

**File**: `input_pipeline/cache.py`

```python
import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict

class JsonCache:
    """JSON file cache with corruption recovery and TTL support."""

    def __init__(self, filepath: str = '.cache_places.json', ttl_hours: int = 24):
        self.filepath = filepath
        self.backup_path = filepath + '.backup'
        self.tmp_path = filepath + '.tmp'
        self.ttl_hours = ttl_hours
        self._cache: Dict[str, dict] = {}
        self._load_safely()

    def _load_safely(self):
        """Load cache with fallback to backup and automatic cleanup."""
        try:
            # Try to load primary cache
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._cache = data.get('entries', {})
                    self._cleanup_expired()

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Primary cache corrupted - try backup
            if os.path.exists(self.backup_path):
                try:
                    with open(self.backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._cache = data.get('entries', {})
                        # Restore from backup
                        shutil.copy2(self.backup_path, self.filepath)
                except Exception:
                    # Backup also corrupted - start fresh
                    self._cache = {}
            else:
                # No backup - start fresh
                self._cache = {}

    def _cleanup_expired(self):
        """Remove entries older than TTL."""
        now = datetime.utcnow().timestamp()
        expired_keys = []

        for key, entry in self._cache.items():
            if 'timestamp' in entry:
                age_seconds = now - entry['timestamp']
                if age_seconds > self.ttl_hours * 3600:
                    expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, respecting TTL."""
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check TTL
        if 'timestamp' in entry:
            age_seconds = (datetime.utcnow() - datetime.fromisoformat(
                entry['timestamp']
            )).total_seconds()

            if age_seconds > self.ttl_hours * 3600:
                del self._cache[key]  # Evict expired
                return None

        return entry.get('value')

    def set(self, key: str, value: Any):
        """Set value in cache with timestamp."""
        self._cache[key] = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'manual'
        }
        self._save_safely()

    def _save_safely(self):
        """Save cache with atomic write and backup rotation."""
        try:
            # Create backup of current cache if it exists
            if os.path.exists(self.filepath):
                shutil.copy2(self.filepath, self.backup_path)

            # Write to temporary file first
            data = {'entries': self._cache}
            with open(self.tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Atomic rename
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(self.tmp_path, self.filepath)

        except Exception as e:
            # If write fails, try to restore from backup
            if os.path.exists(self.backup_path):
                try:
                    shutil.copy2(self.backup_path, self.filepath)
                except:
                    pass
            # Clean up temp file
            if os.path.exists(self.tmp_path):
                os.remove(self.tmp_path)
            raise IOError(f"Failed to save cache: {e}")

    def clear(self):
        """Clear all cache entries."""
        self._cache = {}
        self._save_safely()
```

---

### FIX #7: Graceful Dependency Degradation - 1 Hour

**File**: `input_pipeline/resolver_city.py`

```python
def resolve_city(place: str, cache: JsonCache) -> ResolvedPlace:
    """
    Resolve city with graceful fallback if geopy unavailable.

    Fallback chain:
    1. Check ALIASES (hardcoded, always available)
    2. Check cache (previously resolved)
    3. Try geopy (online geocoding, optional)
    4. Fail with helpful error message
    """

    place_lower = place.lower().strip()

    # Step 1: Check ALIASES (always available)
    if place_lower in ALIASES:
        alias = ALIASES[place_lower]
        return ResolvedPlace(
            query=place,
            name=alias['name'],
            country=alias.get('country'),
            lat=alias['lat'],
            lon=alias['lon'],
            tz_name=alias.get('tz'),
            source='alias',
            confidence=0.95,
            warnings=[]
        )

    # Step 2: Check cache
    cached = cache.get(place_lower)
    if cached:
        if isinstance(cached, dict):
            return ResolvedPlace(**cached)
        return cached

    # Step 3: Try geopy
    try:
        import geopy.geocoders
        from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    except ImportError:
        # Geopy not installed
        raise ValueError(
            f"Cannot resolve city '{place}'. Geopy not installed.\n"
            f"Options:\n"
            f"  1. Use standard city name (check ALIASES)\n"
            f"  2. Install geopy: pip install geopy\n"
            f"  3. Provide coordinates manually (if supported)"
        )

    try:
        geocoder = geopy.geocoders.Nominatim(user_agent='astro_calc')
        location = geocoder.geocode(place, timeout=5)

        if location:
            result = ResolvedPlace(
                query=place,
                name=location.address or place,
                country=None,  # Could parse from address
                lat=location.latitude,
                lon=location.longitude,
                tz_name=None,  # Will be resolved separately
                source='geopy',
                confidence=0.8,
                warnings=[]
            )
            # Cache for next time
            cache.set(place_lower, {
                'query': result.query,
                'name': result.name,
                'country': result.country,
                'lat': result.lat,
                'lon': result.lon,
                'tz_name': result.tz_name,
                'source': result.source,
                'confidence': result.confidence,
            })
            return result

    except GeocoderTimedOut:
        raise ValueError(
            f"Geocoding server timeout while resolving '{place}'. "
            f"Try again in a moment or use a city from ALIASES."
        )
    except GeocoderUnavailable:
        raise ValueError(
            f"Geocoding service unavailable. "
            f"Try again later or use a city from ALIASES."
        )
    except Exception as e:
        raise ValueError(
            f"Geocoding failed for '{place}': {e}\n"
            f"Try using a different city name or one from ALIASES."
        )

    # Step 4: No resolution possible
    raise ValueError(
        f"Cannot resolve city '{place}'.\n"
        f"Options:\n"
        f"  1. Use a standard city name: {', '.join(list(ALIASES.keys())[:5])}...\n"
        f"  2. Check spelling and try again\n"
        f"  3. Install geopy for more cities: pip install geopy"
    )
```

---

### FIX #8-11: Remaining HIGH Issues - 10 Hours

[Continued in next section...]

---

## PART 3: TESTING & VALIDATION

### Create Comprehensive Test Suite

**File**: `test_red_team_fixes.py`

```python
import pytest
from datetime import datetime, date
from input_pipeline import normalize_input
from astro_adapter import calc_houses_raw

class TestCriticalFixes:
    """Test suite for red team issue fixes."""

    def test_unicode_encoding(self):
        """Verify Unicode output doesn't crash."""
        # Should not raise UnicodeEncodeError
        result = normalize_input('1990-01-01', '12:00', 'Москва')
        assert result.place_name  # Got some result

    def test_future_date_rejection(self):
        """Verify future dates are rejected."""
        with pytest.raises(ValueError, match='after 2300'):
            normalize_input('2301-01-01', '12:00', 'Moscow')

    def test_strict_date_format(self):
        """Verify only ISO format accepted."""
        # ACCEPT: ISO
        normalize_input('1990-01-15', '12:00', 'Moscow')

        # REJECT: Non-ISO
        with pytest.raises(ValueError):
            normalize_input('19900115', '12:00', 'Moscow')

    def test_extreme_coordinates(self):
        """Verify pole coordinates rejected."""
        with pytest.raises(ValueError, match='undefined'):
            calc_houses_raw(2400000, 90.0, 0.0)

    def test_cache_corruption_recovery(self):
        """Verify corrupted cache doesn't crash."""
        # Simulate corruption
        import json
        with open('.cache_places.json', 'w') as f:
            f.write('{invalid json}')

        # Should recover
        result = normalize_input('1990-01-01', '12:00', 'Moscow')
        assert result is not None

# Run: pytest test_red_team_fixes.py -v
```

---

## SUMMARY: Implementation Checklist

- [ ] **Week 1 (9 hours)**

  - [ ] Fix #1: Unicode encoding (1h)
  - [ ] Fix #2: Future date validation (2h)
  - [ ] Fix #3: Strict date format (2h)
  - [ ] Fix #4: DST handling (4h)

- [ ] **Week 2 (14 hours)**

  - [ ] Fix #5: Coordinate validation (1h)
  - [ ] Fix #6: Cache resilience (2h)
  - [ ] Fix #7: Dependency fallback (1h)
  - [ ] Fix #8-11: High severity issues (10h)

- [ ] **Testing & Validation (4 hours)**
  - [ ] Create test suite
  - [ ] Run full test coverage
  - [ ] Verify all fixes work
  - [ ] Check for regressions

**Total**: ~27 hours

---

**Implementation Guide Complete** ✓
