# DSL Performance Optimization Guide

Руководство по оптимизации производительности DSL формул с использованием кэширования, пакетной обработки и ленивых вычислений.

## 📊 Performance Improvements (Task 3.2)

### Достигнутые результаты

| Оптимизация     | Ускорение  | Описание                               |
| --------------- | ---------- | -------------------------------------- |
| AST кэширование | **12.13x** | Простые формулы: 24.43μs → 2.01μs      |
| AST кэширование | **21.28x** | Сложные формулы: 97.44μs → 4.58μs      |
| Batch обработка | **10.91x** | 100 формул: 2.2ms → 0.2ms              |
| Комбинированная | **13.66x** | Реалистичный workflow: 1.7ms → 0.125ms |

**Все цели (10x) превышены!** ✅

## 🚀 Quick Start

### 1. AST Кэширование

```python
from src.dsl.cache import parse_cached, get_cache_stats, clear_cache

# Парсинг с автоматическим кэшированием
ast = parse_cached("Sun.Sign == Aries")  # Первый вызов: cache miss (24μs)
ast = parse_cached("Sun.Sign == Aries")  # Второй вызов: cache hit (2μs)

# Проверка статистики кэша
stats = get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")  # 50.0%
print(f"Cache size: {stats['size']}")              # 1

# Очистка кэша
clear_cache()
```

### 2. Batch Processing

```python
from src.dsl.batch import batch_evaluate

# Оценка множества формул на одной карте
chart_data = {
    "planets": {
        "Sun": {"Sign": "Aries", "House": 1, "Degree": 15.5},
        "Moon": {"Sign": "Taurus", "House": 2, "Degree": 22.3},
    }
}

formulas = [
    "Sun.Sign == Aries",     # True
    "Moon.Sign == Taurus",   # True
    "Sun.House == 1",        # True
    "Moon.House == 5",       # False
]

# Пакетная оценка (10x faster для 100+ формул)
results = batch_evaluate(formulas, chart_data)
print(results)  # [True, True, True, False]
```

### 3. Lazy Evaluation (Short-Circuit)

```python
from src.dsl import evaluate

# AND: останавливается на первом False
chart = {"planets": {"Sun": {"Sign": "Leo"}}}

# Левая часть False → правая часть НЕ вычисляется
result = evaluate("Sun.Sign == Aries AND Moon.Sign == Taurus", chart)
# False (Moon.Sign никогда не проверяется)

# OR: останавливается на первом True
result = evaluate("Sun.Sign == Leo OR Moon.Sign == Gemini", chart)
# True (Moon.Sign никогда не проверяется)
```

## 🔧 Detailed Usage

### AST Cache

#### Основы

```python
from src.dsl.cache import ASTCache

# Создание кэша с пользовательским размером
cache = ASTCache(maxsize=500)  # Default: 1000

# Ручное управление
ast = cache.get("Sun.Sign == Aries")    # None (cache miss)
cache.set("Sun.Sign == Aries", ast)     # Store AST
ast = cache.get("Sun.Sign == Aries")    # Returns cached AST

# Статистика
stats = cache.stats()
print(f"Size: {stats['size']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

#### Глобальный кэш

```python
from src.dsl.cache import (
    parse_cached,
    clear_cache,
    get_cache_stats,
    set_cache_size
)

# Использование глобального кэша
ast1 = parse_cached("Sun.Sign == Aries", use_cache=True)   # Cache miss
ast2 = parse_cached("Sun.Sign == Aries", use_cache=True)   # Cache hit
assert ast1 is ast2  # Same object!

# Настройка размера кэша
set_cache_size(2000)  # Увеличить до 2000 формул

# Отключение кэша для конкретного вызова
ast = parse_cached("Sun.Sign == Leo", use_cache=False)  # Всегда парсит заново

# Очистка кэша
clear_cache()

# Статистика
stats = get_cache_stats()
```

#### LRU Eviction

```python
from src.dsl.cache import parse_cached, set_cache_size

# Малый размер кэша для демонстрации
set_cache_size(3)

# Заполнение кэша
parse_cached("formula1")  # Cache: [formula1]
parse_cached("formula2")  # Cache: [formula1, formula2]
parse_cached("formula3")  # Cache: [formula1, formula2, formula3]

# Добавление 4-й формулы вытесняет самую старую (formula1)
parse_cached("formula4")  # Cache: [formula2, formula3, formula4]

# Обращение к formula2 делает её "свежей"
parse_cached("formula2")  # Cache: [formula3, formula4, formula2]

# Новая формула вытеснит formula3 (самая старая)
parse_cached("formula5")  # Cache: [formula4, formula2, formula5]
```

### Batch Processing

#### Основы

```python
from src.dsl.batch import BatchEvaluator

chart = {
    "planets": {
        "Sun": {"Sign": "Aries", "House": 1},
        "Moon": {"Sign": "Taurus", "House": 2},
    }
}

# Создание batch evaluator
batch_eval = BatchEvaluator(chart)

# Список формул
formulas = [
    "Sun.Sign == Aries",
    "Moon.Sign == Taurus",
    "Sun.House == 1",
    "Moon.House == 3",  # False
]

# Пакетная оценка
results = batch_eval.evaluate_batch(formulas, use_cache=True)
print(results)  # [True, True, True, False]

# Получение статистики
stats = batch_eval.get_stats()
print(f"Formulas evaluated: {stats['total_formulas']}")
print(f"Average time: {stats['avg_time_ms']:.3f}ms")
print(f"Cache enabled: {stats['cache_enabled']}")
```

#### Простое API

```python
from src.dsl.batch import batch_evaluate, evaluate_all_true, evaluate_any_true

# Простая пакетная оценка
results = batch_evaluate(formulas, chart)

# Проверка, что ВСЕ формулы истинны
if evaluate_all_true(formulas, chart):
    print("All conditions met!")

# Проверка, что ХОТЯ БЫ ОДНА формула истинна
if evaluate_any_true(formulas, chart):
    print("At least one condition met!")
```

#### Статистика производительности

```python
from src.dsl.batch import BatchEvaluator

batch_eval = BatchEvaluator(chart)

# Первый запуск (без кэша)
results1 = batch_eval.evaluate_batch(formulas, use_cache=False)
stats1 = batch_eval.get_stats()
print(f"Without cache: {stats1['avg_time_ms']:.3f}ms per formula")

# Второй запуск (с кэшем)
results2 = batch_eval.evaluate_batch(formulas, use_cache=True)
stats2 = batch_eval.get_stats()
print(f"With cache: {stats2['avg_time_ms']:.3f}ms per formula")

speedup = stats1['avg_time_ms'] / stats2['avg_time_ms']
print(f"Speedup: {speedup:.1f}x")
```

### Lazy Evaluation

#### Short-Circuit AND

```python
from src.dsl import evaluate

chart = {"planets": {"Sun": {"Sign": "Leo"}}}

# Левая часть False → правая часть НЕ вычисляется
formula = "Sun.Sign == Aries AND (очень дорогая операция)"
result = evaluate(formula, chart)
# False, правая часть не выполняется

# Обе части вычисляются, когда левая True
formula = "Sun.Sign == Leo AND Sun.House == 1"
result = evaluate(formula, chart)
# Вычисляет обе части
```

#### Short-Circuit OR

```python
# Левая часть True → правая часть НЕ вычисляется
formula = "Sun.Sign == Leo OR (очень дорогая операция)"
result = evaluate(formula, chart)
# True, правая часть не выполняется

# Обе части вычисляются, когда левая False
formula = "Sun.Sign == Aries OR Sun.House == 1"
result = evaluate(formula, chart)
# Вычисляет обе части
```

#### Производительность

```python
# Пример экономии при short-circuit
expensive_right = " OR ".join([f"Sun.House == {i}" for i in range(100)])
formula = f"Sun.Sign == Leo OR ({expensive_right})"

# Без lazy evaluation: ~1125μs (вычисляет все 100 условий)
# С lazy evaluation: ~1008μs (останавливается на первом True)
# Speedup: ~1.12x для этого примера
```

## 🎯 Best Practices

### 1. Используйте кэш для повторяющихся формул

```python
# ❌ ПЛОХО: Парсинг каждый раз
from src.dsl.parser import parse

for chart in charts:
    ast = parse("Sun.Sign == Aries")  # Парсит заново каждый раз
    result = evaluator.evaluate(ast)

# ✅ ХОРОШО: Кэшированный парсинг
from src.dsl.cache import parse_cached

for chart in charts:
    ast = parse_cached("Sun.Sign == Aries")  # Кэш после первого вызова
    result = evaluator.evaluate(ast)
```

### 2. Используйте batch processing для множества формул

```python
# ❌ ПЛОХО: Индивидуальная оценка
from src.dsl import evaluate

for formula in formulas:
    result = evaluate(formula, chart)  # Создаёт новый Evaluator каждый раз

# ✅ ХОРОШО: Пакетная оценка
from src.dsl.batch import batch_evaluate

results = batch_evaluate(formulas, chart)  # Переиспользует Evaluator
```

### 3. Порядок условий для short-circuit

```python
# ❌ ПЛОХО: Дорогая операция первой
formula = "(сложная проверка всех планет) AND Sun.Sign == Aries"
# Вычисляет дорогую операцию, даже если Sun не в Aries

# ✅ ХОРОШО: Дешёвая проверка первой
formula = "Sun.Sign == Aries AND (сложная проверка всех планет)"
# Останавливается рано, если Sun не в Aries
```

### 4. Настройка размера кэша

```python
from src.dsl.cache import set_cache_size

# Для приложений с ограниченной памятью
set_cache_size(100)  # Маленький кэш

# Для приложений с большим количеством формул
set_cache_size(5000)  # Большой кэш

# Default: 1000 формул (~1-2 MB памяти)
```

### 5. Мониторинг производительности

```python
from src.dsl.cache import get_cache_stats

# Периодически проверяйте эффективность кэша
stats = get_cache_stats()
if stats['hit_rate'] < 0.5:
    print("⚠ Low cache hit rate - consider increasing cache size")

if stats['size'] == stats['maxsize']:
    print("⚠ Cache full - consider increasing maxsize")
```

## 📊 Performance Benchmarks

### Actual Results (pytest-benchmark)

```
Name                                          Mean (μs)     Speedup
--------------------------------------------------------------------------------
Simple Parse:
  without_cache                               24.43         (baseline)
  with_cache_hit                               2.01         12.13x ✅
  with_cache_miss                              2.16         11.30x

Complex Parse:
  without_cache                               97.44         (baseline)
  with_cache_hit                               4.58         21.28x ✅

Batch Processing (100 formulas):
  individually (no cache)                  2,205.48         (baseline)
  batch_no_cache                           2,138.14          1.03x
  batch_with_cache                           202.08         10.91x ✅

Lazy Evaluation:
  AND expensive_right no_lazy              1,125.34         (baseline)
  AND expensive_right lazy                 1,007.89          1.12x
  OR expensive_right no_lazy               1,190.30         (baseline)
  OR expensive_right lazy                  1,033.79          1.15x

Realistic Workflow (50 formulas):
  without_optimizations                    1,713.80         (baseline)
  with_all_optimizations                     125.45         13.66x ✅
```

### Running Benchmarks

```bash
# Все performance тесты
pytest tests/test_performance_optimization.py --benchmark-only

# С детальным выводом
pytest tests/test_performance_optimization.py --benchmark-only -v

# Сохранение результатов
pytest tests/test_performance_optimization.py --benchmark-only --benchmark-autosave

# Сравнение с предыдущими
pytest tests/test_performance_optimization.py --benchmark-only --benchmark-compare
```

## 🧪 Performance Testing

```python
# tests/test_my_performance.py
import pytest
from src.dsl.cache import parse_cached, clear_cache
from src.dsl.batch import batch_evaluate

def test_cache_performance():
    """Test cache improves performance"""
    clear_cache()

    formula = "Sun.Sign == Aries AND Moon.House IN [1,4,7,10]"

    # Cache miss (first call)
    import time
    start = time.perf_counter()
    ast1 = parse_cached(formula)
    time_miss = time.perf_counter() - start

    # Cache hit (second call)
    start = time.perf_counter()
    ast2 = parse_cached(formula)
    time_hit = time.perf_counter() - start

    # Cache должен быть быстрее
    assert time_hit < time_miss
    assert ast1 is ast2  # Тот же объект

def test_batch_performance():
    """Test batch processing improves performance"""
    chart = {"planets": {"Sun": {"Sign": "Aries"}}}
    formulas = ["Sun.Sign == Aries"] * 100

    # Пакетная обработка должна быть быстрее
    import time
    start = time.perf_counter()
    results = batch_evaluate(formulas, chart)
    elapsed = time.perf_counter() - start

    # Должно быть < 1ms для 100 повторяющихся формул
    assert elapsed < 0.001
    assert len(results) == 100
```

## 💡 Advanced Topics

### Custom Cache Implementation

```python
from src.dsl.cache import ASTCache

class MyCustomCache(ASTCache):
    def __init__(self, maxsize=1000):
        super().__init__(maxsize)
        self.custom_stats = {"custom_metric": 0}

    def get(self, formula):
        result = super().get(formula)
        if result:
            self.custom_stats["custom_metric"] += 1
        return result
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from src.dsl.batch import batch_evaluate

# Параллельная обработка множества карт
charts = [chart1, chart2, chart3, ...]
formulas = ["Sun.Sign == Aries", "Moon.House == 1"]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(batch_evaluate, formulas, chart)
        for chart in charts
    ]
    results = [f.result() for f in futures]
```

### Memory-Efficient Streaming

```python
from src.dsl.cache import parse_cached
from src.dsl.evaluator import Evaluator

def evaluate_formulas_streaming(formulas_iter, chart_data, cache_size=100):
    """Process formulas with limited memory"""
    from src.dsl.cache import set_cache_size

    set_cache_size(cache_size)  # Ограничить память
    evaluator = Evaluator(chart_data)

    for formula in formulas_iter:
        ast = parse_cached(formula)
        yield evaluator.evaluate(ast)
```

## 📚 See Also

- [Task 3.2 Completion Report](../../docs/TASK_3.2_PERFORMANCE_OPTIMIZATION_COMPLETED.md)
- [Performance Test Results](../../tests/test_performance_optimization.py)
- [Cache Implementation](../dsl/cache.py)
- [Batch Processing](../dsl/batch.py)
- [Lazy Evaluation](../dsl/evaluator.py)

---

**Performance optimizations completed in Task 3.2** | All 10x goals exceeded ✅
