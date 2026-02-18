"""
Event Finder - поиск значимых астрологических событий и паттернов.

Для профессиональных астрологов: поиск конкретных конфигураций,
соединений планет, критических градусов, специфических паттернов.

Version 2: работает с реальной структурой фактов из calculate_natal_with_facts()
"""

from typing import Any


def _parse_aspect_object(obj_string: str) -> tuple[str, str] | None:
    """Parse 'Planet1-Planet2' format."""
    if "-" not in obj_string:
        return None
    parts = obj_string.split("-", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return None


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
            "conjunctions": [{planets: [...], orbs: {...}, sign: "...", tight: bool}],
            "count": int
        }
    """
    # Собрать все соединения
    conjunctions_raw = []

    for fact in facts:
        if fact.get("type") != "aspect" or fact.get("value") != "conjunction":
            continue

        orb = fact.get("details", {}).get("orb", 999)
        if orb > max_orb:
            continue

        parsed = _parse_aspect_object(fact.get("object", ""))
        if not parsed:
            continue

        p1, p2 = parsed

        # Фильтр по планетам
        if planets and (p1 not in planets or p2 not in planets):
            continue

        conjunctions_raw.append({"p1": p1, "p2": p2, "orb": orb})

    if not conjunctions_raw:
        return {"found": False, "conjunctions": [], "count": 0}

    # Группировать связанные планеты
    groups = []
    for conj in conjunctions_raw:
        p1, p2, orb = conj["p1"], conj["p2"], conj["orb"]

        # Найти группу с этими планетами
        found_group = None
        for group in groups:
            if p1 in group["planets"] or p2 in group["planets"]:
                found_group = group
                break

        if found_group:
            found_group["planets"].add(p1)
            found_group["planets"].add(p2)
            found_group["orbs"][f"{p1}-{p2}"] = round(orb, 2)
        else:
            groups.append({"planets": {p1, p2}, "orbs": {f"{p1}-{p2}": round(orb, 2)}})

    # Обогатить данными
    results = []
    for group in groups:
        if len(group["planets"]) < min_planets:
            continue

        planets_list = sorted(list(group["planets"]))

        # Получить позиции планет
        planet_lons = {}
        for planet in planets_list:
            pos_fact = next(
                (
                    f
                    for f in facts
                    if f.get("type") == "planet_in_sign" and f.get("object") == planet
                ),
                None,
            )
            if pos_fact:
                planet_lons[planet] = pos_fact.get("details", {}).get("longitude", 0)

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


def find_stelliums(
    facts: list[dict], min_planets: int = 3, max_degrees: int = 10
) -> dict[str, Any]:
    """Найти стеллиумы (скопления планет)."""
    planet_positions = []

    for fact in facts:
        if fact.get("type") == "planet_in_sign" and fact.get("object") in [
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
        ]:
            lon = fact.get("details", {}).get("longitude")
            if lon is not None:
                planet_positions.append({"planet": fact["object"], "longitude": lon})

    results = []
    checked = set()

    for i, p1 in enumerate(planet_positions):
        cluster = [p1]

        for p2 in planet_positions[i + 1 :]:
            diff = abs(p1["longitude"] - p2["longitude"])
            if diff > 180:
                diff = 360 - diff

            if diff <= max_degrees:
                cluster.append(p2)

        if len(cluster) >= min_planets:
            planets_set = tuple(sorted([p["planet"] for p in cluster]))
            if planets_set not in checked:
                avg_lon = sum(p["longitude"] for p in cluster) / len(cluster)
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

                results.append(
                    {
                        "planets": list(planets_set),
                        "count": len(cluster),
                        "sign": signs[sign_num],
                        "average_longitude": round(avg_lon, 2),
                        "tight": all(
                            abs(p["longitude"] - avg_lon) < 8 for p in cluster
                        ),
                    }
                )
                checked.add(planets_set)

    return {"found": len(results) > 0, "stelliums": results, "count": len(results)}


def find_retrogrades(facts: list[dict]) -> dict[str, Any]:
    """Найти ретроградные планеты."""
    retrogrades = []

    for fact in facts:
        if fact.get("type") == "retrograde" and fact.get("value") == "Retrograde":
            retrogrades.append(fact.get("object"))

    return {
        "found": len(retrogrades) > 0,
        "planets": retrogrades,
        "count": len(retrogrades),
        "multiple": len(retrogrades) >= 3,
    }


def find_critical_degrees(facts: list[dict]) -> dict[str, Any]:
    """Найти планеты на критических градусах (0°, 29°, экзальтация)."""
    results = {
        "anaretic": [],  # 29°
        "zero_degree": [],  # 0°
        "exaltation": [],  # точные градусы экзальтации
    }

    exaltation_degrees = {
        "Sun": (0, 19),  # Aries 19°
        "Moon": (1, 3),  # Taurus 3°
        "Venus": (11, 27),  # Pisces 27°
        "Mars": (9, 28),  # Capricorn 28°
        "Jupiter": (3, 15),  # Cancer 15°
        "Saturn": (6, 21),  # Libra 21°
    }

    for fact in facts:
        if fact.get("type") != "planet_in_sign":
            continue

        planet = fact.get("object")
        lon = fact.get("details", {}).get("longitude")

        if lon is None:
            continue

        deg_in_sign = lon % 30
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

        # 29° (анаретический)
        if deg_in_sign >= 29.0:
            results["anaretic"].append(
                {
                    "planet": planet,
                    "degree": round(deg_in_sign, 2),
                    "sign": signs[sign_num],
                }
            )

        # 0° (начало знака)
        if deg_in_sign <= 0.5:
            results["zero_degree"].append(
                {
                    "planet": planet,
                    "degree": round(deg_in_sign, 2),
                    "sign": signs[sign_num],
                }
            )

        # Экзальтация
        if planet in exaltation_degrees:
            exalt_sign_num, exalt_deg = exaltation_degrees[planet]
            if sign_num == exalt_sign_num and abs(deg_in_sign - exalt_deg) <= 1.0:
                results["exaltation"].append(
                    {
                        "planet": planet,
                        "degree": round(deg_in_sign, 2),
                        "sign": signs[sign_num],
                        "exaltation_degree": exalt_deg,
                        "orb": round(abs(deg_in_sign - exalt_deg), 2),
                    }
                )

    total = sum(len(v) for v in results.values())

    return {"found": total > 0, "planets": results, "count": total}


def find_aspect_patterns(facts: list[dict], max_orb: float = 5.0) -> dict[str, Any]:
    """
    Найти основные аспектные паттерны.

    Note: Полная реализация Grand Trine, T-Square требует сложной логики.
    Пока возвращаем базовую информацию.
    """
    return {
        "found": False,
        "patterns": {
            "grand_trine": {"found": False, "count": 0},
            "t_square": {"found": False, "count": 0},
            "grand_cross": {"found": False, "count": 0},
            "yod": {"found": False, "count": 0},
        },
        "total_count": 0,
        "summary": "Pattern detection not fully implemented yet",
        "note": "Use formula_validator.check_formula_exists() for specific patterns",
    }


def search_events(
    facts: list[dict], query: str, max_orb: float = 5.0
) -> dict[str, Any]:
    """
    Поиск событий/паттернов по текстовому запросу.

    Args:
        facts: Факты из карты
        query: Запрос (e.g., "mars saturn", "stellium", "retrograde")
        max_orb: Орбис для аспектов

    Returns:
        Результаты поиска
    """
    query_lower = query.lower()

    # Определить тип запроса
    if "stellium" in query_lower or "стеллиум" in query_lower:
        return find_stelliums(facts)

    elif "retrograde" in query_lower or "ретроград" in query_lower:
        return find_retrogrades(facts)

    elif (
        "critical" in query_lower
        or "29" in query_lower
        or "0 degree" in query_lower
        or "критич" in query_lower
    ):
        return find_critical_degrees(facts)

    elif "pattern" in query_lower or "паттерн" in query_lower:
        return find_aspect_patterns(facts, max_orb)

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
        elif len(planets_in_query) == 1:
            # Найти все соединения с этой планетой
            return find_conjunctions(
                facts, planets=planets_in_query, max_orb=max_orb, min_planets=2
            )

        return {
            "error": f"Could not parse query: {query}",
            "suggestion": "Try: 'mars saturn pluto', 'stellium', 'retrograde', 'critical degrees'",
        }
