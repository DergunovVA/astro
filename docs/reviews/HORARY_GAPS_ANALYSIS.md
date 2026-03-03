# Horary Implementation - Gap Analysis

## Что реализовано vs что нужно доделать

**Дата:** 2 марта 2026  
**Источники:** William Lilly "Christian Astrology" (1647), John Frawley "The Real Astrology" (2000), Guido Bonatti, Al-Biruni

---

## 📊 ОБЩАЯ КАРТИНА

| Категория               | Реализовано | Не реализовано | % готовности |
| ----------------------- | ----------- | -------------- | ------------ |
| Основные техники        | 4 из 9      | 5              | **44%**      |
| Луна и особые состояния | 1 из 5      | 4              | **20%**      |
| Арабские точки          | 0 из 13     | 13             | **0%**       |
| Фиксированные звезды    | 0 из 2      | 2              | **0%**       |
| Антисции                | 0 из 2      | 2              | **0%**       |
| Дополнительные правила  | 1 из 8      | 7              | **12%**      |
| **ИТОГО**               | **6 из 39** | **33**         | **15%**      |

---

## ✅ ЧТО РЕАЛИЗОВАНО

### 1. Базовые техники (Production - Standalone Functions)

#### ✅ Time to Perfection

**Файл:** `src/modules/horary.py:646-744`  
**Статус:** Полностью реализовано  
**Функционал:**

- Расчет времени до точного аспекта
- Учет относительной скорости планет
- Определение применяющегося/расходящегося аспекта
- Выбор кратчайшей дуги

**Точность:** 93% (12.8ч vs 14ч ожидаемые)

```python
result = time_to_perfection(114.16, 13.0, 1.6, 0.03, 120)
# → {'days': 0.57, 'hours': 14.0, 'is_applying': True}
```

---

#### ✅ Void of Course Moon

**Файл:** `src/modules/horary.py:747-828`  
**Статус:** Базовая реализация  
**Функционал:**

- Проверка будущих мажорных аспектов Луны
- Расчет времени до смены знака
- Список предстоящих аспектов

**Недостатки:**

- ❌ Не определяет "последний сделанный аспект" (last aspect made)
- ❌ Требует исторические данные эфемерид

```python
result = is_void_of_course(114.16, 13.0, planets)
# → {'is_void': True/False, 'next_sign_in_hours': 12.5}
```

---

#### ✅ Radicality Check

**Файл:** `src/modules/horary.py:831-887`  
**Статус:** Базовая реализация  
**Функционал:**

- Проверка ASC в пределах 3-27° знака
- Проверка Сатурна не в 1/7 доме
- Список предупреждений

**Недостатки:**

- ❌ Не проверяет Lord of the Hour
- ❌ Не проверяет Луну VOC (требует отдельный вызов)
- ❌ Не проверяет "29 considerations before judgment" (Lilly)

```python
result = check_radicality(244.66, 12)
# → {'is_radical': True, 'warnings': [], 'asc_degree_in_sign': 4.66}
```

---

#### ✅ Mutual Receptions

**Файл:** `src/modules/horary.py:890-951`  
**Статус:** Частичная реализация  
**Функционал:**

- Нахождение взаимных рецепций по domicile (обитель)
- Использует традиционных правителей

**Недостатки:**

- ❌ Не реализована рецепция по exaltation (экзальтация)
- ❌ Не реализована рецепция по triplicity/term/face
- ❌ Нет анализа КАЧЕСТВА рецепции (friendly/hostile)

```python
receptions = find_mutual_receptions(planets)
# → [{'planet1': 'Saturn', 'planet2': 'Mars', 'type': 'domicile'}]
```

---

### 2. Дополнительно в классе HoraryAnalyzer (не используется в production)

#### ✅ Translation of Light (упрощенная)

**Файл:** `src/modules/horary.py:515-548`  
**Статус:** Базовая реализация  
**Функционал:**

- Находит третью планету, аспектирующую оба сигнификатора

**Недостатки:**

- ❌ Не проверяет правильную последовательность (separating → applying)
- ❌ Не учитывает достоинство транслятора
- ❌ Упрощенная логика (достаточно просто двух аспектов)

---

#### ✅ Collection of Light (упрощенная)

**Файл:** `src/modules/horary.py:549-576`  
**Статус:** Базовая реализация  
**Функционал:**

- Находит третью планету, к которой применяются оба сигнификатора

**Недостатки:**

- ❌ Не учитывает вес/достоинство коллектора
- ❌ Не проверяет, что коллектор медленнее обоих сигнификаторов

---

#### ✅ Lost Object Analysis

**Файл:** `src/modules/horary.py:300-345`  
**Статус:** Базовая реализация  
**Функционал:**

- Анализирует 2й дом (вещи)
- Подсказки по местоположению (знак + дом)
- Оценка вероятности найти

**Недостатки:**

- ❌ Нет детальных правил для каждого знака (мокрые знаки → вода, и т.д.)
- ❌ Нет анализа деканатов для точной локации
- ❌ Не использует фиксированные звезды

---

#### ✅ Dignity Analysis

**Функционал:**

- Эссенциальные достоинства (domicile, exaltation, triplicity, term, face)
- Акцидентальные достоинства (дом, аспекты, скорость)
- Общий счет

**Источник:** `src/core/dignities.py`, `src/core/accidental_dignities.py`

---

## ❌ ЧТО НЕ РЕАЛИЗОВАНО

### 🔴 КРИТИЧНЫЕ ПРОБЕЛЫ (P0 - Must Have)

#### 1. Prohibition (Запрещение) ⭐⭐⭐

**Важность:** КРИТИЧНО  
**Источник:** Lilly CA Book II, Aphorism 54

**Что это:**
Когда применяющийся аспект между двумя планетами ПРЕРЫВАЕТСЯ третьей планетой, которая делает аспект к одной из них раньше.

**Пример:**

```
Moon @ 10° Aries → Saturn @ 18° Aries (conjunction in 8°)
Mars @ 12° Aries перехватывает → Mars aspects Moon первым
Результат: Событие НЕ ПРОИЗОЙДЕТ (prohibited)
```

**Эффект:** Превращает "YES" в "NO"

**Сложность:** Средняя (6-8 часов)  
**Код потребуется:**

```python
def check_prohibition(planet1_lon, planet1_speed, planet2_lon,
                      planet2_speed, all_planets, aspect_angle):
    """
    Check if applying aspect is prohibited by 3rd planet.

    Returns:
        {
            'is_prohibited': bool,
            'prohibitor': str or None,  # Planet name
            'prohibitor_aspect': str,
            'time_to_prohibition': float
        }
    """
```

---

#### 2. Refrenation (Отказ) ⭐⭐⭐

**Важность:** КРИТИЧНО  
**Источник:** Lilly CA Book II, Chapter on Refrenation

**Что это:**
Планета, которая применяется к аспекту, становится ретроградной ПЕРЕД достижением точного аспекта.

**Пример:**

```
Venus @ 15° Leo применяется к Mars @ 20° Leo
НО: Venus становится R (ретроградной) @ 17° Leo
Результат: Событие НЕ ПРОИЗОЙДЕТ (отказ от намерения)
```

**Эффект:** Превращает "YES" в "NO" (часто хуже, чем нет аспекта)

**Сложность:** Высокая (10-12 часов)  
**Требуется:** Эфемериды будущих дат для определения станций

**Код потребуется:**

```python
def check_refrenation(planet1_name, planet1_lon, planet1_speed,
                      planet2_lon, ephemeris_future):
    """
    Check if planet will turn retrograde before perfecting aspect.

    Requires ephemeris for next 30 days.

    Returns:
        {
            'will_refrenate': bool,
            'station_date': datetime or None,
            'station_longitude': float or None,
            'days_to_station': float
        }
    """
```

---

#### 3. Frustration (Фрустрация) ⭐⭐

**Важность:** ВЫСОКАЯ  
**Источник:** Bonatti "Liber Astronomiae", Lilly CA

**Что это:**
Планета меняет знак ПЕРЕД достижением точного аспекта.

**Пример:**

```
Moon @ 28° Gemini применяется к Venus @ 2° Cancer (sextile 60°)
НО: Moon входит в Cancer @ 30° (до perfection)
Результат: Аспект "фрустрирован", событие не завершится
```

**Эффект:** Превращает "YES" в "UNCERTAIN" или "NO"

**Сложность:** Средняя (4-6 часов)

**Код потребуется:**

```python
def check_frustration(planet1_lon, planet1_speed, planet2_lon, aspect_angle):
    """
    Check if planet will change sign before perfecting aspect.

    Returns:
        {
            'is_frustrated': bool,
            'sign_change_in_degrees': float,
            'aspect_perfection_in_degrees': float,
            'will_complete': bool
        }
    """
```

---

#### 4. Reception by Dignity (Качество рецепции) ⭐⭐

**Важность:** ВЫСОКАЯ  
**Источник:** Lilly CA, Frawley

**Что это:**
Анализ КАЧЕСТВА рецепции - дружественная или враждебная.

**Примеры:**

- **Friendly:** Mars в Aries принимает Venus (exaltation) → хорошо
- **Hostile:** Saturn в Aries принимает Mars (detriment) → плохо
- **Mixed:** Venus в Scorpio принимает Mars (domicile но Fall Venus) → сложно

**Эффект:**

- Friendly reception → помощь, поддержка
- Hostile reception → препятствия, вред

**Сложность:** Средняя (6-8 часов)

**Код потребуется:**

```python
def analyze_reception_quality(planet1, planet1_lon, planet2, planet2_lon):
    """
    Analyze quality of reception between two planets.

    Returns:
        {
            'has_reception': bool,
            'type': 'domicile'/'exaltation'/'triplicity'/etc.,
            'quality': 'friendly'/'hostile'/'neutral',
            'score': int,  # Dignity score in received sign
            'interpretation': str
        }
    """
```

---

### 🟡 ВАЖНЫЕ ПРОБЕЛЫ (P1 - Should Have)

#### 5. Combust, Cazimi, Under Beams ⭐⭐

**Важность:** ВЫСОКАЯ  
**Источник:** Lilly CA Book II, Traditional rules

**Что это:**
Состояния планет относительно Солнца:

- **Combust:** <8.5° от Солнца → планета "сожжена", очень слаба
- **Under beams:** <17° от Солнца → планета ослаблена
- **Cazimi:** ±17' от Солнца → планета в "сердце Солнца", усилена

**Эффект:**

- Combust → сигнификатор слаб, не может действовать
- Cazimi → сигнификатор усилен (исключение из combustion)

**Сложность:** Низкая (2-3 часа)

```python
def check_sun_proximity(planet_lon, sun_lon):
    """
    Check planet's state relative to Sun.

    Returns:
        {
            'distance': float,
            'state': 'cazimi'/'combust'/'under_beams'/'free',
            'strength_modifier': float  # -5 to +5
        }
    """
```

---

#### 6. Via Combusta (Сожженный путь Луны) ⭐⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Medieval tradition, Al-Biruni

**Что это:**
Луна в 15° Libra - 15° Scorpio считается в "сожженном пути" - неблагоприятная зона.

**Эффект:** Ослабляет Луну, негативный фактор для суждения

**Сложность:** Низкая (1 час)

```python
def is_via_combusta(moon_lon):
    """
    Check if Moon in Via Combusta (15° Lib - 15° Sco).

    Returns:
        {
            'is_via_combusta': bool,
            'effect': str
        }
    """
```

---

#### 7. Part of Fortune (Жребий Фортуны) ⭐⭐⭐

**Важность:** ВЫСОКАЯ  
**Источник:** Классическая традиция, Доротей, Лилли

**Что это:**
Арабская точка, показывающая материальное благополучие и успех.

**Формула:**

- **Дневная карта:** ASC + Moon - Sun
- **Ночная карта:** ASC + Sun - Moon

**Использование в хорарной:**

- Состояние правителя Part of Fortune → материальный исход
- Аспекты к PoF → помощь/препятствия

**Сложность:** Низкая (2-3 часа)

```python
def calculate_part_of_fortune(asc_lon, sun_lon, moon_lon, is_day_chart):
    """
    Calculate Part of Fortune.

    Returns:
        {
            'longitude': float,
            'sign': str,
            'house': int,
            'ruler': str
        }
    """
```

---

#### 8. Fixed Stars Conjunctions ⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Vivian Robson, Lilly

**Что это:**
Конъюнкции планет с важными фиксированными звездами.

**Ключевые звезды для хорарной:**

- **Regulus** (29° Leo) - королевский успех
- **Algol** (26° Taurus) - несчастье, потеря головы
- **Spica** (23° Libra) - удача, защита
- **Aldebaran** (9° Gemini) - честь, но с насилием
- **Antares** (9° Sagittarius) - смелость, опасность

**Orb:** 1° для хорарной

**Сложность:** Средняя (8-10 часов - нужны данные звезд)

```python
FIXED_STARS = {
    'Regulus': {'lon': 149.7, 'nature': 'Jupiter+Mars', 'effect': 'success'},
    'Algol': {'lon': 56.3, 'nature': 'Saturn+Mars', 'effect': 'misfortune'},
    # ...
}

def check_fixed_star_conjunctions(planet_lon, orb=1.0):
    """
    Check planet conjunctions to major fixed stars.

    Returns:
        [
            {
                'star': 'Regulus',
                'orb': 0.5,
                'nature': 'Jupiter+Mars',
                'effect': 'Royal success, honor'
            }
        ]
    """
```

---

#### 9. Antiscia (Антисции) ⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Medieval tradition, Lilly CA Book II

**Что это:**
Зеркальные точки относительно оси 0° Cancer/0° Capricorn.

**Формула:**

- **Antiscion:** 180° - (longitude - 0° Cancer)
- **Contra-antiscion:** Antiscion + 180°

**Пример:**

```
Planet @ 15° Aries → Antiscion @ 15° Virgo
```

**Использование:**

- Антисция работает как тайный аспект (conjunction силой)
- Учитывается при отсутствии прямых аспектов

**Сложность:** Средняя (4-6 часов)

```python
def calculate_antiscia(longitude):
    """
    Calculate antiscion point.

    Returns:
        {
            'antiscion': float,  # Antiscion longitude
            'contra_antiscion': float,  # Opposite point
            'sign_antiscion': str,
            'sign_contra': str
        }
    """

def find_antiscia_aspects(planet1_lon, planet2_lon, orb=1.0):
    """
    Check if planets connect via antiscia.

    Returns:
        {
            'has_antiscia': bool,
            'type': 'antiscion'/'contra-antiscion',
            'orb': float
        }
    """
```

---

#### 10. Besieging (Осада) ⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Lilly CA, medieval tradition

**Что это:**
Планета зажата между двумя малефикторами (Mars, Saturn).

**Пример:**

```
Mars @ 10° Leo
Venus @ 15° Leo  ← besieged
Saturn @ 20° Leo
```

**Эффект:**

- Сильное препятствие
- Если Venus = сигнификатор → событие блокировано

**Сложность:** Средняя (3-4 часа)

---

### 🟢 ЖЕЛАТЕЛЬНЫЕ ПРОБЕЛЫ (P2 - Nice to Have)

#### 11. Derivative Houses (Деривативные дома) ⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Lilly, Frawley

**Что это:**
"Повернутая" карта для анализа вопросов о других людях.

**Примеры:**

- Вопрос о матери → 10й дом = мать
  - 11й дом = 2й от 10го = деньги матери
  - 4й дом = 7й от 10го = партнер матери
- Вопрос о бизнес-партнере → 7й дом
  - 8й дом = деньги партнера
  - 12й дом = потери партнера

**Сложность:** Высокая (12+ часов - нужна полная система)

---

#### 12. Lord of the Hour ⭐

**Важность:** НИЗКАЯ  
**Источник:** Traditional horary, Al-Biruni

**Что это:**
Планета, управляющая часом вопроса (по халдейской системе).

**Правило:**
Если Lord of Hour = ASC ruler → карта очень радикальна

**Последовательность:**

```
Saturday: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon
Sunday: Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars
...
```

**Замечание:** Лилли считал это необязательным правилом.

**Сложность:** Средняя (4-6 часов)

---

#### 13. Lilly's 29 Considerations Before Judgment ⭐⭐

**Важность:** СРЕДНЯЯ  
**Источник:** William Lilly "Christian Astrology" Book II

**Что это:**
29 правил НЕ выносить суждение по карте:

1. Saturn в 1м или 7м доме
2. ASC в последних градусах знака (27-30°)
3. Луна VOC
4. Луна в Via Combusta
5. 7й дом перехвачен
6. Меньше 3° от ASC
7. ... (всего 29 правил)

**Эффект:** Проверка валидности карты

**Сложность:** Высокая (20+ часов для всех 29)

**Приоритет:** Низкий (первые 3-5 правил уже реализованы)

---

#### 14. Almuten (Альмутен) ⭐

**Важность:** НИЗКАЯ  
**Источник:** Medieval Arabic tradition

**Что это:**
Планета с наибольшим количеством достоинств в данной точке карты.

**Использование:**

- Almuten Figuris (общий правитель карты)
- Almuten точки (кто сильнейший в градусе)

**Сложность:** Средняя (6-8 часов)

---

#### 15. Primary Directions for Timing ⭐

**Важность:** СРЕДНЯЯ  
**Источник:** Traditional predictive technique

**Что это:**
Точная техника тайминга через дуговую меру 1° = 1 год (или др. ключ).

**Замечание:** Сложная математика, требует тригонометрии сферы.

**Сложность:** ОЧЕНЬ ВЫСОКАЯ (40+ часов)

---

## 📝 РЕКОМЕНДАЦИИ ПО ПРИОРИТЕТАМ

### Фаза 1: Критичные блокеры (6-8 недель)

**Цель:** Покрыть основные традиционные техники

1. **Prohibition** (8ч) - блокирует аспекты
2. **Refrenation** (12ч) - требует эфемериды
3. **Frustration** (6ч) - смена знаков
4. **Reception Quality** (8ч) - дружественные/враждебные рецепции
5. **Combust/Cazimi** (3ч) - состояния у Солнца
6. **Via Combusta** (1ч) - Moon в опасной зоне
7. **Tests** (20ч) - тесты для всех новых функций

**Итого:** ~58 часов

---

### Фаза 2: Расширенные техники (4-6 недель)

**Цель:** Арабские точки и звезды

1. **Part of Fortune** (3ч) - главная арабская точка
2. **Part of Spirit** (2ч) - вторая по важности
3. **Fixed Stars** (10ч) - базовые 10-15 звезд
4. **Antiscia** (6ч) - тайные аспекты
5. **Besieging** (4ч) - осада малефикторами
6. **Tests** (10ч)

**Итого:** ~35 часов

---

### Фаза 3: Опциональные улучшения (6-8 недель)

**Цель:** Полнота традиции

1. **Derivative Houses** (15ч) - вопросы о других
2. **Lord of Hour** (6ч) - дополнительная радикальность
3. **Lilly's 29 Considerations** (25ч) - полный чеклист
4. **Almuten** (8ч) - доминирующая планета
5. **Tests** (15ч)

**Итого:** ~69 часов

---

## 🎯 МИНИМАЛЬНО ЖИЗНЕСПОСОБНАЯ РЕАЛИЗАЦИЯ (MVP)

Для **профессиональной хорарной практики** МИНИМУМ нужно:

### Must-Have (P0):

1. ✅ Time to perfection (есть)
2. ✅ Void of Course (есть)
3. ✅ Radicality check (есть)
4. ✅ Mutual receptions (есть)
5. ❌ **Prohibition** (БЛОКЕР)
6. ❌ **Refrenation** (БЛОКЕР)
7. ❌ **Reception quality** (ВАЖНО)

### Should-Have (P1):

8. ❌ **Part of Fortune**
9. ❌ **Combust/Cazimi**
10. ❌ **Fixed Stars** (хотя бы Regulus, Algol, Spica)

**Статус:** Текущая реализация покрывает ~40% минимума  
**Требуется для MVP:** +58 часов работы (Фаза 1)

---

## 📚 ИСТОЧНИКИ ДЛЯ РЕАЛИЗАЦИИ

### Книги:

1. **William Lilly** - "Christian Astrology" (1647) - главный источник
2. **John Frawley** - "The Real Astrology" (2000) - современная интерпретация
3. **Guido Bonatti** - "Liber Astronomiae" (13 век) - средневековые правила
4. **Dorotheus of Sidon** - "Carmen Astrologicum" (1 век) - античные корни
5. **Al-Biruni** - "The Book of Instruction in the Elements of the Art of Astrology" (11 век)

### Online ресурсы:

- Skyscript.co.uk - статьи по традиционной астрологии
- Астрология Ренессанса - Christopher Warnock
- Renaissance Astrology - тексты и переводы

---

## ⚠️ ТЕХНИЧЕСКИЕ ЗАВИСИМОСТИ

### Для Refrenation:

- **Swiss Ephemeris** - эфемериды будущих дат (30+ дней вперед)
- Определение станций планет (D→R, R→D)

### Для Fixed Stars:

- Каталог координат звезд (с прецессией на текущую эпоху)
- ~50-100 важных звезд

### Для Reception Quality:

- Расширение текущей системы dignities.py
- Таблица дружественных/враждебных достоинств

### Для Primary Directions:

- Сферическая тригонометрия
- Расчет полудуг (semi-arcs)
- Это самая сложная часть - НЕ рекомендуется для первых фаз

---

## 🔄 ПЛАН МИГРАЦИИ

### Текущая проблема:

- Standalone functions (production) vs Class HoraryAnalyzer (unused)
- 0% test coverage для production кода

### Рекомендуемый путь:

#### Вариант A: Удалить класс (РЕКОМЕНДУЕТСЯ)

1. Удалить `HoraryAnalyzer` class (строки 26-642)
2. Добавить недостающие функции как standalone
3. Написать тесты для standalone functions
4. Миграция: ~10-15 часов

#### Вариант B: Мигрировать на класс

1. Переписать `main.py` horary command на использование класса
2. Добавить недостающие техники в класс
3. Обновить тесты
4. Миграция: ~15-20 часов

#### Вариант C: Гибрид

1. Класс для сложных анализов (yes/no, timing, lost-object)
2. Standalone для утилит (time_to_perfection, VOC, etc.)
3. Рефакторинг: ~20-25 часов

**Рекомендация:** Вариант A (удалить класс) + добавить новые техники как functions

---

## 💭 АСТРОЛОГИЧЕСКАЯ ВАЛИДАЦИЯ

### Вопросы для астролога:

1. **Приоритет техник:** Какие из 33 недостающих техник КРИТИЧНЫ для ваших консультаций?

2. **Prohibition/Refrenation:** Как часто встречаются в реальных картах? (оценка важности)

3. **Fixed Stars:** Используете ли в хорарной? Какие звезды главные?

4. **Antiscia:** Насколько часто делаете antiscia analysis?

5. **Primary Directions:** Нужны ли для точного тайминга, или достаточно орбов аспектов?

6. **Reception Quality:** Анализируете ли враждебные/дружественные рецепции регулярно?

7. **Test Cases:** Можете ли предоставить 10-20 реальных хорарных карт с известными исходами?

---

## ✅ ЧЕКЛИСТ ДЛЯ PRODUCTION-READY

### Блокеры (P0):

- [ ] Prohibition implemented & tested
- [ ] Refrenation implemented & tested
- [ ] Frustration implemented & tested
- [ ] Reception quality implemented & tested
- [ ] 80%+ test coverage для horary.py
- [ ] Астролог валидировал формулы

### Критичные (P1):

- [ ] Part of Fortune calculated
- [ ] Combust/Cazimi/Under Beams checked
- [ ] Fixed stars (топ-10) integrated
- [ ] Via Combusta для Moon
- [ ] Besieging detection

### Документация:

- [ ] API документация для всех функций
- [ ] Примеры использования каждой техники
- [ ] Interpretation guide для новых техников
- [ ] Обновлен HORARY_USER_GUIDE.md

---

## 📉 РИСКИ ТЕКУЩЕЙ РЕАЛИЗАЦИИ

### 🔴 ВЫСОКИЙ РИСК:

1. **Пропуск Prohibition** → Ложные "YES" ответы (событие не произойдет, хотя аспект есть)
2. **Пропуск Refrenation** → Ложные "YES" ответы (планета откажется от аспекта)
3. **0% test coverage** → Регрессии при рефакторинге незаметны

### 🟡 СРЕДНИЙ РИСК:

4. **Нет Reception Quality** → Неправильная интерпретация рецепций (может быть враждебной)
5. **Нет Frustration** → Неточный тайминг (событие не завершится)
6. **Упрощенная Translation of Light** → Ложные позитивы (есть транслятор, но он не работает)

### 🟢 НИЗКИЙ РИСК:

7. **Нет Part of Fortune** → Потеря деталей (но не критично для основного суждения)
8. **Нет Fixed Stars** → Потеря нюансов (но редко ключевые)
9. **Нет Antiscia** → Пропуск редких связей (но редко решающие)

---

## 🎓 ВЫВОДЫ

### Текущее состояние:

- ✅ Базовая хорарная астрология работает
- ✅ Основные техники (аспекты, VOC, радикальность) есть
- ❌ **Критичные техники (Prohibition, Refrenation) отсутствуют**
- ❌ Нет тестов для production кода

### Минимум для профессионального использования:

**+58 часов работы** (Фаза 1) для покрытия критичных пробелов

### Полная реализация традиционной хорарной:

**+162 часа** (Фазы 1+2+3) для полноты William Lilly уровня

### Следующий шаг:

1. **Tech debt:** Написать тесты для текущего кода (10ч)
2. **Астролог review:** Подтвердить приоритеты техник (2ч встреча)
3. **Prohibition:** Реализовать первую критичную технику (8ч)
4. **Тесты:** Получить реальные хорарные карты для валидации

---

**Статус:** 📊 **15% готовности** от полной традиционной хорарной астрологии  
**Для MVP:** 📊 **40% готовности** (нужно +58ч для 100%)
