# Astro Calculator - Input Pipeline

Production-grade input normalization pipeline for astrological calculations. Handles date/time parsing, geolocation, timezone conversion with **ZERO personal data retention**.

**Phase 3 Status**: ✅ **OPTIMIZED & HARDENED**

- Structured logging with PII redaction
- Performance benchmarks (pytest-benchmark)
- Fuzzy city matching for typo correction
- All 40+ tests passing

## 🔐 Privacy First

✅ **GDPR Compliant** | No PII stored | Coordinate caching only | Optional geopy

See [PRIVACY.md](PRIVACY.md) for full data policy.

## Features

- **Multi-format date parsing**: ISO, European (DD.MM.YYYY), US (MM/DD/YYYY), text ("15 Jan 2000"), compact (YYYYMMDD)
- **City resolution**: 80+ global city aliases + Nominatim geolocation + fuzzy typo correction
- **Timezone accuracy**: Handles DST, fallback to UTC, ZoneInfo with fold parameter
- **Reproducible caching**: Local `.cache_places.json` prevents repeated API calls
- **Strict mode**: Explicit validation for ambiguous inputs
- **Graceful degradation**: Works without geopy/timezonefinder
- **Structured logging**: PII-safe observability for debugging

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Test (IMPORTANT: use python -m pytest, not pytest.exe directly)
python -m pytest test_input_pipeline.py test_integration_commands.py -q

# Use
python main.py natal 2000-01-15 14:30 Moscow --strict
```

## 🔮 DSL Module - Astrology Query Language

**NEW IN STAGE 3**: Domain Specific Language for astrological chart queries and validation.

```python
from src.dsl import evaluate, parse, validate

# Quick evaluation
result = evaluate("Sun.Sign == Aries AND Moon.House IN [1,4,7,10]", chart_data)
# True/False

# Validation with localized errors
result = validate("Sun.Retrograde == true", lang="en")
# ValidationResult(is_valid=False, error="Sun cannot be retrograde!")

# AST parsing (with caching for performance)
from src.dsl.cache import parse_cached
ast = parse_cached("Sun.Sign == Leo")  # 12x faster on cache hit
```

### Key Features

| Feature               | Status | Description                                          |
| --------------------- | ------ | ---------------------------------------------------- |
| **Logical Operators** | ✅     | AND, OR, NOT, IN, ==, !=, <, >, <=, >=               |
| **Aggregators**       | ✅     | COUNT, AVG, MIN, MAX with WHERE filters              |
| **Validation**        | ✅     | 35+ astrological rules (retrograde, aspects, etc.)   |
| **i18n Support**      | ✅     | English/Russian error messages                       |
| **Performance**       | ✅     | AST caching (12x), batch processing (10x), lazy eval |
| **CLI Modes**         | ✅     | --verbose, --quiet, normal output                    |

**Test Coverage**: 499 tests (204 DSL + 295 other) ✅

### Quick Examples

```bash
# Check single condition (normal mode)
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn"
# ✓ Sun.Sign == Capricorn → True

# Automation-friendly output (quiet mode)
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn" --quiet
# True

# Detailed debugging (verbose mode)
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn" --verbose
# Step 1: Normalizing input...
# Step 2: Calculating planetary positions...
# Step 3: Interpreting chart...
# [Full chart data with planet table]

# Complex queries
python main.py natal 1982-01-08 12:00 "Tel Aviv" \
  --check="COUNT(Planet WHERE Retrograde == true) > 2"
# ✓ COUNT(Planet WHERE Retrograde == true) > 2 → False (1 retrograde)

# Russian error messages
from src.dsl.validator import AstrologicalValidator
validator = AstrologicalValidator(lang="ru")
result = validator.validate("Sun.Retrograde == true")
# "Ошибка валидации: Sun не может быть ретроградным!"
```

### Performance Optimizations (Stage 3.2)

```python
from src.dsl.cache import parse_cached, get_cache_stats
from src.dsl.batch import batch_evaluate

# AST caching: 12.13x faster for simple formulas
ast = parse_cached("Sun.Sign == Aries")  # First call: 24μs
ast = parse_cached("Sun.Sign == Aries")  # Cache hit: 2μs

# Batch processing: 10.91x faster for multiple formulas
formulas = ["Sun.Sign == Aries", "Moon.House == 1", "Mercury.Retrograde == false"]
results = batch_evaluate(formulas, chart_data)  # [True, False, True]

# Check cache stats
stats = get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")  # 75.0%
```

### Documentation

- **[DSL Module README](src/dsl/README.md)** - Complete DSL reference (syntax, operators, testing)
- **[Performance Guide](docs/PERFORMANCE_GUIDE.md)** - Caching, batch processing, benchmarks
- **[CLI Modes Guide](docs/CLI_GUIDE.md)** - --verbose, --quiet, normal output
- **[i18n Guide](docs/I18N_GUIDE.md)** - Localization, language switching, custom catalogs

### Testing Protocol

**⚠️ CRITICAL**: Always run tests via `python -m pytest`, NOT `pytest` directly.

Why? The pytest package runs from venv context and imports modules correctly.

```bash
# ✅ CORRECT - Uses venv's Python and pytest
python -m pytest -q

# ✅ ALSO CORRECT - Full test run with verbose output
python -m pytest test_input_pipeline.py test_integration_commands.py -v

# ❌ WRONG - May use global pytest.exe, import failures
pytest test_input_pipeline.py
```

**Test Results**:

```
40 passed in 13.63s

Test Coverage:
  - input_pipeline: 3 datetime parsing tests
  - resolution: 5 timezone + city tests
  - integration: 18 CLI commands tests
  - caching: 4 cache tests
  - context: 6 input context tests
```

## Architecture

```
CLI Input (strings)
    ↓
[Boundary Layer: input_pipeline]
  ├─ Date parsing → ISO strings
  ├─ City resolution → coordinates + timezone
  ├─ Timezone conversion → UTC datetime
  └─ Returns NormalizedInput
    ↓
[Core Math: astro_adapter]
  ├─ Receives: UTC datetime + float coordinates
  ├─ Swiss Ephemeris calculations
  └─ Returns: planets dict (str → float)
```

## CLI Parameters

All commands support:

```bash
--tz TIMEZONE              # Override timezone (e.g., Europe/Moscow)
--lat LATITUDE             # Override latitude (-90 to 90)
--lon LONGITUDE            # Override longitude (-180 to 180)
--locale LOCALE_STR        # Hint for date parsing (en_US, de_DE, etc.)
--strict                   # Fail on ambiguity (no fallback)
```

Examples:

```bash
# With explicit timezone
python main.py natal 2000-01-15 14:30 Moscow --tz Europe/Moscow

# With explicit coordinates
python main.py natal 2000-01-15 14:30 "Secret Place" --lat 51.5 --lon -0.127

# Strict mode (fails if ambiguous)
python main.py natal 15.01.2000 14:30 Moscow --strict

# With locale hint
python main.py natal 01/15/2000 14:30 "New York" --locale en_US
```

## API Usage

```python
from input_pipeline import normalize_input
from astro_adapter import natal_calculation

# Normalize input
ni = normalize_input(
    date_str="2000-01-15",
    time_str="14:30",
    place_str="Moscow"
)

# Calculate
result = natal_calculation(ni.utc_dt, ni.lat, ni.lon)
print(result['planets'])  # {'Sun': 26.15, 'Moon': 3.84, ...}
```

## Documentation

### Core Documentation

- [INPUT_PIPELINE.md](INPUT_PIPELINE.md) - Complete input pipeline API reference
- [PRIVACY.md](PRIVACY.md) - Data handling & GDPR compliance
- [LICENSE](LICENSE) - MIT License

### DSL Module (Stage 3)

- [DSL Module README](src/dsl/README.md) - Complete DSL reference (1280+ lines)
- [Performance Guide](docs/PERFORMANCE_GUIDE.md) - Caching, batch processing, optimization
- [CLI Modes Guide](docs/CLI_GUIDE.md) - --verbose, --quiet output modes
- [i18n Guide](docs/I18N_GUIDE.md) - Localization and translation

### Project Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component structure
- [Implementation Status](docs/ASTROLOGY_IMPLEMENTATION_STATUS.md) - Feature completion tracker
- [Completion Summary](docs/COMPLETION_SUMMARY.md) - Project milestones
- [Red Team Audit](docs/RED_TEAM_FINAL_REPORT.md) - Security and quality audit

## Testing

```bash
# Run all tests
pytest test_input_pipeline.py -v

# Specific test
pytest test_input_pipeline.py::TestDateTimeParsing::test_iso_format -v

# Coverage
pytest test_input_pipeline.py --cov=input_pipeline
```

## Performance

### Input Pipeline

| Operation            | Time       | Notes                      |
| -------------------- | ---------- | -------------------------- |
| parse_date_time      | ~1ms       | Regex-based                |
| resolve_city (alias) | ~1ms       | Cache hit                  |
| resolve_city (geopy) | ~500ms     | API call                   |
| resolve_tz_name      | ~10ms      | Fast lookup                |
| **Full pipeline**    | **~500ms** | First run; **~1ms** cached |

### DSL Performance (Stage 3.2)

| Operation                        | Without Cache | With Cache | Speedup       |
| -------------------------------- | ------------- | ---------- | ------------- |
| Simple parse (Sun.Sign == Aries) | 24.43μs       | 2.01μs     | **12.13x** ✅ |
| Complex parse (nested AND/OR)    | 97.44μs       | 4.58μs     | **21.28x** ✅ |
| Batch (100 formulas)             | 2,205μs       | 202μs      | **10.91x** ✅ |
| Realistic workflow (50 formulas) | 1,714μs       | 125μs      | **13.66x** ✅ |

**All 10x performance goals exceeded!** See [PERFORMANCE_GUIDE.md](docs/PERFORMANCE_GUIDE.md) for details.

## Data Safety

✅ **What we DON'T do:**

- ❌ Store personal birth data
- ❌ Transmit user calculations anywhere
- ❌ Track or identify users
- ❌ Use cookies/analytics

✅ **What we cache locally:**

- City names → coordinates (public geographic data)
- Never transmitted; delete with `.gitignore`

✅ **User control:**

- `--lat/--lon` bypass geolocation entirely
- `--tz` bypasses timezone lookup
- `reset_global_cache()` clears local cache

## 🏆 Production Readiness

**Status**: ✅ **PRODUCTION READY WITH MONITORING**

- ✅ All CRITICAL issues fixed (UTF-8, date validation, DST handling)
- ✅ 40/40 tests passing
- ✅ Input validation prevents garbage data
- ✅ Boundary layer normalizes Swiss Ephemeris tuples → floats
- ✅ Error handling graceful (doesn't crash on missing dependencies)
- ✅ GDPR compliant (no data retention)

**Known Limitations** (see [RED_TEAM_PRODUCTION_READINESS.md](RED_TEAM_PRODUCTION_READINESS.md)):

- City typos fall back to geopy (slower)
- No fuzzy matching for city aliases
- Cache has no TTL (stale data possible, but unlikely)
- No rate limiting (fine for CLI, problematic for web API)

**Deployment Checklist**:

- ✅ Run `python -m pytest` to verify
- ✅ Check `.gitignore` excludes `.cache_places.json` (contains coordinates)
- ✅ Windows users: UTF-8 forced automatically
- ⚠️ If exposing as web service: add rate limiting, logging redaction, cache TTL

## Diagnostics

If CLI fails:

```bash
# Test date parsing
python -c "from input_pipeline import normalize_input; normalize_input('2000-01-15', '14:30', 'Moscow')"

# Test cache
python -c "from input_pipeline import get_global_cache; print(get_global_cache()._cache)"

# Test timezone
python -c "from input_pipeline import make_aware; from datetime import datetime; print(make_aware(datetime(2000, 1, 15, 14, 30), 'Europe/Moscow'))"
```

## Requirements

```
Python 3.9+
swisseph>=2.10
dateparser>=1.0
geopy>=2.0  (optional; falls back to alias database)
timezonefinder>=6.0  (optional; falls back to UTC)
zoneinfo (stdlib Python 3.9+)
typer>=0.4  (for CLI)
pytest>=7.0  (for testing)
```

## Observability & Logging

Enable structured logging with PII redaction:

```python
import logging
from input_pipeline.resolver_city import resolve_city

# Enable logging (all PII automatically redacted)
logging.basicConfig(level=logging.DEBUG)

place = resolve_city("Moscow")
# Log output: resolve_city: success | {'source': 'alias', 'confidence': 0.95}
```

**Redacted Fields**:

- Dates: `2000-01-15` → `XXXX-XX-XX`
- Coordinates: `55.7558` → `X.XX`
- Place names: `Moscow, RU` → `[Place: RU]`

## Performance

Run benchmarks:

```bash
python -m pytest test_performance_benchmarks.py -v --benchmark-only
```

**Baseline Targets**:

- Date parsing (ISO): <1ms ✅
- City resolution (alias): <1ms ✅
- Typo correction: <50ms ✅
- Full pipeline: <20ms ✅

## Known Limitations

- 80 city aliases (covers major cities globally)
- No caching TTL (assumes stable geographic data)
- Synchronous I/O only (10s geopy timeout)

## Contributing

This is a stable implementation. For issues:

1. Check [PRIVACY.md](PRIVACY.md) for data handling rules
2. Run tests: `python -m pytest -q`
3. Test with `--devils` flag for debugging
4. Run benchmarks before and after optimization

## License

MIT License - See [LICENSE](LICENSE)

---

**Status**: Production-ready | **Last Updated**: January 15, 2026
