# DSL Design Brainstorm: Logical Operators & Multiple Objects

## 🎯 Цель

Разработать **простой, интуитивный синтаксис** для астрологического DSL с поддержкой:

1. Логических операторов (AND, OR, NOT)
2. Обработки нескольких объектов одновременно
3. Сложных комбинаций формул

## 👥 Участники брейнсторма

### 1. Senior Backend Developer (Производительность)

### 2. UX/API Designer (Простота использования)

### 3. Professional Astrologer (Астрологическая логика)

### 4. Regular User (Интуитивность)

### 5. Frontend Developer (UI интеграция)

---

## 🧠 РАУНД 1: Логические операторы

### Backend Developer говорит:

**"Давайте используем стандартные операторы"**

```python
# SQL-style (понятно всем, кто работал с базами данных)
Sun.Sign == Aries AND Moon.Sign == Taurus
Mars.House == 1 OR Mars.House == 10
NOT Saturn.Retrograde

# Символы (компактно, привычно программистам)
Sun.Sign == Aries && Moon.Sign == Taurus
Mars.House == 1 || Mars.House == 10
!Saturn.Retrograde

# Python-style (читабельно, естественно)
Sun.Sign == Aries and Moon.Sign == Taurus
Mars.House == 1 or Mars.House == 10
not Saturn.Retrograde
```

**Приоритет операторов:**

- `NOT/!` - высший
- `AND/&&` - средний
- `OR/||` - низший
- Скобки `()` для явного порядка

**Плюсы:**

- Стандартная логика
- Легко парсить
- Понятно разработчикам

**Минусы:**

- Может быть сложно для неопытных пользователей

---

### Professional Astrologer говорит:

**"Астрологи не программисты! Нужен естественный язык"**

```
# Естественный язык (как астрологи говорят)
Sun in Aries and Moon in Taurus
Mars conjunct Saturn or Mars conjunct Pluto
Venus trine Jupiter and Venus sextile Moon
no retrograde planets

# Функциональный стиль (группировка по смыслу)
HasAspect(Mars, Saturn, Conj) and HasAspect(Venus, Jupiter, Trine)
InSign(Sun, Aries) or InSign(Sun, Leo)
NotRetrograde(Mercury)

# Краткие формы
Sun@Aries & Moon@Taurus  # @ = "в знаке"
Mars^Saturn | Mars^Pluto  # ^ = "аспект к"
!Retro(Mercury)
```

**Астрологические группы:**

```
Malefics = [Mars, Saturn]  # Злотворные
Benefics = [Venus, Jupiter]  # Благотворные
PersonalPlanets = [Sun, Moon, Mercury, Venus, Mars]
SocialPlanets = [Jupiter, Saturn]
OuterPlanets = [Uranus, Neptune, Pluto]

# Использование:
Malefics.HasAspect(Moon, Square)
OuterPlanets.AnyRetrograde
```

**Плюсы:**

- Понятно астрологам
- Близко к профессиональной терминологии
- Читается как предложение

**Минусы:**

- Сложнее парсить
- Длиннее записи

---

### Regular User говорит:

**"Я хочу просто спросить бота: 'Есть ли у меня...'"**

```
# Вопросительный стиль (для ботов)
Mars with Saturn?
Sun in fire signs?
any planets retrograde?
3 or more planets in Aquarius?

# Утвердительный стиль (проще)
Mars + Saturn  # Соединение
Sun = Aries    # В знаке
Moon > 5       # Сила > 5

# Смешанный стиль (компромисс)
Sun in Aries AND Moon in Taurus
Mars conjunct (Saturn OR Pluto)
Venus trine Jupiter AND NOT Mercury retrograde
```

**Простые шаблоны:**

```
[Planet] in [Sign]
[Planet] conjunct [Planet]
[Planet] in house [Number]
[Planet] retrograde
```

**Плюсы:**

- Максимально просто
- Можно научить за 2 минуты
- Подходит для разговорных ботов

**Минусы:**

- Ограниченная выразительность
- Сложно строить сложные запросы

---

### UX/API Designer говорит:

**"Нужна консистентность и предсказуемость"**

```
# Единый формат для всех проверок
Check(Sun.Sign == Aries)
Check(Mars.Asp.Conj(Saturn))
Check(Moon.House == 7)

# Цепочки (chainable API)
Sun.InSign(Aries).And(Moon.InSign(Taurus))
Mars.Conjunct(Saturn).Or(Mars.Conjunct(Pluto))
Venus.Trine(Jupiter).And.Not(Mercury.Retrograde)

# Объектно-ориентированный стиль
Planet("Sun").Sign("Aries") && Planet("Moon").Sign("Taurus")
Aspect("Mars", "Saturn", "Conj") || Aspect("Mars", "Pluto", "Conj")
```

**Автодополнение friendly:**

```
Planet.  → [Sun, Moon, Mercury, Venus, Mars, ...]
Sun.     → [Sign, House, Degree, Retrograde, Dignity, ...]
Asp.     → [Conj, Opp, Trine, Square, Sextile, ...]
```

**Плюсы:**

- Удобно для IDE с автодополнением
- Самодокументирующийся код
- Легко добавлять новые методы

**Минусы:**

- Многословность
- Может быть избыточным для простых случаев

---

### Frontend Developer говорит:

**"Мне нужна визуальная конструкция + текстовое представление"**

```json
// JSON для UI Builder
{
  "operator": "AND",
  "conditions": [
    {"planet": "Sun", "property": "Sign", "value": "Aries"},
    {"planet": "Moon", "property": "Sign", "value": "Taurus"}
  ]
}

// Конвертируется в текст:
"Sun.Sign == Aries AND Moon.Sign == Taurus"
```

**Визуальный конструктор (drag & drop):**

```
┌─────────────────────────────────────┐
│ [Sun ▼] [in sign ▼] [Aries ▼]      │
├─────────────────────────────────────┤
│           [AND ▼]                   │
├─────────────────────────────────────┤
│ [Moon ▼] [in sign ▼] [Taurus ▼]    │
└─────────────────────────────────────┘
```

**Плюсы:**

- Для UI идеально
- Валидация на лету
- Нет синтаксических ошибок

**Минусы:**

- Требует GUI
- Не подходит для CLI/API

---

## 🧠 РАУНД 2: Множественные объекты

### Backend Developer:

```python
# Списки (массивы)
Asp(Mars, [Saturn, Pluto], Conj)  # Mars с любым из списка
Asp([Mars, Venus], Saturn, Conj)  # Любой из списка с Saturn

# Множественные планеты с OR семантикой
InSign([Sun, Moon], Aries)  # Sun OR Moon в Овне

# Wildcards
Asp(Mars, Any, Conj)  # Mars соединение с кем угодно
Asp(Any, Saturn, Square)  # Кто угодно квадрат к Saturn
```

---

### Professional Astrologer:

```python
# Группы планет
Malefics = [Mars, Saturn, Pluto]
Benefics = [Venus, Jupiter]

# Использование групп
Malefics.Asp(Moon, Square)  # Любая злотворная в квадрате к Луне
Benefics.InHouse(1)  # Любая благотворная в 1 доме

# Стеллиум (3+ планеты близко)
Stellium([Sun, Moon, Mercury, Venus], max_orb=10)

# Конфигурации
TSquare([Mars, Jupiter, Saturn])  # Т-квадрат из этих планет
GrandTrine([Sun, Moon, Jupiter])  # Большой трин
```

---

### Regular User:

```python
# Простой список через запятую
Mars, Saturn in conjunction
Sun, Moon, Mercury in Aquarius
any of Mars, Venus, Jupiter in house 10

# Множественное число для "любой из"
planets in Aries  # Любые планеты в Овне (сколько?)
malefics retrograde  # Любая злотворная ретроградная
```

---

### UX/API Designer:

```python
# Явные методы для множественности
AnyOf([Mars, Saturn, Pluto]).Conjunct(Moon)
AllOf([Sun, Moon, Mercury]).InSign(Aquarius)
NoneOf([Mars, Venus]).Retrograde

# Quantifiers (квантификаторы)
AtLeast(3, Planets).InSign(Aquarius)
Exactly(2, Planets).Retrograde
Between(1, 3, Planets).InHouse(10)

# Count-based
Count(Planets, InSign=Aquarius) >= 3
Count(Planets, Retrograde=True) >= 2
```

---

### Frontend Developer:

```json
// Множественный выбор в UI
{
  "type": "aspect",
  "planet1": ["Mars", "Venus"],  // MULTIPLE
  "planet2": "Saturn",
  "aspect": "Conjunction",
  "logic": "OR"  // Mars OR Venus
}

// Quantifier в UI
{
  "type": "count",
  "filter": {"sign": "Aquarius"},
  "operator": ">=",
  "value": 3
}
```

---

## 🧠 РАУНД 3: Dual Syntax & Fluent API

### 💡 Предложение: Поддержка двух стилей операторов

**Backend Developer:**

**"Почему бы не поддерживать оба стиля одновременно?"**

```python
# SQL-style (для астрологов и обычных пользователей)
Sun.Sign == Aries AND Moon.Sign == Taurus
Mars.House == 1 OR Mars.House == 10
NOT Saturn.Retrograde

# C/Python-style (для разработчиков и программистов)
Sun.Sign == Aries && Moon.Sign == Taurus
Mars.House == 1 || Mars.House == 10
!Saturn.Retrograde

# Можно даже смешивать (но не рекомендуется):
Sun.Sign == Aries && Moon.Sign == Taurus OR Mars.House == 1
```

**Таблица эквивалентности:**

| SQL Style | C/Python Style | Описание       |
| --------- | -------------- | -------------- |
| `AND`     | `&&`           | Логическое И   |
| `OR`      | `\|\|`         | Логическое ИЛИ |
| `NOT`     | `!`            | Логическое НЕ  |

**Плюсы:**

- ✅ Максимальная гибкость
- ✅ Привычно программистам (`&&`, `||`)
- ✅ Понятно новичкам (`AND`, `OR`)
- ✅ Легко реализовать в лексере

**Минусы:**

- ⚠️ Может сбивать с толку (два способа одного и того же)
- ⚠️ Возможность смешивания стилей (плохо для читаемости)
- ⚠️ В документации надо обе версии показывать

---

### 🔗 Предложение: Fluent/Chainable API

**UX/API Designer:**

**"А что если сделать цепочечный синтаксис, как в jQuery или Lodash?"**

```python
# Вариант 1: Через запятую (компактно)
Sun,Mars,Saturn.conj.Moon
# "Sun ИЛИ Mars ИЛИ Saturn в соединении с Moon"

Venus,Jupiter.trine.Sun
# "Venus ИЛИ Jupiter в трине к Sun"

Mars,Venus,Mercury.in_sign.Aries
# "Mars ИЛИ Venus ИЛИ Mercury в Овне"

Sun,Moon,Mercury.in_house.10
# "Sun ИЛИ Moon ИЛИ Mercury в 10 доме"

# Вариант 2: Через точку (методы)
Sun.and(Moon).in_sign(Aries)
Mars.or(Venus).conj(Saturn)
Mercury.not().retrograde()

# Вариант 3: Краткий синтаксис
Sun@Aries & Moon@Taurus  # @ = "в знаке"
Mars^Saturn | Venus^Jupiter  # ^ = "аспект к"
!Retro(Mercury)  # ! = NOT
```

**Полный пример Fluent API:**

```python
# Простой
Sun.in_sign(Aries)
# → Sun.Sign == Aries

# С несколькими планетами (OR семантика)
Mars,Venus.in_sign(Taurus)
# → Mars.Sign == Taurus OR Venus.Sign == Taurus

# Аспекты
Mars,Saturn.conj.Pluto
# → Asp(Mars, Pluto, Conj) OR Asp(Saturn, Pluto, Conj)

# Обратное направление
Sun.conj.Mars,Venus
# → Asp(Sun, Mars, Conj) OR Asp(Sun, Venus, Conj)

# Множественное соединение
Mars,Venus.conj.Saturn,Pluto
# → (Asp(Mars,Saturn,Conj) OR Asp(Mars,Pluto,Conj) OR
#     Asp(Venus,Saturn,Conj) OR Asp(Venus,Pluto,Conj))

# Методы цепочкой
Sun.in_sign(Aries).and(Moon.in_sign(Taurus))
Mars.in_house(1).or(Mars.in_house(10))
```

**Плюсы:**

- ✅ Очень компактно
- ✅ Читается естественно (слева направо)
- ✅ Удобно для автодополнения в IDE
- ✅ Меньше скобок и кавычек
- ✅ Цепочки методов (chainable)

**Минусы:**

- ⚠️ Может быть неоднозначным (`Mars,Venus.conj.Saturn` - кто с кем?)
- ⚠️ Сложнее парсить (нужен контекстно-зависимый парсер)
- ⚠️ Необычно для астрологов (слишком "программистский")
- ⚠️ Запятая имеет двойное значение (список И разделитель)

---

### 🗣️ Professional Astrologer критикует:

**"Стоп! Я против символов && || ! и запятых!"**

```
❌ ПЛОХО (непонятно астрологу):
Sun.Sign == Aries && Moon.Sign == Taurus
Mars,Venus.conj.Saturn  // Что это вообще значит?!
Sun@Aries & Moon@Taurus  // Где вы такое видели?

✅ ХОРОШО (читается как предложение):
Sun in Aries AND Moon in Taurus
Mars or Venus conjunction Saturn
Sun in Aries and Moon in Taurus
```

**Аргументы:**

1. **Астрологи не программисты** - большинство не знает что такое `&&` и `||`
2. **Естественный язык понятнее** - "AND" читается как "и"
3. **Меньше путаницы** - `Sun,Mars.conj.Moon` - это Mars с Moon? Или Sun с Moon?
4. **Профессиональная терминология** - мы говорим "в соединении", а не `.conj.`

**Предложение астролога:**

```python
# Естественный язык (как мы говорим)
Sun in Aries
Mars conjunct Saturn
Venus trine Jupiter and square Pluto
Moon in 7th house or 8th house
not Mercury retrograde

# Если хотите компактность - используйте функции:
Asp(Mars, Saturn, Conj) and Asp(Venus, Jupiter, Trine)
InSign(Sun, Aries) or InSign(Sun, Leo)
```

---

### 👨‍💻 Backend Developer отвечает:

**"Хорошо, но тогда поддержим ОБА стиля!"**

```python
# Режим 1: SQL-style (для астрологов)
parser.set_mode('natural')
Sun.Sign == Aries AND Moon.Sign == Taurus
NOT Mercury.Retrograde

# Режим 2: C-style (для программистов)
parser.set_mode('compact')
Sun.Sign == Aries && Moon.Sign == Taurus
!Mercury.Retrograde

# Режим 3: Fluent API (для продвинутых)
parser.set_mode('fluent')
Sun,Mars.conj.Saturn
Venus.in_sign(Taurus).and(Jupiter.in_house(2))

# Режим 4: Авто-детект (пробуем все парсеры)
parser.set_mode('auto')
# Принимает любой синтаксис
```

**Реализация:**

```python
class FormulaParser:
    def __init__(self, mode='auto'):
        self.mode = mode
        self.parsers = {
            'natural': NaturalLanguageParser(),
            'compact': CompactParser(),
            'fluent': FluentAPIParser(),
        }

    def parse(self, formula: str):
        if self.mode == 'auto':
            # Try all parsers
            for parser in self.parsers.values():
                try:
                    return parser.parse(formula)
                except:
                    continue
            raise SyntaxError("Could not parse formula")

        return self.parsers[self.mode].parse(formula)
```

---

### 🎨 UX Designer критикует Fluent API:

**"Запятая перегружена значениями - это плохой UX!"**

```python
# Проблема 1: Запятая = список ИЛИ разделитель?
Mars,Venus.conj.Saturn
# Это:
# a) (Mars OR Venus) conjunction Saturn ?
# b) Mars, (Venus conjunction Saturn) ?
# c) Mars conjunction (Venus, Saturn) ?

# Проблема 2: Порядок имеет значение?
Mars,Venus.conj.Saturn
# vs
conj.Saturn.Mars,Venus
# Это одно и то же?

# Проблема 3: Цепочки запутывают
Sun.in_sign(Aries).and(Moon.in_sign(Taurus)).or(Mars.in_house(1))
# Скобки где? Приоритет какой?
# (Sun.in_sign(Aries) AND Moon.in_sign(Taurus)) OR Mars.in_house(1) ?
# Sun.in_sign(Aries) AND (Moon.in_sign(Taurus) OR Mars.in_house(1)) ?
```

**Предложение UX:**

**"Если хотим компактность - делаем ЧЕТКИЕ правила"**

```python
# Правило 1: Запятая ТОЛЬКО для списков
planets = [Mars, Venus, Saturn]
Asp(Any(Mars, Venus), Saturn, Conj)  # Четко!

# Правило 2: Точка ТОЛЬКО для свойств
Sun.Sign == Aries
Mars.House == 10

# Правило 3: Методы ТОЛЬКО для действий
Asp(Mars, Saturn, Conj)
Count(Planets, Sign==Aries) >= 3

# Правило 4: Логика ТОЛЬКО через ключевые слова
Asp(Mars, Saturn, Conj) AND NOT Mercury.Retrograde
```

---

### 👤 Regular User голосует:

**"Мне всё равно, лишь бы работало и в боте понималось!"**

```python
# Что я хочу написать в Telegram:
"есть ли у меня марс с сатурном?"
"солнце в овне?"
"3 планеты в водолее?"

# Что я НЕ хочу писать:
"Sun.Sign == Aries && Moon.Sign == Taurus"  ❌ Слишком сложно
"Asp(Mars, [Saturn, Pluto], Conj)"  ❌ Не понимаю скобки
"Mars,Venus.conj.Saturn"  ❌ Что это вообще?

# Что я готов написать:
"Sun in Aries AND Moon in Taurus"  ✅ Понятно!
"Mars conjunct Saturn"  ✅ Читается естественно
```

---

### 🏆 Выводы раунда 3

#### ✅ Что принять:

1. **Dual operator syntax** (оба стиля):
   - SQL-style: `AND`, `OR`, `NOT` (основной)
   - C-style: `&&`, `||`, `!` (альтернативный)
   - В документации показывать оба

2. **Режимы парсера** (опционально):
   - Auto-detect (по умолчанию) - пробует оба синтаксиса
   - Strict mode - только один синтаксис

#### ❌ Что отклонить (пока):

1. **Fluent API с запятыми** (`Mars,Venus.conj.Saturn`):
   - Слишком неоднозначно
   - Сложно парсить
   - Непонятно пользователям
   - Версия 2.0? (когда будет UI builder)

2. **Символьные операторы** (`@`, `^`):
   - Не интуитивно
   - Нестандартно
   - Сложно запомнить

#### 🤔 Что обсудить ещё:

1. **Python-style операторы** (`and`, `or`, `not` в нижнем регистре):
   - Плюсы: Python-like, современно
   - Минусы: может конфликтовать с именами переменных?

2. **Русские операторы** (`И`, `ИЛИ`, `НЕ`):
   - Плюсы: для русскоязычных ботов
   - Минусы: нужна поддержка Unicode, две документации

3. **Mixed syntax** (разрешить смешивание):

   ```python
   Sun.Sign == Aries && Moon.Sign == Taurus OR Mars.House == 1
   #                 ^^                    ^^
   # C-style         SQL-style
   ```

   - Плюсы: максимальная гибкость
   - Минусы: хаос, плохая читаемость

---

## 🎨 ФИНАЛЬНЫЙ ДИЗАЙН: Hybrid Approach (updated)

### Уровень 1: Простой (для Regular Users & Bots)

```python
# Естественный язык + минимум операторов
Sun in Aries
Moon in Taurus
Mars conjunct Saturn
Venus trine Jupiter
Mercury retrograde

# Логика через AND/OR (русские/английские)
Sun in Aries AND Moon in Taurus
Mars conjunct Saturn OR Mars conjunct Pluto
Sun in Aries И Moon in Taurus ИЛИ Sun in Leo
```

### Уровень 2: Средний (для Astrologers)

```python
# Точечная нотация (dot notation)
Sun.Sign == Aries
Moon.House == 7
Mars.Dignity > 5

# Функции для аспектов
Asp(Mars, Saturn, Conj)
Asp(Venus, Jupiter, Trine, orb<5)

# Логические операторы
Sun.Sign == Aries AND Moon.Sign == Taurus
Asp(Mars, Saturn, Conj) OR Asp(Mars, Pluto, Conj)

# Группы
Malefics.Asp(Moon, Square)
OuterPlanets.Retrograde
```

### Уровень 3: Продвинутый (для Developers)

```python
# Списки и wildcards
Asp(Mars, [Saturn, Pluto], Conj)
Asp([Mars, Venus], Any, Conj)

# Quantifiers
Count(Planets, Sign==Aquarius) >= 3
AtLeast(3, Planets, InSign=Aquarius)

# Сложные условия
(Sun.Sign == Aries AND Moon.Sign == Taurus) OR
(Sun.Sign == Leo AND Moon.Sign == Scorpio)

# Паттерны
HasPattern(GrandTrine) AND Count(Retrograde) >= 3
```

---

## 💡 РЕКОМЕНДУЕМЫЙ СИНТАКСИС

### Базовая грамматика

```python
# УСЛОВИЯ (Conditions)
<planet>.<property> <operator> <value>
  Sun.Sign == Aries
  Moon.House == 7
  Mars.Degree >= 29

# АСПЕКТЫ (Aspects)
Asp(<planet1>, <planet2>, <aspect> [, orb<N>])
  Asp(Mars, Saturn, Conj)
  Asp(Venus, Jupiter, Trine, orb<5)

# ЛОГИЧЕСКИЕ ОПЕРАТОРЫ (Boolean Operators)
<condition> AND <condition>
<condition> OR <condition>
NOT <condition>
( <condition> )

# МНОЖЕСТВЕННЫЕ ОБЪЕКТЫ (Multiple Objects)
Asp(<planet>, [<planet>, <planet>], <aspect>)  # OR семантика
Count(<filter>) <operator> <number>

# ГРУППЫ (Groups)
<group>.Asp(<planet>, <aspect>)
<group>.<property>
```

### Операторы

| Оператор | Значение         | Пример                |
| -------- | ---------------- | --------------------- |
| `==`     | Равно            | `Sun.Sign == Aries`   |
| `!=`     | Не равно         | `Moon.Sign != Gemini` |
| `>`      | Больше           | `Mars.Dignity > 5`    |
| `<`      | Меньше           | `Venus.Orb < 3`       |
| `>=`     | Больше или равно | `Saturn.Degree >= 29` |
| `<=`     | Меньше или равно | `Moon.Degree <= 1`    |
| `AND`    | Логическое И     | `A AND B`             |
| `OR`     | Логическое ИЛИ   | `A OR B`              |
| `NOT`    | Логическое НЕ    | `NOT A`               |

### Предопределенные группы

```python
PersonalPlanets = [Sun, Moon, Mercury, Venus, Mars]
SocialPlanets = [Jupiter, Saturn]
OuterPlanets = [Uranus, Neptune, Pluto]
Malefics = [Mars, Saturn, Pluto]
Benefics = [Venus, Jupiter]
```

### Специальные функции

```python
# Подсчет
Count(Planets, <filter>)
  Count(Planets, Sign==Aquarius)
  Count(Planets, Retrograde==True)
  Count(Planets, House==10)

# Паттерны
HasPattern(<pattern>)
  HasPattern(GrandTrine)
  HasPattern(TSquare)
  HasPattern(Yod)

# Стеллиум
Stellium(<sign>, min=N)
  Stellium(Aquarius, min=3)

# Критические градусы
Critical(<planet>)
  Critical(Saturn)  # 0° или 29°
```

---

## 📝 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Простые запросы

```python
# Солнце в Овне
Sun.Sign == Aries

# Луна в 7 доме
Moon.House == 7

# Марс ретроградный
Mars.Retrograde == True

# Венера в экзальтации
Venus.Dignity > 5
```

### Аспекты

```python
# Марс соединение Сатурн
Asp(Mars, Saturn, Conj)

# Венера трин Юпитер с орбисом < 5°
Asp(Venus, Jupiter, Trine, orb<5)

# Солнце оппозиция Луна
Asp(Sun, Moon, Opp)
```

### Логические комбинации

```python
# Солнце в Овне И Луна в Тельце
Sun.Sign == Aries AND Moon.Sign == Taurus

# Марс с Сатурном ИЛИ Марс с Плутоном
Asp(Mars, Saturn, Conj) OR Asp(Mars, Pluto, Conj)

# НЕ Меркурий ретроградный
NOT Mercury.Retrograde

# Сложное условие
(Sun.Sign == Aries AND Moon.Sign == Taurus) OR
(Sun.Sign == Leo AND Moon.Sign == Scorpio)
```

### Множественные объекты

```python
# Марс с Сатурном ИЛИ Плутоном
Asp(Mars, [Saturn, Pluto], Conj)

# Марс ИЛИ Венера с Сатурном
Asp([Mars, Venus], Saturn, Conj)

# 3+ планет в Водолее
Count(Planets, Sign==Aquarius) >= 3

# Любая злотворная в квадрате к Луне
Malefics.Asp(Moon, Square)
```

### Паттерны и конфигурации

```python
# Большой трин есть
HasPattern(GrandTrine)

# Т-квадрат И 3+ ретроградных
HasPattern(TSquare) AND Count(Planets, Retrograde==True) >= 3

# Стеллиум в Водолее (минимум 3 планеты)
Stellium(Aquarius, min=3)
```

---

## 🔧 ИМПЛЕМЕНТАЦИЯ: Parser Design

### Lexer (Tokenizer)

```python
TOKENS = {
    # Keywords
    'AND', 'OR', 'NOT',
    'Asp', 'Count', 'HasPattern', 'Stellium',

    # Planets
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',

    # Properties
    'Sign', 'House', 'Degree', 'Dignity', 'Retrograde',

    # Operators
    '==', '!=', '>', '<', '>=', '<=',

    # Delimiters
    '(', ')', '[', ']', ',', '.',

    # Aspects
    'Conj', 'Opp', 'Trine', 'Square', 'Sextile',

    # Signs
    'Aries', 'Taurus', 'Gemini', ...
}
```

### Grammar (using pyparsing or lark)

```python
from pyparsing import *

# Базовые элементы
PLANET = oneOf("Sun Moon Mercury Venus Mars Jupiter Saturn Uranus Neptune Pluto")
SIGN = oneOf("Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces")
ASPECT = oneOf("Conj Opp Trine Square Sextile Quintile Sesquiquadrate")
PROPERTY = oneOf("Sign House Degree Dignity Retrograde")
OPERATOR = oneOf("== != > < >= <=")
NUMBER = pyparsing_common.number

# Выражения
planet_prop = PLANET + "." + PROPERTY
comparison = planet_prop + OPERATOR + (SIGN | NUMBER | "True" | "False")

aspect_expr = "Asp" + "(" + PLANET + "," + PLANET + "," + ASPECT + Optional("," + "orb" + "<" + NUMBER) + ")"

count_expr = "Count" + "(" + "Planets" + "," + planet_prop + OPERATOR + (SIGN | NUMBER) + ")" + OPERATOR + NUMBER

# Логика
expr = comparison | aspect_expr | count_expr
and_expr = expr + ZeroOrMore("AND" + expr)
or_expr = and_expr + ZeroOrMore("OR" + and_expr)
not_expr = Optional("NOT") + or_expr
formula = not_expr
```

### AST (Abstract Syntax Tree)

```python
class ASTNode:
    pass

class Comparison(ASTNode):
    def __init__(self, planet, property, operator, value):
        self.planet = planet
        self.property = property
        self.operator = operator
        self.value = value

class AspectCheck(ASTNode):
    def __init__(self, planet1, planet2, aspect, orb=None):
        self.planet1 = planet1
        self.planet2 = planet2
        self.aspect = aspect
        self.orb = orb

class BooleanOp(ASTNode):
    def __init__(self, operator, left, right=None):
        self.operator = operator  # AND, OR, NOT
        self.left = left
        self.right = right
```

---

## 🚀 NEXT STEPS

### Phase 1: Core Parser (1-2 дня)

- [ ] Implement lexer
- [ ] Implement parser (grammar)
- [ ] Build AST
- [ ] Unit tests

### Phase 2: Evaluator (1-2 дня)

- [ ] AST → evaluation against chart data
- [ ] Handle all operators
- [ ] Handle multiple objects
- [ ] Error handling

### Phase 3: CLI Integration (0.5 дня)

- [ ] `--check` flag
- [ ] Multiple formulas support
- [ ] Pretty output

### Phase 4: API Integration (0.5 дня)

- [ ] REST endpoint `/charts?having=<formula>`
- [ ] JSON response
- [ ] Error messages

### Phase 5: Bot Integration (1 день)

- [ ] Natural language → formula translation
- [ ] Telegram bot example
- [ ] Voice-friendly responses

### Phase 6: UI Builder (optional, 2-3 дня)

- [ ] Visual formula constructor
- [ ] Drag & drop interface
- [ ] Formula validation
- [ ] Preview results

---

## 🎯 ИТОГОВЫЕ РЕКОМЕНДАЦИИ (updated)

### ✅ Принять в v1.0:

1. **Hybrid approach** - 3 уровня сложности
2. **Dual syntax для операторов**:
   - Primary: `AND`, `OR`, `NOT` (SQL-style)
   - Alternative: `&&`, `||`, `!` (C/Python-style)
   - Auto-detect: парсер принимает оба
3. **Скобки () для группировки** ⭐ КРИТИЧНО
   - Явная группировка условий
   - Вложенные выражения
4. **Приоритет операторов** (когда нет скобок):
   - Высший: `NOT`, `!`
   - Средний: `AND`, `&&`
   - Низший: `OR`, `||`
5. **Точечная нотация** для свойств планет (`Sun.Sign`)
6. **Функциональный стиль** для аспектов (`Asp(...)`)
7. **Списки в квадратных скобках** для множественных объектов
8. **Предопределенные группы** (Malefics, Benefics, etc.)
9. **Count() и HasPattern()** для продвинутых запросов
10. **Астрологическая валидация** ⭐ КРИТИЧНО
    - **Базовая валидация (v1.0.0):**
      - Sun/Moon не могут быть ретроградными
      - Нет аспектов планеты к самой себе
      - Дома только 1-12
      - Градусы 0-29
    - **Расширенная валидация достоинств (v1.0.0):** 🔬 ТРЕБУЕТ ТЕСТИРОВАНИЯ
      - Проверка управителей (Ruler)
      - Проверка экзальтаций (Exaltation)
      - Проверка изгнаний (Detriment)
      - Проверка падений (Fall)
      - Конфликтующие достоинства
      - ⚠️ TODO: Покрыть unit-тестами (30+ тест-кейсов)
      - ⚡ TODO: Оптимизация таблиц поиска (O(1) вместо O(n))
    - Понятные образовательные сообщения об ошибках
    - Конфигурационные файлы (dignities.yaml, aspects.yaml)
11. **Агрегаторы (planet/planets, aspect/aspects)** ⭐ КРИТИЧНО
    - `any(planet).Sign == Leo` - есть ли планета в Льве?
    - `count(planet, Retrograde == True)` - сколько ретроградных?
    - `any(aspect).Type == Square` - есть ли квадрат?
    - Экономия кода 60-95%!

### 🤔 Рассмотреть для v1.0 (если успеем):

1. **any() синтаксис с явными списками** - альтернатива многословным OR
   ```python
   any([Sun, Moon, Mars]).Sign == Aries  # вместо Sun.Sign == Aries OR ...
   Mars.conj(any([Saturn, Pluto]))        # вместо Asp(Mars, [Saturn, Pluto], Conj)
   ```
2. **Автоопределение типа операции** по контексту:
   - Если после `.property` есть `==` → проверка свойства
   - Если после `.method()` есть объект → аспект/метод
3. **Агрегаторы house/houses, sign/signs** - дополнительно к planet/aspect
   ```python
   any(house).PlanetsCount >= 3  # стеллиум в доме
   any(sign).PlanetsCount >= 4   # стеллиум в знаке
   ```

### ⚠️ Принять с ограничениями:

1. **Смешивание операторов** (AND + &&) - разрешено, но не рекомендуется
2. **Python-style** (`and`/`or`/`not` нижний регистр) - только для Python API
3. **Русские операторы** (`И`/`ИЛИ`/`НЕ`) - только для Telegram ботов

### ❌ Отложить на v2.0 или никогда:

1. **Fluent API с запятыми** (`Mars,Venus.conj.Saturn`) - слишком неоднозначно
2. **Символьные операторы** (`@`, `^`) - не интуитивно

### 🎯 Планируется на v2.0:

1. **Template-based естественный язык** (без AI) - простые шаблоны покроют 90% запросов
2. **Визуальный конструктор формул** (веб/GUI/мобайл) - "не сложнее Excel"
3. **AI-powered NLP** (опционально) - для сложных вопросов
4. **Telegram bot interactive builder** - пошаговое создание формул
5. **Библиотека готовых формул** - шаблоны для типичных задач
6. **BETWEEN/IN_RANGE** - удобные диапазоны (градусы, даты)
7. **XOR** - exclusive OR (редко нужен)
8. **AT_LEAST/AT_MOST/EXACTLY** - алиасы для Count
9. **Расширенные синонимы** - Conjunction = Conj = Cnj
10. **Дополнительная валидация уровня 2-3:**
    - Предупреждения о нетипичных комбинациях
    - Детектор взаимной рецепции (auto-suggest)
    - Проверка Almuten (сильнейшая планета по достоинствам)
    - Peregrinus (планета без достоинств)
11. **Фильтры WHERE для агрегаторов** - `any(planet WHERE Sign IN Fire).Retrograde`
12. **Дополнительные агрегаторы** - luminaries, malefics, benefics, angles, points
13. **Антисы и контр-антисы** - symmetry points (продвинутая астрология)

### 📝 Примеры финального синтаксиса:

```python
# Вариант 1: SQL-style (основной, рекомендуемый)
Sun.Sign == Aries AND Moon.Sign == Taurus
Mars.House == 1 OR Mars.House == 10
NOT Saturn.Retrograde

# Вариант 2: C-style (для программистов)
Sun.Sign == Aries && Moon.Sign == Taurus
Mars.House == 1 || Mars.House == 10
!Saturn.Retrograde

# Вариант 3: Смешанный (разрешено, но не рекомендуется)
Sun.Sign == Aries && Moon.Sign == Taurus OR Mars.House == 1

# Вариант 4: Со скобками (группировка)
(Sun.Sign == Aries AND Moon.Sign == Taurus) OR Mars.House == 1
Sun.Sign == Aries AND (Moon.Sign == Taurus OR Mars.Sign == Leo)

# Вариант 5: Вложенные скобки
((Sun.Sign == Aries AND Moon.Sign == Taurus) OR
 (Sun.Sign == Leo AND Moon.Sign == Scorpio)) AND Mars.House == 1

# Вариант 6: Приоритет без скобок (NOT > AND > OR)
NOT Sun.Retrograde AND Mars.House == 1 OR Venus.Sign == Taurus
# → ((NOT Sun.Retrograde) AND Mars.House == 1) OR Venus.Sign == Taurus

# Вариант 7: С функциями
Asp(Mars, Saturn, Conj) AND NOT Mercury.Retrograde
Count(Planets, Sign==Aquarius) >= 3 && HasPattern(GrandTrine)

# Вариант 8: Списки (OR семантика)
Asp(Mars, [Saturn, Pluto], Conj)  # Mars с Saturn ИЛИ Pluto
Asp([Mars, Venus], Saturn, Conj)  # Mars ИЛИ Venus с Saturn

# Вариант 9: Комбинация всего
(Asp(Mars, Saturn, Conj) OR Asp(Mars, Pluto, Conj)) AND
NOT Mercury.Retrograde AND
(Sun.Sign == Aries OR Sun.Sign == Scorpio)

# Вариант 10: С агрегаторами (НОВОЕ! ⭐)
any(planet).Sign == Leo                    # Есть ли планета в Льве?
any(planet).House == 10                    # Есть ли планета в 10 доме?
count(planet, Retrograde == True) >= 2     # Две или более ретроградных?
any(aspect).Type == Square                 # Есть ли квадрат в карте?
all(planets).Sign IN Fire                  # Все планеты в огне?

# Вариант 11: Агрегаторы + логика
any(planet).Sign == Aries AND any(planet).House == 1
count(planet, Sign IN Fire) >= 3 OR count(planet, Sign IN Water) >= 3
any(aspect).Type == Square AND NOT Mercury.Retrograde

# Вариант 12: Сравнение (было → стало)
# БЫЛО (100+ символов):
Sun.Sign == Leo OR Moon.Sign == Leo OR Mercury.Sign == Leo OR Venus.Sign == Leo OR Mars.Sign == Leo

# СТАЛО (24 символа, экономия -76%):
any(planet).Sign == Leo
```

### 💡 Специальные режимы:

```python
# Для Telegram бота (русский язык):
"Солнце в Овне И Луна в Тельце"
"Марс соединение Сатурн ИЛИ Марс соединение Плутон"

# Для Python API (нижний регистр):
>>> chart.check("sun.sign == 'Aries' and moon.sign == 'Taurus'")
True

# Для REST API (URL-safe):
GET /charts?having=Sun.Sign%3D%3DAries%26%26Moon.Sign%3D%3DTaurus
# (URL-encoded: Sun.Sign==Aries&&Moon.Sign==Taurus)
```

---

## 🗣️ РАУНД 4: Естественный язык (Natural Language)

### Вопрос: Нужен ли AI/ML для естественного языка?

**Backend Developer:**

**"Зависит от того, насколько 'естественным' мы хотим сделать язык!"**

### Вариант A: Без AI (Template-based)

**Простые шаблоны на регулярных выражениях**

```python
# Что МОЖНО без AI (90% запросов):

# Шаблон 1: "[планета] в [знак]"
"Солнце в Овне" → Sun.Sign == Aries
"Луна в Тельце" → Moon.Sign == Taurus
"Марс в Козероге" → Mars.Sign == Capricorn

# Шаблон 2: "[планета] в [число] доме"
"Венера в 7 доме" → Venus.House == 7
"Марс в 10 доме" → Mars.House == 10
"Юпитер в первом доме" → Jupiter.House == 1

# Шаблон 3: "[планета] [аспект] [планета]"
"Марс соединение Сатурн" → Asp(Mars, Saturn, Conj)
"Венера трин Юпитер" → Asp(Venus, Jupiter, Trine)
"Солнце оппозиция Луна" → Asp(Sun, Moon, Opp)

# Шаблон 4: "есть ли [что-то]"
"есть ли Марс с Сатурном?" → Asp(Mars, Saturn, Conj)
"есть ли большой трин?" → HasPattern(GrandTrine)
"есть ли ретроградные планеты?" → Count(Planets, Retrograde==True) > 0

# Шаблон 5: "[число] планет в [знак]"
"3 планеты в Водолее" → Count(Planets, Sign==Aquarius) >= 3
"больше 2 планет в Овне" → Count(Planets, Sign==Aries) > 2

# Шаблон 6: "[планета] ретроградный"
"Меркурий ретроградный" → Mercury.Retrograde == True
"Марс не ретроградный" → NOT Mars.Retrograde
```

**Реализация (без AI):**

```python
import re

class NaturalLanguageParser:
    """Template-based parser, no AI needed."""

    PATTERNS = [
        # Паттерн: "[планета] в [знак]"
        (r'(\w+)\s+в\s+(\w+)',
         lambda m: f"{m[1]}.Sign == {m[2]}"),

        # Паттерн: "[планета] в [N] доме"
        (r'(\w+)\s+в\s+(\d+)\s+доме',
         lambda m: f"{m[1]}.House == {m[2]}"),

        # Паттерн: "[планета] соединение [планета]"
        (r'(\w+)\s+соединение\s+(\w+)',
         lambda m: f"Asp({m[1]}, {m[2]}, Conj)"),

        # Паттерн: "[планета] трин [планета]"
        (r'(\w+)\s+трин\s+(\w+)',
         lambda m: f"Asp({m[1]}, {m[2]}, Trine)"),

        # Паттерн: "есть ли [планета] с [планета]"
        (r'есть\s+ли\s+(\w+)\s+с\s+(\w+)',
         lambda m: f"Asp({m[1]}, {m[2]}, Conj)"),

        # Паттерн: "[N] планет в [знак]"
        (r'(\d+)\s+планет\w*\s+в\s+(\w+)',
         lambda m: f"Count(Planets, Sign=={m[2]}) >= {m[1]}"),
    ]

    TRANSLATIONS = {
        # Планеты
        'Солнце': 'Sun', 'Луна': 'Moon', 'Меркурий': 'Mercury',
        'Венера': 'Venus', 'Марс': 'Mars', 'Юпитер': 'Jupiter',
        'Сатурн': 'Saturn', 'Уран': 'Uranus', 'Нептун': 'Neptune', 'Плутон': 'Pluto',

        # Знаки
        'Овен': 'Aries', 'Телец': 'Taurus', 'Близнецы': 'Gemini',
        'Рак': 'Cancer', 'Лев': 'Leo', 'Дева': 'Virgo',
        'Весы': 'Libra', 'Скорпион': 'Scorpio', 'Стрелец': 'Sagittarius',
        'Козерог': 'Capricorn', 'Водолей': 'Aquarius', 'Рыбы': 'Pisces',
    }

    def parse(self, text: str) -> str:
        """Convert natural language to formula."""
        # Normalize
        text = text.strip().lower()

        # Translate Russian to English
        for ru, en in self.TRANSLATIONS.items():
            text = text.replace(ru.lower(), en)

        # Try patterns
        for pattern, converter in self.PATTERNS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return converter(match.groups())

        raise ValueError(f"Could not parse: {text}")

# Примеры использования:
parser = NaturalLanguageParser()

parser.parse("Солнце в Овне")
# → "Sun.Sign == Aries"

parser.parse("Марс соединение Сатурн")
# → "Asp(Mars, Saturn, Conj)"

parser.parse("есть ли Марс с Сатурном?")
# → "Asp(Mars, Saturn, Conj)"

parser.parse("3 планеты в Водолее")
# → "Count(Planets, Sign==Aquarius) >= 3"
```

**Плюсы (без AI):**

- ✅ Работает оффлайн
- ✅ Мгновенно (нет задержек API)
- ✅ Предсказуемо (детерминировано)
- ✅ Не требует обучения моделей
- ✅ Легко отладить
- ✅ Покрывает 90% типичных запросов

**Минусы (без AI):**

- ⚠️ Не понимает вариации:
  - "Солнце в Овне" ✅
  - "У меня Солнце находится в знаке Овна" ❌
  - "Мое солнце - это Овен" ❌
- ⚠️ Требует точных формулировок
- ⚠️ Не понимает синонимы автоматически
- ⚠️ Нужно добавлять паттерны вручную

---

### Вариант B: С AI/NLP (Intent Recognition)

**UX Designer:**

**"А если использовать AI для распознавания намерений?"**

```python
# Что ВОЗМОЖНО с AI (100% запросов):

# Вариации одного и того же:
"Солнце в Овне" → Sun.Sign == Aries
"У меня Солнце в Овне" → Sun.Sign == Aries
"Мое Солнце находится в знаке Овна" → Sun.Sign == Aries
"Я Овен" → Sun.Sign == Aries
"Солнечный знак Овен" → Sun.Sign == Aries

# Сложные вопросы:
"Есть ли у меня напряженные аспекты Марса?"
  → Asp(Mars, Any, Square) OR Asp(Mars, Any, Opp)

"Какие у меня гармоничные аспекты Венеры?"
  → Asp(Venus, Any, Trine) OR Asp(Venus, Any, Sextile)

"Много ли у меня ретроградных планет?"
  → Count(Planets, Retrograde==True) >= 3

# Разговорный стиль:
"А у меня Марс как-то связан с Сатурном?"
  → Asp(Mars, Saturn, Any)

"Чет я не помню, большой трин у меня есть или нет"
  → HasPattern(GrandTrine)
```

**Реализация (с AI):**

```python
from openai import OpenAI  # или local model

class AIParser:
    """AI-powered natural language parser."""

    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key) if api_key else None

    SYSTEM_PROMPT = """
You are an astrology formula translator.
Convert natural language questions to astrology DSL formulas.

Available syntax:
- Sun.Sign == Aries
- Asp(Mars, Saturn, Conj)
- Count(Planets, Sign==Aquarius) >= 3
- HasPattern(GrandTrine)

Examples:
User: "Солнце в Овне"
Assistant: Sun.Sign == Aries

User: "есть ли Марс с Сатурном?"
Assistant: Asp(Mars, Saturn, Conj)

User: "3 планеты в Водолее"
Assistant: Count(Planets, Sign==Aquarius) >= 3

Now translate the user's question:
"""

    def parse(self, text: str) -> str:
        """Convert natural language to formula using AI."""
        if not self.client:
            raise ValueError("OpenAI API key not set")

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.1,  # Low temp for consistency
            max_tokens=100
        )

        formula = response.choices[0].message.content.strip()
        return formula

# Альтернатива: Local model (без API)
class LocalAIParser:
    """Using local BERT/T5 model."""

    def __init__(self):
        # Load pre-trained model
        from transformers import pipeline
        self.classifier = pipeline("text-classification",
                                   model="your-fine-tuned-model")

    def parse(self, text: str) -> str:
        # Classify intent
        intent = self.classifier(text)[0]

        # Extract entities (planets, signs, aspects)
        entities = self.extract_entities(text)

        # Build formula based on intent + entities
        return self.build_formula(intent, entities)
```

**Плюсы (с AI):**

- ✅ Понимает вариации формулировок
- ✅ Работает с разговорным языком
- ✅ Понимает синонимы
- ✅ Может обучаться на данных
- ✅ Покрывает 100% запросов (теоретически)

**Минусы (с AI):**

- ⚠️ Требует API (OpenAI, Claude, etc.) или локальную модель
- ⚠️ Задержка на запрос (0.5-2 секунды)
- ⚠️ Стоимость API ($0.01-0.10 за запрос)
- ⚠️ Не всегда предсказуемо
- ⚠️ Нужно валидировать результат
- ⚠️ Может галлюцинировать (выдумывать формулы)

---

### 🤔 Professional Astrologer спрашивает:

**"А ЗАЧЕМ нам естественный язык вообще?"**

**Аргументы:**

1. **Для Telegram ботов** - пользователи пишут вопросы, а не формулы
2. **Для UI** - интерфейс "спроси меня что угодно"
3. **Для новичков** - проще спросить "есть ли марс с сатурном?" чем написать `Asp(Mars, Saturn, Conj)`

**НО:**

1. **Профессионалы предпочитают формулы** - точнее и быстрее
2. **API не нужен естественный язык** - там JSON/параметры
3. **CLI тоже не нужен** - кто пишет в терминале, тот знает синтаксис

**Вывод:** Естественный язык нужен **только для ботов** (Telegram, WhatsApp, etc.)

---

### 🎯 Рекомендации по естественному языку

#### Phase 1: Template-based (без AI) ✅

**Реализовать сразу:**

```python
# 20-30 базовых шаблонов покроют 90% запросов
template_parser = NaturalLanguageParser()

# Поддержка:
"[планета] в [знак]"
"[планета] в [N] доме"
"[планета] [аспект] [планета]"
"есть ли [что-то]"
"[N] планет в [знак]"
"[планета] ретроградный"
```

**Плюсы:**

- Работает оффлайн
- Быстро (мгновенно)
- Бесплатно
- Покрывает большинство случаев

**Когда использовать:**

- Telegram bot (базовый режим)
- Quick checks
- Интерактивные подсказки

#### Phase 2: AI-powered (опционально) ⏳

**Добавить позже (если нужно):**

```python
# Fallback на AI если шаблон не сработал
try:
    formula = template_parser.parse(user_query)
except ValueError:
    # Template не подошел → пробуем AI
    formula = ai_parser.parse(user_query)
```

**Когда использовать:**

- Продвинутый режим Telegram бота
- Если пользователь платит за API
- Для сложных вопросов

#### Phase 3: Hybrid (рекомендуется) 🎯

**Лучший подход:**

```python
class HybridParser:
    def __init__(self, use_ai=False):
        self.template_parser = NaturalLanguageParser()
        self.ai_parser = AIParser() if use_ai else None

    def parse(self, text: str) -> str:
        # 1. Попытка через шаблоны (быстро, бесплатно)
        try:
            return self.template_parser.parse(text)
        except ValueError as e:
            if not self.ai_parser:
                raise e

            # 2. Fallback на AI (медленно, платно)
            return self.ai_parser.parse(text)

# Использование:
# Free tier: только шаблоны
bot_free = HybridParser(use_ai=False)

# Paid tier: шаблоны + AI fallback
bot_paid = HybridParser(use_ai=True)
```

---

### 📊 Сравнение подходов

| Критерий      | Template-based     | AI-powered               | Hybrid           |
| ------------- | ------------------ | ------------------------ | ---------------- |
| **Скорость**  | ⚡ <10ms           | 🐌 500-2000ms            | ⚡/🐌 Зависит    |
| **Стоимость** | 💰 Free            | 💰💰💰 $0.01-0.10/запрос | 💰/💰💰 Зависит  |
| **Точность**  | 📊 90% (шаблоны)   | 📊 95% (может ошибаться) | 📊 95% (лучшее)  |
| **Гибкость**  | 🔒 Жесткие шаблоны | 🤸 Любые формулировки    | 🤸/🔒 Лучшее     |
| **Оффлайн**   | ✅ Да              | ❌ Нет (нужен API)       | ⚠️ Частично      |
| **Покрытие**  | 📈 90% запросов    | 📈 100% запросов         | 📈 100% запросов |

---

### 💡 Практические примеры

#### Пример 1: Telegram бот (Free tier)

```python
@bot.message_handler(commands=['check'])
def check_formula(message):
    query = message.text.replace('/check ', '')
    parser = NaturalLanguageParser()

    try:
        formula = parser.parse(query)
        result = evaluate_formula(formula, user_chart)
        bot.reply_to(message, f"✅ {formula}: {result}")
    except ValueError:
        bot.reply_to(message,
            "❌ Не понял вопрос. Попробуйте:\n"
            "- 'Солнце в Овне'\n"
            "- 'Марс соединение Сатурн'\n"
            "- 'есть ли большой трин?'"
        )
```

#### Пример 2: Telegram бот (Paid tier с AI)

```python
@bot.message_handler(commands=['ask'])
def ask_ai(message):
    query = message.text.replace('/ask ', '')
    parser = HybridParser(use_ai=True)

    # Сначала шаблоны, потом AI
    formula = parser.parse(query)
    result = evaluate_formula(formula, user_chart)

    bot.reply_to(message,
        f"🤖 Понял: {formula}\n"
        f"{'✅ Да' if result else '❌ Нет'}"
    )
```

#### Пример 3: Voice Assistant

```python
# Алиса/Siri/Google Assistant
def voice_check(speech_text: str):
    # Speech to text (уже сделано голосовым помощником)

    parser = HybridParser(use_ai=True)
    formula = parser.parse(speech_text)
    result = evaluate_formula(formula, user_chart)

    return f"{'Да' if result else 'Нет'}, у вас {formula}"

# User: "Алиса, есть ли у меня Марс с Сатурном?"
# Alexa: "Да, у вас Asp(Mars, Saturn, Conj)"
```

---

### 🎯 Финальная рекомендация по NL

**Для MVP (Minimum Viable Product):**

1. ✅ **Реализовать Template-based парсер** (20-30 шаблонов)
   - Покрывает 90% типичных вопросов
   - Работает оффлайн, бесплатно, быстро
   - Достаточно для большинства пользователей

2. ⏳ **Отложить AI на Phase 2**
   - Добавить когда появятся реальные пользователи
   - Собрать статистику "непонятых" вопросов
   - Решить: добавить шаблоны ИЛИ подключить AI

3. 🎯 **Гибридный подход в будущем**
   - Template-based для 90% запросов
   - AI fallback для сложных случаев
   - Опциональная подписка для AI режима

**Итого: ДА, естественный язык МОЖНО без AI для большинства случаев!** 🚀

---

## 🎨 РАУНД 5: Визуальный конструктор формул (Formula Builder)

### Предложение: "Конструктор как в Excel"

**UX Designer:**

**"Давайте сделаем визуальный конструктор! Щелкай мышкой - и формула готова, не сложнее Excel!"**

### Концепция: No-Code Formula Builder

**Проблема:**

- Астрологи не программисты
- Синтаксис пугает (`Asp(Mars, Saturn, Conj) AND NOT Mercury.Retrograde`)
- Хочется "накликать" формулу мышкой

**Решение:**
Визуальный конструктор с выпадающими списками + drag-n-drop

---

### 🖥️ Вариант 1: Desktop GUI (Tkinter/PyQt)

**Интерфейс:**

```
┌─────────────────────────────────────────────────────────┐
│ Formula Builder                                    [X]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [+ Add Condition]  [+ Add Group]  [Clear]  [Preview]  │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ Condition 1:                             [X]   │     │
│  │  ┌─────────┐  ┌──────┐  ┌─────────┐          │     │
│  │  │  Sun ▼  │  │ in ▼ │  │ Aries ▼ │          │     │
│  │  └─────────┘  └──────┘  └─────────┘          │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  Operator: ( ) AND  ( ) OR  ( ) NOT                    │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ Condition 2:                             [X]   │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │     │
│  │  │ Mars ▼  │  │ aspect ▼│  │Saturn ▼ │       │     │
│  │  └─────────┘  └─────────┘  └─────────┘       │     │
│  │  Type: ( ) Conjunction (●) Square ( ) Trine   │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │ Generated Formula:                          │       │
│  │                                             │       │
│  │ Sun.Sign == Aries AND Asp(Mars,Saturn,Sq)  │       │
│  │                                             │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│         [Copy Formula]  [Save]  [Execute]              │
└─────────────────────────────────────────────────────────┘
```

**Код (PyQt пример):**

```python
from PyQt5.QtWidgets import *
import json

class FormulaBuilderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astrology Formula Builder")
        self.conditions = []
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Кнопки управления
        buttons = QHBoxLayout()
        buttons.addWidget(QPushButton("+ Add Condition", clicked=self.add_condition))
        buttons.addWidget(QPushButton("+ Add Group", clicked=self.add_group))
        buttons.addWidget(QPushButton("Clear", clicked=self.clear_all))
        layout.addLayout(buttons)

        # Scroll area для условий
        self.conditions_area = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.conditions_area)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Preview формулы
        self.formula_preview = QTextEdit()
        self.formula_preview.setReadOnly(True)
        layout.addWidget(QLabel("Generated Formula:"))
        layout.addWidget(self.formula_preview)

        # Действия
        actions = QHBoxLayout()
        actions.addWidget(QPushButton("Copy", clicked=self.copy_formula))
        actions.addWidget(QPushButton("Save", clicked=self.save_formula))
        actions.addWidget(QPushButton("Execute", clicked=self.execute_formula))
        layout.addLayout(actions)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def add_condition(self):
        """Добавить новое условие."""
        condition_widget = ConditionWidget()
        condition_widget.changed.connect(self.update_preview)
        self.conditions_area.addWidget(condition_widget)
        self.conditions.append(condition_widget)
        self.update_preview()

    def update_preview(self):
        """Генерировать formula preview."""
        parts = []
        for i, cond in enumerate(self.conditions):
            formula_part = cond.to_formula()
            if i > 0:
                operator = " AND "  # TODO: выбор оператора
                parts.append(operator)
            parts.append(formula_part)

        formula = "".join(parts)
        self.formula_preview.setText(formula)

    def to_json(self):
        """Export to JSON (for storage)."""
        return {
            "conditions": [c.to_dict() for c in self.conditions],
            "formula": self.formula_preview.toPlainText()
        }

class ConditionWidget(QWidget):
    """Виджет для одного условия."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Тип условия
        self.condition_type = QComboBox()
        self.condition_type.addItems([
            "Planet in Sign",
            "Planet in House",
            "Aspect",
            "Retrograde",
            "Count Planets"
        ])
        self.condition_type.currentTextChanged.connect(self.update_fields)
        layout.addWidget(self.condition_type)

        # Динамические поля (зависят от типа)
        self.fields_widget = QWidget()
        self.fields_layout = QHBoxLayout()
        self.fields_widget.setLayout(self.fields_layout)
        layout.addWidget(self.fields_widget)

        # Remove button
        layout.addWidget(QPushButton("X", clicked=self.remove_self))

        self.setLayout(layout)
        self.update_fields()

    def update_fields(self):
        """Показать нужные поля для выбранного типа."""
        # Clear old fields
        for i in reversed(range(self.fields_layout.count())):
            self.fields_layout.itemAt(i).widget().setParent(None)

        condition_type = self.condition_type.currentText()

        if condition_type == "Planet in Sign":
            # [Planet ▼] in [Sign ▼]
            self.planet = QComboBox()
            self.planet.addItems(["Sun", "Moon", "Mercury", "Venus", "Mars",
                                 "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])
            self.sign = QComboBox()
            self.sign.addItems(["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"])

            self.fields_layout.addWidget(self.planet)
            self.fields_layout.addWidget(QLabel("in"))
            self.fields_layout.addWidget(self.sign)

        elif condition_type == "Planet in House":
            # [Planet ▼] in house [1-12]
            self.planet = QComboBox()
            self.planet.addItems(["Sun", "Moon", "Mercury", "Venus", "Mars",
                                 "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])
            self.house = QSpinBox()
            self.house.setRange(1, 12)

            self.fields_layout.addWidget(self.planet)
            self.fields_layout.addWidget(QLabel("in house"))
            self.fields_layout.addWidget(self.house)

        elif condition_type == "Aspect":
            # [Planet1 ▼] [Aspect ▼] [Planet2 ▼]
            self.planet1 = QComboBox()
            self.planet1.addItems(["Sun", "Moon", "Mercury", "Venus", "Mars",
                                  "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])
            self.aspect = QComboBox()
            self.aspect.addItems(["Conjunction", "Opposition", "Trine", "Square", "Sextile"])
            self.planet2 = QComboBox()
            self.planet2.addItems(["Sun", "Moon", "Mercury", "Venus", "Mars",
                                  "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])

            self.fields_layout.addWidget(self.planet1)
            self.fields_layout.addWidget(self.aspect)
            self.fields_layout.addWidget(self.planet2)

        elif condition_type == "Retrograde":
            # [Planet ▼] is [retrograde/direct]
            self.planet = QComboBox()
            self.planet.addItems(["Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                                 "Uranus", "Neptune", "Pluto"])
            self.retro = QComboBox()
            self.retro.addItems(["retrograde", "direct"])

            self.fields_layout.addWidget(self.planet)
            self.fields_layout.addWidget(QLabel("is"))
            self.fields_layout.addWidget(self.retro)

    def to_formula(self) -> str:
        """Конвертировать в formula string."""
        condition_type = self.condition_type.currentText()

        if condition_type == "Planet in Sign":
            return f"{self.planet.currentText()}.Sign == {self.sign.currentText()}"

        elif condition_type == "Planet in House":
            return f"{self.planet.currentText()}.House == {self.house.value()}"

        elif condition_type == "Aspect":
            aspect_map = {
                "Conjunction": "Conj",
                "Opposition": "Opp",
                "Trine": "Trine",
                "Square": "Square",
                "Sextile": "Sextile"
            }
            return f"Asp({self.planet1.currentText()}, {self.planet2.currentText()}, {aspect_map[self.aspect.currentText()]})"

        elif condition_type == "Retrograde":
            retro_value = "True" if self.retro.currentText() == "retrograde" else "False"
            return f"{self.planet.currentText()}.Retrograde == {retro_value}"

        return ""

    def to_dict(self) -> dict:
        """Export to JSON."""
        return {
            "type": self.condition_type.currentText(),
            "formula": self.to_formula()
        }

# Использование:
if __name__ == "__main__":
    app = QApplication([])
    window = FormulaBuilderGUI()
    window.show()
    app.exec_()
```

---

### 📱 Вариант 2: Mobile App (React Native / Flutter)

**Интерфейс (мобильный):**

```
┌───────────────────────────┐
│ ☰  Formula Builder    [+] │
├───────────────────────────┤
│                           │
│ ┌───────────────────────┐ │
│ │ Condition 1      [×]  │ │
│ │                       │ │
│ │ [   Sun       ▼]      │ │
│ │ [   in sign   ▼]      │ │
│ │ [   Aries     ▼]      │ │
│ │                       │ │
│ └───────────────────────┘ │
│                           │
│      AND / OR / NOT       │
│                           │
│ ┌───────────────────────┐ │
│ │ Condition 2      [×]  │ │
│ │                       │ │
│ │ [   Mars      ▼]      │ │
│ │ [   aspect    ▼]      │ │
│ │ [   Saturn    ▼]      │ │
│ │ Type: Square          │ │
│ │                       │ │
│ └───────────────────────┘ │
│                           │
│ ┌─────────────────────┐   │
│ │ Generated:          │   │
│ │ Sun.Sign == Aries   │   │
│ │ AND                 │   │
│ │ Asp(Mars,Saturn,Sq) │   │
│ └─────────────────────┘   │
│                           │
│  [Copy] [Save] [Run]      │
└───────────────────────────┘
```

**Код (React Native пример):**

```jsx
import React, { useState } from "react";
import { View, Text, Button, Picker, ScrollView } from "react-native";

const FormulaBuilder = () => {
  const [conditions, setConditions] = useState([]);

  const addCondition = () => {
    setConditions([
      ...conditions,
      {
        type: "planet_in_sign",
        planet: "Sun",
        sign: "Aries",
      },
    ]);
  };

  const generateFormula = () => {
    return conditions
      .map((cond, i) => {
        let formula = "";

        if (cond.type === "planet_in_sign") {
          formula = `${cond.planet}.Sign == ${cond.sign}`;
        } else if (cond.type === "aspect") {
          formula = `Asp(${cond.planet1}, ${cond.planet2}, ${cond.aspect})`;
        }

        if (i > 0) return ` AND ${formula}`;
        return formula;
      })
      .join("");
  };

  return (
    <ScrollView>
      <Button title="+ Add Condition" onPress={addCondition} />

      {conditions.map((cond, idx) => (
        <ConditionCard
          key={idx}
          condition={cond}
          onChange={(newCond) => {
            const newConditions = [...conditions];
            newConditions[idx] = newCond;
            setConditions(newConditions);
          }}
          onRemove={() => {
            setConditions(conditions.filter((_, i) => i !== idx));
          }}
        />
      ))}

      <View style={{ padding: 10, backgroundColor: "#f0f0f0" }}>
        <Text>Generated Formula:</Text>
        <Text style={{ fontFamily: "monospace" }}>{generateFormula()}</Text>
      </View>

      <Button title="Execute" onPress={() => alert("TODO: execute")} />
    </ScrollView>
  );
};
```

---

### 🌐 Вариант 3: Web Interface (React/Vue)

**Интерфейс (веб):**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Astrology Formula Builder</title>
    <style>
      .condition-card {
        border: 1px solid #ccc;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
      }
      .formula-preview {
        background: #f5f5f5;
        padding: 15px;
        font-family: monospace;
        border-left: 4px solid #4caf50;
      }
    </style>
  </head>
  <body>
    <div id="app">
      <h1>🔮 Formula Builder</h1>

      <button @click="addCondition">+ Add Condition</button>

      <div v-for="(cond, idx) in conditions" :key="idx" class="condition-card">
        <select v-model="cond.type" @change="updatePreview">
          <option value="planet_in_sign">Planet in Sign</option>
          <option value="aspect">Aspect</option>
          <option value="retrograde">Retrograde</option>
        </select>

        <!-- Planet in Sign -->
        <template v-if="cond.type === 'planet_in_sign'">
          <select v-model="cond.planet" @change="updatePreview">
            <option v-for="p in planets" :value="p">{{ p }}</option>
          </select>
          <span>in</span>
          <select v-model="cond.sign" @change="updatePreview">
            <option v-for="s in signs" :value="s">{{ s }}</option>
          </select>
        </template>

        <!-- Aspect -->
        <template v-if="cond.type === 'aspect'">
          <select v-model="cond.planet1" @change="updatePreview">
            <option v-for="p in planets" :value="p">{{ p }}</option>
          </select>
          <select v-model="cond.aspect" @change="updatePreview">
            <option>Conjunction</option>
            <option>Opposition</option>
            <option>Trine</option>
            <option>Square</option>
          </select>
          <select v-model="cond.planet2" @change="updatePreview">
            <option v-for="p in planets" :value="p">{{ p }}</option>
          </select>
        </template>

        <button @click="removeCondition(idx)">×</button>

        <div v-if="idx < conditions.length - 1">
          <label>
            <input
              type="radio"
              name="operator_{{idx}}"
              value="AND"
              v-model="cond.operator"
            />
            AND
          </label>
          <label>
            <input
              type="radio"
              name="operator_{{idx}}"
              value="OR"
              v-model="cond.operator"
            />
            OR
          </label>
        </div>
      </div>

      <div class="formula-preview">
        <strong>Generated Formula:</strong>
        <pre>{{ generatedFormula }}</pre>
      </div>

      <button @click="copyFormula">📋 Copy</button>
      <button @click="saveFormula">💾 Save</button>
      <button @click="executeFormula">▶️ Execute</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/vue@3"></script>
    <script>
      const { createApp } = Vue;

      createApp({
        data() {
          return {
            conditions: [],
            planets: [
              "Sun",
              "Moon",
              "Mercury",
              "Venus",
              "Mars",
              "Jupiter",
              "Saturn",
            ],
            signs: [
              "Aries",
              "Taurus",
              "Gemini",
              "Cancer",
              "Leo",
              "Virgo",
              "Libra",
              "Scorpio",
              "Sagittarius",
              "Capricorn",
              "Aquarius",
              "Pisces",
            ],
            generatedFormula: "",
          };
        },
        methods: {
          addCondition() {
            this.conditions.push({
              type: "planet_in_sign",
              planet: "Sun",
              sign: "Aries",
              operator: "AND",
            });
            this.updatePreview();
          },
          removeCondition(idx) {
            this.conditions.splice(idx, 1);
            this.updatePreview();
          },
          updatePreview() {
            this.generatedFormula = this.conditions
              .map((cond, i) => {
                let formula = "";

                if (cond.type === "planet_in_sign") {
                  formula = `${cond.planet}.Sign == ${cond.sign}`;
                } else if (cond.type === "aspect") {
                  formula = `Asp(${cond.planet1}, ${cond.planet2}, ${cond.aspect})`;
                } else if (cond.type === "retrograde") {
                  formula = `${cond.planet}.Retrograde == True`;
                }

                if (i > 0) {
                  return ` ${this.conditions[i - 1].operator} ${formula}`;
                }
                return formula;
              })
              .join("");
          },
          copyFormula() {
            navigator.clipboard.writeText(this.generatedFormula);
            alert("Formula copied!");
          },
          saveFormula() {
            const json = JSON.stringify(
              {
                conditions: this.conditions,
                formula: this.generatedFormula,
              },
              null,
              2,
            );

            const blob = new Blob([json], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "astro_formula.json";
            a.click();
          },
          executeFormula() {
            // TODO: Call API to execute formula
            alert(`Executing: ${this.generatedFormula}`);
          },
        },
      }).mount("#app");
    </script>
  </body>
</html>
```

---

### 📊 JSON Representation (Backend Format)

**Формат хранения формул:**

```json
{
  "name": "My Formula",
  "description": "Sun in Aries AND Mars square Saturn",
  "conditions": [
    {
      "type": "planet_in_sign",
      "planet": "Sun",
      "sign": "Aries"
    },
    {
      "operator": "AND",
      "type": "aspect",
      "planet1": "Mars",
      "planet2": "Saturn",
      "aspect": "Square"
    }
  ],
  "generated_formula": "Sun.Sign == Aries AND Asp(Mars, Saturn, Square)"
}
```

**Конвертер JSON → Formula:**

```python
class FormulaBuilder:
    """Convert JSON builder format to formula string."""

    @staticmethod
    def from_json(data: dict) -> str:
        """Convert JSON to formula."""
        parts = []

        for condition in data['conditions']:
            # Get operator
            if 'operator' in condition and parts:
                parts.append(f" {condition['operator']} ")

            # Build condition formula
            if condition['type'] == 'planet_in_sign':
                formula = f"{condition['planet']}.Sign == {condition['sign']}"

            elif condition['type'] == 'planet_in_house':
                formula = f"{condition['planet']}.House == {condition['house']}"

            elif condition['type'] == 'aspect':
                formula = f"Asp({condition['planet1']}, {condition['planet2']}, {condition['aspect']})"

            elif condition['type'] == 'retrograde':
                retro = "True" if condition.get('is_retrograde', True) else "False"
                formula = f"{condition['planet']}.Retrograde == {retro}"

            elif condition['type'] == 'count_planets':
                operator = condition.get('count_operator', '>=')
                formula = f"Count(Planets, Sign=={condition['sign']}) {operator} {condition['count']}"

            parts.append(formula)

        return "".join(parts)

    @staticmethod
    def to_json(formula: str) -> dict:
        """Parse formula string back to JSON (inverse operation)."""
        # TODO: This is harder - need parser
        # For now, just store as string
        return {
            "type": "raw_formula",
            "formula": formula
        }

# Пример использования:
json_data = {
    "conditions": [
        {"type": "planet_in_sign", "planet": "Sun", "sign": "Aries"},
        {"operator": "AND", "type": "aspect", "planet1": "Mars", "planet2": "Saturn", "aspect": "Square"}
    ]
}

formula = FormulaBuilder.from_json(json_data)
print(formula)
# → "Sun.Sign == Aries AND Asp(Mars, Saturn, Square)"
```

---

### 📱 Telegram Bot Integration

**Использование builder в телеграм боте:**

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler

class TelegramFormulaBuilder:
    """Interactive formula builder for Telegram."""

    def __init__(self):
        self.user_formulas = {}  # user_id → formula_data

    def start_builder(self, update: Update, context):
        """Начать построение формулы."""
        user_id = update.effective_user.id
        self.user_formulas[user_id] = {"conditions": []}

        keyboard = [
            [InlineKeyboardButton("🌟 Planet in Sign", callback_data="add_planet_sign")],
            [InlineKeyboardButton("🏠 Planet in House", callback_data="add_planet_house")],
            [InlineKeyboardButton("🔗 Aspect", callback_data="add_aspect")],
            [InlineKeyboardButton("🔄 Retrograde", callback_data="add_retrograde")],
            [InlineKeyboardButton("✅ Done", callback_data="builder_done")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("What do you want to add?", reply_markup=reply_markup)

    def add_planet_sign(self, update: Update, context):
        """Добавить условие 'планета в знаке'."""
        # Step 1: Select planet
        keyboard = [
            [InlineKeyboardButton("☉ Sun", callback_data="planet_Sun")],
            [InlineKeyboardButton("☽ Moon", callback_data="planet_Moon")],
            [InlineKeyboardButton("☿ Mercury", callback_data="planet_Mercury")],
            # ... и т.д.
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text("Select planet:", reply_markup=reply_markup)

    def show_preview(self, user_id):
        """Показать preview формулы."""
        data = self.user_formulas[user_id]
        formula = FormulaBuilder.from_json(data)
        return f"📝 Current formula:\n`{formula}`"

# Bot commands:
# /build - Start formula builder
# User clicks buttons
# Bot shows: "Sun.Sign == Aries"
# User adds more conditions
# Bot shows: "Sun.Sign == Aries AND Asp(Mars, Saturn, Square)"
# User clicks "Done"
# Bot executes formula
```

---

### 🎯 Pros & Cons

**✅ Плюсы визуального конструктора:**

1. **Не нужно знать синтаксис** - просто выбираешь из списков
2. **Нет ошибок** - невозможно написать неправильную формулу
3. **Быстрее для простых формул** - 3 клика вместо печатания
4. **Обучает синтаксису** - видишь generated formula
5. **Мобильно-дружелюбен** - работает на телефоне
6. **Доступен неопытным** - астрологи без программирования

**⚠️ Минусы:**

1. **Медленнее для сложных формул** - много кликов
2. **Ограничен UI** - может не поддерживать все фичи DSL
3. **Занимает место** - нужен экран
4. **Требует разработки UI** - дополнительная работа

---

### 💡 Рекомендации

**Phase 1 (MVP):**

- ✅ Простой веб-конструктор (5-10 типов условий)
- ✅ Export в formula string
- ✅ Preview в реальном времени

**Phase 2:**

- ⏳ Desktop GUI (PyQt/Tkinter)
- ⏳ Telegram bot interactive builder
- ⏳ Save/load templates

**Phase 3:**

- 🎯 Mobile app (React Native/Flutter)
- 🎯 Drag-n-drop визуальный редактор
- 🎯 Библиотека готовых формул

**Вывод: Конструктор - отличная идея для v2.0 или параллельно с DSL!** 🎨

---

## 🔧 РАУНД 6: Сложные логические операторы

### Вопрос: Нужны ли более сложные операторы и комбинации?

**Backend Developer:**

**"Давайте разберем, что ЕЩЁ может понадобиться помимо AND/OR/NOT!"**

---

### 1. Скобки для группировки (КРИТИЧНО!) ⭐

**Проблема:**

```python
# Без скобок - неоднозначно:
Sun.Sign == Aries AND Moon.Sign == Taurus OR Mars.Sign == Leo

# Это (Sun AND Moon) OR Mars?
# Или Sun AND (Moon OR Mars)?
```

**Решение:**

```python
# Явная группировка скобками:
(Sun.Sign == Aries AND Moon.Sign == Taurus) OR Mars.Sign == Leo

# ИЛИ:
Sun.Sign == Aries AND (Moon.Sign == Taurus OR Mars.Sign == Leo)
```

**Рекомендация:** ✅ **ОБЯЗАТЕЛЬНО поддерживать скобки!**

**Приоритет по умолчанию (если нет скобок):**

1. `NOT` / `!` (высший)
2. `AND` / `&&` (средний)
3. `OR` / `||` (низший)

```python
# Без скобок:
NOT Sun.Retrograde AND Mars.House == 1 OR Venus.Sign == Taurus

# Интерпретируется как:
(NOT Sun.Retrograde) AND (Mars.House == 1) OR (Venus.Sign == Taurus)

# Или еще точнее:
((NOT Sun.Retrograde) AND (Mars.House == 1)) OR (Venus.Sign == Taurus)
```

---

### 2. XOR (Exclusive OR) - либо одно, либо другое ❓

**Что это:**

```python
# XOR: true если ТОЛЬКО ОДНО условие true (но не оба)
Sun.Sign == Aries XOR Moon.Sign == Aries

# True: Sun в Овне, но Moon НЕ в Овне
# True: Moon в Овне, но Sun НЕ в Овне
# False: Оба в Овне
# False: Оба НЕ в Овне
```

**Астрологические примеры:**

```python
# "Либо Солнце в огненном знаке, либо Луна, но не оба"
In(Sun.Sign, Fire) XOR In(Moon.Sign, Fire)

# "Либо ретроградный Меркурий, либо ретроградная Венера (но не оба)"
Mercury.Retrograde XOR Venus.Retrograde
```

**Альтернатива (без XOR):**

```python
# Можно выразить через AND/OR/NOT:
(Sun.Sign == Aries AND NOT Moon.Sign == Aries) OR
(NOT Sun.Sign == Aries AND Moon.Sign == Aries)

# Или короче:
(Sun.Sign == Aries OR Moon.Sign == Aries) AND NOT (Sun.Sign == Aries AND Moon.Sign == Aries)
```

**Professional Astrologer:**

**"XOR нужен РЕДКО в астрологии. Обычно важно 'хотя бы одно' (OR) или 'оба' (AND), но не 'ровно одно'."**

**Рекомендация:** ⏳ **Отложить на v2.0** (можно выразить через AND/OR/NOT)

---

### 3. ALL() / ANY() / NONE() - удобные агрегаторы ⭐

**Проблема:**

```python
# Хочу проверить: "все три планеты в огненных знаках"
In(Sun.Sign, Fire) AND In(Mars.Sign, Fire) AND In(Jupiter.Sign, Fire)
# Длинно и неудобно!
```

**Решение:**

```python
# Вариант A: Функция ALL
ALL([
    In(Sun.Sign, Fire),
    In(Mars.Sign, Fire),
    In(Jupiter.Sign, Fire)
])

# Вариант B: Count-based (уже есть)
Count([Sun, Mars, Jupiter], In(Sign, Fire)) == 3

# Вариант C: Компактный синтаксис
ALL(Sun, Mars, Jupiter) In(Sign, Fire)
```

**Примеры использования:**

```python
# ANY: хотя бы одна планета ретроградная
ANY([Mercury.Retrograde, Venus.Retrograde, Mars.Retrograde])

# Или через Count:
Count([Mercury, Venus, Mars], Retrograde==True) >= 1

# NONE: ни одна планета не в Овне
NONE([
    Sun.Sign == Aries,
    Moon.Sign == Aries,
    Mars.Sign == Aries
])

# Или через Count:
Count([Sun, Moon, Mars], Sign==Aries) == 0

# ALL: все личные планеты в угловых домах
ALL([
    In(Sun.House, [1, 4, 7, 10]),
    In(Moon.House, [1, 4, 7, 10]),
    In(Mercury.House, [1, 4, 7, 10]),
    In(Venus.House, [1, 4, 7, 10]),
    In(Mars.House, [1, 4, 7, 10])
])
```

**UX Designer:**

**"ALL/ANY/NONE читаются понятнее, чем Count! Но Count мощнее."**

**Рекомендация:** 🤔 **Опционально** - можно добавить как синтаксический сахар

```python
# Реализация:
ALL([conditions]) → все conditions == True
ANY([conditions]) → хотя бы один == True
NONE([conditions]) → все conditions == False

# Через Count:
ALL([...]) === Count([...]) == len([...])
ANY([...]) === Count([...]) >= 1
NONE([...]) === Count([...]) == 0
```

---

### 4. AT_LEAST() / AT_MOST() / EXACTLY() - точный подсчет 🎯

**Расширение Count:**

```python
# Вместо:
Count(Planets, In(Sign, Fire)) >= 3

# Можно:
AT_LEAST(3, Planets, In(Sign, Fire))

# Вместо:
Count(Planets, Retrograde==True) <= 2

# Можно:
AT_MOST(2, Planets, Retrograde==True)

# Вместо:
Count(Planets, House==7) == 1

# Можно:
EXACTLY(1, Planets, House==7)
```

**Примеры:**

```python
# "Хотя бы 4 планеты в знаках земли"
AT_LEAST(4, Planets, In(Sign, Earth))

# "Не более 2 планет ретроградных"
AT_MOST(2, Planets, Retrograde==True)

# "Ровно 3 планеты в кардинальных знаках"
EXACTLY(3, Planets, In(Sign, Cardinal))
```

**Backend Developer:**

**"Это просто алиасы для Count! Можно добавить, но не критично."**

**Рекомендация:** ⏳ **Низкий приоритет** - Count уже покрывает все случаи

---

### 5. IMPLIES (импликация →) - "если A, то B" 🎓

**Логика:**

```python
# A IMPLIES B эквивалентно: NOT A OR B
Sun.Sign == Aries IMPLIES Mars.Dignity == Rulership

# Читается: "Если Солнце в Овне, то Марс должен быть в управлении"
# True если: Sun НЕ в Овне ИЛИ Mars в управлении
# False только если: Sun в Овне И Mars НЕ в управлении
```

**Астрологические примеры:**

```python
# "Если Луна в 7 доме, то должен быть брак (аспект Венеры)"
Moon.House == 7 IMPLIES Asp(Venus, [Sun, Moon, Asc], Any)

# "Если есть стеллиум, то он должен быть в фиксированных знаках"
HasPattern(Stellium) IMPLIES Count(Planets, In(Sign, Fixed)) >= 3
```

**Альтернатива (без IMPLIES):**

```python
# Через NOT...OR:
NOT (Sun.Sign == Aries) OR Mars.Dignity == Rulership

# Или логически эквивалентно:
Sun.Sign != Aries OR Mars.Dignity == Rulership
```

**Professional Astrologer:**

**"Слишком программистский! Астрологи так не думают!"**

**Regular User:**

**"Что это вообще такое?? 😵"**

**Рекомендация:** ❌ **НЕ НУЖНО** - слишком академическое, непонятно пользователям

---

### 6. Вложенные условия IF...THEN...ELSE 🌳

**Идея:**

```python
IF Sun.Sign == Aries THEN
    Mars.Dignity == Rulership
ELSE
    Mars.Dignity == Detriment
```

**Проблемы:**

1. Сложно читать
2. Можно выразить через AND/OR
3. Не характерно для астрологии

**Альтернатива:**

```python
# Через тернарный оператор (если нужен результат):
Mars.Dignity == (Rulership IF Sun.Sign == Aries ELSE Detriment)

# Через обычную логику:
(Sun.Sign == Aries AND Mars.Dignity == Rulership) OR
(Sun.Sign != Aries AND Mars.Dignity == Detriment)
```

**Рекомендация:** ❌ **НЕ НУЖНО** - слишком сложно

---

### 7. BETWEEN / IN_RANGE - диапазоны 📊

**Для чисел:**

```python
# Вместо:
Sun.Degree >= 10 AND Sun.Degree <= 20

# Можно:
BETWEEN(Sun.Degree, 10, 20)
# ИЛИ:
Sun.Degree IN_RANGE [10..20]
# ИЛИ Python-style:
10 <= Sun.Degree <= 20
```

**Для дат (транзиты):**

```python
# Событие между 2024-01-01 и 2024-12-31
BETWEEN(EventDate, 2024-01-01, 2024-12-31)

# Транзит в диапазоне
Transit(Mars.Conj.Saturn) BETWEEN 2024-06-01 AND 2024-06-30
```

**Рекомендация:** ✅ **Да, полезно!** Можно добавить в v1.0 или v2.0

---

### 8. WITHIN / NEAR - орбисы и близость 🎯

**Для аспектов с орбисом:**

```python
# Солнце около 0° Овна (±5°)
WITHIN(Sun.Degree, 0, orb=5)

# Марс в пределах орбиса соединения с Сатурном
WITHIN(Asp(Mars, Saturn), Conj, orb=8)

# Альтернатива (уже есть в Asp):
Asp(Mars, Saturn, Conj, orb=8)
```

**Рекомендация:** ⏸ **Уже покрыто функцией Asp() с параметром orb**

---

### 9. Квантификаторы FOR_ALL / EXISTS 🔍

**Идея из математической логики:**

```python
# "Для ВСЕХ планет верно, что они не ретроградные"
FOR_ALL planet IN Planets: NOT planet.Retrograde

# "Существует планета в 10 доме"
EXISTS planet IN Planets: planet.House == 10
```

**Альтернатива через Count:**

```python
# FOR_ALL:
Count(Planets, Retrograde==True) == 0

# EXISTS:
Count(Planets, House==10) >= 1
```

**Рекомендация:** ⏳ **Низкий приоритет** - Count покрывает это

---

### 📊 Сводная таблица: Что добавить?

| Оператор/Функция             | Нужен?         | Приоритет       | Комментарий                              |
| ---------------------------- | -------------- | --------------- | ---------------------------------------- |
| **Скобки ()**                | ✅ ДА          | ⭐⭐⭐ Критично | Группировка обязательна!                 |
| **Приоритет операторов**     | ✅ ДА          | ⭐⭐⭐ Критично | NOT > AND > OR                           |
| **XOR**                      | ⏳ v2.0        | ⭐ Низкий       | Редко нужен, можно выразить через AND/OR |
| **ALL/ANY/NONE**             | 🤔 Опционально | ⭐⭐ Средний    | Синтаксический сахар для Count           |
| **AT_LEAST/AT_MOST/EXACTLY** | ⏳ v2.0        | ⭐ Низкий       | Алиасы для Count                         |
| **IMPLIES (→)**              | ❌ НЕТ         | -               | Слишком академическое                    |
| **IF...THEN...ELSE**         | ❌ НЕТ         | -               | Слишком сложно                           |
| **BETWEEN/IN_RANGE**         | ✅ ДА          | ⭐⭐ Средний    | Удобно для диапазонов                    |
| **WITHIN/NEAR**              | ⏸ Уже есть     | -               | Покрыто orb в Asp()                      |
| **FOR_ALL/EXISTS**           | ⏳ v2.0        | ⭐ Низкий       | Count покрывает                          |

---

### 🎯 Финальные рекомендации (Раунд 6)

**✅ Добавить в v1.0 (КРИТИЧНО):**

1. **Скобки () для группировки**

   ```python
   (Sun.Sign == Aries AND Moon.Sign == Taurus) OR Mars.House == 1
   ```

2. **Чёткий приоритет операторов**

   ```python
   # Без скобок:
   NOT A AND B OR C
   # → ((NOT A) AND B) OR C
   ```

3. **Документация приоритетов**
   - Высший: `NOT`, `!`
   - Средний: `AND`, `&&`
   - Низший: `OR`, `||`
   - Скобки переопределяют

**🤔 Рассмотреть для v1.0 (ОПЦИОНАЛЬНО):**

4. **ALL/ANY/NONE** - если пользователи запросят

   ```python
   ALL([Sun.Sign == Aries, Moon.Sign == Aries, Mars.Sign == Aries])
   ```

5. **BETWEEN для диапазонов** - полезно для градусов
   ```python
   BETWEEN(Sun.Degree, 0, 10)
   # Альтернатива: 0 <= Sun.Degree <= 10
   ```

**⏳ Отложить на v2.0 (НЕ КРИТИЧНО):**

6. **XOR** - редко нужен
7. **AT_LEAST/AT_MOST** - Count покрывает
8. **FOR_ALL/EXISTS** - Count покрывает

**❌ НЕ ДОБАВЛЯТЬ:**

9. **IMPLIES** - непонятно пользователям
10. **IF...THEN...ELSE** - слишком сложно

---

### 💡 Примеры с новыми операторами

**С группировкой скобками:**

```python
# Сложное условие с явной группировкой:
(Sun.Sign == Aries OR Sun.Sign == Leo OR Sun.Sign == Sagittarius) AND
(Moon.House == 1 OR Moon.House == 10) AND
NOT Saturn.Retrograde

# Вложенные скобки:
((Sun.Sign == Aries AND Moon.Sign == Taurus) OR
 (Sun.Sign == Leo AND Moon.Sign == Scorpio)) AND
Mars.House == 1
```

**С приоритетом (без скобок):**

```python
# Интерпретация:
Sun.Sign == Aries AND Moon.Sign == Taurus OR Mars.House == 1
# → (Sun.Sign == Aries AND Moon.Sign == Taurus) OR Mars.House == 1

# С NOT:
NOT Sun.Retrograde AND Mars.House == 1 OR Venus.Sign == Taurus
# → ((NOT Sun.Retrograde) AND Mars.House == 1) OR Venus.Sign == Taurus
```

**С ALL/ANY (если добавим):**

```python
# Все планеты в огне:
ALL([
    In(Sun.Sign, Fire),
    In(Moon.Sign, Fire),
    In(Mars.Sign, Fire),
    In(Jupiter.Sign, Fire)
])

# Хотя бы одна планета ретроградная:
ANY([Mercury.Retrograde, Venus.Retrograde, Mars.Retrograde])
```

**С BETWEEN (если добавим):**

```python
# Солнце в первой декаде Овна (0-10°):
Sun.Sign == Aries AND BETWEEN(Sun.Degree, 0, 10)

# Возраст от 25 до 35 лет:
BETWEEN(Age, 25, 35)
```

---

### 📖 Обновления документации

**Нужно добавить:**

1. **Operator Precedence Guide**
   - Таблица приоритетов
   - Примеры со скобками и без
   - Типичные ошибки

2. **Grouping & Nesting**
   - Как использовать скобки
   - Вложенные выражения
   - Best practices

3. **Advanced Operators Reference**
   - ALL/ANY/NONE (если добавим)
   - BETWEEN (если добавим)
   - Примеры использования

---

**Вывод Раунда 6: Скобки и приоритет операторов - КРИТИЧНО для v1.0! Остальное можно добавить позже по запросу.** 🔧

---

### 📋 Documentation needed:

1. **Quick Start** - 5 примеров для начала
2. **Reference** - все операторы и функции
3. **Cookbook** - типичные задачи (20+ рецептов)
4. **API Docs** - для разработчиков
5. **Builder Guide** - как использовать визуальный конструктор

---

## 💬 ФИНАЛЬНЫЕ ВОПРОСЫ ДЛЯ УТВЕРЖДЕНИЯ

### Критичные (для v1.0):

1. **Операторы**: AND/OR/NOT (SQL) или and/or/not (Python) или оба?
   - Рекомендация: Оба (dual syntax)

2. **Скобки**: Обязательная поддержка () для группировки?
   - Рекомендация: ✅ ДА, критично!

3. **Приоритет**: NOT > AND > OR (стандартный)?
   - Рекомендация: ✅ ДА

4. **Регистр**: Case-sensitive (Mars) или case-insensitive (mars)?
   - Рекомендация: Case-insensitive для удобства

5. **Русский язык**: Поддерживать "И/ИЛИ/НЕ" для Telegram ботов?
   - Рекомендация: ✅ ДА, для ботов

### Опциональные (можно отложить):

6. **ALL/ANY/NONE**: Добавить как синтаксический сахар?
   - Можно через Count(), но ALL/ANY читабельнее

7. **BETWEEN**: Для диапазонов градусов/дат?
   - Можно через `>=` и `<=`, но BETWEEN удобнее

8. **XOR**: Exclusive OR (либо одно, либо другое)?
   - Редко нужен, можно отложить

9. **Синонимы аспектов**: Conjunction = Conj = Cnj?
   - Удобно, но усложняет парсер

**Главный вопрос: Начинаем имплементацию с базовым набором (AND/OR/NOT + скобки) или сразу с расширенным?** 🚀

---

## 🎯 РАУНД 7: Альтернативный синтаксис any() и астрологическая валидация

### Предложение: `any(множество).свойство` вместо `ANY([...])`

**User предлагает:**

**"Давайте сделаем `any([Sun, Moon, Mars]).Sign == Aries` вместо `ANY([Sun.Sign == Aries, Moon.Sign == Aries, ...])`!"**

---

### Синтаксис с any()

**Идея:**

```python
# Вместо длинного:
Sun.Sign == Aries OR Moon.Sign == Aries OR Mars.Sign == Aries

# Или:
ANY([Sun.Sign == Aries, Moon.Sign == Aries, Mars.Sign == Aries])

# Можно:
any([Sun, Moon, Mars]).Sign == Aries
```

**Как определить, что это - аспект или свойство:**

```python
# Если после .property есть == или != → это свойство
any([Sun, Moon, Mars]).Sign == Aries
any([Mercury, Venus]).Retrograde == True
any([Mars, Saturn]).House == 10

# Если после .method есть другой объект/множество → это аспект
any([Mars, Saturn]).conj(Pluto)
Sun.conj(any([Saturn, Pluto]))
any([Mars, Venus]).trine(any([Jupiter, Neptune]))

# Если после .method скобки с параметрами → это функция/свойство
any([Sun, Moon]).in_sign(Fire)
any([Mars, Saturn]).in_house([1, 10, 7, 4])
```

---

### 📊 Сравнение синтаксисов

| Задача                  | Старый синтаксис                            | Новый синтаксис `any()`                                  |
| ----------------------- | ------------------------------------------- | -------------------------------------------------------- |
| **Планета в знаке**     | `Sun.Sign == Aries OR Moon.Sign == Aries`   | `any([Sun, Moon]).Sign == Aries`                         |
| **Аспект к нескольким** | `Asp(Mars, [Saturn, Pluto], Conj)`          | `Mars.conj(any([Saturn, Pluto]))`                        |
| **Несколько к одному**  | `Asp([Mars, Venus], Saturn, Conj)`          | `any([Mars, Venus]).conj(Saturn)`                        |
| **Многие ко многим**    | `Asp([Mars, Venus], [Saturn, Pluto], Conj)` | `any([Mars, Venus]).conj(any([Saturn, Pluto]))`          |
| **Ретроградность**      | `Mercury.Retrograde OR Venus.Retrograde`    | `any([Mercury, Venus]).Retrograde == True`               |
| **Дома**                | `Mars.House == 1 OR Mars.House == 10`       | `Mars.House IN [1, 10]` или `any([1, 10]) == Mars.House` |

---

### 🤔 Плюсы и минусы

**✅ Плюсы `any()` синтаксиса:**

1. **Компактнее** - меньше повторений

   ```python
   # Было:
   Sun.Sign == Aries OR Moon.Sign == Aries OR Mars.Sign == Aries

   # Стало:
   any([Sun, Moon, Mars]).Sign == Aries
   ```

2. **Читабельнее** для списков

   ```python
   any([Mercury, Venus, Mars]).Retrograde == True
   ```

3. **Логично** - "любой из [список] имеет свойство X"

4. **Похоже на Python/SQL** - `any()` знакомая функция

**⚠️ Минусы:**

1. **Неоднозначность** - что означает `any([Sun, Moon]).conj(Mars)`?
   - (Sun OR Moon) conj Mars?
   - Sun conj (Moon conj Mars)?

2. **Сложность парсинга** - нужен контекстный анализ

   ```python
   # Парсер должен понять:
   any([...]).Sign == X  # → проверка свойства
   any([...]).conj(Y)     # → аспект
   any([...]).in_house()  # → метод
   ```

3. **Конфликт с функциями** - `any()` это оператор или функция?

---

### 💡 Professional Astrologer НАКОНЕЦ-ТО говорит об ошибках:

**"СТОП! А КТО БУДЕТ ВАЛИДИРОВАТЬ АСТРОЛОГИЧЕСКИЙ БРЕД?!"**

### Астрологическая валидация (критично!) ⚠️

**Невозможные комбинации:**

```python
# ❌ ОШИБКА: Солнце НИКОГДА не ретроградно!
Sun.Retrograde == True

# ❌ ОШИБКА: Луна НИКОГДА не ретроградна!
Moon.Retrograde == True

# ❌ ОШИБКА: Аспект планеты к самой себе невозможен
Asp(Mars, Mars, Conj)
Mars.conj(Mars)

# ❌ ОШИБКА: Дом должен быть 1-12
Sun.House == 15

# ❌ ОШИБКА: Градус должен быть 0-29 (или 0-359 в абсолютных)
Sun.Degree == 35  # для градуса в знаке

# ❌ ОШИБКА: Несуществующий аспект (если используем предопределенные)
Asp(Mars, Saturn, Quintile)  # если Quintile не поддерживается

# ⚠️ ПРЕДУПРЕЖДЕНИЕ: Сомнительные комбинации
Asc.Retrograde  # У Асцендента нет ретроградности
MC.Sign  # Технически верно, но редко используется
```

**Список планет без ретроградности:**

- ✅ Могут быть ретроградными: Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- ❌ НЕ могут: Sun, Moon
- ❌ НЕ могут: Asc, MC, IC, Dsc (это точки, не планеты)
- ⚠️ Спорно: North Node, South Node (технически могут, но это вычисляемые точки)

---

### 🔧 Как реализовать валидацию

**Вариант A: На уровне парсера (compile-time)**

```python
class FormulaValidator:
    """Validate formula for astrological errors."""

    NON_RETROGRADE_BODIES = {'Sun', 'Moon', 'Asc', 'MC', 'IC', 'Dsc'}
    VALID_HOUSES = range(1, 13)
    VALID_DEGREES_IN_SIGN = range(0, 30)

    def validate(self, ast):
        """Check AST for astrological impossibilities."""
        errors = []

        # Check retrograde errors
        if ast.type == 'property_check':
            if ast.property == 'Retrograde':
                if ast.object in self.NON_RETROGRADE_BODIES:
                    errors.append(
                        f"Error: {ast.object} cannot be retrograde! "
                        f"Only planets can be retrograde (not Sun/Moon/angles)."
                    )

        # Check self-aspect
        if ast.type == 'aspect':
            if ast.planet1 == ast.planet2:
                errors.append(
                    f"Error: Planet cannot aspect itself! "
                    f"Asp({ast.planet1}, {ast.planet2}, ...) is meaningless."
                )

        # Check house range
        if ast.type == 'property_check' and ast.property == 'House':
            if ast.value not in self.VALID_HOUSES:
                errors.append(
                    f"Error: House must be 1-12, got {ast.value}"
                )

        return errors

# Использование:
formula = "Sun.Retrograde == True"
ast = parse(formula)
errors = FormulaValidator().validate(ast)

if errors:
    print("❌ Astrological errors found:")
    for error in errors:
        print(f"  - {error}")
    raise ValueError("Invalid formula")
else:
    print("✅ Formula is astrologically valid")
```

**Вариант B: На уровне выполнения (runtime)**

```python
class Planet:
    def __init__(self, name, ...):
        self.name = name
        self._retrograde = False

    @property
    def Retrograde(self):
        if self.name in ['Sun', 'Moon']:
            raise AttributeError(
                f"{self.name} cannot be retrograde! "
                f"This is an astrological impossibility."
            )
        return self._retrograde

# Использование:
chart = Chart(...)
try:
    result = chart.Sun.Retrograde
except AttributeError as e:
    print(f"❌ {e}")
```

**Вариант C: Гибридный (рекомендуется)**

```python
# 1. Парсер ловит явные ошибки:
"Sun.Retrograde == True"  # → Compile-time error

# 2. Runtime ловит динамические:
formula = f"{planet_name}.Retrograde == True"
# Если planet_name из user input → проверяем при выполнении
```

---

### 🎯 Уровни валидации

**Level 1: Критические ошибки (ДОЛЖНЫ блокировать)**

- ❌ Sun/Moon ретроградны
- ❌ Аспект к самому себе
- ❌ Дом вне диапазона 1-12
- ❌ Градус вне диапазона

**Level 2: Предупреждения (МОЖНО разрешить с warning)**

- ⚠️ Asc.Retrograde (технически бессмысленно, но не сломает программу)
- ⚠️ Слишком большой орбис (>15°)
- ⚠️ Экзотические аспекты (Quintile, Biquintile)

**Level 3: Best practices (ТОЛЬКО для edukации)**

- 💡 Использование устаревших терминов
- 💡 Неоптимальные формулы

---

### 🗣️ Комментарии команды

**Professional Astrologer:**

**"СПАСИБО, что наконец-то спросили! Валидация КРИТИЧНА!"**

**"Астрологи-новички постоянно делают ошибки типа 'ретроградная Луна' или 'Солнце в 15 доме'. Программа ДОЛЖНА их ловить и объяснять!"**

**Список частых ошибок новичков:**

1. "Ретроградное Солнце/Луна" ← САМОЕ ЧАСТОЕ!
2. "Марс в аспекте с Марсом"
3. "Венера в 13 доме"
4. "Солнце в -5 градусах"
5. "Аспект 73 градуса" (не классический)

**Backend Developer:**

**"any() синтаксис - хорошая идея, но нужна четкая грамматика!"**

**Предлагаю:**

```python
# Четкое правило:
any(СПИСОК).СВОЙСТВО ОПЕРАТОР ЗНАЧЕНИЕ  # → property check
any(СПИСОК).МЕТОД(ОБЪЕКТ)                # → aspect/method call

# Примеры:
any([Sun, Moon]).Sign == Aries           # property
any([Mars, Venus]).conj(Saturn)           # method
```

**UX Designer:**

**"Ошибки должны быть ПОНЯТНЫМИ и ОБУЧАЮЩИМИ!"**

```python
# Плохо:
Error: Invalid retrograde check for Sun

# Хорошо:
❌ Астрологическая ошибка: Солнце не может быть ретроградным!

ℹ️  Объяснение:
Ретроградными могут быть только планеты: Меркурий, Венера, Марс,
Юпитер, Сатурн, Уран, Нептун, Плутон.

Солнце и Луна НИКОГДА не бывают ретроградными, так как
мы наблюдаем с Земли, а Земля вращается вокруг Солнца.

💡 Возможно, вы хотели проверить:
  - Mercury.Retrograde == True
  - Venus.Retrograde == True
```

**Regular User:**

**"Ага! Вот почему мой запрос не работал! Валидация нужна!"**

---

### 🎯 Финальная рекомендация (Раунд 7)

**✅ Добавить в v1.0:**

1. **Астрологическую валидацию (критично!)**
   - Sun/Moon не ретроградны
   - Нет аспектов к себе
   - Дома 1-12
   - Понятные сообщения об ошибках

2. **any() синтаксис (опционально)**
   - Если успеем реализовать parse logic
   - Как альтернатива многословным OR
   - С четкой грамматикой

**📝 Примеры с валидацией:**

```python
# Парсер/валидатор ловит:
>>> check("Sun.Retrograde == True")
❌ Астрологическая ошибка: Солнце не может быть ретроградным!
   Только планеты могут быть ретроградными.

>>> check("Asp(Mars, Mars, Conj)")
❌ Ошибка: Планета не может иметь аспект к самой себе!
   Проверьте формулу: Asp(Mars, Mars, Conj)

>>> check("Venus.House == 15")
❌ Ошибка: Номер дома должен быть от 1 до 12, получено: 15

>>> check("Sun.Degree == 35")
❌ Ошибка: Градус в знаке должен быть 0-29°, получено: 35°
   (Если нужен абсолютный градус, используйте Sun.AbsoluteDegree)

# Правильные формулы:
>>> check("Mercury.Retrograde == True")
✅ Формула корректна

>>> check("any([Mercury, Venus, Mars]).Retrograde == True")
✅ Формула корректна (хотя бы одна из планет ретроградна)
```

**Вывод: Астрологическая валидация - ОБЯЗАТЕЛЬНА! `any()` синтаксис - хорошая идея, но требует тщательной проработки грамматики.** ⚠️

---

## � РАУНД 7.1: Расширенная астрологическая валидация

### Критика от User: "Почему астролог молчит про управителей?"

**User справедливо отмечает:**

**"и почему астролог молчит по поводу проверки на управителя? и прочих подобных?"**

**Проблема:** Текущая валидация покрывает только базовые ошибки:

- ✅ Ретроградность (Sun/Moon не могут быть)
- ✅ Самоаспект (Mars к Mars бессмысленен)
- ✅ Диапазон домов (1-12)
- ✅ Диапазон градусов (0-29)

**НО пропущены важные астрологические правила!**

---

### 📚 Астрологические концепции для валидации

**1. Управители (Rulers)**

Каждый знак управляется определенной планетой:

```python
RULERS = {
    'Aries': 'Mars',
    'Taurus': 'Venus',
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': ['Mars', 'Pluto'],      # традиционный + современный
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': ['Saturn', 'Uranus'],  # традиционный + современный
    'Pisces': ['Jupiter', 'Neptune']   # традиционный + современный
}

# Обратная связь (планета → знаки, которыми управляет):
PLANET_RULES = {
    'Sun': ['Leo'],
    'Moon': ['Cancer'],
    'Mercury': ['Gemini', 'Virgo'],
    'Venus': ['Taurus', 'Libra'],
    'Mars': ['Aries', 'Scorpio'],  # + Pluto для Scorpio
    'Jupiter': ['Sagittarius', 'Pisces'],  # + Neptune для Pisces
    'Saturn': ['Capricorn', 'Aquarius'],  # + Uranus для Aquarius
    'Uranus': ['Aquarius'],  # современный
    'Neptune': ['Pisces'],   # современный
    'Pluto': ['Scorpio']     # современный
}
```

**2. Достоинства (Dignities)**

Планета может иметь разные статусы в знаке:

```python
DIGNITIES = {
    'Rulership': {  # Планета в своем доме (сильная позиция)
        'Sun': ['Leo'],
        'Moon': ['Cancer'],
        'Mercury': ['Gemini', 'Virgo'],
        'Venus': ['Taurus', 'Libra'],
        'Mars': ['Aries', 'Scorpio'],
        'Jupiter': ['Sagittarius', 'Pisces'],
        'Saturn': ['Capricorn', 'Aquarius']
    },
    'Exaltation': {  # Экзальтация (возвышение, очень сильна)
        'Sun': 'Aries',      # 19° Aries точная экзальтация
        'Moon': 'Taurus',    # 3° Taurus
        'Mercury': 'Virgo',  # 15° Virgo
        'Venus': 'Pisces',   # 27° Pisces
        'Mars': 'Capricorn', # 28° Capricorn
        'Jupiter': 'Cancer', # 15° Cancer
        'Saturn': 'Libra'    # 21° Libra
    },
    'Detriment': {  # Изгнание (противоположность управлению, слабая)
        'Sun': ['Aquarius'],
        'Moon': ['Capricorn'],
        'Mercury': ['Sagittarius', 'Pisces'],
        'Venus': ['Scorpio', 'Aries'],
        'Mars': ['Libra', 'Taurus'],
        'Jupiter': ['Gemini', 'Virgo'],
        'Saturn': ['Cancer', 'Leo']
    },
    'Fall': {  # Падение (противоположность экзальтации, очень слабая)
        'Sun': 'Libra',      # 19° Libra
        'Moon': 'Scorpio',   # 3° Scorpio
        'Mercury': 'Pisces', # 15° Pisces
        'Venus': 'Virgo',    # 27° Virgo
        'Mars': 'Cancer',    # 28° Cancer
        'Jupiter': 'Capricorn', # 15° Capricorn
        'Saturn': 'Aries'    # 21° Aries
    }
}
```

**3. Рецепция (Reception)**

Взаимная рецепция — когда две планеты в знаках друг друга:

```python
# Пример:
# Mars в Taurus (знак Venus) + Venus в Aries (знак Mars) → mutual reception!
```

---

### ⚠️ Ошибки, которые нужно ловить

**1. Некорректное использование Ruler**

```python
# ОШИБКА: Попытка проверить, управляет ли планета другой планетой
❌ Mars.Ruler == Venus
   # Бессмысленно! Планета не "управляет" другой планетой
   # Планета управляет ЗНАКОМ

# ПРАВИЛЬНО: Проверка управителя знака
✅ Mars.Sign.Ruler == Mars  # Марс в знаке, которым управляет (Aries или Scorpio)

# Или через Dignity:
✅ Mars.Dignity == Rulership  # Марс в достоинстве управления
```

**2. Некорректные комбинации Dignity**

```python
# ОШИБКА: Неправильный знак экзальтации
❌ Sun.Sign == Taurus AND Sun.Dignity == Exaltation
   # Солнце экзальтировано в Овне, НЕ в Тельце!

# ПРАВИЛЬНО:
✅ Sun.Sign == Aries AND Sun.Dignity == Exaltation
✅ Moon.Sign == Taurus AND Moon.Dignity == Exaltation
```

**3. Противоречивые утверждения**

```python
# ОШИБКА: Планета не может быть одновременно в управлении и падении
❌ Mars.Dignity == Rulership AND Mars.Dignity == Fall
   # Логически невозможно!

# ОШИБКА: В одном знаке нельзя быть и в экзальтации, и в изгнании
❌ Sun.Sign == Aries AND Sun.Dignity == Detriment
   # Солнце в Овне экзальтировано, не может быть в изгнании
```

**4. Неверные управители**

```python
# ОШИБКА: Неправильный управитель знака
❌ Aries.Ruler == Venus
   # Овном управляет Марс, НЕ Венера!

# ПРАВИЛЬНО:
✅ Aries.Ruler == Mars
✅ Taurus.Ruler == Venus
```

---

### 🛠️ Реализация расширенной валидации

```python
class ExtendedAstrologicalValidator:
    """Расширенная астрологическая валидация"""

    # Базовые ошибки (из Round 7)
    NON_RETROGRADE_BODIES = {'Sun', 'Moon', 'Asc', 'MC', 'IC', 'Dsc'}
    VALID_HOUSES = range(1, 13)
    VALID_DEGREES_IN_SIGN = range(0, 30)

    # Управители знаков
    SIGN_RULERS = {
        'Aries': ['Mars'],
        'Taurus': ['Venus'],
        'Gemini': ['Mercury'],
        'Cancer': ['Moon'],
        'Leo': ['Sun'],
        'Virgo': ['Mercury'],
        'Libra': ['Venus'],
        'Scorpio': ['Mars', 'Pluto'],
        'Sagittarius': ['Jupiter'],
        'Capricorn': ['Saturn'],
        'Aquarius': ['Saturn', 'Uranus'],
        'Pisces': ['Jupiter', 'Neptune']
    }

    # Экзальтации
    EXALTATIONS = {
        'Sun': 'Aries',
        'Moon': 'Taurus',
        'Mercury': 'Virgo',
        'Venus': 'Pisces',
        'Mars': 'Capricorn',
        'Jupiter': 'Cancer',
        'Saturn': 'Libra'
    }

    # Изгнания (противоположные знаки управлению)
    DETRIMENTS = {
        'Sun': ['Aquarius'],
        'Moon': ['Capricorn'],
        'Mercury': ['Sagittarius', 'Pisces'],
        'Venus': ['Scorpio', 'Aries'],
        'Mars': ['Libra', 'Taurus'],
        'Jupiter': ['Gemini', 'Virgo'],
        'Saturn': ['Cancer', 'Leo']
    }

    # Падения (противоположные знаки экзальтации)
    FALLS = {
        'Sun': 'Libra',
        'Moon': 'Scorpio',
        'Mercury': 'Pisces',
        'Venus': 'Virgo',
        'Mars': 'Cancer',
        'Jupiter': 'Capricorn',
        'Saturn': 'Aries'
    }

    def validate(self, ast):
        """Валидация AST-дерева формулы"""

        # 1. Базовые проверки (из Round 7)
        self._check_retrograde(ast)
        self._check_self_aspect(ast)
        self._check_house_range(ast)
        self._check_degree_range(ast)

        # 2. НОВЫЕ проверки достоинств
        self._check_ruler_usage(ast)
        self._check_dignity_combinations(ast)
        self._check_exaltation_correctness(ast)
        self._check_conflicting_dignities(ast)

    def _check_ruler_usage(self, ast):
        """Проверка корректности использования Ruler"""

        # Ошибка: Planet.Ruler == OtherPlanet (бессмысленно!)
        if (ast.type == 'BinaryOp' and
            ast.left.property == 'Ruler' and
            ast.left.object in PLANETS and
            ast.right in PLANETS):

            raise ValidationError(
                f"❌ Ошибка: {ast.left.object}.Ruler == {ast.right} бессмысленна!\n\n"
                f"ℹ️  Объяснение:\n"
                f"Планета не 'управляет' другой планетой.\n"
                f"Планета управляет ЗНАКОМ (или находится в знаке, которым управляет).\n\n"
                f"💡 Возможно, вы хотели проверить:\n"
                f"  - {ast.left.object}.Dignity == Rulership  # Планета в своем доме\n"
                f"  - {ast.left.object}.Sign.Ruler == {ast.left.object}  # Планета управляет знаком, в котором находится"
            )

    def _check_dignity_combinations(self, ast):
        """Проверка корректности комбинаций планета+знак+достоинство"""

        # Пример: Sun.Sign == Taurus AND Sun.Dignity == Exaltation
        if self._is_dignity_check(ast):
            planet = ast.planet
            sign = ast.sign
            dignity = ast.dignity

            # Проверяем соответствие
            if dignity == 'Exaltation':
                correct_sign = self.EXALTATIONS.get(planet)
                if sign != correct_sign:
                    raise ValidationError(
                        f"❌ Астрологическая ошибка: {planet} экзальтировано в {correct_sign}, НЕ в {sign}!\n\n"
                        f"ℹ️  Экзальтации планет:\n"
                        f"   Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces\n"
                        f"   Mars: Capricorn, Jupiter: Cancer, Saturn: Libra\n\n"
                        f"💡 Правильная формула:\n"
                        f"  {planet}.Sign == {correct_sign} AND {planet}.Dignity == Exaltation"
                    )

            elif dignity == 'Rulership':
                correct_signs = self.SIGN_RULERS.get(sign, [])
                if planet not in self._get_rulers_for_sign(sign):
                    rulers_str = ' или '.join(self._get_rulers_for_sign(sign))
                    raise ValidationError(
                        f"❌ Астрологическая ошибка: {sign} управляется {rulers_str}, НЕ {planet}!\n\n"
                        f"ℹ️  Управители знаков:\n"
                        f"   Aries→Mars, Taurus→Venus, Gemini→Mercury, Cancer→Moon\n"
                        f"   Leo→Sun, Virgo→Mercury, Libra→Venus, Scorpio→Mars/Pluto\n\n"
                        f"💡 Возможно, вы имели в виду:\n"
                        f"  {planet}.Dignity == Rulership  # Проверить, что {planet} в своем доме"
                    )

            # Аналогично для Detriment и Fall...

    def _check_exaltation_correctness(self, ast):
        """Проверка правильности экзальтаций"""

        # Если указана экзальтация, проверяем соответствие планеты и знака
        pass  # Реализация выше в _check_dignity_combinations

    def _check_conflicting_dignities(self, ast):
        """Проверка конфликтующих достоинств"""

        # Пример: Mars.Dignity == Rulership AND Mars.Dignity == Fall
        # Невозможно одновременно!

        if self._has_conflicting_dignities(ast):
            raise ValidationError(
                f"❌ Логическая ошибка: Планета не может быть одновременно в разных достоинствах!\n\n"
                f"ℹ️  Объяснение:\n"
                f"В одном знаке планета имеет только ОДНО состояние:\n"
                f"  - Rulership (управление)\n"
                f"  - Exaltation (экзальтация)\n"
                f"  - Detriment (изгнание)\n"
                f"  - Fall (падение)\n"
                f"  - или нейтральное положение (ничего из вышеперечисленного)\n\n"
                f"💡 Используйте OR для проверки нескольких вариантов:\n"
                f"  Mars.Dignity == Rulership OR Mars.Dignity == Exaltation"
            )

    def _get_rulers_for_sign(self, sign):
        """Получить управителей знака"""
        return self.SIGN_RULERS.get(sign, [])

    def _is_dignity_check(self, ast):
        """Проверить, является ли это проверкой достоинства"""
        # Упрощенная проверка, в реальности нужен анализ AST
        return hasattr(ast, 'dignity') and ast.dignity in ['Rulership', 'Exaltation', 'Detriment', 'Fall']

    def _has_conflicting_dignities(self, ast):
        """Проверить наличие конфликтующих достоинств в одной формуле"""
        # Нужно проанализировать AST на наличие AND между разными Dignity для одной планеты
        return False  # Упрощенная заглушка
```

---

### 📝 Примеры ошибок и правильных формул

**Ошибка 1: Неправильный управитель**

```python
>>> check("Mars.Ruler == Venus")
❌ Ошибка: Mars.Ruler == Venus бессмысленна!

ℹ️  Объяснение:
Планета не 'управляет' другой планетой.
Планета управляет ЗНАКОМ (или находится в знаке, которым управляет).

💡 Возможно, вы хотели проверить:
  - Mars.Dignity == Rulership  # Марс в своем доме
  - Mars.Sign.Ruler == Mars  # Марс управляет своим знаком
```

**Ошибка 2: Неправильная экзальтация**

```python
>>> check("Sun.Sign == Taurus AND Sun.Dignity == Exaltation")
❌ Астрологическая ошибка: Sun экзальтировано в Aries, НЕ в Taurus!

ℹ️  Экзальтации планет:
   Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces
   Mars: Capricorn, Jupiter: Cancer, Saturn: Libra

💡 Правильная формула:
  Sun.Sign == Aries AND Sun.Dignity == Exaltation
```

**Ошибка 3: Конфликтующие достоинства**

```python
>>> check("Mars.Dignity == Rulership AND Mars.Dignity == Fall")
❌ Логическая ошибка: Планета не может быть одновременно в разных достоинствах!

ℹ️  Объяснение:
В одном знаке планета имеет только ОДНО состояние:
  - Rulership (управление)
  - Exaltation (экзальтация)
  - Detriment (изгнание)
  - Fall (падение)
  - или нейтральное положение

💡 Используйте OR для проверки нескольких вариантов:
  Mars.Dignity == Rulership OR Mars.Dignity == Exaltation
```

**Правильные формулы:**

```python
# Проверка, что планета в своем доме (управление)
✅ Mars.Dignity == Rulership
✅ Mars.Sign == Aries AND Mars.Dignity == Rulership

# Проверка экзальтации
✅ Sun.Dignity == Exaltation
✅ Sun.Sign == Aries AND Sun.Dignity == Exaltation

# Проверка слабых позиций
✅ Mars.Dignity == Detriment  # Марс в изгнании
✅ Saturn.Dignity == Fall  # Сатурн в падении

# Проверка взаимной рецепции
✅ (Mars.Sign == Taurus AND Venus.Sign == Aries)  # Mutual reception!

# Проверка, что управитель знака аспектирует планету в этом знаке
✅ Sun.Sign == Aries AND Asp(Sun, Mars, Trine)  # Солнце в Овне (управитель Марс) + трин к Марсу
```

---

### 🗣️ Комментарии команды (обновленные)

**Professional Astrologer:**

**"ДА! НАКОНЕЦ-ТО! Это я и имел в виду!"**

**"Проверка управителей и достоинств - это ОСНОВЫ астрологии! Без этого валидация неполная!"**

**Дополнительные важные проверки:**

1. **Взаимная рецепция** - когда планеты в знаках друг друга:

   ```python
   Mars.Sign == Taurus AND Venus.Sign == Aries  # Взаимная рецепция!
   ```

2. **Антис и контр-антис** (advanced):

   ```python
   # Symmetry points по оси 0° Cancer-Capricorn
   # Пока отложим на v2.0
   ```

3. **Almuten** - сильнейшая планета по достоинствам:

   ```python
   # Расчет баллов Essential Dignities
   # Тоже v2.0
   ```

4. **Peregrinus** - планета без достоинств:
   ```python
   Planet.Dignity == None  # Или Peregrine
   ```

**Backend Developer:**

**"Хорошо! Но таблицы управителей/экзальтаций нужно вынести в конфигурационные файлы!"**

**Предложение:**

```python
# config/dignities.yaml
rulers:
  Aries: [Mars]
  Taurus: [Venus]
  Scorpio: [Mars, Pluto]  # traditional + modern
  # ...

exaltations:
  Sun: Aries
  Moon: Taurus
  # ...
```

**UX Designer:**

**"Сообщения об ошибках стали еще лучше! Астрологу сразу понятно, что не так!"**

**Regular User:**

**"Вау! Теперь программа знает астрологию лучше меня! 😅"**

---

### 🎯 Финальная рекомендация (Раунд 7.1)

**✅ ОБЯЗАТЕЛЬНО добавить в v1.0:**

1. **Расширенная валидация достоинств:**
   - ✅ Проверка управителей (Ruler)
   - ✅ Проверка экзальтаций (Exaltation)
   - ✅ Проверка изгнаний (Detriment)
   - ✅ Проверка падений (Fall)
   - ✅ Проверка конфликтующих достоинств
   - ✅ Понятные образовательные сообщения

2. **Конфигурационные файлы для астрологических правил:**
   - dignities.yaml (управители, экзальтации, изгнания, падения)
   - aspects.yaml (орбы, типы аспектов)
   - Возможность кастомизации (традиционная vs современная астрология)

**📋 Обновленный список проверок валидатора:**

**Уровень 1: Критические ошибки (БЛОКИРУЮТ выполнение)**

1. ✅ Sun/Moon ретроградны (невозможно физически)
2. ✅ Самоаспект (Mars к Mars)
3. ✅ Дом вне диапазона 1-12
4. ✅ Градус вне диапазона 0-29
5. ✅ **Неправильный управитель (NEW!)**
6. ✅ **Неправильная экзальтация (NEW!)**
7. ✅ **Конфликтующие достоинства (NEW!)**

**Уровень 2: Предупреждения (выполнение возможно, но сомнительно)**

1. ⚠️ Asc/MC ретроградны (технически невозможно)
2. ⚠️ Большой орб аспекта (>10°)
3. ⚠️ Необычная комбинация (например, Pluto в аспекте к Asc - редко используется)
4. ⚠️ **Планета в изгнании или падении (NEW!)** - не ошибка, но астролог должен знать

**Уровень 3: Рекомендации (best practices)**

1. 💡 Использование устаревших названий (Node вместо NorthNode)
2. 💡 Можно упростить формулу (предложить aggregators)
3. 💡 **Взаимная рецепция обнаружена (NEW!)** - полезная информация для астролога

**Вывод: Расширенная валидация делает DSL ПРОФЕССИОНАЛЬНЫМ инструментом для астрологов!** 🌟

### 🧪 Пометки на тестирование и оптимизацию (v1.0.0):

**1. Unit-тесты для валидации достоинств (приоритет: ВЫСОКИЙ)** ⚠️

```python
# tests/test_dignity_validation.py

class TestRulerValidation:
    def test_invalid_planet_ruler_planet():
        """Mars.Ruler == Venus должно выдать ошибку"""
        assert raises(ValidationError, "Mars.Ruler == Venus")

    def test_valid_dignity_check():
        """Mars.Dignity == Rulership - валидная формула"""
        assert validate("Mars.Dignity == Rulership") == True

class TestExaltationValidation:
    def test_wrong_exaltation_sign():
        """Sun в Taurus не может быть в экзальтации"""
        assert raises(ValidationError,
                     "Sun.Sign == Taurus AND Sun.Dignity == Exaltation")

    def test_correct_exaltation():
        """Sun в Aries может быть в экзальтации"""
        assert validate("Sun.Sign == Aries AND Sun.Dignity == Exaltation") == True

class TestConflictingDignities:
    def test_rulership_and_fall_conflict():
        """Планета не может быть одновременно в управлении и падении"""
        assert raises(ValidationError,
                     "Mars.Dignity == Rulership AND Mars.Dignity == Fall")

# ⚠️ TODO: Добавить 30+ тест-кейсов для всех комбинаций планет/знаков
# ⚠️ TODO: Edge cases (внешние планеты, Chiron, Lilith)
# ⚠️ TODO: Тестирование локализации ошибок (RU/EN)
```

**2. Оптимизация таблиц поиска (приоритет: СРЕДНИЙ)** ⚡

```python
# До оптимизации: O(n) поиск в списках
RULERS = {
    'Aries': ['Mars'],
    'Scorpio': ['Mars', 'Pluto'],
    # ...
}

# После оптимизации: O(1) хэш-таблицы для обратного поиска
PLANET_RULES_SIGNS = {
    'Mars': {'Aries', 'Scorpio'},
    'Pluto': {'Scorpio'},
    'Venus': {'Taurus', 'Libra'},
    # ... hash для O(1) проверки
}

EXALTATION_LOOKUP = {
    ('Sun', 'Aries'): True,
    ('Moon', 'Taurus'): True,
    ('Mercury', 'Virgo'): True,
    # ... hash для O(1) проверки
}

# ⚡ TODO: Benchmark before/after (ожидаем 10x speedup)
# ⚡ TODO: Профилирование с cProfile для поиска узких мест
```

**3. Конфигурационные файлы (приоритет: ВЫСОКИЙ)** 📋

```yaml
# config/dignities.yaml

# Режим астрологии (выбирается пользователем)
mode: modern # или traditional

traditional: # Традиционная астрология (7 планет)
  rulers:
    Aries: [Mars]
    Taurus: [Venus]
    Gemini: [Mercury]
    Cancer: [Moon]
    Leo: [Sun]
    Virgo: [Mercury]
    Libra: [Venus]
    Scorpio: [Mars] # Только традиционный управитель
    Sagittarius: [Jupiter]
    Capricorn: [Saturn]
    Aquarius: [Saturn] # Только традиционный управитель
    Pisces: [Jupiter] # Только традиционный управитель

modern: # Современная астрология (10 планет)
  rulers:
    Aries: [Mars]
    # ... (те же, что traditional, плюс:)
    Scorpio: [Mars, Pluto]
    Aquarius: [Saturn, Uranus]
    Pisces: [Jupiter, Neptune]

exaltations: # Едины для обеих систем
  Sun: { sign: Aries, degree: 19 }
  Moon: { sign: Taurus, degree: 3 }
  Mercury: { sign: Virgo, degree: 15 }
  Venus: { sign: Pisces, degree: 27 }
  Mars: { sign: Capricorn, degree: 28 }
  Jupiter: { sign: Cancer, degree: 15 }
  Saturn: { sign: Libra, degree: 21 }

# ⚠️ TODO: YAML loader + validator
# ⚠️ TODO: Настройка через CLI: --astro-mode=traditional/modern
# ⚠️ TODO: Поддержка кастомных YAML (для редких школ астрологии)
```

**4. Качество сообщений об ошибках (приоритет: СРЕДНИЙ)** 💬

```python
# ⚠️ TODO: A/B тестирование с реальными астрологами:
#
# Версия A (краткая):
# ❌ Ошибка: Sun не может быть в экзальтации в Taurus
#
# Версия B (обучающая):
# ❌ Астрологическая ошибка: Sun экзальтировано в Aries, НЕ в Taurus!
#
# ℹ️  Экзальтации планет:
#    Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces
#    Mars: Capricorn, Jupiter: Cancer, Saturn: Libra
#
# 💡 Правильная формула:
#   Sun.Sign == Aries AND Sun.Dignity == Exaltation
#
# Метрика: Понятность ошибки (опрос, шкала 1-5 звезд)

# ⚠️ TODO: Локализация (RU/EN)
# ⚠️ TODO: Режим verbosity (--verbose для обучающих, --quiet для кратких)
```

**5. Performance бенчмарки (приоритет: НИЗКИЙ)** 📊

```python
# ⚠️ TODO: Измерить время валидации:
#
# Целевые метрики:
# - Простая формула (1 проверка): < 1ms
# - Сложная с 10+ проверками: < 10ms
# - Формула с агрегаторами: < 50ms
# - Батч из 100 формул: < 500ms
#
# Инструменты:
# - pytest-benchmark для регрессий
# - memory_profiler для утечек памяти
# - Continuous benchmarking в CI/CD

# Acceptance criteria:
# - 99th percentile latency < 100ms
# - Memory usage < 50MB для валидатора
```

**6. Integration тесты (приоритет: ВЫСОКИЙ)** 🔗

```python
# tests/test_integration_validation.py

def test_full_validation_pipeline():
    """Полный цикл: parse → validate → execute"""

    # Валидная формула
    result = parse_and_validate(
        "Sun.Sign == Aries AND Sun.Dignity == Exaltation"
    )
    assert result.is_valid == True

    # Невалидная формула (неправильная экзальтация)
    with pytest.raises(ValidationError) as exc:
        parse_and_validate(
            "Sun.Sign == Taurus AND Sun.Dignity == Exaltation"
        )
    assert "Sun экзальтировано в Aries" in str(exc.value)

    # Валидация + выполнение на реальной карте
    chart = calculate_chart("1982-01-08", "13:40", "Саратов")
    result = execute_formula(chart, "Sun.Dignity == Exaltation")
    # Sun в Capricorn (нейтральное положение) → False

# ⚠️ TODO: 20+ integration тестов для всех комбинаций
# ⚠️ TODO: Тестирование на реальных картах (dataset из 100+ карт)
```

**Итоговый чек-лист для v1.0.0:** ✅

- [ ] **Высокий приоритет:**
  - [ ] 30+ unit-тестов для валидации достоинств
  - [ ] Конфигурационные YAML файлы (traditional/modern)
  - [ ] 20+ integration тестов
  - [ ] Локализация сообщений (RU/EN)

- [ ] **Средний приоритет:**
  - [ ] Оптимизация таблиц поиска (O(1))
  - [ ] A/B тестирование сообщений об ошибках
  - [ ] Benchmark regression тесты

- [ ] **Низкий приоритет:**
  - [ ] Performance profiling
  - [ ] Memory leak detection
  - [ ] Continuous benchmarking

**Deadline:** Все "высокий приоритет" → перед релизом v1.0.0

---

## �💡 РАУНД 8: Агрегаторы (planet/planets, aspect/aspects)

### Предложение: Использовать агрегаторы вместо явных списков

**User предлагает:**

**"`any(planet).sign == Leo` - разве не проще, чем перечислять все планеты?"**

---

### Концепция агрегаторов

**Идея: Ключевые слова для обозначения "всех объектов типа"**

```python
# Агрегаторы (единственное число = любой объект типа):
planet   # любая планета (Sun, Moon, Mercury, ..., Pluto)
aspect   # любой аспект в карте
house    # любой дом (1-12)
sign     # любой знак (Aries, Taurus, ...)

# Агрегаторы (множественное число = все объекты типа):
planets  # все планеты
aspects  # все аспекты
houses   # все дома
signs    # все знаки
```

---

### 📝 Сравнение синтаксисов

**Задача 1: "Есть ли хотя бы одна планета в Льве?"**

```python
# Старый синтаксис (явный список):
Sun.Sign == Leo OR Moon.Sign == Leo OR Mercury.Sign == Leo OR ... (10+ планет!)

# С any() и списком:
any([Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto]).Sign == Leo

# С агрегатором (НОВОЕ):
any(planet).Sign == Leo  # ✨ ПРОЩЕ!
```

**Задача 2: "Все планеты в огненных знаках?"**

```python
# Старый:
Sun.Sign IN Fire AND Moon.Sign IN Fire AND Mercury.Sign IN Fire AND ...

# С all() и списком:
all([Sun, Moon, Mercury, ...]).Sign IN Fire

# С агрегатором (НОВОЕ):
all(planets).Sign IN Fire  # ✨ ПРОЩЕ!
```

**Задача 3: "Есть ли планета в 10 доме?"**

```python
# Старый:
Sun.House == 10 OR Moon.House == 10 OR Mercury.House == 10 OR ...

# С any() и списком:
any([Sun, Moon, Mercury, ...]).House == 10

# С агрегатором (НОВОЕ):
any(planet).House == 10  # ✨ ПРОЩЕ!
```

**Задача 4: "Есть ли квадрат в карте?"**

```python
# Старый (очень сложно):
Asp(Sun, Moon, Square) OR Asp(Sun, Mercury, Square) OR ...  # сотни комбинаций!

# С агрегатором (НОВОЕ):
any(aspect).Type == Square  # ✨ НАМНОГО ПРОЩЕ!
```

---

### 🔍 Детальная спецификация агрегаторов

#### 1. Агрегатор `planet` / `planets`

**`planet` (единственное число) = любая одна планета**

```python
# Определение:
planet ∈ {Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto}

# Примеры:
any(planet).Sign == Leo           # Есть ли планета в Льве?
any(planet).House == 10           # Есть ли планета в 10 доме?
any(planet).Retrograde == True    # Есть ли ретроградная планета?
count(planet, Sign == Leo) >= 3   # Сколько планет в Льве?
```

**`planets` (множественное число) = все планеты**

```python
# Примеры:
all(planets).Sign IN Fire         # ВСЕ планеты в огне?
count(planets, Retrograde) == 0   # НЕТ ретроградных планет?
any(planets).Dignity == Exaltation  # Есть ли планета в экзальтации?
```

**Вопрос: Что включать в `planet`/`planets`?**

```python
# Вариант A: Только классические планеты (10 штук)
planet = {Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto}

# Вариант B: + фиктивные точки
planet = {...классические..., NorthNode, SouthNode, Chiron, Lilith}

# Вариант C: + углы
planet = {...все..., Asc, MC, IC, Dsc}

# Рекомендация: Вариант A (классические), остальное через отдельные агрегаторы
```

#### 2. Агрегатор `aspect` / `aspects`

**`aspect` = любой аспект в карте**

```python
# Примеры:
any(aspect).Type == Square        # Есть ли квадрат?
any(aspect).Orb < 1               # Есть ли точный аспект (орб <1°)?
count(aspect, Type == Trine) >= 3 # Есть ли 3+ трина?

# Фильтрация аспектов:
any(aspect WHERE Planet1 == Mars).Type == Conj  # Есть ли соединение с Марсом?
```

**Структура aspect:**

```python
aspect = {
    'Planet1': Mars,
    'Planet2': Saturn,
    'Type': Square,
    'Orb': 2.5,
    'Applying': True  # аппликация
}
```

#### 3. Агрегатор `house` / `houses`

**`house` = любой дом (1-12)**

```python
# Примеры:
any(house).PlanetsCount >= 3      # Есть ли стеллиум (3+ планеты в доме)?
any(house).Ruler.Retrograde       # Есть ли дом с ретроградным управителем?

# Особые дома:
any(house IN [1,4,7,10]).PlanetsCount > 0  # Есть планеты в угловых домах?
```

#### 4. Агрегатор `sign` / `signs`

**`sign` = любой знак**

```python
# Примеры:
any(sign).PlanetsCount >= 4       # Есть стеллиум в знаке (4+ планеты)?
count(sign, PlanetsCount > 0)     # В скольких знаках есть планеты?

# Фильтрация по элементу:
any(sign IN Fire).PlanetsCount >= 3  # Много ли планет в огне?
```

---

### 🎯 Синтаксис с фильтрами (WHERE)

**Расширенная фильтрация:**

```python
# Базовый синтаксис:
any(АГРЕГАТОР).СВОЙСТВО ОПЕРАТОР ЗНАЧЕНИЕ

# С фильтром WHERE:
any(АГРЕГАТОР WHERE УСЛОВИЕ).СВОЙСТВО ОПЕРАТОР ЗНАЧЕНИЕ

# Примеры:

# Есть ли ретроградная планета в огненном знаке?
any(planet WHERE Sign IN Fire).Retrograde == True

# Есть ли квадрат с участием Марса?
any(aspect WHERE Planet1 == Mars OR Planet2 == Mars).Type == Square

# Есть ли точный (орб <1°) трин?
any(aspect WHERE Type == Trine).Orb < 1

# Есть ли угловой дом (1,4,7,10) с 3+ планетами?
any(house WHERE Number IN [1,4,7,10]).PlanetsCount >= 3

# Сколько планет в мутабельных знаках?
count(planet WHERE Sign IN Mutable)
```

---

### 📊 Сравнительная таблица

| Задача                  | Без агрегаторов                                              | С агрегаторами                         | Экономия |
| ----------------------- | ------------------------------------------------------------ | -------------------------------------- | -------- |
| **Планета в Льве**      | `Sun.Sign == Leo OR Moon.Sign == Leo OR ...` (100+ символов) | `any(planet).Sign == Leo` (24 символа) | **-76%** |
| **Все планеты в огне**  | `Sun.Sign IN Fire AND Moon.Sign IN Fire AND ...`             | `all(planets).Sign IN Fire`            | **-80%** |
| **Есть квадрат?**       | `Asp(Sun,Moon,Sq) OR Asp(Sun,Merc,Sq) OR ...` (сотни!)       | `any(aspect).Type == Square`           | **-95%** |
| **Планета в 10 доме**   | `Sun.House == 10 OR Moon.House == 10 OR ...`                 | `any(planet).House == 10`              | **-75%** |
| **Ретроградных планет** | `count([Merc,Venus,Mars,...], Retro)`                        | `count(planet, Retrograde)`            | **-60%** |

**Вывод: Агрегаторы экономят 60-95% кода!** 🚀

---

### 🤔 Плюсы и минусы

**✅ Плюсы агрегаторов:**

1. **Компактность** - в 5-10 раз короче кода
2. **Читабельность** - `any(planet).Sign == Leo` понятнее
3. **Не нужно помнить все планеты** - агрегатор знает сам
4. **Легко для новичков** - не нужно знать список планет
5. **Универсальность** - работает для любого количества планет
6. **Масштабируемость** - если добавим новые планеты, код не сломается

**⚠️ Минусы:**

1. **Неоднозначность** - что включено в `planet`?
   - Только классические 10?
   - - фиктивные точки?
   - - углы?

2. **Производительность** - нужно итерировать по всем планетам

   ```python
   # Компилятор может оптимизировать:
   any(planet).Sign == Leo
   # → раскрыть в OR:
   # → Sun.Sign == Leo OR Moon.Sign == Leo OR ...
   ```

3. **Конфликт с переменными** - `planet` это ключевое слово или переменная?

   ```python
   # Ключевое слово:
   any(planet).Sign == Leo

   # Или переменная?
   planet = Mars
   planet.Sign == Aries  # КОНФЛИКТ!
   ```

4. **Документация** - нужно четко описать, что входит в каждый агрегатор

---

### 🎨 UX Designer комментирует:

**"Агрегаторы - ОТЛИЧНАЯ идея для новичков!"**

**Сценарии использования:**

**Новичок:**

```python
# Простой вопрос: "Есть ли планета в Льве?"
>>> any(planet).Sign == Leo
True

# "Сколько планет ретроградных?"
>>> count(planet, Retrograde == True)
3
```

**Продвинутый:**

```python
# Сложный запрос: "Есть ли квадрат с участием Марса к планете в 10 доме?"
>>> any(aspect WHERE (Planet1 == Mars OR Planet2 == Mars)
                  AND Type == Square).OtherPlanet.House == 10
True
```

---

### 🔧 Backend Developer реализация:

```python
# Агрегаторы как предопределенные константы
AGGREGATORS = {
    'planet': ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
               'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'],
    'planets': ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'],
    'aspect': lambda chart: chart.aspects,  # все аспекты из карты
    'aspects': lambda chart: chart.aspects,
    'house': range(1, 13),
    'houses': range(1, 13),
}

# Парсинг:
def parse_aggregator(expr):
    """
    any(planet).Sign == Leo
    ↓
    Sun.Sign == Leo OR Moon.Sign == Leo OR Mercury.Sign == Leo OR ...
    """
    if expr.aggregator == 'planet':
        conditions = []
        for p in AGGREGATORS['planet']:
            conditions.append(f"{p}.{expr.property} {expr.operator} {expr.value}")
        return " OR ".join(conditions)

# Компиляция с оптимизацией:
def compile_formula(formula: str) -> callable:
    ast = parse(formula)

    # Оптимизация: раскрыть агрегаторы на этапе компиляции
    if ast.type == 'any_aggregator':
        # any(planet).Sign == Leo
        # → замена на явную проверку
        def check(chart):
            for planet_name in AGGREGATORS['planet']:
                planet = getattr(chart, planet_name)
                if planet.Sign == ast.value:
                    return True
            return False
        return check
```

---

### 💡 Professional Astrologer поддерживает:

**"Агрегаторы - именно то, что нужно астрологам!"**

**Типичные вопросы клиентов:**

1. ❓ "Есть ли у меня планеты в Водолее?"
   → `any(planet).Sign == Aquarius`

2. ❓ "Сколько у меня ретроградных планет?"
   → `count(planet, Retrograde == True)`

3. ❓ "Есть ли у меня квадраты?"
   → `any(aspect).Type == Square`

4. ❓ "Есть ли планеты в 7 доме (дом партнерства)?"
   → `any(planet).House == 7`

5. ❓ "Есть ли у меня стеллиум?"
   → `any(sign).PlanetsCount >= 4` или `any(house).PlanetsCount >= 3`

**"ВСЕ эти вопросы проще с агрегаторами!"**

---

### 🎯 Финальная рекомендация (Раунд 8)

**✅ ОДНОЗНАЧНО добавить в v1.0:**

1. **Агрегаторы `planet` / `planets`**

   ```python
   any(planet).Sign == Leo
   all(planets).Sign IN Fire
   count(planet, Retrograde == True)
   ```

2. **Агрегатор `aspect` / `aspects`**

   ```python
   any(aspect).Type == Square
   count(aspect, Type == Trine) >= 3
   ```

3. **Агрегаторы `house` / `houses`, `sign` / `signs` (опционально)**
   ```python
   any(house).PlanetsCount >= 3  # стеллиум в доме
   any(sign).PlanetsCount >= 4   # стеллиум в знаке
   ```

**📋 Определения:**

```python
# v1.0 (минимум):
planet/planets = [Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto]

# v1.5 (расширенный):
planet/planets = [...классические... + NorthNode, SouthNode, Chiron]

# v2.0 (полный):
planet/planets + points = [...все... + Lilith, Vertex, PartOfFortune]
angles = [Asc, MC, IC, Dsc]
luminaries = [Sun, Moon]
malefics = [Mars, Saturn]
benefics = [Jupiter, Venus]
```

**⚙️ Синтаксис:**

```python
# Базовый:
any(АГРЕГАТОР).СВОЙСТВО ОПЕРАТОР ЗНАЧЕНИЕ
all(АГРЕГАТОР).СВОЙСТВО ОПЕРАТОР ЗНАЧЕНИЕ
count(АГРЕГАТОР, УСЛОВИЕ)

# С фильтром (v2.0):
any(АГРЕГАТОР WHERE УСЛОВИЕ).СВОЙСТВО
```

**📊 Примеры:**

```python
# Простые:
any(planet).Sign == Leo
any(planet).House == 10
any(aspect).Type == Square

# Сложные:
count(planet, Sign IN Fire) >= 3
all(planets WHERE Retrograde == False).Speed > 0
any(aspect WHERE Type IN [Square, Opp]).Orb < 2

# Комбинированные:
(any(planet).Sign == Aries AND any(planet).House == 1) OR
(count(planet, Sign IN Fire) >= 4)
```

**Вывод: Агрегаторы - ОБЯЗАТЕЛЬНО для v1.0! Делают DSL в 5-10 раз компактнее и понятнее.** ✨

---

### 📋 Documentation needed:
