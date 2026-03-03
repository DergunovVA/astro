# Fixes Applied - houses & arabic-parts Commands

## Summary
Fixed 2 broken CLI commands by correcting imports and function usage.

## Changes Made

### 1. Fixed `houses` Command (main.py lines 713-765)

**Before:**
```python
from src.core.core_geometry import lon_to_sign_deg
...
"sign": lon_to_sign_deg(houses_data[i])[0],
"degree": lon_to_sign_deg(houses_data[i])[1],
```

**After:**
```python
from src.core.dignities import get_planet_sign, get_planet_degree_in_sign
...
"sign": get_planet_sign(houses_data[i]),
"degree": get_planet_degree_in_sign(houses_data[i]),
```

**Files Changed:** main.py (4 replacements)

### 2. Fixed `arabic-parts` Command (main.py lines 806-858)

**Before:**
```python
from src.core.core_geometry import lon_to_sign_deg
...
"sign": lon_to_sign_deg(lon)[0],
"degree": lon_to_sign_deg(lon)[1],
```

**After:**
```python
from src.core.dignities import get_planet_sign, get_planet_degree_in_sign
...
"sign": get_planet_sign(lon),
"degree": get_planet_degree_in_sign(lon),
```

**Files Changed:** main.py (3 replacements)

## Testing Results

### ✅ houses Command - Table Format
```
━━━ Placidus Houses ━━━
Date: 1982-01-08 08:30:00 UTC
Location: 31.8953, 34.8106

House │ Sign        │ Degree   │ Longitude
──────┼─────────────┼──────────┼──────────
   1  │ Pisces      │  29.82°  │  359.82°
   2  │ Taurus      │   8.33°  │   38.33°
   3  │ Gemini      │   6.44°  │   66.44°
   4  │ Gemini      │  29.89°  │   89.89°
   5  │ Cancer      │  23.32°  │  113.32°
   6  │ Leo         │  21.38°  │  141.38°
   7  │ Virgo       │  29.82°  │  179.82°
   8  │ Scorpio     │   8.33°  │  218.33°
   9  │ Sagittarius │   6.44°  │  246.44°
  10  │ Sagittarius │  29.89°  │  269.89°
  11  │ Capricorn   │  23.32°  │  293.32°
  12  │ Aquarius    │  21.38°  │  321.38°
```

### ✅ houses Command - Degrees Format
```
Placidus Houses:
House  1:  29.82° Pisces
House  2:   8.33° Taurus
House  3:   6.44° Gemini
House  4:  29.89° Gemini
House  5:  23.32° Cancer
House  6:  21.38° Leo
House  7:  29.82° Virgo
House  8:   8.33° Scorpio
House  9:   6.44° Sagittarius
House 10:  29.89° Sagittarius
House 11:  23.32° Capricorn
House 12:  21.38° Aquarius
```

### ✅ houses Command - JSON Format
```json
{
    "input": {
        "confidence": 0.8,
        "timezone": "Asia/Jerusalem",
        "coordinates": {
            "lat": 31.8952532,
            "lon": 34.8105616
        }
    },
    "house_system": "Placidus",
    "houses": [
        {
            "house": 1,
            "longitude": 359.8168829361804,
            "sign": "Pisces",
            "degree": 29.816882936180377
        },
        ...
    ]
}
```

### ✅ arabic-parts Command - Table Format
```
━━━ Arabic Parts (Жребии) ━━━
Date: 1982-01-08 08:30:00 UTC
Location: 31.8953, 34.8106

Point             │ Sign        │ Degree   │ Longitude
──────────────────┼─────────────┼──────────┼──────────
Lilith            │ Sagittarius │  29.31°  │  269.31°
Vertex            │ Libra       │   6.20°  │  186.20°
East Point        │ Gemini      │  29.82°  │   89.82°
Part of Fortune   │ Virgo       │   9.25°  │  159.25°
Part of Spirit    │ Libra       │  20.38°  │  200.38°
```

## Architecture Verification

### Swiss Ephemeris Integration (✅ Verified)
- **astro_adapter.py** → `swe.calc_ut()` for planets
- **house_systems.py** → `swe.houses()` for house cusps
- **astro_adapter.py** → `calc_special_points()` for Arabic Parts

### Data Flow (✅ Verified)
```
main.py
  ↓
normalize_input() → InputContext
  ↓
natal_calculation(utc_dt, lat, lon, extended=True)
  ↓
{
  "houses": [359.82, 38.33, ...],          ← swe.houses()
  "special_points": {                       ← calc_special_points()
    "Part of Fortune": 159.25,
    "Part of Spirit": 200.38,
    "Lilith": 269.31,
    "Vertex": 186.20,
    "East Point": 89.82
  }
}
  ↓
get_planet_sign() + get_planet_degree_in_sign() → formatting
  ↓
Output (table/json/degrees)
```

### Converter Functions (✅ Verified)
- **Primary source:** `src/core/dignities.py`
  - `get_planet_sign(lon)` → "Aries", "Taurus", etc.
  - `get_planet_degree_in_sign(lon)` → 0-30

- **Usage verified:**
  - ✅ horary.py - uses correct import
  - ✅ main.py houses - now uses correct import
  - ✅ main.py arabic_parts - now uses correct import
  - ⚠️ chart_converter.py - has duplicates (can be cleaned up later)
  - ⚠️ output_formatter.py - uses inline `lon % 30` (can be cleaned up later)

## Status: Fixed & Tested

**Original Issues:**
1. ❌ `houses` command - ImportError
2. ❌ `arabic-parts` command - ImportError

**After Fixes:**
1. ✅ `houses` command - All 3 formats working (table, degrees, json)
2. ✅ `arabic-parts` command - Both formats working (table, json)
3. ✅ No import errors
4. ✅ Pylance: 0 errors
5. ✅ All calculations verified against birth data (8 Jan 1982, 10:30, Rehovot)

## Next Steps (Optional Code Quality Improvements)

1. **Remove duplicates** in `chart_converter.py`:
   - `sign_from_longitude()` → use `get_planet_sign()`
   - `degree_in_sign()` → use `get_planet_degree_in_sign()`

2. **Replace inline calculations** in `output_formatter.py`:
   - `lon % 30` → use `get_planet_degree_in_sign(lon)`

3. **Add tests** for CLI commands:
   - `test_houses_command()` 
   - `test_arabic_parts_command()`

## User Request Status

From user's original request (v0.1-0.3):
- ✅ **Координаты 12 домов** - `houses` command working with 3 formats
- ✅ **Арабские точки** - `arabic-parts` command working
  - Part of Fortune (день/ночь формула)
  - Part of Spirit
  - Lilith (True Black Moon)
  - Vertex
  - East Point
- ❌ **Сравнение релокационных карт** - needs implementation
- ❌ **Прозерпина** - needs implementation
- ⚠️ **Ректификация** - exists as stub, needs enhancement
