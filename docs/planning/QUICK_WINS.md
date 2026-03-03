# 🎯 QUICK WINS - Мелочи и Красивости

**Дата:** 26 февраля 2026  
**Стратегия:** Делаем сейчас → потом хардкор  
**Критерий:** ≤ 2 часа на фичу, видимый результат

---

## 📊 ТЕКУЩИЙ СТАТУС

### ✅ Готово (v0.1-0.3):

- Дома 12 (команда `houses`)
- Арабские точки 5 (команда `arabic-parts`)
- Прозерпина (ID 57)
- Comparative charts (команда `comparative --chart-type relocation`)

### ⏸️ Отложено:

- Ректификация → v0.5+ (сложно, 3-5 дней)

---

## 🚀 КАТЕГОРИИ QUICK WINS

### 1️⃣ Улучшение OUTPUT (красивости)

**Текущая проблема:**

- JSON громоздкий (50+ строк для простой карты)
- Нет компактного формата для терминала
- Символы планет есть, но не везде используются

**Quick wins:**

#### A) Compact format (1h)

```bash
python main.py natal 1982-01-08 09:40 Saratov --format compact

# Output:
☉ Cap 17°37' (H12) | ☽ Gem 25°24' (H5) | ☿ Aqu 3°55' (H1)
♀ Cap 26°51' (H12) | ♂ Lib 26°53' (H9) | ♃ Sco 6°22' (H9)
♄ Lib 20°56'℞ (H9) | ♅ Sag 2°18' (H10) | ♆ Sag 24°19' (H11)
♇ Lib 26°48' (H9) | ☊ Can 20°06' (H6)

ASC: Aqu 3°41' | MC: Sco 4°43'
Major aspects: 9 | Stellium: Libra (3)
```

#### B) Beautiful table (1h)

```bash
python main.py natal 1982-01-08 09:40 Saratov --format table

# Output:
┌─────────┬──────┬─────────┬───────┬────────┬────────┐
│ Planet  │ Sign │ Degree  │ House │ Dignity│ Speed  │
├─────────┼──────┼─────────┼───────┼────────┼────────┤
│ ☉ Sun   │ ♑ Cap│ 17°37'  │  12   │ Neutral│  1.01° │
│ ☽ Moon  │ ♊ Gem│ 25°24'  │   5   │ Neutral│ 13.45° │
│ ☿ Merc  │ ♒ Aqu│  3°55'  │   1   │ Neutral│  1.23° │
│ ♀ Venus │ ♑ Cap│ 26°51'  │  12   │ Neutral│  1.18° │
│ ♂ Mars  │ ♎ Lib│ 26°53'  │   9   │ Detrim │  0.65° │
│ ♃ Jup   │ ♏ Sco│  6°22'  │   9   │ Neutral│  0.20° │
│ ♄ Sat ℞ │ ♎ Lib│ 20°56'  │   9   │ Exalt  │ -0.05° │
│ ♅ Uran  │ ♐ Sag│  2°18'  │  10   │ Neutral│  0.06° │
│ ♆ Nept  │ ♐ Sag│ 24°19'  │  11   │ Neutral│  0.04° │
│ ♇ Pluto │ ♎ Lib│ 26°48'  │   9   │ Neutral│  0.02° │
└─────────┴──────┴─────────┴───────┴────────┴────────┘
```

#### C) Color support (1.5h)

- Красный: ♂ Mars, ♇ Pluto
- Синий: ☽ Moon, ♆ Neptune
- Желтый: ☉ Sun
- Зеленый: ♀ Venus, ♃ Jupiter
- Серый: ♄ Saturn
- Элементы: 🔥 Fire, 💧 Water, 🌬️ Air, 🌍 Earth

#### D) Summary line (0.5h)

```bash
python main.py natal 1982-01-08 09:40 Saratov --summary

# Output:
☉ ♑ 17° | ☽ ♊ 25° | ASC ♒ 3° | MC ♏ 4° | Stellium ♎ (♂♄♇) | 9 aspects
```

**Приоритет:** 🔥 HIGH  
**Время:** 4h total  
**Эффект:** UX резко лучше, терминал читаемый

---

### 2️⃣ Расширение данных (малые справочники)

**Текущая проблема:**

- Города: только 5 в data/cities_sample.txt
- Нет фиксированных звезд
- Нет часовых поясов для популярных городов

**Quick wins:**

#### E) Расширенный атлас городов (1h)

```yaml
# data/cities_extended.yaml
cities:
  - name: Moscow
    country: RU
    lat: 55.7558
    lon: 37.6173
    timezone: Europe/Moscow
    aliases: [Москва, MSK]

  - name: London
    country: GB
    lat: 51.5074
    lon: -0.1278
    timezone: Europe/London
    aliases: [Лондон, LDN]

  # ... 100 крупнейших городов мира
```

**Источник:** https://simplemaps.com/data/world-cities

#### F) Топ-15 фиксированных звезд (1.5h)

```yaml
# data/fixed_stars.yaml
stars:
  - name: Regulus
    constellation: Leo
    longitude: 29.50 # Leo (tropical 2000)
    precession: 0.014 # degrees per year
    magnitude: 1.35
    nature: Mars-Jupiter
    interpretation: "Royal Star, leadership, courage"
    orb: 1.0

  - name: Aldebaran
    constellation: Taurus
    longitude: 9.47 # Gemini
    magnitude: 0.85
    nature: Mars
    interpretation: "Watcher of East, military honors"

  # ... 13 more
```

**Источник:** Robson's Fixed Stars and Constellations

#### G) Арабские точки расширенные (1h)

```yaml
# config/arabic_parts.yaml
parts:
  # Текущие (5):
  - Fortune
  - Spirit
  - Lilith (Mean)
  - Vertex
  - East Point

  # Новые (еще 10):
  - Part of Marriage
  - Part of Children
  - Part of Death
  - Part of Sudden Events
  - Part of Siblings
  - Part of Father
  - Part of Mother
  - Part of Sickness
  - Part of Profession
  - Part of Love
```

**Приоритет:** 🟡 MEDIUM  
**Время:** 3.5h total  
**Эффект:** Больше данных, меньше ручной работы

---

### 3️⃣ Дополнительные команды (функционал)

**Текущие команды:** natal, transit, solar, relocate, rectify, devils, comparative, synastry, psychology, houses, arabic-parts

**Quick wins:**

#### H) Команда `aspects` (1h)

```bash
python main.py aspects 1982-01-08 09:40 Saratov

# Output:
Major aspects (5):
  ☉ ☐ ♄  Sun square Saturn (orb 3.32°) - Challenge
  ☽ △ ☿  Moon trine Mercury (orb 1.49°) - Harmony
  ♂ ☌ ♇  Mars conjunction Pluto (orb 0.05°) - Power
  ♃ ✱ ☽  Jupiter sextile Moon (orb 1.02°) - Opportunity
  ♄ △ ☿  Saturn trine Mercury (orb 2.01°) - Discipline

Minor aspects (11):
  [...]
```

#### I) Команда `dignities` (1.5h)

```bash
python main.py dignities 1982-01-08 09:40 Saratov

# Output:
Essential Dignities:
  ☉ Sun in ♑ Capricorn: Neutral (0)
  ☽ Moon in ♊ Gemini: Neutral (0)
  ♂ Mars in ♎ Libra: Detriment (-4)
  ♄ Saturn in ♎ Libra: Exaltation (+4)

Accidental Dignities:
  ☉ Sun in H12 (Cadent): Weak (-2)
  ♄ Saturn Retrograde: Debilitated (-2)

Total Scores:
  ♄ Saturn: +2 (Exalted but retrograde)
  ☽ Moon: +1 (Angular house)
  ☉ Sun: -2 (Cadent)
  ♂ Mars: -4 (Detriment)
```

#### J) Команда `transits` (2h)

```bash
python main.py transits 1982-01-08 09:40 Saratov --date 2026-02-26

# Output:
Transits for 2026-02-26:
  Transit ♃ Jupiter (♊ Gemini 12°) ☌ Natal ☽ Moon (♊ Gemini 25°)
    → Orb: 13°, applying (2 weeks to exact)
    → Interpretation: Expansion, optimism, good fortune

  Transit ♄ Saturn (♓ Pisces 16°) ☐ Natal ☉ Sun (♑ Capricorn 17°)
    → Orb: 1°, separating
    → Interpretation: Restriction, discipline, challenge
```

#### K) Команда `chart-info` (0.5h)

```bash
python main.py chart-info 1982-01-08 09:40 Saratov

# Output:
Chart Type: Natal
Date: 1982-01-08 09:40 (Europe/Saratov)
Coordinates: 51.53°N, 46.00°E

Sun Sign: ♑ Capricorn
Moon Sign: ♊ Gemini
Ascendant: ♒ Aquarius 3°41'
MC: ♏ Scorpio 4°43'

House System: Placidus
Zodiac: Tropical
Ayanamsa: N/A

Stellium: ♎ Libra (♂ Mars, ♄ Saturn, ♇ Pluto)
Chart Shape: Splay (scattered planets)
Hemisphere: Mostly Eastern (independent)
```

**Приоритет:** 🔥 HIGH  
**Время:** 5h total  
**Эффект:** Больше функций без сложной логики

---

### 4️⃣ Улучшение UX (удобства)

**Quick wins:**

#### L) Auto-save карт (1h)

```bash
python main.py natal 1982-01-08 09:40 Saratov --save "john_natal"

# Saves to: ~/.astro/charts/john_natal.json
```

```bash
python main.py load john_natal --format compact
```

#### M) History команда (0.5h)

```bash
python main.py history

# Output:
Recent calculations:
1. 2026-02-26 14:30 - Natal chart: 1982-01-08 Saratov
2. 2026-02-26 14:15 - Comparative: Moscow, London, Tokyo
3. 2026-02-25 19:45 - Transit: 2026-02-26
```

#### N) Aliases для команд (0.5h)

```bash
python main.py n 1982-01-08 09:40 Saratov  # alias for natal
python main.py t 2026-02-26  # alias for transits (uses last natal)
python main.py a  # alias for aspects (uses last natal)
```

#### O) Config file (1h)

```yaml
# ~/.astro/config.yaml
defaults:
  house_system: Placidus
  zodiac: Tropical
  orb_major: 8.0
  orb_minor: 3.0
  format: table
  language: ru

colors:
  enabled: true
  scheme: dark # or light

cache:
  enabled: true
  ttl: 86400 # 1 day
```

**Приоритет:** 🟢 LOW  
**Время:** 3h total  
**Эффект:** Удобство для частого использования

---

## 📁 СПРАВОЧНИКИ (2-4 часа каждый)

### База 1: Географические точки

**Структура:**

```
data/
  geography/
    cities_world_1000.yaml       # 1000 крупнейших городов
    cities_russia_100.yaml       # 100 городов России
    timezones.yaml               # Mapping city → timezone
    coordinates_cache.db         # SQLite кэш для geopy
```

**Источники:**

- SimpleMaps World Cities Database (15000+ городов)
- OpenStreetMap Nominatim
- IANA Timezone Database

**Время:** 3h (парсинг + структурирование)

---

### База 2: Фиксированные звезды

**Структура:**

```
data/
  fixed_stars/
    ptolemy_48.yaml          # 48 звезд Ptolemy
    robson_110.yaml          # 110 звезд Robson
    bernadette_brady.yaml    # Современные интерпретации
    precession.py            # Расчет прецессии
```

**Поля:**

- Name (Latin + Common)
- Constellation
- Longitude (epoch 2000)
- Precession rate
- Magnitude
- Nature (Mars-like, Venus-like)
- Interpretation (short)
- Orb (обычно 1°)

**Источники:**

- Robson: "Fixed Stars and Constellations in Astrology"
- Brady: "Brady's Book of Fixed Stars"
- Swiss Ephemeris fixed stars file

**Время:** 4h (исследование + структурирование)

---

### База 3: Астероиды (опционально)

**Структура:**

```
data/
  asteroids/
    main_four.yaml      # Ceres, Pallas, Juno, Vesta
    centaurs.yaml       # Chiron, Pholus, Nessus
    tno.yaml            # Trans-Neptunian Objects
```

**Swiss Ephemeris:**

- ID 2: Ceres
- ID 3: Pallas
- ID 4: Juno
- ID 5: Vesta
- ID 10: Chiron (уже есть)

**Время:** 2h (интеграция Swiss Ephemeris IDs)

---

### База 4: Арабские точки расширенные

**Структура:**

```
config/
  arabic_parts_extended.yaml
```

**Формулы:**

- Day formula: ASC + X - Y
- Night formula: ASC + Y - X
- Source: Al-Biruni, Bonatti, Lilly

**Время:** 2h (исследование формул)

---

## ☁️ ОБЛАЧНАЯ БАЗА КАРТ (архитектура)

### Проблема:

Пользователь работает с ноутбука и телефона → нужна синхронизация карт

### Решение: Backend + Client Sync

---

### Вариант A: Простой (Firebase/Supabase)

**Stack:**

- **Backend:** Supabase (PostgreSQL + Auth + Storage)
- **Desktop:** Python client (sync on save/load)
- **Mobile:** Flutter app (real-time sync)

**Schema:**

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  created_at TIMESTAMP
);

-- Charts
CREATE TABLE charts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name TEXT,
  birth_date DATE,
  birth_time TIME,
  place TEXT,
  lat FLOAT,
  lon FLOAT,
  timezone TEXT,
  chart_data JSONB,  -- Full calculation result
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Sync
CREATE TABLE sync_log (
  id UUID PRIMARY KEY,
  user_id UUID,
  device_id TEXT,
  chart_id UUID,
  action TEXT,  -- created, updated, deleted
  synced_at TIMESTAMP
);
```

**API:**

```python
# Python client
import supabase

client = supabase.create_client(url, key)

# Save chart
chart = {...}
client.table('charts').insert({
    'user_id': user_id,
    'name': 'John Natal',
    'chart_data': chart
}).execute()

# Load charts
charts = client.table('charts')\
    .select('*')\
    .eq('user_id', user_id)\
    .execute()
```

**Время:** 8-12 часов (интеграция)

**Стоимость:** $0-25/мес (Supabase Free tier: 500MB DB, 2GB bandwidth)

---

### Вариант B: Custom (FastAPI + PostgreSQL)

**Stack:**

- **Backend:** FastAPI + PostgreSQL + Redis (cache)
- **Auth:** JWT tokens
- **Storage:** S3-compatible (Cloudflare R2)
- **Deploy:** Railway / Fly.io / DigitalOcean App Platform

**Структура:**

```
astro-cloud/
  backend/
    main.py           # FastAPI app
    models.py         # SQLAlchemy models
    auth.py           # JWT authentication
    routes/
      charts.py
      sync.py
      users.py

  client/
    sync_client.py    # Python sync client

  mobile/
    (Flutter app)
```

**API Endpoints:**

```python
# FastAPI routes
POST   /api/auth/register
POST   /api/auth/login
GET    /api/charts              # List all charts
POST   /api/charts              # Create chart
GET    /api/charts/{id}         # Get chart
PUT    /api/charts/{id}         # Update chart
DELETE /api/charts/{id}         # Delete chart
POST   /api/sync                # Sync all charts
```

**Sync Logic:**

```python
# Client-side
class ChartSyncClient:
    def sync(self):
        # 1. Get local charts
        local = self.get_local_charts()

        # 2. Get remote charts
        remote = self.api.get_charts()

        # 3. Resolve conflicts (last-write-wins)
        for chart in local:
            if chart.updated_at > remote[chart.id].updated_at:
                self.api.update_chart(chart)

        # 4. Download new charts
        for chart in remote:
            if chart.id not in local:
                self.save_local_chart(chart)
```

**Время:** 20-30 часов (полная реализация)

**Стоимость:** $5-10/мес (Railway/Fly.io)

---

### Вариант C: Hybrid (Local-first)

**Подход:** Local SQLite + Optional cloud backup

**Stack:**

- **Local:** SQLite database (charts.db)
- **Backup:** Optional cloud sync (Dropbox/Google Drive API)
- **No auth:** Files sync via cloud storage

**SQLite Schema:**

```sql
CREATE TABLE charts (
  id TEXT PRIMARY KEY,
  name TEXT,
  birth_date TEXT,
  birth_time TEXT,
  place TEXT,
  chart_data TEXT,  -- JSON
  created_at INTEGER,
  updated_at INTEGER
);

CREATE INDEX idx_name ON charts(name);
CREATE INDEX idx_date ON charts(birth_date);
```

**Sync:**

```python
# Desktop: ~/Dropbox/AstroCharts/charts.db
# Mobile: Read-only access via Dropbox API
```

**Время:** 4-6 часов (SQLite + Dropbox integration)

**Стоимость:** $0 (use existing Dropbox/Drive)

---

### Рекомендация: Вариант C (Local-first)

**Почему:**

1. **Простота:** SQLite = zero setup
2. **Приватность:** Данные локальные, пользователь контролирует
3. **Sync:** Dropbox/Drive делают работу за нас
4. **Mobile:** Flutter Dropbox SDK (read charts.db)
5. **Offline:** Все работает без интернета

**MVP (4 часа):**

```python
# 1. Create ChartDatabase class (1h)
class ChartDatabase:
    def __init__(self, db_path="~/.astro/charts.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def save_chart(self, name, chart_data):
        ...

    def load_chart(self, name):
        ...

    def list_charts(self):
        ...

# 2. Integrate with main.py (1h)
@app.command()
def save(name: str):
    """Save last calculation to database"""
    db = ChartDatabase()
    chart = load_last_calculation()
    db.save_chart(name, chart)

# 3. Add search/filter (1h)
@app.command()
def list():
    """List all saved charts"""
    db = ChartDatabase()
    for chart in db.list_charts():
        print(f"{chart.name} - {chart.birth_date}")

# 4. Dropbox sync (1h - optional)
def sync_to_dropbox():
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    with open(DB_PATH, 'rb') as f:
        dbx.files_upload(f.read(), '/charts.db',
                         mode=WriteMode('overwrite'))
```

---

## 📅 ПРЕДЛАГАЕМЫЙ ПЛАН

### Sprint 1: Output & UX (Week 1, 12h)

**Day 1-2 (6h): Форматы вывода**

- ✅ Compact format (1h)
- ✅ Beautiful table (1h)
- ✅ Color support (1.5h)
- ✅ Summary line (0.5h)
- ✅ Tests + docs (2h)

**Day 3-4 (6h): Новые команды**

- ✅ `aspects` command (1h)
- ✅ `dignities` command (1.5h)
- ✅ `chart-info` command (0.5h)
- ✅ Tests + docs (3h)

**Result:** v0.1.5 - Better UX

---

### Sprint 2: Справочники (Week 2, 12h)

**Day 1 (4h): География**

- ✅ Parse SimpleMaps data (2h)
- ✅ Create cities_world_1000.yaml (1h)
- ✅ Integrate with resolver (1h)

**Day 2 (4h): Звезды**

- ✅ Research Robson + Brady (2h)
- ✅ Create fixed_stars.yaml (1h)
- ✅ Add `--stars` flag to natal (1h)

**Day 3 (4h): Арабские точки**

- ✅ Research formulas (1h)
- ✅ Extend arabic_parts.yaml (1h)
- ✅ Implement logic (2h)

**Result:** v0.1.8 - More data

---

### Sprint 3: Облачная база (Week 3, 8h)

**Day 1 (4h): Local database**

- ✅ ChartDatabase class (1h)
- ✅ CRUD operations (1h)
- ✅ Integrate with CLI (1h)
- ✅ Tests (1h)

**Day 2 (4h): Sync (optional)**

- ❓ Dropbox integration (2h)
- ❓ Auto-sync on save/load (1h)
- ❓ Mobile Flutter POC (1h)

**Result:** v0.2.0 - Chart persistence

---

## 🎯 КРИТЕРИИ УСПЕХА

### Output:

- [x] 4 формата: json, compact, table, summary
- [ ] Цвета в терминале
- [ ] Unicode symbols для планет и знаков

### Функционал:

- [x] 11 команд → 15 команд (+4)
- [ ] Dignities работают
- [ ] Транзиты работают
- [ ] Aspects отдельная команда

### Справочники:

- [ ] 1000+ городов в атласе
- [ ] 15+ фиксированных звезд
- [ ] 15+ арабских точек (от 5)

### База:

- [ ] SQLite charts.db
- [ ] CRUD operations
- [ ] Optional Dropbox sync

---

## ✅ NEXT STEPS

**Сейчас (1 action):**

1. Выбрать что делать первым:
   - A) Output formats (compact, table, colors)
   - B) New commands (aspects, dignities, transits)
   - C) Geography database
   - D) Chart persistence (SQLite)

**Технически:**

- Все quick wins независимые (можно параллельно)
- Приоритет: Output → Commands → Data → Cloud

**Вопрос:**
С чего начинаем? Предлагаю **A) Output formats** (4h, сразу видимый результат)
