# Action Plan - Critical Fixes

## 🔴 БЛОКЕРЫ (Начать немедленно)

### 1. Создать тесты для production функций

**Файл:** `tests/test_horary_standalone.py`
**Время:** 6 часов

```python
"""
Unit tests for standalone horary functions (production code)
"""
import pytest
from src.modules.horary import (
    time_to_perfection,
    is_void_of_course,
    check_radicality,
    find_mutual_receptions,
)

class TestTimeToPerfection:
    def test_moon_trine_saturn_applying(self):
        """Moon 114.16° approaching Saturn 1.6° (trine 120°)"""
        result = time_to_perfection(
            planet1_lon=114.16,
            planet1_speed=13.0,
            planet2_lon=1.6,
            planet2_speed=0.03,
            aspect_angle=120
        )

        assert result["is_applying"] is True
        assert 0.5 <= result["days"] <= 0.6
        assert result["current_distance"] == pytest.approx(7.44, abs=0.1)

    def test_moon_trine_saturn_separating(self):
        """Moon past exact trine, separating"""
        result = time_to_perfection(
            planet1_lon=130.0,  # Past the trine
            planet1_speed=13.0,
            planet2_lon=1.6,
            planet2_speed=0.03,
            aspect_angle=120
        )

        assert result["is_applying"] is False

    def test_retrograde_planet(self):
        """Saturn retrograde approaching Sun"""
        result = time_to_perfection(
            planet1_lon=10.0,
            planet1_speed=-0.03,  # Retrograde
            planet2_lon=15.0,
            planet2_speed=1.0,
            aspect_angle=0  # Conjunction
        )

        # Both moving toward each other
        assert result["is_applying"] is True


class TestVoidOfCourse:
    def test_moon_not_void(self):
        """Moon makes trine to Saturn before leaving Cancer"""
        result = is_void_of_course(
            moon_lon=114.16,  # Cancer 24.16°
            moon_speed=13.0,
            planets={
                "Sun": 310.12,
                "Saturn": 1.6,
                "Jupiter": 105.29,
            }
        )

        assert result["is_void"] is False
        assert result["current_sign"] == "Cancer"
        assert len(result["upcoming_aspects"]) > 0

    def test_moon_void(self):
        """Moon makes no major aspects before leaving sign"""
        result = is_void_of_course(
            moon_lon=118.0,  # Late Cancer, no planets ahead
            moon_speed=13.0,
            planets={
                "Sun": 50.0,   # Too far back
                "Saturn": 40.0,  # Too far back
            }
        )

        assert result["is_void"] is True


class TestRadicality:
    def test_valid_asc(self):
        """ASC at 4.7° in sign (valid)"""
        result = check_radicality(asc_lon=4.7, saturn_house=5)

        assert result["is_radical"] is True
        assert len(result["warnings"]) == 0

    def test_asc_too_early(self):
        """ASC at 2° in sign (too early)"""
        result = check_radicality(asc_lon=2.0, saturn_house=5)

        assert result["is_radical"] is False
        assert any("too early" in w for w in result["warnings"])

    def test_asc_too_late(self):
        """ASC at 28° in sign (too late)"""
        result = check_radicality(asc_lon=358.0, saturn_house=5)

        assert result["is_radical"] is False
        assert any("too late" in w for w in result["warnings"])

    def test_saturn_in_1st_house(self):
        """Saturn in 1st house blocks judgment"""
        result = check_radicality(asc_lon=15.0, saturn_house=1)

        assert result["is_radical"] is False
        assert any("Saturn in 1st house" in w for w in result["warnings"])


class TestMutualReceptions:
    def test_mars_saturn_reception(self):
        """Mars in Aquarius ↔ Saturn in Aries"""
        planets = {
            "Mars": {"longitude": 327.9},    # Aquarius
            "Saturn": {"longitude": 1.6},    # Aries
            "Jupiter": {"longitude": 105.3}, # Cancer
        }

        result = find_mutual_receptions(planets)

        assert len(result) == 1
        assert result[0]["planet1"] == "Mars"
        assert result[0]["planet2"] == "Saturn"
        assert result[0]["type"] == "domicile"

    def test_no_receptions(self):
        """No mutual receptions"""
        planets = {
            "Sun": {"longitude": 310.0},
            "Moon": {"longitude": 114.0},
        }

        result = find_mutual_receptions(planets)

        assert len(result) == 0
```

### 2. Рефакторинг архитектуры

**Время:** 4 часа

**Решение:** Удалить класс HoraryAnalyzer (не используется)

```bash
# Шаги:
# 1. Создать резервную копию
cp src/modules/horary.py src/modules/horary_backup_20260302.py

# 2. Удалить строки 26-642 (класс HoraryAnalyzer)
# 3. Оставить только standalone функции (строки 643-951)
# 4. Переместить все импорты в начало файла

# 4. Удалить старые тесты (они для класса)
mv tests/test_horary.py tests/test_horary_OLD.py

# 5. Создать новые тесты (см. выше)
```

**Новая структура `horary.py`:**

```python
"""
Horary Astrology - Standalone Functions

Traditional horary methods for answering specific questions.
Based on William Lilly's "Christian Astrology" (1647).
"""

from typing import Dict, Optional, Any, List

# ✅ ВСЕ импорты в начале
from src.core.dignities import (
    calculate_essential_dignity,
    get_planet_sign,
    get_dispositor,
    is_day_chart,
)
from src.core.accidental_dignities import (
    calculate_accidental_dignity,
    get_total_dignity,
)
from src.core.aspects_math import MAJOR_ASPECTS


def time_to_perfection(...) -> Dict[str, Any]:
    """Calculate time until aspect perfection"""
    # ... реализация ...

def is_void_of_course(...) -> Dict[str, Any]:
    """Check if Moon is Void of Course"""
    # ... реализация ...

def check_radicality(...) -> Dict[str, bool]:
    """Validate horary chart radicality"""
    # ... реализация ...

def find_mutual_receptions(...) -> List[Dict[str, str]]:
    """Find mutual receptions between planets"""
    # ... реализация ...
```

### 3. Переместить импорты

**Время:** 30 минут

Заменить:

```python
# ❌ Внутри функций
def is_void_of_course(...):
    from src.core.dignities import get_planet_sign
    from src.core.aspects_math import MAJOR_ASPECTS
```

На:

```python
# ✅ В начале файла (уже сделано выше)
```

---

## 🟡 КРИТИЧНЫЕ (После блокеров)

### 4. Исправить lint errors

**Время:** 1-2 часа

```bash
# Установить ruff (быстрый линтер)
pip install ruff

# Автоматически исправить
ruff check --fix tests/

# Вручную проверить оставшиеся
ruff check tests/
```

### 5. Добавить валидацию

**Время:** 1 час

```python
# main.py, horary() команда

# ❌ Текущий код:
planet_longs = {
    name: data.get("longitude", 0) for name, data in planets.items()
}

# ✅ Исправленный код:
planet_longs = {}
required_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

for planet_name in required_planets:
    if planet_name not in planets:
        out.error(f"Missing planet: {planet_name}")
        raise typer.Exit(code=2)

    lon = planets[planet_name].get("longitude")
    if lon is None:
        out.error(f"Planet {planet_name} has no longitude")
        raise typer.Exit(code=2)

    planet_longs[planet_name] = lon

# Outer planets optional
for planet_name in ["Uranus", "Neptune", "Pluto"]:
    if planet_name in planets:
        lon = planets[planet_name].get("longitude")
        if lon is not None:
            planet_longs[planet_name] = lon
```

### 6. Обновить STRUCTURE.md

**Время:** 15 минут

```markdown
├── modules/ # Интеграционные модули
│ ├── astro_adapter.py # Swiss Ephemeris адаптер
│ ├── interpretation_layer.py # Facts→Signals→Decisions
│ ├── horary.py # 🆕 Хорарная астрология
│ ├── synastry.py # Синастрия (две карты)
│ └── house_systems.py # 9 систем домов
```

---

## 🟢 УЛУЧШЕНИЯ (После критичных)

### 7. Разделить на подмодули

**Время:** 2-3 часа (OPTIONAL)

```
src/modules/horary/
├── __init__.py           # Public API
├── timing.py             # time_to_perfection()
├── validation.py         # check_radicality(), is_void_of_course()
└── receptions.py         # find_mutual_receptions()
```

### 8. Type hints

**Время:** 1 час

```bash
pip install mypy
mypy src/modules/horary.py --strict
```

### 9. Dataclasses

**Время:** 2-3 часа

```python
from dataclasses import dataclass

@dataclass
class PerfectionTime:
    days: float
    hours: float
    is_applying: bool
    current_distance: float
    relative_speed: float

def time_to_perfection(...) -> PerfectionTime:
    # ...
    return PerfectionTime(days=0.53, hours=12.8, ...)
```

---

## ⏱️ TIMELINE

```
Week 1: BLOCKERS
├── Mon-Tue: Write tests (6h)
├── Wed: Remove HoraryAnalyzer class (4h)
└── Thu: Move imports to top (0.5h)
    └── STATUS: Ready for testing

Week 2: CRITICAL
├── Mon: Fix lint errors (2h)
├── Tue: Add validation (1h)
├── Wed: Update docs (0.5h)
└── Thu-Fri: Astrologer review + fixes
    └── STATUS: Ready for production

Week 3: IMPROVEMENTS (optional)
├── Mon-Tue: Refactor to submodules
├── Wed: Add type hints
└── Thu-Fri: Use dataclasses
    └── STATUS: Production-ready + maintainable
```

---

## ✅ SUCCESS CRITERIA

**Минимум для production:**

- [ ] 80%+ test coverage для horary functions
- [ ] 0 дублирований кода (класс удален)
- [ ] 0 lint errors
- [ ] Валидация всех входов
- [ ] Астролог подтвердил корректность расчетов

**Желательно:**

- [ ] 95%+ test coverage
- [ ] MyPy --strict проходит
- [ ] Документация синхронизирована
- [ ] Dataclasses для результатов

---

**Начать с:** Пункт 1 (тесты) - самое критичное!
