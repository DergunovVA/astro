"""
Event Finder - поиск значимых астрологических событий и паттернов.

Для профессиональных астрологов: поиск конкретных конфигураций,
соединений планет, критических градусов, специфических паттернов.
"""

from typing import Any


def _parse_aspect(asp_fact: dict) -> dict | None:
    """
    Parse aspect fact to unified format.

    Input format: {object: "Planet1-Planet2", value: "conjunction", details: {orb: 2.3}}
    Output format: {from: "Planet1", to: "Planet2", aspect: "conjunction", orb: 2.3}
    """
    if asp_fact.get("type") != "aspect":
        return None

    obj = asp_fact.get("object", "")
    if "-" not in obj:
        return None

    p1, p2 = obj.split("-", 1)

    return {
        "from": p1,
        "to": p2,
        "aspect": asp_fact.get("value", ""),
        "orb": asp_fact.get("details", {}).get("orb", 0),
        "motion": asp_fact.get("details", {}).get("motion", ""),
    }


def find_conjunctions(
    facts: list[dict],
    planets: list[str] | None = None,
    max_orb: float = 5.0,
    min_planets: int = 2,
) -> dict[str, Any]:
    """
    Найти соединения (conjunctions) планет.

    Args:
        facts: Список фактов из карты
        planets: Список планет для поиска (None = все планеты)
        max_orb: Максимальный орбис соединения (градусы)
        min_planets: Минимальное количество планет в соединении

    Returns:
        {
            "found": bool,
            "conjunctions": [
                {
                    "planets": ["Mars", "Saturn", "Pluto"],
                    "orbs": {"Mars-Saturn": 2.3, "Mars-Pluto": 4.1, "Saturn-Pluto": 1.8},
                    "average_longitude": 189.5,
                    "sign": "Libra",
                    "tight": True  # если все орбисы < 3°
                }
            ],
            "count": int
        }

    Example:
        # Найти Mars-Saturn-Pluto conjunction:
        >>> find_conjunctions(facts, planets=["Mars", "Saturn", "Pluto"], max_orb=5)

        # Найти любые тройные соединения:
        >>> find_conjunctions(facts, min_planets=3, max_orb=8)
    """
    aspects = [f for f in facts if f["type"] == "aspect"]

    # Фильтр по планетам
    if planets:
        aspects = [
            a
            for a in aspects
            if a["details"]["from"] in planets and a["details"]["to"] in planets
        ]

    # Найти все соединения
    conjunctions_raw = [
        a
        for a in aspects
        if a["details"]["aspect"] == "conjunction" and a["details"]["orb"] <= max_orb
    ]

    # Группировать связанные соединения
    groups = []
    processed = set()

    for conj in conjunctions_raw:
        p1 = conj["details"]["from"]
        p2 = conj["details"]["to"]
        orb = conj["details"]["orb"]

        pair = tuple(sorted([p1, p2]))
        if pair in processed:
            continue

        # Найти группу с этими планетами
        found_group = None
        for group in groups:
            if p1 in group["planets"] or p2 in group["planets"]:
                found_group = group
                break

        if found_group:
            # Добавить в существующую группу
            found_group["planets"].add(p1)
            found_group["planets"].add(p2)
            found_group["orbs"][f"{p1}-{p2}"] = round(orb, 2)
        else:
            # Создать новую группу
            groups.append({"planets": {p1, p2}, "orbs": {f"{p1}-{p2}": round(orb, 2)}})

        processed.add(pair)

    # Фильтровать по min_planets и обогатить данными
    results = []
    for group in groups:
        if len(group["planets"]) >= min_planets:
            planets_list = sorted(list(group["planets"]))

            # Получить позиции планет
            planet_lons = {}
            for planet in planets_list:
                pos_fact = next(
                    (
                        f
                        for f in facts
                        if f["type"] == "planet_in_sign" and f["object"] == planet
                    ),
                    None,
                )
                if pos_fact:
                    planet_lons[planet] = pos_fact["details"]["longitude"]

            if planet_lons:
                avg_lon = sum(planet_lons.values()) / len(planet_lons)
                sign_num = int(avg_lon // 30)
                signs = [
                    "Aries",
                    "Taurus",
                    "Gemini",
                    "Cancer",
                    "Leo",
                    "Virgo",
                    "Libra",
                    "Scorpio",
                    "Sagittarius",
                    "Capricorn",
                    "Aquarius",
                    "Pisces",
                ]

                # Проверить тесноту (все орбисы < 3°)
                tight = all(o < 3.0 for o in group["orbs"].values())

                results.append(
                    {
                        "planets": planets_list,
                        "orbs": group["orbs"],
                        "average_longitude": round(avg_lon, 2),
                        "sign": signs[sign_num],
                        "tight": tight,
                        "max_orb": round(max(group["orbs"].values()), 2),
                    }
                )

    return {"found": len(results) > 0, "conjunctions": results, "count": len(results)}


def find_aspect_patterns(facts: list[dict], max_orb: float = 5.0) -> dict[str, Any]:
    """
    Найти все значимые аспектные паттерны в карте.

    Находит:
    - Grand Trine
    - T-Square
    - Grand Cross
    - Yod (Finger of God)
    - Kite
    - Stellium

    Returns:
        {
            "patterns": {
                "grand_trine": [...],
                "t_square": [...],
                "grand_cross": [...],
                "yod": [...],
                "kite": [...],
                "stellium": [...]
            },
            "total_count": int,
            "summary": str
        }
    """
    from .formula_validator import (
        _find_grand_trine,
        _find_t_square,
        _find_grand_cross,
        _find_yod,
        _find_kite,
        _find_stellium,
    )

    patterns = {
        "grand_trine": _find_grand_trine(facts, max_orb),
        "t_square": _find_t_square(facts, max_orb),
        "grand_cross": _find_grand_cross(facts, max_orb),
        "yod": _find_yod(facts, max_orb),
        "kite": _find_kite(facts, max_orb),
        "stellium": _find_stellium(facts, min_planets=3, max_degrees=10),
    }

    total = sum(p["count"] for p in patterns.values())

    # Создать текстовую сводку
    summary_parts = []
    for name, data in patterns.items():
        if data["found"]:
            summary_parts.append(f"{name}: {data['count']}")

    summary = ", ".join(summary_parts) if summary_parts else "No major patterns found"

    return {"patterns": patterns, "total_count": total, "summary": summary}


def find_critical_degrees(facts: list[dict]) -> dict[str, Any]:
    """
    Найти планеты на критических градусах.

    Критические градусы:
    - 0° (начало знака) - инициация
    - 29° (анаретический) - завершение, кризис
    - 15° (середина знака) - кульминация
    - Экзальтация планет (точные градусы)

    Returns:
        {
            "found": bool,
            "planets": {
                "anaretic": [{"planet": "Mars", "degree": 29.8, "sign": "Aries"}],
                "zero_degree": [...],
                "mid_degree": [...],
                "exaltation": [...]
            },
            "count": int
        }
    """
    planet_positions = []

    for fact in facts:
        if fact["type"] == "planet_in_sign" and fact["object"] in [
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
            "Ascendant",
            "Midheaven",
        ]:
            lon = fact["details"]["longitude"]
            degree_in_sign = lon % 30
            sign_num = int(lon // 30)
            signs = [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces",
            ]

            planet_positions.append(
                {
                    "planet": fact["object"],
                    "longitude": lon,
                    "degree_in_sign": degree_in_sign,
                    "sign": signs[sign_num],
                }
            )

    # Точные градусы экзальтации
    exaltation_degrees = {
        "Sun": (0, 19),  # Aries 19°
        "Moon": (1, 3),  # Taurus 3°
        "Mercury": (5, 15),  # Virgo 15°
        "Venus": (11, 27),  # Pisces 27°
        "Mars": (9, 28),  # Capricorn 28°
        "Jupiter": (3, 15),  # Cancer 15°
        "Saturn": (6, 21),  # Libra 21°
    }

    results = {
        "anaretic": [],  # 29°
        "zero_degree": [],  # 0°
        "mid_degree": [],  # 15°
        "exaltation": [],  # точные градусы экзальтации
    }

    for pos in planet_positions:
        deg = pos["degree_in_sign"]

        # 29° (анаретический градус) - critical threshold
        if deg >= 29.0:
            results["anaretic"].append(
                {
                    "planet": pos["planet"],
                    "degree": round(deg, 2),
                    "sign": pos["sign"],
                    "exact": deg >= 29.5,
                }
            )

        # 0° (начало знака) - ±0.5°
        if deg <= 0.5:
            results["zero_degree"].append(
                {
                    "planet": pos["planet"],
                    "degree": round(deg, 2),
                    "sign": pos["sign"],
                    "exact": deg <= 0.1,
                }
            )

        # 15° (середина знака) - ±0.5°
        if 14.5 <= deg <= 15.5:
            results["mid_degree"].append(
                {
                    "planet": pos["planet"],
                    "degree": round(deg, 2),
                    "sign": pos["sign"],
                    "exact": 14.9 <= deg <= 15.1,
                }
            )

        # Точный градус экзальтации - ±1°
        planet = pos["planet"]
        if planet in exaltation_degrees:
            exalt_sign_num, exalt_deg = exaltation_degrees[planet]
            current_sign_num = int(pos["longitude"] // 30)

            if current_sign_num == exalt_sign_num and abs(deg - exalt_deg) <= 1.0:
                results["exaltation"].append(
                    {
                        "planet": planet,
                        "degree": round(deg, 2),
                        "sign": pos["sign"],
                        "exaltation_degree": exalt_deg,
                        "orb": round(abs(deg - exalt_deg), 2),
                    }
                )

    total = sum(len(v) for v in results.values())

    return {"found": total > 0, "planets": results, "count": total}


def find_stelliums(
    facts: list[dict],
    min_planets: int = 3,
    max_degrees: int = 10,
    by_sign: bool = False,
) -> dict[str, Any]:
    """
    Найти stelliums (скопления планет).

    Args:
        facts: Факты из карты
        min_planets: Минимум планет в stellium (обычно 3)
        max_degrees: Максимальное расстояние между крайними планетами
        by_sign: True = stellium только в одном знаке, False = по градусам

    Returns:
        {
            "found": bool,
            "stelliums": [
                {
                    "planets": ["Sun", "Mercury", "Venus"],
                    "sign": "Aquarius",
                    "house": 10,
                    "span_degrees": 16.5,
                    "tight": False
                }
            ],
            "count": int
        }
    """
    from .formula_validator import _find_stellium

    result = _find_stellium(facts, min_planets, max_degrees)

    if not result["found"]:
        return result

    # Обогатить данными о домах
    for stellium in result["instances"]:
        # Найти дом для центра stellium
        avg_lon = stellium["average_longitude"]

        # Найти планету ближайшую к среднему градусу
        sample_planet = stellium["planets"][0]
        house_fact = next(
            (f for f in facts if f["type"] == "house" and f["object"] == sample_planet),
            None,
        )

        if house_fact:
            stellium["house"] = house_fact["details"]["house"]

        # Рассчитать фактический span
        planet_lons = []
        for planet in stellium["planets"]:
            pos_fact = next(
                (
                    f
                    for f in facts
                    if f["type"] == "planet_in_sign" and f["object"] == planet
                ),
                None,
            )
            if pos_fact:
                planet_lons.append(pos_fact["details"]["longitude"])

        if planet_lons:
            span = max(planet_lons) - min(planet_lons)
            stellium["span_degrees"] = round(span, 2)
            stellium["tight"] = span <= 8  # Считается tight если < 8°

    return {
        "found": result["found"],
        "stelliums": result["instances"],
        "count": result["count"],
    }


def find_retrogrades(facts: list[dict]) -> dict[str, Any]:
    """
    Найти все ретроградные планеты.

    Returns:
        {
            "found": bool,
            "planets": ["Mercury", "Venus", "Saturn"],
            "count": int,
            "multiple": bool  # 3+ планет retrograde = особое значение
        }
    """
    retrograde_facts = [
        f for f in facts if f["type"] == "retrograde" and f.get("value") == "Retrograde"
    ]

    planets = [f["object"] for f in retrograde_facts]

    return {
        "found": len(planets) > 0,
        "planets": planets,
        "count": len(planets),
        "multiple": len(planets) >= 3,
        "details": [
            {"planet": f["object"], "speed": f["details"].get("speed", 0)}
            for f in retrograde_facts
        ],
    }


def find_out_of_bounds(facts: list[dict]) -> dict[str, Any]:
    """
    Найти планеты "out of bounds" (деклинация > ±23.5°).

    Примечание: требует данных о деклинации (не всегда доступны).

    Returns:
        {
            "found": bool,
            "planets": [{"planet": "Moon", "declination": 25.3}],
            "count": int
        }
    """
    # TODO: требует расширения astro_adapter для получения declination
    # Временная заглушка
    return {
        "found": False,
        "planets": [],
        "count": 0,
        "note": "Declination data not yet implemented",
    }


def search_events(
    facts: list[dict], query: str, max_orb: float = 5.0
) -> dict[str, Any]:
    """
    Поиск событий/паттернов по текстовому запросу.

    Args:
        facts: Факты из карты
        query: Запрос (examples: "mars saturn", "grand trine", "stellium in aquarius")
        max_orb: Орбис для аспектов

    Returns:
        Результаты поиска в зависимости от query

    Examples:
        >>> search_events(facts, "mars saturn pluto")  # Найдет соединение
        >>> search_events(facts, "grand cross")        # Найдет Grand Cross
        >>> search_events(facts, "stellium")           # Найдет стеллиумы
        >>> search_events(facts, "retrograde")         # Найдет ретроградные планеты
    """
    query_lower = query.lower()

    # Определить тип запроса
    if (
        "grand" in query_lower
        or "t-square" in query_lower
        or "yod" in query_lower
        or "kite" in query_lower
    ):
        # Паттерны
        return find_aspect_patterns(facts, max_orb)

    elif "stellium" in query_lower:
        return find_stelliums(facts)

    elif "retrograde" in query_lower or "ретроград" in query_lower:
        return find_retrogrades(facts)

    elif "critical" in query_lower or "29" in query_lower or "0 degree" in query_lower:
        return find_critical_degrees(facts)

    else:
        # Попробовать найти соединение планет
        planet_names = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
            "pluto",
        ]

        planets_in_query = [p.capitalize() for p in planet_names if p in query_lower]

        if len(planets_in_query) >= 2:
            return find_conjunctions(facts, planets=planets_in_query, max_orb=max_orb)

        return {
            "error": f"Could not parse query: {query}",
            "suggestion": "Try: 'mars saturn', 'grand trine', 'stellium', 'retrograde', 'critical degrees'",
        }
