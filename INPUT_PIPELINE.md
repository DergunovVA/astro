# Input Pipeline Documentation

## Overview

The **input_pipeline** is the **boundary layer** between raw CLI input and the core astro-mathematical engine. It handles:

- Date/time parsing (multiple formats)
- City geolocation resolution
- Timezone determination and UTC conversion
- Input validation and normalization
- Caching for reproducibility

**Core principle**: All external dependencies (geopy, dateparser, timezonefinder, zoneinfo) are used **ONLY** in this layer. The core math engine (`astro_adapter`, `aspects_math`) receives clean floats and datetimes with NO tuples or external types.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           CLI Input (raw strings)            │
│  date="15.01.2000" time="14:30" place="Москва"  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
         ┌───────────────────┐
         │ BOUNDARY LAYER    │
         │ input_pipeline/   │
         └───────────────────┘
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────────┐
   │ Parse  │ │Resolve │ │ Resolve    │
   │DateTime│ │  City  │ │ Timezone   │
   └────┬───┘ └───┬────┘ └──────┬─────┘
        │         │             │
        └─────────┼─────────────┘
                  ▼
         ┌─────────────────────┐
         │ NormalizedInput     │
         │ ✓ utc_dt (datetime) │
         │ ✓ local_dt (datetime) │
         │ ✓ lat (float)       │
         │ ✓ lon (float)       │
         │ ✓ tz_name (str)     │
         │ ✓ confidence (0-1)  │
         │ ✓ warnings (list)   │
         └────────┬────────────┘
                  │
                  ▼
    ┌──────────────────────────────┐
    │  CORE MATH ENGINE            │
    │  (astro_adapter)             │
    │  Input: utc_dt + lat/lon     │
    │  Output: planets {Dict[str,float]} │
    └──────────────────────────────┘
```

---

## Module Structure

### 1. `models.py` - Data Classes

**ParseWarning**: Represents a parse-time warning with:

- `code`: String identifier (e.g., "DATE_AMBIGUOUS", "GEOPY_MISSING")
- `message`: Human-readable message

**ResolvedPlace**: Result of city/location resolution:

- `query`: Original input string
- `name`: Resolved city name
- `lat`, `lon`: Decimal degrees (-90 to 90, -180 to 180)
- `tz_name`: IANA timezone name
- `source`: How it was resolved ("alias" | "geocoder" | "override")
- `confidence`: 0.0-1.0 confidence score
- `warnings`: List of ParseWarning

**NormalizedInput**: Complete normalized input result:

- `raw_date`, `raw_time`, `raw_place`: Original inputs
- `local_dt`: Timezone-aware datetime in local time
- `utc_dt`: Timezone-aware datetime in UTC (for core math)
- `tz_name`: Timezone string
- `lat`, `lon`: Coordinates
- `confidence`: Min confidence across all stages
- `warnings`: All warnings from all stages

### 2. `parser_datetime.py` - Date/Time Parsing

**Function**: `parse_date_time(date_str: str, time_str: str, locale: str | None = None) -> ParsedDateTime`

**Supported formats**:

- ISO: `2000-01-15`
- European: `15.01.2000`, `15/01/2000`
- US: `01/15/2000`
- Flexible: `January 15, 2000`

**Example**:

```python
result = parse_date_time("15.01.2000", "14:30")
print(result.date_iso)   # "2000-01-15"
print(result.time_iso)   # "14:30:00"
```

### 3. `resolver_city.py` - Location Resolution

**Function**: `resolve_city(place_str: str, cache: JsonCache | None = None) -> ResolvedPlace`

**Resolution strategy** (priority order):

1. **Cache**: Local `.cache_places.json`
2. **Aliases**: 80+ pre-defined cities (Moscow, London, Tokyo, etc.)
3. **Geocoding**: geopy Nominatim (if installed)
4. **Typo detection**: Fuzzy matching fallback
5. **Error**: Raise ValueError if nothing works

**Example**:

```python
rp = resolve_city("Moscow")
print(rp.name)       # "Moscow"
print(rp.lat)        # 55.7558
print(rp.lon)        # 37.6173
print(rp.tz_name)    # "Europe/Moscow"
print(rp.confidence) # 0.95
```

### 4. `resolver_timezone.py` - Timezone Resolution

**Function**: `resolve_tz_name(lat: float, lon: float, hint: str | None = None) -> tuple[str, list[ParseWarning], float]`

**Function**: `make_aware(local_naive: datetime, tz_name: str) -> tuple[datetime, datetime, int]`

**Returns**:

- `local`: Timezone-aware datetime in local time
- `utc`: Timezone-aware datetime in UTC
- `offset_min`: UTC offset in minutes

**Example**:

```python
from datetime import datetime
from input_pipeline.resolver_timezone import make_aware

naive = datetime(2000, 1, 15, 14, 30, 0)
local, utc, offset_min = make_aware(naive, "Europe/Moscow")
print(utc)       # datetime(2000, 1, 15, 11, 30, 0, tzinfo=UTC)
print(offset_min) # 180 (Moscow UTC+3)
```

### 5. `cache.py` - JSON Cache

**Class**: `JsonCache(path: str = ".cache_places.json")`

**Features**:

- ✓ Atomic writes (temp file + rename)
- ✓ Corruption recovery
- ✓ Key normalization
- ✓ Persistent storage

**Methods**:

- `get(key: str) -> Optional[dict]`
- `set(key: str, value: dict) -> None`
- `clear() -> None`

**Example**:

```python
from input_pipeline.cache import JsonCache

cache = JsonCache()
cached = cache.get("moscow")
cache.set("moscow", {"name": "Moscow", ...})
```

### 6. `__init__.py` - Main API

**Main function**: `normalize_input(...) -> NormalizedInput`

**Signature**:

```python
def normalize_input(
    date_str: str,
    time_str: str,
    place_str: str,
    tz_override: str | None = None,
    lat_override: float | None = None,
    lon_override: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    use_global_cache: bool = True
) -> NormalizedInput
```

**Behavior**:

- **Default** (strict=False): Graceful fallback
- **Strict** (strict=True): Fail if ANY ambiguity detected
- **With overrides**: lat/lon bypass city resolution

**Example**:

```python
from input_pipeline import normalize_input

ni = normalize_input(
    date_str="1985-08-15",
    time_str="23:45:00",
    place_str="Москва"
)

print(ni.utc_dt)    # datetime in UTC
print(ni.local_dt)  # datetime in local time
print(ni.tz_name)   # "Europe/Moscow"
print(ni.lat)       # 55.7558
print(ni.lon)       # 37.6173
```

---

## CLI Integration

All commands support enhanced parameters:

```bash
# Explicit timezone
python main.py natal 2000-01-15 14:30 Moscow --tz Europe/Moscow

# Explicit coordinates
python main.py natal 2000-01-15 14:30 "Unknown" --lat 51.5 --lon -0.127

# Strict mode
python main.py natal 2000-01-15 14:30 Moscow --strict

# With locale hint
python main.py natal 01/15/2000 14:30 "New York" --locale en_US
```

**Exit codes**:

- `0`: Success
- `1`: Unexpected error
- `2`: User input error (invalid date, city not found, strict violation)

---

## Error Handling & Recovery

### Missing Dependencies (Graceful Fallback)

```python
# If geopy not installed:
rp = resolve_city("Buenos Aires")  # Falls back to alias
# Still works with warnings

# If timezonefinder not installed:
tz_name, warnings, conf = resolve_tz_name(lat, lon)
# Returns ("UTC", [ParseWarning(...)], 0.3)
```

### Corrupted Cache (Automatic Recovery)

```python
cache = JsonCache()
# If corrupted:
# 1. Backs up to .cache_places.json.backup
# 2. Resets to empty cache
# 3. Prints warning
```

---

## Testing

Run the comprehensive test suite:

```bash
pytest test_input_pipeline.py -v
```

**Coverage**:

- Date/time parsing (ISO, European, US formats)
- City resolution (aliases, typos, geopy fallback)
- Timezone calculation (DST, offsets)
- Cache persistence and corruption recovery
- Strict mode validation
- Integration tests

---

## Performance

| Operation                 | Time   | Notes              |
| ------------------------- | ------ | ------------------ |
| parse_date_time           | ~1ms   | Fast (regex)       |
| resolve_city (alias)      | ~1ms   | Cache-first        |
| resolve_city (cache miss) | ~500ms | Geopy Nominatim    |
| resolve_tz_name           | ~10ms  | Fast lookup        |
| normalize_input           | ~500ms | Dominated by geopy |

**Caching effect**: Second call is 500× faster.

---

## Known Limitations

1. **City coverage**: ~80 cities (covers major cities worldwide)
2. **Synchronous I/O**: Blocks on network (10s timeout)
3. **No TTL on cache**: Entries never expire

---

## Examples

### Moscow Birth Chart

```python
from input_pipeline import normalize_input
from astro_adapter import natal_calculation

ni = normalize_input(
    date_str="1961-07-01",
    time_str="19:02:00",
    place_str="London"
)

print(f"UTC: {ni.utc_dt}")
print(f"Local: {ni.local_dt}")
print(f"TZ: {ni.tz_name}")
print(f"Lat/Lon: {ni.lat}, {ni.lon}")

result = natal_calculation(ni.utc_dt, ni.lat, ni.lon)
```

### Strict Mode Rejection

```python
try:
    ni = normalize_input(
        date_str="2000-01-15",
        time_str="14:30",
        place_str="St. Petersburg",  # Ambiguous!
        strict=True
    )
except ValueError as e:
    print(e)  # "Strict mode: ambiguous location"

# Fix: provide explicit coords
ni = normalize_input(
    date_str="2000-01-15",
    time_str="14:30",
    place_str="St. Petersburg",
    lat_override=59.9311,
    lon_override=30.3609,
    tz_override="Europe/Moscow",
    strict=True
)
```

---

**Status**: Production-ready (Iteration 2)
