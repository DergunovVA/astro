#!/usr/bin/env python
"""
tools/compare_reference.py
===========================
Генерирует HTML-отчёт сравнения расчётов приложения с эталонными данными Zet/SE.

Использование:
    python tools/compare_reference.py
    python tools/compare_reference.py --output my_report.html

Выходной файл: docs/reference_comparison.html (по умолчанию)
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from modules.astro_adapter import natal_calculation  # noqa: E402

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]
SIGN_SYMBOLS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
PLANET_SYMBOLS = {
    "Sun":"☉","Moon":"☽","Mercury":"☿","Venus":"♀","Mars":"♂",
    "Jupiter":"♃","Saturn":"♄","Uranus":"♅","Neptune":"♆","Pluto":"♇",
}
PLANET_TOL = 0.01
ANGLE_TOL  = 0.10

def _sign(lon): return SIGNS[int(lon/30) % 12]
def _sign_sym(lon): return SIGN_SYMBOLS[int(lon/30) % 12]
def _deg(lon): return lon % 30
def _fmt(lon):
    d = _deg(lon)
    dm = int(d)
    ms = int((d-dm)*60)
    return f"{dm:02d}°{ms:02d}' {_sign_sym(lon)} {_sign(lon)}"

def _get_lon(result, planet):
    p = result["planets"].get(planet)
    if p is None: return None
    return p["longitude"] if isinstance(p, dict) else float(p)

def _get_retro(result, planet):
    p = result["planets"].get(planet)
    if isinstance(p, dict): return bool(p.get("retrograde", False))
    return False


def build_comparison(name: str, ref: dict) -> dict:
    """Запускает расчёт и возвращает структуру для отчёта."""
    dt = datetime.fromisoformat(ref["utc"].replace("Z", "+00:00"))
    result = natal_calculation(dt, ref["lat"], ref["lon"], extended=True)

    rows = []
    for pname, ref_data in ref["planets"].items():
        ref_lon  = ref_data["longitude"]
        calc_lon = _get_lon(result, pname)
        if calc_lon is None:
            rows.append({
                "planet": pname, "symbol": PLANET_SYMBOLS.get(pname,""),
                "ref_lon": ref_lon, "calc_lon": None,
                "ref_retro": ref_data["retrograde"], "calc_retro": None,
                "delta": None, "ok": False,
            })
            continue
        delta = abs(calc_lon - ref_lon)
        if delta > 180: delta = 360 - delta
        ref_retro  = ref_data["retrograde"]
        calc_retro = _get_retro(result, pname)
        rows.append({
            "planet": pname,
            "symbol": PLANET_SYMBOLS.get(pname, ""),
            "ref_lon":    ref_lon,
            "calc_lon":   calc_lon,
            "ref_retro":  ref_retro,
            "calc_retro": calc_retro,
            "delta":      delta,
            "ok":         delta <= PLANET_TOL and ref_retro == calc_retro,
        })

    # Angles
    calc_asc = result["houses"][0]
    calc_mc  = result["houses"][9] if len(result["houses"]) > 9 else None
    calc_vtx = result["special_points"].get("Vertex")

    angle_rows = []
    for aname, ref_val, calc_val, tol in [
        ("ASC",    ref["angles"]["asc"],    calc_asc, ANGLE_TOL),
        ("MC",     ref["angles"]["mc"],     calc_mc,  ANGLE_TOL),
        ("Vertex", ref["angles"]["vertex"], calc_vtx, ANGLE_TOL),
    ]:
        if calc_val is None:
            angle_rows.append({"name": aname, "ref": ref_val, "calc": None, "delta": None, "ok": False})
            continue
        delta = abs(ref_val - calc_val)
        if delta > 180: delta = 360 - delta
        angle_rows.append({
            "name": aname, "ref": ref_val, "calc": calc_val,
            "delta": delta, "ok": delta <= tol,
        })

    # Houses
    house_rows = []
    ref_houses = ref.get("houses_placidus", {})
    for i, cusp in enumerate(result["houses"]):
        hn = f"H{i+1}"
        ref_cusp = ref_houses.get(hn)
        if ref_cusp is not None:
            delta = abs(cusp - ref_cusp)
            if delta > 180: delta = 360 - delta
            house_rows.append({
                "house": hn, "ref": ref_cusp, "calc": cusp,
                "delta": delta, "ok": delta <= ANGLE_TOL,
            })

    total = len(rows)
    passed = sum(1 for r in rows if r["ok"])
    return {
        "name": name, "utc": ref["utc"], "lat": ref["lat"], "lon": ref["lon"],
        "planet_rows": rows, "angle_rows": angle_rows, "house_rows": house_rows,
        "passed": passed, "total": total,
    }


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
body { background: #0e0e1a; color: #e0e0f0; padding: 24px; }
h1 { color: #c9a84c; font-size: 2rem; margin-bottom: 8px; }
h2 { color: #8fa8d8; font-size: 1.3rem; margin: 28px 0 10px; border-bottom: 1px solid #2a2a44; padding-bottom: 6px; }
h3 { color: #7bbfaa; font-size: 1.05rem; margin: 18px 0 8px; }
.meta { color: #8888aa; font-size: 0.85rem; margin-bottom: 24px; }
.summary { display: flex; gap: 20px; flex-wrap: wrap; margin: 16px 0; }
.badge { background: #1a1a2e; border-radius: 8px; padding: 10px 18px; }
.badge .val { font-size: 1.8rem; font-weight: bold; }
.badge .lbl { font-size: 0.78rem; color: #8888aa; }
.green  { color: #5de88e; }
.yellow { color: #f0c040; }
.red    { color: #f06060; }
table { border-collapse: collapse; width: 100%; margin-bottom: 24px; font-size: 0.88rem; }
th { background: #1a1a2e; color: #8fa8d8; padding: 8px 10px; text-align: left; }
td { padding: 6px 10px; border-bottom: 1px solid #1c1c30; }
tr:hover td { background: #16162a; }
.ok  { background: #0d2a1c; }
.bad { background: #2a0d0d; }
.retro { color: #f06060; font-weight: bold; }
.delta-ok  { color: #5de88e; }
.delta-bad { color: #f06060; }
.section { background: #131320; border-radius: 10px; padding: 20px; margin-bottom: 30px; }
.chart-bar { height: 10px; border-radius: 5px; background: #5de88e; display: inline-block; }
.chart-bar-bad { background: #f06060; }
"""

def _planet_row(r):
    ok_cls  = "ok" if r["ok"] else "bad"
    if r["calc_lon"] is None:
        return f'<tr class="{ok_cls}"><td>{r["symbol"]} {r["planet"]}</td>' \
               f'<td>{_fmt(r["ref_lon"])}</td><td colspan="3" class="red">НЕ ВЫЧИСЛЕНО</td>' \
               f'<td class="red">❌</td></tr>'
    delta_cls = "delta-ok" if r["delta"] <= PLANET_TOL else "delta-bad"
    ref_r  = '<span class="retro">℞</span>' if r["ref_retro"]  else ""
    calc_r = '<span class="retro">℞</span>' if r["calc_retro"] else ""
    retro_ok = "✅" if r["ref_retro"] == r["calc_retro"] else "❌"
    lon_ok   = "✅" if r["delta"] <= PLANET_TOL else "⚠️"
    return (
        f'<tr class="{ok_cls}">'
        f'<td><b>{r["symbol"]}</b> {r["planet"]}</td>'
        f'<td>{_fmt(r["ref_lon"])} ({r["ref_lon"]:.4f}°) {ref_r}</td>'
        f'<td>{_fmt(r["calc_lon"])} ({r["calc_lon"]:.4f}°) {calc_r}</td>'
        f'<td class="{delta_cls}">{r["delta"]:.5f}°</td>'
        f'<td>{lon_ok} {retro_ok}</td>'
        f'</tr>'
    )

def _angle_row(r):
    ok_cls = "ok" if r["ok"] else "bad"
    if r["calc"] is None:
        return f'<tr class="{ok_cls}"><td><b>{r["name"]}</b></td>' \
               f'<td>{_fmt(r["ref"])}</td><td class="red">НЕ ВЫЧИСЛЕНО</td>' \
               f'<td>—</td><td class="red">❌</td></tr>'
    delta_cls = "delta-ok" if r["delta"] <= ANGLE_TOL else "delta-bad"
    return (
        f'<tr class="{ok_cls}">'
        f'<td><b>{r["name"]}</b></td>'
        f'<td>{_fmt(r["ref"])} ({r["ref"]:.4f}°)</td>'
        f'<td>{_fmt(r["calc"])} ({r["calc"]:.4f}°)</td>'
        f'<td class="{delta_cls}">{r["delta"]:.5f}°</td>'
        f'<td>{"✅" if r["ok"] else "⚠️"}</td>'
        f'</tr>'
    )

def _house_row(r):
    ok_cls    = "ok" if r["ok"] else "bad"
    delta_cls = "delta-ok" if r["delta"] <= ANGLE_TOL else "delta-bad"
    return (
        f'<tr class="{ok_cls}">'
        f'<td>{r["house"]}</td>'
        f'<td>{_fmt(r["ref"])} ({r["ref"]:.4f}°)</td>'
        f'<td>{_fmt(r["calc"])} ({r["calc"]:.4f}°)</td>'
        f'<td class="{delta_cls}">{r["delta"]:.5f}°</td>'
        f'<td>{"✅" if r["ok"] else "⚠️"}</td>'
        f'</tr>'
    )

def render_section(comp: dict) -> str:
    pct = int(comp["passed"] / comp["total"] * 100) if comp["total"] else 0
    bar_w = pct
    bar_cls = "chart-bar" if pct >= 80 else "chart-bar-bad"
    badge_cls = "green" if pct == 100 else ("yellow" if pct >= 80 else "red")

    planet_rows = "\n".join(_planet_row(r) for r in comp["planet_rows"])
    angle_rows  = "\n".join(_angle_row(r) for r in comp["angle_rows"])
    house_rows  = "\n".join(_house_row(r) for r in comp["house_rows"])

    return f"""
<div class="section">
  <h2>{comp["name"]}</h2>
  <div class="meta">UTC: {comp["utc"]} &nbsp;|&nbsp; Lat: {comp["lat"]} Lon: {comp["lon"]}</div>
  <div class="summary">
    <div class="badge">
      <div class="val {badge_cls}">{comp["passed"]}/{comp["total"]}</div>
      <div class="lbl">Планеты OK</div>
    </div>
    <div class="badge">
      <div class="val {badge_cls}">{pct}%</div>
      <div class="lbl">Совпадений</div>
    </div>
    <div class="badge" style="flex:1; align-items:center; display:flex; gap:10px">
      <span style="font-size:0.8rem; color:#8888aa">Точность:</span>
      <div style="flex:1; background:#1a1a2e; border-radius:5px; height:10px">
        <div class="{bar_cls}" style="width:{bar_w}%"></div>
      </div>
    </div>
  </div>

  <h3>🪐 Планеты (допуск ±{PLANET_TOL}°)</h3>
  <table>
    <thead><tr>
      <th>Планета</th><th>Эталон (Zet/SE)</th><th>Расчёт</th><th>Δ (°)</th><th>OK</th>
    </tr></thead>
    <tbody>{planet_rows}</tbody>
  </table>

  <h3>⬆️ Углы (допуск ±{ANGLE_TOL}°)</h3>
  <table>
    <thead><tr>
      <th>Угол</th><th>Эталон</th><th>Расчёт</th><th>Δ (°)</th><th>OK</th>
    </tr></thead>
    <tbody>{angle_rows}</tbody>
  </table>

  <h3>🏠 Дома Плацидус (допуск ±{ANGLE_TOL}°)</h3>
  <table>
    <thead><tr>
      <th>Дом</th><th>Эталон</th><th>Расчёт</th><th>Δ (°)</th><th>OK</th>
    </tr></thead>
    <tbody>{house_rows}</tbody>
  </table>
</div>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate reference comparison HTML report")
    parser.add_argument("--output", default=str(ROOT / "docs" / "reference_comparison.html"))
    args = parser.parse_args()

    ref_path = ROOT / "tests" / "fixtures" / "zet_reference_charts.json"
    reference = json.loads(ref_path.read_text(encoding="utf-8"))

    CHART_LABELS = {
        "einstein": "Альберт Эйнштейн (14.03.1879, 10:50 UTC, Ulm DE)",
        "marilyn":  "Мэрилин Монро (01.06.1926, 17:30 UTC, Los Angeles CA)",
        "rehovot":  "Карта Рехово́та (08.01.1982, 11:40 UTC)",
    }

    sections_html = ""
    total_pass, total_all = 0, 0
    for key, label in CHART_LABELS.items():
        ref = reference[key]
        print(f"Вычисляю: {label}...")
        comp = build_comparison(label, ref)
        sections_html += render_section(comp)
        total_pass += comp["passed"]
        total_all  += comp["total"]

    overall_pct = int(total_pass / total_all * 100) if total_all else 0

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Astro — Сравнение с эталоном Zet/SE</title>
  <style>{CSS}</style>
</head>
<body>
  <h1>🔭 Сравнение с эталоном Swiss Ephemeris / Zet</h1>
  <p class="meta">
    Сгенерировано: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} &nbsp;|&nbsp;
    Допуск планет: ±{PLANET_TOL}° &nbsp;|&nbsp; Допуск углов: ±{ANGLE_TOL}° &nbsp;|&nbsp;
    <b>Итого: {total_pass}/{total_all} ({overall_pct}%)</b>
  </p>
  <p class="meta" style="margin-bottom:16px">
    Zet использует Swiss Ephemeris — тот же движок, что и наше приложение.
    Расхождения &gt; ±0.01° указывают на ошибки в расчётах (орбсы, округление, временной пояс).
  </p>
  {sections_html}
</body>
</html>"""

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"\n✅ Отчёт сохранён: {out}")
    print(f"   Итого планет OK: {total_pass}/{total_all} ({overall_pct}%)")


if __name__ == "__main__":
    main()
