# 🟡 STAGE 2: QUALITY ASSURANCE

**Период:** 22 февраля - 7 марта 2026 (2 недели)  
**Приоритет:** 🟡 HIGH  
**Статус:** 📋 PLANNED  
**Команда:** QA Team + Dev Team

---

## 🎯 ЦЕЛИ ЭТАПА

### Главная цель

Расширить покрытие тестами edge cases, профилировать производительность и создать performance baselines.

### Конкретные цели

1. ✅ Расширить test coverage для edge cases (Chiron, Lilith, outer planets)
2. ✅ Профилировать DSL систему
3. ✅ Создать performance baselines и benchmarks
4. ✅ Создать dataset из реальных натальных карт

### Метрики успеха

- Edge case coverage: 100%
- Performance baseline: Established
- DSL execution: < 50ms per formula
- Dataset: 100+ real charts

---

## 📋 ЗАДАЧИ

### Task 2.1: Expand Edge Case Tests

**Приоритет:** 🟡 HIGH  
**Оценка:** 8 часов  
**Назначено:** QA Team  
**Статус:** 📋 PLANNED

#### Категории edge cases

##### 2.1.1: Minor Bodies (Chiron, Lilith, etc.)

**Файл:** `tests/test_edge_cases_minor_bodies.py`

```python
"""Test minor bodies and special points"""

import pytest
from src.dsl.lexer import tokenize
from src.dsl.parser import parse
from src.dsl.evaluator import evaluate

class TestMinorBodies:
    """Tests for Chiron, Lilith, True Node, etc."""

    def test_chiron_no_classical_dignities(self):
        """Chiron не имеет классических достоинств"""
        chart = {
            "planets": {
                "Chiron": {"Sign": "Aries", "House": 1, "Dignity": None}
            }
        }
        # Should not raise error
        result = evaluate("Chiron.Sign == Aries", chart)
        assert result is True

    def test_lilith_as_calculated_point(self):
        """Lilith - это вычисляемая точка, не планета"""
        chart = {
            "points": {
                "Lilith": {"Sign": "Scorpio", "House": 8}
            }
        }
        result = evaluate("Lilith.Sign == Scorpio", chart)
        assert result is True

    def test_true_node_vs_mean_node(self):
        """Различие между True Node и Mean Node"""
        chart = {
            "points": {
                "TrueNode": {"Sign": "Cancer", "Degree": 15.5},
                "MeanNode": {"Sign": "Cancer", "Degree": 14.8}
            }
        }
        # Both should be accessible
        assert evaluate("TrueNode.Sign == Cancer", chart)
        assert evaluate("MeanNode.Sign == Cancer", chart)
```

##### 2.1.2: Outer Planets Exaltations

**Файл:** `tests/test_edge_cases_outer_planets.py`

```python
"""Test controversial dignities for outer planets"""

class TestOuterPlanetDignities:
    """Uranus, Neptune, Pluto dignities are debated"""

    def test_uranus_modern_rulership(self):
        """Uranus как современный управитель Aquarius"""
        validator = AstrologicalValidator(mode="modern")
        # Should accept Uranus ruling Aquarius
        result = validator.check_dignity_sign_match(
            "Uranus", "Aquarius", "Rulership"
        )
        assert result is None  # No error

    def test_uranus_traditional_no_rulership(self):
        """В традиционной астрологии Uranus не управляет знаками"""
        validator = AstrologicalValidator(mode="traditional")
        # Should warn or reject
        result = validator.check_dignity_sign_match(
            "Uranus", "Aquarius", "Rulership"
        )
        assert result is not None  # Warning expected

    def test_pluto_exaltation_debate(self):
        """Экзальтация Pluto не определена классически"""
        validator = AstrologicalValidator(mode="modern")
        result = validator.check_exaltation("Pluto", "Leo")
        # Should be warning, not error
        assert result.level == ValidationLevel.WARNING
```

##### 2.1.3: Boundary Conditions

**Файл:** `tests/test_edge_cases_boundaries.py`

```python
"""Test boundary conditions and extreme values"""

class TestBoundaryConditions:
    """Edge cases for degrees, houses, aspects"""

    def test_degree_29_59(self):
        """Планета на последнем градусе знака"""
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries", "Degree": 29.99, "House": 1}
            }
        }
        result = evaluate("Sun.Degree > 29", chart)
        assert result is True

    def test_degree_0_00(self):
        """Планета точно на 0° знака"""
        chart = {
            "planets": {
                "Moon": {"Sign": "Taurus", "Degree": 0.0, "House": 2}
            }
        }
        result = evaluate("Moon.Degree == 0", chart)
        assert result is True

    def test_retrograde_at_station(self):
        """Планета на станции (начало/конец ретроградности)"""
        chart = {
            "planets": {
                "Mercury": {
                    "Retrograde": True,
                    "Speed": 0.001  # Almost stationary
                }
            }
        }
        result = evaluate("Mercury.Retrograde == True", chart)
        assert result is True
```

##### 2.1.4: Complex Formulas

**Файл:** `tests/test_edge_cases_complex.py`

```python
"""Test complex formula combinations"""

class TestComplexFormulas:
    """Multi-planet, multi-condition formulas"""

    def test_multiple_planets_and_conditions(self):
        """Формула с несколькими планетами и условиями"""
        formula = """
        (Sun.Sign == Leo AND Sun.House == 5) OR
        (Moon.Sign == Cancer AND Moon.House == 4) OR
        (Jupiter.Dignity IN [Rulership, Exaltation])
        """
        chart = {
            "planets": {
                "Sun": {"Sign": "Aries", "House": 1},
                "Moon": {"Sign": "Cancer", "House": 4, "Dignity": "Neutral"},
                "Jupiter": {"Sign": "Sagittarius", "House": 9, "Dignity": "Rulership"}
            }
        }
        result = evaluate(formula, chart)
        assert result is True  # Jupiter satisfies last condition

    def test_nested_aggregators(self):
        """Вложенные агрегаторы"""
        formula = "COUNT(planets WHERE Dignity IN [Rulership, Exaltation]) >= 2"
        chart = {
            "planets": {
                "Sun": {"Dignity": "Rulership"},
                "Moon": {"Dignity": "Exaltation"},
                "Mars": {"Dignity": "Detriment"}
            }
        }
        result = evaluate(formula, chart)
        assert result is True
```

#### Acceptance Criteria

- ✅ 50+ новых edge case тестов
- ✅ Покрытие minor bodies (Chiron, Lilith, Nodes)
- ✅ Покрытие outer planets dignities
- ✅ Граничные условия (0°, 29°59', stations)
- ✅ Сложные формулы

#### Estimated Tasks

- Minor bodies: 2 hours
- Outer planets: 2 hours
- Boundary conditions: 2 hours
- Complex formulas: 2 hours

---

### Task 2.2: Profile DSL Performance

**Приоритет:** 🟡 HIGH  
**Оценка:** 4 hours  
**Назначено:** Performance Team  
**Статус:** 📋 PLANNED

#### Инструменты

- cProfile - Python built-in profiler
- line_profiler - Line-by-line profiling
- memory_profiler - Memory usage
- pytest-benchmark - Benchmarking framework

#### Шаги выполнения

##### 2.2.1: Profile Lexer

```bash
# Profile tokenization
python -m cProfile -o lexer.prof -s cumtime \
    -c "from src.dsl.lexer import tokenize; \
        [tokenize('Sun.Sign == Aries') for _ in range(1000)]"

# Analyze results
python -m pstats lexer.prof
```

##### 2.2.2: Profile Parser

```bash
# Profile AST construction
python -m cProfile -o parser.prof -s cumtime \
    -c "from src.dsl.parser import parse; \
        [parse('Sun.Sign == Aries AND Moon.House == 1') for _ in range(1000)]"
```

##### 2.2.3: Profile Evaluator

```python
# tests/test_performance_dsl.py
import pytest
from src.dsl.evaluator import evaluate

@pytest.mark.benchmark(group="dsl")
def test_simple_formula_performance(benchmark):
    """Benchmark simple formula evaluation"""
    chart = {...}  # Sample chart
    result = benchmark(evaluate, "Sun.Sign == Aries", chart)
    assert result is not None

@pytest.mark.benchmark(group="dsl")
def test_complex_formula_performance(benchmark):
    """Benchmark complex formula with aggregators"""
    chart = {...}
    formula = "COUNT(planets WHERE Dignity IN [Rulership, Exaltation]) >= 3"
    result = benchmark(evaluate, formula, chart)
```

##### 2.2.4: Create Performance Report

```bash
# Run benchmarks
pytest tests/test_performance_dsl.py --benchmark-only \
    --benchmark-save=baseline_stage2

# Generate report
pytest-benchmark compare baseline_stage2 \
    --csv=performance_report.csv
```

#### Acceptance Criteria

- ✅ Lexer profiled and documented
- ✅ Parser profiled and documented
- ✅ Evaluator profiled and documented
- ✅ Bottlenecks identified
- ✅ Performance report created

---

### Task 2.3: Establish Performance Baselines

**Приоритет:** 🟡 HIGH  
**Оценка:** 2 hours  
**Назначено:** Performance Team  
**Статус:** 📋 PLANNED

#### Baseline Metrics

```python
# tests/baselines/performance_baselines.py

BASELINES = {
    "lexer": {
        "simple_formula": {
            "target": "< 1ms",
            "acceptable": "< 2ms",
            "critical": "< 5ms"
        },
        "complex_formula": {
            "target": "< 3ms",
            "acceptable": "< 5ms",
            "critical": "< 10ms"
        }
    },
    "parser": {
        "simple_formula": {
            "target": "< 2ms",
            "acceptable": "< 5ms",
            "critical": "< 10ms"
        },
        "complex_formula": {
            "target": "< 10ms",
            "acceptable": "< 20ms",
            "critical": "< 50ms"
        }
    },
    "evaluator": {
        "simple_evaluation": {
            "target": "< 5ms",
            "acceptable": "< 10ms",
            "critical": "< 20ms"
        },
        "complex_evaluation": {
            "target": "< 20ms",
            "acceptable": "< 50ms",
            "critical": "< 100ms"
        },
        "aggregator_evaluation": {
            "target": "< 30ms",
            "acceptable": "< 75ms",
            "critical": "< 150ms"
        }
    },
    "full_pipeline": {
        "single_formula": {
            "target": "< 10ms",
            "acceptable": "< 30ms",
            "critical": "< 50ms"
        },
        "batch_100_formulas": {
            "target": "< 200ms",
            "acceptable": "< 500ms",
            "critical": "< 1000ms"
        }
    }
}
```

#### Performance Tests

```python
# tests/test_performance_baselines.py

import pytest
from tests.baselines.performance_baselines import BASELINES

class TestPerformanceBaselines:
    """Ensure performance meets baseline targets"""

    @pytest.mark.benchmark
    def test_meets_simple_formula_target(self, benchmark):
        """Simple formula should meet target baseline"""
        result = benchmark(evaluate, "Sun.Sign == Aries", sample_chart)
        baseline = BASELINES["full_pipeline"]["single_formula"]
        assert benchmark.stats['mean'] < parse_time(baseline["acceptable"])
```

#### Acceptance Criteria

- ✅ Baseline targets defined
- ✅ Baseline tests created
- ✅ All tests passing within acceptable range
- ✅ Critical paths identified

---

### Task 2.4: Create Real Chart Dataset

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 6 hours  
**Назначено:** Data Team  
**Статус:** 📋 PLANNED

#### Dataset Requirements

- **Size:** 100+ натальных карт
- **Sources:** Публичные данные знаменитостей
- **Anonymization:** Если частные данные
- **Formats:** JSON, compatible with our schema

#### Sources

1. **AstroDatabank** - публичные карты знаменитостей
2. **Synthetic Generation** - генерация тестовых карт
3. **User Contributions** - с согласием пользователей (анонимно)

#### Schema

```json
{
  "charts": [
    {
      "id": "chart_001",
      "metadata": {
        "name": "Anonymous Person 1",
        "date": "1990-01-15",
        "time": "14:30:00",
        "place": "Moscow",
        "lat": 55.7558,
        "lon": 37.6173,
        "timezone": "Europe/Moscow"
      },
      "planets": {
        "Sun": {"Sign": "Capricorn", "Degree": 24.5, "House": 10, ...},
        "Moon": {...},
        ...
      },
      "houses": {...},
      "aspects": {...}
    },
    ...
  ]
}
```

#### Validation

```python
# tests/test_dataset_validation.py

def test_dataset_schema():
    """Validate dataset schema"""
    with open('tests/fixtures/chart_dataset.json') as f:
        data = json.load(f)

    assert 'charts' in data
    assert len(data['charts']) >= 100

    for chart in data['charts']:
        assert 'metadata' in chart
        assert 'planets' in chart
        # ... validate schema
```

#### Acceptance Criteria

- ✅ 100+ charts collected
- ✅ Schema validated
- ✅ Anonymization complete
- ✅ Dataset documented

---

## 📊 ПРОГРЕСС ВЫПОЛНЕНИЯ

### Week 1 (Feb 22-28)

```
Mon-Tue: Task 2.1 (Edge cases) - 8 hours
Wed: Task 2.2 (Profiling) - 4 hours
Thu: Task 2.3 (Baselines) - 2 hours
Fri: Review & adjustments
```

### Week 2 (Mar 1-7)

```
Mon-Wed: Task 2.4 (Dataset) - 6 hours
Thu: Integration testing
Fri: Stage 2 wrap-up & documentation
```

### Checklist

- [ ] Task2.1: Edge case tests
- [ ] Task 2.2: Performance profiling
- [ ] Task 2.3: Baselines established
- [ ] Task 2.4: Dataset created
- [ ] All new tests passing
- [ ] Performance report created
- [ ] STAGE_2_RESULTS.md created

---

## 🎯 EXPECTED RESULTS

### Test Coverage

```
Before Stage 2:
- Total tests: 295
- Edge case coverage: Limited
- Performance tests: Basic

After Stage 2:
- Total tests: 345+ (50 new)
- Edge case coverage: 100%
- Performance tests: Comprehensive
```

### Performance Metrics

- ✅ Baseline targets defined
- ✅ All components profiled
- ✅ Bottlenecks identified
- ✅ Optimization roadmap created

### Dataset

- ✅ 100+ real charts
- ✅ Validated schema
- ✅ Ready for integration tests

---

## 🚨 RISKS & MITIGATION

### Risk 1: Insufficient astrological knowledge

**Mitigation:** Consult astrology experts, research classical texts

### Risk 2: Performance doesn't meet targets

**Mitigation:** Document current performance, plan optimization for Stage 3

### Risk 3: Dataset privacy concerns

**Mitigation:** Use only public data or fully anonymize

---

## 🔄 TRANSITION TO STAGE 3

### Prerequisites

- ✅ All Stage 2 tasks complete
- ✅ 345+ tests passing
- ✅ Baselines established
- ✅ Dataset ready

### Handoff

1. Create STAGE_2_RESULTS.md
2. Performance optimization plan for Stage 3
3. Schedule Stage 3 kickoff

---

_Created: 2026-02-20_  
_Start Date: 2026-02-22_  
_Target Completion: 2026-03-07_
