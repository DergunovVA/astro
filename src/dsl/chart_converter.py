"""
Конвертер данных натальной карты в формат для DSL Evaluator

Преобразует результаты расчета карты (из astro_adapter.natal_calculation)
в формат, ожидаемый Evaluator для выполнения DSL формул.
"""

from typing import Dict, Any, List


def sign_from_longitude(longitude: float) -> str:
    """
    Определить знак зодиака по долготе

    Args:
        longitude: Долгота планеты в градусах (0-360)

    Returns:
        Название знака (Aries, Taurus, ...)
    """
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

    sign_index = int(longitude // 30)
    return signs[sign_index % 12]


def degree_in_sign(longitude: float) -> float:
    """
    Градус планеты в знаке (0-30)

    Args:
        longitude: Долгота планеты в градусах (0-360)

    Returns:
        Градус в знаке (0.0 - 29.999...)
    """
    return longitude % 30


def house_from_longitude(longitude: float, houses: List[float]) -> int:
    """
    Определить дом планеты по её долготе и куспидам домов

    Args:
        longitude: Долгота планеты (0-360)
        houses: Список из 12 куспидов домов [45.6, 78.9, ...]

    Returns:
        Номер дома (1-12)
    """
    # Нормализуем долготу к диапазону 0-360
    longitude = longitude % 360

    # houses уже список из 12 элементов
    cusps = [h % 360 for h in houses]

    # Определяем дом методом сравнения с куспидами
    for i in range(12):
        current_cusp = cusps[i]
        next_cusp = cusps[(i + 1) % 12]

        # Обрабатываем переход через 0°
        if current_cusp < next_cusp:
            if current_cusp <= longitude < next_cusp:
                return i + 1
        else:  # Переход через 0° Овна
            if longitude >= current_cusp or longitude < next_cusp:
                return i + 1

    # Fallback (не должно случиться)
    return 1


def get_dignity(planet_name: str, sign: str) -> str:
    """
    Определить достоинство планеты в знаке

    Args:
        planet_name: Название планеты
        sign: Знак зодиака

    Returns:
        Достоинство: Rulership, Exaltation, Detriment, Fall, Neutral

    Note: Упрощенная версия. Для полной точности нужно использовать
          AstrologicalValidator из src.dsl.validator
    """
    # Управители (Rulership)
    rulership = {
        "Sun": ["Leo"],
        "Moon": ["Cancer"],
        "Mercury": ["Gemini", "Virgo"],
        "Venus": ["Taurus", "Libra"],
        "Mars": ["Aries", "Scorpio"],
        "Jupiter": ["Sagittarius", "Pisces"],
        "Saturn": ["Capricorn", "Aquarius"],
        "Uranus": ["Aquarius"],
        "Neptune": ["Pisces"],
        "Pluto": ["Scorpio"],
    }

    # Экзальтации (Exaltation)
    exaltation = {
        "Sun": "Aries",
        "Moon": "Taurus",
        "Mercury": "Virgo",
        "Venus": "Pisces",
        "Mars": "Capricorn",
        "Jupiter": "Cancer",
        "Saturn": "Libra",
    }

    # Изгнание (Detriment) - противоположный знак управления
    detriment = {
        "Sun": ["Aquarius"],
        "Moon": ["Capricorn"],
        "Mercury": ["Sagittarius", "Pisces"],
        "Venus": ["Aries", "Scorpio"],
        "Mars": ["Libra", "Taurus"],
        "Jupiter": ["Gemini", "Virgo"],
        "Saturn": ["Cancer", "Leo"],
    }

    # Падение (Fall) - противоположный знак экзальтации
    fall = {
        "Sun": "Libra",
        "Moon": "Scorpio",
        "Mercury": "Pisces",
        "Venus": "Virgo",
        "Mars": "Cancer",
        "Jupiter": "Capricorn",
        "Saturn": "Aries",
    }

    # Проверяем достоинства
    if planet_name in rulership and sign in rulership[planet_name]:
        return "Rulership"

    if planet_name in exaltation and sign == exaltation[planet_name]:
        return "Exaltation"

    if planet_name in detriment and sign in detriment[planet_name]:
        return "Detriment"

    if planet_name in fall and sign == fall[planet_name]:
        return "Fall"

    return "Neutral"


def convert_chart_for_evaluator(calc_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать результаты расчета карты в формат для DSL Evaluator

    Args:
        calc_result: Результат natal_calculation() с extended=True

    Returns:
        Словарь в формате для Evaluator:
        {
            'planets': {
                'Sun': {
                    'Sign': 'Capricorn',
                    'House': 9,
                    'Dignity': 'Neutral',
                    'Retrograde': False,
                    'Degree': 17.5,
                    'Longitude': 287.5
                },
                ...
            },
            'houses': {
                1: {'Sign': 'Taurus', 'Cusp': 45.6},
                ...
            }
        }
    """
    planets_data = calc_result.get("planets", {})
    houses_data = calc_result.get("houses", [])  # список из 12 куспидов

    # Конвертируем планеты
    converted_planets = {}

    for planet_name, planet_info in planets_data.items():
        # Пропускаем специальные объекты (North Node, Chiron и т.д.)
        # Оставляем только основные планеты
        if planet_name not in [
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
            continue

        # Если extended=True, planet_info - это dict
        # Если extended=False, planet_info - это float (только долгота)
        if isinstance(planet_info, dict):
            longitude = planet_info.get("longitude", 0.0)
            speed = planet_info.get("speed", 0.0)
            retrograde = planet_info.get("retrograde", False)
        else:
            longitude = float(planet_info)
            speed = 0.0
            retrograde = False

        sign = sign_from_longitude(longitude)
        degree = degree_in_sign(longitude)
        house = house_from_longitude(longitude, houses_data)
        dignity = get_dignity(planet_name, sign)

        converted_planets[planet_name] = {
            "Sign": sign,
            "House": house,
            "Dignity": dignity,
            "Retrograde": retrograde,
            "Degree": round(degree, 2),
            "Longitude": round(longitude, 2),
            "Speed": round(speed, 4),
        }

    # Конвертируем дома - houses_data это список из 12 элементов
    converted_houses = {}

    if isinstance(houses_data, list) and len(houses_data) == 12:
        for i, cusp_longitude in enumerate(houses_data, start=1):
            sign = sign_from_longitude(cusp_longitude)
            converted_houses[i] = {
                "Sign": sign,
                "Cusp": round(cusp_longitude, 2),
            }

    return {
        "planets": converted_planets,
        "houses": converted_houses,
    }


def format_dsl_result(
    formula: str, result: Any, chart_data: Dict[str, Any], verbose: bool = False
) -> str:
    """
    Форматировать результат выполнения DSL формулы

    Args:
        formula: Исходная формула
        result: Результат выполнения (обычно bool)
        chart_data: Данные карты (для контекста)
        verbose: Показать дополнительную информацию

    Returns:
        Отформатированная строка результата
    """
    lines = []

    # Заголовок
    lines.append("=" * 60)
    lines.append("DSL Formula Check")
    lines.append("=" * 60)

    # Формула
    lines.append(f"\nFormula: {formula}")

    # Результат
    result_symbol = "✅" if result else "❌"
    lines.append(f"\nResult: {result_symbol} {result}")

    if verbose:
        # Дополнительная информация о планетах в формуле
        lines.append("\n" + "-" * 60)
        lines.append("Chart Context:")
        lines.append("-" * 60)

        # Извлечь упоминания планет из формулы
        planets = chart_data.get("planets", {})
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
        ]:
            if planet_name in formula:
                planet_data = planets.get(planet_name, {})
                if planet_data:
                    lines.append(
                        f"\n{planet_name}:\n"
                        f"  Sign: {planet_data.get('Sign', 'N/A')}\n"
                        f"  House: {planet_data.get('House', 'N/A')}\n"
                        f"  Dignity: {planet_data.get('Dignity', 'N/A')}\n"
                        f"  Retrograde: {planet_data.get('Retrograde', False)}"
                    )

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
