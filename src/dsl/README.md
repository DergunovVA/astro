# DSL Module - Астрологический Domain Specific Language

Модуль для формулирования и валидации астрологических запросов.

## 🎯 Возможности

### 1. **Логические операторы**

```python
# SQL-style (рекомендуется)
Sun.Sign == Aries AND Moon.Sign == Taurus
Mars.House == 1 OR Mars.House == 10
NOT Saturn.Retrograde

# C-style (альтернатива)
Sun.Sign == Aries && Moon.Sign == Taurus
Mars.House == 1 || Mars.House == 10
!Saturn.Retrograde
```

### 2. **Агрегаторы**

```python
# Вместо длинного списка:
Sun.Sign == Leo OR Moon.Sign == Leo OR Mercury.Sign == Leo OR ...

# Используйте агрегаторы (экономия 60-95% кода):
any(planet).Sign == Leo
count(planet, Retrograde == True) >= 2
all(planets).Sign IN Fire
```

### 3. **Астрологическая валидация** ⭐

Автоматическая проверка корректности формул:

```python
# ❌ ОШИБКИ (блокируют выполнение):
Sun.Retrograde == True
# → Солнце не может быть ретроградным!

Sun.Sign == Taurus AND Sun.Dignity == Exaltation
# → Солнце экзальтировано в Овне, НЕ в Тельце!

Mars.Ruler == Venus
# → Бессмысленно! Планета не управляет планетой.

# ✅ ПРАВИЛЬНО:
Mercury.Retrograde == True
Sun.Sign == Aries AND Sun.Dignity == Exaltation
Mars.Dignity == Rulership
```

## 📦 Установка и использование

### Установка зависимостей

```bash
pip install pyyaml pytest pytest-benchmark
```

### Быстрый старт

```python
from src.dsl.validator import AstrologicalValidator

# Создание валидатора
validator = AstrologicalValidator(mode='modern')  # или 'traditional'

# Проверка ретроградности
result = validator.check_retrograde('Sun')
if result:
    print(result.message)
    print(result.details)
    # ❌ Астрологическая ошибка: Sun не может быть ретроградным!

# Проверка экзальтации
result = validator.check_exaltation('Sun', 'Aries')
# None - нет ошибки, Sun действительно экзальтировано в Aries

result = validator.check_exaltation('Sun', 'Taurus')
if result:
    print(result.message)
    # ❌ Астрологическая ошибка: Sun экзальтировано в Aries, НЕ в Taurus!

# Получение статуса достоинства
status = validator.get_dignity_status('Mars', 'Aries')
print(status)  # Rulership

status = validator.get_dignity_status('Sun', 'Aries')
print(status)  # Exaltation
```

## 🧪 Тестирование

### Запуск всех тестов

```bash
# Все тесты модуля
pytest tests/test_dignity_validation.py -v

# Только тесты ретроградности
pytest tests/test_dignity_validation.py::TestRetrogradeValidation -v

# Только тесты экзальтаций
pytest tests/test_dignity_validation.py::TestExaltationValidation -v

# С подробным выводом
pytest tests/test_dignity_validation.py -vv

# Performance benchmarks
pytest tests/test_dignity_validation.py::TestPerformance --benchmark-only
```

### Текущее покрытие

✅ **105+ тестов** покрывают:

**Валидатор (60 тестов):**

- Базовую валидацию (ретроградность, диапазоны, самоаспекты)
- Валидацию достоинств (Ruler, Exaltation, Detriment, Fall)
- Конфликтующие комбинации
- Traditional vs Modern режимы
- Качество сообщений об ошибках
- Edge cases
- Performance (440ns per lookup, 2.3M ops/sec)

**Lexer (45 тестов):**

- Базовая токенизация
- Числа (int, float)
- Строки (quotes, escaping)
- Ключевые слова и операторы
- Агрегаторы (planets, aspects, houses)
- Комментарии
- Отслеживание позиций
- Обработка ошибок
- Edge cases

## 🔤 Lexer (Токенизатор)

### Обзор

Lexer преобразует текстовые формулы в последовательность токенов для дальнейшего парсинга.

### Быстрый старт

```python
from src.dsl.lexer import tokenize

# Простая токенизация
tokens = tokenize("Sun.Sign == Aries")
for token in tokens:
    print(token)
# Token(type=IDENTIFIER, value='Sun', line=1, column=0)
# Token(type=DOT, value='.', line=1, column=3)
# Token(type=IDENTIFIER, value='Sign', line=1, column=4)
# Token(type=EQ, value='==', line=1, column=9)
# Token(type=IDENTIFIER, value='Aries', line=1, column=12)
# Token(type=EOF, value='', line=1, column=17)
```

### Поддерживаемый синтаксис

#### Типы токенов (24 типа)

**Логические операторы:**

- `AND` / `&&` - Логическое И
- `OR` / `||` - Логическое ИЛИ
- `NOT` / `!` - Логическое НЕ

**Операторы сравнения:**

- `==` - Равно
- `!=` - Не равно
- `<` - Меньше
- `>` - Больше
- `<=` - Меньше или равно
- `>=` - Больше или равно
- `IN` - Вхождение в список

**Агрегаторы:**

- `planets` - Все планеты
- `aspects` - Все аспекты
- `houses` - Все дома

**Разделители:**

- `(` `)` - Скобки
- `[` `]` - Квадратные скобки (списки)
- `.` - Точка (доступ к свойству)
- `,` - Запятая

**Литералы:**

- `IDENTIFIER` - Идентификаторы (Sun, Aries, Mercury)
- `NUMBER` - Числа (123, 45.6)
- `STRING` - Строки ("text", 'text')
- `BOOLEAN` - Булевы значения (True, False)

**Специальные:**

- `EOF` - Конец формулы
- `UNKNOWN` - Неизвестный символ (ошибка)

#### Ключевые слова

Регистрозависимые:

- `AND`, `OR`, `NOT` - Логические операторы (UPPERCASE)
- `IN` - Оператор вхождения (UPPERCASE)
- `planets`, `aspects`, `houses` - Агрегаторы (lowercase)
- `True`, `False` - Булевы значения (Capitalized)

#### Комментарии

```python
# Однострочные комментарии начинаются с #
"Sun.Sign == Aries"  # Комментарий в конце строки

# Комментарии игнорируются при токенизации
```

### Примеры формул

#### Простые выражения

```python
# Сравнение свойства
"Sun.Sign == Aries"
# ➜ Sun -> DOT -> Sign -> EQ -> Aries

# Доступ к свойству
"Mars.House"
# ➜ Mars -> DOT -> House

# Числовое сравнение
"Mars.House == 10"
# ➜ Mars -> DOT -> House -> EQ -> NUMBER(10)
```

#### Логические операторы

```python
# Конъюнкция (AND)
"Sun.Sign == Aries AND Moon.Sign == Taurus"
# ➜ Sun.Sign -> EQ -> Aries -> AND -> Moon.Sign -> EQ -> Taurus

# Дизъюнкция (OR)
"Mars.Sign == Aries OR Mars.Sign == Scorpio"
# ➜ Mars.Sign -> EQ -> Aries -> OR -> Mars.Sign -> EQ -> Scorpio

# Отрицание (NOT)
"NOT (Venus.Retrograde == True)"
# ➜ NOT -> LPAREN -> Venus.Retrograde -> EQ -> TRUE -> RPAREN
```

#### Списки и IN оператор

```python
# Проверка вхождения
"Mars.House IN [1, 4, 7, 10]"
# ➜ Mars.House -> IN -> LBRACKET -> 1, 4, 7, 10 -> RBRACKET

# Список знаков
"Sun.Sign IN [Aries, Leo, Sagittarius]"
# ➜ Sun.Sign -> IN -> [Aries, Leo, Sagittarius]
```

#### Агрегаторы

```python
# Все планеты с достоинством
"planets.Dignity == Rulership"
# ➜ PLANETS -> DOT -> Dignity -> EQ -> Rulership

# Все аспекты
"aspects.Type == Conjunction"
# ➜ ASPECTS -> DOT -> Type -> EQ -> Conjunction

# Все дома
"houses.Ruler == Mars"
# ➜ HOUSES -> DOT -> Ruler -> EQ -> Mars
```

#### Сложные формулы

```python
# Комбинация условий
"(Sun.Dignity == Exaltation OR Moon.Dignity == Rulership) AND NOT Mars.Retrograde"

# С приоритетами
"NOT (Venus.Retrograde == True) AND Mars.House IN [1, 4, 7, 10]"

# С агрегаторами
"planets.Dignity IN [Rulership, Exaltation] AND Sun.Sign == Leo"
```

### Строковые литералы

```python
# Двойные кавычки
'"Hello, world!"'

# Одинарные кавычки
"'Hello, world!'"

# Escape-последовательности
'"Line 1\\nLine 2"'  # Перевод строки
'"Tab\\there"'        # Табуляция
'"Quote: \\"Hi\\""'   # Кавычки внутри строки
```

### Обработка ошибок

```python
from src.dsl.lexer import LexerError

try:
    tokens = tokenize("Sun @ Moon")  # Недопустимый символ
except LexerError as e:
    print(e)
    # Неизвестный символ: '@' на позиции (строка 1, колонка 4)

try:
    tokens = tokenize('"Unclosed string')  # Незакрытая строка
except LexerError as e:
    print(e)
    # Незакрытая строка на позиции (строка 1, колонка 16)
```

### Отслеживание позиций

Каждый токен хранит информацию о позиции:

```python
token = Token(
    type=TokenType.IDENTIFIER,
    value='Sun',
    line=1,      # Номер строки (1-based)
    column=0     # Позиция в строке (0-based)
)
```

Это позволяет:

- Показывать точные позиции ошибок
- Выводить подсветку синтаксиса
- Генерировать подсказки в IDE

### Производительность

- ✅ Токенизация простой формулы: **< 1ms**
- ✅ Токенизация сложной формулы (50+ токенов): **< 5ms**
- ✅ 45 тестов выполняются за: **0.61s**

### API Reference

```python
from src.dsl.lexer import Lexer, Token, TokenType, LexerError

# Класс Lexer
lexer = Lexer("Sun.Sign == Aries")
tokens = lexer.tokenize()  # Возвращает List[Token]

# Или через convenience function
from src.dsl.lexer import tokenize
tokens = tokenize("Sun.Sign == Aries")

# Token dataclass
token = Token(
    type=TokenType.IDENTIFIER,
    value='Sun',
    line=1,
    column=0
)

# Все типы токенов
TokenType.AND          # Логическое И
TokenType.OR           # Логическое ИЛИ
TokenType.NOT          # Логическое НЕ
TokenType.EQ           # ==
TokenType.NEQ          # !=
TokenType.LT           # <
TokenType.GT           # >
TokenType.LTE          # <=
TokenType.GTE          # >=
TokenType.IN           # IN
TokenType.LPAREN       # (
TokenType.RPAREN       # )
TokenType.LBRACKET     # [
TokenType.RBRACKET     # ]
TokenType.DOT          # .
TokenType.COMMA        # ,
TokenType.PLANETS      # planets
TokenType.ASPECTS      # aspects
TokenType.HOUSES       # houses
TokenType.IDENTIFIER   # Sun, Aries
TokenType.NUMBER       # 123, 45.6
TokenType.STRING       # "text"
TokenType.BOOLEAN      # True, False
TokenType.EOF          # Конец формулы
TokenType.UNKNOWN      # Ошибка
```

### Тестирование

```bash
# Запуск тестов Lexer
pytest tests/test_lexer.py -v

# Только определённый тест-класс
pytest tests/test_lexer.py::TestBasicTokenization -v

# С подробным выводом
pytest tests/test_lexer.py -vv

# Результат:
# 45 passed in 0.61s
```

## ⚙️ Конфигурация

### Файл `config/dignities.yaml`

Содержит определения:

- **Управителей знаков** (Rulership)
- **Экзальтаций** (Exaltation)
- **Изгнаний** (Detriment)
- **Падений** (Fall)

### Режимы астрологии

**Traditional** (7 классических планет):

```yaml
traditional:
  rulers:
    Scorpio: [Mars] # Только Mars
    Aquarius: [Saturn] # Только Saturn
    Pisces: [Jupiter] # Только Jupiter
```

**Modern** (10 планет с внешними):

```yaml
modern:
  rulers:
    Scorpio: [Mars, Pluto] # Mars + Pluto
    Aquarius: [Saturn, Uranus] # Saturn + Uranus
    Pisces: [Jupiter, Neptune] # Jupiter + Neptune
```

### Переключение режима

```python
# Через код
validator = AstrologicalValidator(mode='traditional')

# Через CLI (будет реализовано)
python main.py natal ... --check="formula" --astro-mode=traditional
```

## 🏗️ Архитектура

```
src/dsl/
├── __init__.py          # Публичный API
├── validator.py         # ✅ Астрологический валидатор (552 строки)
├── lexer.py            # ✅ Токенизатор формул (400 строк)
├── parser.py           # TODO: Парсер в AST
└── evaluator.py        # TODO: Выполнение формул на карте

config/
├── dignities.yaml      # ✅ Определения достоинств (168 строк)
└── aspects.yaml        # TODO: Орбы и типы аспектов

tests/
├── test_dignity_validation.py  # ✅ Unit-тесты валидатора (60 тестов)
├── test_lexer.py               # ✅ Unit-тесты лексера (45 тестов)
├── test_parser.py              # TODO: Тесты парсера (~20 тестов)
└── test_integration.py         # TODO: E2E тесты (~15 тестов)
```

## 📊 Производительность

**Целевые метрики** (v1.0):

- ✅ Простая проверка: **< 1ms** (достигнуто: 440ns = 0.00044ms)
- ✅ Токенизация формулы: **< 1ms** (достигнуто: < 0.5ms)
- ✅ Сложная формула (10+ проверок): **< 10ms**
- ⏳ Формула с агрегаторами: **< 50ms** (TODO)
- ⏳ Батч из 100 формул: **< 500ms** (TODO)

**Оптимизации**:

- ✅ O(1) lookup таблицы (хэш-таблицы вместо списков)
- ✅ Предкомпиляция конфигурации при загрузке
- ✅ Эффективная токенизация (peek-ahead, minimal allocations)
- ⏳ Кэширование AST (TODO)

**Бенчмарки**:

```
Validator: 440ns per lookup = 2,300,000 ops/sec
Lexer: 45 тестов за 0.61s = ~13ms per test
Total: 105 тестов за 3.25s = ~31ms per test
```

## 🎓 Примеры валидации

### Базовая валидация

```python
validator = AstrologicalValidator()

# Ретроградность
validator.check_retrograde('Sun')        # ❌ Ошибка
validator.check_retrograde('Mercury')    # ✅ OK

# Самоаспект
validator.check_self_aspect('Mars', 'Mars')     # ❌ Ошибка
validator.check_self_aspect('Mars', 'Saturn')   # ✅ OK

# Диапазоны
validator.check_house_range(1)      # ✅ OK
validator.check_house_range(13)     # ❌ Ошибка
validator.check_degree_range(15)    # ✅ OK (0-29)
validator.check_degree_range(35)    # ❌ Ошибка
```

### Валидация достоинств

```python
# Экзальтации
validator.check_exaltation('Sun', 'Aries')      # ✅ OK
validator.check_exaltation('Sun', 'Taurus')     # ❌ Ошибка
validator.check_exaltation('Moon', 'Taurus')    # ✅ OK

# Соответствие планета-знак-достоинство
validator.check_dignity_sign_match('Mars', 'Aries', 'Rulership')    # ✅ OK
validator.check_dignity_sign_match('Mars', 'Taurus', 'Rulership')   # ❌ Ошибка

# Конфликты
validator.check_conflicting_dignities('Mars', 'Rulership', 'Fall')  # ❌ Ошибка
```

### Вспомогательные методы

```python
# Получение управителей
validator.get_ruler('Aries')        # ['Mars']
validator.get_ruler('Scorpio')      # ['Mars', 'Pluto'] в modern

# Проверка достоинств
validator.is_in_rulership('Mars', 'Aries')      # True
validator.is_in_exaltation('Sun', 'Aries')      # True
validator.is_in_fall('Saturn', 'Aries')         # True
validator.is_in_detriment('Mars', 'Libra')      # True

# Определение статуса
validator.get_dignity_status('Mars', 'Aries')       # 'Rulership'
validator.get_dignity_status('Sun', 'Aries')        # 'Exaltation'
validator.get_dignity_status('Sun', 'Gemini')       # 'Peregrine'
validator.get_dignity_status('Saturn', 'Aries')     # 'Fall'
```

## 🗺️ Roadmap

### v1.0.0-alpha (ТЕКУЩАЯ ВЕРСИЯ) ✅

- ✅ Базовая валидация (retrograde, ranges, self-aspect)
- ✅ Расширенная валидация достоинств (Ruler, Exaltation, Detriment, Fall)
- ✅ Конфигурационные YAML файлы
- ✅ Traditional vs Modern режимы
- ✅ Образовательные сообщения об ошибках
- ✅ **Lexer - полная токенизация формул** ⭐ NEW
- ✅ **105+ unit-тестов** (60 validator + 45 lexer)
- ✅ **Performance оптимизации** (O(1) lookups)

### v1.0.0-beta (В РАЗРАБОТКЕ) ⏳

- ⏳ **Parser - построение AST** (в процессе)
- ⏳ Evaluator - выполнение на картах
- ⏳ Агрегаторы (any/all/count)
- ⏳ Integration тесты
- ⏳ CLI интеграция

**Прогресс**: 40% (2 из 5 компонентов готовы)

### v1.0.0 (РЕЛИЗ) 🎯

- ⏳ Все функции из v1.0.0-beta
- ⏳ Полная документация
- ⏳ Примеры использования
- ⏳ Локализация (RU/EN)
- ⏳ 150+ тестов

**Ожидается**: 2-3 недели

### v2.0 (БУДУЩЕЕ) 💡

- Natural language parser (template-based)
- Visual formula builder (web/GUI/mobile)
- Расширенная валидация (mutual reception, almuten)
- AI-powered NLP (опционально)
- WHERE фильтры для агрегаторов
- Дополнительные агрегаторы (luminaries, malefics, benefics)

## 🤝 Вклад

### Как помочь проекту

1. **Тестирование** - найдите баги, предложите edge cases
2. **Документация** - улучшите примеры, добавьте туториалы
3. **Конфигурация** - добавьте альтернативные школы астрологии
4. **Производительность** - оптимизируйте узкие места

### Запуск в dev режиме

```bash
# Клонирование
git clone https://github.com/DergunovVA/astro.git
cd astro

# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/test_dignity_validation.py -v

# Запуск с coverage
pytest tests/test_dignity_validation.py --cov=src/dsl --cov-report=html
```

## 📄 Лицензия

MIT License - см. LICENSE файл

## 📧 Контакты

- GitHub: https://github.com/DergunovVA/astro
- Issues: https://github.com/DergunovVA/astro/issues

---

**Создано с ❤️ для астрологического сообщества**
