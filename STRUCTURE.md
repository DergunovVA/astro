# Структура проекта Astro Engine

## Обзор

```
astro/
├── main.py                     # CLI точка входа (Typer)
├── conftest.py                 # Pytest конфигурация
├── requirements.txt            # Python зависимости
├── README.md                   # Основная документация
├── LICENSE                     # MIT лицензия
│
├── docs/                       # Документация
│   ├── ARCHITECTURE.md         # Архитектура системы
│   ├── INPUT_PIPELINE.md       # Input pipeline документация
│   ├── COMPARATIVE_CHARTS.md   # Синтетические карты
│   └── ...                     # Другие документы
│
├── data/                       # Данные и кэш
│   ├── .cache_places.json      # Кэш городов (gitignored)
│   └── user_*.json            # Пользовательские данные (gitignored)
│
├── src/                        # Исходный код
│   ├── core/                   # Основной математический слой
│   │   ├── __init__.py
│   │   ├── core_geometry.py        # Чистая геометрия (углы, дома, планеты)
│   │   ├── core_math.py            # Помощник для координат
│   │   ├── aspects_math.py         # Расчет аспектов
│   │   ├── houses_math.py          # Математика домов
│   │   ├── solar_math.py           # Solar return расчеты
│   │   ├── transit_math.py         # Transit расчеты
│   │   ├── relocation_math.py      # Relocation расчеты
│   │   └── rectification_math.py   # Rectification расчеты
│   │
│   ├── models/                 # Pydantic моделиданных
│   │   ├── __init__.py
│   │   ├── facts_models.py         # Fact (факты о карте)
│   │   ├── signals_models.py       # Signal (интерпретация)
│   │   └── decisions_models.py     # Decision (советы)
│   │
│   ├── modules/                # Интеграционные модули
│   │   ├── __init__.py
│   │   ├── astro_adapter.py        # Swiss Ephemeris адаптер
│   │   ├── interpretation_layer.py # Facts→Signals→Decisions
│   │   ├── synastry.py             # Синастрия (две карты)
│   │   └── house_systems.py        # 9 систем домов
│   │
│   ├── input_pipeline/         # Нормализация входных данных
│   │   ├── __init__.py
│   │   ├── models.py               # Pydantic модели
│   │   ├── cache.py                # JsonCache для городов
│   │   ├── parser_datetime.py      # Парсинг дат/времени
│   │   ├── resolver_city.py        # Разрешение городов
│   │   ├── resolver_timezone.py    # Разрешение timezone
│   │   └── context.py              # InputContext wrapper
│   │
│   └── signals_models.py       # (deprecated) Legacy models
│
├── tests/                      # Тестовый код
│   ├── conftest.py             # Pytest fixtures (если есть)
│   ├── test_basic.py           # Базовые unit tests
│   ├── test_integration_commands.py  # CLI интеграционные тесты
│   ├── test_input_pipeline.py       # Input pipeline unit tests
│   ├── test_new_features.py         # Новые features (house systems, synastry)
│   ├── test_performance_benchmarks.py# Производительность
│   │
│   ├── unit/                   # Unit тесты (структура для будущего)
│   └── integration/            # Integration тесты (структура для будущего)
│
├── input_pipeline/             # (legacy) Старая папка входа
│   └── ...                     # Файлы перемещены в src/input_pipeline/
│
├── .gitignore                  # Git исключения
├── .benchmarks/                # Результаты бенчмарков
└── .pytest_cache/              # Кэш pytest
```

## Слои архитектуры

### 1. CLI Layer (main.py)

```
User Input → Typer Commands
   ↓
@app.command() decorators:
   - natal: Natal chart
   - transit: Current transits
   - solar: Solar return
   - relocation: Chart relocation
   - rectify: Birth time rectification
   - devils: Debug output
   - explain: Explanation mode
   - synastry: Two chart comparison
   - comparative: Multi-city same date/time
```

### 2. Input Normalization (src/input_pipeline/)

```
Raw User Input → NormalizedInput
   ├─ parse_date_time(): Date/time parsing (ISO + European formats)
   ├─ resolve_city(): City name → Coordinates (aliases + geopy + cache)
   ├─ resolve_tz_name(): Timezone name validation + DST
   └─ make_aware(): UTC datetime creation
```

### 3. Calculation Layer (src/)

```
NormalizedInput → natal_calculation() → Calculation Result {jd, planets, houses}
   ├─ astro_adapter.py: Swiss Ephemeris wrapper
   │  ├─ calc_planets_raw(): 7 planets + speeds
   │  ├─ calc_houses_raw(): 12 house cusps (with 9 systems)
   │  └─ julian_day(): UTC datetime → JD
   │
   └─ house_systems.py: 9 house systems
      ├─ Placidus (default)
      ├─ Whole Sign
      ├─ Koch, Regiomontanus, Campanus, Topocentric, Equal, Porphyry, Alcabitius
      └─ All via Swiss Ephemeris
```

### 4. Core Math Layer (src/core/)

```
Calculation Result → Pure Float Math → Geometry Results
   ├─ core_geometry.py: Main calculations
   │  ├─ angle_diff(): Shortest angular distance
   │  ├─ planet_in_sign(): Sign placement
   │  ├─ planet_in_house(): House placement
   │  └─ calculate_aspects(): All aspect detection (9 types)
   │
   ├─ aspects_math.py: Aspect configuration
   │  ├─ MAJOR_ASPECTS (5): conjunction, opposition, square, trine, sextile
   │  ├─ MINOR_ASPECTS (4): semisextile, semisquare, sesquiquadrate, quincunx
   │  └─ calc_aspects(): 5-tuple returns with category
   │
   └─ solar_math.py, transit_math.py, etc: Specialized calculations
```

### 5. Interpretation Layer (src/modules/interpretation_layer.py)

```
Geometry Results → Facts/Signals/Decisions

facts_from_calculation(calc_result):
   → Fact[] {Sun in Aries, Sun in House 5, Sun-Moon opposition, ...}

signals_from_facts(facts):
   → Signal[] {intensity="high", domain="relationships", ...}

decisions_from_signals(signals):
   → Decision[] {interpretation=..., strength=...}
```

### 6. Special Features

```
src/modules/synastry.py:
   ├─ calculate_synastry_aspects(): Compare two charts
   ├─ calculate_composite_chart(): Average planets/houses
   └─ Sorting: major hard > major soft > minor

src/modules/house_systems.py:
   └─ 9 systems with dispatch architecture
```

## Файловая организация по типам

### Основной код (src/)

```
src/core/           → Pure math (floats only)
src/models/         → Pydantic data classes
src/modules/        → High-level orchestration
src/input_pipeline/ → Input normalization
```

### Тесты (tests/)

```
tests/              → Integration и unit tests
tests/unit/         → Unit tests (структура)
tests/integration/  → Integration tests (структура)

Текущая организация:
├─ test_basic.py
├─ test_integration_commands.py
├─ test_input_pipeline.py
├─ test_new_features.py
└─ test_performance_benchmarks.py
```

### Документация (docs/)

```
docs/
├─ ARCHITECTURE.md          → Архитектурный обзор
├─ INPUT_PIPELINE.md       → Input pipeline детали
├─ COMPARATIVE_CHARTS.md   → Синтетические карты
└─ ... (другие документы)
```

## Ключевые принципы

### 1. Слойная архитектура

- **CLI** → **Input** → **Calculate** → **Core Math** → **Interpret** → **Output**
- Каждый слой зависит только от нижних слоев
- Слои легко тестировать отдельно

### 2. Типизация

- Type hints везде (Python 3.10+)
- Pydantic для данных
- Frozen dataclasses для неизменяемости

### 3. Кэширование

- `JsonCache` для городов (gitignored)
- Persistent cache между запусками
- Fallback к geopy только при cache miss

### 4. Чистые функции

- `core/` слой содержит только чистые функции
- Нет побочных эффектов
- Детерминированные результаты

### 5. Тестирование

- 55+ тестов (unit + integration)
- Все новые features покрыты
- Performance benchmarks

## Статистика кода

```
Lines of Code (приблизительно):

src/core/           ~1200 lines (чистая математика)
src/models/         ~300 lines (data models)
src/modules/        ~1400 lines (orchestration + synastry)
src/input_pipeline/ ~600 lines (normalization)
tests/              ~1500 lines (comprehensive tests)
docs/               ~3000 lines (documentation)

TOTAL:              ~8000 lines
```

## Команды для работы

```bash
# Запуск natal chart
python main.py natal 1985-01-15 14:30 Moscow

# С выбором системы домов
python main.py natal 1985-01-15 14:30 Moscow --house-system Koch

# Синастрия (две карты)
python main.py synastry 1990-05-15 14:30 Moscow 1992-03-20 10:15 London

# С minor аспектами
python main.py synastry DATE1 TIME1 PLACE1 DATE2 TIME2 PLACE2 --include-minor

# Все тесты
python -m pytest tests/ -q

# С покрытием (если установлено)
python -m pytest tests/ --cov=src
```

## Миграция кода

Если нужно добавить новую функцию:

1. **Новый расчет?** → `src/core/`
2. **Новый тип данных?** → `src/models/`
3. **Новая интеграция?** → `src/modules/`
4. **Новый ввод?** → `src/input_pipeline/`
5. **Новая CLI команда?** → `main.py` + `src/modules/`

## Будущие улучшения

- [ ] Переместить legacy файлы (`signals_models.py`)
- [ ] Расширить `tests/unit/` и `tests/integration/` структуру
- [ ] Добавить async/await для geopy
- [ ] API versioning
- [ ] REST API (FastAPI)
- [ ] Веб-UI (React/Vue)

---

**Дата обновления**: Январь 2026
**Версия архитектуры**: 3.0 (с synastry и 9 house systems)
**Python версия**: 3.10+
