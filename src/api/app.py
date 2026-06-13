from __future__ import annotations

import sys
from datetime import date as date_type
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

project_root = Path(__file__).resolve().parents[2]
src_root = project_root / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import swisseph as swe
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.aspects_math import ASPECTS, calc_aspects
from core.core_geometry import calculate_house_positions, planet_in_sign
from core.dignities import ZODIAC_SIGNS, get_dispositor, get_planet_sign
from input_pipeline import InputContext, normalize_input
from modules.astro_adapter import julian_day, natal_calculation
from modules.horary import (
    check_radicality,
    find_mutual_receptions,
    is_void_of_course,
    time_to_perfection,
)
from modules.interpretation_layer import (
    calculate_accidental_dignity,
    calculate_essential_dignity,
    decisions_from_signals,
    facts_from_calculation,
    is_day_chart,
    signals_from_facts,
)
from modules.synastry import calculate_synastry_aspects
from professional.progressions import secondary_progressions, solar_arc_directions
from professional.time_lords import annual_profections, firdaria, profection_timeline

app = FastAPI(
    title="Astro API",
    version="1.0.0",
    description="FastAPI wrapper around the astrology CLI calculations.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthData(BaseModel):
    name: str = Field(..., description="Place name or label used for geocoding/metadata")
    date_str: str
    time_str: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    tz: Optional[str] = None
    house_system: str = "Placidus"
    locale: Optional[str] = None
    strict: bool = False


class AspectsRequest(BirthData):
    aspect_type: str = "all"
    max_orb: float = 10.0
    planets: Optional[List[str]] = None


class SolarRequest(BirthData):
    year: int


class ProfectionsRequest(BirthData):
    target_date: Optional[str] = None
    timeline: bool = False
    years: int = 72


class ProgressionsRequest(BirthData):
    target_date: Optional[str] = None
    no_houses: bool = False


class SolarArcRequest(BirthData):
    target_date: Optional[str] = None


class HoraryRequest(BirthData):
    question_type: str = "lost-item"
    quesited_house: Optional[int] = None


class ApiEnvelope(BaseModel):
    status: str = "ok"
    result: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str = "ok"


def _normalize_context(payload: BirthData) -> InputContext:
    ni = normalize_input(
        payload.date_str,
        payload.time_str,
        payload.name,
        tz_override=payload.tz,
        lat_override=payload.lat,
        lon_override=payload.lon,
        locale=payload.locale,
        strict=payload.strict,
    )
    return InputContext.from_normalized(ni)


def _planet_longitudes(planets: Dict[str, Any]) -> Dict[str, float]:
    return {
        name: float(data.get("longitude", 0.0)) if isinstance(data, dict) else float(data)
        for name, data in planets.items()
    }


def _natal_result(payload: BirthData) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    calc_result = natal_calculation(
        ctx.utc_dt,
        ctx.lat,
        ctx.lon,
        house_method=payload.house_system,
        extended=True,
    )
    facts = facts_from_calculation(calc_result)
    signals = signals_from_facts(facts)
    decisions = decisions_from_signals(signals)
    return {
        "input_metadata": ctx.to_metadata_dict(),
        "chart": calc_result,
        "facts": [fact.model_dump() for fact in facts],
        "signals": [signal.model_dump() for signal in signals],
        "decisions": [decision.model_dump() for decision in decisions],
    }


def _serialize_aspects(aspects: List[tuple[str, str, str, float, str]]) -> List[Dict[str, Any]]:
    return [
        {
            "planet1": p1,
            "planet2": p2,
            "type": aspect_type,
            "orb": round(float(orb), 4),
            "category": category,
        }
        for p1, p2, aspect_type, orb, category in aspects
    ]


def _filter_aspects(
    aspects: List[tuple[str, str, str, float, str]],
    aspect_type_filter: str,
    max_orb: float,
    planet_filter: Optional[List[str]],
) -> List[tuple[str, str, str, float, str]]:
    filtered: List[tuple[str, str, str, float, str]] = []
    selected = {planet.lower() for planet in planet_filter or []}
    for aspect in aspects:
        p1, p2, _, orb, category = aspect
        if float(orb) > max_orb:
            continue
        if aspect_type_filter in {"major", "minor"} and category.lower() != aspect_type_filter.lower():
            continue
        if selected and p1.lower() not in selected and p2.lower() not in selected:
            continue
        filtered.append(aspect)
    return filtered


def _aspects_result(payload: AspectsRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    calc_result = natal_calculation(
        ctx.utc_dt,
        ctx.lat,
        ctx.lon,
        house_method=payload.house_system,
        extended=True,
    )
    planet_longs = _planet_longitudes(calc_result.get("planets", {}))
    raw_aspects = calc_aspects(planet_longs, include_minor=True, min_orb=0.0)
    filtered = _filter_aspects(raw_aspects, payload.aspect_type, payload.max_orb, payload.planets)
    return {
        "input_metadata": ctx.to_metadata_dict(),
        "chart": calc_result,
        "filters": {
            "aspect_type": payload.aspect_type,
            "max_orb": payload.max_orb,
            "planets": payload.planets or [],
        },
        "aspects": _serialize_aspects(filtered),
    }


def _solar_result(payload: SolarRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    natal_jd = julian_day(ctx.utc_dt)
    natal_sun = swe.calc_ut(natal_jd, swe.SUN)[0][0]
    approx_start = datetime(
        payload.year,
        ctx.utc_dt.month,
        max(1, ctx.utc_dt.day - 10),
        tzinfo=ZoneInfo("UTC"),
    )
    jd_start = julian_day(approx_start)
    step = 0.5
    current_jd = jd_start
    solar_return_jd = None

    def _diff(target: float, current: float) -> float:
        return (target - current) % 360

    for _ in range(760):
        sun_lon = swe.calc_ut(current_jd, swe.SUN)[0][0]
        next_lon = swe.calc_ut(current_jd + step, swe.SUN)[0][0]
        if _diff(natal_sun, sun_lon) < 180 and _diff(natal_sun, next_lon) > 180:
            low, high = current_jd, current_jd + step
            for _ in range(50):
                mid = (low + high) / 2
                mid_lon = swe.calc_ut(mid, swe.SUN)[0][0]
                if _diff(natal_sun, mid_lon) < 180:
                    low = mid
                else:
                    high = mid
            solar_return_jd = (low + high) / 2
            break
        current_jd += step

    if solar_return_jd is None:
        raise ValueError(f"Could not find Solar Return for year {payload.year}")

    y, m, d, h = swe.revjul(solar_return_jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int((((h - hour) * 60) - minute) * 60)
    solar_return_utc = datetime(y, m, d, hour, minute, second, tzinfo=ZoneInfo("UTC"))

    chart = natal_calculation(solar_return_utc, ctx.lat, ctx.lon, house_method=payload.house_system, extended=True)
    facts = facts_from_calculation(chart)
    signals = signals_from_facts(facts)
    decisions = decisions_from_signals(signals)
    return {
        "type": "solar_return",
        "year": payload.year,
        "natal_sun_longitude": round(float(natal_sun), 4),
        "solar_return_utc": solar_return_utc.isoformat(),
        "solar_return_jd": round(float(solar_return_jd), 6),
        "input_metadata": ctx.to_metadata_dict_minimal(),
        "chart": chart,
        "facts": [fact.model_dump() for fact in facts],
        "signals": [signal.model_dump() for signal in signals],
        "decisions": [decision.model_dump() for decision in decisions],
    }


def _extract_asc_sign(calc_result: Dict[str, Any]) -> Optional[str]:
    houses = calc_result.get("houses") or []
    asc_lon: Optional[float] = None
    if isinstance(houses, dict):
        asc_raw = houses.get("H1") or houses.get("ASC")
        if asc_raw is not None:
            asc_lon = float(asc_raw)
    elif isinstance(houses, list) and houses:
        asc_lon = float(houses[0])
    if asc_lon is None:
        return None
    return ZODIAC_SIGNS[int(asc_lon / 30) % 12]


def _profections_result(payload: ProfectionsRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon, house_method=payload.house_system)
    asc_sign = _extract_asc_sign(calc_result)
    house_signs = None
    if asc_sign:
        asc_index = ZODIAC_SIGNS.index(asc_sign)
        house_signs = [ZODIAC_SIGNS[(asc_index + idx) % 12] for idx in range(12)]

    birth_date = ctx.utc_dt.date() if hasattr(ctx.utc_dt, "date") else ctx.utc_dt
    planets = calc_result.get("planets", {})
    sun = planets.get("Sun")
    sun_lon = float(sun.get("longitude", 0.0)) if isinstance(sun, dict) else float(sun or 0.0)
    houses = calc_result.get("houses") or []
    asc_lon = float(houses[0]) if isinstance(houses, list) and houses else 0.0
    is_day = is_day_chart(sun_lon, asc_lon)

    if payload.timeline:
        timeline = profection_timeline(birth_date, years=payload.years, house_signs=house_signs)
        return {
            "type": "profection_timeline",
            "birth_date": birth_date.isoformat(),
            "asc_sign": asc_sign,
            "timeline": timeline,
        }

    profection = annual_profections(birth_date, payload.target_date, house_signs=house_signs)
    return {
        "type": "profections",
        "input_metadata": ctx.to_metadata_dict_minimal(),
        "asc_sign": asc_sign,
        "is_day_chart": is_day,
        "annual_profection": profection,
        "firdaria": firdaria(birth_date, is_day_chart=is_day, target_date=payload.target_date),
    }


def _progressions_result(payload: ProgressionsRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    birth_date = ctx.utc_dt.date() if hasattr(ctx.utc_dt, "date") else ctx.utc_dt
    result = secondary_progressions(
        birth_date=birth_date,
        birth_lat=ctx.lat,
        birth_lon=ctx.lon,
        target_date=payload.target_date,
        include_houses=not payload.no_houses,
    )
    result["input_metadata"] = ctx.to_metadata_dict_minimal()
    return result


def _solar_arc_result(payload: SolarArcRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    birth_date = ctx.utc_dt.date() if hasattr(ctx.utc_dt, "date") else ctx.utc_dt
    result = solar_arc_directions(
        birth_date=birth_date,
        birth_lat=ctx.lat,
        birth_lon=ctx.lon,
        target_date=payload.target_date,
    )
    result["input_metadata"] = ctx.to_metadata_dict_minimal()
    return result


def _horary_result(payload: HoraryRequest) -> Dict[str, Any]:
    ctx = _normalize_context(payload)
    calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon, house_method=payload.house_system, extended=True)
    planets = calc_result.get("planets", {})
    houses = calc_result.get("houses", [])

    quesited_house = payload.quesited_house
    if quesited_house is None:
        quesited_house = {
            "lost-item": 2,
            "will-it-happen": 7,
            "timing": 7,
            "relationship": 7,
        }.get(payload.question_type, 7)

    planet_longs = _planet_longitudes(planets)
    planet_houses = calculate_house_positions(houses, planet_longs)
    sun_lon = planet_longs.get("Sun", 0.0)
    asc_lon = float(houses[0]) if houses else 0.0
    day_chart = is_day_chart(sun_lon, asc_lon)
    radicality = check_radicality(asc_lon, planet_houses.get("Saturn", 0))

    moon_data = planets.get("Moon", {})
    moon_lon = float(moon_data.get("longitude", 0.0))
    moon_speed = float(moon_data.get("speed", 13.0))
    voc_result = is_void_of_course(moon_lon, moon_speed, planet_longs)

    querent_ruler = get_dispositor(get_planet_sign(asc_lon), traditional=True)
    quesited_cusp = float(houses[quesited_house - 1]) if houses and quesited_house <= len(houses) else 0.0
    quesited_ruler = get_dispositor(get_planet_sign(quesited_cusp), traditional=True)

    def _planet_details(name: str) -> Dict[str, Any]:
        if name not in planet_longs:
            return {"sign": "N/A", "house": None, "dignity": "N/A", "dignity_score": 0}
        lon = planet_longs[name]
        sign_name = ZODIAC_SIGNS[planet_in_sign(lon)]
        house = planet_houses.get(name)
        essential = calculate_essential_dignity(name, lon, day_chart)
        planet_data = planets.get(name, {})
        accidental = calculate_accidental_dignity(
            planet=name,
            house=house,
            is_retrograde=bool(planet_data.get("retrograde", False)),
            speed=float(planet_data.get("speed", 0.0)),
            longitude=lon,
            sun_longitude=sun_lon,
        )
        total = essential["score"] + accidental["score"]
        if total >= 5:
            label = "Very Strong"
        elif total >= 2:
            label = "Strong"
        elif total >= -2:
            label = "Moderate"
        elif total >= -5:
            label = "Weak"
        else:
            label = "Very Weak"
        return {
            "sign": sign_name,
            "house": house,
            "dignity": label,
            "dignity_score": total,
        }

    querent_data = _planet_details(querent_ruler)
    quesited_data = _planet_details(quesited_ruler)
    all_aspects = calc_aspects(planet_longs, include_minor=True, min_orb=0.1)
    serialized_aspects = _serialize_aspects(all_aspects)
    key_aspect = next(
        (
            aspect
            for aspect in serialized_aspects
            if {aspect["planet1"], aspect["planet2"]} == {"Moon", quesited_ruler}
        ),
        None,
    )

    perfection_time = None
    if key_aspect:
        perfection_time = time_to_perfection(
            moon_lon,
            moon_speed,
            planet_longs.get(quesited_ruler, 0.0),
            float(planets.get(quesited_ruler, {}).get("speed", 0.0)),
            ASPECTS[key_aspect["type"]]["angle"],
        )

    applying_aspects = [
        aspect for aspect in serialized_aspects if {aspect["planet1"], aspect["planet2"]} & {querent_ruler, quesited_ruler, "Moon"}
    ]
    separating_aspects = []
    if key_aspect and perfection_time and not perfection_time.get("is_applying", False):
        separating_aspects.append({**key_aspect, "timing": perfection_time})

    verdict = "maybe"
    confidence = 0.45
    rationale = "Mixed testimonies."
    if key_aspect and perfection_time and perfection_time.get("is_applying", False):
        verdict = "yes"
        confidence = 0.8 if key_aspect["type"] in {"trine", "sextile"} else 0.68
        rationale = "Applying contact between the Moon and quesited ruler supports perfection."
    elif key_aspect:
        verdict = "no"
        confidence = 0.67
        rationale = "The contact is separating, suggesting the opportunity has already passed."
    elif voc_result.get("is_void"):
        verdict = "no"
        confidence = 0.72
        rationale = "Void-of-course Moon weakens the likelihood of perfection."

    return {
        "question": {
            "type": payload.question_type,
            "quesited_house": quesited_house,
        },
        "input_metadata": ctx.to_metadata_dict(),
        "chart": calc_result,
        "radicality": radicality,
        "void_of_course": voc_result,
        "significators": {
            "querent": {"planet": querent_ruler, **querent_data},
            "quesited": {"planet": quesited_ruler, **quesited_data},
        },
        "applying_aspects": [
            {**aspect, "timing": perfection_time}
            for aspect in applying_aspects
            if not perfection_time or perfection_time.get("is_applying", False) or aspect != key_aspect
        ],
        "separating_aspects": separating_aspects,
        "receptions": find_mutual_receptions(planets),
        "key_aspect": key_aspect,
        "verdict": {
            "answer": verdict,
            "confidence": confidence,
            "rationale": rationale,
        },
    }


def _execute(builder, payload: BaseModel) -> ApiEnvelope:
    try:
        return ApiEnvelope(result=builder(payload))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/natal", response_model=ApiEnvelope)
def natal(payload: BirthData) -> ApiEnvelope:
    return _execute(_natal_result, payload)


@app.post("/aspects", response_model=ApiEnvelope)
def aspects(payload: AspectsRequest) -> ApiEnvelope:
    return _execute(_aspects_result, payload)


@app.post("/solar", response_model=ApiEnvelope)
def solar(payload: SolarRequest) -> ApiEnvelope:
    return _execute(_solar_result, payload)


@app.post("/profections", response_model=ApiEnvelope)
def profections(payload: ProfectionsRequest) -> ApiEnvelope:
    return _execute(_profections_result, payload)


@app.post("/progressions", response_model=ApiEnvelope)
def progressions(payload: ProgressionsRequest) -> ApiEnvelope:
    return _execute(_progressions_result, payload)


@app.post("/solar-arc", response_model=ApiEnvelope)
def solar_arc(payload: SolarArcRequest) -> ApiEnvelope:
    return _execute(_solar_arc_result, payload)


@app.post("/horary", response_model=ApiEnvelope)
def horary(payload: HoraryRequest) -> ApiEnvelope:
    return _execute(_horary_result, payload)
