# 🟢 STAGE 3: PERFORMANCE & UX IMPROVEMENTS

**Период:** 8-31 марта 2026 (3 недели)  
**Приоритет:** 🟢 MEDIUM  
**Статус:** 📋 PLANNED  
**Команда:** Dev Team + UX Team

---

## 🎯 ЦЕЛИ ЭТАПА

### Главная цель

Оптимизировать производительность DSL системы и улучшить пользовательский опыт через локализацию и расширенные опции.

### Конкретные цели

1. ✅ Систематическая локализация (RU/EN)
2. ✅ Оптимизация производительности DSL (10x improvement target)
3. ✅ AST caching и batch processing
4. ✅ Verbose/quiet modes для CLI

### Метрики успеха

- Localization: 100% (RU/EN)
- DSL performance: 10x faster
- Batch 100 formulas: < 500ms
- User satisfaction: Improved CLI UX

---

## 📋 ЗАДАЧИ

### Task 3.1: Systematic Localization (RU/EN)

**Приоритет:** 🟡 HIGH  
**Оценка:** 12 hours  
**Назначено:** Dev Team + i18n specialist  
**Статус:** 📋 PLANNED

#### Структура локализации

##### 3.1.1: Create i18n infrastructure

```python
# src/i18n/__init__.py
from typing import Dict, Any
import yaml
import os

class Localizer:
    """Internationalization support"""

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.messages = self._load_messages(lang)

    def _load_messages(self, lang: str) -> Dict[str, Any]:
        """Load message catalog for language"""
        locale_path = os.path.join(
            os.path.dirname(__file__),
            "locales",
            f"{lang}.yaml"
        )
        with open(locale_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, key: str, **kwargs) -> str:
        """Get localized message"""
        message = self.messages.get(key, key)
        return message.format(**kwargs) if kwargs else message

    def _(self, key: str, **kwargs) -> str:
        """Shorthand for get()"""
        return self.get(key, **kwargs)

# Global instance
_localizer = None

def get_localizer(lang: str = "en") -> Localizer:
    """Get or create global localizer"""
    global _localizer
    if _localizer is None or _localizer.lang != lang:
        _localizer = Localizer(lang)
    return _localizer

def _(key: str, **kwargs) -> str:
    """Quick access to localization"""
    return get_localizer()._(key, **kwargs)
```

##### 3.1.2: Create message catalogs

**File:** `src/i18n/locales/en.yaml`

```yaml
# English messages
errors:
  retrograde_not_allowed: "{planet} cannot be retrograde!"
  retrograde_explanation: |
    Only planets can be retrograde: Mercury, Venus, Mars, 
    Jupiter, Saturn, Uranus, Neptune, Pluto.
    {planet} is NEVER retrograde.

  house_range_error: "House number must be 1-12, got {num}"
  house_range_explanation: "In astrology, there are 12 houses in the horoscope."

  degree_range_error: "Degree must be 0-{max}°, got {degree}°"

  planet_aspect_self: "Planet cannot aspect itself!"
  planet_aspect_explanation: "Check your formula: Asp({planet1}, {planet2}, ...)"

dignities:
  ruler_error: "{planet}.Ruler == {target} makes no sense!"
  ruler_explanation: |
    A planet doesn't rule another planet.
    A planet rules a SIGN (or is in a sign it rules).

  exaltation_error: "{planet} is exalted in {correct_sign}, NOT in {wrong_sign}!"
  exaltation_list: |
    Planet exaltations:
    Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces
    Mars: Capricorn, Jupiter: Cancer, Saturn: Libra

suggestions:
  try_instead: "Try instead:"
  examples: "Examples:"

warnings:
  planet_weak: "{planet} in {dignity} in {sign}"
  planet_weak_details: "Planet is in a weak position, may manifest with difficulty."
```

**File:** `src/i18n/locales/ru.yaml`

```yaml
# Russian messages
errors:
  retrograde_not_allowed: "{planet} не может быть ретроградным!"
  retrograde_explanation: |
    Ретроградными могут быть только планеты: Mercury, Venus, Mars, 
    Jupiter, Saturn, Uranus, Neptune, Pluto.
    {planet} НИКОГДА не бывает ретроградным.

  house_range_error: "Номер дома должен быть 1-12, получено {num}"
  house_range_explanation: "В астрологии используется 12 домов гороскопа."

  degree_range_error: "Градус должен быть 0-{max}°, получено {degree}°"

  planet_aspect_self: "Планета не может иметь аспект к самой себе!"
  planet_aspect_explanation: "Проверьте формулу: Asp({planet1}, {planet2}, ...)"

dignities:
  ruler_error: "{planet}.Ruler == {target} бессмысленна!"
  ruler_explanation: |
    Планета не управляет другой планетой.
    Планета управляет ЗНАКОМ (или находится в знаке, которым управляет).

  exaltation_error: "{planet} экзальтирован в {correct_sign}, НЕ в {wrong_sign}!"
  exaltation_list: |
    Экзальтации планет:
    Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces
    Mars: Capricorn, Jupiter: Cancer, Saturn: Libra

suggestions:
  try_instead: "Попробуйте вместо этого:"
  examples: "Примеры:"

warnings:
  planet_weak: "{planet} в {dignity} в {sign}"
  planet_weak_details: "Планета в слабой позиции, может проявляться с трудом."
```

##### 3.1.3: Update Validator to use i18n

```python
# src/dsl/validator.py
from src.i18n import get_localizer

class AstrologicalValidator:
    def __init__(self, config_path=None, mode="modern", lang="en"):
        self.mode = mode
        self.lang = lang
        self.loc = get_localizer(lang)
        # ... rest of init

    def check_retrograde(self, body: str) -> Optional[ValidationResult]:
        """Check if body can be retrograde"""
        if body in self.NON_RETROGRADE_BODIES:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=self.loc._("errors.retrograde_not_allowed", planet=body),
                details=self.loc._("errors.retrograde_explanation", planet=body),
                suggestions=[
                    "Mercury.Retrograde == True",
                    "Venus.Retrograde == True",
                ]
            )
        return None
```

##### 3.1.4: Add --lang CLI parameter

```python
# main.py
@click.option('--lang', type=click.Choice(['en', 'ru']), default='en',
              help='Language for messages (en/ru)')
def validate_command(formula, date, time, place, tz, mode, lang):
    """Validate astrological formula"""
    from src.i18n import get_localizer
    loc = get_localizer(lang)

    # Use localized messages
    print(loc._("validation.checking_formula"))
    # ...
```

#### Acceptance Criteria

- ✅ i18n infrastructure created
- ✅ EN and RU catalogs complete
- ✅ Validator uses localization
- ✅ CLI --lang parameter works
- ✅ All messages localized

---

### Task 3.2: DSL Performance Optimization

**Приоритет:** 🟡 HIGH  
**Оценка:** 16 hours  
**Назначено:** Performance Team  
**Статус:** 📋 PLANNED

#### Optimization Targets

```
Target: 10x performance improvement
- Simple formula: 10ms → 1ms
- Complex formula: 50ms → 5ms
- Batch 100: 1000ms → 100ms
```

#### Optimization Strategies

##### 3.2.1: AST Caching

```python
# src/dsl/cache.py
from typing import Dict
from functools import lru_cache
from src.dsl.parser import ASTNode, parse

class ASTCache:
    """Cache parsed AST trees"""

    def __init__(self, maxsize: int = 1000):
        self._cache: Dict[str, ASTNode] = {}
        self._maxsize = maxsize

    def get(self, formula: str) -> Optional[ASTNode]:
        """Get cached AST or None"""
        return self._cache.get(formula)

    def set(self, formula: str, ast: ASTNode):
        """Cache AST for formula"""
        if len(self._cache) >= self._maxsize:
            # Remove oldest entry (FIFO)
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[formula] = ast

    def clear(self):
        """Clear cache"""
        self._cache.clear()

# Global cache
_ast_cache = ASTCache()

def parse_cached(formula: str) -> ASTNode:
    """Parse with caching"""
    ast = _ast_cache.get(formula)
    if ast is None:
        ast = parse(formula)
        _ast_cache.set(formula, ast)
    return ast
```

##### 3.2.2: Optimize Lookup Tables

```python
# src/dsl/validator.py

# BEFORE: List lookups O(n)
def is_in_rulership(planet, sign):
    rulers = self.rulers.get(sign, [])
    return planet in rulers  # O(n) lookup in list

# AFTER: Set lookups O(1)
def _build_lookup_tables(self):
    # Convert to sets for O(1) lookup
    self.ruler_lookup = {}
    for sign, planets in self.rulers.items():
        self.ruler_lookup[sign] = set(planets)  # Convert to set

def is_in_rulership(planet, sign):
    rulers = self.ruler_lookup.get(sign, set())
    return planet in rulers  # O(1) lookup in set
```

##### 3.2.3: Lazy Evaluation

```python
# src/dsl/evaluator.py

def evaluate_and(self, left_ast, right_ast, chart):
    """Short-circuit AND evaluation"""
    left_result = self._evaluate_node(left_ast, chart)
    if not left_result:
        return False  # Short-circuit, don't evaluate right
    return self._evaluate_node(right_ast, chart)

def evaluate_or(self, left_ast, right_ast, chart):
    """Short-circuit OR evaluation"""
    left_result = self._evaluate_node(left_ast, chart)
    if left_result:
        return True  # Short-circuit
    return self._evaluate_node(right_ast, chart)
```

##### 3.2.4: Batch Processing

```python
# src/dsl/batch.py

def evaluate_batch(formulas: List[str], chart: Dict) -> List[bool]:
    """Evaluate multiple formulas efficiently"""
    # Parse all formulas (with caching)
    asts = [parse_cached(f) for f in formulas]

    # Evaluate all ASTs
    results = []
    evaluator = Evaluator(chart)
    for ast in asts:
        results.append(evaluator.evaluate(ast))

    return results
```

#### Benchmarking

```python
# tests/test_performance_optimized.py

@pytest.mark.benchmark(group="optimized")
def test_ast_caching_speedup(benchmark):
    """Benchmark AST caching improvement"""
    formula = "Sun.Sign == Aries AND Moon.House == 1"

    def parse_with_cache():
        return parse_cached(formula)

    result = benchmark(parse_with_cache)
    # Should be ~10x faster on cache hit

@pytest.mark.benchmark(group="optimized")
def test_batch_processing(benchmark):
    """Benchmark batch evaluation"""
    formulas = [f"Sun.Sign == Aries" for _ in range(100)]
    chart = {...}

    result = benchmark(evaluate_batch, formulas, chart)
    # Should be < 500ms for 100 formulas
```

#### Acceptance Criteria

- ✅ AST caching implemented
- ✅ Lookup tables optimized
- ✅ Lazy evaluation implemented
- ✅ Batch processing works
- ✅ 10x performance improvement achieved

---

### Task 3.3: Verbose/Quiet CLI Modes

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 4 hours  
**Назначено:** Dev Team  
**Статус:** 📋 PLANNED

#### Implementation

```python
# main.py

@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
def validate_command(formula, verbose, quiet, **kwargs):
    """Validate formula with verbosity control"""

    if verbose:
        # Educational mode: explain everything
        print(f"📋 Formula: {formula}")
        print(f"🔍 Parsing formula...")
        ast = parse(formula)
        print(f"✅ AST: {ast}")
        print(f"🔍 Evaluating on chart...")
        result = evaluate(ast, chart)
        print(f"✅ Result: {result}")

        if validation_errors:
            print(f"\n⚠️ Validation issues found:")
            for error in validation_errors:
                print(f"  - {error.message}")
                if error.details:
                    print(f"    Details: {error.details}")
                if error.suggestions:
                    print(f"    Suggestions:")
                    for s in error.suggestions:
                        print(f"      • {s}")

    elif quiet:
        # Minimal mode: just result
        result = evaluate(formula, chart)
        print("true" if result else "false")

    else:
        # Normal mode: balanced output
        result = evaluate(formula, chart)
        print(f"Result: {result}")
        if validation_errors:
            print(f"Warnings: {len(validation_errors)}")
```

#### Examples

```bash
# Verbose mode
$ python main.py validate "Sun.Sign == Aries" --verbose
📋 Formula: Sun.Sign == Aries
🔍 Parsing formula...
✅ Parsed successfully
🔍 Evaluating on chart...
✅ Result: True
ℹ️  Sun is in Aries at 15°30'
ℹ️  No validation issues

# Quiet mode
$ python main.py validate "Sun.Sign == Aries" --quiet
true

# Normal mode
$ python main.py validate "Sun.Sign == Aries"
Result: True
```

#### Acceptance Criteria

- ✅ --verbose flag works
- ✅ --quiet flag works
- ✅ Normal mode balanced
- ✅ Educational for --verbose

---

### Task 3.4: Documentation & Examples

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 4 hours  
**Назначено:** Tech Writer  
**Статус:** 📋 PLANNED

#### Updates needed

1. Update `src/dsl/README.md` with i18n examples
2. Add performance optimization guide
3. Create user guide for verbose/quiet modes
4. Update API documentation

#### Acceptance Criteria

- ✅ All docs updated
- ✅ Examples for new features
- ✅ Performance guide created

---

## 📊 ПРОГРЕСС ВЫПОЛНЕНИЯ

### Week 1 (Mar 8-14)

```
Mon-Wed: Task 3.1 (Localization) - 12 hours
Thu-Fri: Task 3.2 start (AST caching) - 8 hours
```

### Week 2 (Mar 15-21)

```
Mon-Tue: Task 3.2 continue (Optimization) - 8 hours
Wed: Task 3.3 (Verbose/Quiet) - 4 hours
Thu-Fri: Testing & benchmarking
```

### Week 3 (Mar 22-28)

```
Mon-Tue: Task 3.4 (Documentation) - 4 hours
Wed-Thu: Integration & final testing
Fri: Stage 3 wrap-up, STAGE_3_RESULTS.md
```

---

## 🎯 EXPECTED RESULTS

### Performance

```
Before Stage 3:
- Simple formula: ~10ms
- Complex formula: ~50ms
- Batch 100: ~1000ms

After Stage 3:
- Simple formula: ~1ms (10x) ✅
- Complex formula: ~5ms (10x) ✅
- Batch 100: ~100ms (10x) ✅
```

### Localization

- ✅ Full RU/EN support
- ✅ 100+ messages localized
- ✅ CLI --lang parameter

### UX

- ✅ --verbose mode (educational)
- ✅ --quiet mode (minimal)
- ✅ Improved user experience

---

## 🔄 TRANSITION TO STAGE 4

### Prerequisites

- ✅ 10x performance improvement verified
- ✅ Localization complete
- ✅ All tests passing
- ✅ Documentation updated

### Handoff

1. Performance benchmarks documented
2. i18n guide for future contributors
3. Stage 4 planning session

---

_Created: 2026-02-20_  
_Start: 2026-03-08_  
_Target: 2026-03-31_
