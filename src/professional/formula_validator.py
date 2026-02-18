"""
Formula Validator - проверка астрологических формул и расчетов.

Для профессиональных астрологов: проверка правильности расчетов,
наличия специфических конфигураций, валидация достоинств.
"""

from typing import Any


def validate_aspect_orbs(facts: list[dict], strict: bool = False) -> dict[str, Any]:
    """
    Проверить правильность орбисов аспектов.

    Args:
        facts: Список фактов из calculate_natal_with_facts()
        strict: Строгий режим (True = традиционные орбисы по Лилли)

    Returns:
        {
            "valid": bool,
            "issues": [{"aspect": str, "issue": str, "expected_orb": float, "actual_orb": float}],
            "summary": {"total_aspects": int, "valid": int, "questionable": int}
        }
    """
    from src.core.orbs import PLANET_ORBS, ASPECT_ORB_MULTIPLIERS

    aspects = [f for f in facts if f["type"] == "aspect"]
    issues = []
    questionable = 0

    for asp in aspects:
        details = asp.get("details", {})
        orb = details.get("orb", 0)
        from_planet = details.get("from", "")
        to_planet = details.get("to", "")
        aspect_type = details.get("aspect", "")

        # Рассчитать максимальный допустимый орбис
        from_orb = PLANET_ORBS.get(from_planet, 5.0)
        to_orb = PLANET_ORBS.get(to_planet, 5.0)
        base_orb = min(from_orb, to_orb)  # Moiety method

        multiplier = ASPECT_ORB_MULTIPLIERS.get(aspect_type, 1.0)
        max_orb = base_orb * multiplier

        # Для strict mode - уменьшить орбисы
        if strict:
            max_orb *= 0.75  # Традиционный подход - более узкие орбисы

        # Проверка
        if orb > max_orb:
            issues.append(
                {
                    "aspect": f"{from_planet} {aspect_type} {to_planet}",
                    "issue": "orb_too_wide",
                    "expected_max_orb": round(max_orb, 2),
                    "actual_orb": round(orb, 2),
                    "severity": "error" if orb > max_orb * 1.2 else "warning",
                }
            )
            questionable += 1
        elif orb > max_orb * 0.9:
            # Близко к границе - предупреждение
            issues.append(
                {
                    "aspect": f"{from_planet} {aspect_type} {to_planet}",
                    "issue": "orb_near_limit",
                    "expected_max_orb": round(max_orb, 2),
                    "actual_orb": round(orb, 2),
                    "severity": "info",
                }
            )

    return {
        "valid": len([i for i in issues if i["severity"] == "error"]) == 0,
        "issues": issues,
        "summary": {
            "total_aspects": len(aspects),
            "valid": len(aspects) - questionable,
            "questionable": questionable,
            "strict_mode": strict,
        },
    }


def validate_dignities(facts: list[dict]) -> dict[str, Any]:
    """
    Проверить правильность расчета достоинств.

    Проверяет:
    - Essential dignities (domicile, exaltation, etc.)
    - Accidental dignities (house strength, motion)
    - Total dignity = essential + accidental

    Returns:
        {
            "valid": bool,
            "issues": [{"planet": str, "issue": str, "details": dict}],
            "planets": {planet: {"essential": int, "accidental": int, "total": int}}
        }
    """
    issues = []
    planet_dignities = {}

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
        # Найти факты о достоинствах
        ess_fact = next(
            (
                f
                for f in facts
                if f.get("object") == planet and f.get("type") == "essential_dignity"
            ),
            None,
        )
        acc_fact = next(
            (
                f
                for f in facts
                if f.get("object") == planet and f.get("type") == "accidental_dignity"
            ),
            None,
        )
        total_fact = next(
            (
                f
                for f in facts
                if f.get("object") == planet and f.get("type") == "total_dignity"
            ),
            None,
        )

        if not ess_fact or not acc_fact or not total_fact:
            issues.append(
                {
                    "planet": planet,
                    "issue": "missing_dignity_data",
                    "details": {
                        "has_essential": ess_fact is not None,
                        "has_accidental": acc_fact is not None,
                        "has_total": total_fact is not None,
                    },
                }
            )
            continue

        # Извлечь scores
        ess_score = ess_fact.get("details", {}).get("score", 0)
        acc_score = acc_fact.get("details", {}).get("score", 0)
        total_score = total_fact.get("details", {}).get("total_score", 0)

        planet_dignities[planet] = {
            "essential": ess_score,
            "accidental": acc_score,
            "total": total_score,
        }

        # Проверка арифметики
        expected_total = ess_score + acc_score
        if total_score != expected_total:
            issues.append(
                {
                    "planet": planet,
                    "issue": "total_dignity_mismatch",
                    "details": {
                        "essential": ess_score,
                        "accidental": acc_score,
                        "calculated_total": expected_total,
                        "actual_total": total_score,
                        "difference": total_score - expected_total,
                    },
                }
            )

        # Проверка диапазонов
        if ess_score < -10 or ess_score > 10:
            issues.append(
                {
                    "planet": planet,
                    "issue": "essential_dignity_out_of_range",
                    "details": {"score": ess_score, "expected_range": "(-10, +10)"},
                }
            )

        if acc_score < -10 or acc_score > 15:
            issues.append(
                {
                    "planet": planet,
                    "issue": "accidental_dignity_out_of_range",
                    "details": {"score": acc_score, "expected_range": "(-10, +15)"},
                }
            )

    return {"valid": len(issues) == 0, "issues": issues, "planets": planet_dignities}


def check_formula_exists(
    facts: list[dict], formula: str, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Проверить наличие конкретной астрологической формулы/конфигурации.

    Args:
        facts: Список фактов из карты
        formula: Тип формулы ("t-square", "grand-trine", "grand-cross", "yod", "kite", "stellium")
        config: Настройки поиска (max_orb, min_planets, etc.)

    Returns:
        {
            "found": bool,
            "instances": [{"planets": [...], "details": {...}}],
            "count": int
        }
    """
    config = config or {}
    max_orb = config.get("max_orb", 5.0)

    formula = formula.lower()

    if formula == "t-square":
        return _find_t_square(facts, max_orb)
    elif formula == "grand-trine":
        return _find_grand_trine(facts, max_orb)
    elif formula == "grand-cross":
        return _find_grand_cross(facts, max_orb)
    elif formula == "yod":
        return _find_yod(facts, max_orb)
    elif formula == "kite":
        return _find_kite(facts, max_orb)
    elif formula == "stellium":
        min_planets = config.get("min_planets", 3)
        max_degrees = config.get("max_degrees", 10)
        return _find_stellium(facts, min_planets, max_degrees)
    else:
        return {
            "found": False,
            "error": f"Unknown formula: {formula}",
            "available": [
                "t-square",
                "grand-trine",
                "grand-cross",
                "yod",
                "kite",
                "stellium",
            ],
        }


def _find_t_square(facts: list[dict], max_orb: float) -> dict[str, Any]:
    """T-Square: 2 planets in opposition + both square to 3rd planet."""
    aspects = [f for f in facts if f["type"] == "aspect"]
    instances = []

    # Найти все оппозиции
    oppositions = [
        a
        for a in aspects
        if a["details"]["aspect"] == "opposition" and a["details"]["orb"] <= max_orb
    ]

    for opp in oppositions:
        p1 = opp["details"]["from"]
        p2 = opp["details"]["to"]

        # Найти планеты в квадрате к обеим
        for asp in aspects:
            if asp["details"]["aspect"] != "square" or asp["details"]["orb"] > max_orb:
                continue

            p3 = asp["details"]["from"]
            p4 = asp["details"]["to"]

            # Проверить что p3 в квадрате к p1 и p2
            if p3 in [p1, p2] or p4 in [p1, p2]:
                continue

            # Найти вторую сторону квадрата
            apex = p3 if p4 in [p1, p2] else p4 if p3 in [p1, p2] else None
            if not apex:
                # Проверить более сложные случаи
                squares_to_p1 = [
                    a
                    for a in aspects
                    if a["details"]["aspect"] == "square"
                    and a["details"]["orb"] <= max_orb
                    and (a["details"]["from"] == p1 or a["details"]["to"] == p1)
                ]
                squares_to_p2 = [
                    a
                    for a in aspects
                    if a["details"]["aspect"] == "square"
                    and a["details"]["orb"] <= max_orb
                    and (a["details"]["from"] == p2 or a["details"]["to"] == p2)
                ]

                for sq1 in squares_to_p1:
                    apex_candidate = (
                        sq1["details"]["from"]
                        if sq1["details"]["to"] == p1
                        else sq1["details"]["to"]
                    )

                    # Проверить что этот же apex в квадрате к p2
                    if any(
                        apex_candidate in [sq["details"]["from"], sq["details"]["to"]]
                        for sq in squares_to_p2
                    ):
                        instances.append(
                            {
                                "planets": [p1, p2, apex_candidate],
                                "apex": apex_candidate,
                                "opposition": {
                                    "from": p1,
                                    "to": p2,
                                    "orb": opp["details"]["orb"],
                                },
                                "type": "T-Square",
                            }
                        )
                        break

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }


def _find_grand_trine(facts: list[dict], max_orb: float) -> dict[str, Any]:
    """Grand Trine: 3 planets all in trine to each other."""
    aspects = [f for f in facts if f["type"] == "aspect"]
    trines = [
        a
        for a in aspects
        if a["details"]["aspect"] == "trine" and a["details"]["orb"] <= max_orb
    ]

    instances = []
    checked = set()

    for t1 in trines:
        p1 = t1["details"]["from"]
        p2 = t1["details"]["to"]

        # Найти третью планету в трине к обеим
        for t2 in trines:
            if t2 == t1:
                continue

            planets_in_t2 = {t2["details"]["from"], t2["details"]["to"]}
            if p1 in planets_in_t2:
                p3 = (
                    t2["details"]["to"]
                    if t2["details"]["from"] == p1
                    else t2["details"]["from"]
                )
            elif p2 in planets_in_t2:
                p3 = (
                    t2["details"]["to"]
                    if t2["details"]["from"] == p2
                    else t2["details"]["from"]
                )
            else:
                continue

            # Проверить что p2 и p3 тоже в трине
            if any(
                set([a["details"]["from"], a["details"]["to"]]) == {p2, p3}
                and a["details"]["aspect"] == "trine"
                and a["details"]["orb"] <= max_orb
                for a in trines
            ):
                planets_set = tuple(sorted([p1, p2, p3]))
                if planets_set not in checked:
                    instances.append(
                        {"planets": list(planets_set), "type": "Grand Trine"}
                    )
                    checked.add(planets_set)

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }


def _find_grand_cross(facts: list[dict], max_orb: float) -> dict[str, Any]:
    """Grand Cross: 4 planets, 2 oppositions, all square to each other."""
    aspects = [f for f in facts if f["type"] == "aspect"]
    oppositions = [
        a
        for a in aspects
        if a["details"]["aspect"] == "opposition" and a["details"]["orb"] <= max_orb
    ]

    instances = []
    checked = set()

    for opp1 in oppositions:
        p1, p2 = opp1["details"]["from"], opp1["details"]["to"]

        for opp2 in oppositions:
            if opp2 == opp1:
                continue

            p3, p4 = opp2["details"]["from"], opp2["details"]["to"]

            if len({p1, p2, p3, p4}) != 4:
                continue

            # Проверить что все 4 планеты в квадратах
            squares = [
                a
                for a in aspects
                if a["details"]["aspect"] == "square" and a["details"]["orb"] <= max_orb
            ]
            square_pairs = {
                frozenset([sq["details"]["from"], sq["details"]["to"]])
                for sq in squares
            }

            required_squares = [
                frozenset([p1, p3]),
                frozenset([p1, p4]),
                frozenset([p2, p3]),
                frozenset([p2, p4]),
            ]

            if all(pair in square_pairs for pair in required_squares):
                planets_set = tuple(sorted([p1, p2, p3, p4]))
                if planets_set not in checked:
                    instances.append(
                        {"planets": list(planets_set), "type": "Grand Cross"}
                    )
                    checked.add(planets_set)

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }


def _find_yod(facts: list[dict], max_orb: float) -> dict[str, Any]:
    """Yod (Finger of God): 2 planets in sextile + both quincunx to 3rd (apex)."""
    aspects = [f for f in facts if f["type"] == "aspect"]
    sextiles = [
        a
        for a in aspects
        if a["details"]["aspect"] == "sextile" and a["details"]["orb"] <= max_orb
    ]
    quincunxes = [
        a
        for a in aspects
        if a["details"]["aspect"] == "quincunx" and a["details"]["orb"] <= max_orb
    ]

    instances = []

    for sextile in sextiles:
        p1 = sextile["details"]["from"]
        p2 = sextile["details"]["to"]

        # Найти планету в квинконсе к обеим
        for q1 in quincunxes:
            planets_in_q1 = {q1["details"]["from"], q1["details"]["to"]}

            if p1 in planets_in_q1:
                apex = (
                    q1["details"]["to"]
                    if q1["details"]["from"] == p1
                    else q1["details"]["from"]
                )

                # Проверить что apex также в квинконсе к p2
                if any(
                    set([a["details"]["from"], a["details"]["to"]]) == {p2, apex}
                    and a["details"]["aspect"] == "quincunx"
                    and a["details"]["orb"] <= max_orb
                    for a in quincunxes
                ):
                    instances.append(
                        {
                            "planets": [p1, p2, apex],
                            "apex": apex,
                            "base": [p1, p2],
                            "type": "Yod",
                        }
                    )

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }


def _find_kite(facts: list[dict], max_orb: float) -> dict[str, Any]:
    """Kite: Grand Trine + 4th planet opposite one corner and sextile to other two."""
    grand_trines = _find_grand_trine(facts, max_orb)

    if not grand_trines["found"]:
        return {"found": False, "instances": [], "count": 0}

    aspects = [f for f in facts if f["type"] == "aspect"]
    instances = []

    for gt in grand_trines["instances"]:
        p1, p2, p3 = gt["planets"]

        # Найти планету в оппозиции к одной из вершин
        oppositions = [
            a
            for a in aspects
            if a["details"]["aspect"] == "opposition" and a["details"]["orb"] <= max_orb
        ]

        for opp in oppositions:
            if p1 in [opp["details"]["from"], opp["details"]["to"]]:
                p4 = (
                    opp["details"]["to"]
                    if opp["details"]["from"] == p1
                    else opp["details"]["from"]
                )
                opposite_to = p1
                other_two = [p2, p3]
            elif p2 in [opp["details"]["from"], opp["details"]["to"]]:
                p4 = (
                    opp["details"]["to"]
                    if opp["details"]["from"] == p2
                    else opp["details"]["from"]
                )
                opposite_to = p2
                other_two = [p1, p3]
            elif p3 in [opp["details"]["from"], opp["details"]["to"]]:
                p4 = (
                    opp["details"]["to"]
                    if opp["details"]["from"] == p3
                    else opp["details"]["from"]
                )
                opposite_to = p3
                other_two = [p1, p2]
            else:
                continue

            # Проверить что p4 в секстиле к двум другим вершинам
            sextiles = [
                a
                for a in aspects
                if a["details"]["aspect"] == "sextile"
                and a["details"]["orb"] <= max_orb
            ]
            sextile_pairs = {
                frozenset([sx["details"]["from"], sx["details"]["to"]])
                for sx in sextiles
            }

            if all(frozenset([p4, other]) in sextile_pairs for other in other_two):
                instances.append(
                    {
                        "planets": [p1, p2, p3, p4],
                        "grand_trine": [p1, p2, p3],
                        "kite_point": p4,
                        "opposite_to": opposite_to,
                        "type": "Kite",
                    }
                )

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }


def _find_stellium(
    facts: list[dict], min_planets: int, max_degrees: int
) -> dict[str, Any]:
    """Stellium: 3+ planets within max_degrees."""
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
        ]:
            planet_positions.append(
                {"planet": fact["object"], "longitude": fact["details"]["longitude"]}
            )

    instances = []
    checked = set()

    for i, p1 in enumerate(planet_positions):
        cluster = [p1]

        for p2 in planet_positions[i + 1 :]:
            # Вычислить угловое расстояние
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

                instances.append(
                    {
                        "planets": list(planets_set),
                        "count": len(cluster),
                        "sign": signs[sign_num],
                        "average_longitude": round(avg_lon, 2),
                        "type": "Stellium",
                    }
                )
                checked.add(planets_set)

    return {
        "found": len(instances) > 0,
        "instances": instances,
        "count": len(instances),
    }
