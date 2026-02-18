"""
Примеры использования профессиональных инструментов.

Для астрологов, разработчиков API, и создателей ботов/плагинов.
"""

import json
from src.professional import (
    find_conjunctions,
    find_aspect_patterns,
    find_stelliums,
    find_critical_degrees,
    validate_aspect_orbs,
    validate_dignities,
    check_formula_exists,
)


def example_find_mars_saturn_pluto(chart_data: dict):
    """
    Пример: найти соединение Mars-Saturn-Pluto в карте.

    Use case: Проверить наличие конкретной конфигурации
    """
    facts = chart_data.get("facts", [])

    result = find_conjunctions(facts, planets=["Mars", "Saturn", "Pluto"], max_orb=5.0)

    if result["found"]:
        for conj in result["conjunctions"]:
            print(f"✨ Найдено соединение: {' + '.join(conj['planets'])}")
            print(f"   Знак: {conj['sign']}")
            print(f"   Средний градус: {conj['average_longitude']:.2f}°")
            print(f"   Тесное: {'Да' if conj['tight'] else 'Нет'}")
            print(f"   Орбисы: {conj['orbs']}")
    else:
        print("❌ Соединение Mars-Saturn-Pluto не найдено")

    return result


def example_find_all_patterns(chart_data: dict):
    """
    Пример: найти все значимые паттерны в карте.

    Use case: Полный анализ конфигураций
    """
    facts = chart_data.get("facts", [])

    patterns = find_aspect_patterns(facts, max_orb=5.0)

    print(f"\n📊 Паттерны в карте: {patterns['total_count']}")
    print(f"   {patterns['summary']}\n")

    for pattern_type, data in patterns["patterns"].items():
        if data["found"]:
            print(f"\n🔸 {pattern_type.upper()}: {data['count']} найдено")
            for instance in data["instances"]:
                print(f"   • Планеты: {', '.join(instance['planets'])}")
                if "apex" in instance:
                    print(f"     Apex: {instance['apex']}")

    return patterns


def example_validate_calculations(chart_data: dict):
    """
    Пример: проверить правильность расчетов.

    Use case: QA, тестирование, верификация данных
    """
    facts = chart_data.get("facts", [])

    print("\n🔍 Проверка орбисов аспектов...")
    orb_check = validate_aspect_orbs(facts, strict=False)

    if orb_check["valid"]:
        print(
            f"✅ Все орбисы корректны ({orb_check['summary']['total_aspects']} аспектов)"
        )
    else:
        print("⚠️  Найдены проблемы:")
        for issue in orb_check["issues"]:
            if issue["severity"] == "error":
                print(
                    f"   ❌ {issue['aspect']}: орбис {issue['actual_orb']}° > {issue['expected_max_orb']}°"
                )

    print("\n🔍 Проверка достоинств...")
    dignity_check = validate_dignities(facts)

    if dignity_check["valid"]:
        print("✅ Все достоинства рассчитаны верно")
    else:
        print("⚠️  Найдены ошибки:")
        for issue in dignity_check["issues"]:
            print(f"   ❌ {issue['planet']}: {issue['issue']}")

    return {"orbs": orb_check, "dignities": dignity_check}


def example_check_specific_formula(chart_data: dict, formula: str = "t-square"):
    """
    Пример: проверить наличие конкретной формулы.

    Use case: Поиск специфической конфигурации
    """
    facts = chart_data.get("facts", [])

    result = check_formula_exists(facts, formula, config={"max_orb": 5.0})

    if result["found"]:
        print(f"\n✨ {formula.upper()} найден! ({result['count']} шт.)")
        for instance in result["instances"]:
            print(f"   • {instance}")
    else:
        print(f"\n❌ {formula.upper()} не найден")

    return result


def example_telegram_bot_response(chart_data: dict, user_query: str):
    """
    Пример: ответ Telegram-бота на запрос пользователя.

    Use case: Интеграция с ботом
    """
    from src.professional.event_finder import search_events

    facts = chart_data.get("facts", [])
    result = search_events(facts, user_query)

    # Форматировать ответ для Telegram
    if "error" in result:
        return f"❓ {result['error']}\n💡 {result.get('suggestion', '')}"

    if result.get("found"):
        if "conjunctions" in result:
            msg = "✨ Найденные соединения:\n"
            for conj in result["conjunctions"]:
                msg += f"\n🔸 {' + '.join(conj['planets'])}\n"
                msg += f"   📍 {conj['sign']} ({conj['average_longitude']:.1f}°)\n"
                if conj["tight"]:
                    msg += "   ⚡ Очень тесное соединение!\n"
            return msg

        elif "patterns" in result:
            msg = f"📊 Найдено паттернов: {result['total_count']}\n\n"
            msg += result["summary"]
            return msg

        elif "planets" in result and isinstance(result["planets"], list):
            # Retrograde
            msg = f"♻️ Ретроградные планеты: {len(result['planets'])}\n"
            msg += "\n".join([f"• {p}" for p in result["planets"]])
            return msg

    return "🤷 Ничего не найдено"


def example_api_endpoint(chart_data: dict):
    """
    Пример: REST API endpoint для веб-приложения.

    Use case: Backend для сайта/приложения

    GET /api/chart/analysis
    Returns:
        {
            "patterns": {...},
            "critical_planets": {...},
            "stelliums": {...},
            "validation": {...}
        }
    """
    facts = chart_data.get("facts", [])

    analysis = {
        "patterns": find_aspect_patterns(facts),
        "critical_planets": find_critical_degrees(facts),
        "stelliums": find_stelliums(facts),
        "validation": {
            "orbs": validate_aspect_orbs(facts),
            "dignities": validate_dignities(facts),
        },
    }

    return analysis


def example_wordpress_plugin(chart_data: dict):
    """
    Пример: WordPress плагин "Astro Widget".

    Use case: Виджет для сайта

    Shortcode: [astro_chart user_id="123" show="patterns,stellium"]
    """
    facts = chart_data.get("facts", [])

    # Минимальный набор для виджета
    widget_data = {
        "sun_sign": next(
            (
                f["value"]
                for f in facts
                if f["object"] == "Sun" and f["type"] == "planet_in_sign"
            ),
            "?",
        ),
        "moon_sign": next(
            (
                f["value"]
                for f in facts
                if f["object"] == "Moon" and f["type"] == "planet_in_sign"
            ),
            "?",
        ),
        "ascendant": next(
            (
                f["value"]
                for f in facts
                if f["object"] == "Ascendant" and f["type"] == "planet_in_sign"
            ),
            "?",
        ),
        "patterns": find_aspect_patterns(facts)["summary"],
        "stelliums": find_stelliums(facts)["count"],
    }

    # HTML для WordPress
    html = f"""
    <div class="astro-widget">
        <h3>Ваша натальная карта</h3>
        <p>☉ Солнце: {widget_data["sun_sign"]}</p>
        <p>☽ Луна: {widget_data["moon_sign"]}</p>
        <p>⬆️ Асцендент: {widget_data["ascendant"]}</p>
        <p>✨ Паттерны: {widget_data["patterns"]}</p>
        <p>🌟 Стеллиумов: {widget_data["stelliums"]}</p>
    </div>
    """

    return html


# Если запустить этот файл напрямую
if __name__ == "__main__":
    import sys
    import os

    # Добавить parent dir в PATH
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src.modules.natal_calculation import calculate_natal_with_facts
    from src.input_pipeline.normalize_input import normalize_input, InputContext

    print("=" * 70)
    print("           ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ PROFESSIONAL TOOLS")
    print("=" * 70)

    # Пример данных (можно заменить на реальные)
    test_date = "1982-01-08"
    test_time = "13:40"
    test_place = "Saratov"

    print(f"\nТестовая карта: {test_date} {test_time} {test_place}\n")

    try:
        # Получить данные карты
        ni = normalize_input(test_date, test_time, test_place)
        ctx = InputContext.from_normalized(ni)
        chart_data = calculate_natal_with_facts(
            ctx.utc_dt, ctx.lat, ctx.lon, extended=True
        )

        # Примеры
        print("\n" + "=" * 70)
        print("1. ПОИСК СОЕДИНЕНИЯ MARS-SATURN-PLUTO")
        print("=" * 70)
        example_find_mars_saturn_pluto(chart_data)

        print("\n" + "=" * 70)
        print("2. ПОИСК ВСЕХ ПАТТЕРНОВ")
        print("=" * 70)
        example_find_all_patterns(chart_data)

        print("\n" + "=" * 70)
        print("3. ВАЛИДАЦИЯ РАСЧЕТОВ")
        print("=" * 70)
        example_validate_calculations(chart_data)

        print("\n" + "=" * 70)
        print("4. КРИТИЧЕСКИЕ ГРАДУСЫ")
        print("=" * 70)
        critical = find_critical_degrees(chart_data["facts"])
        if critical["found"]:
            print(f"Найдено планет на критических градусах: {critical['count']}")
            for category, planets in critical["planets"].items():
                if planets:
                    print(f"\n{category}:")
                    for p in planets:
                        print(f"  • {p}")

        print("\n" + "=" * 70)
        print("5. TELEGRAM BOT ПРИМЕР")
        print("=" * 70)
        bot_response = example_telegram_bot_response(chart_data, "mars saturn pluto")
        print(bot_response)

        print("\n" + "=" * 70)
        print("6. API ENDPOINT ПРИМЕР")
        print("=" * 70)
        api_data = example_api_endpoint(chart_data)
        print(json.dumps(api_data, indent=2, ensure_ascii=False)[:500] + "...")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
