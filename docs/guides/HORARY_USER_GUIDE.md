# Horary Astrology Command - User Guide

## Overview

The `horary` command performs traditional horary astrology analysis to answer specific questions using the chart cast for the moment the question is asked.

## Basic Usage

```bash
python main.py horary "YYYY-MM-DD" "HH:MM" "Location" --question-type TYPE
```

### Example

```bash
python main.py horary "2026-02-28" "00:16" "Rehovot, Israel" --question-type lost-item
```

---

## Parameters

### Required

- **date**: Date in format `YYYY-MM-DD`
- **time**: Time in format `HH:MM` (24-hour)
- **place**: Location string (city, country)
- **--question-type**: Type of question being asked

### Question Types

| Type             | Description                  | Quesited House   |
| ---------------- | ---------------------------- | ---------------- |
| `lost-item`      | Will I find my lost item?    | 2 (possessions)  |
| `will-it-happen` | Will this event happen?      | 7 (general)      |
| `timing`         | When will this happen?       | 7 (general)      |
| `relationship`   | Will this relationship work? | 7 (partnerships) |

### Optional

- **--quesited-house N**: Override automatic house selection (1-12)
- **--no-color**: Disable colored output
- **--strict**: Strict location validation
- **--tz TIMEZONE**: Override timezone
- **--lat LATITUDE**: Override latitude
- **--lon LONGITUDE**: Override longitude

---

## Output Structure

### 1. Question Metadata

```
Вопрос: lost-item
Время: 2026-02-28T00:16:00+02:00
Место: Rehovot, IL
Координаты: 31.90°N, 34.81°E
```

### 2. Radicality Check

Traditional validity test:

- ✓ Chart is radical (valid for judgment)
- ASC degree within 3-27° of sign
- Saturn not in 1st or 7th house

**Red flags:**

- ASC < 3° → Question may be premature
- ASC > 27° → Question may be too late
- Saturn in 1st/7th → Judgment blocked

### 3. Void of Course Moon

Checks if Moon makes major aspects before leaving current sign.

**Favorable:** ✓ Луна делает аспекты  
**Unfavorable:** ✗ Луна БЕЗ КУРСА

### 4. Significators

Shows the ruling planets for:

- **Querent** (person asking): 1st house ruler
- **Quesited** (thing/event asked about): Question-specific house ruler

For each significator:

- Planet name
- Sign position
- House placement
- Essential/accidental dignity strength

### 5. Key Aspect

Most important aspect (usually Moon to quesited ruler):

- Aspect type: ☌ ☍ △ □ ✶
- Orb (tightness)
- Motion: APPLYING ✓ or SEPARATING
- Time to perfection (hours/days)

**Applying aspects** (getting tighter) are favorable for "yes" answers.

### 6. Mutual Receptions

Planets in each other's ruling signs create mutual help:

```
✓ Mars ↔ Saturn
  Mars в Aquarius (знак Saturn)
  Saturn в Aries (знак Mars)
```

Strengthens connection between significators.

### 7. Judgment

Traditional synthesis:

- ✓ Positive outcome (will happen, will be found)
- ✗ Negative outcome (won't happen, won't be found)
- Timing estimate (if applicable)
- Notes on ease/difficulty

---

## Interpretation Guide

### For Lost Items (lost-item)

**Favorable indicators:**

- ✅ Chart radical
- ✅ Moon not VOC
- ✅ Applying aspect between Moon and 2nd house ruler
- ✅ Harmonious aspect (trine △, sextile ✶)
- ✅ Mutual reception between significators
- ✅ Strong essential dignity of quesited ruler

**Unfavorable indicators:**

- ❌ Chart not radical
- ❌ Moon VOC
- ❌ Separating aspects only
- ❌ Hard aspects (square □, opposition ☍)
- ❌ No aspects to significators
- ❌ Weak essential dignity

**Timing:**

- Time to perfection = days/hours until item found
- Faster aspects = quicker recovery

### For Will-It-Happen Questions (will-it-happen)

**Yes indicators:**

- Applying aspect between significators
- Mutual reception
- Strong dignities
- Benefic aspects

**No indicators:**

- Separating aspects
- No aspects
- Afflictions
- Weak dignities

---

## Examples

### Example 1: Lost Keys

```bash
python main.py horary "2026-03-15" "14:30" "London, UK" --question-type lost-item
```

**Outcome:**

```
✓ ПРОГНОЗ: Вещь БУДЕТ НАЙДЕНА
Ожидаемое время находки: ~2.3 дня
```

**Why:** Moon trine 2nd house ruler, applying, mutual reception present.

### Example 2: Job Interview Outcome

```bash
python main.py horary "2026-03-20" "09:00" "New York, USA" --question-type will-it-happen
```

**Outcome:**

```
✗ ПРОГНОЗ: Событие НЕ ПРОИЗОЙДЕТ
```

**Why:** Moon VOC, separating aspects, no connection to 10th house ruler.

### Example 3: Relationship Question

```bash
python main.py horary "2026-04-01" "20:15" "Paris, France" --question-type relationship
```

**Outcome:**

```
✓ ПРОГНОЗ: Благоприятный исход
Аспект: Venus △ Mars (applying)
```

**Why:** Significators in harmonious applying aspect with mutual reception.

---

## Traditional Rules Reference

### Chart Radicality (William Lilly)

1. ASC 3-27° within sign
2. Moon not VOC (unless question about isolation/nothing happening)
3. Saturn not in 1st or 7th house
4. Lord of hour matches chart (optional, not implemented)

### Perfection of the Matter

Event will manifest when significators perfect their aspect:

- **Conjunction**: Direct application
- **Other aspects**: Trine, sextile, square, opposition all valid

### Translation of Light (Future)

When a faster planet connects two significators:

- Planet aspects both significators
- Brings the matter to completion
- (Not yet implemented)

### Collection of Light (Future)

When slower planet receives both significators:

- Both planets aspect the collector
- Collector "collects" and unites them
- (Not yet implemented)

---

## Tips

1. **Ask immediately**: Cast chart when question first arises
2. **Be specific**: Clear question gets clear answer
3. **One question**: Don't ask multiple questions in one chart
4. **Check radicality**: Heed warnings about chart validity
5. **Moon importance**: Moon is key co-significator in most questions
6. **Trust the chart**: First chart is the radical chart

---

## Limitations

### Not Implemented Yet

- Part of Fortune and Arabic Parts
- Translation/Collection of light
- Fixed star conjunctions
- Antiscion aspects
- Progressions and directions for timing

### Traditional vs. Modern

- Uses traditional rulerships (Saturn for Aquarius, Mars for Scorpio)
- Outer planets (Uranus, Neptune, Pluto) available but not primary rulers
- House systems: Regiomontanus preferred for horary (use `--house-system`)

---

## Troubleshooting

### "Chart is not radical"

**Cause:** ASC too early/late in sign, or Saturn in angular house  
**Solution:** Question may be premature or too late. Wait or reformulate.

### "Moon VOC"

**Cause:** Moon makes no major aspects before leaving sign  
**Interpretation:** "Nothing will come of the matter" - usually negative

### "No key aspect found"

**Cause:** Moon not aspecting quesited ruler  
**Interpretation:** Lack of connection suggests no outcome or need to check secondary rulers

### Strange timezone results

**Solution:** Use `--tz` to override: `--tz "Europe/London"`

---

## Advanced Usage

### Custom House Selection

```bash
# Ask about 5th house matter (children, creativity)
python main.py horary "2026-03-15" "10:00" "Berlin, Germany" \
    --question-type will-it-happen --quesited-house 5
```

### Debugging

```bash
# Check raw chart data
python main.py natal "2026-03-15" "10:00" "Berlin, Germany" --format json
```

### Comparison

```bash
# First cast horary
python main.py horary "2026-03-15" "10:00" "Berlin, Germany" --question-type lost-item

# Then check aspects separately
python main.py aspects "2026-03-15" "10:00" "Berlin, Germany" --planets "Moon,Saturn"
```

---

## Further Reading

### Books (Traditional Horary)

- **William Lilly** - "Christian Astrology" (1647)
- **John Frawley** - "The Real Astrology" (2000)
- **Alphée Lavoie** - "Lost Horary" (1998)

### Online Resources

- Skyscript.co.uk - Traditional horary articles
- John Frawley's School of Traditional Astrology
- Renaissance Astrology - Christopher Warnock

---

_For technical details, see: [HORARY_IMPLEMENTATION_COMPLETE.md](HORARY_IMPLEMENTATION_COMPLETE.md)_
