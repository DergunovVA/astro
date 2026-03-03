"""
Output formatters for different user personas.
Transforms JSON facts into human-readable formats.
"""

from typing import Any
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)


def format_summary(data: dict[str, Any], lang: str = "ru") -> str:
    """
    Brief human-readable summary for regular users.
    Focuses on: Sun, Moon, Ascendant, top 5 aspects.

    Args:
        data: Natal chart data from calculate_natal_with_facts()
        lang: Language code (ru or en)

    Returns:
        Formatted text summary
    """
    facts = data.get("facts", [])
    chart_info = data.get("input_metadata", {})
    place_info = chart_info.get("place", {})

    # Extract key positions
    sun_sign = _find_fact(facts, "Sun", "planet_in_sign")
    moon_sign = _find_fact(facts, "Moon", "planet_in_sign")
    asc_sign = _find_fact(facts, "Ascendant", "planet_in_sign")
    # Extract dignities
    sun_dignity = _find_fact(facts, "Sun", "total_dignity")
    moon_dignity = _find_fact(facts, "Moon", "total_dignity")

    # Extract top aspects (tight orbs, major only)
    aspects = [
        f
        for f in facts
        if f["type"] == "aspect" and f.get("details", {}).get("orb", 10) < 3
    ]
    aspects_sorted = sorted(aspects, key=lambda x: x.get("details", {}).get("orb", 10))[
        :5
    ]

    # Build output
    output = []
    output.append("=" * 65)
    output.append(
        "           📜 КРАТКИЙ НАТАЛЬНЫЙ ОТЧЁТ"
        if lang == "ru"
        else "           📜 NATAL CHART SUMMARY"
    )
    output.append("=" * 65)
    output.append("")
    output.append(f"🗓  Дата: {chart_info.get('local_datetime', '?')}")
    output.append(
        f"📍 Место: {place_info.get('name', '?')}, {place_info.get('country', '?')}"
    )
    output.append("")
    output.append("=" * 65)
    output.append("           🌟 ОСНОВНЫЕ ПОЗИЦИИ")
    output.append("=" * 65)
    output.append("")

    # Sun
    if sun_sign:
        house = _find_fact(facts, "Sun", "house")
        house_num = house.get("details", {}).get("house", "?") if house else "?"
        strength = _dignity_stars(sun_dignity)
        output.append(
            f"☉  СОЛНЦЕ в знаке {sun_sign.get('value', '?')} ({house_num} дом)"
        )
        sun_dig_value = sun_dignity.get("value", "?") if sun_dignity else "?"
        output.append(f"   Сила: {sun_dig_value} {strength}")
        output.append(f"   {_sun_interpretation(sun_sign.get('value', ''), lang)}")
        output.append("")

    # Moon
    if moon_sign:
        house = _find_fact(facts, "Moon", "house")
        house_num = house.get("details", {}).get("house", "?") if house else "?"
        strength = _dignity_stars(moon_dignity)
        output.append(
            f"☽  ЛУНА в знаке {moon_sign.get('value', '?')} ({house_num} дом)"
        )
        moon_dig_value = moon_dignity.get("value", "?") if moon_dignity else "?"
        output.append(f"   Сила: {moon_dig_value} {strength}")
        output.append(f"   {_moon_interpretation(moon_sign.get('value', ''), lang)}")
        output.append("")

    # Ascendant
    if asc_sign:
        output.append(f"⬆️  АСЦЕНДЕНТ в знаке {asc_sign.get('value', '?')}")
        output.append(f"   {_asc_interpretation(asc_sign.get('value', ''), lang)}")
        output.append("")

    output.append("=" * 65)
    output.append("           ✨ ТОП-5 АСПЕКТОВ (ТОЧНЫЕ)")
    output.append("=" * 65)
    output.append("")

    if not aspects_sorted:
        output.append("   Нет точных аспектов (орбис < 3°)")
    else:
        for i, asp in enumerate(aspects_sorted, 1):
            details = asp.get("details", {})
            p1 = _planet_symbol(details.get("from", "?"))
            p2 = _planet_symbol(details.get("to", "?"))
            aspect_type = details.get("aspect", "?")
            aspect_symbol = _aspect_symbol(aspect_type)
            orb = details.get("orb", 0)
            motion = details.get("motion", "?")
            motion_emoji = (
                "⚡"
                if motion == "applying"
                else "📉"
                if motion == "separating"
                else "⏸"
            )

            quality = _aspect_quality(aspect_type, lang)

            output.append(
                f"{i}. {p1} {aspect_symbol} {p2} (орбис {orb:.2f}°) {motion_emoji}"
            )
            output.append(f"   {quality}")
            output.append("")

    output.append("=" * 65)
    output.append("           💡 КЛЮЧЕВЫЕ ПАТТЕРНЫ")
    output.append("=" * 65)
    output.append("")

    # Extract psychological patterns
    psych_facts = [f for f in facts if f["type"] == "psychological_signal"]
    if psych_facts:
        for pf in psych_facts[:3]:  # Top 3 patterns
            output.append(f"• {pf.get('value', '?')}")
            if pf.get("details", {}).get("description"):
                output.append(f"  {pf['details']['description']}")
            output.append("")
    else:
        output.append("   (Психологические паттерны не рассчитаны)")
        output.append("")

    output.append("=" * 65)
    output.append("")
    output.append("💡 Для полного отчёта используйте:")
    output.append("   python main.py natal <дата> <время> <место> --psychological")
    output.append("")
    output.append("📊 Для таблиц аспектов:")
    output.append("   python main.py natal <дата> <время> <место> --format=table")
    output.append("")

    return "\n".join(output)


def _find_fact(facts: list, obj: str, fact_type: str) -> dict | None:
    """Find specific fact for object."""
    for f in facts:
        if f.get("object") == obj and f.get("type") == fact_type:
            return f
    return None


def _dignity_stars(dignity_fact: dict | None) -> str:
    """Convert dignity score to star rating."""
    if not dignity_fact:
        return ""

    score = dignity_fact.get("details", {}).get("total_score", 0)

    if score >= 10:
        return "★★★★★"
    elif score >= 5:
        return "★★★★☆"
    elif score >= 0:
        return "★★★☆☆"
    elif score >= -5:
        return "★★☆☆☆"
    else:
        return "★☆☆☆☆"


def _planet_symbol(name: str) -> str:
    """Get planet symbol."""
    symbols = {
        "Sun": "☉",
        "Moon": "☽",
        "Mercury": "☿",
        "Venus": "♀",
        "Mars": "♂",
        "Jupiter": "♃",
        "Saturn": "♄",
        "Uranus": "♅",
        "Neptune": "♆",
        "Pluto": "♇",
        "Ascendant": "ASC",
        "Midheaven": "MC",
        "North_Node": "☊",
        "Chiron": "⚷",
        "Proserpina": "⚸",  # Hypothetical trans-Plutonian (Swiss Ephemeris)
    }
    return symbols.get(name, name)


def _aspect_symbol(aspect: str) -> str:
    """Get aspect symbol."""
    symbols = {
        "conjunction": "☌",
        "opposition": "☍",
        "trine": "△",
        "square": "□",
        "sextile": "⚹",
        "quintile": "Q",
        "septile": "S",
        "novile": "N",
    }
    return symbols.get(aspect.lower(), aspect)


def _aspect_quality(aspect: str, lang: str = "ru") -> str:
    """Get aspect interpretation."""
    interp = {
        "conjunction": {
            "ru": "Соединение - объединение энергий, усиление качества",
            "en": "Conjunction - union of energies, amplification",
        },
        "opposition": {
            "ru": "Оппозиция - напряжение, необходимость баланса",
            "en": "Opposition - tension, need for balance",
        },
        "trine": {
            "ru": "Трин - гармония, лёгкий поток энергии, таланты",
            "en": "Trine - harmony, easy flow of energy, talents",
        },
        "square": {
            "ru": "Квадрат - конфликт, мотивация к действию",
            "en": "Square - conflict, motivation to act",
        },
        "sextile": {
            "ru": "Секстиль - возможности, творческие решения",
            "en": "Sextile - opportunities, creative solutions",
        },
    }
    return interp.get(aspect.lower(), {}).get(lang, aspect)


def _sun_interpretation(sign: str, lang: str = "ru") -> str:
    """Brief Sun sign interpretation."""
    interp = {
        "Aries": {"ru": "Энергия, инициатива, лидерство"},
        "Taurus": {"ru": "Стабильность, упорство, материальность"},
        "Gemini": {"ru": "Общение, любознательность, гибкость"},
        "Cancer": {"ru": "Эмоциональность, забота, интуиция"},
        "Leo": {"ru": "Творчество, самовыражение, щедрость"},
        "Virgo": {"ru": "Анализ, служение, практичность"},
        "Libra": {"ru": "Гармония, партнёрство, дипломатия"},
        "Scorpio": {"ru": "Глубина, трансформация, страсть"},
        "Sagittarius": {"ru": "Расширение, философия, свобода"},
        "Capricorn": {"ru": "Амбиции, структура, ответственность"},
        "Aquarius": {"ru": "Инновации, независимость, гуманизм"},
        "Pisces": {"ru": "Сострадание, мистика, творчество"},
    }
    return interp.get(sign, {}).get(lang, "")


def _moon_interpretation(sign: str, lang: str = "ru") -> str:
    """Brief Moon sign interpretation."""
    interp = {
        "Aries": {"ru": "Эмоциональная спонтанность, быстрые реакции"},
        "Taurus": {"ru": "Потребность в стабильности, комфорте"},
        "Gemini": {"ru": "Эмоциональная подвижность, любопытство"},
        "Cancer": {"ru": "Глубокие чувства, привязанность к дому"},
        "Leo": {"ru": "Потребность в признании, тёплое сердце"},
        "Virgo": {"ru": "Эмоциональная сдержанность, аналитичность"},
        "Libra": {"ru": "Потребность в гармонии отношений"},
        "Scorpio": {"ru": "Интенсивные эмоции, глубина переживаний"},
        "Sagittarius": {"ru": "Эмоциональная свобода, оптимизм"},
        "Capricorn": {"ru": "Эмоциональный контроль, серьёзность"},
        "Aquarius": {"ru": "Эмоциональная независимость, уникальность"},
        "Pisces": {"ru": "Эмоциональная чувствительность, эмпатия"},
    }
    return interp.get(sign, {}).get(lang, "")


def _asc_interpretation(sign: str, lang: str = "ru") -> str:
    """Brief Ascendant interpretation."""
    interp = {
        "Aries": {"ru": "Прямой, активный, инициативный подход к жизни"},
        "Taurus": {"ru": "Спокойный, практичный, упорный стиль"},
        "Gemini": {"ru": "Любознательный, коммуникативный образ"},
        "Cancer": {"ru": "Осторожный, заботливый, чувствительный"},
        "Leo": {"ru": "Уверенный, яркий, креативный образ"},
        "Virgo": {"ru": "Сдержанный, аналитичный, услужливый"},
        "Libra": {"ru": "Дипломатичный, гармоничный, социальный"},
        "Scorpio": {"ru": "Интенсивный, проницательный, магнетичный"},
        "Sagittarius": {"ru": "Оптимистичный, свободолюбивый, прямой"},
        "Capricorn": {"ru": "Серьёзный, ответственный, целеустремлённый"},
        "Aquarius": {"ru": "Оригинальный, независимый, дружелюбный"},
        "Pisces": {"ru": "Мягкий, сочувствующий, мечтательный"},
    }
    return interp.get(sign, {}).get(lang, "")


def format_markdown(data: dict[str, Any]) -> str:
    """
    Markdown format for documentation/sharing.
    """
    facts = data.get("facts", [])
    chart_info = data.get("input_metadata", {})
    place_info = chart_info.get("place", {})
    coords = chart_info.get("coordinates", {})

    output = []
    output.append("# Натальная карта")
    output.append(f"\n**Дата:** {chart_info.get('local_datetime', '?')}")
    output.append(
        f"**Место:** {place_info.get('name', '?')}, {place_info.get('country', '?')}"
    )
    output.append(f"**Координаты:** {coords.get('lat', '?')}, {coords.get('lon', '?')}")
    output.append("\n---\n")

    output.append("## Основные позиции\n")

    # Sun, Moon, Asc
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Ascendant"]:
        position = _find_fact(facts, planet, "planet_in_sign")
        if position:
            output.append(
                f"**{_planet_symbol(planet)} {planet}:** {position.get('value', '?')}"
            )

    output.append("\n---\n")
    output.append("## Достоинства планет\n")

    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        total_dig = _find_fact(facts, planet, "total_dignity")
        if total_dig:
            score = total_dig.get("details", {}).get("total_score", 0)
            value = total_dig.get("value", "?")
            output.append(
                f"- **{_planet_symbol(planet)} {planet}:** {value} ({score:+d}) {_dignity_stars(total_dig)}"
            )

    output.append("\n---\n")
    output.append("## Ключевые аспекты\n")

    aspects = [
        f
        for f in facts
        if f["type"] == "aspect" and f.get("details", {}).get("orb", 10) < 3
    ]
    aspects_sorted = sorted(aspects, key=lambda x: x.get("details", {}).get("orb", 10))

    for asp in aspects_sorted[:10]:
        details = asp.get("details", {})
        p1 = _planet_symbol(details.get("from", "?"))
        p2 = _planet_symbol(details.get("to", "?"))
        aspect = details.get("aspect", "?")
        orb = details.get("orb", 0)
        motion = details.get("motion", "?")

        output.append(f"- {p1} **{aspect}** {p2} (орбис {orb:.2f}°, {motion})")

    return "\n".join(output)


def format_compact(data: dict[str, Any], lang: str = "ru") -> str:
    """
    Compact format - planets on one line each.

    Example:
        ☉ Cap 17°37' (H12) | ☽ Gem 25°24' (H5) | ☿ Aqu 3°55' (H1)
        ♀ Cap 26°51' (H12) | ♂ Lib 26°53' (H9) | ♃ Sco 6°22' (H9)

    Args:
        data: Chart data from natal calculation
        lang: Language code (ru or en)

    Returns:
        Compact formatted text
    """
    facts = data.get("facts", [])

    # Extract planets
    planets_data = []
    for planet_name in [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "North_Node",
    ]:
        pos = _find_fact(facts, planet_name, "planet_in_sign")
        if pos:
            symbol = _planet_symbol(planet_name)
            sign = pos.get("value", "?")
            sign_short = sign[:3] if sign else "?"
            lon = pos.get("details", {}).get("longitude", 0)
            deg = int(lon % 30)
            minutes = int((lon % 30 - deg) * 60)
            # House number is in details.house of planet_in_sign fact
            house_num = pos.get("details", {}).get("house", "?")

            # Check retrograde
            retro = ""
            speed_fact = _find_fact(facts, planet_name, "speed")
            if speed_fact and speed_fact.get("details", {}).get("speed", 0) < 0:
                retro = "℞"

            planets_data.append(
                f"{symbol} {sign_short} {deg}°{minutes:02d}'{retro} (H{house_num})"
            )

    # Format in 3 columns
    output = []
    for i in range(0, len(planets_data), 3):
        line = " | ".join(planets_data[i : i + 3])
        output.append(line)

    # Add Ascendant and MC
    asc = _find_fact(facts, "Ascendant", "planet_in_sign")
    mc = _find_fact(facts, "Midheaven", "planet_in_sign")

    angles = []
    if asc:
        sign = asc.get("value", "?")[:3]
        lon = asc.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        minutes = int((lon % 30 - deg) * 60)
        angles.append(f"ASC: {sign} {deg}°{minutes:02d}'")

    if mc:
        sign = mc.get("value", "?")[:3]
        lon = mc.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        minutes = int((lon % 30 - deg) * 60)
        angles.append(f"MC: {sign} {deg}°{minutes:02d}'")

    if angles:
        output.append("")
        output.append(" | ".join(angles))

    # Count aspects and stelliums
    aspects = [f for f in facts if f["type"] == "aspect"]
    major = [a for a in aspects if a.get("details", {}).get("category") == "major"]

    stelliums = [f for f in facts if f["type"] == "stellium"]

    stats = []
    stats.append(f"Major aspects: {len(major)}")
    if stelliums:
        for stell in stelliums:
            sign = stell.get("details", {}).get("sign", "?")
            count = stell.get("details", {}).get("planet_count", 0)
            stats.append(f"Stellium: {sign} ({count})")

    if stats:
        output.append(" | ".join(stats))

    return "\n".join(output)


def format_summary_line(data: dict[str, Any], lang: str = "ru") -> str:
    """
    Single line summary - ultra compact.

    Example:
        ☉ ♑ 17° | ☽ ♊ 25° | ASC ♒ 3° | MC ♏ 4° | Stellium ♎ (♂♄♇) | 9 aspects

    Args:
        data: Chart data from natal calculation
        lang: Language code (ru or en)

    Returns:
        One line summary
    """
    facts = data.get("facts", [])

    parts = []

    # Sun
    sun = _find_fact(facts, "Sun", "planet_in_sign")
    if sun:
        sign = sun.get("value", "?")
        sign_symbol = _sign_symbol(sign)
        lon = sun.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        parts.append(f"☉ {sign_symbol} {deg}°")

    # Moon
    moon = _find_fact(facts, "Moon", "planet_in_sign")
    if moon:
        sign = moon.get("value", "?")
        sign_symbol = _sign_symbol(sign)
        lon = moon.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        parts.append(f"☽ {sign_symbol} {deg}°")

    # Ascendant
    asc = _find_fact(facts, "Ascendant", "planet_in_sign")
    if asc:
        sign = asc.get("value", "?")
        sign_symbol = _sign_symbol(sign)
        lon = asc.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        parts.append(f"ASC {sign_symbol} {deg}°")

    # MC
    mc = _find_fact(facts, "Midheaven", "planet_in_sign")
    if mc:
        sign = mc.get("value", "?")
        sign_symbol = _sign_symbol(sign)
        lon = mc.get("details", {}).get("longitude", 0)
        deg = int(lon % 30)
        parts.append(f"MC {sign_symbol} {deg}°")

    # Stellium
    stelliums = [f for f in facts if f["type"] == "stellium"]
    if stelliums:
        stell = stelliums[0]
        sign = stell.get("details", {}).get("sign", "?")
        sign_symbol = _sign_symbol(sign)
        planets = stell.get("details", {}).get("planets", [])
        planet_symbols = "".join([_planet_symbol(p) for p in planets[:3]])
        parts.append(f"Stellium {sign_symbol} ({planet_symbols})")

    # Aspects count
    aspects = [f for f in facts if f["type"] == "aspect"]
    major = [a for a in aspects if a.get("details", {}).get("category") == "major"]
    parts.append(f"{len(major)} aspects")

    return " | ".join(parts)


def _planet_color(planet_name: str) -> str:
    """Get ANSI color code for a planet."""
    colors = {
        "Sun": Fore.YELLOW,
        "Moon": Fore.CYAN,
        "Mercury": Fore.GREEN,
        "Venus": Fore.GREEN,
        "Mars": Fore.RED,
        "Jupiter": Fore.BLUE,
        "Saturn": Fore.WHITE,  # Dim/neutral
        "Uranus": Fore.CYAN,
        "Neptune": Fore.BLUE,
        "Pluto": Fore.RED,
        "North Node": Fore.MAGENTA,
    }
    return colors.get(planet_name, "")


def _colorize(text: str, color: str, use_colors: bool = True) -> str:
    """Apply color to text if colors are enabled."""
    if not use_colors:
        return text
    return f"{color}{text}{Style.RESET_ALL}"


def _visible_len(text: str) -> int:
    """Get visible length of string (excluding ANSI escape codes)."""
    import re

    # Remove ANSI escape sequences
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return len(ansi_escape.sub("", text))


def _ljust_visible(text: str, width: int) -> str:
    """Left-justify text considering only visible characters (excluding ANSI codes)."""
    visible_length = _visible_len(text)
    padding = width - visible_length
    return text + " " * padding if padding > 0 else text


def _sign_symbol(sign: str) -> str:
    """Get zodiac sign symbol."""
    symbols = {
        "Aries": "♈",
        "Taurus": "♉",
        "Gemini": "♊",
        "Cancer": "♋",
        "Leo": "♌",
        "Virgo": "♍",
        "Libra": "♎",
        "Scorpio": "♏",
        "Sagittarius": "♐",
        "Capricorn": "♑",
        "Aquarius": "♒",
        "Pisces": "♓",
    }
    return symbols.get(sign, sign[:3])


def format_table(
    data: dict[str, Any], lang: str = "ru", use_colors: bool = True
) -> str:
    """
    Beautiful table format with Unicode box-drawing characters.

    Args:
        data: Natal chart data from calculate_natal_with_facts()
        lang: Language code (ru or en)
        use_colors: Enable ANSI terminal colors for planets

    Returns:
        Formatted table with planets, signs, houses, dignities
    """
    facts = data.get("facts", [])

    # Planet names and symbols
    planets_order = [
        ("Sun", "☉"),
        ("Moon", "☽"),
        ("Mercury", "☿"),
        ("Venus", "♀"),
        ("Mars", "♂"),
        ("Jupiter", "♃"),
        ("Saturn", "♄"),
        ("Uranus", "♅"),
        ("Neptune", "♆"),
        ("Pluto", "♇"),
        ("North Node", "☊"),
    ]

    # Collect data for each planet
    rows = []
    for planet_name, symbol in planets_order:
        planet_pos = _find_fact(facts, planet_name, "planet_in_sign")
        if not planet_pos:
            continue

        # Extract fields
        sign = planet_pos.get("value", "")
        details = planet_pos.get("details", {})
        longitude = details.get("longitude", 0)
        house = details.get("house", "?")

        # Calculate degree within sign
        degree_in_sign = longitude % 30
        deg = int(degree_in_sign)
        min_val = int((degree_in_sign - deg) * 60)
        degree_str = f"{deg:2d}°{min_val:02d}'"

        # Get dignity
        dignity_fact = _find_fact(facts, planet_name, "total_dignity")
        dignity = dignity_fact.get("value", "Neutral") if dignity_fact else "Neutral"

        # Get speed (retrograde check)
        speed_fact = _find_fact(facts, planet_name, "speed")
        speed = speed_fact.get("details", {}).get("speed", 0) if speed_fact else 0
        speed_str = f"{abs(speed):5.2f}°"
        if speed < 0:
            speed_str += " ℞"

        # Sign symbol and abbreviation
        sign_sym = _sign_symbol(sign)
        sign_abbr = sign[:3]

        # Apply color to planet symbol
        planet_color = _planet_color(planet_name)
        colored_symbol = _colorize(symbol, planet_color, use_colors)

        rows.append(
            {
                "planet": f"{colored_symbol} {planet_name}",
                "sign": f"{sign_sym} {sign_abbr}",
                "degree": degree_str,
                "house": f"{house:>2}" if house != "?" else " ?",
                "dignity": dignity,
                "speed": speed_str,
            }
        )

    # Build table
    output = []

    # Column widths
    col_widths = {
        "planet": 13,
        "sign": 7,
        "degree": 8,
        "house": 5,
        "dignity": 8,
        "speed": 9,
    }

    # Header labels
    if lang == "ru":
        headers = {
            "planet": "Планета",
            "sign": "Знак",
            "degree": "Градус",
            "house": "Дом",
            "dignity": "Сила",
            "speed": "Скорость",
        }
    else:
        headers = {
            "planet": "Planet",
            "sign": "Sign",
            "degree": "Degree",
            "house": "House",
            "dignity": "Dignity",
            "speed": "Speed",
        }

    # Top border
    top = "┌" + "─" * col_widths["planet"] + "┬"
    top += "─" * col_widths["sign"] + "┬"
    top += "─" * col_widths["degree"] + "┬"
    top += "─" * col_widths["house"] + "┬"
    top += "─" * col_widths["dignity"] + "┬"
    top += "─" * col_widths["speed"] + "┐"
    output.append(top)

    # Header row
    header_row = "│"
    header_row += _ljust_visible(headers["planet"], col_widths["planet"]) + "│"
    header_row += _ljust_visible(headers["sign"], col_widths["sign"]) + "│"
    header_row += _ljust_visible(headers["degree"], col_widths["degree"]) + "│"
    header_row += _ljust_visible(headers["house"], col_widths["house"]) + "│"
    header_row += _ljust_visible(headers["dignity"], col_widths["dignity"]) + "│"
    header_row += _ljust_visible(headers["speed"], col_widths["speed"]) + "│"
    output.append(header_row)

    # Separator after header
    sep = "├" + "─" * col_widths["planet"] + "┼"
    sep += "─" * col_widths["sign"] + "┼"
    sep += "─" * col_widths["degree"] + "┼"
    sep += "─" * col_widths["house"] + "┼"
    sep += "─" * col_widths["dignity"] + "┼"
    sep += "─" * col_widths["speed"] + "┤"
    output.append(sep)

    # Data rows
    for row in rows:
        data_row = "│"
        data_row += _ljust_visible(row["planet"], col_widths["planet"]) + "│"
        data_row += _ljust_visible(row["sign"], col_widths["sign"]) + "│"
        data_row += _ljust_visible(row["degree"], col_widths["degree"]) + "│"
        data_row += _ljust_visible(row["house"], col_widths["house"]) + "│"
        data_row += _ljust_visible(row["dignity"], col_widths["dignity"]) + "│"
        data_row += _ljust_visible(row["speed"], col_widths["speed"]) + "│"
        output.append(data_row)

    # Bottom border
    bottom = "└" + "─" * col_widths["planet"] + "┴"
    bottom += "─" * col_widths["sign"] + "┴"
    bottom += "─" * col_widths["degree"] + "┴"
    bottom += "─" * col_widths["house"] + "┴"
    bottom += "─" * col_widths["dignity"] + "┴"
    bottom += "─" * col_widths["speed"] + "┘"
    output.append(bottom)

    # Add chart info
    chart_info = data.get("input_metadata", {})
    place_info = chart_info.get("place", {})
    output.append("")
    output.append(f"📅 {chart_info.get('datetime_utc_iso', 'N/A')}")
    output.append(
        f"📍 {place_info.get('name', 'Unknown')}, {place_info.get('country', '')}"
    )

    # Add aspect count
    aspects = [f for f in facts if f["type"] == "aspect"]
    major = [a for a in aspects if a.get("details", {}).get("category") == "major"]
    output.append(f"✨ {len(major)} major aspects")

    return "\n".join(output)


def format_aspects(
    data: dict[str, Any],
    lang: str = "ru",
    aspect_type: str = "all",
    max_orb: float = 10.0,
    planet_filter: list[str] | None = None,
    use_colors: bool = True,
) -> str:
    """
    Format aspects in a table.

    Args:
        data: Natal chart data with facts
        lang: Language code (ru or en)
        aspect_type: Filter by type - 'major', 'minor', or 'all'
        max_orb: Maximum orb to display
        planet_filter: List of planet names to filter by (e.g., ['Moon', 'Saturn'])
        use_colors: Enable ANSI terminal colors

    Returns:
        Formatted aspects table
    """
    facts = data.get("facts", [])

    # Filter aspects
    aspects = [
        f
        for f in facts
        if f["type"] == "aspect" and f.get("details", {}).get("orb", 0) <= max_orb
    ]

    if aspect_type != "all":
        aspects = [
            a for a in aspects if a.get("details", {}).get("category") == aspect_type
        ]

    # Filter by planets if specified
    if planet_filter:
        filtered_aspects = []
        for asp in aspects:
            planets_str = asp.get("object", "")
            # Split by common separators (dash, space, etc.)
            planets_in_aspect = planets_str.replace("-", " ").split()
            # Check if any of the filtered planets are in this aspect
            if any(planet in planets_in_aspect for planet in planet_filter):
                filtered_aspects.append(asp)
        aspects = filtered_aspects

    # Sort by orb (tightest first)
    aspects.sort(key=lambda a: a.get("details", {}).get("orb", 999))

    if not aspects:
        return "No aspects found matching criteria."

    # Aspect symbols
    aspect_symbols = {
        "conjunction": "☌",
        "opposition": "☍",
        "trine": "△",
        "square": "□",
        "sextile": "✶",
        "quincunx": "⚻",
        "semisextile": "⚺",
        "quintile": "Q",
        "biquintile": "bQ",
        "semisquare": "sq",
        "sesquiquadrate": "sqq",
    }

    # Build output
    output = []

    # Header
    if lang == "ru":
        title = f"✨ АСПЕКТЫ ({len(aspects)})"
        if planet_filter:
            title += f" [Фильтр: {', '.join(planet_filter)}]"
    else:
        title = f"✨ ASPECTS ({len(aspects)})"
        if planet_filter:
            title += f" [Filter: {', '.join(planet_filter)}]"

    output.append("=" * 70)
    output.append(title.center(70))
    output.append("=" * 70)
    output.append("")

    # Column widths
    col_widths = {"planets": 20, "aspect": 15, "orb": 8, "type": 10, "motion": 10}

    # Header labels
    if lang == "ru":
        headers = {
            "planets": "Планеты",
            "aspect": "Аспект",
            "orb": "Орб",
            "type": "Тип",
            "motion": "Движение",
        }
    else:
        headers = {
            "planets": "Planets",
            "aspect": "Aspect",
            "orb": "Orb",
            "type": "Type",
            "motion": "Motion",
        }

    # Table border
    top = "┌" + "─" * col_widths["planets"] + "┬"
    top += "─" * col_widths["aspect"] + "┬"
    top += "─" * col_widths["orb"] + "┬"
    top += "─" * col_widths["type"] + "┬"
    top += "─" * col_widths["motion"] + "┐"
    output.append(top)

    # Header row
    header_row = "│"
    header_row += _ljust_visible(headers["planets"], col_widths["planets"]) + "│"
    header_row += _ljust_visible(headers["aspect"], col_widths["aspect"]) + "│"
    header_row += _ljust_visible(headers["orb"], col_widths["orb"]) + "│"
    header_row += _ljust_visible(headers["type"], col_widths["type"]) + "│"
    header_row += _ljust_visible(headers["motion"], col_widths["motion"]) + "│"
    output.append(header_row)

    # Separator
    sep = "├" + "─" * col_widths["planets"] + "┼"
    sep += "─" * col_widths["aspect"] + "┼"
    sep += "─" * col_widths["orb"] + "┼"
    sep += "─" * col_widths["type"] + "┼"
    sep += "─" * col_widths["motion"] + "┤"
    output.append(sep)

    # Data rows
    for asp in aspects:
        planets = asp.get("object", "")
        aspect_name = asp.get("value", "")
        details = asp.get("details", {})
        orb = details.get("orb", 0)
        category = details.get("category", "")
        motion = details.get("motion", "")

        # Get aspect symbol
        symbol = aspect_symbols.get(aspect_name, "")
        aspect_display = f"{symbol} {aspect_name}" if symbol else aspect_name

        # Colorize by category
        if use_colors:
            if category == "major":
                aspect_display = _colorize(aspect_display, Fore.YELLOW, use_colors)
            else:
                aspect_display = _colorize(aspect_display, Fore.CYAN, use_colors)

        # Format motion
        if lang == "ru":
            motion_text = "сходящийся" if motion == "applying" else "расходящийся"
        else:
            motion_text = motion

        data_row = "│"
        data_row += _ljust_visible(planets, col_widths["planets"]) + "│"
        data_row += _ljust_visible(aspect_display, col_widths["aspect"]) + "│"
        data_row += _ljust_visible(f"{orb:.2f}°", col_widths["orb"]) + "│"
        data_row += _ljust_visible(category, col_widths["type"]) + "│"
        data_row += _ljust_visible(motion_text, col_widths["motion"]) + "│"
        output.append(data_row)

    # Bottom border
    bottom = "└" + "─" * col_widths["planets"] + "┴"
    bottom += "─" * col_widths["aspect"] + "┴"
    bottom += "─" * col_widths["orb"] + "┴"
    bottom += "─" * col_widths["type"] + "┴"
    bottom += "─" * col_widths["motion"] + "┘"
    output.append(bottom)

    # Chart info
    chart_info = data.get("input_metadata", {})
    place_info = chart_info.get("place", {})
    output.append("")
    output.append(f"📅 {chart_info.get('datetime_utc_iso', 'N/A')}")
    output.append(
        f"📍 {place_info.get('name', 'Unknown')}, {place_info.get('country', '')}"
    )

    return "\n".join(output)


def format_dignities(
    data: dict[str, Any],
    lang: str = "ru",
    use_colors: bool = True,
) -> str:
    """
    Format planetary dignities table.

    Args:
        data: Natal chart data with facts
        lang: Language code (ru or en)
        use_colors: Enable ANSI terminal colors

    Returns:
        Formatted dignities table
    """
    facts = data.get("facts", [])

    # Get planet order
    planets_order = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]

    # Collect dignity data
    rows = []
    for planet in planets_order:
        essential = next(
            (
                f
                for f in facts
                if f["object"] == planet and f["type"] == "essential_dignity"
            ),
            None,
        )
        accidental = next(
            (
                f
                for f in facts
                if f["object"] == planet and f["type"] == "accidental_dignity"
            ),
            None,
        )
        total = next(
            (
                f
                for f in facts
                if f["object"] == planet and f["type"] == "total_dignity"
            ),
            None,
        )

        if not total:
            continue

        ess_score = essential.get("details", {}).get("score", 0) if essential else 0
        acc_score = accidental.get("details", {}).get("score", 0) if accidental else 0
        total_score = total.get("details", {}).get("total_score", 0)

        # Essential dignity details
        ess_details = essential.get("details", {}) if essential else {}
        domicile = "✓" if ess_details.get("domicile") else ""
        exaltation = "✓" if ess_details.get("exaltation") else ""
        detriment = "✓" if ess_details.get("detriment") else ""
        fall = "✓" if ess_details.get("fall") else ""

        # Accidental dignity details
        acc_details = accidental.get("details", {}) if accidental else {}
        house_str = acc_details.get("house_strength", 0)
        motion_str = acc_details.get("motion_strength", 0)

        # Total strength label
        strength = total.get("value", "Neutral")

        # Colorize strength
        if use_colors:
            if "Very Strong" in strength:
                strength = _colorize(strength, Fore.GREEN, use_colors)
            elif "Strong" in strength:
                strength = _colorize(strength, Fore.CYAN, use_colors)
            elif "Weak" in strength or "Very Weak" in strength:
                strength = _colorize(strength, Fore.RED, use_colors)

        rows.append(
            {
                "planet": planet,
                "essential": f"{ess_score:+d}",
                "domicile": domicile,
                "exaltation": exaltation,
                "detriment": detriment,
                "fall": fall,
                "accidental": f"{acc_score:+d}",
                "house": f"{house_str:+d}",
                "motion": f"{motion_str:+d}",
                "total": f"{total_score:+d}",
                "strength": strength,
            }
        )

    # Build output
    output = []

    # Header
    if lang == "ru":
        title = "⭐ ДОСТОИНСТВА ПЛАНЕТ"
    else:
        title = "⭐ PLANETARY DIGNITIES"

    output.append("=" * 100)
    output.append(title.center(100))
    output.append("=" * 100)
    output.append("")

    # Column widths
    col_widths = {
        "planet": 10,
        "essential": 9,
        "domicile": 5,
        "exaltation": 5,
        "detriment": 5,
        "fall": 5,
        "accidental": 10,
        "house": 6,
        "motion": 6,
        "total": 6,
        "strength": 12,
    }

    # Header labels
    if lang == "ru":
        headers = {
            "planet": "Планета",
            "essential": "Эссенц.",
            "domicile": "Влад.",
            "exaltation": "Экз.",
            "detriment": "Изгн.",
            "fall": "Пад.",
            "accidental": "Акцид.",
            "house": "Дом",
            "motion": "Движ.",
            "total": "Итого",
            "strength": "Сила",
        }
    else:
        headers = {
            "planet": "Planet",
            "essential": "Essential",
            "domicile": "Dom.",
            "exaltation": "Exlt.",
            "detriment": "Detr.",
            "fall": "Fall",
            "accidental": "Accidental",
            "house": "House",
            "motion": "Motion",
            "total": "Total",
            "strength": "Strength",
        }

    # Table border (top)
    top = "┌" + "─" * col_widths["planet"] + "┬"
    top += "─" * col_widths["essential"] + "┬"
    top += "─" * col_widths["domicile"] + "┬"
    top += "─" * col_widths["exaltation"] + "┬"
    top += "─" * col_widths["detriment"] + "┬"
    top += "─" * col_widths["fall"] + "┬"
    top += "─" * col_widths["accidental"] + "┬"
    top += "─" * col_widths["house"] + "┬"
    top += "─" * col_widths["motion"] + "┬"
    top += "─" * col_widths["total"] + "┬"
    top += "─" * col_widths["strength"] + "┐"
    output.append(top)

    # Header row
    header_row = "│"
    for key in [
        "planet",
        "essential",
        "domicile",
        "exaltation",
        "detriment",
        "fall",
        "accidental",
        "house",
        "motion",
        "total",
        "strength",
    ]:
        header_row += _ljust_visible(headers[key], col_widths[key]) + "│"
    output.append(header_row)

    # Separator
    sep = "├" + "─" * col_widths["planet"] + "┼"
    sep += "─" * col_widths["essential"] + "┼"
    sep += "─" * col_widths["domicile"] + "┼"
    sep += "─" * col_widths["exaltation"] + "┼"
    sep += "─" * col_widths["detriment"] + "┼"
    sep += "─" * col_widths["fall"] + "┼"
    sep += "─" * col_widths["accidental"] + "┼"
    sep += "─" * col_widths["house"] + "┼"
    sep += "─" * col_widths["motion"] + "┼"
    sep += "─" * col_widths["total"] + "┼"
    sep += "─" * col_widths["strength"] + "┤"
    output.append(sep)

    # Data rows
    for row in rows:
        data_row = "│"
        for key in [
            "planet",
            "essential",
            "domicile",
            "exaltation",
            "detriment",
            "fall",
            "accidental",
            "house",
            "motion",
            "total",
            "strength",
        ]:
            data_row += _ljust_visible(row[key], col_widths[key]) + "│"
        output.append(data_row)

    # Bottom border
    bottom = "└" + "─" * col_widths["planet"] + "┴"
    bottom += "─" * col_widths["essential"] + "┴"
    bottom += "─" * col_widths["domicile"] + "┴"
    bottom += "─" * col_widths["exaltation"] + "┴"
    bottom += "─" * col_widths["detriment"] + "┴"
    bottom += "─" * col_widths["fall"] + "┴"
    bottom += "─" * col_widths["accidental"] + "┴"
    bottom += "─" * col_widths["house"] + "┴"
    bottom += "─" * col_widths["motion"] + "┴"
    bottom += "─" * col_widths["total"] + "┴"
    bottom += "─" * col_widths["strength"] + "┘"
    output.append(bottom)

    # Legend
    output.append("")
    if lang == "ru":
        output.append("Легенда:")
        output.append(
            "  Эссенциальные: Влад. = владение, Экз. = экзальтация, Изгн. = изгнание, Пад. = падение"
        )
        output.append(
            "  Акцидентальные: Дом = позиция в доме, Движ. = скорость движения"
        )
    else:
        output.append("Legend:")
        output.append(
            "  Essential: Dom. = domicile (rulership), Exlt. = exaltation, Detr. = detriment, Fall = fall"
        )
        output.append(
            "  Accidental: House = house position strength, Motion = motion/speed strength"
        )

    # Chart info
    chart_info = data.get("input_metadata", {})
    place_info = chart_info.get("place", {})
    output.append("")
    output.append(f"📅 {chart_info.get('datetime_utc_iso', 'N/A')}")
    output.append(
        f"📍 {place_info.get('name', 'Unknown')}, {place_info.get('country', '')}"
    )

    return "\n".join(output)


def format_transits(
    natal_data: dict[str, Any],
    transit_data: dict[str, Any],
    transits_aspects: list[dict[str, Any]],
    lang: str = "ru",
    max_orb: float = 3.0,
    use_colors: bool = True,
) -> str:
    """
    Format transits to natal chart.

    Args:
        natal_data: Natal chart calculation result
        transit_data: Transit chart calculation result
        transits_aspects: List of aspects between transit and natal planets
        lang: Language code (ru or en)
        max_orb: Maximum orb to display
        use_colors: Enable ANSI terminal colors

    Returns:
        Formatted transits table
    """
    # Filter aspects by orb
    aspects = [a for a in transits_aspects if a.get("orb", 0) <= max_orb]

    # Sort by orb (tightest first)
    aspects.sort(key=lambda a: a.get("orb", 999))

    if not aspects:
        return "No transits found within orb limit."

    # Aspect symbols
    aspect_symbols = {
        "conjunction": "☌",
        "opposition": "☍",
        "trine": "△",
        "square": "□",
        "sextile": "✶",
        "quincunx": "⚻",
        "semisextile": "⚺",
        "quintile": "Q",
        "biquintile": "bQ",
        "semisquare": "sq",
        "sesquiquadrate": "sqq",
    }

    # Build output
    output = []

    # Header
    if lang == "ru":
        title = f"🌟 ТРАНЗИТЫ К НАТАЛЬНОЙ КАРТЕ ({len(aspects)})"
    else:
        title = f"🌟 TRANSITS TO NATAL CHART ({len(aspects)})"

    output.append("=" * 80)
    output.append(title.center(80))
    output.append("=" * 80)
    output.append("")

    # Column widths
    col_widths = {
        "transit": 15,
        "aspect": 12,
        "natal": 15,
        "orb": 8,
        "type": 8,
        "category": 8,
    }

    # Header labels
    if lang == "ru":
        headers = {
            "transit": "Транзит",
            "aspect": "Аспект",
            "natal": "Натальная",
            "orb": "Орб",
            "type": "Тип",
            "category": "Категория",
        }
    else:
        headers = {
            "transit": "Transit",
            "aspect": "Aspect",
            "natal": "Natal",
            "orb": "Orb",
            "type": "Type",
            "category": "Category",
        }

    # Table border (top)
    top = "┌" + "─" * col_widths["transit"] + "┬"
    top += "─" * col_widths["aspect"] + "┬"
    top += "─" * col_widths["natal"] + "┬"
    top += "─" * col_widths["orb"] + "┬"
    top += "─" * col_widths["type"] + "┬"
    top += "─" * col_widths["category"] + "┐"
    output.append(top)

    # Header row
    header_row = "│"
    header_row += _ljust_visible(headers["transit"], col_widths["transit"]) + "│"
    header_row += _ljust_visible(headers["aspect"], col_widths["aspect"]) + "│"
    header_row += _ljust_visible(headers["natal"], col_widths["natal"]) + "│"
    header_row += _ljust_visible(headers["orb"], col_widths["orb"]) + "│"
    header_row += _ljust_visible(headers["type"], col_widths["type"]) + "│"
    header_row += _ljust_visible(headers["category"], col_widths["category"]) + "│"
    output.append(header_row)

    # Separator
    sep = "├" + "─" * col_widths["transit"] + "┼"
    sep += "─" * col_widths["aspect"] + "┼"
    sep += "─" * col_widths["natal"] + "┼"
    sep += "─" * col_widths["orb"] + "┼"
    sep += "─" * col_widths["type"] + "┼"
    sep += "─" * col_widths["category"] + "┤"
    output.append(sep)

    # Data rows
    for asp in aspects:
        transit_planet = asp.get("planet1", "")
        natal_planet = asp.get("planet2", "")
        aspect_name = asp.get("aspect", "")
        orb = asp.get("orb", 0)
        asp_type = asp.get("type", "")
        category = asp.get("category", "")

        # Get aspect symbol
        symbol = aspect_symbols.get(aspect_name, "")
        aspect_display = f"{symbol} {aspect_name}" if symbol else aspect_name

        # Colorize by type
        if use_colors:
            if asp_type == "hard":
                aspect_display = _colorize(aspect_display, Fore.RED, use_colors)
            else:
                aspect_display = _colorize(aspect_display, Fore.GREEN, use_colors)

        # Format type label
        if lang == "ru":
            type_label = "напряж." if asp_type == "hard" else "гармон."
        else:
            type_label = asp_type

        data_row = "│"
        data_row += _ljust_visible(transit_planet, col_widths["transit"]) + "│"
        data_row += _ljust_visible(aspect_display, col_widths["aspect"]) + "│"
        data_row += _ljust_visible(natal_planet, col_widths["natal"]) + "│"
        data_row += _ljust_visible(f"{orb:.2f}°", col_widths["orb"]) + "│"
        data_row += _ljust_visible(type_label, col_widths["type"]) + "│"
        data_row += _ljust_visible(category, col_widths["category"]) + "│"
        output.append(data_row)

    # Bottom border
    bottom = "└" + "─" * col_widths["transit"] + "┴"
    bottom += "─" * col_widths["aspect"] + "┴"
    bottom += "─" * col_widths["natal"] + "┴"
    bottom += "─" * col_widths["orb"] + "┴"
    bottom += "─" * col_widths["type"] + "┴"
    bottom += "─" * col_widths["category"] + "┘"
    output.append(bottom)

    # Chart info
    natal_info = natal_data.get("input_metadata", {})
    transit_info = transit_data.get("input_metadata", {})
    natal_place = natal_info.get("place", {})
    transit_place = transit_info.get("place", {})

    output.append("")
    if lang == "ru":
        output.append("📊 Натальная карта:")
    else:
        output.append("📊 Natal Chart:")
    output.append(f"   📅 {natal_info.get('utc_datetime', 'N/A')}")
    output.append(
        f"   📍 {natal_place.get('name', 'Unknown')}, {natal_place.get('country', '')}"
    )
    output.append("")
    if lang == "ru":
        output.append("🌍 Транзиты на дату:")
    else:
        output.append("🌍 Transits for:")
    output.append(f"   📅 {transit_info.get('utc_datetime', 'N/A')}")
    output.append(
        f"   📍 {transit_place.get('name', 'Unknown')}, {transit_place.get('country', '')}"
    )

    return "\n".join(output)
