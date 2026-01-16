# Astro Engine Architecture

## Core Rules (MANDATORY)

### 1. Core Math Works Only With Float Degrees

- **All internal calculations use float (degrees, 0-360 range)**
- No tuple, list, dict, string in arithmetic
- No DMS (Degrees/Minutes/Seconds) in core functions
- No radian conversions in core (only at boundary if needed)

```python
# ✅ CORRECT
def angle_diff(lon1: float, lon2: float) -> float:
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    return min(abs(lon1 - lon2) % 360, abs(lon2 - lon1) % 360)

# ❌ WRONG
def angle_diff(lon1, lon2):  # No type guard
    return (lon1 - lon2) % 360  # No ensure_float
```

### 2. Swiss Ephemeris Tuples Must Be Unpacked At Boundary

- **Astro Adapter layer only place where swe.calc_ut, swe.houses are called**
- Unpack immediately: `result[0][0]` → float
- Never pass tuple into Core functions

```python
# ✅ CORRECT (Astro Adapter)
def calc_planets_raw(jd: float) -> Dict[str, float]:
    planets = {}
    for p in [swe.SUN, swe.MOON, ...]:
        result = swe.calc_ut(jd, p)  # Returns ((lon, lat, ...), flags)
        pos_tuple = result[0]  # Unpack outer tuple
        planets[swe.get_planet_name(p)] = float(pos_tuple[0])  # Extract float
    return planets

# ❌ WRONG (passing tuple to Core)
planets = swe.calc_ut(jd, swe.SUN)  # Raw tuple
angle_diff(planets[0][0], other_lon)  # Tuple in arithmetic
```

### 3. Any Subtraction/Addition Of Angles Must Operate On Floats

- **Use `ensure_float()` before every arithmetic operation**
- Catches type errors immediately with clear message
- Non-negotiable for data integrity

```python
# ✅ CORRECT
def aspect_match(lon1: float, lon2: float, asp_angle: float) -> bool:
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    asp_angle = ensure_float(asp_angle)
    diff = angle_diff(lon1, lon2)  # Safe: both are floats
    error = abs(diff - asp_angle)  # Safe: both are floats
    return error <= 8.0

# ❌ WRONG
def aspect_match(lon1, lon2, asp_angle):
    diff = angle_diff(lon1, lon2)  # May receive tuple
    error = abs(diff - asp_angle)  # Arithmetic on unknown type
```

### 4. DMS, Tuples, Strings Are Presentation-Layer Only

- **Core: float only**
- **Interpretation: Fact objects, no math**
- **CLI: JSON serialization, formatting**

```python
# Layer separation example:
#
# Core (core_geometry.py): float → float
#   angle_diff(287.956, 190.014) → 97.942
#
# Adapter (astro_adapter.py): tuple → float
#   swe.calc_ut(jd, SUN) → {'Sun': 287.956}
#
# Interpretation (interpretation_layer.py): float → Fact object
#   facts.append(Fact(..., value="Capricorn", details={'longitude': 287.956}))
#
# CLI (main.py): Fact → JSON string
#   json.dumps(facts, ...) → {"value": "Capricorn", "details": {...}}
```

---

## Four-Layer Architecture

### Layer 1: Core Math Engine (core_geometry.py)

- **Pure mathematics**: float → float
- **Functions**: angle_diff, aspect_match, planet_in_sign, planet_in_house, normalize_longitude
- **Guard**: `ensure_float()` on all inputs
- **Tests**: Unit tests for each function, strict type checking
- **No I/O, no strings, no state**

```python
def ensure_float(value) -> float:
    """Type guard: strict conversion or error."""
    if isinstance(value, (tuple, list, dict, str)):
        raise TypeError(f"ensure_float: received {type(value).__name__}")
    return float(value)
```

### Layer 2: Astro Adapter (astro_adapter.py)

- **Bridge**: Swiss Ephemeris ↔ Core
- **Functions**: calc_planets_raw, calc_houses_raw, julian_day, natal_calculation
- **Responsibility**: Unpack tuples, normalize to float, build dictionaries
- **Returns**: Dict[str, float] for planets, List[float] for houses, Dict for metadata
- **Tests**: Integration tests with mock swe, type validation

```python
def calc_planets_raw(jd: float) -> Dict[str, float]:
    planets = {}
    for p in [swe.SUN, swe.MOON, ...]:
        result = swe.calc_ut(jd, p)  # ((lon, lat, ...), flags)
        planets[swe.get_planet_name(p)] = float(result[0][0])
    return planets
```

### Layer 3: Interpretation (interpretation_layer.py)

- **No calculations**: facts_from_calculation, signals_from_facts, decisions_from_signals
- **Transformation only**: float → Fact/Signal/Decision objects
- **Uses Core results**: calls planet_in_sign, calculate_aspects, calculate_house_positions
- **Pydantic models**: Fact, Signal, Decision (self-validating)
- **Tests**: Unit tests for mapping logic, no arithmetic

```python
def facts_from_calculation(calc_result: Dict) -> List[Fact]:
    """Transform core floats into Facts (no math)."""
    facts = []
    planets = calc_result["planets"]
    for planet, lon in planets.items():
        sign_idx = planet_in_sign(lon)  # Core function, returns int
        sign = ZODIAC_SIGNS[sign_idx]
        facts.append(Fact(
            id=f"{planet}_position",
            type="planet_in_sign",
            value=sign,
            details={"longitude": lon}
        ))
    return facts
```

### Layer 4: CLI (main.py)

- **Formatting only**: Fact/Signal/Decision → JSON
- **I/O**: typer.echo, json.dumps
- **Commands**: natal, transit, solar, relocate, devils, rectify
- **Tests**: Integration tests, CLI response validation
- **No calculations, no business logic**

```python
@app.command()
def natal(date: str, time: str, place: str):
    calc_result = natal_calculation(date, time, place)  # Adapter
    facts = facts_from_calculation(calc_result)  # Interpretation
    signals = signals_from_facts(facts)
    decisions = decisions_from_signals(signals)
    result = {
        "facts": [f.model_dump() for f in facts],  # Convert to dict
        "signals": [s.model_dump() for s in signals],
        "decisions": [d.model_dump() for d in decisions]
    }
    typer.echo(json.dumps(result, indent=2))  # Format and output
```

---

## Type Safety

### Strict Type Hierarchy

```
Swiss Ephemeris (raw)
    ↓ [unpack tuple]
float (degrees)
    ↓ [ensure_float guard]
Core Math (angle_diff, aspects, houses)
    ↓ [no calculation, only mapping]
Fact/Signal/Decision objects
    ↓ [serialize to dict]
JSON string
    ↓ [output to CLI]
User
```

### ensure_float Everywhere

- **Core**: All function inputs validated
- **Adapter**: Results from swe explicitly converted
- **Interpretation**: Passed through guards before use in Core functions
- **CLI**: No arithmetic (serialization only)

### Type Validation Tests

```python
def test_core_functions_reject_tuple():
    with pytest.raises(TypeError):
        angle_diff((287.95, 0.0), 190.01)

def test_core_functions_reject_string():
    with pytest.raises(TypeError):
        planet_in_sign("287.95")

def test_adapter_always_returns_float():
    planets = calc_planets_raw(jd)
    for name, lon in planets.items():
        assert isinstance(lon, float), f"{name}: {type(lon)}"

def test_houses_always_floats():
    houses = calc_houses_raw(jd, lat, lon)
    for h in houses:
        assert isinstance(h, float), f"House: {type(h)}"
```

---

## TDD Workflow (Mandatory for New Calculations)

### 1. Write Failing Test

```python
def test_angle_diff_returns_float():
    result = angle_diff(287.956, 190.014)
    assert isinstance(result, float)
    assert 97.9 < result < 97.95
```

### 2. Describe Expected Types

```
INPUT:  lon1: float (0-360), lon2: float (0-360)
OUTPUT: float (0-180)
PROPERTIES:
  - Symmetric: angle_diff(a, b) == angle_diff(b, a)
  - Normalized: 0 <= result <= 180
  - Never negative, never > 180
```

### 3. Write Code

```python
def angle_diff(lon1: float, lon2: float) -> float:
    lon1 = ensure_float(lon1)
    lon2 = ensure_float(lon2)
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)
```

### 4. Run Test

```bash
pytest test_core_geometry.py::test_angle_diff_returns_float -v
```

---

## File Structure

```
astro/
├── core_geometry.py          # Core math: float → float
│   ├── ensure_float()        # Type guard
│   ├── angle_diff()
│   ├── aspect_match()
│   ├── planet_in_sign()
│   ├── planet_in_house()
│   └── calculate_aspects()
├── astro_adapter.py          # Swiss Ephemeris → float
│   ├── calc_planets_raw()
│   ├── calc_houses_raw()
│   ├── julian_day()
│   └── natal_calculation()
├── interpretation_layer.py   # float → Fact/Signal/Decision
│   ├── facts_from_calculation()
│   ├── signals_from_facts()
│   └── decisions_from_signals()
├── facts_models.py           # Pydantic: Fact
├── signals_models.py         # Pydantic: Signal
├── decisions_models.py       # Pydantic: Decision
├── main.py                   # CLI: Fact → JSON
├── test_core_geometry.py     # Unit: core math
├── test_astro_adapter.py     # Integration: adapter
├── test_interpretation.py    # Unit: facts/signals
└── test_cli.py              # Integration: CLI
```

---

## Example: Full Chain (1982-01-08 13:40 Moscow)

### Input

```
date="1982-01-08", time="13:40", place="Moscow"
```

### Core Chain

```
1. Adapter: Unpack Swiss Ephemeris
   swe.calc_ut(jd, SUN) → ((287.956, -0.0001, ...), 260) → 287.956 (float)

2. Core: Calculate positions and aspects
   angle_diff(287.956, 190.014) → 97.942
   aspect_match(287.956, 190.014, 90.0, 8.0) → (True, 7.942)

3. Interpretation: Create facts
   planet_in_sign(287.956) → 9 → "Capricorn"
   planet_in_house(287.956, [113.63, 127.49, ...]) → 6
   Fact(id="Sun_position", value="Capricorn", details={"longitude": 287.956, "house": 6})

4. CLI: Serialize and output
   json.dumps({"facts": [{"id": "Sun_position", "value": "Capricorn", ...}]})
```

### Output (formatted)

```json
{
  "facts": [
    {
      "id": "Sun_position",
      "type": "planet_in_sign",
      "value": "Capricorn",
      "details": {"longitude": 287.956, "house": 6}
    }
  ],
  "signals": [...],
  "decisions": [...]
}
```

---

## Notes

- **No magic numbers in Core**: all orbs, zodiac divisions, house systems must be configurable
- **No timezone handling in Core**: should be in Adapter or separate module
- **No DST in Core**: Adapter responsibility
- **Devil's Mode**: exposes raw floats and internal weights, same Core logic
- **Explain/Fix Layer**: optional, read-only access to results, no influence on calculations
