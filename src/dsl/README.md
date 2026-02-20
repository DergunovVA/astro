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

✅ **204 теста** (203 passing, 99.5%) покрывают:

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

**Parser (46 тестов):**

- Базовый парсинг (литералы, идентификаторы)
- Доступ к свойствам (Sun.Sign)
- Сравнения (==, !=, <, >, <=, >=, IN)
- Списки ([1, 4, 7, 10])
- Логические операторы (AND, OR, NOT)
- Приоритет операторов
- Агрегаторы (planets.Dignity)
- Скобки и вложенность
- Сложные формулы
- Обработка ошибок
- AST представление

**Evaluator (53 теста):** ⭐ NEW

- Базовое выполнение (equality, inequality)
- Доступ к свойствам планет
- Числовые сравнения (<, >, <=, >=)
- IN оператор
- Логические операторы (AND, OR, NOT)
- Агрегаторы (planets, houses, aspects)
- Булевы значения
- Сложные формулы
- Обработка ошибок
- Edge cases
- Приоритет операторов

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

## 🌳 Parser (AST Builder)

### Обзор

Parser преобразует последовательность токенов в **Abstract Syntax Tree (AST)** - древовидную структуру, представляющую логику формулы.

### Быстрый старт

```python
from src.dsl.parser import parse

# Парсинг простой формулы
ast = parse("Sun.Sign == Aries")
print(ast)
# ASTNode(type=COMPARISON, value='==',
#         left=Property(Sun.Sign),
#         right=Identifier(Aries))

# Парсинг сложной формулы
ast = parse("Sun.Dignity == Exaltation AND Moon.House IN [1, 4, 7, 10]")
print(ast.type)  # NodeType.BINARY_OP
print(ast.value)  # AND
```

### Грамматика

Parser использует **рекурсивный спуск** (Recursive Descent) с операторными приоритетами:

```
expression     → or_expr
or_expr        → and_expr ( OR and_expr )*
and_expr       → not_expr ( AND not_expr )*
not_expr       → NOT not_expr | comparison
comparison     → primary ( ('==' | '!=' | '<' | '>' | '<=' | '>=' | 'IN') primary )?
primary        → identifier | number | string | boolean | list | property | aggregator | '(' expression ')'
```

#### Приоритет операторов

```
(Высший)   3. NOT      (унарный)
           2. AND      (конъюнкция)
(Низший)   1. OR       (дизъюнкция)
```

Пример:

```python
# NOT Moon.Retrograde AND Mars.House == 1 OR Sun.Sign == Leo
# Эквивалентно:
# ((NOT Moon.Retrograde) AND (Mars.House == 1)) OR (Sun.Sign == Leo)
```

### Типы узлов AST (11 типов)

#### Логические операции

**1. BINARY_OP** - Бинарные операторы AND, OR

```python
# Sun.Sign == Aries AND Moon.Sign == Taurus
ASTNode(
    type=NodeType.BINARY_OP,
    value='AND',
    left=Comparison(Sun.Sign == Aries),
    right=Comparison(Moon.Sign == Taurus)
)
```

**2. UNARY_OP** - Унарный оператор NOT

```python
# NOT Mars.Retrograde
ASTNode(
    type=NodeType.UNARY_OP,
    value='NOT',
    operand=Property(Mars.Retrograde)
)
```

#### Сравнения

**3. COMPARISON** - Операторы ==, !=, <, >, <=, >=, IN

```python
# Mars.House >= 10
ASTNode(
    type=NodeType.COMPARISON,
    value='>=',
    left=Property(Mars.House),
    right=Number(10)
)
```

#### Доступ к данным

**4. PROPERTY** - Доступ к свойству планеты

```python
# Sun.Sign
ASTNode(
    type=NodeType.PROPERTY,
    object=Identifier('Sun'),
    property='Sign'
)
```

**5. AGGREGATOR** - Агрегатор planets, aspects, houses

```python
# planets.Dignity
ASTNode(
    type=NodeType.AGGREGATOR,
    aggregator='planets',
    property='Dignity'
)
```

#### Литералы

**6. IDENTIFIER** - Идентификатор (Sun, Aries, Rulership)

```python
ASTNode(type=NodeType.IDENTIFIER, value='Aries')
```

**7. NUMBER** - Число (целое или float)

```python
ASTNode(type=NodeType.NUMBER, value=42)
ASTNode(type=NodeType.NUMBER, value=3.14)
```

**8. STRING** - Строковый литерал

```python
ASTNode(type=NodeType.STRING, value="Hello")
```

**9. BOOLEAN** - Булево значение

```python
ASTNode(type=NodeType.BOOLEAN, value=True)
```

**10. LIST** - Список

```python
# [1, 4, 7, 10]
ASTNode(
    type=NodeType.LIST,
    children=[
        Number(1),
        Number(4),
        Number(7),
        Number(10)
    ]
)
```

### Примеры парсинга

#### Простые выражения

```python
from src.dsl.parser import parse

# Свойство планеты
ast = parse("Sun.Sign")
# ➜ Property(object=Sun, property=Sign)

# Простое сравнение
ast = parse("Mars.House == 10")
# ➜ Comparison(==, left=Property(Mars.House), right=Number(10))

# Булев литерал
ast = parse("True")
# ➜ Boolean(True)
```

#### Логические операторы

```python
# AND
ast = parse("Sun.Sign == Aries AND Moon.Sign == Taurus")
# ➜ BinaryOp(AND,
#       left=Comparison(Sun.Sign == Aries),
#       right=Comparison(Moon.Sign == Taurus))

# OR
ast = parse("Mars.Sign == Aries OR Mars.Sign == Scorpio")
# ➜ BinaryOp(OR, ...)

# NOT
ast = parse("NOT Venus.Retrograde")
# ➜ UnaryOp(NOT, operand=Property(Venus.Retrograde))
```

#### Приоритет и скобки

```python
# Приоритет: NOT > AND > OR
ast = parse("NOT A AND B OR C")
# ➜ OR(
#       AND(NOT(A), B),
#       C
#     )

# Скобки переопределяют приоритет
ast = parse("NOT (A AND B) OR C")
# ➜ OR(
#       NOT(AND(A, B)),
#       C
#     )

ast = parse("A AND (B OR C)")
# ➜ AND(
#       A,
#       OR(B, C)
#     )
```

#### Списки и IN оператор

```python
# Список чисел
ast = parse("[1, 4, 7, 10]")
# ➜ List([Number(1), Number(4), Number(7), Number(10)])

# IN оператор
ast = parse("Moon.House IN [1, 4, 7, 10]")
# ➜ Comparison(IN,
#       left=Property(Moon.House),
#       right=List([1, 4, 7, 10]))

# Список идентификаторов
ast = parse("Sun.Sign IN [Aries, Leo, Sagittarius]")
# ➜ Comparison(IN,
#       left=Property(Sun.Sign),
#       right=List([Aries, Leo, Sagittarius]))
```

#### Агрегаторы

```python
# Агрегатор planets
ast = parse("planets.Dignity == Rulership")
# ➜ Comparison(==,
#       left=Aggregator(planets, Dignity),
#       right=Identifier(Rulership))

# Агрегатор aspects
ast = parse("aspects.Type")
# ➜ Aggregator(aspects, Type)

# Сравнение с списком
ast = parse("planets.Dignity IN [Rulership, Exaltation]")
# ➜ Comparison(IN,
#       left=Aggregator(planets, Dignity),
#       right=List([Rulership, Exaltation]))
```

#### Сложные формулы

```python
# Реальный пример
ast = parse(
    "(Sun.Dignity == Exaltation OR Moon.Dignity == Rulership) "
    "AND NOT Mars.Retrograde"
)
# ➜ AND(
#       OR(
#           Comparison(Sun.Dignity == Exaltation),
#           Comparison(Moon.Dignity == Rulership)
#       ),
#       NOT(Property(Mars.Retrograde))
#     )

# С агрегатором и списком
ast = parse(
    "planets.Dignity IN [Rulership, Exaltation] "
    "AND Sun.Sign == Leo"
)
# ➜ AND(
#       Comparison(IN, Aggregator(planets.Dignity), List([Rulership, Exaltation])),
#       Comparison(==, Property(Sun.Sign), Identifier(Leo))
#     )
```

### Обработка ошибок

```python
from src.dsl.parser import ParserError, parse

# Пустая формула
try:
    ast = parse("")
except ParserError as e:
    print(e)  # Пустая формула

# Неожиданный токен
try:
    ast = parse("Sun.Sign ==")
except ParserError as e:
    print(e)  # Неожиданный конец формулы на позиции ...

# Незакрытая скобка
try:
    ast = parse("(Sun.Sign == Aries")
except ParserError as e:
    print(e)  # Ожидалась закрывающая скобка ')', получен: EOF

# Незакрытый список
try:
    ast = parse("Moon.House IN [1, 4, 7")
except ParserError as e:
    print(e)  # Ожидалась закрывающая скобка ']', получен: EOF

# Недопустимый доступ к свойству
try:
    ast = parse("Sun.")
except ParserError as e:
    print(e)  # Ожидался идентификатор после '.', получен: EOF
```

### Представление AST

Parser генерирует удобочитаемое представление AST:

```python
ast = parse("Sun.Sign == Aries AND Moon.House == 1")
print(ast)
# BinaryOp(AND,
#   Comparison(==, Property(Sun.Sign), Identifier(Aries)),
#   Comparison(==, Property(Moon.House), Number(1))
# )

# Через __repr__()
repr(ast)
# "ASTNode(type=BINARY_OP, value='AND', left=..., right=...)"
```

### Производительность

- ✅ Парсинг простой формулы: **< 1ms**
- ✅ Парсинг сложной формулы (10+ узлов): **< 3ms**
- ✅ 46 тестов выполняются за: **0.44s**

### API Reference

```python
from src.dsl.parser import Parser, ASTNode, NodeType, ParserError

# Класс Parser
from src.dsl.lexer import tokenize
tokens = tokenize("Sun.Sign == Aries")
parser = Parser(tokens)
ast = parser.parse()  # Возвращает ASTNode

# Или через convenience function
from src.dsl.parser import parse
ast = parse("Sun.Sign == Aries")

# ASTNode dataclass
node = ASTNode(
    type=NodeType.COMPARISON,
    value='==',
    left=left_node,
    right=right_node
)

# Все типы узлов
NodeType.BINARY_OP      # AND, OR
NodeType.UNARY_OP       # NOT
NodeType.COMPARISON     # ==, !=, <, >, <=, >=, IN
NodeType.PROPERTY       # Sun.Sign, Mars.House
NodeType.AGGREGATOR     # planets.Dignity, aspects.Type
NodeType.IDENTIFIER     # Sun, Aries, Mercury
NodeType.NUMBER         # 123, 45.6
NodeType.STRING         # "text"
NodeType.BOOLEAN        # True, False
NodeType.LIST           # [1, 2, 3]
```

### Тестирование

```bash
# Запуск тестов Parser
pytest tests/test_parser.py -v

# Только определённый тест-класс
pytest tests/test_parser.py::TestBasicParsing -v

# Только сложные формулы
pytest tests/test_parser.py::TestComplexFormulas -v

# С подробным выводом
pytest tests/test_parser.py -vv

# Результат:
# 46 passed in 0.44s
```

### Интеграция с Lexer

Parser работает в связке с Lexer:

```python
from src.dsl.lexer import tokenize
from src.dsl.parser import Parser

# 1. Токенизация
formula = "Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]"
tokens = tokenize(formula)

# 2. Парсинг
parser = Parser(tokens)
ast = parser.parse()

# 3. Использование AST
print(ast.type)        # NodeType.BINARY_OP
print(ast.value)       # AND
print(ast.left.type)   # NodeType.COMPARISON
print(ast.right.type)  # NodeType.COMPARISON
```

Или короче через `parse()`:

```python
from src.dsl.parser import parse

ast = parse("Sun.Sign == Aries AND Moon.House IN [1, 4, 7, 10]")
# Внутри вызывает tokenize() и Parser()
```

## 🎯 Evaluator (AST Executor)

### Обзор

Evaluator выполняет AST на данных натальной карты, возвращая результат (обычно bool для формул-условий).

### Быстрый старт

```python
from src.dsl import parse, evaluate

# Данные карты
chart_data = {
    'planets': {
        'Sun': {'Sign': 'Capricorn', 'House': 9, 'Dignity': 'Neutral'},
        'Moon': {'Sign': 'Aquarius', 'House': 2, 'Dignity': 'Neutral'},
        'Mars': {'Sign': 'Libra', 'House': 6, 'Retrograde': False}
    }
}

# Способ 1: Через evaluate() (рекомендуется)
result = evaluate("Sun.Sign == Capricorn", chart_data)
print(result)  # True

# Способ 2: Явное создание Evaluator
from src.dsl.evaluator import Evaluator

ast = parse("Sun.Sign == Capricorn AND Moon.House < 5")
evaluator = Evaluator(chart_data)
result = evaluator.evaluate(ast)
print(result)  # True
```

### Поддерживаемые операции

#### Доступ к свойствам

```python
# Sun.Sign → "Capricorn"
result = evaluate("Sun.Sign", chart_data)
print(result)  # "Capricorn"

# Mars.House → 6
result = evaluate("Mars.House", chart_data)
print(result)  # 6

# Mars.Retrograde → False
result = evaluate("Mars.Retrograde", chart_data)
print(result)  # False
```

#### Сравнения

```python
# Равенство
evaluate("Sun.Sign == Capricorn", chart_data)  # True
evaluate("Moon.Sign != Aries", chart_data)  # True

# Числовые сравнения
evaluate("Moon.House > 1", chart_data)  # True (2 > 1)
evaluate("Mars.House <= 10", chart_data)  # True (6 <= 10)

# IN оператор
evaluate("Sun.House IN [9, 10, 11, 12]", chart_data)  # True
evaluate("Moon.Sign IN [Aries, Leo, Sagittarius]", chart_data)  # False
```

#### Логические операторы

```python
# AND
evaluate("Sun.Sign == Capricorn AND Moon.House == 2", chart_data)  # True

# OR
evaluate("Sun.Sign == Aries OR Moon.House == 2", chart_data)  # True

# NOT
evaluate("NOT (Mars.Retrograde == True)", chart_data)  # True

# Сложные комбинации
evaluate(
    "(Sun.Sign == Capricorn OR Moon.Sign == Aries) AND NOT Mars.Retrograde",
    chart_data
)  # True
```

#### Агрегаторы

```python
# Данные карты с агрегаторами
chart = {
    'planets': {
        'Sun': {'Dignity': 'Neutral'},
        'Moon': {'Dignity': 'Neutral'},
        'Mars': {'Dignity': 'Detriment'},
        'Venus': {'Dignity': 'Neutral'}
    }
}

# planets.Dignity → ['Neutral', 'Neutral', 'Detriment', 'Neutral']
result = evaluate("planets.Dignity", chart)
print(result)  # ['Neutral', 'Neutral', 'Detriment', 'Neutral']

# Проверка вхождения
result = evaluate("Detriment IN planets.Dignity", chart)
print(result)  # True

# Агрегаторы houses и aspects
chart_with_houses = {
    'houses': {
        1: {'Sign': 'Taurus', 'Ruler': 'Venus'},
        2: {'Sign': 'Gemini', 'Ruler': 'Mercury'}
    },
    'aspects': [
        {'Type': 'Conjunction', 'Planet1': 'Sun', 'Planet2': 'Mars'},
        {'Type': 'Trine', 'Planet1': 'Moon', 'Planet2': 'Venus'}
    ]
}

evaluate("Taurus IN houses.Sign", chart_with_houses)  # True
evaluate("Conjunction IN aspects.Type", chart_with_houses)  # True
```

### Производительность

- ✅ Простая формула (`Sun.Sign == Aries`): **< 0.1ms**
- ✅ Средняя формула (3-5 условий с AND/OR): **< 0.5ms**
- ✅ Сложная формула (агрегаторы): **< 2ms**
- ✅ 53 теста выполняются за: **0.85s**

### API Reference

```python
from src.dsl.evaluator import Evaluator, EvaluatorError

# Класс Evaluator
evaluator = Evaluator(chart_data)
result = evaluator.evaluate(ast)  # Выполнить AST

# Convenience function (рекомендуется)
from src.dsl.evaluator import evaluate
result = evaluate("Sun.Sign == Aries", chart_data)

# Ошибки
try:
    result = evaluator.evaluate(ast)
except EvaluatorError as e:
    print(f"Ошибка выполнения: {e}")
```

### Тестирование

```bash
# Запуск тестов Evaluator
pytest tests/test_evaluator.py -v

# Только определённый тест-класс
pytest tests/test_evaluator.py::TestBasicEvaluation -v

# С подробным выводом
pytest tests/test_evaluator.py -vv

# Результат:
# 53 passed in 0.85s
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
├── __init__.py          # ✅ Публичный API
├── validator.py         # ✅ Астрологический валидатор (550 строк)
├── lexer.py            # ✅ Токенизатор формул (700 строк)
├── parser.py           # ✅ Парсер в AST (475 строк)
└── evaluator.py        # ✅ Выполнение формул на карте (420 строк) ⭐ NEW

config/
├── dignities.yaml      # ✅ Определения достоинств (168 строк)
└── aspects.yaml        # TODO: Орбы и типы аспектов

tests/
├── test_dignity_validation.py  # ✅ Unit-тесты валидатора (60 тестов)
├── test_lexer.py               # ✅ Unit-тесты лексера (45 тестов)
├── test_parser.py              # ✅ Unit-тесты парсера (46 тестов)
├── test_evaluator.py           # ✅ Unit-тесты evaluator (53 теста) ⭐ NEW
└── test_integration.py         # TODO: E2E тесты (~15 тестов)
```

## 📊 Производительность

**Целевые метрики** (v1.0):

- ✅ Простая проверка: **< 1ms** (достигнуто: 440ns = 0.00044ms)
- ✅ Токенизация формулы: **< 1ms** (достигнуто: < 0.5ms)
- ✅ Парсинг формулы: **< 1ms** (достигнуто: < 0.5ms) ⭐ NEW
- ✅ Сложная формула (10+ проверок): **< 10ms** (достигнуто: < 3ms)
- ⏳ Формула с агрегаторами: **< 50ms** (TODO)
- ⏳ Батч из 100 формул: **< 500ms** (TODO)

**Оптимизации**:

- ✅ O(1) lookup таблицы (хэш-таблицы вместо списков)
- ✅ Предкомпиляция конфигурации при загрузке
- ✅ Эффективная токенизация (peek-ahead, minimal allocations)
- ✅ Рекурсивный спуск без backtracking ⭐ NEW
- ⏳ Кэширование AST (TODO)

**Бенчмарки**:

```
Validator: 440ns per lookup = 2,300,000 ops/sec
Lexer: 45 тестов за 0.61s = ~13ms per test
Parser: 46 тестов за 0.44s = ~9.5ms per test ⭐ NEW
Total: 151 тест за 4.30s = ~28ms per test
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

### v1.0.0-beta (ТЕКУЩАЯ ВЕРСИЯ) ✅

- ✅ Базовая валидация (retrograde, ranges, self-aspect)
- ✅ Расширенная валидация достоинств (Ruler, Exaltation, Detriment, Fall)
- ✅ Конфигурационные YAML файлы
- ✅ Traditional vs Modern режимы
- ✅ Образовательные сообщения об ошибках
- ✅ **Lexer - полная токенизация формул** (700 строк, 45 тестов)
- ✅ **Parser - построение AST** (475 строк, 46 тестов)
- ✅ **Evaluator - выполнение на картах** (420 строк, 53 теста) ⭐ NEW
- ✅ **204 unit-теста** (60 + 45 + 46 + 53)
- ✅ **Performance оптимизации** (O(1) lookups, < 1ms parsing, < 2ms evaluation)

**Прогресс**: 80% (4 из 5 компонентов готовы) ⭐

### v1.0.0 (РЕЛИЗ) 🎯

- ⏳ CLI интеграция (--check флаг)
- ⏳ E2E Integration тесты
- ⏳ Полная документация
- ⏳ Примеры использования
- ⏳ Локализация (RU/EN)
- ⏳ 220+ тестов

**Ожидается**: 3-5 дней ⭐

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
