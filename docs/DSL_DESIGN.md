# Astro Formula DSL - Design Document

## Концепция

Domain-Specific Language для астрологических формул - позволяет астрологам писать условия и запросы на простом языке вместо программирования.

## Статус

✅ **BRAINSTORMED** - см. [DSL_BRAINSTORM.md](DSL_BRAINSTORM.md) для полного анализа

🎯 **READY FOR IMPLEMENTATION** - синтаксис утвержден

## 🎨 Финальный синтаксис (Hybrid Approach)

### Уровень 1: Простой (для начинающих)

```python
# Базовые проверки
Sun.Sign == Aries
Moon.House == 7
Mars.Retrograde == True
Venus.Dignity > 5

# Аспекты
Asp(Mars, Saturn, Conj)
Asp(Venus, Jupiter, Trine)
```

### Уровень 2: Средний (логика)

```python
# Логические операторы AND/OR/NOT
Sun.Sign == Aries AND Moon.Sign == Taurus
Mars.House == 1 OR Mars.House == 10
NOT Mercury.Retrograde

# Скобки для группировки
(Sun.Sign == Aries AND Moon.Sign == Taurus) OR (Sun.Sign == Leo)

# Аспекты с орбисом
Asp(Mars, Saturn, Conj, orb<5)
```

### Уровень 3: Продвинутый (множественные объекты)

```python
# Списки планет (OR семантика)
Asp(Mars, [Saturn, Pluto], Conj)  # Mars с Saturn ИЛИ Pluto
Asp([Mars, Venus], Saturn, Conj)  # Mars ИЛИ Venus с Saturn

# Группы планет
Malefics.Asp(Moon, Square)  # Любая злотворная в квадрате к Луне
OuterPlanets.Retrograde     # Любая внешняя ретроградная

# Подсчет
Count(Planets, Sign==Aquarius) >= 3
Count(Planets, Retrograde==True) >= 2

# Паттерны
HasPattern(GrandTrine)
Stellium(Aquarius, min=3)
```

## 📖 Полная грамматика

### Базовые элементы

**Планеты:**

```
Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
```

**Знаки:**

```
Aries, Taurus, Gemini, Cancer, Leo, Virgo,
Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces
```

**Аспекты:**

```
Conj (Conjunction), Opp (Opposition), Trine, Square, Sextile,
Quintile, Sesquiquadrate, Semisquare, Semisextile, Quincunx
```

**Свойства планет:**

```
.Sign       - Знак зодиака
.House      - Дом (1-12)
.Degree     - Градус в знаке (0-30)
.Dignity    - Достоинство (число)
.Retrograde - Ретроградность (True/False)
```

### Операторы сравнения

| Оператор | Значение         | Пример                |
| -------- | ---------------- | --------------------- |
| `==`     | Равно            | `Sun.Sign == Aries`   |
| `!=`     | Не равно         | `Moon.Sign != Gemini` |
| `>`      | Больше           | `Mars.Dignity > 5`    |
| `<`      | Меньше           | `Venus.Orb < 3`       |
| `>=`     | Больше или равно | `Saturn.Degree >= 29` |
| `<=`     | Меньше или равно | `Moon.Degree <= 1`    |

### Логические операторы

| Оператор | Приоритет   | Пример                                      |
| -------- | ----------- | ------------------------------------------- |
| `NOT`    | Высший      | `NOT Mars.Retrograde`                       |
| `AND`    | Средний     | `Sun.Sign == Aries AND Moon.Sign == Taurus` |
| `OR`     | Низший      | `Mars.House == 1 OR Mars.House == 10`       |
| `( )`    | Группировка | `(A AND B) OR C`                            |

**Альтернативы (опционально):**

- Русские операторы: `И`, `ИЛИ`, `НЕ`
- Python-style: `and`, `or`, `not`
- Символы: `&&`, `||`, `!` (для программистов)

### Функции

**Аспекты:**

```python
Asp(<planet1>, <planet2>, <aspect> [, orb<N>])

# Примеры:
Asp(Mars, Saturn, Conj)
Asp(Venus, Jupiter, Trine, orb<5)
Asp(Sun, Moon, Opp, orb<8)
```

**Подсчет:**

```python
Count(Planets, <filter>) <operator> <number>

# Примеры:
Count(Planets, Sign==Aquarius) >= 3
Count(Planets, Retrograde==True) >= 2
Count(Planets, House==10) == 1
```

**Паттерны:**

```python
HasPattern(<pattern_name>)

# Примеры:
HasPattern(GrandTrine)
HasPattern(TSquare)
HasPattern(GrandCross)
HasPattern(Yod)
HasPattern(Kite)
```

**Стеллиум:**

```python
Stellium(<sign>, min=<N>)

# Примеры:
Stellium(Aquarius, min=3)
Stellium(Pisces, min=4)
```

### Предопределенные группы

```python
# Личные планеты
PersonalPlanets = [Sun, Moon, Mercury, Venus, Mars]

# Социальные планеты
SocialPlanets = [Jupiter, Saturn]

# Внешние планеты
OuterPlanets = [Uranus, Neptune, Pluto]

# Злотворные
Malefics = [Mars, Saturn, Pluto]

# Благотворные
Benefics = [Venus, Jupiter]

# Использование:
Malefics.Asp(Moon, Square)
OuterPlanets.Retrograde
PersonalPlanets.InSign(Aries)
```

## 📝 Примеры использования

### 🔍 Простые проверки

```python
# Солнце в Козероге
Sun.Sign == Capricorn
# → True (для карты 1982-01-08)

# Луна в Близнецах
Moon.Sign == Gemini
# → True

# Марс ретроградный
Mars.Retrograde == True
# → False (нет ретроградов)

# Сатурн в экзальтации
Saturn.Dignity > 5
# → True (21.79° Libra - экзальтация!)
```

### ⚡ Аспекты

```python
# Марс соединение Сатурн
Asp(Mars, Saturn, Conj)
# → False (они в разных знаках)

# Солнце квинтиль Юпитер (точный!)
Asp(Sun, Jupiter, Quintile, orb<2)
# → True (орбис 1.31°)

# Любой аспект Марс-Луна
Asp(Mars, Moon, Any)
# → Check all aspects
```

### 🔗 Логические комбинации

```python
# Солнце в Козероге И Луна в Близнецах
Sun.Sign == Capricorn AND Moon.Sign == Gemini
# → True

# Марс в 1 ИЛИ 10 доме
Mars.House == 1 OR Mars.House == 10
# → True/False (зависит от времени)

# Сатурн экзальтирован И НЕ ретрограден
Saturn.Dignity > 5 AND NOT Saturn.Retrograde
# → True

# Сложное условие
(Sun.Sign == Capricorn AND Moon.Sign == Gemini) OR
(Asp(Mars, Saturn, Conj) AND Count(Planets, Retrograde==True) >= 3)
# → True (первая часть верна)
```

### 🌟 Множественные объекты

```python
# Марс с Сатурном ИЛИ Плутоном
Asp(Mars, [Saturn, Pluto], Conj)
# → Если есть любой из этих аспектов = True

# Марс ИЛИ Венера с Сатурном
Asp([Mars, Venus], Saturn, Conj)
# → Если любая из планет в соединении с Сатурном

# 3+ планет в Водолее
Count(Planets, Sign==Aquarius) >= 3
# → True/False

# Злотворные в квадрате к Луне
Malefics.Asp(Moon, Square)
# → Если Mars, Saturn или Pluto в квадрате к Луне
```

### 🎨 Паттерны и конфигурации

```python
# Большой трин
HasPattern(GrandTrine)
# → True/False

# Т-квадрат И 3+ ретроградных
HasPattern(TSquare) AND Count(Planets, Retrograde==True) >= 3
# → Проверка обоих условий

# Стеллиум в Козероге (минимум 3 планеты в пределах 10°)
Stellium(Capricorn, min=3)
# → True/False
```

## 🚀 Интеграция

### CLI

```bash
# Одна формула
python main.py natal 1982-01-08 13:40 Саратов --check="Sun.Sign == Capricorn"
# Output: ✅ True

# Сложная формула
python main.py natal 1982-01-08 13:40 Саратов --check="Sun.Sign == Capricorn AND Moon.Sign == Gemini"
# Output: ✅ True

# Множественная проверка
python main.py natal 1982-01-08 13:40 Саратов \
  --check="Sun.Sign == Capricorn" \
  --check="Asp(Sun, Jupiter, Quintile, orb<2)" \
  --check="Saturn.Dignity > 5"
# Output:
# ✅ Sun.Sign == Capricorn: True
# ✅ Asp(Sun, Jupiter, Quintile, orb<2): True
# ✅ Saturn.Dignity > 5: True
```

### Telegram Bot

```python
from src.professional.formula_language import evaluate_formula

@bot.message_handler(commands=['check'])
def check_formula(message):
    user_chart = get_user_chart(message.from_user.id)
    query = message.text.replace('/check ', '')

    # NLP: переводим вопрос в формулу
    formula = natural_language_to_formula(query)

    result = evaluate_formula(formula, user_chart)

    if result:
        bot.reply_to(message, f"✅ Да! {formula}")
    else:
        bot.reply_to(message, f"❌ Нет. {formula}")

# Примеры:
# User: "/check есть ли у меня марс с сатурном?"
# Bot: "✅ Да! Asp(Mars, Saturn, Conj, orb<10)"

# User: "/check солнце в овне?"
# Bot: "❌ Нет. Sun.Sign == Aries (у вас Sun.Sign == Capricorn)"

# User: "/check 3 планеты в водолее?"
# Bot: "✅ Да! Count(Planets, Sign==Aquarius) >= 3"
```

### REST API

```python
# Flask/FastAPI endpoint
@app.get("/api/charts")
def get_charts(having: str = None):
    """
    GET /api/charts?having=Sun.House==10
    GET /api/charts?having=HasPattern(GrandTrine)
    GET /api/charts?having=Count(Planets,Retrograde==True)>=3
    """
    charts = database.get_all_charts()

    if having:
        from src.professional.formula_language import evaluate_formula
        filtered = [
            chart for chart in charts
            if evaluate_formula(having, chart.facts)
        ]
        return {"charts": filtered, "filter": having, "count": len(filtered)}

    return {"charts": charts, "count": len(charts)}

# Response:
{
  "charts": [
    {"name": "User1", "date": "1982-01-08", ...},
    {"name": "User3", "date": "1990-03-15", ...}
  ],
  "filter": "Sun.House == 10",
  "count": 2
}
```

### WordPress Shortcode

```php
// PHP plugin
function astro_check_shortcode($atts, $content = null) {
    $formula = $atts['formula'];
    $user_chart = get_user_natal_chart(get_current_user_id());

    $result = evaluate_formula_api($formula, $user_chart);

    if ($result) {
        return $content;  // Показать контент если условие True
    }
    return '';  // Скрыть если False
}
add_shortcode('astro_check', 'astro_check_shortcode');

// Использование:
[astro_check formula="Sun.Sign == Leo"]
  <div class="leo-message">
    🦁 Вы Лев! Сильная личность, лидерские качества.
  </div>
[/astro_check]

[astro_check formula="Asp(Mars, Saturn, Conj)"]
  <div class="mars-saturn-message">
    ⚔️ У вас Марс-Сатурн! Железная дисциплина и выдержка.
  </div>
[/astro_check]

[astro_check formula="Count(Planets, Retrograde==True) >= 3"]
  <div class="retrograde-message">
    🔄 3+ ретроградных планет: склонность к рефлексии и внутренней работе.
  </div>
[/astro_check]
```

## Архитектура

```
Пользователь вводит формулу
         ↓
    Parser (pyparsing/lark)
         ↓
    AST (Abstract Syntax Tree)
         ↓
    Evaluator + Chart Data
         ↓
    Boolean result (True/False)
```

## Примерная реализация

```python
# src/professional/formula_language.py

from pyparsing import *

# Tokens
PLANET = oneOf("Sun Moon Mercury Venus Mars Jupiter Saturn Uranus Neptune Pluto")
SIGN = oneOf("Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces")
PROPERTY = oneOf("Sign House Degree Dignity Essential Accidental")

# Grammar
planet_prop = PLANET + "." + PROPERTY
comparison = planet_prop + oneOf("== != > < >= <=") + (SIGN | NUMBER)

def evaluate_formula(formula: str, chart_data: dict) -> bool:
    """Evaluate formula against chart data."""
    ast = parse_formula(formula)
    return execute_ast(ast, chart_data)
```

## Примеры для тестирования

```python
# После получения синтаксиса ZET:

# 1. Базовые проверки
evaluate_formula("Sun.Sign == Capricorn", chart)  # True
evaluate_formula("Moon.Sign == Gemini", chart)    # True

# 2. Аспекты
evaluate_formula("Asp(Mars, Saturn, Conj, orb<5)", chart)  # ?

# 3. Множественные условия
evaluate_formula("Count(Retrograde) >= 3", chart)  # False (0 в карте)

# 4. Критические градусы
evaluate_formula("Saturn.IsExalted", chart)  # True (21.79° Libra)
```

## TODO

- [ ] Получить примеры синтаксиса ZET от пользователя
- [ ] Выбрать parser library (pyparsing vs lark)
- [ ] Спроектировать полную грамматику
- [ ] Реализовать parser
- [ ] Реализовать evaluator
- [ ] Интегрировать в CLI
- [ ] Создать примеры для Telegram bot
- [ ] Создать примеры для REST API
- [ ] Документация по синтаксису
- [ ] Тесты

## Ссылки

- **ZET astrology software**: популярная астрологическая программа с мощным языком формул
- **pyparsing**: Python parser library
- **lark**: Modern parsing library for Python

## Ждём от пользователя

Примеры реального синтаксиса формул из ZET:

- Как записываются условия на планеты?
- Как записываются аспекты?
- Какие операторы используются (==, !=, AND, OR)?
- Есть ли функции/методы (Count, Asp, HasPattern)?
- Синтаксис для домов, знаков, градусов?

**Как только получим примеры - начинаем имплементацию! 🚀**
