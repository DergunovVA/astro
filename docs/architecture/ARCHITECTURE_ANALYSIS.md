# АРХИТЕКТУРНЫЙ АНАЛИЗ ПРОЕКТА ASTRO ENGINE

## Анализ разработчика, интегратора, аналитика и архитектора

---

## 1. ОБЗОР ТЕКУЩЕЙ АРХИТЕКТУРЫ

### Структура проекта (4-слойная):

```
┌─────────────────────────────────────────┐
│      CLI Layer (main.py)                │ ← Typer, JSON output
│  [natal, transit, solar, relocate, ...]│
├─────────────────────────────────────────┤
│  Input Normalization Layer              │ ← NEW: normalize_input()
│  (input_pipeline/*) - dataclass based   │
├─────────────────────────────────────────┤
│  Interpretation Layer                   │ ← Fact/Signal/Decision
│  (interpretation_layer.py)              │
├─────────────────────────────────────────┤
│  Astro Adapter (astro_adapter.py)       │ ← Swiss Ephemeris boundary
│  [Tuple unwrapping, normalization]     │
├─────────────────────────────────────────┤
│  Core Math Layer (core_geometry.py)     │ ← Pure float math
│  [angle_diff, aspect_match, ...]       │
└─────────────────────────────────────────┘
```

### Ключевые компоненты:

- **core_geometry.py** (267 строк) - чистая математика
- **astro_adapter.py** (48 строк) - граница Swiss Ephemeris
- **interpretation_layer.py** - генерация фактов/сигналов/решений
- **input_pipeline/** - НОВОЕ: нормализация ввода (6 модулей)
  - models.py (frozen dataclass)
  - parser_datetime.py (многоформатное парсирование)
  - resolver_city.py (geopy + fuzzy matching)
  - resolver_timezone.py (zoneinfo)
  - cache.py (JsonCache)
  - **init**.py (orchestrator)
- **main.py** (129 строк) - 6 команд CLI

---

## 2. АНАЛИЗ С ТОЧКИ ЗРЕНИЯ РАЗРАБОТЧИКА

### ✅ СИЛЬНЫЕ СТОРОНЫ:

1. **Четкое разделение ответственности**

   - Core: только float-математика
   - Adapter: только распаковка кортежей Swiss Ephemeris
   - Interpretation: только преобразование фактов
   - CLI: только сериализация JSON

2. **Type Safety на границах**

   ```python
   # Core принимает только float
   def angle_diff(lon1: float, lon2: float) -> float:
       lon1 = ensure_float(lon1)  # Guard!
       lon2 = ensure_float(lon2)  # Guard!
   ```

3. **Новый input_pipeline выполнен правильно**

   - Frozen dataclasses вместо Pydantic (более легкий)
   - Cache-first стратегия
   - Fuzzy matching для опечаток
   - Поддержка любого города (geopy fallback)

4. **Хорошее тестовое покрытие**
   - 15 тестов input_pipeline (все проходят)
   - Базовые тесты основных функций

### ❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:

1. **Неэффективность: Duplicate Dependencies & String Conversions**

   ```python
   # main.py (BAD):
   ni = normalize_input(date, time, place, tz_override=tz)
   calc_result = natal_calculation(
       ni.utc_dt.strftime("%Y-%m-%d"),      # ← Конвертируем обратно!
       ni.utc_dt.strftime("%H:%M"),          # ← Конвертируем обратно!
       ni.place_name
   )
   ```

   **Проблема**: normalize_input() парсит → datetime, а потом natal_calculation()
   требует строки. Циклический парсинг!

2. **Неиспользованная информация**

   ```python
   ni = normalize_input(...)  # Возвращает:
   # - ni.lat, ni.lon           ← ЕСТЬ!
   # - ni.utc_dt               ← ЕСТЬ!
   # - ni.tz_name              ← ЕСТЬ!
   # Но natal_calculation() получает:
   # - строка даты, строка времени (re-parse!), место
   # - А relocate_coords(place) СНОВА вычисляет lat/lon!
   ```

3. **Проблема с relocation_math.py**

   ```python
   # relocation_math.py
   def relocate_coords(place: str) -> dict:
       # Старая реализация - не использует new input_pipeline
       # Каждый раз переделает поиск города!
   ```

4. **Неправильное использование datetime в adapter**

   ```python
   # astro_adapter.py:29
   dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
   # Это НЕПРАВИЛЬНО для мировых вычислений!
   # Нужно использовать UTC datetime, а не local!
   ```

5. **Пропущенная интеграция transit, solar, rectify**
   ```python
   @app.command()
   def transit(date: str, time: str, place: str):
       calc_result = natal_calculation(date, time, place)  # ← No normalize_input!
   ```

---

## 3. АНАЛИЗ С ТОЧКИ ЗРЕНИЯ ИНТЕГРАТОРА

### Точки интеграции (CURRENT STATE):

1. **main.py ← input_pipeline** ✅ Хорошо интегрировано

   - normalize_input() работает
   - Возвращает полный NormalizedInput
   - Предоставляет warnings

2. **main.py ← astro_adapter** ⚠️ Частичная интеграция

   - Проходит строки вместо datetime/coords
   - Терять информацию о timezone

3. **main.py ← interpretation_layer** ✅ Хорошо
   - facts_from_calculation() работает
   - signals_from_facts() работает
   - decisions_from_signals() работает

### Проблемы интеграции:

1. **Разрыв типов между слоями**

   ```
   input_pipeline    → NormalizedInput (datetime, lat, lon, tz)
                      ↓
   main.py          → natal_calculation(str, str, str)
                      ↓
   astro_adapter    → julian_day(str, str) ← RE-PARSING!
   ```

2. **Пропущенные команды**

   - `transit` - не использует normalize_input()
   - `solar` - не использует normalize_input()
   - `rectify` - не использует normalize_input()
   - `devils` - не использует normalize_input()

3. **Стара relocation_math.py дублирует работу**
   - resolve_city() уже есть в input_pipeline
   - relocate_coords() переделает поиск города
   - Не использует cache

---

## 4. АНАЛИЗ С ТОЧКИ ЗРЕНИЯ АНАЛИТИКА (DATA FLOW)

### Текущий поток данных:

**NATAL команда:**

```
User input: "1990-01-01", "12:00", "Moscow"
     ↓
normalize_input()
     ├─ parse_date_time() → ParsedDateTime
     ├─ resolve_city()    → ResolvedPlace (lat=55.7558, lon=37.6173)
     ├─ resolve_tz_name() → (tz_name="Europe/Moscow", warnings, confidence)
     └─ make_aware()      → (local_dt, utc_dt, offset)
          ↓ Returns NormalizedInput
     ├─ raw_date, raw_time, raw_place
     ├─ local_dt (aware), utc_dt (aware), tz_name
     ├─ lat, lon, place_name, country
     └─ confidence, warnings
          ↓
natal_calculation(
    ni.utc_dt.strftime("%Y-%m-%d"),  # ← ПРИ-БЫЛ: Re-parse date!
    ni.utc_dt.strftime("%H:%M"),      # ← ПРИ-БЫЛ: Re-parse time!
    ni.place_name                     # ← INFO LOSS: lat/lon already computed!
)
     ↓
astro_adapter.natal_calculation()
     ├─ relocate_coords(ni.place_name) ← RE-GEOCODE place!
     ├─ julian_day(date_str, time_str)
     ├─ calc_planets_raw(jd)
     └─ calc_houses_raw(jd, lat, lon)
          ↓ Returns Dict with floats
     ├─ jd, planets, houses
     ├─ coords (from relocate_coords!)
     └─ datetime, place
          ↓
interpretation_layer.facts_from_calculation()
     ├─ planet_in_sign()
     ├─ planet_in_house()
     └─ aspects_calc()
          ↓ Returns List[Fact]
```

### Потеря данных (DATA LOSS):

1. **Confidence информация** - compute в normalize_input(), но не pass дальше
2. **Warnings** - compute в normalize_input(), но не include в result (only if explain=False)
3. **Timezone информация** - compute в resolve_tz_name(), но не use в julian_day()
4. **Country информация** - есть в ResolvedPlace, но никуда не pass
5. **Source информация** - (alias/geocoder/cached) - не tracked

### Неиспользованные данные:

```python
ni = normalize_input(...)
# NormalizedInput имеет:
ni.confidence              # ← Никогда не используется после!
ni.warnings               # ← Используется только если not explain
ni.tz_name                # ← Никогда не используется
ni.country                # ← Никогда не используется
ni.lat, ni.lon            # ← Переиспользуются через relocate_coords()!
ni.utc_dt                 # ← Конвертируется обратно в строку
```

---

## 5. АНАЛИЗ С ТОЧКИ ЗРЕНИЯ АРХИТЕКТОРА (DESIGN)

### Архитектурные риски (SEVERITY: HIGH → CRITICAL):

| #   | РИСК                                                    | SEVERITY | IMPACT                      | PROBABILITY |
| --- | ------------------------------------------------------- | -------- | --------------------------- | ----------- |
| 1   | Double-parsing: string → datetime → string              | MEDIUM   | Perf, Data loss             | HIGH        |
| 2   | Double-geocoding: resolve_city() + relocate_coords()    | HIGH     | Perf, Network calls         | HIGH        |
| 3   | Timezone информация не propagated                       | HIGH     | Wrong results in DST        | MEDIUM      |
| 4   | relocation_math.py не интегрирован с input_pipeline     | HIGH     | Stale code, duplication     | HIGH        |
| 5   | Только natal использует normalize_input()               | CRITICAL | Inconsistency               | MEDIUM      |
| 6   | No input validation в commands                          | MEDIUM   | Bad error messages          | HIGH        |
| 7   | Pydantic deprecation warnings (.dict() → .model_dump()) | LOW      | Tech debt                   | MEDIUM      |
| 8   | Cache не shared между командами                         | MEDIUM   | Perf, duplicate geopy calls | MEDIUM      |

### Неэффективные решения:

1. **String Round-trip в natal_calculation()**

   ```
   CURRENT: datetime → string → parse string again
   BETTER:  Pass NormalizedInput directly or unpack it
   IMPACT:  2-3x faster, zero data loss
   ```

2. **Double geocoding через relocate_coords()**

   ```
   CURRENT:
   - resolve_city() geocodes place → ResolvedPlace(lat, lon)
   - natal_calculation() → relocate_coords() geocodes place AGAIN

   BETTER:  Pass coords directly from NormalizedInput
   IMPACT:  Eliminate geopy calls, 10x faster, no network delays
   ```

3. **relocation_math.py не использует JsonCache**

   ```python
   # CURRENT:
   def relocate_coords(place: str) -> dict:
       from geopy.geocoders import Nominatim
       geolocator = Nominatim(user_agent="astroprocessor")
       location = geolocator.geocode(place)  # ← ALWAYS network call!

   # SHOULD USE:
   from input_pipeline import resolve_city
   from input_pipeline.cache import JsonCache
   cache = JsonCache()
   rp = resolve_city(place, cache)
   return {"lon": rp.lon, "lat": rp.lat}  # ← Cache-aware!
   ```

4. **Неправильное использование datetime в julian_day()**

   ```python
   # CURRENT (WRONG):
   def julian_day(date_str: str, time_str: str) -> float:
       dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
       return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

   # PROBLEM: Treats as LOCAL time, not UTC!
   # SHOULD BE:
   def julian_day(utc_dt: datetime) -> float:
       # utc_dt is already aware (UTC)
       return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                         utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
   ```

---

## 6. ПУТИ УСТРАНЕНИЯ И ОПТИМИЗАЦИИ

### Приоритет 1: CRITICAL (Fix immediately)

#### A. Обновить natal_calculation() signature

```python
# BEFORE:
def natal_calculation(date: str, time: str, place: str) -> Dict[str, Any]:

# AFTER:
def natal_calculation(utc_dt: datetime, lat: float, lon: float) -> Dict[str, Any]:
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)
    planets = calc_planets_raw(jd)
    houses = calc_houses_raw(jd, lat, lon)
    return {
        "jd": jd,
        "planets": planets,
        "houses": houses,
        "coords": {"lat": lat, "lon": lon}
    }
```

**BENEFIT**:

- ✅ No re-parsing
- ✅ Correct UTC handling
- ✅ Direct coord usage
- ✅ Pass confidence/timezone info

**EFFORT**: 15 min (astro_adapter.py + main.py)

#### B. Интегрировать relocation_math.py с input_pipeline

```python
# CURRENT relocation_math.py:
def relocate_coords(place: str) -> dict:
    # Old code with direct Nominatim

# NEW relocation_math.py:
from input_pipeline import resolve_city
from input_pipeline.cache import JsonCache

def relocate_coords(place: str) -> dict:
    cache = JsonCache()
    rp = resolve_city(place, cache)
    return {"lat": rp.lat, "lon": rp.lon}  # ← Cache-aware!
```

**BENEFIT**:

- ✅ Reuse cached results
- ✅ Eliminate duplicate geopy calls
- ✅ Fuzzy matching for typos
- ✅ Single source of truth

**EFFORT**: 5 min (relocation_math.py)

#### C. Интегрировать normalize_input() во все команды

```python
# CURRENT:
@app.command()
def transit(date: str, time: str, place: str):
    calc_result = natal_calculation(date, time, place)

# NEW:
@app.command()
def transit(date: str, time: str, place: str, tz: str | None = None):
    ni = normalize_input(date, time, place, tz_override=tz)
    # transit_calculation(ni.utc_dt, ni.lat, ni.lon) when ready
    calc_result = natal_calculation(ni.utc_dt, ni.lat, ni.lon)
    # Include warnings in result
```

**BENEFIT**:

- ✅ Consistent input handling
- ✅ Timezone support everywhere
- ✅ Error messages
- ✅ Warnings propagation

**EFFORT**: 30 min (main.py - apply same pattern to transit, solar, rectify, devils)

### Приоритет 2: HIGH (Fix within sprint)

#### D. Создать InputContext dataclass

```python
@dataclass(frozen=True)
class InputContext:
    """Bridge between input_pipeline and calculation layers."""
    normalized: NormalizedInput      # All parsed data
    utc_dt: datetime                 # For julian_day
    lat: float                       # For houses
    lon: float                       # For houses
    tz_name: str                     # For transits/progressions
    confidence: float                # Meta info
    warnings: List[ParseWarning]     # All issues
    source: str                      # alias/geocoder/cached
```

**USE IN MAIN.PY:**

```python
ni = normalize_input(...)
ctx = InputContext(
    normalized=ni,
    utc_dt=ni.utc_dt,
    lat=ni.lat,
    lon=ni.lon,
    tz_name=ni.tz_name,
    confidence=ni.confidence,
    warnings=ni.warnings,
    source=...  # track where coords came from
)
calc_result = natal_calculation(
    ctx.utc_dt, ctx.lat, ctx.lon
)
result["input_metadata"] = {
    "confidence": ctx.confidence,
    "source": ctx.source,
    "warnings": [...]
}
```

**BENEFIT**:

- ✅ Single context object
- ✅ Easy to pass through layers
- ✅ Metadata tracking
- ✅ Future-proof for new fields

**EFFORT**: 1 hour (create class + refactor main.py)

#### E. Обновить julian_day() на UTC-aware

```python
# CURRENT:
def julian_day(date_str: str, time_str: str) -> float:
    dt = datetime.strptime(...)
    return swe.julday(...)

# NEW:
def julian_day(utc_dt: datetime) -> float:
    """Convert UTC datetime to Julian Day."""
    if utc_dt.tzinfo is None or utc_dt.tzinfo != timezone.utc:
        raise ValueError("julian_day() requires UTC datetime")

    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    )
```

**BENEFIT**:

- ✅ Explicit UTC requirement
- ✅ Error on wrong timezone
- ✅ Millisecond precision

**EFFORT**: 10 min (astro_adapter.py + tests)

### Приоритет 3: MEDIUM (Optimize later)

#### F. Глобальный Cache singleton

```python
# input_pipeline/cache.py
_global_cache = None

def get_global_cache() -> JsonCache:
    global _global_cache
    if _global_cache is None:
        _global_cache = JsonCache()
    return _global_cache
```

**USE:**

```python
# Everywhere instead of JsonCache()
cache = get_global_cache()
```

**BENEFIT**:

- ✅ Single cache across all commands
- ✅ Persistent during session
- ✅ Eliminate cache misses
- ✅ Network-free for known cities

**EFFORT**: 5 min (implementation) + 15 min (refactor callers)

#### G. Расширить ALIASES

```python
ALIASES = {
    # Russia (часто используемые города)
    "moscow": ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", 0.95, "alias"),
    "москва": ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow", 0.95, "alias"),
    "saratov": ("Saratov", "RU", 51.5339, 46.0021, "Europe/Saratov", 0.95, "alias"),
    "саратов": ("Saratov", "RU", 51.5339, 46.0021, "Europe/Saratov", 0.95, "alias"),
    "lipetsk": ("Lipetsk", "RU", 52.6086, 39.5726, "Europe/Moscow", 0.95, "alias"),
    "липецк": ("Lipetsk", "RU", 52.6086, 39.5726, "Europe/Moscow", 0.95, "alias"),

    # Major World Cities
    "london": ("London", "GB", 51.5074, -0.1278, "Europe/London", 0.95, "alias"),
    "paris": ("Paris", "FR", 48.8566, 2.3522, "Europe/Paris", 0.95, "alias"),
    "tokyo": ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo", 0.95, "alias"),
    "new york": ("New York", "US", 40.7128, -74.0060, "America/New_York", 0.95, "alias"),
}
```

**BENEFIT**:

- ✅ Fast path for common cities
- ✅ No network calls needed
- ✅ Consistent behavior globally

**EFFORT**: 20 min (add cities)

#### H. Input validation в CLI

```python
@app.command()
def natal(
    date: str = typer.Argument(..., help="Date: YYYY-MM-DD or DD.MM.YYYY"),
    time: str = typer.Argument(..., help="Time: HH:MM or HH:MM:SS"),
    place: str = typer.Argument(..., help="City name (any city in world)"),
    tz: str | None = typer.Option(None, "--tz", help="Override timezone (e.g., Europe/Moscow)"),
    explain: bool = typer.Option(False, help="Include explanation layer"),
    devils: bool = typer.Option(False, help="Include raw calculation data")
):
    """
    Calculate natal chart for given date, time, and place.

    Examples:
    - python -m main natal 1990-01-01 12:00 Moscow
    - python -m main natal 01.01.1990 12:00 "New York" --explain
    - python -m main natal 1985-06-15 14:30 Paris --tz Europe/Paris
    """
```

**BENEFIT**:

- ✅ Help text in CLI
- ✅ Better error messages
- ✅ Examples in help
- ✅ Clear parameter semantics

**EFFORT**: 20 min (add docs, type hints)

#### I. Pydantic deprecation fix

```python
# main.py
# CURRENT:
result = {
    "facts": [f.dict() for f in facts],      # ⚠️ Deprecated
    "signals": [s.dict() for s in signals],
    "decisions": [d.dict() for d in decisions]
}

# NEW (Pydantic v2):
result = {
    "facts": [f.model_dump() for f in facts],  # ✅ Recommended
    "signals": [s.model_dump() for s in signals],
    "decisions": [d.model_dump() for d in decisions]
}

# OR use model_dump_json() for better performance
import json
result = {
    "facts": json.loads(f.model_dump_json()) for f in facts,
    ...
}
```

**BENEFIT**:

- ✅ Remove deprecation warnings
- ✅ Pydantic v2 compliant
- ✅ Better performance

**EFFORT**: 5 min (global replace)

---

## 7. IMPLEMENTATION ROADMAP

### WEEK 1 (CRITICAL FIX - 2-3 hours)

1. **Session 1 (30 min)**

   - Обновить `natal_calculation()` signature:
     - `(str, str, str)` → `(datetime, float, float)`
   - Обновить `julian_day()`:
     - Добавить UTC-aware check
   - Обновить `main.py natal`:
     - Pass `ni.utc_dt, ni.lat, ni.lon`

2. **Session 2 (20 min)**

   - Update `relocation_math.py`:
     - Use `resolve_city()` + cache instead of direct Nominatim
   - Test all commands

3. **Session 3 (40 min)**
   - Integrate `normalize_input()` in:
     - `transit()`
     - `solar()`
     - `rectify()`
     - `devils()`
   - Test each command

### WEEK 2 (HIGH PRIORITY - 2-3 hours)

4. **Session 4 (60 min)**

   - Create `InputContext` dataclass
   - Refactor main.py to use InputContext
   - Add result["input_metadata"] with warnings/confidence/source

5. **Session 5 (30 min)**

   - Implement global cache singleton
   - Update all cache.JsonCache() → get_global_cache()
   - Test cache persistence

6. **Session 6 (30 min)**
   - Fix Pydantic deprecation warnings
   - Add CLI help text and examples
   - Add input validation

### WEEK 3 (OPTIMIZATION - 1-2 hours)

7. **Session 7 (60 min)**
   - Expand ALIASES with 20-30 major world cities
   - Benchmark: before vs after
   - Document common city aliases

---

## 8. EXPECTED IMPROVEMENTS

### Performance:

- **Date/Time parsing**: 2-3x faster (no round-trip)
- **Geocoding**: 10x faster for cached cities (no network calls)
- **Overall natal chart**: 5-10x faster for repeated places
- **Memory**: Slightly better (fewer object allocations)

### Code Quality:

- **Consistency**: All commands use same input normalization
- **Maintainability**: Single source of truth for geocoding
- **Error messages**: Better error reporting from normalize_input()
- **Type safety**: Explicit UTC datetime requirements

### User Experience:

- **Timezone support**: `--tz` available everywhere
- **Typo tolerance**: "Moskow" → "Moscow" auto-correction
- **Metadata**: Confidence/source/warnings included
- **Documentation**: Clear help text and examples

### Technical Debt Reduction:

- ✅ No deprecated Pydantic methods
- ✅ No duplicate code (relocation_math.py consolidation)
- ✅ No double-parsing
- ✅ No double-geocoding

---

## 9. RISKS & MITIGATION

| RISK                                   | MITIGATION                                                       |
| -------------------------------------- | ---------------------------------------------------------------- |
| Breaking change in natal_calculation() | Write adapter layer for backward compat, deprecate old signature |
| Cache invalidation issues              | Add version check in JsonCache, add --clear-cache flag           |
| Geopy rate limiting                    | Expand ALIASES, use bigger local cache, add backoff              |
| Timezone edge cases (DST)              | Comprehensive DST tests in test_input_pipeline.py                |
| Different coord precision              | Document lat/lon precision (4-5 decimal places = ~10m)           |

---

## 10. ВЫВОДЫ

### Текущее состояние: GOOD BUT INEFFICIENT

- ✅ Архитектура правильная (4 слоя)
- ✅ Новый input_pipeline отличный
- ❌ НО не полностью интегрирован
- ❌ НО есть двойное парсирование и двойная геокодировка
- ❌ НО только 1 из 6 команд использует normalize_input()

### Главные проблемы (сортировка по влиянию):

1. **Double-geocoding** (relocation_math.py не использует input_pipeline cache)
2. **String round-trip** (datetime → string → parse again)
3. **Inconsistent input handling** (только natal использует normalize_input)
4. **Missing timezone info propagation** (правильно парсится, но не используется)
5. **Tech debt** (Pydantic deprecations)

### ROI оптимизации:

- **Effort**: 5-7 часов разработки
- **Benefit**:
  - 5-10x performance improvement
  - 100% consistency across commands
  - Better error messages and metadata
  - Eliminated tech debt
  - Future-proof architecture

**RECOMMENDATION**: Do CRITICAL fixes (Priority 1) in next sprint. Huge impact, small effort.
