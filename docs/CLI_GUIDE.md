# CLI Verbosity Modes Guide

Руководство по использованию режимов вывода CLI (--verbose, --quiet, normal) для различных сценариев использования.

## 📊 Overview (Task 3.3)

Astro Calculator поддерживает 3 уровня детализации вывода:

| Mode        | Flag        | Use Case                      | Output Level            |
| ----------- | ----------- | ----------------------------- | ----------------------- |
| **QUIET**   | `--quiet`   | Automation, scripting, piping | Minimal (results only)  |
| **NORMAL**  | (default)   | Interactive use, learning     | Concise, readable       |
| **VERBOSE** | `--verbose` | Debugging, understanding      | Detailed, comprehensive |

## 🚀 Quick Start

### Quiet Mode (Automation)

```bash
# Только результат (True/False)
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn" --quiet
# Output: True

# JSON без форматирования (компактный)
python main.py natal 1982-01-08 12:00 "Tel Aviv" --quiet
# Output: {"planets":{"Sun":{"sign":"Capricorn",...}},...}
```

### Normal Mode (Default)

```bash
# Читаемый вывод с минимальным контекстом
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn"
# Output: ✓ Sun.Sign == Capricorn → True

# Pretty-printed JSON
python main.py natal 1982-01-08 12:00 "Tel Aviv"
# Output:
# {
#   "planets": {
#     "Sun": {
#       "sign": "Capricorn",
#       ...
#     }
#   }
# }
```

### Verbose Mode (Debugging)

```bash
# Детальный вывод с пошаговым процессом
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn" --verbose
# Output:
# Step 1: Normalizing input...
#   Date: 1982-01-08
#   Time: 12:00
#   UTC: 1982-01-08 10:00:00+00:00
#   Location: Tel Aviv
#   Coordinates: 32.0853, 34.7818
#
# Step 2: Calculating planetary positions...
#   Planets calculated: 11
#
# Step 3: Interpreting chart...
#   Facts extracted: 188
#   Signals generated: 1
#   Decisions made: 1
#
# Converting chart data for DSL evaluator...
# Evaluating formula: Sun.Sign == Capricorn
#
# ============================================================
# DSL Formula Evaluation
# ============================================================
#
# Formula: Sun.Sign == Capricorn
# Result:  ✓ True
#
# Chart Data:
#   Planets: 10
#   Houses: 12
#   Aspects: 0
#
#   Planet Positions:
#     Sun        → Capricorn     17.80° (House 9)
#     Moon       → Gemini        28.11° (House 2)
#     Mercury    → Aquarius       4.19° (House 10)
#     ...
# ============================================================
```

## 🎯 Use Cases

### 1. Scripting & Automation (--quiet)

```bash
#!/bin/bash
# check_compatibility.sh

PERSON1_CHART="1982-01-08 12:00 Tel_Aviv"
PERSON2_CHART="1990-05-15 08:30 Moscow"

# Получить только результаты для обработки
SUN_COMPATIBLE=$(python main.py natal $PERSON1_CHART --check="Sun.Sign == Capricorn" --quiet)
MOON_COMPATIBLE=$(python main.py natal $PERSON2_CHART --check="Moon.Sign == Taurus" --quiet)

if [ "$SUN_COMPATIBLE" == "True" ] && [ "$MOON_COMPATIBLE" == "True" ]; then
    echo "Compatible!"
else
    echo "Not compatible"
fi
```

### 2. JSON Processing (--quiet)

```bash
# Получить карту в компактном JSON и обработать с jq
python main.py natal 1982-01-08 12:00 "Tel Aviv" --quiet | jq '.planets.Sun.sign'
# Output: "Capricorn"

# Batch processing
for date in 1982-01-08 1990-05-15 1995-12-20; do
    python main.py natal $date 12:00 "Tel Aviv" --quiet | \
        jq -r '.planets.Sun.sign'
done
```

### 3. Data Pipelines (--quiet)

```python
# pipeline.py
import subprocess
import json

def get_chart_data(birthdate, time, location):
    """Get chart data for processing"""
    cmd = [
        "python", "main.py", "natal",
        birthdate, time, location,
        "--quiet"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# Process multiple charts
charts = []
for person in people:
    chart = get_chart_data(person['date'], person['time'], person['location'])
    charts.append(chart)
```

### 4. Learning & Exploration (normal mode)

```bash
# Понятный вывод для изучения формул
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Sun.Sign == Capricorn"
# ✓ Sun.Sign == Capricorn → True

# Попробовать разные формулы
python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="Moon.Sign IN [Gemini, Libra, Aquarius]"
# ✓ Moon.Sign IN [Gemini, Libra, Aquarius] → True

python main.py natal 1982-01-08 12:00 "Tel Aviv" --check="COUNT(Planet WHERE Retrograde == true) > 2"
# ✓ COUNT(Planet WHERE Retrograde == true) > 2 → False (1 retrograde planets)
```

### 5. Debugging & Troubleshooting (--verbose)

```bash
# Понять, что происходит на каждом шаге
python main.py natal invalid-date 12:00 "Unknown City" --verbose
# Output:
# Step 1: Normalizing input...
#   ERROR: Failed to parse date: invalid-date
#   [Detailed error message and traceback]

# Проверить, правильно ли интерпретируется локация
python main.py natal 1982-01-08 12:00 "Tel Aviv" --verbose
# Output:
# Step 1: Normalizing input...
#   Date: 1982-01-08
#   Time: 12:00
#   Timezone: Asia/Jerusalem
#   UTC: 1982-01-08 10:00:00+00:00  ← Проверка конвертации
#   Location: Tel Aviv
#   Coordinates: 32.0853, 34.7818  ← Проверка координат
```

### 6. Understanding DSL Evaluation (--verbose)

```bash
# Детальный вывод DSL формулы
python main.py natal 1982-01-08 12:00 "Tel Aviv" \
    --check="Sun.Sign == Capricorn AND Moon.House == 2" \
    --verbose

# Output:
# ...
# ============================================================
# DSL Formula Evaluation
# ============================================================
#
# Formula: Sun.Sign == Capricorn AND Moon.House == 2
# Result:  ✓ True
#
# Chart Data:
#   Planets: 10
#   Houses: 12
#   Aspects: 0
#
#   Planet Positions:
#     Sun        → Capricorn     17.80° (House 9)   ← Capricorn ✅
#     Moon       → Gemini        28.11° (House 2)   ← House 2 ✅
#     ...
#
# Evaluation Steps:
#   1. Sun.Sign == Capricorn → True
#   2. Moon.House == 2 → True
#   3. True AND True → True
# ============================================================
```

## 🔧 Implementation Details

### Output Levels (OutputLevel Enum)

```python
from src.cli.output import OutputLevel

class OutputLevel(IntEnum):
    QUIET = 0    # Minimal output
    NORMAL = 1   # Default output
    VERBOSE = 2  # Detailed output
```

### CLIOutput Class

```python
from src.cli.output import CLIOutput, OutputLevel

# Creating output instance
out = CLIOutput(level=OutputLevel.VERBOSE)

# Message filtering methods
out.quiet("Always shown")      # All levels
out.success("Success!")        # NORMAL + VERBOSE
out.info("Information")        # NORMAL + VERBOSE
out.verbose("Details")         # VERBOSE only
out.error("Error!", err=True)  # All levels, stderr

# Formatting
out.section("Main Section")    # VERBOSE only
out.subsection("Subsection")   # VERBOSE only
out.bullet("Item")             # VERBOSE only
```

### Global Configuration

```python
from src.cli import configure_output, get_output, set_output_level

# Configure based on CLI flags
out = configure_output(verbose=True, quiet=False)
# Returns: CLIOutput(level=VERBOSE)

out = configure_output(verbose=False, quiet=True)
# Returns: CLIOutput(level=QUIET)

out = configure_output(verbose=False, quiet=False)
# Returns: CLIOutput(level=NORMAL)

# Get global instance
out = get_output()

# Change level dynamically
from src.cli.output import OutputLevel
set_output_level(OutputLevel.VERBOSE)
```

### JSON Formatting

```python
from src.cli.output import CLIOutput, OutputLevel

# Quiet mode: compact JSON
out = CLIOutput(level=OutputLevel.QUIET)
out.json_result({"planets": {"Sun": {"sign": "Aries"}}})
# {"planets":{"Sun":{"sign":"Aries"}}}

# Normal/Verbose mode: pretty-printed JSON
out = CLIOutput(level=OutputLevel.NORMAL)
out.json_result({"planets": {"Sun": {"sign": "Aries"}}})
# {
#   "planets": {
#     "Sun": {
#       "sign": "Aries"
#     }
#   }
# }
```

### DSL Result Formatting

```python
from src.cli.output import CLIOutput, OutputLevel

chart_data = {
    "planets": {"Sun": {"Sign": "Capricorn", "Degree": 17.80, "House": 9}},
    "houses": {...},
}

# Quiet mode
out = CLIOutput(level=OutputLevel.QUIET)
formatted = out.format_dsl_result("Sun.Sign == Capricorn", True, chart_data)
# "True"

# Normal mode
out = CLIOutput(level=OutputLevel.NORMAL)
formatted = out.format_dsl_result("Sun.Sign == Capricorn", True, chart_data)
# "✓ Sun.Sign == Capricorn → True"

# Verbose mode
out = CLIOutput(level=OutputLevel.VERBOSE)
formatted = out.format_dsl_result("Sun.Sign == Capricorn", True, chart_data)
# ============================================================
# DSL Formula Evaluation
# ============================================================
#
# Formula: Sun.Sign == Capricorn
# Result:  ✓ True
#
# Chart Data:
#   Planets: 10
#   Houses: 12
#   Aspects: 0
#
#   Planet Positions:
#     Sun        → Capricorn     17.80° (House 9)
#     ...
# ============================================================
```

## 📊 Output Examples

### Validation Results

**Quiet Mode:**

```bash
$ python main.py natal 1982-01-08 12:00 "Tel Aviv" --validate --quiet
True
```

**Normal Mode:**

```bash
$ python main.py natal 1982-01-08 12:00 "Tel Aviv" --validate
✓ Chart is valid
```

**Verbose Mode:**

```bash
$ python main.py natal 1982-01-08 12:00 "Tel Aviv" --validate --verbose
============================================================
Chart Validation
============================================================

Validating chart...

All Rules:
  ✓ rule_sun_not_retrograde: Sun is not retrograde
  ✓ rule_planets_in _houses: All planets in houses
  ✓ rule_valid_aspects: Valid aspect orbs

Result: ✓ Valid

============================================================
```

### Error Handling

**Quiet Mode:**

```bash
$ python main.py natal invalid-date 12:00 "Tel Aviv" --quiet
ERROR: Failed to parse date: invalid-date
```

**Normal Mode:**

```bash
$ python main.py natal invalid-date 12:00 "Tel Aviv"
ERROR: Failed to parse date: invalid-date
Expected format: YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY
```

**Verbose Mode:**

```bash
$ python main.py natal invalid-date 12:00 "Tel Aviv" --verbose
Step 1: Normalizing input...
  ERROR: Failed to parse date: invalid-date

Expected format: YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY

Traceback (most recent call last):
  File "main.py", line 156, in natal
    normalized = normalize_input(...)
  File "input_pipeline/parser_datetime.py", line 45, in parse_date
    raise ValueError(f"Failed to parse date: {date_str}")
ValueError: Failed to parse date: invalid-date
```

## 🎨 Best Practices

### 1. Choose the Right Mode

```bash
# ❌ ПЛОХО: Verbose для скриптов (слишком много вывода)
result=$(python main.py natal ... --verbose | grep "Result")

# ✅ ХОРОШО: Quiet для скриптов
result=$(python main.py natal ... --check="Sun.Sign == Aries" --quiet)

# ❌ ПЛОХО: Quiet для обучения (непонятно)
python main.py natal ... --check="complex formula" --quiet
# Output: False  ← Почему?

# ✅ ХОРОШО: Verbose для обучения
python main.py natal ... --check="complex formula" --verbose
# Output: Детальная информация о каждом шаге
```

### 2. Piping & Redirection

```bash
# Quiet mode для piping
python main.py natal 1982-01-08 12:00 "Tel Aviv" --quiet | jq

# Normal mode для файлов (читаемость)
python main.py natal 1982-01-08 12:00 "Tel Aviv" > chart.txt

# Verbose mode для логов
python main.py natal 1982-01-08 12:00 "Tel Aviv" --verbose > debug.log 2>&1
```

### 3. Error Handling

```bash
# Quiet mode: проверить код возврата
python main.py natal invalid-date ... --quiet
if [ $? -ne 0 ]; then
    echo "Error occurred"
fi

# Verbose mode: получить детальную информацию об ошибке
python main.py natal invalid-date ... --verbose 2> errors.log
```

### 4. Programmatic Usage

```python
import subprocess
import sys

def run_chart_cli(date, time, location, formula=None, mode="normal"):
    """Run CLI with specified verbosity mode"""
    cmd = ["python", "main.py", "natal", date, time, location]

    if formula:
        cmd.extend(["--check", formula])

    if mode == "quiet":
        cmd.append("--quiet")
    elif mode == "verbose":
        cmd.append("--verbose")
    # Normal mode = no flag

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        return None

# Automation: quiet mode
result = run_chart_cli("1982-01-08", "12:00", "Tel Aviv",
                       formula="Sun.Sign == Capricorn",
                       mode="quiet")
if result == "True":
    print("Match!")

# Debugging: verbose mode
result = run_chart_cli("invalid", "12:00", "Tel Aviv",
                       mode="verbose")
# Detailed error output
```

## 🧪 Testing

```python
# tests/test_cli_modes.py
import subprocess

def test_quiet_mode():
    """Quiet mode returns only result"""
    result = subprocess.run(
        ["python", "main.py", "natal", "1982-01-08", "12:00", "Tel Aviv",
         "--check=Sun.Sign == Capricorn", "--quiet"],
        capture_output=True,
        text=True
    )
    assert result.stdout.strip() == "True"
    assert "Step 1" not in result.stdout  # No verbose output

def test_normal_mode():
    """Normal mode returns formatted result"""
    result = subprocess.run(
        ["python", "main.py", "natal", "1982-01-08", "12:00", "Tel Aviv",
         "--check=Sun.Sign == Capricorn"],
        capture_output=True,
        text=True
    )
    assert "✓ Sun.Sign == Capricorn → True" in result.stdout
    assert "Step 1" not in result.stdout  # No verbose output

def test_verbose_mode():
    """Verbose mode returns detailed output"""
    result = subprocess.run(
        ["python", "main.py", "natal", "1982-01-08", "12:00", "Tel Aviv",
         "--check=Sun.Sign == Capricorn", "--verbose"],
        capture_output=True,
        text=True
    )
    assert "Step 1: Normalizing input" in result.stdout
    assert "Step 2: Calculating" in result.stdout
    assert "Planet Positions:" in result.stdout
```

## 📚 See Also

- [Task 3.3 Completion Report](../../docs/TASK_3.3_CLI_MODES_COMPLETED.md)
- [CLI Output Implementation](../cli/output.py)
- [CLI Tests](../../tests/test_cli_output.py)
- [Integration Tests](../../tests/test_cli_integration.py)

---

**CLI verbosity modes completed in Task 3.3** | 3 modes, 35 tests passing ✅
