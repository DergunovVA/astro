# Implementation Plan: Critical Horary Techniques

## Prohibition, Refrenation, Reception Quality

**Sprint:** Horary P0 Blockers  
**Duration:** 28 hours  
**Priority:** CRITICAL

---

## 📋 OVERVIEW

Имплементация 3 критичных техник хорарной астрологии:

1. **Prohibition** (Запрещение) - 8 часов
2. **Refrenation** (Отказ) - 12 часов
3. **Reception Quality** (Качество рецепции) - 8 часов

**Цель:** Устранить false positives (ложные "YES" ответы)

---

## 1️⃣ PROHIBITION (Запрещение)

### 📖 Теория (William Lilly CA Book II)

**Определение:**  
Когда применяющийся аспект между двумя сигнификаторами прерывается третьей планетой, которая делает аспект к одной из них раньше.

**Правила:**

1. Планета A применяется к планете B (applying aspect)
2. Планета C находится "между ними" (по долготе)
3. Планета C сделает аспект к A или B РАНЬШЕ, чем A аспектирует B
4. Результат: Событие НЕ ПРОИЗОЙДЕТ (prohibited)

**Исключения:**

- Если C имеет взаимную рецепцию с A или B → prohibition может не работать
- Если C - бенефиктор (Venus, Jupiter) → может помогать, не блокировать

---

### 💻 Код

```python
def check_prohibition(
    planet1: str,
    planet1_lon: float,
    planet1_speed: float,
    planet2: str,
    planet2_lon: float,
    planet2_speed: float,
    aspect_angle: float,
    all_planets: Dict[str, Dict[str, Any]],
    orb: float = 8.0
) -> Dict[str, Any]:
    """
    Check if applying aspect is prohibited by 3rd planet.

    Traditional horary rule: When a faster planet applies to aspect
    with slower planet, but another planet intercepts and aspects
    one of them first, the matter is "prohibited" (won't happen).

    Args:
        planet1: First significator name
        planet1_lon: Longitude of first planet (degrees)
        planet1_speed: Daily speed of first planet
        planet2: Second significator name
        planet2_lon: Longitude of second planet
        planet2_speed: Daily speed of second planet
        aspect_angle: Target aspect (0, 60, 90, 120, 180)
        all_planets: Dict with all planets data
        orb: Maximum orb for aspects (default 8°)

    Returns:
        {
            'is_prohibited': bool,
            'prohibitor': str or None,  # Planet name
            'prohibitor_aspect': str or None,  # Aspect type (conjunction, trine, etc.)
            'prohibitor_target': str or None,  # Which significator (planet1/planet2)
            'time_to_prohibition': float or None,  # Days until prohibition
            'time_to_perfection': float or None,  # Days until original aspect
            'explanation': str
        }

    Example:
        >>> # Moon @ 10° Aries → Saturn @ 18° Aries (conjunction in 8°)
        >>> # Mars @ 12° Aries intercepts Moon first
        >>> result = check_prohibition(
        ...     'Moon', 10.0, 13.0,
        ...     'Saturn', 18.0, 0.03,
        ...     0,  # conjunction
        ...     all_planets
        ... )
        >>> print(result['is_prohibited'])  # True
        >>> print(result['prohibitor'])  # 'Mars'
    """
    from src.core.aspects_math import MAJOR_ASPECTS

    result = {
        'is_prohibited': False,
        'prohibitor': None,
        'prohibitor_aspect': None,
        'prohibitor_target': None,
        'time_to_prohibition': None,
        'time_to_perfection': None,
        'explanation': 'No prohibition detected'
    }

    # Calculate time to perfection for main aspect
    main_perfection = time_to_perfection(
        planet1_lon, planet1_speed,
        planet2_lon, planet2_speed,
        aspect_angle
    )

    if not main_perfection['is_applying']:
        result['explanation'] = 'Main aspect is separating (not applying)'
        return result

    time_to_main = main_perfection['days']
    result['time_to_perfection'] = time_to_main

    # Check each other planet for interception
    for other_name, other_data in all_planets.items():
        if other_name == planet1 or other_name == planet2:
            continue

        if 'longitude' not in other_data or 'Speed' not in other_data:
            continue

        other_lon = other_data['longitude']
        other_speed = other_data.get('Speed', 0.0)

        # Check if other planet will aspect planet1 or planet2
        # before main perfection

        for aspect_name, aspect_config in MAJOR_ASPECTS.items():
            check_angle = aspect_config['angle']

            # Check aspect to planet1
            perfection1 = time_to_perfection(
                other_lon, other_speed,
                planet1_lon, planet1_speed,
                check_angle
            )

            if perfection1['is_applying'] and perfection1['days'] < time_to_main:
                # Check orb - prohibition usually within normal orb
                if abs(perfection1['current_distance']) <= orb:
                    result['is_prohibited'] = True
                    result['prohibitor'] = other_name
                    result['prohibitor_aspect'] = aspect_name
                    result['prohibitor_target'] = planet1
                    result['time_to_prohibition'] = perfection1['days']
                    result['explanation'] = (
                        f"{other_name} will {aspect_name} {planet1} in "
                        f"{perfection1['days']:.2f} days, BEFORE {planet1} "
                        f"perfects {aspect_angle}° aspect with {planet2} "
                        f"(in {time_to_main:.2f} days). Matter is PROHIBITED."
                    )
                    return result

            # Check aspect to planet2
            perfection2 = time_to_perfection(
                other_lon, other_speed,
                planet2_lon, planet2_speed,
                check_angle
            )

            if perfection2['is_applying'] and perfection2['days'] < time_to_main:
                if abs(perfection2['current_distance']) <= orb:
                    result['is_prohibited'] = True
                    result['prohibitor'] = other_name
                    result['prohibitor_aspect'] = aspect_name
                    result['prohibitor_target'] = planet2
                    result['time_to_prohibition'] = perfection2['days']
                    result['explanation'] = (
                        f"{other_name} will {aspect_name} {planet2} in "
                        f"{perfection2['days']:.2f} days, BEFORE {planet1} "
                        f"perfects aspect with {planet2} "
                        f"(in {time_to_main:.2f} days). Matter is PROHIBITED."
                    )
                    return result

    result['explanation'] = 'No planet intercepts the applying aspect'
    return result
```

---

### 🧪 Tests

```python
# tests/test_horary_prohibition.py

def test_prohibition_basic():
    """Test basic prohibition scenario."""
    # Moon @ 10° → Saturn @ 18° (conjunction in 8°)
    # Mars @ 12° intercepts

    all_planets = {
        'Moon': {'longitude': 10.0, 'Speed': 13.0},
        'Saturn': {'longitude': 18.0, 'Speed': 0.03},
        'Mars': {'longitude': 12.0, 'Speed': 0.5}
    }

    result = check_prohibition(
        'Moon', 10.0, 13.0,
        'Saturn', 18.0, 0.03,
        0,  # conjunction
        all_planets
    )

    assert result['is_prohibited'] == True
    assert result['prohibitor'] == 'Mars'
    assert result['time_to_prohibition'] < result['time_to_perfection']


def test_no_prohibition():
    """Test case where no prohibition occurs."""
    # Moon @ 10° → Saturn @ 18° (conjunction)
    # Mars @ 25° (after Saturn, can't intercept)

    all_planets = {
        'Moon': {'longitude': 10.0, 'Speed': 13.0},
        'Saturn': {'longitude': 18.0, 'Speed': 0.03},
        'Mars': {'longitude': 25.0, 'Speed': 0.5}
    }

    result = check_prohibition(
        'Moon', 10.0, 13.0,
        'Saturn', 18.0, 0.03,
        0,
        all_planets
    )

    assert result['is_prohibited'] == False


def test_prohibition_with_trine():
    """Test prohibition via trine aspect."""
    # Moon @ 10° Aries → Venus @ 22° Leo (trine = 120°)
    # Jupiter @ 14° Aries trines Venus first

    all_planets = {
        'Moon': {'longitude': 10.0, 'Speed': 13.0},
        'Venus': {'longitude': 142.0, 'Speed': 1.2},  # 22° Leo
        'Jupiter': {'longitude': 14.0, 'Speed': 0.2}
    }

    result = check_prohibition(
        'Moon', 10.0, 13.0,
        'Venus', 142.0, 1.2,
        120,  # trine
        all_planets
    )

    # Should detect prohibition (Jupiter intercepts)
    assert result['is_prohibited'] == True
```

---

### 📍 Integration

**Location:** `src/modules/horary.py` (после `find_mutual_receptions()`)

**Usage in horary command:**

```python
# main.py horary() command

# After finding key aspect:
if key_aspect and key_aspect['is_applying']:
    # Check for prohibition
    prohibition = check_prohibition(
        'Moon', moon_lon, moon_speed,
        quesited_ruler, quesited_lon, quesited_speed,
        key_aspect['angle'],
        planets
    )

    if prohibition['is_prohibited']:
        formatted_text.append(f"\n🚫 PROHIBITION DETECTED")
        formatted_text.append(f"   Prohibitor: {prohibition['prohibitor']}")
        formatted_text.append(f"   {prohibition['explanation']}")
        judgment = "NO (prohibited)"
```

---

## 2️⃣ REFRENATION (Отказ)

### 📖 Теория

**Определение:**  
Планета, применяющаяся к аспекту, становится ретроградной ПЕРЕД достижением точного аспекта.

**Эффект:**  
"Отказ от намерения" - событие НЕ произойдет, или человек передумает.

**Сложность:**  
Требует эфемериды будущих дат (Swiss Ephemeris) для определения станций планет.

---

### 💻 Код

```python
def check_refrenation(
    planet_name: str,
    planet_lon: float,
    planet_speed: float,
    target_lon: float,
    target_speed: float,
    aspect_angle: float,
    ephemeris_jd_start: float,
    ephemeris_func: callable
) -> Dict[str, Any]:
    """
    Check if planet will turn retrograde before perfecting aspect.

    Refrenation = planet "changes its mind" by going retrograde
    before reaching exact aspect. Traditional interpretation:
    matter will NOT happen, or person will back out.

    Args:
        planet_name: Name of planet to check (e.g., 'Venus')
        planet_lon: Current longitude of planet
        planet_speed: Current daily speed (negative if already retrograde)
        target_lon: Longitude of target planet
        target_speed: Daily speed of target
        aspect_angle: Target aspect (0, 60, 90, 120, 180)
        ephemeris_jd_start: Julian Day for start date
        ephemeris_func: Function to get ephemeris (e.g., swisseph.calc_ut)

    Returns:
        {
            'will_refrenate': bool,
            'is_currently_retrograde': bool,
            'station_date': datetime or None,  # When planet stations
            'station_jd': float or None,  # Julian Day of station
            'station_longitude': float or None,  # Where planet stations
            'days_to_station': float or None,
            'days_to_perfection': float or None,
            'explanation': str
        }

    Example:
        >>> # Venus @ 15° Leo applies to Mars @ 20° Leo
        >>> # Venus will station R @ 17° Leo in 4 days
        >>> # Perfection would be in 5 days
        >>> result = check_refrenation(
        ...     'Venus', 135.0, 1.2,  # 15° Leo
        ...     140.0, 0.5,  # Mars @ 20° Leo
        ...     0,  # conjunction
        ...     jd_now,
        ...     swisseph.calc_ut
        ... )
        >>> print(result['will_refrenate'])  # True
    """
    import swisseph as swe
    from datetime import datetime, timedelta

    result = {
        'will_refrenate': False,
        'is_currently_retrograde': planet_speed < 0,
        'station_date': None,
        'station_jd': None,
        'station_longitude': None,
        'days_to_station': None,
        'days_to_perfection': None,
        'explanation': ''
    }

    # If already retrograde, no refrenation (already "refused")
    if planet_speed < 0:
        result['explanation'] = f"{planet_name} is already retrograde"
        return result

    # Calculate time to perfection
    perfection = time_to_perfection(
        planet_lon, planet_speed,
        target_lon, target_speed,
        aspect_angle
    )

    if not perfection['is_applying']:
        result['explanation'] = "Aspect is separating (not applying)"
        return result

    days_to_perfect = perfection['days']
    result['days_to_perfection'] = days_to_perfect

    # Get planet ID for Swiss Ephemeris
    planet_ids = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN, 'Uranus': swe.URANUS,
        'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO
    }

    if planet_name not in planet_ids:
        result['explanation'] = f"Unknown planet: {planet_name}"
        return result

    planet_id = planet_ids[planet_name]

    # Check ephemeris for next N days (until perfection + buffer)
    max_days = min(int(days_to_perfect) + 10, 60)  # Cap at 60 days

    prev_speed = planet_speed

    for day_offset in range(1, max_days):
        jd = ephemeris_jd_start + day_offset

        # Calculate planet position for this date
        try:
            calc_result = ephemeris_func(jd, planet_id)
            new_lon = calc_result[0]
            new_speed = calc_result[3]  # Longitude speed
        except Exception as e:
            result['explanation'] = f"Ephemeris error: {e}"
            return result

        # Check if speed changed sign (station)
        if prev_speed > 0 and new_speed < 0:
            # Direct → Retrograde station found!
            result['will_refrenate'] = day_offset < days_to_perfect
            result['station_jd'] = jd
            result['station_longitude'] = new_lon
            result['days_to_station'] = day_offset

            # Convert JD to datetime
            jd_int = int(jd)
            jd_frac = jd - jd_int + 0.5
            if jd_frac >= 1.0:
                jd_int += 1
                jd_frac -= 1.0

            result['station_date'] = swe.jdut1_to_utc(jd)[0:3]  # (year, month, day)

            if result['will_refrenate']:
                result['explanation'] = (
                    f"{planet_name} will station RETROGRADE in {day_offset} days "
                    f"@ {new_lon:.2f}°, BEFORE perfecting aspect "
                    f"(needed {days_to_perfect:.2f} days). "
                    f"Matter is REFRENATED (refused)."
                )
            else:
                result['explanation'] = (
                    f"{planet_name} will station retrograde in {day_offset} days "
                    f"@ {new_lon:.2f}°, but AFTER perfection "
                    f"({days_to_perfect:.2f} days). No refrenation."
                )

            return result

        prev_speed = new_speed

    result['explanation'] = (
        f"{planet_name} will not station retrograde within "
        f"{max_days} days (perfection in {days_to_perfect:.2f} days)"
    )
    return result
```

---

### 🧪 Tests

```python
# tests/test_horary_refrenation.py
import swisseph as swe

def test_refrenation_venus():
    """Test Venus refrenation scenario."""
    # Historical case: Venus stations R @ 17° Leo
    # Setup: Venus @ 15° Leo → Mars @ 20° Leo

    # JD for a date when Venus will station soon
    jd = 2460000.5  # Example JD

    result = check_refrenation(
        'Venus', 135.0, 1.2,
        140.0, 0.5,
        0,  # conjunction
        jd,
        swe.calc_ut
    )

    # Should detect refrenation if station happens before perfection
    # (Actual test needs real ephemeris date)
    assert 'will_refrenate' in result
    assert 'station_longitude' in result


def test_no_refrenation_fast_planet():
    """Test that fast planets (Moon) rarely refrenate."""
    jd = 2460000.5

    result = check_refrenation(
        'Moon', 10.0, 13.0,
        18.0, 0.03,
        0,
        jd,
        swe.calc_ut
    )

    # Moon perfects aspect in <1 day, won't station
    assert result['will_refrenate'] == False
```

---

### 📍 Integration

**Dependencies:**

- Swiss Ephemeris (already used in project)
- Need Julian Day calculation from datetime

**Usage:**

```python
# In horary command
if key_aspect and key_aspect['is_applying']:
    # Check planets that can go retrograde
    # (not Sun, Moon, or already retrograde)
    if planet_name not in ['Sun', 'Moon'] and planet_speed > 0:
        refrenation = check_refrenation(
            planet_name, planet_lon, planet_speed,
            target_lon, target_speed,
            key_aspect['angle'],
            jd_now,
            swisseph.calc_ut
        )

        if refrenation['will_refrenate']:
            formatted_text.append(f"\n🔄 REFRENATION DETECTED")
            formatted_text.append(f"   {refrenation['explanation']}")
            judgment = "NO (refrenated)"
```

---

## 3️⃣ RECEPTION QUALITY (Качество рецепции)

### 📖 Теория

**Определение:**  
Рецепция может быть **дружественной** (friendly) или **враждебной** (hostile) в зависимости от достоинства планеты в принимающем знаке.

**Правила:**

- **Friendly Reception:** Планета в domicile/exaltation/triplicity принимающей планеты → помощь
- **Hostile Reception:** Планета в detriment/fall принимающей планеты → вред, препятствия
- **Neutral:** Другие случаи

**Пример:**

```
✅ Mars в Овне принимает Venus (Venus exalted в Овне) → Mars помогает Venus
❌ Saturn в Овне принимает Mars (Mars exalted в Козероге, но Saturn в detriment в Овне) → сложно
```

---

### 💻 Код

```python
def analyze_reception_quality(
    planet1: str,
    planet1_lon: float,
    planet2: str,
    planet2_lon: float,
    traditional: bool = True
) -> Dict[str, Any]:
    """
    Analyze quality of reception between two planets.

    Reception = planet in sign ruled by another planet.
    Quality = how well planet is received (friendly/hostile).

    Args:
        planet1: First planet name
        planet1_lon: Longitude of first planet
        planet2: Second planet name
        planet2_lon: Longitude of second planet
        traditional: Use traditional rulers (Saturn=Aquarius, Mars=Scorpio)

    Returns:
        {
            'planet1_receives_planet2': {
                'has_reception': bool,
                'type': 'domicile'/'exaltation'/'triplicity'/'term'/'face' or None,
                'quality': 'friendly'/'hostile'/'neutral',
                'score': int,  # Dignity score of planet2 in planet1's sign
                'interpretation': str
            },
            'planet2_receives_planet1': {
                # Same structure
            },
            'is_mutual': bool,  # Both directions have reception
            'overall_quality': 'friendly'/'hostile'/'mixed'/'neutral'
        }

    Example:
        >>> # Mars @ 1.6° Aries, Saturn @ 327.9° Aquarius
        >>> # Mars rules Aries, Saturn rules Aquarius
        >>> # Saturn in Aries (Mars' sign), Mars in Aquarius (Saturn's sign)
        >>> result = analyze_reception_quality('Saturn', 327.9, 'Mars', 1.6)
        >>> print(result['is_mutual'])  # True
        >>> print(result['overall_quality'])  # 'neutral' or 'mixed'
    """
    from src.core.dignities import (
        get_planet_sign,
        get_dispositor,
        calculate_essential_dignity,
        DOMICILE,
        EXALTATION,
        TRIPLICITY
    )

    result = {
        'planet1_receives_planet2': {
            'has_reception': False,
            'type': None,
            'quality': 'neutral',
            'score': 0,
            'interpretation': ''
        },
        'planet2_receives_planet1': {
            'has_reception': False,
            'type': None,
            'quality': 'neutral',
            'score': 0,
            'interpretation': ''
        },
        'is_mutual': False,
        'overall_quality': 'neutral'
    }

    # Get signs
    p1_sign = get_planet_sign(planet1_lon)
    p2_sign = get_planet_sign(planet2_lon)

    # Check if planet1 is ruled by planet2 → planet2 receives planet1
    p1_ruler = get_dispositor(p1_sign, traditional=traditional)

    if p1_ruler == planet2:
        # Planet2 receives planet1
        reception_data = result['planet2_receives_planet1']
        reception_data['has_reception'] = True
        reception_data['type'] = 'domicile'

        # Check dignity of planet1 in planet2's sign
        dignity = calculate_essential_dignity(planet1, planet1_lon, is_day=True)
        reception_data['score'] = dignity.get('total', 0)

        # Determine quality
        if dignity.get('total', 0) >= 4:  # Domicile (+5) or Exaltation (+4)
            reception_data['quality'] = 'friendly'
            reception_data['interpretation'] = (
                f"{planet2} receives {planet1} in {p1_sign} (friendly - "
                f"{planet1} strong here, score +{dignity.get('total', 0)})"
            )
        elif dignity.get('total', 0) <= -4:  # Detriment (-5) or Fall (-4)
            reception_data['quality'] = 'hostile'
            reception_data['interpretation'] = (
                f"{planet2} receives {planet1} in {p1_sign} (hostile - "
                f"{planet1} weak/debilitated here, score {dignity.get('total', 0)})"
            )
        else:
            reception_data['quality'] = 'neutral'
            reception_data['interpretation'] = (
                f"{planet2} receives {planet1} in {p1_sign} (neutral, "
                f"score {dignity.get('total', 0)})"
            )

    # Check opposite direction
    p2_ruler = get_dispositor(p2_sign, traditional=traditional)

    if p2_ruler == planet1:
        reception_data = result['planet1_receives_planet2']
        reception_data['has_reception'] = True
        reception_data['type'] = 'domicile'

        dignity = calculate_essential_dignity(planet2, planet2_lon, is_day=True)
        reception_data['score'] = dignity.get('total', 0)

        if dignity.get('total', 0) >= 4:
            reception_data['quality'] = 'friendly'
            reception_data['interpretation'] = (
                f"{planet1} receives {planet2} in {p2_sign} (friendly, "
                f"score +{dignity.get('total', 0)})"
            )
        elif dignity.get('total', 0) <= -4:
            reception_data['quality'] = 'hostile'
            reception_data['interpretation'] = (
                f"{planet1} receives {planet2} in {p2_sign} (hostile, "
                f"score {dignity.get('total', 0)})"
            )
        else:
            reception_data['quality'] = 'neutral'
            reception_data['interpretation'] = (
                f"{planet1} receives {planet2} in {p2_sign} (neutral, "
                f"score {dignity.get('total', 0)})"
            )

    # Check mutual reception
    result['is_mutual'] = (
        result['planet1_receives_planet2']['has_reception'] and
        result['planet2_receives_planet1']['has_reception']
    )

    # Overall quality
    q1 = result['planet1_receives_planet2']['quality']
    q2 = result['planet2_receives_planet1']['quality']

    if q1 == 'friendly' and q2 == 'friendly':
        result['overall_quality'] = 'friendly'
    elif q1 == 'hostile' or q2 == 'hostile':
        if q1 == q2:
            result['overall_quality'] = 'hostile'
        else:
            result['overall_quality'] = 'mixed'
    else:
        result['overall_quality'] = 'neutral'

    return result
```

---

### 🧪 Tests

```python
# tests/test_horary_reception_quality.py

def test_friendly_reception():
    """Test friendly reception case."""
    # Venus in Pisces (exalted) received by Jupiter
    # Jupiter rules Pisces

    result = analyze_reception_quality(
        'Jupiter', 280.0,  # Capricorn
        'Venus', 350.0,  # Pisces
        traditional=True
    )

    assert result['planet1_receives_planet2']['has_reception'] == True
    assert result['planet1_receives_planet2']['quality'] == 'friendly'


def test_hostile_reception():
    """Test hostile reception case."""
    # Mars in Libra (detriment) received by Venus

    result = analyze_reception_quality(
        'Venus', 30.0,  # Taurus
        'Mars', 200.0,  # Libra
        traditional=True
    )

    assert result['planet1_receives_planet2']['has_reception'] == True
    assert result['planet1_receives_planet2']['quality'] == 'hostile'


def test_mutual_reception_mixed():
    """Test mutual reception with mixed quality."""
    # Saturn in Aries (fall) ↔ Mars in Aquarius (neutral)

    result = analyze_reception_quality(
        'Saturn', 5.0,  # Aries
        'Mars', 328.0,  # Aquarius
        traditional=True
    )

    assert result['is_mutual'] == True
    assert result['overall_quality'] in ['mixed', 'hostile']
```

---

### 📍 Integration

**Usage in horary:**

```python
# In main.py horary command

# After finding mutual receptions:
for reception in mutual_receptions:
    p1 = reception['planet1']
    p2 = reception['planet2']

    # Analyze quality
    quality = analyze_reception_quality(
        p1, planets[p1]['longitude'],
        p2, planets[p2]['longitude'],
        traditional=True
    )

    formatted_text.append(f"\n   Quality: {quality['overall_quality'].upper()}")

    if quality['planet1_receives_planet2']['has_reception']:
        formatted_text.append(f"   {quality['planet1_receives_planet2']['interpretation']}")

    if quality['planet2_receives_planet1']['has_reception']:
        formatted_text.append(f"   {quality['planet2_receives_planet1']['interpretation']}")

    # Adjust judgment based on quality
    if quality['overall_quality'] == 'hostile':
        formatted_text.append("   ⚠️  Hostile reception may cause difficulties")
```

---

## 📅 TIMELINE

### Week 1 (8 hours)

- [ ] Implement `check_prohibition()` (4h)
- [ ] Write tests for prohibition (2h)
- [ ] Integrate into horary command (1h)
- [ ] Documentation (1h)

### Week 2 (12 hours)

- [ ] Implement `check_refrenation()` (6h)
- [ ] Write tests for refrenation (3h)
- [ ] Integrate into horary command (2h)
- [ ] Documentation + ephemeris setup (1h)

### Week 3 (8 hours)

- [ ] Implement `analyze_reception_quality()` (4h)
- [ ] Write tests (2h)
- [ ] Integrate into horary command (1h)
- [ ] Update user guide with all 3 techniques (1h)

---

## ✅ ACCEPTANCE CRITERIA

### Prohibition:

- [ ] Detects when 3rd planet intercepts applying aspect
- [ ] Calculates time to prohibition vs time to perfection
- [ ] Returns clear explanation
- [ ] Handles edge cases (separating aspects, retrograde, etc.)
- [ ] 90%+ test coverage

### Refrenation:

- [ ] Uses Swiss Ephemeris to check future stations
- [ ] Detects Direct→Retrograde stations within perfection window
- [ ] Handles fast planets (Moon, Mercury) correctly
- [ ] Returns station date and longitude
- [ ] 90%+ test coverage

### Reception Quality:

- [ ] Analyzes essential dignity in received sign
- [ ] Classifies as friendly/hostile/neutral
- [ ] Handles mutual receptions
- [ ] Provides clear interpretation
- [ ] Works with traditional rulers
- [ ] 90%+ test coverage

---

## 🎯 SUCCESS METRICS

**Before:**

- False "YES" rate: Unknown (no tracking)
- Test coverage: 0% for production horary code

**After:**

- False "YES" rate: <5% (validated by astrologer)
- Test coverage: 90%+ for all 3 techniques
- Critical techniques: 3 of 5 implemented (60%)

---

## 📚 RESOURCES

### Code references:

- `src/modules/horary.py` - existing functions
- `src/core/dignities.py` - dignity calculations
- `src/core/aspects_math.py` - aspect definitions

### Documentation:

- William Lilly "Christian Astrology" Book II
  - Chapter on Prohibition (p.297-302)
  - Chapter on Refrenation (p.302-305)
  - Chapter on Reception (p.112-118)

### Test data needed:

- 5-10 real horary charts with known outcomes
- Cases where prohibition occurred
- Cases where refrenation occurred
- Various reception types

---

## 🚀 DEPLOYMENT

1. Merge to feature branch: `feature/horary-critical-techniques`
2. Run full test suite
3. Astrologer validation (2-3 test cases per technique)
4. Code review
5. Merge to main
6. Update user guide
7. Announce new features

**Target release:** Sprint 2026-03-15 to 2026-04-15
