# Comparative Charts Feature

## Overview

The `comparative` command calculates natal/astrological charts for the same date and time across multiple cities, enabling comparative astrology analysis (e.g., relocation astrology).

## Usage

### From Command Line (CLI cities)

```bash
python main.py comparative 1985-01-15 14:30 --chart-type natal Moscow London Tokyo Sydney
```

### From File (One city per line)

```bash
python main.py comparative 1985-01-15 14:30 --chart-type natal --cities-file cities.txt
```

### File Format

`cities.txt`:

```
Moscow
London
Tokyo
Sydney
New York
# Comments start with #
```

## Options

- **DATE**: Birth date (13+ formats supported: ISO, EU, US, compact, text)
- **TIME**: Birth time (HH:MM, HH:MM:SS)
- **--chart-type**: Type of chart (default: `natal`)
  - `natal` - Natal birth chart
  - `transit` - Transit chart
  - `solar` - Solar return chart
  - `relocation` - Relocation chart (same natal chart, different cities)
- **--cities-file**: File path with city names (one per line)
- **--tz**: Override timezone for all cities (optional)

## Output

JSON structure with all charts and errors:

```json
{
  "comparative_data": {
    "chart_type": "natal",
    "date": "1985-01-15",
    "time": "14:30",
    "cities_count": 5,
    "successful": 5,
    "failed": 0,
    "timestamp": "2026-01-15T23:16:11"
  },
  "charts": [
    {
      "place": "Moscow",
      "chart_type": "natal",
      "input_metadata": {
        "confidence": 0.95,
        "timezone": "Europe/Moscow",
        "local_datetime": "1985-01-15T14:30:00+03:00",
        "utc_datetime": "1985-01-15T11:30:00+00:00",
        "coordinates": {"lat": 55.7558, "lon": 37.6173},
        "place": {"name": "Moscow", "country": "RU"},
        "warnings": []
      },
      "facts": [...planets, houses...],
      "signals": [...astrological signals...],
      "decisions": [...interpretations...],
      "planets": {...raw longitudes...},
      "houses": [...12 house cusps...]
    },
    ...more cities...
  ],
  "errors": [
    {"place": "InvalidCity", "error": "City not found: Invalid location"}
  ]
}
```

## Features

- **Graceful Error Handling**: If one city fails, others are still calculated
- **Flexible Input**: CLI arguments OR file input
- **Multi-City Comparison**: Calculate same birth time across unlimited cities
- **All Chart Types**: Supports natal, transit, solar, and relocation charts
- **Rich Metadata**: Timezone, coordinates, DST info, confidence scores
- **Astrological Interpretation**: Facts, signals, and decisions for each location

## Implementation

### Modules

- **comparative_charts.py**: Core logic
  - `load_cities_from_file(filepath)`: Load cities from text file
  - `calculate_chart(date, time, place, chart_type, ...)`: Single city calculation
  - `comparative_charts(date, time, cities, chart_type, ...)`: Multi-city wrapper

### Integration Points

- Uses existing `normalize_input()` for date/time/timezone normalization
- Uses existing `natal_calculation()` for astrological calculations
- Uses existing `interpretation_layer` for facts/signals/decisions

### Testing

- 4 integration tests added
- CLI cities input ✅
- File input ✅
- Different chart types ✅
- Partial failure handling ✅
- All 44 tests passing (40 existing + 4 new)

## Examples

### Example 1: Compare birth chart interpretation across cities

```bash
python main.py comparative 1985-01-15 14:30 --chart-type natal \
  Moscow London Tokyo Sydney "New York"
```

### Example 2: Relocation astrology (same chart, different cities)

```bash
python main.py comparative 1985-01-15 14:30 --chart-type relocation \
  --cities-file cities.txt
```

### Example 3: With timezone override

```bash
python main.py comparative 1985-01-15 14:30 --chart-type natal \
  --tz "UTC" Moscow London
```

## Future Enhancements

- Comparative aspects between charts
- Composite chart calculation
- Synastry (relationship) charts
- Chart comparison matrix
- Visual output (SVG/PNG)
- CSV export for statistical analysis
