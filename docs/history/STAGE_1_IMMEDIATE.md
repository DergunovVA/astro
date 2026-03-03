# 🔴 STAGE 1: IMMEDIATE STABILIZATION

**Период:** 20-21 февраля 2026 (2 дня)  
**Приоритет:** 🔴 CRITICAL  
**Статус:** 🔄 IN PROGRESS  
**Команда:** Dev Team + QA Team

---

## 🎯 ЦЕЛИ ЭТАПА

### Главная цель

Стабилизировать кодовую базу, достичь 100% test passing rate и очистить deprecated код.

### Конкретные цели

1. ✅ Исправить все failing tests (1/295 currently failing)
2. ✅ Удалить весь deprecated код
3. ✅ Достичь clean test output (no warnings)
4. ✅ Обновить документацию по результатам

### Метрики успеха

- Tests passing: 295/295 (100%)
- Deprecated files: 0
- Test warnings: 0
- Code coverage: > 80%

---

## 📋 ЗАДАЧИ

### Task 1.1: Исправить Unicode Encoding Error

**Приоритет:** 🔴 CRITICAL  
**Оценка:** 30 минут  
**Назначено:** Dev Team  
**Статус:** ⏳ TODO

#### Проблема

```
ERROR tests/test_dignity_validation.py::TestPerformance::test_lookup_performance
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 184
```

#### Причина

Windows по умолчанию использует CP1252 encoding вместо UTF-8 при subprocess.

#### Решение

```python
# В test_dignity_validation.py::TestPerformance::test_lookup_performance

# БЫЛО:
result = subprocess.run(cmd, capture_output=True, text=True)

# СТАЛО:
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding='utf-8'  # Явно указываем UTF-8
)
```

#### Шаги выполнения

1. [ ] Открыть `tests/test_dignity_validation.py`
2. [ ] Найти test_lookup_performance
3. [ ] Добавить `encoding='utf-8'` ко всем subprocess.run()
4. [ ] Проверить другие тесты с subprocess
5. [ ] Запустить тест: `pytest tests/test_dignity_validation.py::TestPerformance::test_lookup_performance -v`
6. [ ] Убедиться что тест проходит

#### Acceptance Criteria

- ✅ Тест test_lookup_performance проходит
- ✅ Нет Unicode ошибок
- ✅ Работает на Windows и Linux

#### Dependencies

- None

---

### Task 1.2: Cleanup Deprecated Code

**Приоритет:** 🔴 CRITICAL  
**Оценка:** 1 час  
**Назначено:** Dev Team  
**Статус:** ⏳ TODO

#### Список deprecated файлов

1. `src/professional/event_finder_old.py` - помечен как OLD
2. Части `src/core/core_math.py` - помечены для cleanup в v0.2

#### Шаги выполнения

##### 1.2.1: Проверить зависимости

```bash
# Найти все импорты event_finder_old
grep -r "event_finder_old" . --include="*.py" | grep -v ".pyc"

# Найти импорты core_math
grep -r "from src.core.core_math import" . --include="*.py"
grep -r "import src.core.core_math" . --include="*.py"
```

##### 1.2.2: Удалить event_finder_old.py

```bash
# Если нет зависимостей:
git rm src/professional/event_finder_old.py

# Обновить __init__.py если нужно
# vim src/professional/__init__.py
```

##### 1.2.3: Очистить core_math.py

```python
# Удалить или закомментировать deprecated секции
# Оставить только актуальные функции
# Обновить docstring с пометкой о cleanup
```

##### 1.2.4: Запустить тесты

```bash
# Проверить что ничего не сломалось
pytest tests/ -v --tb=short
```

#### Acceptance Criteria

- ✅ event_finder_old.py удален
- ✅ core_math.py очищен от deprecated кода
- ✅ Все тесты проходят
- ✅ Нет broken imports

#### Dependencies

- Task 1.1 должен быть завершен (чтобы тесты проходили)

---

### Task 1.3: Fix Test Warnings

**Приоритет:** 🟡 HIGH  
**Оценка:** 30 минут  
**Назначено:** QA Team  
**Статус:** ⏳ TODO

#### Проблема

```
PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset
```

#### Решение

Добавить в `pytest.ini` или `pyproject.toml`:

```ini
# pytest.ini
[pytest]
asyncio_default_fixture_loop_scope = function
```

#### Шаги выполнения

1. [ ] Создать или обновить pytest.ini
2. [ ] Добавить asyncio config
3. [ ] Запустить тесты: `pytest tests/ -v`
4. [ ] Убедиться что warning исчез

#### Acceptance Criteria

- ✅ Нет deprecation warnings
- ✅ Все тесты проходят
- ✅ Clean test output

#### Dependencies

- None

---

### Task 1.4: Run Full Test Suite

**Приоритет:** 🔴 CRITICAL  
**Оценка:** 15 минут  
**Назначено:** QA Team  
**Статус:** ⏳ TODO

#### Цель

Убедиться что все 295 тестов проходят успешно.

#### Команды

```bash
# Full test run
pytest tests/ -v --tb=short

# С coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Только быстрые тесты (smoke test)
pytest tests/ -v -m "not slow"
```

#### Ожидаемый результат

```
============================= test session starts =============================
...
======================= 295 passed in XX.XXs ===============================
```

#### Acceptance Criteria

- ✅ 295/295 tests passing
- ✅ No errors
- ✅ No warnings
- ✅ Coverage > 80%

#### Dependencies

- Task 1.1 (Unicode fix)
- Task 1.2 (Cleanup)
- Task 1.3 (Warnings fix)

---

### Task 1.5: Update Documentation

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 30 минут  
**Назначено:** Dev Team  
**Статус:** ⏳ TODO

#### Файлы для обновления

1. `docs/TODO_ROADMAP.md` - обновить прогресс Stage 1
2. `docs/STAGE_1_RESULTS.md` - создать отчет о результатах
3. `docs/PROJECT_STATUS_COMPLETE.md` - обновить статус
4. `README.md` - обновить badge тестов

#### Шаги выполнения

1. [ ] Создать STAGE_1_RESULTS.md
2. [ ] Обновить прогресс в TODO_ROADMAP.md
3. [ ] Обновить метрики в PROJECT_STATUS_COMPLETE.md
4. [ ] Добавить test badge в README.md

#### Acceptance Criteria

- ✅ STAGE_1_RESULTS.md создан
- ✅ Все метрики обновлены
- ✅ Documentation актуальна

#### Dependencies

- Task 1.4 (Full test suite must pass)

---

## 📊 ПРОГРЕСС ВЫПОЛНЕНИЯ

### Timeline

```
Day 1 (2026-02-20):
├── 09:00-10:00  Task 1.1: Fix Unicode error
├── 10:00-11:00  Task 1.2: Cleanup deprecated code
├── 11:00-11:30  Task 1.3: Fix test warnings
├── 11:30-12:00  Task 1.4: Run full test suite
└── 14:00-14:30  Task 1.5: Update documentation

Day 2 (2026-02-21):
├── 09:00-10:00  Review & validation
├── 10:00-11:00  Bug fixes if needed
├── 11:00-12:00  Final test run
└── 14:00-15:00  Stage 1 retrospective
```

### Checklist

- [ ] Task 1.1: Unicode fix
- [ ] Task 1.2: Cleanup deprecated
- [ ] Task 1.3: Fix warnings
- [ ] Task 1.4: Full test suite
- [ ] Task 1.5: Update docs
- [ ] All tests passing (295/295)
- [ ] No deprecated code
- [ ] Zero warnings
- [ ] Stage 1 complete!

---

## 🎯 EXPECTED RESULTS

### Code Quality

```
Before Stage 1:
- Tests passing: 80/295 (27%)
- Deprecated files: 2
- Warnings: Multiple
- Code cleanliness: 85%

After Stage 1:
- Tests passing: 295/295 (100%) ✅
- Deprecated files: 0 ✅
- Warnings: 0 ✅
- Code cleanliness: 95% ✅
```

### Deliverables

1. ✅ Clean test suite (100% passing)
2. ✅ No deprecated code
3. ✅ Updated documentation
4. ✅ STAGE_1_RESULTS.md report

---

## 🚨 RISKS & MITIGATION

### Risk 1: Unicode fix breaks other tests

**Probability:** Low  
**Impact:** Medium  
**Mitigation:** Test on both Windows and Linux

### Risk 2: Removing deprecated code breaks functionality

**Probability:** Low  
**Impact:** High  
**Mitigation:** Thorough dependency check before removal

### Risk 3: Not enough time to complete

**Probability:** Low  
**Impact:** Medium  
**Mitigation:** Focus on critical tasks first (1.1, 1.2, 1.4)

---

## 📈 METRICS TO TRACK

### Daily Metrics

- [ ] Tests passing count
- [ ] Test execution time
- [ ] Code coverage %
- [ ] Number of warnings

### Final Metrics

- [ ] Total time spent
- [ ] Issues encountered
- [ ] Issues resolved
- [ ] Documentation updated

---

## 🔄 TRANSITION TO STAGE 2

### Prerequisites for Stage 2

- ✅ All Stage 1 tasks complete
- ✅ 295/295 tests passing
- ✅ Zero deprecated code
- ✅ Zero warnings

### Handoff to Stage 2

1. Create STAGE_1_RESULTS.md
2. Update TODO_ROADMAP.md progress
3. Schedule Stage 2 kickoff meeting
4. Assign Stage 2 tasks

---

## 📞 COMMUNICATION

### Daily Standup

- **Time:** 09:00 daily
- **Duration:** 15 minutes
- **Format:** What done, what blocking, what next

### Status Updates

- **To:** Product Owner
- **When:** End of Day 1, End of Day 2
- **Format:** Email with progress report

### Completion Announcement

- **To:** All stakeholders
- **When:** After Task 1.5 complete
- **Format:** Slack + Email with STAGE_1_RESULTS.md

---

## ✅ DEFINITION OF DONE

Stage 1 считается завершенным когда:

- [x] TODO audit complete
- [ ] All 5 tasks completed
- [ ] 295/295 tests passing
- [ ] Zero deprecated code
- [ ] Zero test warnings
- [ ] Documentation updated
- [ ] STAGE_1_RESULTS.md created
- [ ] Code review passed
- [ ] QA sign-off received

---

_Created: 2026-02-20_  
_Owner: Dev Team Lead_  
_Status: IN PROGRESS_  
_Next Review: 2026-02-21_
