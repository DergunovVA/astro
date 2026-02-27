# System Analysis Report

## Import Graph and Dependencies

### Swiss Ephemeris Integration Points

**4 files use Swiss Ephemeris directly:**

1. **src/modules/astro_adapter.py** - MAIN calculation hub
   - `calc_planets_raw(jd)` → calls `swe.calc_ut()` for planets
   - `calc_planets_extended(jd)` → extended with retrograde status
   - `calc_special_points()` → Part of Fortune, Black Moon Lilith, Vertex
   - `swe.julday()` → datetime → Julian Day conversion

2. **src/modules/house_systems.py** - House calculations
   - `swe.houses(jd, lat, lon)` → 7 different house systems
   - Placidus, Koch, Regiomontanus, Campanus, Topocentric, Equal, Whole Sign

3. **src/calc/sidereal.py** - Sidereal calculations
   - Tropical ↔ Sidereal conversions

4. **src/core/houses_math.py** - House math utilities
   - Uses swe for house-related calculations

### Data Flow Architecture

```
INPUT → input_pipeline → astro_adapter → interpretation_layer → output
  ↓                           ↓                    ↓                 ↓
  parser              Swiss Ephemeris         Core Math         Formatter
  geocoding           (swe.calc_ut)           (dignities)       (tables/json)
  timezone            (swe.houses)            (aspects)
```

### Converter Functions (lon → sign/degree)

**PRIMARY SOURCE (canonical):**
- `src/core/dignities.py`:
  - `get_planet_sign(longitude)` → str (e.g., "Aries")
  - `get_planet_degree_in_sign(longitude)` → float (0-30)

**DUPLICATES (should be removed):**
- `src/dsl/chart_converter.py`:
  - `sign_from_longitude(longitude)` - DUPLICATE
  - `degree_in_sign(longitude)` - DUPLICATE

**INLINE USAGE (should use dignities.py):**
- `src/modules/output_formatter.py` line 353: `lon % 30`

**CORRECT USAGE:**
- `src/modules/horary.py` - imports and uses `get_planet_sign()` ✅
- `src/core/dignities.py` - uses its own functions ✅

### Import Style

The project uses `sys.path` manipulation (in `main.py` lines 12-15):
```python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))
```

This allows imports like:
- `from modules.astro_adapter import natal_calculation`
- `from core.dignities import get_planet_sign`

**All internal imports are CORRECT and working.**

## Broken Commands Analysis

### Command: `houses`
**Location:** main.py line 689  
**Error:** `ImportError: cannot import name 'lon_to_sign_deg' from 'src.core.core_geometry'`  
**Issue:** Function doesn't exist in core_geometry.py

**Current code (broken):**
```python
from src.core.core_geometry import lon_to_sign_deg
...
"sign": lon_to_sign_deg(houses_data[i])[0],
"degree": lon_to_sign_deg(houses_data[i])[1],
```

**Fix needed:**
```python
from src.core.dignities import get_planet_sign, get_planet_degree_in_sign
...
"sign": get_planet_sign(houses_data[i]),
"degree": get_planet_degree_in_sign(houses_data[i]),
```

### Command: `arabic_parts`
**Location:** main.py line 779  
**Error:** Same as above - `ImportError: cannot import name 'lon_to_sign_deg'`

**Fix:** Same pattern as houses command

## Test Results

✅ **Base natal command works:** 16KB output, all calculations functioning
❌ **houses command:** Import error
❌ **arabic_parts command:** Import error

## Critical Paths Verification

### Path 1: Natal Chart Calculation
```
main.py → normalize_input() → natal_calculation()
  → calc_planets_extended() → swe.calc_ut()
  → calc_houses() → swe.houses()
  → calc_special_points() → Part of Fortune
```
**Status:** ✅ WORKING (verified with test)

### Path 2: House Display
```
main.py houses → natal_calculation() → houses data
  → lon_to_sign_deg() [BROKEN - function doesn't exist]
```
**Status:** ❌ BROKEN - needs fix

### Path 3: Arabic Parts Display
```
main.py arabic_parts → natal_calculation(extended=True)
  → calc_special_points() → Part of Fortune, Part of Spirit
  → lon_to_sign_deg() [BROKEN]
```
**Status:** ❌ BROKEN - needs fix

### Path 4: Converter Usage
**Multiple uses across codebase:**
- ✅ horary.py - uses correct import
- ✅ dignities.py - internal usage correct
- ⚠️ chart_converter.py - has duplicates
- ⚠️ output_formatter.py - uses inline calculation

## Recommendations

### Immediate Fixes (Priority 1)
1. Fix `houses` command import in main.py line 713
2. Fix `arabic_parts` command import in main.py line 806
3. Update usage from `lon_to_sign_deg()[0/1]` to separate function calls

### Code Quality (Priority 2)
1. Remove duplicate converters from chart_converter.py
2. Replace inline `lon % 30` in output_formatter.py
3. Consolidate all converter usage to dignities.py

### New Features (Priority 3)
1. ✅ Houses display - EXISTS, just needs fix
2. ✅ Arabic Parts display - EXISTS, just needs fix
3. ❌ Relocation comparison - needs implementation
4. ❌ Proserpina (hypothetical planet) - needs implementation
5. ⚠️ Rectification - exists as stub, needs enhancement
