"""
Output formatters for different user personas.
Transforms JSON facts into human-readable formats.
"""

from typing import Any


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
        output.append(f"   Сила: {sun_dignity.get('value', '?')} {strength}")
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
        output.append(f"   Сила: {moon_dignity.get('value', '?')} {strength}")
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


def format_table(data: dict[str, Any]) -> str:
    """
    Professional astrologer table format.
    Includes planet positions grid and aspect matrix.
    """
    facts = data.get("facts", [])

    output = []
    output.append("\n" + "=" * 90)
    output.append("                         НАТАЛЬНАЯ КАРТА - ТАБЛИЦА ПОЗИЦИЙ")
    output.append("=" * 90)

    # Planet positions table
    output.append(
        "\n┌─────────────┬─────────────┬──────────┬────┬──────┬─────────────┬─────────────┬─────────────┐"
    )
    output.append(
        "│ Планета     │ Знак        │ Градус   │ R/D│ Дом  │ Эссенц.     │ Акцид.      │ Всего       │"
    )
    output.append(
        "├─────────────┼─────────────┼──────────┼────┼──────┼─────────────┼─────────────┼─────────────┤"
    )

    planets = [
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

    for planet in planets:
        # Get facts
        position = _find_fact(facts, planet, "planet_in_sign")
        house = _find_fact(facts, planet, "house")
        retro = _find_fact(facts, planet, "retrograde")
        ess_dig = _find_fact(facts, planet, "essential_dignity")
        acc_dig = _find_fact(facts, planet, "accidental_dignity")
        total_dig = _find_fact(facts, planet, "total_dignity")

        # Format values
        planet_name = f"{_planet_symbol(planet)} {planet}".ljust(12)
        sign = position.get("value", "?").ljust(12) if position else "?".ljust(12)

        # Get degree from details
        degree = "?"
        if position and "details" in position:
            lon = position["details"].get("longitude", 0)
            deg_in_sign = lon % 30
            degree = f"{int(deg_in_sign):02d}°{int((deg_in_sign % 1) * 60):02d}'"
        degree = degree.ljust(9)

        retro_str = " R " if retro and retro.get("value") == "Retrograde" else " D "
        house_str = (
            str(house.get("details", {}).get("house", "?")).rjust(4)
            if house
            else "?".rjust(4)
        )

        ess_str = (
            (
                ess_dig.get("value", "?")
                + f" ({ess_dig.get('details', {}).get('score', 0):+d})"
            ).ljust(12)
            if ess_dig
            else "?".ljust(12)
        )
        acc_str = (
            (
                acc_dig.get("value", "?")
                + f" ({acc_dig.get('details', {}).get('score', 0):+d})"
            ).ljust(12)
            if acc_dig
            else "?".ljust(12)
        )
        total_str = (
            (
                total_dig.get("value", "?")
                + f" ({total_dig.get('details', {}).get('total_score', 0):+d})"
            ).ljust(12)
            if total_dig
            else "?".ljust(12)
        )

        output.append(
            f"│ {planet_name}│ {sign}│ {degree}│{retro_str}│{house_str}│ {ess_str}│ {acc_str}│ {total_str}│"
        )

    output.append(
        "└─────────────┴─────────────┴──────────┴────┴──────┴─────────────┴─────────────┴─────────────┘"
    )

    # Aspects section (major only, tight orbs)
    output.append("\n" + "=" * 90)
    output.append("                         МАЖОРНЫЕ АСПЕКТЫ (орбис < 5°)")
    output.append("=" * 90 + "\n")

    aspects = [
        f
        for f in facts
        if f["type"] == "aspect" and f.get("details", {}).get("orb", 10) < 5
    ]
    aspects_sorted = sorted(aspects, key=lambda x: x.get("details", {}).get("orb", 10))

    if not aspects_sorted:
        output.append("  Нет точных аспектов")
    else:
        output.append(
            "┌─────────────┬─────┬─────────────┬────────────┬─────────┬─────────────┐"
        )
        output.append(
            "│ Планета 1   │ Асп │ Планета 2   │ Орбис      │ Движение│ Тип         │"
        )
        output.append(
            "├─────────────┼─────┼─────────────┼────────────┼─────────┼─────────────┤"
        )

        for asp in aspects_sorted[:15]:  # Top 15
            details = asp.get("details", {})
            p1 = (
                _planet_symbol(details.get("from", "?"))
                + " "
                + details.get("from", "?")
            ).ljust(12)
            p2 = (
                _planet_symbol(details.get("to", "?")) + " " + details.get("to", "?")
            ).ljust(12)
            asp_sym = _aspect_symbol(details.get("aspect", "?")).center(4)
            orb_str = f"{details.get('orb', 0):6.2f}°".ljust(11)
            motion = details.get("motion", "?")[:8].ljust(8)
            asp_type = details.get("aspect", "?").ljust(12)

            output.append(f"│ {p1}│ {asp_sym}│ {p2}│ {orb_str}│ {motion}│ {asp_type}│")

        output.append(
            "└─────────────┴─────┴─────────────┴────────────┴─────────┴─────────────┘"
        )

    output.append("\n" + "=" * 90 + "\n")

    return "\n".join(output)


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
