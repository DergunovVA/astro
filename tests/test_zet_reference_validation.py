"""
tests/test_zet_reference_validation.py
=======================================
Сравнение расчётов приложения с эталонными значениями Swiss Ephemeris
(Zet/Astrozet использует тот же движок — результаты должны совпадать).

Запуск:
    python -m pytest tests/test_zet_reference_validation.py -v
    python -m pytest tests/test_zet_reference_validation.py -v -s   # с ASCII-таблицей

Отчёт HTML:
    python tools/compare_reference.py
"""

import json
import sys
import pytest
from pathlib import Path
from datetime import datetime, timezone

# ── путь ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from modules.astro_adapter import natal_calculation, julian_day  # noqa: E402

# ── константы допустимой погрешности ─────────────────────────────────────────
PLANET_TOL_DEG  = 0.01   # планеты:  ±0.01° (~0.6 угловые минуты)
ANGLE_TOL_DEG   = 0.10   # ASC/MC:   ±0.10° (зависит от точности времени)
VERTEX_TOL_DEG  = 0.10
HOUSE_TOL_DEG   = 0.10

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

# ── загрузка эталона ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def reference():
    path = ROOT / "tests" / "fixtures" / "zet_reference_charts.json"
    assert path.exists(), f"Reference file not found: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def calc_einstein(reference):
    ref = reference["einstein"]
    dt  = datetime.fromisoformat(ref["utc"].replace("Z", "+00:00"))
    return natal_calculation(dt, ref["lat"], ref["lon"], extended=True), ref

@pytest.fixture(scope="module")
def calc_marilyn(reference):
    ref = reference["marilyn"]
    dt  = datetime.fromisoformat(ref["utc"].replace("Z", "+00:00"))
    return natal_calculation(dt, ref["lat"], ref["lon"], extended=True), ref

@pytest.fixture(scope="module")
def calc_rehovot(reference):
    ref = reference["rehovot"]
    dt  = datetime.fromisoformat(ref["utc"].replace("Z", "+00:00"))
    return natal_calculation(dt, ref["lat"], ref["lon"], extended=True), ref


# ── вспомогательные функции ───────────────────────────────────────────────────

def _get_lon(result: dict, planet: str) -> float | None:
    """Извлечь долготу планеты из результата natal_calculation."""
    p = result["planets"].get(planet)
    if p is None:
        return None
    if isinstance(p, dict):
        return p["longitude"]
    return float(p)

def _get_retro(result: dict, planet: str) -> bool:
    p = result["planets"].get(planet)
    if isinstance(p, dict):
        return bool(p.get("retrograde", False))
    return False

def _sign(lon: float) -> str:
    return SIGNS[int(lon / 30) % 12]

def _deg(lon: float) -> float:
    return lon % 30

def _fmt(lon: float) -> str:
    s = _sign(lon)
    d = _deg(lon)
    return f"{d:6.3f}° {s}"

def _print_comparison(calc_result: dict, ref: dict) -> None:
    """Печатает ASCII-таблицу сравнения (вызывается при -s)."""
    planets = list(ref["planets"].keys())
    print("\n")
    print("┌────────────┬──────────────────────┬──────────────────────┬──────────┬────────┐")
    print("│ Planet     │ Reference (Zet/SE)   │ Calculated           │  Δ (°)   │ Status │")
    print("├────────────┼──────────────────────┼──────────────────────┼──────────┼────────┤")
    for pname in planets:
        ref_data = ref["planets"][pname]
        ref_lon  = ref_data["longitude"]
        calc_lon = _get_lon(calc_result, pname)
        if calc_lon is None:
            print(f"│ {pname:10} │ {_fmt(ref_lon):20} │ {'NOT FOUND':20} │ {'?':8} │ {'❌':6} │")
            continue
        delta = abs(calc_lon - ref_lon)
        # wrap-around safe
        if delta > 180:
            delta = 360 - delta
        ok = "✅" if delta <= PLANET_TOL_DEG else "⚠️ "
        ref_r  = "R" if ref_data["retrograde"] else " "
        calc_r = "R" if _get_retro(calc_result, pname) else " "
        retro_match = "✅" if ref_r == calc_r else "❌"
        print(
            f"│ {pname:10} │ {_fmt(ref_lon):20}{ref_r}│ "
            f"{_fmt(calc_lon):20}{calc_r}│ "
            f"{delta:8.4f} │ {ok} {retro_match} │"
        )
    # ASC / MC / Vertex
    print("├────────────┼──────────────────────┼──────────────────────┼──────────┼────────┤")
    for angle, ref_val, calc_val, tol in [
        ("ASC",    ref["angles"]["asc"],    calc_result["houses"][0],         ANGLE_TOL_DEG),
        ("MC",     ref["angles"]["mc"],     calc_result["houses"][9] if len(calc_result["houses"]) > 9 else None, ANGLE_TOL_DEG),
        ("Vertex", ref["angles"]["vertex"], calc_result["special_points"].get("Vertex"), VERTEX_TOL_DEG),
    ]:
        if calc_val is None:
            print(f"│ {angle:10} │ {_fmt(ref_val):20} │ {'NOT FOUND':20} │ {'?':8} │ {'❌':6} │")
            continue
        delta = abs(ref_val - calc_val)
        if delta > 180:
            delta = 360 - delta
        ok = "✅" if delta <= tol else "⚠️ "
        print(
            f"│ {angle:10} │ {_fmt(ref_val):21}│ "
            f"{_fmt(calc_val):21}│ "
            f"{delta:8.4f} │ {ok}    │"
        )
    print("└────────────┴──────────────────────┴──────────────────────┴──────────┴────────┘\n")


# ═══════════════════════════════════════════════════════════════════════════════
# ТЕСТЫ: Einstein 14.03.1879
# ═══════════════════════════════════════════════════════════════════════════════

class TestEinsteinChart:
    """Альберт Эйнштейн, 14.03.1879, 10:50 UTC, Ulm DE (48.4011N, 9.9876E)."""

    def test_sun_pisces(self, calc_einstein):
        result, ref = calc_einstein
        calc_lon = _get_lon(result, "Sun")
        ref_lon  = ref["planets"]["Sun"]["longitude"]
        assert calc_lon is not None
        assert abs(calc_lon - ref_lon) <= PLANET_TOL_DEG, \
            f"Sun: calc={calc_lon:.4f}, ref={ref_lon:.4f}, Δ={abs(calc_lon-ref_lon):.4f}°"
        assert _sign(calc_lon) == "Pisces"

    def test_moon_sagittarius(self, calc_einstein):
        result, ref = calc_einstein
        calc_lon = _get_lon(result, "Moon")
        ref_lon  = ref["planets"]["Moon"]["longitude"]
        assert abs(calc_lon - ref_lon) <= PLANET_TOL_DEG
        assert _sign(calc_lon) == "Sagittarius"

    @pytest.mark.parametrize("planet", [
        "Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"
    ])
    def test_planet_longitude(self, calc_einstein, planet):
        result, ref = calc_einstein
        ref_lon  = ref["planets"][planet]["longitude"]
        calc_lon = _get_lon(result, planet)
        assert calc_lon is not None, f"{planet} missing in calc result"
        delta = abs(calc_lon - ref_lon)
        if delta > 180:
            delta = 360 - delta
        assert delta <= PLANET_TOL_DEG, \
            f"{planet}: calc={_fmt(calc_lon)}, ref={_fmt(ref_lon)}, Δ={delta:.4f}°"

    @pytest.mark.parametrize("planet,expected_retro", [
        ("Sun", False), ("Moon", False), ("Uranus", True),
        ("Neptune", False), ("Mercury", False),
    ])
    def test_retrograde_flags(self, calc_einstein, planet, expected_retro):
        result, _ = calc_einstein
        assert _get_retro(result, planet) == expected_retro, \
            f"{planet} retrograde mismatch"

    def test_asc_cancer(self, calc_einstein):
        result, ref = calc_einstein
        calc_asc = result["houses"][0]
        ref_asc  = ref["angles"]["asc"]
        delta = abs(calc_asc - ref_asc)
        if delta > 180:
            delta = 360 - delta
        assert delta <= ANGLE_TOL_DEG, \
            f"ASC: calc={_fmt(calc_asc)}, ref={_fmt(ref_asc)}, Δ={delta:.4f}°"
        assert _sign(calc_asc) == "Cancer"

    def test_vertex(self, calc_einstein):
        result, ref = calc_einstein
        calc_v = result["special_points"].get("Vertex")
        ref_v  = ref["angles"]["vertex"]
        assert calc_v is not None, "Vertex not calculated"
        delta = abs(calc_v - ref_v)
        if delta > 180:
            delta = 360 - delta
        assert delta <= VERTEX_TOL_DEG, \
            f"Vertex: calc={_fmt(calc_v)}, ref={_fmt(ref_v)}, Δ={delta:.4f}°"

    def test_print_table(self, calc_einstein, capsys):
        """Печатает сравнительную таблицу при -s."""
        result, ref = calc_einstein
        _print_comparison(result, ref)


# ═══════════════════════════════════════════════════════════════════════════════
# ТЕСТЫ: Marilyn Monroe 01.06.1926
# ═══════════════════════════════════════════════════════════════════════════════

class TestMarilynChart:
    """Мэрилин Монро, 01.06.1926, 17:30 UTC, Los Angeles CA (34.0522N, 118.2437W)."""

    @pytest.mark.parametrize("planet", [
        "Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"
    ])
    def test_planet_longitude(self, calc_marilyn, planet):
        result, ref = calc_marilyn
        ref_lon  = ref["planets"][planet]["longitude"]
        calc_lon = _get_lon(result, planet)
        assert calc_lon is not None, f"{planet} missing"
        delta = abs(calc_lon - ref_lon)
        if delta > 180:
            delta = 360 - delta
        assert delta <= PLANET_TOL_DEG, \
            f"{planet}: calc={_fmt(calc_lon)}, ref={_fmt(ref_lon)}, Δ={delta:.4f}°"

    def test_sun_gemini(self, calc_marilyn):
        result, _ = calc_marilyn
        assert _sign(_get_lon(result, "Sun")) == "Gemini"

    def test_moon_aquarius(self, calc_marilyn):
        result, _ = calc_marilyn
        assert _sign(_get_lon(result, "Moon")) == "Aquarius"

    def test_saturn_retrograde(self, calc_marilyn):
        result, _ = calc_marilyn
        assert _get_retro(result, "Saturn") is True

    def test_print_table(self, calc_marilyn, capsys):
        result, ref = calc_marilyn
        _print_comparison(result, ref)


# ═══════════════════════════════════════════════════════════════════════════════
# ТЕСТЫ: Rehovot 1982 (внутренний эталон из natal_rehovot.json)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRehovotChart:
    """Карта Рехово́та, 08.01.1982, 11:40 UTC (31.8952N, 34.8105E)."""

    @pytest.mark.parametrize("planet", [
        "Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"
    ])
    def test_planet_longitude(self, calc_rehovot, planet):
        result, ref = calc_rehovot
        ref_lon  = ref["planets"][planet]["longitude"]
        calc_lon = _get_lon(result, planet)
        assert calc_lon is not None, f"{planet} missing"
        delta = abs(calc_lon - ref_lon)
        if delta > 180:
            delta = 360 - delta
        assert delta <= PLANET_TOL_DEG, \
            f"{planet}: calc={_fmt(calc_lon)}, ref={_fmt(ref_lon)}, Δ={delta:.4f}°"

    def test_sun_capricorn(self, calc_rehovot):
        result, _ = calc_rehovot
        assert _sign(_get_lon(result, "Sun")) == "Capricorn"

    def test_moon_gemini(self, calc_rehovot):
        result, _ = calc_rehovot
        assert _sign(_get_lon(result, "Moon")) == "Gemini"

    def test_venus_retrograde(self, calc_rehovot):
        result, _ = calc_rehovot
        assert _get_retro(result, "Venus") is True

    def test_asc_gemini(self, calc_rehovot):
        result, ref = calc_rehovot
        calc_asc = result["houses"][0]
        assert _sign(calc_asc) == "Gemini", \
            f"ASC sign: expected Gemini, got {_sign(calc_asc)}"

    def test_vertex_scorpio(self, calc_rehovot):
        result, ref = calc_rehovot
        v = result["special_points"].get("Vertex")
        ref_v = ref["angles"]["vertex"]
        assert v is not None
        delta = abs(v - ref_v)
        if delta > 180:
            delta = 360 - delta
        assert delta <= VERTEX_TOL_DEG

    def test_print_table(self, calc_rehovot, capsys):
        result, ref = calc_rehovot
        _print_comparison(result, ref)


# ═══════════════════════════════════════════════════════════════════════════════
# ТЕСТ: Solar Return эталон — Rehovot 2025
# ═══════════════════════════════════════════════════════════════════════════════

class TestSolarReturn:
    """
    Проверяет Solar Return: Солнце возвращается на natal lon=287.8709°
    в 2025 году. Допуск: ±0.001° (бинарный поиск точен).
    """

    def test_solar_return_sun_matches_natal(self):
        """Солнце SR должно совпадать с натальным с точностью < 0.001°."""
        import swisseph as swe
        from modules.astro_adapter import julian_day

        natal_utc = datetime(1982, 1, 8, 11, 40, 0, tzinfo=timezone.utc)
        natal_jd  = julian_day(natal_utc)
        natal_sun = swe.calc_ut(natal_jd, swe.SUN)[0][0]

        approx_start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        jd = julian_day(approx_start)
        sr_jd = None

        def _diff(target, current):
            return (target - current) % 360

        step = 0.5
        for _ in range(760):
            d_now  = _diff(natal_sun, swe.calc_ut(jd, swe.SUN)[0][0])
            d_next = _diff(natal_sun, swe.calc_ut(jd + step, swe.SUN)[0][0])
            if d_now < 180 and d_next > 180:
                lo, hi = jd, jd + step
                for _ in range(50):
                    mid = (lo + hi) / 2
                    if _diff(natal_sun, swe.calc_ut(mid, swe.SUN)[0][0]) < 180:
                        lo = mid
                    else:
                        hi = mid
                sr_jd = (lo + hi) / 2
                break
            jd += step

        assert sr_jd is not None, "Solar Return JD not found"
        sr_sun = swe.calc_ut(sr_jd, swe.SUN)[0][0]
        delta  = abs(sr_sun - natal_sun)
        if delta > 180:
            delta = 360 - delta
        assert delta < 0.001, \
            f"SR Sun={sr_sun:.6f} vs natal={natal_sun:.6f}, Δ={delta:.6f}°"

    def test_solar_return_in_target_year(self):
        """SR должен находиться в 2025 году."""
        import swisseph as swe
        from modules.astro_adapter import julian_day

        natal_utc = datetime(1982, 1, 8, 11, 40, 0, tzinfo=timezone.utc)
        natal_jd  = julian_day(natal_utc)
        natal_sun = swe.calc_ut(natal_jd, swe.SUN)[0][0]

        approx_start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        jd = julian_day(approx_start)

        def _diff(target, current):
            return (target - current) % 360

        step, sr_jd = 0.5, None
        for _ in range(760):
            d_now  = _diff(natal_sun, swe.calc_ut(jd, swe.SUN)[0][0])
            d_next = _diff(natal_sun, swe.calc_ut(jd + step, swe.SUN)[0][0])
            if d_now < 180 and d_next > 180:
                lo, hi = jd, jd + step
                for _ in range(50):
                    mid = (lo + hi) / 2
                    if _diff(natal_sun, swe.calc_ut(mid, swe.SUN)[0][0]) < 180:
                        lo = mid
                    else:
                        hi = mid
                sr_jd = (lo + hi) / 2
                break
            jd += step

        y, m, d, _ = swe.revjul(sr_jd)
        assert y == 2025, f"SR year expected 2025, got {y}"
        assert m == 1,    f"SR month expected January, got {m}"
