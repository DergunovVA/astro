# Interpretation Layer: Core results → Facts/Signals/Decisions (no calculations)
from models.facts_models import Fact
from models.signals_models import Signal
from models.decisions_models import Decision
from core.core_geometry import (
    calculate_aspects,
    calculate_house_positions,
    planet_in_sign,
)
from core.dignities import (
    calculate_essential_dignity,
    is_day_chart,
    get_dispositor_chain,
    find_mutual_receptions,
)
from core.accidental_dignities import (
    calculate_accidental_dignity,
    get_total_dignity,
)
from typing import List, Dict, Any

ASPECTS_CONFIG = {
    # Major aspects
    "conjunction": 0,
    "opposition": 180,
    "trine": 120,
    "square": 90,
    "sextile": 60,
    # Minor aspects (basic)
    "semisextile": 30,
    "semisquare": 45,
    "sesquiquadrate": 135,
    "quincunx": 150,
    # Minor aspects (advanced)
    "quintile": 72,  # 5th harmonic - creativity, talent
    "biquintile": 144,  # 5th harmonic
    "septile": 51.43,  # 7th harmonic - fate, spiritual
    "novile": 40,  # 9th harmonic - completion, wisdom
}

ZODIAC_SIGNS = [
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


def facts_from_calculation(calc_result: Dict[str, Any]) -> List[Fact]:
    """Transform core calculation (floats) into Fact objects (no math).

    Supports both simple planet data (Dict[str, float]) and extended data
    (Dict[str, dict]) with retrograde indicators.
    """
    facts = []

    # Planet positions (sign + house)
    planets = calc_result["planets"]
    houses = calc_result["houses"]

    # Normalize planets to dict format for uniform processing
    # Handle both old format (float) and new format (dict with "longitude")
    normalized_planets = {}
    planet_metadata = {}  # Store retrograde and other metadata

    for planet, data in planets.items():
        if isinstance(data, dict):
            # Extended format: {"longitude": 123.45, "retrograde": True, ...}
            normalized_planets[planet] = data["longitude"]
            planet_metadata[planet] = data
        else:
            # Simple format: just float
            normalized_planets[planet] = data
            planet_metadata[planet] = {"longitude": data, "retrograde": False}

    planet_houses = calculate_house_positions(houses, normalized_planets)

    for planet, lon in normalized_planets.items():
        sign_idx = planet_in_sign(lon)
        sign = ZODIAC_SIGNS[sign_idx]
        house = planet_houses[planet]

        # Get metadata
        metadata = planet_metadata.get(planet, {})
        is_retrograde = metadata.get("retrograde", False)

        # Build details
        details = {"longitude": lon, "house": house}

        # Add retrograde indicator if applicable
        if is_retrograde:
            details["retrograde"] = True

        facts.append(
            Fact(
                id=f"{planet}_position",
                type="planet_in_sign",
                object=planet,
                value=f"{sign}",
                details=details,
            )
        )

    # Essential Dignities
    # Determine if day or night chart
    sun_lon = normalized_planets.get("Sun", 0.0)
    asc_lon = houses[0]  # 1st house cusp = Ascendant
    is_day = is_day_chart(sun_lon, asc_lon)

    # Calculate dignities for each planet
    for planet, lon in normalized_planets.items():
        # Essential dignity
        essential_dignity = calculate_essential_dignity(planet, lon, is_day)

        facts.append(
            Fact(
                id=f"{planet}_essential_dignity",
                type="essential_dignity",
                object=planet,
                value=essential_dignity["dignity_level"],
                details={
                    "score": essential_dignity["score"],
                    "domicile": essential_dignity["domicile"],
                    "exaltation": essential_dignity["exaltation"],
                    "detriment": essential_dignity["detriment"],
                    "fall": essential_dignity["fall"],
                    "triplicity": essential_dignity["triplicity"],
                },
            )
        )

        # Accidental dignity (requires house, speed, retrograde status)
        metadata = planet_metadata.get(planet, {})
        house = planet_houses.get(planet, 1)
        is_retro = metadata.get("retrograde", False)
        speed = metadata.get("speed", 0.0)

        accidental_dignity = calculate_accidental_dignity(
            planet=planet,
            house=house,
            is_retrograde=is_retro,
            speed=speed,
            longitude=lon,
            sun_longitude=sun_lon,
        )

        facts.append(
            Fact(
                id=f"{planet}_accidental_dignity",
                type="accidental_dignity",
                object=planet,
                value=accidental_dignity["strength_level"],
                details={
                    "score": accidental_dignity["score"],
                    "house_strength": accidental_dignity["house_strength"],
                    "motion_strength": accidental_dignity["motion_strength"],
                    "speed_strength": accidental_dignity["speed_strength"],
                    "oriental_occidental": accidental_dignity["oriental_occidental"],
                },
            )
        )

        # Total dignity (combined essential + accidental)
        total = get_total_dignity(essential_dignity, accidental_dignity)

        facts.append(
            Fact(
                id=f"{planet}_total_dignity",
                type="total_dignity",
                object=planet,
                value=total["overall_strength"],
                details={
                    "total_score": total["total_score"],
                    "essential_score": total["essential_score"],
                    "accidental_score": total["accidental_score"],
                },
            )
        )

    # Dispositor chains
    dispositor_chains = get_dispositor_chain(normalized_planets)
    for planet, chain in dispositor_chains.items():
        if chain:  # Only if there's a chain
            facts.append(
                Fact(
                    id=f"{planet}_dispositor_chain",
                    type="dispositor",
                    object=planet,
                    value=chain[0] if chain else None,  # First dispositor
                    details={"chain": chain, "has_cycle": "(cycle)" in " ".join(chain)},
                )
            )

    # Mutual receptions
    mutual_receptions = find_mutual_receptions(normalized_planets)
    for p1, p2, rec_type in mutual_receptions:
        facts.append(
            Fact(
                id=f"{p1}_{p2}_reception",
                type="mutual_reception",
                object=f"{p1}-{p2}",
                value=rec_type,
                details={
                    "planets": [p1, p2],
                    "type": rec_type,  # "mutual_domicile" or "mixed"
                },
            )
        )

    # House cusps
    for i, cusp in enumerate(houses):
        facts.append(
            Fact(
                id=f"house_{i + 1}_cusp",
                type="house_cusp",
                object=f"House {i + 1}",
                value=str(round(cusp, 2)),
                details={},
            )
        )

    # Aspects (now returns 6-tuple with aspect category and motion)
    # Use original planets data (not normalized) to preserve speed information
    aspects = calculate_aspects(planets, ASPECTS_CONFIG)
    for p1, p2, asp_name, orb, asp_category, motion in aspects:
        aspect_details = {
            "orb": round(orb, 2),
            "category": asp_category,  # "major" or "minor"
        }

        # Add applying/separating info if available
        if motion:
            aspect_details["motion"] = (
                motion  # "applying", "separating", or "stationary"
            )

        facts.append(
            Fact(
                id=f"{p1}_{p2}_{asp_name}",
                type="aspect",
                object=f"{p1}-{p2}",
                value=asp_name,
                details=aspect_details,
            )
        )

    # Aspects to angles (ASC, DESC, MC, IC)
    from core.core_geometry import (
        calculate_aspects_to_angles,
        calculate_aspects_to_house_cusps,
    )

    angle_aspects = calculate_aspects_to_angles(planets, houses, ASPECTS_CONFIG)
    for planet, angle, asp_name, orb, asp_category in angle_aspects:
        facts.append(
            Fact(
                id=f"{planet}_{angle}_{asp_name}",
                type="aspect_to_angle",
                object=f"{planet}-{angle}",
                value=asp_name,
                details={
                    "orb": round(orb, 2),
                    "category": asp_category,
                    "angle": angle,  # Which angle: Ascendant, Midheaven, etc.
                },
            )
        )

    # Aspects to house cusps (all 12 houses)
    cusp_aspects = calculate_aspects_to_house_cusps(
        planets, houses, ASPECTS_CONFIG, orb=6.0
    )
    for planet, house_num, asp_name, orb, asp_category in cusp_aspects:
        facts.append(
            Fact(
                id=f"{planet}_house{house_num}_{asp_name}",
                type="aspect_to_cusp",
                object=f"{planet}-House{house_num}",
                value=asp_name,
                details={
                    "orb": round(orb, 2),
                    "category": asp_category,
                    "house": house_num,
                },
            )
        )

    # Special points (Lilith, Vertex, East Point, Parts)
    special_points = calc_result.get("special_points", {})
    for point_name, longitude in special_points.items():
        sign_idx = planet_in_sign(longitude)
        sign = ZODIAC_SIGNS[sign_idx]

        # Calculate house position for special point
        house = None
        for h in range(12):
            next_h = (h + 1) % 12
            cusp = houses[h]
            next_cusp = houses[next_h]

            # Handle wrapping around 360°
            if cusp < next_cusp:
                if cusp <= longitude < next_cusp:
                    house = h + 1
                    break
            else:  # Wraps around 0°
                if longitude >= cusp or longitude < next_cusp:
                    house = h + 1
                    break

        if house is None:
            house = 1  # Fallback

        facts.append(
            Fact(
                id=f"{point_name}_position",
                type="special_point",
                object=point_name,
                value=f"{sign}",
                details={
                    "longitude": round(longitude, 2),
                    "house": house,
                },
            )
        )

    return facts


def signals_from_facts(facts: List[Fact]) -> List[Signal]:
    """Aggregate facts into signals grouped by domain.

    Produces one Signal per domain based on what facts are present:
    - general: overall chart intensity (hard vs soft aspect balance)
    - dignity: essential + accidental dignity summary
    - motion: retrograde planets
    - house_emphasis: angular / cadent emphasis
    - element_balance: fire/earth/air/water distribution
    """
    signals: List[Signal] = []

    # ── collect fact ids by category ───────────────────────────────────────
    hard_ids: List[str] = []
    soft_ids: List[str] = []
    retro_ids: List[str] = []
    strong_ids: List[str] = []
    weak_ids: List[str] = []
    angular_ids: List[str] = []
    cadent_ids: List[str] = []
    element_counts: Dict[str, int] = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    element_ids: Dict[str, List[str]] = {e: [] for e in element_counts}

    HARD_ASPECTS = {"square", "opposition", "semisquare", "sesquiquadrate", "quincunx"}
    SOFT_ASPECTS = {"trine", "sextile", "conjunction", "semisextile"}
    FIRE_SIGNS = {"Aries", "Leo", "Sagittarius"}
    EARTH_SIGNS = {"Taurus", "Virgo", "Capricorn"}
    AIR_SIGNS = {"Gemini", "Libra", "Aquarius"}
    WATER_SIGNS = {"Cancer", "Scorpio", "Pisces"}
    SIGN_ELEMENT = {
        **{s: "Fire" for s in FIRE_SIGNS},
        **{s: "Earth" for s in EARTH_SIGNS},
        **{s: "Air" for s in AIR_SIGNS},
        **{s: "Water" for s in WATER_SIGNS},
    }
    ANGULAR_HOUSES = {1, 4, 7, 10}
    CADENT_HOUSES = {3, 6, 9, 12}

    for f in facts:
        if f.type == "aspect":
            if f.value in HARD_ASPECTS:
                hard_ids.append(f.id)
            elif f.value in SOFT_ASPECTS:
                soft_ids.append(f.id)

        elif f.type == "planet_in_sign":
            details = f.details or {}

            # retrograde
            if details.get("retrograde"):
                retro_ids.append(f.id)

            # dignity score
            score = details.get("dignity_score", details.get("score"))
            if score is not None:
                if score >= 4:
                    strong_ids.append(f.id)
                elif score <= -4:
                    weak_ids.append(f.id)

            # house emphasis
            house = details.get("house")
            if house:
                if house in ANGULAR_HOUSES:
                    angular_ids.append(f.id)
                elif house in CADENT_HOUSES:
                    cadent_ids.append(f.id)

            # element balance
            sign = f.value
            elem = SIGN_ELEMENT.get(sign)
            if elem:
                element_counts[elem] += 1
                element_ids[elem].append(f.id)

    # ── 1. General: hard/soft aspect balance ───────────────────────────────
    total_aspects = len(hard_ids) + len(soft_ids)
    if total_aspects == 0:
        general_intensity = "low"
        general_sources = [f.id for f in facts[:3]]
    else:
        ratio = len(hard_ids) / total_aspects
        if ratio >= 0.6:
            general_intensity = "high"
        elif ratio >= 0.4:
            general_intensity = "medium"
        else:
            general_intensity = "low"
        general_sources = hard_ids[:5] + soft_ids[:3]

    signals.append(Signal(
        id="chart_intensity",
        intensity=general_intensity,
        domain="general",
        period="natal",
        sources=general_sources,
        weight=round(len(hard_ids) / max(total_aspects, 1), 2),
    ))

    # ── 2. Dignity signal ──────────────────────────────────────────────────
    if strong_ids or weak_ids:
        if len(strong_ids) > len(weak_ids):
            dignity_intensity = "high"
        elif len(weak_ids) > len(strong_ids):
            dignity_intensity = "low"
        else:
            dignity_intensity = "medium"
        signals.append(Signal(
            id="dignity_balance",
            intensity=dignity_intensity,
            domain="dignity",
            period="natal",
            sources=(strong_ids + weak_ids)[:8],
            weight=round(len(strong_ids) / max(len(strong_ids) + len(weak_ids), 1), 2),
        ))

    # ── 3. Motion: retrograde planets ─────────────────────────────────────
    if retro_ids:
        retro_intensity = "high" if len(retro_ids) >= 3 else "medium"
        signals.append(Signal(
            id="retrograde_activity",
            intensity=retro_intensity,
            domain="motion",
            period="natal",
            sources=retro_ids,
            weight=round(len(retro_ids) / 10.0, 2),
        ))

    # ── 4. House emphasis ──────────────────────────────────────────────────
    if angular_ids:
        angular_intensity = "high" if len(angular_ids) >= 4 else "medium"
        signals.append(Signal(
            id="angular_emphasis",
            intensity=angular_intensity,
            domain="house_emphasis",
            period="natal",
            sources=angular_ids[:6],
            weight=round(len(angular_ids) / max(len(angular_ids) + len(cadent_ids), 1), 2),
        ))

    # ── 5. Dominant element ───────────────────────────────────────────────
    dominant_elem = max(element_counts, key=lambda e: element_counts[e])
    if element_counts[dominant_elem] >= 3:
        signals.append(Signal(
            id=f"element_{dominant_elem.lower()}",
            intensity="medium" if element_counts[dominant_elem] <= 4 else "high",
            domain="element_balance",
            period="natal",
            sources=element_ids[dominant_elem][:6],
            weight=round(element_counts[dominant_elem] / max(sum(element_counts.values()), 1), 2),
        ))

    return signals


def decisions_from_signals(signals: List[Signal]) -> List[Decision]:
    """Form human-readable decisions from aggregated signals.

    Each signal domain produces a concrete, actionable decision.
    """
    decisions: List[Decision] = []

    signal_map: Dict[str, Signal] = {s.id: s for s in signals}

    # ── General intensity ─────────────────────────────────────────────────
    intensity_sig = signal_map.get("chart_intensity")
    if intensity_sig:
        if intensity_sig.intensity == "high":
            summary = (
                "Карта насыщена напряжёнными аспектами (квадратуры, оппозиции). "
                "Высокая динамика, стремление к действию, вероятны конфликты и рост через преодоление."
            )
            recommendation = "Обратить особое внимание на планеты в вершинах T-квадрата или Большого Креста."
        elif intensity_sig.intensity == "medium":
            summary = (
                "Баланс напряжённых и гармоничных аспектов. "
                "Карта предоставляет ресурсы и ставит задачи примерно поровну."
            )
            recommendation = "Ключевые трины и секстили указывают на природные таланты — развивайте их."
        else:
            summary = (
                "Преобладают гармоничные аспекты (трины, секстили). "
                "Лёгкость реализации, но возможна нехватка мотивации без внешних вызовов."
            )
            recommendation = "Дополнительный вызов и дисциплина помогут реализовать потенциал."
        decisions.append(Decision(
            id="aspect_pattern_assessment",
            summary=summary,
            signals=["chart_intensity"],
            recommendation=recommendation,
            fatal=False,
        ))

    # ── Dignity ───────────────────────────────────────────────────────────
    dignity_sig = signal_map.get("dignity_balance")
    if dignity_sig:
        if dignity_sig.intensity == "high":
            summary = "Ряд планет находится в достоинстве (домициль / экзальтация) — выражены сильные качества."
            rec = "Определите планеты с наивысшим баллом достоинства — они станут главными ресурсами натива."
        elif dignity_sig.intensity == "low":
            summary = "Несколько планет в ущербе или падении — требует осознанной работы с соответствующими сферами."
            rec = "Падшие или изгнанные планеты указывают на области, требующие компенсации и развития."
        else:
            summary = "Смешанная картина достоинств и слабостей."
            rec = "Используйте ресурс планет в достоинстве для поддержки слабых мест карты."
        decisions.append(Decision(
            id="dignity_assessment",
            summary=summary,
            signals=["dignity_balance"],
            recommendation=rec,
            fatal=False,
        ))

    # ── Retrograde ────────────────────────────────────────────────────────
    retro_sig = signal_map.get("retrograde_activity")
    if retro_sig:
        count = len(retro_sig.sources)
        if retro_sig.intensity == "high":
            summary = (
                f"{count} ретроградных планет — выраженная интроверсия, "
                "склонность к переосмыслению, внутреннему поиску."
            )
            rec = "Периоды ретроградных транзитов особенно значимы для переоценки и завершения дел."
        else:
            summary = f"{count} ретроградная(-ых) планета(-ы) вносит(-ят) внутренний, рефлективный акцент."
            rec = "Ретроградные планеты часто указывают на кармический урок или задержанное развитие."
        decisions.append(Decision(
            id="retrograde_assessment",
            summary=summary,
            signals=["retrograde_activity"],
            recommendation=rec,
            fatal=False,
        ))

    # ── Angular emphasis ──────────────────────────────────────────────────
    angular_sig = signal_map.get("angular_emphasis")
    if angular_sig:
        decisions.append(Decision(
            id="angular_house_assessment",
            summary=(
                "Скопление планет в угловых домах (1, 4, 7, 10) — "
                "высокая активность, видимость в мире, способность воздействовать на события."
            ),
            signals=["angular_emphasis"],
            recommendation="Угловые планеты реализуются во внешней жизни — карьера, семья, партнёрства.",
            fatal=False,
        ))

    # ── Element ───────────────────────────────────────────────────────────
    for elem, label_ru in [("fire", "Огонь"), ("earth", "Земля"), ("air", "Воздух"), ("water", "Вода")]:
        elem_sig = signal_map.get(f"element_{elem}")
        if elem_sig:
            descriptions = {
                "fire": "Преобладает стихия Огня — энтузиазм, инициатива, творческая энергия, импульсивность.",
                "earth": "Преобладает стихия Земли — практичность, надёжность, материальная ориентация, упорство.",
                "air": "Преобладает стихия Воздуха — интеллектуализм, общение, социальность, переменчивость.",
                "water": "Преобладает стихия Воды — эмоциональность, интуиция, чувствительность, глубина.",
            }
            decisions.append(Decision(
                id=f"element_{elem}_assessment",
                summary=descriptions[elem],
                signals=[f"element_{elem}"],
                recommendation=f"Уделите внимание развитию недостающих стихий для баланса.",
                fatal=False,
            ))

    # ── Fallback if no signals produced content ───────────────────────────
    if not decisions:
        decisions.append(Decision(
            id="general_assessment",
            summary="Карта сформирована и готова к интерпретации.",
            signals=[s.id for s in signals],
            fatal=False,
        ))

    return decisions
