# Internationalization (i18n) Guide

Руководство по использованию системы локализации для многоязычной поддержки ошибок, сообщений валидации и текстовых выводов.

## 🌍 Overview (Task 3.1)

Astro Calculator поддерживает многоязычные сообщения через модуль i18n:

| Feature                   | Status      | Description                        |
| ------------------------- | ----------- | ---------------------------------- |
| **English (EN)**          | ✅ Complete | Default language (fallback)        |
| **Russian (RU)**          | ✅ Complete | Full translation of all messages   |
| **Dynamic Loading**       | ✅ Complete | Switch languages at runtime        |
| **Interpolation**         | ✅ Complete | Parameter substitution in messages |
| **Lazy Evaluation**       | ✅ Complete | gettext-style lazy strings         |
| **Validator Integration** | ✅ Complete | Localized validation errors        |

**Test Coverage:** 31 tests passing ✅

## 🚀 Quick Start

### Basic Usage

```python
from src.i18n import get_localizer

# English localizer (default)
loc_en = get_localizer("en")
message = loc_en._("errors.retrograde_not_allowed", planet="Sun")
print(message)
# Output: "Sun cannot be retrograde!"

# Russian localizer
loc_ru = get_localizer("ru")
message = loc_ru._("errors.retrograde_not_allowed", planet="Sun")
print(message)
# Output: "Sun не может быть ретроградным!"
```

### Validator Integration

```python
from src.dsl.validator import AstrologicalValidator

# English validation errors
validator_en = AstrologicalValidator(lang="en")
result = validator_en.validate("Sun.Retrograde == true")
if not result.is_valid:
    print(result.error)
    # Output: "Validation error: Sun cannot be retrograde!"

# Russian validation errors
validator_ru = AstrologicalValidator(lang="ru")
result = validator_ru.validate("Sun.Retrograde == true")
if not result.is_valid:
    print(result.error)
    # Output: "Ошибка валидации: Sun не может быть ретроградным!"
```

## 🔧 Detailed Usage

### Localizer Class

```python
from src.i18n.localizer import Localizer

# Create localizer for specific language
loc = Localizer(lang="en")

# Get simple message
message = loc._("validation.success")
# "Validation successful"

# Get message with parameters
message = loc._("errors.invalid_sign", planet="Mars", sign="InvalidSign")
# "Invalid sign for Mars: InvalidSign"

# Get nested message
message = loc._("formula.evaluation.result", result="True")
# "Evaluation result: True"

# Check if key exists
if loc.has_key("errors.custom_error"):
    message = loc._("errors.custom_error")
```

### Supported Languages

```python
from src.i18n import get_localizer, SUPPORTED_LANGS

# List of supported languages
print(SUPPORTED_LANGS)
# ["en", "ru"]

# Get localizer with fallback
loc = get_localizer("fr")  # French not supported
# Returns English localizer (default fallback)

# Explicit fallback
try:
    loc = get_localizer("fr", fallback="ru")  # Fallback to Russian
except ValueError:
    # Language not supported and no fallback
    pass
```

### Message Catalogs

Message catalogs are stored in `src/i18n/locales/`:

```
src/i18n/locales/
├── en.yaml          # English messages (default)
└── ru.yaml          # Russian messages
```

**en.yaml:**

```yaml
errors:
  retrograde_not_allowed: "{planet} cannot be retrograde!"
  invalid_sign: "Invalid sign for {planet}: {sign}"
  invalid_house: "Invalid house for {planet}: {house}"

validation:
  success: "Validation successful"
  failed: "Validation failed"
  error_prefix: "Validation error: "

formula:
  evaluation:
    result: "Evaluation result: {result}"
    error: "Evaluation error: {error}"
```

**ru.yaml:**

```yaml
errors:
  retrograde_not_allowed: "{planet} не может быть ретроградным!"
  invalid_sign: "Неверный знак для {planet}: {sign}"
  invalid_house: "Неверный дом для {planet}: {house}"

validation:
  success: "Валидация успешна"
  failed: "Валидация не пройдена"
  error_prefix: "Ошибка валидации: "

formula:
  evaluation:
    result: "Результат вычисления: {result}"
    error: "Ошибка вычисления: {error}"
```

## 🎯 Common Use Cases

### 1. Localized Error Messages

```python
from src.i18n import get_localizer

def check_planet_retrograde(planet_name, is_retrograde, lang="en"):
    """Check if planet can be retrograde"""
    loc = get_localizer(lang)

    if planet_name in ["Sun", "Moon"] and is_retrograde:
        error = loc._("errors.retrograde_not_allowed", planet=planet_name)
        return {"valid": False, "error": error}

    return {"valid": True}

# English
result = check_planet_retrograde("Sun", True, lang="en")
print(result["error"])
# "Sun cannot be retrograde!"

# Russian
result = check_planet_retrograde("Sun", True, lang="ru")
print(result["error"])
# "Sun не может быть ретроградным!"
```

### 2. Validation with Localization

```python
from src.dsl.validator import AstrologicalValidator
from src.dsl import parse

# Parse formula once
ast = parse("Sun.Retrograde == true")

# Validate with English messages
validator_en = AstrologicalValidator(lang="en")
result_en = validator_en.validate_ast(ast)
print(f"[EN] {result_en.error}")
# "[EN] Validation error: Sun cannot be retrograde!"

# Validate with Russian messages (same AST)
validator_ru = AstrologicalValidator(lang="ru")
result_ru = validator_ru.validate_ast(ast)
print(f"[RU] {result_ru.error}")
# "[RU] Ошибка валидации: Sun не может быть ретроградным!"
```

### 3. User Preferences

```python
from src.i18n import get_localizer

class UserSettings:
    def __init__(self, user_lang="en"):
        self.lang = user_lang
        self.localizer = get_localizer(user_lang)

    def get_message(self, key, **params):
        return self.localizer._(key, **params)

# User prefers Russian
user = UserSettings(user_lang="ru")
message = user.get_message("validation.success")
print(message)
# "Валидация успешна"

# User prefers English
user = UserSettings(user_lang="en")
message = user.get_message("validation.success")
print(message)
# "Validation successful"
```

### 4. Web API with Accept-Language

```python
from flask import Flask, request
from src.i18n import get_localizer
from src.dsl.validator import AstrologicalValidator

app = Flask(__name__)

@app.route("/validate", methods=["POST"])
def validate_formula():
    formula = request.json.get("formula")

    # Get user's preferred language from Accept-Language header
    lang = request.accept_languages.best_match(["en", "ru"], default="en")

    validator = AstrologicalValidator(lang=lang)
    result = validator.validate(formula)

    return {
        "is_valid": result.is_valid,
        "error": result.error,
        "language": lang
    }

# curl -H "Accept-Language: en" -d '{"formula":"Sun.Retrograde==true"}' /validate
# {"is_valid": false, "error": "Validation error: Sun cannot be retrograde!", "language": "en"}

# curl -H "Accept-Language: ru" -d '{"formula":"Sun.Retrograde==true"}' /validate
# {"is_valid": false, "error": "Ошибка валидации: Sun не может быть ретроградным!", "language": "ru"}
```

### 5. CLI with Language Flag

```python
import typer
from src.i18n import get_localizer
from src.dsl.validator import AstrologicalValidator

app = typer.Typer()

@app.command()
def validate(
    formula: str,
    lang: str = typer.Option("en", help="Language code (en, ru)")
):
    """Validate DSL formula with localized messages"""
    loc = get_localizer(lang)
    validator = AstrologicalValidator(lang=lang)

    result = validator.validate(formula)

    if result.is_valid:
        typer.echo(loc._("validation.success"))
    else:
        typer.echo(result.error, err=True)
        raise typer.Exit(code=1)

# python cli.py validate "Sun.Retrograde == true" --lang=en
# Validation error: Sun cannot be retrograde!

# python cli.py validate "Sun.Retrograde == true" --lang=ru
# Ошибка валидации: Sun не может быть ретроградным!
```

## 🧩 Advanced Features

### Lazy Translation (gettext-style)

```python
from src.i18n.localizer import LazyString, Localizer

# Create lazy string (not translated yet)
lazy_msg = LazyString("errors.retrograde_not_allowed", planet="Sun")

# Translation happens when string is used
print(str(lazy_msg))  # Triggers translation

# Useful for deferred translation
class ValidationRule:
    def __init__(self):
        # Store lazy string (localizer chosen later)
        self.error_message = LazyString("errors.retrograde_not_allowed", planet="Sun")

    def get_error(self, lang="en"):
        # Translate when needed
        loc = Localizer(lang)
        return self.error_message.resolve(loc)
```

### Nested Message Keys

```python
from src.i18n import get_localizer

loc = get_localizer("en")

# Access nested keys with dot notation
message = loc._("formula.evaluation.result", result="True")
# "Evaluation result: True"

message = loc._("formula.evaluation.error", error="Division by zero")
# "Evaluation error: Division by zero"

# Or with dictionary-style access
messages_catalog = loc.messages
result_msg = messages_catalog["formula"]["evaluation"]["result"]
```

### Custom Message Catalogs

```yaml
# src/i18n/locales/custom_en.yaml
custom:
  welcome: "Welcome to Astro Calculator!"
  goodbye: "Goodbye, {username}!"

planet_names:
  sun: "The Sun"
  moon: "The Moon"
  mercury: "Mercury"

house_names:
  1: "First House (Ascendant)"
  10: "Tenth House (Midheaven)"
```

```python
from src.i18n.localizer import Localizer

# Load custom catalog
loc = Localizer(lang="en")  # Automatically loads en.yaml

# Access custom messages
welcome = loc._("custom.welcome")
# "Welcome to Astro Calculator!"

goodbye = loc._("custom.goodbye", username="Alice")
# "Goodbye, Alice!"

sun_name = loc._("planet_names.sun")
# "The Sun"
```

### Pluralization

```python
# en.yaml
counts:
  planet_count: "{count} planet(s)"
  planet_count_zero: "no planets"
  planet_count_one: "one planet"
  planet_count_many: "{count} planets"
```

```python
from src.i18n import get_localizer

loc = get_localizer("en")

def format_planet_count(count):
    if count == 0:
        return loc._("counts.planet_count_zero")
    elif count == 1:
        return loc._("counts.planet_count_one")
    else:
        return loc._("counts.planet_count_many", count=count)

print(format_planet_count(0))   # "no planets"
print(format_planet_count(1))   # "one planet"
print(format_planet_count(10))  # "10 planets"
```

## 🛠️ Implementation Details

### Directory Structure

```
src/i18n/
├── __init__.py              # Module exports
├── localizer.py             # Localizer class
└── locales/
    ├── en.yaml              # English messages
    └── ru.yaml              # Russian messages
```

### Localizer Class API

```python
class Localizer:
    """Manages message translations"""

    def __init__(self, lang: str = "en"):
        """Initialize localizer with language code"""

    def _(self, key: str, **params) -> str:
        """Translate message with parameters"""

    def has_key(self, key: str) -> bool:
        """Check if translation key exists"""

    @property
    def lang(self) -> str:
        """Get current language code"""

    @property
    def messages(self) -> dict:
        """Get all messages as dictionary"""
```

### Global Function API

```python
# src/i18n/__init__.py

def get_localizer(lang: str = "en") -> Localizer:
    """Get localizer instance for language"""

SUPPORTED_LANGS = ["en", "ru"]  # List of supported languages
```

### Validator Integration

```python
# src/dsl/validator.py

class AstrologicalValidator:
    def __init__(self, lang: str = "en"):
        """Initialize validator with language"""
        self.localizer = get_localizer(lang)
        self.lang = lang

    def _error(self, key: str, **params) -> str:
        """Get localized error message"""
        error_msg = self.localizer._(key, **params)
        prefix = self.localizer._("validation.error_prefix")
        return f"{prefix}{error_msg}"
```

## 🧪 Testing

```python
# tests/test_i18n_integration.py
import pytest
from src.i18n import get_localizer
from src.dsl.validator import AstrologicalValidator

def test_english_localization():
    """Test English messages"""
    loc = get_localizer("en")
    message = loc._("errors.retrograde_not_allowed", planet="Sun")
    assert message == "Sun cannot be retrograde!"

def test_russian_localization():
    """Test Russian messages"""
    loc = get_localizer("ru")
    message = loc._("errors.retrograde_not_allowed", planet="Sun")
    assert message == "Sun не может быть ретроградным!"

def test_validator_localization():
    """Test validator with different languages"""
    # English validator
    validator_en = AstrologicalValidator(lang="en")
    result_en = validator_en.validate("Sun.Retrograde == true")
    assert "Sun cannot be retrograde!" in result_en.error

    # Russian validator
    validator_ru = AstrologicalValidator(lang="ru")
    result_ru = validator_ru.validate("Sun.Retrograde == true")
    assert "Sun не может быть ретроградным!" in result_ru.error

def test_fallback_to_english():
    """Test fallback when language not supported"""
    loc = get_localizer("fr")  # French not supported
    message = loc._("validation.success")
    assert message == "Validation successful"  # English fallback

def test_missing_key():
    """Test missing translation key"""
    loc = get_localizer("en")
    message = loc._("nonexistent.key")
    assert message in ["nonexistent.key", "[missing: nonexistent.key]"]
```

## 📚 Best Practices

### 1. Use Consistent Key Naming

```python
# ✅ GOOD: Hierarchical, descriptive keys
"errors.retrograde_not_allowed"
"errors.invalid_sign"
"validation.success"
"formula.evaluation.result"

# ❌ BAD: Flat, unclear keys
"error1"
"msg2"
"text_abc"
```

### 2. Parameter Names Should Be Clear

```python
# ✅ GOOD: Clear parameter names
loc._("errors.invalid_sign", planet="Mars", sign="InvalidSign")
# "Invalid sign for Mars: InvalidSign"

# ❌ BAD: Unclear parameter names
loc._("errors.invalid_sign", p="Mars", s="InvalidSign")
```

### 3. Keep Messages Short and Focused

```yaml
# ✅ GOOD: Short, focused messages
errors:
  retrograde_not_allowed: "{planet} cannot be retrograde!"
  invalid_house: "Invalid house: {house}"

# ❌ BAD: Long, complex messages
errors:
  retrograde_error: "An error occurred because {planet} was marked as retrograde, but according to astronomical rules, {planet} cannot be in retrograde motion. Please check your data."
```

### 4. Provide All Translations

```yaml
# ✅ GOOD: Both languages have same keys
# en.yaml
errors:
  retrograde_not_allowed: "{planet} cannot be retrograde!"
  invalid_sign: "Invalid sign: {sign}"

# ru.yaml
errors:
  retrograde_not_allowed: "{planet} не может быть ретроградным!"
  invalid_sign: "Неверный знак: {sign}"

# ❌ BAD: Missing translations
# ru.yaml (missing invalid_sign)
errors:
  retrograde_not_allowed: "{planet} не может быть ретроградным!"
```

### 5. Use Localizer in Classes

```python
# ✅ GOOD: Store localizer as instance variable
class MyValidator:
    def __init__(self, lang="en"):
        self.localizer = get_localizer(lang)

    def validate(self, data):
        error = self.localizer._("errors.custom", data=data)
        return error

# ❌ BAD: Create localizer every time
class MyValidator:
    def validate(self, data, lang="en"):
        # Creates new localizer on every call!
        localizer = get_localizer(lang)
        error = localizer._("errors.custom", data=data)
        return error
```

## 🌐 Adding New Languages

### Step 1: Create Message Catalog

```bash
# Create new language file
cp src/i18n/locales/en.yaml src/i18n/locales/fr.yaml
```

### Step 2: Translate Messages

```yaml
# src/i18n/locales/fr.yaml
errors:
  retrograde_not_allowed: "{planet} ne peut pas être rétrograde!"
  invalid_sign: "Signe invalide pour {planet}: {sign}"

validation:
  success: "Validation réussie"
  failed: "Échec de la validation"
```

### Step 3: Register Language

```python
# src/i18n/__init__.py

SUPPORTED_LANGS = ["en", "ru", "fr"]  # Add new language
```

### Step 4: Test

```python
# tests/test_i18n_french.py
from src.i18n import get_localizer

def test_french_localization():
    loc = get_localizer("fr")
    message = loc._("errors.retrograde_not_allowed", planet="Sun")
    assert message == "Sun ne peut pas être rétrograde!"
```

## 📊 Current Message Catalog

### English (en.yaml)

- `errors.*` - Error messages (10+ keys)
  - `retrograde_not_allowed`
  - `invalid_sign`
  - `invalid_house`
  - `invalid_aspect`

- `validation.*` - Validation messages
  - `success`
  - `failed`
  - `error_prefix`

- `formula.*` - Formula evaluation messages
  - `evaluation.result`
  - `evaluation.error`

### Russian (ru.yaml)

- Complete 1:1 translation of English catalog
- 100% coverage of all keys
- Culturally appropriate wording

## 📚 See Also

- [Task 3.1 Completion Report](../../docs/TASK_3.1_LOCALIZATION_COMPLETED.md)
- [i18n Implementation](../i18n/)
- [Validator with i18n](../dsl/validator.py)
- [i18n Tests](../../tests/test_i18n_integration.py)

---

**Internationalization completed in Task 3.1** | EN/RU support, 31 tests passing ✅
