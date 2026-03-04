"""
Массовое тестирование астрологических функций на реальных личностях

Проверяет точность интерпретаций, сравнивая:
- Расчетные данные
- Психологический анализ
- Известные факты о человеке
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from modules.astro_adapter import natal_calculation  # noqa: E402
from modules.interpretation_layer import facts_from_calculation  # noqa: E402
from modules.psychological_layer import get_psychological_analysis  # noqa: E402
from input_pipeline import normalize_input, InputContext  # noqa: E402


def load_test_profiles():
    """Загрузить тестовые профили"""
    profiles_file = Path(__file__).parent / "test_profiles.json"
    with open(profiles_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["profiles"]


def analyze_profile(profile):
    """Полный анализ профиля"""
    print(f"\n{'=' * 80}")
    print(f"Анализ: {profile['name']} ({profile['profession']})")
    print(f"{'=' * 80}")

    try:
        # Normalize input
        ni = normalize_input(profile["date"], profile["time"], profile["place"])
        ctx = InputContext.from_normalized(ni)

        # Calculate
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon, extended=True)
        facts = facts_from_calculation(calc_result)

        # Psychological analysis
        psych = get_psychological_analysis(calc_result, facts)

        # Extract key info
        planets = calc_result["planets"]

        # Sun sign
        sun_pos = planets.get("Sun", {})
        if isinstance(sun_pos, dict):
            sun_lon = sun_pos.get("longitude", 0)
        else:
            sun_lon = sun_pos

        sun_sign_idx = int(sun_lon / 30)
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
        sun_sign = signs[sun_sign_idx]

        # Moon sign
        moon_pos = planets.get("Moon", {})
        if isinstance(moon_pos, dict):
            moon_lon = moon_pos.get("longitude", 0)
        else:
            moon_lon = moon_pos
        moon_sign = signs[int(moon_lon / 30)]

        # Ascendant
        houses = calc_result["houses"]
        asc_sign = signs[int(houses[0] / 30)]

        # MC (10th house cusp)
        mc_sign = signs[int(houses[9] / 30)]

        # Key aspects (major hard)
        hard_aspects = []
        for fact in facts:
            if fact.type == "aspect" and fact.value in ["square", "opposition"]:
                orb = (fact.details or {}).get("orb", 0)
                if orb < 6:  # Tight orbs only
                    hard_aspects.append(
                        {"planets": fact.object, "type": fact.value, "orb": orb}
                    )

        # Sort by tightness
        hard_aspects.sort(key=lambda x: x["orb"])

        # Demons
        demons = psych["demons"][:3]  # Top 3

        # Proofs
        proofs = psych["proofs"]

        # Results
        result = {
            "profile": profile,
            "chart": {
                "sun": sun_sign,
                "moon": moon_sign,
                "ascendant": asc_sign,
                "mc": mc_sign,
            },
            "key_aspects": hard_aspects[:5],
            "demons": demons,
            "proofs": proofs,
            "metadata": {
                "location": f"{ctx.lat:.2f}, {ctx.lon:.2f}",
                "timezone": ctx.tz_name,
            },
        }

        # Print summary
        print("\n📊 ОСНОВА:")
        print(f"  ☉ Sun: {sun_sign}")
        print(f"  ☽ Moon: {moon_sign}")
        print(f"  ↑ ASC: {asc_sign}")
        print(f"  ⟨ MC: {mc_sign}")

        print("\n🔥 КЛЮЧЕВЫЕ АСПЕКТЫ (напряженные):")
        for asp in hard_aspects[:5]:
            print(f"  • {asp['planets']} {asp['type']} (орб: {asp['orb']:.1f}°)")

        print("\n😈 ДЕМОНЫ (психологические конфликты):")
        for demon in demons:
            print(f"  • {demon['planet']}: {demon['description']}")

        if proofs:
            print("\n💪 ДОКАЗУХИ (компенсации):")
            for proof in proofs:
                print(
                    f"  • {proof['planet']} в {proof['sign']}: {proof['description']}"
                )

        print("\n✅ ОЖИДАЕМЫЕ ЧЕРТЫ:")
        for trait in profile["expected_traits"]:
            print(f"  - {trait}")

        print("\n🤔 СООТВЕТСТВИЕ:")
        # Analysis matching
        matches = analyze_matching(result, profile["expected_traits"])
        for match in matches:
            print(f"  {match}")

        return result

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return None


def analyze_matching(result, expected_traits):
    """Анализ соответствия ожиданиям"""
    matches = []

    chart = result["chart"]
    demons = result["demons"]
    result["proofs"]
    aspects = result["key_aspects"]

    # Check for common patterns
    if "Control" in " ".join(expected_traits) or "control" in " ".join(expected_traits):
        # Look for Pluto/Saturn emphasis
        pluto_aspects = [a for a in aspects if "Pluto" in a["planets"]]
        saturn_aspects = [a for a in aspects if "Saturn" in a["planets"]]
        if pluto_aspects or saturn_aspects:
            matches.append("✓ Control themes: Pluto/Saturn aspects present")

    if "Innovation" in " ".join(expected_traits) or "Revolutionary" in " ".join(
        expected_traits
    ):
        # Look for Uranus/Aquarius
        if "Aquarius" in [chart["sun"], chart["moon"], chart["ascendant"]]:
            matches.append("✓ Innovation: Aquarius placement")

    if "Perfectionism" in " ".join(expected_traits):
        # Sun-Saturn or Virgo
        sun_saturn = any(
            "Sun" in a["planets"] and "Saturn" in a["planets"] for a in aspects
        )
        if sun_saturn:
            matches.append("✓ Perfectionism: Sun-Saturn aspect (demon of unworthiness)")
        if "Virgo" in [chart["sun"], chart["moon"], chart["ascendant"]]:
            matches.append("✓ Perfectionism: Virgo placement")

    if "Power" in " ".join(expected_traits):
        # Pluto, Scorpio, or 8th house emphasis
        if "Scorpio" in [chart["sun"], chart["moon"], chart["mc"]]:
            matches.append("✓ Power focus: Scorpio placement")

    if "Psychological" in " ".join(expected_traits) or "depth" in " ".join(
        expected_traits
    ):
        # Scorpio, 8th house, Pluto
        if "Scorpio" in [chart["sun"], chart["moon"]]:
            matches.append("✓ Psychological depth: Scorpio placement")

    if "Communication" in " ".join(expected_traits):
        # Mercury, Gemini, 3rd house
        if "Gemini" in [chart["sun"], chart["moon"]]:
            matches.append("✓ Communication: Gemini placement")

    if "Creativity" in " ".join(expected_traits) or "Artist" in " ".join(
        expected_traits
    ):
        # Neptune, Pisces, Venus, Leo
        if chart["sun"] in ["Leo", "Pisces"]:
            matches.append(f"✓ Creativity: {chart['sun']} Sun")

    if "Transformation" in " ".join(expected_traits):
        # Pluto, Scorpio
        pluto_aspects = [a for a in aspects if "Pluto" in a["planets"]]
        if pluto_aspects:
            matches.append(f"✓ Transformation: {len(pluto_aspects)} Pluto aspects")

    # Demons matching
    for demon in demons:
        desc = demon["description"].lower()
        if "недостойности" in desc and "Perfectionism" in " ".join(expected_traits):
            matches.append("✓ Perfectionism confirmed by demon analysis")
        if "власт" in desc and "Power" in " ".join(expected_traits):
            matches.append("✓ Power issues confirmed by demon analysis")

    if not matches:
        matches.append("⚠ No obvious matches found (need deeper analysis)")

    return matches


def compare_profiles(results):
    """Сравнение профилей"""
    print(f"\n{'=' * 80}")
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ")
    print(f"{'=' * 80}\n")

    # Table header
    print(f"{'Name':<20} {'Sun':<10} {'Moon':<10} {'ASC':<10} {'Top Demon':<30}")
    print("-" * 80)

    for res in results:
        if res:
            name = res["profile"]["name"][:20]
            sun = res["chart"]["sun"]
            moon = res["chart"]["moon"]
            asc = res["chart"]["ascendant"]
            demon = res["demons"][0]["description"][:30] if res["demons"] else "None"
            print(f"{name:<20} {sun:<10} {moon:<10} {asc:<10} {demon:<30}")

    print()


def main():
    """Main test runner"""
    print("🔬 МАССОВОЕ ТЕСТИРОВАНИЕ АСТРОЛОГИЧЕСКИХ ФУНКЦИЙ")
    print("=" * 80)

    profiles = load_test_profiles()
    print(f"Загружено профилей: {len(profiles)}\n")

    results = []

    for profile in profiles:
        result = analyze_profile(profile)
        if result:
            results.append(result)

        # Pause between profiles
        print("\n" + "-" * 80)

    # Comparison
    if len(results) > 1:
        compare_profiles(results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(__file__).parent / f"test_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Результаты сохранены: {output_file}")
    print(f"✅ Протестировано профилей: {len(results)}/{len(profiles)}")


if __name__ == "__main__":
    main()
