# 📋 ПРОЦЕСС ПЛАНИРОВАНИЯ СПРИНТОВ

**Дата создания:** 26 февраля 2026  
**Версия:** 1.0  
**Цель:** Разделить роли и процесс принятия решений

---

## 🎭 РОЛИ В ПРОЕКТЕ

### 👨‍🔬 Астролог-консультант (ЧТО делать)

**Ответственность:**

- Приоритизация астрологических фич (что важнее профессионалам)
- Валидация корректности расчетов (например, Прозерпина ID 47 vs 57)
- Определение стандартов (какие орбы, какие системы домов)
- Проверка интерпретаций (соответствие школам астрологии)

**НЕ решает:**

- Архитектуру кода
- Технологии реализации
- Performance оптимизации

**Примеры решений:**

- ✅ "Прозерпина ID 57 (Swiss Ephemeris), к расчетам вернемся позже"
- ✅ "Дома: Placidus + 8 других систем обязательны"
- ✅ "Арабские точки: Fortune, Spirit, Lilith, Vertex, East Point"

---

### 👨‍💻 Технический отдел (КАК делать)

**Ответственность:**

- Архитектура системы (модули, слои, API)
- Выбор технологий (Swiss Ephemeris, Pydantic, Typer)
- Оценка трудоемкости (сложность реализации)
- Performance и качество кода
- Testing и CI/CD

**НЕ решает:**

- Какие астрологические фичи важнее
- Астрологическую корректность (орбы, методы)
- Приоритеты для пользователей

**Примеры решений:**

- ✅ "Прозерпина: добавим SWEPH_PATH env variable для гибкости"
- ✅ "Ректификация сложная (v0.5+), требует event correlation"
- ✅ "Comparative уже реализовано, relocation работает"

---

## 🔄 ПРОЦЕСС ПЛАНИРОВАНИЯ СПРИНТА

### Шаг 1: Сбор требований (Вместе)

**Кто:** Астролог + Технический

**Что делаем:**

1. Обзор roadmap ([FEATURE_ROADMAP.md](FEATURE_ROADMAP.md))
2. Анализ пользовательских запросов (issue, feedback)
3. Конкурентный анализ (ZET, Solar Fire, AstroSeek)
4. Технический долг (bugs, refactoring)

**Результат:** Список кандидатов для спринта

**Пример:**

```
Кандидаты:
- Фиксированные звезды (15 основных)
- Ректификация (базовая версия)
- Dignities (rulership, exaltation)
- Транзиты (текущие)
- Arabic parts (расширение до 20)
```

---

### Шаг 2: Астрологическая приоритизация

**Кто:** Астролог-консультант

**Что делаем:**

1. Ранжировать по важности для профессионалов:
   - **MUST HAVE** (без этого система неполная)
   - **SHOULD HAVE** (важно, но можно отложить)
   - **NICE TO HAVE** (улучшения UX)
2. Определить астрологические стандарты:
   - Какие методы использовать (например, какой ayanamsa для Jyotish)
   - Какие орбы (мажорные/минорные аспекты)
   - Какие источники (Lilly для horary, Parashara для Jyotish)

**Результат:** Приоритизированный список с астрологическим обоснованием

**Пример:**

```
1. MUST HAVE: Dignities (rulership, exaltation, detriment, fall)
   Причина: Без этого невозможна horary астрология
   Стандарт: Классическая таблица Ptolemy

2. SHOULD HAVE: Фиксированные звезды (15 основных)
   Причина: Важно для prediction, но не блокирует другие фичи
   Стандарт: Regulus, Aldebaran, Antares, Fomalhaut + 11
   Орбы: 1° для conjunctions

3. NICE TO HAVE: Arabic parts (расширение)
   Причина: 5 основных уже есть, остальные редко используются
```

---

### Шаг 3: Техническая оценка

**Кто:** Технический отдел

**Что делаем:**

1. Оценить сложность реализации:
   - **SIMPLE** (1-2 часа): готовые данные, простая логика
   - **MEDIUM** (4-8 часов): новый модуль, интеграция
   - **COMPLEX** (2-5 дней): архитектурные изменения, R&D
2. Проверить технические зависимости:
   - Нужны ли внешние файлы (ephemeris)
   - Нужны ли новые библиотеки
   - Есть ли технический долг (refactoring)

3. Оценить риски:
   - Изменения в Swiss Ephemeris API
   - Breaking changes в существующем коде
   - Performance проблемы

**Результат:** Оценки с техническим обоснованием

**Пример:**

```
1. Dignities (rulership, exaltation, detriment, fall)
   Сложность: SIMPLE (2 часа)
   Причина: Статическая таблица в YAML, уже есть config/dignities.yaml
   Риски: Нет

2. Фиксированные звезды (15 основных)
   Сложность: MEDIUM (6 часов)
   Причина: Нужен каталог звезд (JSON), Swiss Ephemeris для точных координат
   Риски: Прецессия (звезды двигаются ~1° за 72 года)

3. Ректификация (базовая)
   Сложность: COMPLEX (3-5 дней)
   Причина: Нужен алгоритм scoring, event correlation, time windows
   Риски: Астрологически спорно (много школ, методов)
```

---

### Шаг 4: Формирование спринта (Вместе)

**Кто:** Астролог + Технический

**Что делаем:**

1. Матрица приоритет vs сложность:

   ```
   Priority\Complexity | SIMPLE | MEDIUM | COMPLEX
   -------------------|--------|--------|--------
   MUST HAVE          |   🟢   |   🟡   |   🔴
   SHOULD HAVE        |   🟢   |   🟡   |   🟠
   NICE TO HAVE       |   🟢   |   🔵   |   ⚪
   ```

   - 🟢 Включить в спринт (приоритет + быстро)
   - 🟡 Включить, если есть время
   - 🟠 Отложить на следующий спринт
   - 🔴 Требует отдельного R&D спринта
   - 🔵 Backlog (nice to have, но мало времени)
   - ⚪ Deferred (сложно + низкий приоритет)

2. Определить scope спринта:
   - Длина спринта: 1-2 недели
   - Capacity: реальное время (не календарное)
   - Buffer: 20% на непредвиденное

3. Сформировать список задач:
   - User story (зачем)
   - Acceptance criteria (как проверить)
   - Technical notes (как делать)

**Результат:** Sprint backlog с четким scope

**Пример спринта (1 неделя, 20 часов работы):**

```
Sprint: v0.2 Dignities (Week 1)
Capacity: 20 hours + 4h buffer = 24h

Tasks:
1. 🟢 Essential Dignities (2h) - MUST HAVE + SIMPLE
   - User story: Как астролог, хочу видеть dignities планет
   - Acceptance: Rulership, Exaltation, Detriment, Fall для всех планет
   - Technical: Extend config/dignities.yaml, add to output_formatter.py

2. 🟢 Accidental Dignities (4h) - MUST HAVE + MEDIUM
   - User story: Как астролог, хочу оценивать силу планет в домах
   - Acceptance: Angular/Succedent/Cadent, direct/retrograde scoring
   - Technical: New module src/core/accidental_dignities.py

3. 🟡 Mutual Reception (2h) - SHOULD HAVE + SIMPLE
   - User story: Как астролог, хочу видеть взаимные рецепции
   - Acceptance: Найти все пары планет в mutual reception
   - Technical: Logic in src/core/dignities.py

4. 🟢 Dignity Score (4h) - MUST HAVE + MEDIUM
   - User story: Как астролог, хочу общую оценку силы планеты
   - Acceptance: Score -5 до +5 для каждой планеты
   - Technical: Formula: essential + accidental dignities

Total: 12h planned (+ 12h buffer)
```

---

### Шаг 5: Execution & Review

**Execution:**

- Технический строит фичи
- Астролог проверяет корректность
- Daily sync (если нужно)

**Mid-sprint check:**

- День 3-4: проверить прогресс
- Корректировать scope если нужно

**Sprint review:**

- Demo фич астрологу
- Проверка acceptance criteria
- Testing (unit + manual)

**Retrospective:**

- Что сработало?
- Что не сработало?
- Как улучшить процесс?

---

## 📊 DECISION FRAMEWORK

### Когда спорим (Астролог vs Технический)

**Пример 1: Прозерпина**

- Астролог: "Хочу Прозерпину в 29° Libra (как в онлайн калькуляторах)"
- Технический: "Swiss Ephemeris дает 3° Scorpio (ID 57, стандарт)"
- **Решение:** Технический прав (Swiss Ephemeris = gold standard)
- **Компромисс:** Астролог исследует другие методы позже

**Пример 2: Ректификация**

- Астролог: "Ректификация MUST HAVE для профессионалов"
- Технический: "Ректификация COMPLEX (3-5 дней), не успеем в спринт"
- **Решение:** Астролог прав (приоритет), но откладываем на отдельный спринт
- **Компромисс:** Добавить stub команду сейчас, полная реализация позже

**Пример 3: Орбы аспектов**

- Астролог: "Орбы должны быть настраиваемые (каждая школа по-своему)"
- Технический: "Сделать настройку орбов = 8 часов (конфиг, UI, tests)"
- **Решение:** Астролог прав, но не MUST HAVE
- **Компромисс:** Hardcode стандартные орбы сейчас (2h), configurable позже (v0.3)

### Правило разрешения конфликтов

1. **Астрологическая корректность** > **Техническое удобство**
   - Если Swiss Ephemeris дает правильный результат, используем его
   - Если нужен нестандартный метод, обосновать астрологически

2. **Scope control** > **Feature creep**
   - Если фича сложная, лучше отложить чем делать плохо
   - MVP (minimal viable product) > идеальная реализация

3. **Профессионалы** > **Любители**
   - Prioritize features для профессиональных астрологов
   - Simplifications для новичков позже (v1.0+)

---

## 🎯 ТЕКУЩИЙ СТАТУС (26 февраля 2026)

### Что сделано (v0.1-0.3):

✅ **1. Координаты 12 домов**

- Команда: `python main.py houses <date> <time> <place>`
- Формат: table, degrees, json
- Системы: Placidus (по умолчанию), Whole Sign, Equal, etc.

✅ **2. Арабские точки**

- Команда: `python main.py arabic-parts <date> <time> <place>`
- Точки: Fortune, Spirit, Lilith, Vertex, East Point

✅ **3. Прозерпина**

- ID 57 (Swiss Ephemeris standard, Valentin Abramov version)
- Включена в natal/extended расчеты
- Примечание: Расчеты отличаются от онлайн калькуляторов (это нормально для гипотетических планет)

✅ **4. Сравнение релокационных карт**

- Команда: `python main.py comparative <date> <time> --chart-type relocation <cities>...`
- УЖЕ РАБОТАЕТ! (обнаружено при проверке)
- Документация: [docs/COMPARATIVE_CHARTS.md](COMPARATIVE_CHARTS.md)

⚠️ **5. Ректификация**

- Команда существует: `python main.py rectify <date> <time> <place>`
- Статус: STUB (возвращает пустой список candidates)
- Complexity: HIGH (требует event correlation, aspect scoring)
- Планы: v0.5+ (отдельный R&D спринт)

### Решение: Что делать дальше?

**Варианты:**

#### A) Закрыть v0.1-0.3 как есть (4/5)

- Ректификация = stub (команда работает, функционал позже)
- Перейти к v0.2 Dignities (более важно для профессионалов)
- **Pros:** Focus на важное, не тратим время на сложное
- **Cons:** Ректификация заявлена, но не работает

#### B) Простая ректификация (12 часов)

- Алгоритм: перебор времени ±2 часа, scoring по aspects to angles
- Без event correlation (только статистика)
- **Pros:** Хоть какая-то функциональность
- **Cons:** Астрологически слабая, может ввести в заблуждение

#### C) Полная ректификация (3-5 дней)

- Events correlation, транзиты, прогрессии
- Несколько методов (Trutina Hermetis, etc.)
- **Pros:** Профессиональный уровень
- **Cons:** Долго, блокирует другие фичи

---

## 🤔 ПРЕДЛОЖЕНИЯ ПЕРЕД СЛЕДУЮЩИМ СПРИНТОМ

### Вопрос 1: Закрываем v0.1-0.3?

- [ ] Да, ректификация = stub (переходим к v0.2)
- [ ] Нет, делаем простую ректификацию (12h)
- [ ] Нет, делаем полную ректификацию (3-5 дней)

### Вопрос 2: Приоритет v0.2?

Варианты (по важности для профессионалов):

**A) Dignities (Essential + Accidental)**

- Время: 12-16 часов
- Важность: MUST HAVE для horary астрологии
- Готовность: config/dignities.yaml уже есть

**B) Horary Methods (Void of Course, Via Combusta)**

- Время: 8-12 часов
- Важность: MUST HAVE для horary астрологии
- Зависимости: Нужны dignities

**C) Фиксированные звезды (15 основных)**

- Время: 6-8 часов
- Важность: SHOULD HAVE (важно, но не блокирует)
- Готовность: Нужен каталог (JSON)

**D) Транзиты (текущие + на дату)**

- Время: 4-6 часов
- Важность: SHOULD HAVE (востребовано пользователями)
- Готовность: Логика есть, нужен wrapper

### Вопрос 3: Длина спринта?

- [ ] 1 неделя (20h работы) - фокус на 1-2 больших фичах
- [ ] 2 недели (40h работы) - комплексный релиз
- [ ] Flexible (по готовности фич) - без жестких дедлайнов

---

## 📝 ПРЕДЛАГАЕМЫЙ ПЛАН

### Рекомендация: Sprint v0.2 (2 недели)

**Week 1: Dignities (16h)**

1. Essential Dignities (2h) - rulership, exaltation, detriment, fall
2. Accidental Dignities (4h) - angular/succedent/cadent, speed
3. Mutual Reception (2h) - взаимные рецепции
4. Dignity Score (4h) - общая оценка силы планеты
5. Tests + Docs (4h)

**Week 2: Horary Methods (12h)**

1. Void of Course Moon (2h)
2. Via Combusta warning (1h)
3. Applying/Separating aspects (4h)
4. Horary interpretation layer (3h)
5. Tests + Docs (2h)

**Total:** 28h planned + 12h buffer = 40h (2 weeks)

**Release:** v0.2 Horary Astrology (базовый уровень)

---

## ✅ NEXT STEPS

**Для Астролога-консультанта:**

1. Ответить на Вопрос 1 (ректификация)
2. Приоритизировать v0.2 (dignities vs horary vs stars vs transits)
3. Уточнить стандарты:
   - Dignities scoring: традиционный vs современный?
   - Void of Course: какой орб?
   - Via Combusta: 15° Libra - 15° Scorpio (классика)?

**Для Технического отдела:**

1. Дождаться решения по v0.1-0.3 (ректификация)
2. Подготовить technical design для v0.2:
   - Структура модулей
   - API contracts
   - Test strategy
3. Оценить риски и зависимости

**Совместно:**

1. Созвон/обсуждение (30 мин)
2. Сформировать sprint backlog
3. Начать execution

---

## 📌 ШАБЛОН SPRINT PLANNING

Для будущих спринтов использовать этот шаблон:

```markdown
# Sprint: <Name> (<Dates>)

## Астрологический приоритет

- MUST HAVE: [список фич]
- SHOULD HAVE: [список фич]
- NICE TO HAVE: [список фич]

## Техническая оценка

| Feature | Priority | Complexity | Time | Risks |
| ------- | -------- | ---------- | ---- | ----- |
| X       | MUST     | SIMPLE     | 2h   | None  |
| Y       | SHOULD   | MEDIUM     | 6h   | ...   |

## Sprint Scope

**Capacity:** 20h work + 4h buffer = 24h total
**Duration:** 1 week

**Tasks:**

1. [Task 1] (Xh) - [Priority + Complexity]
2. [Task 2] (Xh) - [Priority + Complexity]

**Total:** Xh planned

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests: X new tests
- [ ] Docs: Updated

## Sprint Review

- Date: [Date]
- Demo: [Link to demo]
- Status: [Completed / Partially / Deferred]
```

---

**Создано:** 26 февраля 2026  
**Автор:** GitHub Copilot + User  
**Статус:** Draft (ждем решений от астролога)
