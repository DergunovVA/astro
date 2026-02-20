import json
import os
import sys
from pathlib import Path
from typing import Optional, List

# Add src directory to Python path when running as a script
# This allows imports like "from modules.X" to work
# MUST be done before importing local modules
project_root = Path(__file__).parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import typer  # noqa: E402

from modules.astro_adapter import natal_calculation  # noqa: E402
from modules.interpretation_layer import (  # noqa: E402
    facts_from_calculation,
    signals_from_facts,
    decisions_from_signals,
)
from modules.psychological_layer import get_psychological_analysis  # noqa: E402
from input_pipeline import normalize_input, InputContext  # noqa: E402
from modules.comparative_charts import comparative_charts, load_cities_from_file  # noqa: E402
from modules.synastry import calculate_synastry_aspects, calculate_composite_chart  # noqa: E402

# Force UTF-8 encoding for all I/O (fixes Windows cp1252 encoding issues)
# Force UTF-8 encoding on Windows for proper Unicode output
# Note: Use reconfigure() instead of TextIOWrapper to avoid pytest conflicts
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Python <3.7 fallback
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

os.environ["PYTHONIOENCODING"] = "utf-8"

app = typer.Typer()


@app.command()
def natal(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    explain: bool = False,
    devils: bool = False,
    house_system: str = "Placidus",
    extended: bool = True,  # Changed default to True for applying/separating aspects
    psychological: bool = False,
    format: str = "json",  # Output format: json, summary, table, markdown
    validate: bool = False,  # Professional: validate formulas and calculations
    find_events: str = "",  # Professional: find events/patterns (e.g., "mars saturn", "grand trine", "stellium")
    check: str = "",  # DSL: check formula on chart (e.g., "Sun.Sign == Capricorn AND Moon.House IN [1,4,7,10]")
):
    try:
        # Step 1: Normalize input
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)

        # Step 2: Calculate using normalized data directly
        # Use extended=True to include retrograde indicators and full planet data
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method=house_system, extended=extended
        )

        # Step 3: Interpret
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)

        # Step 4: CLI output
        result = {
            "input_metadata": ctx.to_metadata_dict(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions],
        }
        if explain:
            result["explain"] = [
                {"signal": s.id, "reason": "Demo reason"} for s in signals
            ]
            result["fix"] = [{"signal": s.id, "advice": "Demo advice"} for s in signals]
        if devils:
            result["devils"] = {"raw": True, "calc": calc_result}
        if psychological:
            psych = get_psychological_analysis(calc_result, facts)
            result["psychological"] = psych

        # Professional tools
        if validate:
            from src.professional import validate_aspect_orbs, validate_dignities

            # Convert Pydantic models to dicts for professional tools
            facts_dict = [
                f.model_dump() if hasattr(f, "model_dump") else f for f in facts
            ]

            result["validation"] = {
                "orbs": validate_aspect_orbs(facts_dict, strict=False),
                "dignities": validate_dignities(facts_dict),
            }

        if find_events:
            from src.professional.event_finder import search_events

            # Convert Pydantic models to dicts for professional tools
            facts_dict = [
                f.model_dump() if hasattr(f, "model_dump") else f for f in facts
            ]

            result["events"] = search_events(facts_dict, find_events, max_orb=5.0)

        # DSL formula check
        if check:
            from src.dsl import evaluate
            from src.dsl.chart_converter import (
                convert_chart_for_evaluator,
                format_dsl_result,
            )
            from src.dsl.lexer import LexerError
            from src.dsl.parser import ParserError
            from src.dsl.evaluator import EvaluatorError

            try:
                # Конвертируем данные карты в формат для Evaluator
                chart_data = convert_chart_for_evaluator(calc_result)

                # Выполняем DSL формулу
                dsl_result = evaluate(check, chart_data)

                # Форматируем результат
                formatted = format_dsl_result(
                    formula=check,
                    result=dsl_result,
                    chart_data=chart_data,
                    verbose=True,
                )

                # Если check используется, выводим только результат DSL
                typer.echo(formatted)
                return  # Завершаем выполнение, не выводим JSON

            except LexerError as e:
                typer.echo(f"❌ Lexer Error: {e}", err=True)
                raise typer.Exit(code=2)
            except ParserError as e:
                typer.echo(f"❌ Parser Error: {e}", err=True)
                raise typer.Exit(code=2)
            except EvaluatorError as e:
                typer.echo(f"❌ Evaluator Error: {e}", err=True)
                raise typer.Exit(code=2)
            except Exception as e:
                typer.echo(f"❌ Unexpected DSL Error: {e}", err=True)
                import traceback

                traceback.print_exc()
                raise typer.Exit(code=1)

        # Output formatting based on format parameter
        if format == "json":
            typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
        elif format == "summary":
            from src.modules.output_formatter import format_summary

            typer.echo(format_summary(result))
        elif format == "table":
            from src.modules.output_formatter import format_table

            typer.echo(format_table(result))
        elif format == "markdown":
            from src.modules.output_formatter import format_markdown

            typer.echo(format_markdown(result))
        else:
            typer.echo(
                f"Unknown format: {format}. Use: json, summary, table, markdown",
                err=True,
            )
            raise typer.Exit(code=2)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def transit(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
):
    try:
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions],
        }
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def solar(
    year: int,
    natal_date: str,
    natal_time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
):
    try:
        ni = normalize_input(
            natal_date,
            natal_time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions],
        }
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def relocate(place: str):
    from input_pipeline import resolve_city
    from input_pipeline.cache import JsonCache

    cache = JsonCache()
    rp = resolve_city(place, cache)

    result = {
        "query": rp.query,
        "place": rp.name,
        "country": rp.country,
        "coords": {"lat": rp.lat, "lon": rp.lon},
        "timezone": rp.tz_name,
        "source": rp.source,
        "confidence": rp.confidence,
    }
    if rp.warnings:
        result["warnings"] = [
            {"code": w.code, "message": w.message} for w in rp.warnings
        ]

    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))


@app.command()
def rectify(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
):
    try:
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "candidates": [],
            "facts_count": len(facts),
        }
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def devils(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
):
    try:
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        result = {
            "input_metadata": ctx.to_metadata_dict(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions],
            "devils": {
                "raw": True,
                "calc": calc_result,
                "weights": [s.weight for s in signals]
                if any(s.weight for s in signals)
                else [],
            },
        }
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def comparative(
    date: str,
    time: str,
    chart_type: str = typer.Option(
        "natal", help="Chart type: natal, transit, solar, relocation"
    ),
    cities_file: Optional[str] = typer.Option(
        None, help="File with city names (one per line)"
    ),
    cities: Optional[List[str]] = typer.Argument(
        None, help="City names (if not using cities_file)"
    ),
    tz: Optional[str] = typer.Option(None, help="Override timezone for all cities"),
):
    """
    Calculate comparative charts for the same date/time across multiple cities.

    Usage:
      # From file
      python main.py comparative 1985-01-15 14:30 --chart-type natal --cities-file cities.txt

      # From command line
      python main.py comparative 1985-01-15 14:30 --chart-type natal Moscow London Tokyo
    """
    try:
        # Determine which cities to use
        if cities_file:
            cities_list = load_cities_from_file(cities_file)
            typer.echo(f"Loaded {len(cities_list)} cities from {cities_file}", err=True)
        elif cities:
            cities_list = cities
        else:
            typer.echo(
                "Error: provide either --cities-file or city names as arguments",
                err=True,
            )
            raise typer.Exit(code=2)

        # Validate chart type
        valid_types = {"natal", "transit", "solar", "relocation"}
        if chart_type not in valid_types:
            typer.echo(f"Error: chart_type must be one of {valid_types}", err=True)
            raise typer.Exit(code=2)

        # Calculate comparative charts
        result = comparative_charts(
            date_str=date,
            time_str=time,
            cities=cities_list,
            chart_type=chart_type,
            tz_override=tz,
        )

        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def synastry(
    date1: str,
    time1: str,
    place1: str,
    date2: str,
    time2: str,
    place2: str,
    tz1: str | None = None,
    tz2: str | None = None,
    house_system: str = "Placidus",
    include_minor: bool = False,
):
    """Compare two natal charts (synastry/relationship astrology).

    Usage:
    python main.py synastry 1990-05-15 14:30 Moscow 1992-03-20 10:15 London

    Returns: Synastry aspects, composite chart insights, relationship indicators.
    """
    try:
        # Normalize both inputs
        ni1 = normalize_input(date1, time1, place1, tz_override=tz1)
        ni2 = normalize_input(date2, time2, place2, tz_override=tz2)
        ctx1 = InputContext.from_normalized(ni1)
        ctx2 = InputContext.from_normalized(ni2)

        # Calculate both natal charts
        calc1 = natal_calculation(
            ctx1.utc_dt, ctx1.lat, ctx1.lon, house_method=house_system
        )
        calc2 = natal_calculation(
            ctx2.utc_dt, ctx2.lat, ctx2.lon, house_method=house_system
        )

        # Calculate synastry aspects (cross-chart)
        synastry_aspects = calculate_synastry_aspects(
            calc1["planets"], calc2["planets"], include_minor=include_minor
        )

        # Calculate composite chart
        composite = calculate_composite_chart(calc1, calc2)

        # Sort synastry aspects by importance (major hard > major soft > minor)
        def aspect_priority(asp):
            category_val = 0 if asp["category"] == "major" else 1
            type_val = 0 if asp["type"] == "hard" else 1
            orb_val = asp["orb"]  # Smaller orb = tighter = more important
            return (category_val, type_val, orb_val)

        synastry_aspects.sort(key=aspect_priority)

        result = {
            "synastry_summary": {
                "person1": {"date": date1, "time": time1, "place": place1},
                "person2": {"date": date2, "time": time2, "place": place2},
                "total_aspects": len(synastry_aspects),
                "house_system": house_system,
            },
            "synastry_aspects": synastry_aspects[:20],  # Top 20 aspects
            "chart1_metadata": ctx1.to_metadata_dict(),
            "chart2_metadata": ctx2.to_metadata_dict(),
            "composite_planets": composite["planets"],
            "composite_houses": composite["houses"],
        }

        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def psychology(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    focus: str | None = None,  # shadow, demon, impulse, proof, revenge
):
    """
    Глубинный психологический анализ натальной карты.

    Анализирует:
    - Тени (подавленные качества)
    - Демоны (деструктивные паттерны)
    - Позывы (неосознанные мотивации)
    - Доказухи (компенсаторное поведение)
    - Мести (обиды, желание компенсировать)

    Примеры:
    python main.py psychology "8 Jan 1982" "13:40" "Saratov"
    python main.py psychology "8 Jan 1982" "13:40" "Saratov" --focus shadow
    """
    try:
        # Normalize input
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        ctx = InputContext.from_normalized(ni)

        # Calculate with extended mode for retrograde detection
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon, extended=True)
        facts = facts_from_calculation(calc_result)

        # Psychological analysis
        psych = get_psychological_analysis(calc_result, facts)

        # Filter by focus if specified
        if focus:
            valid_types = ["shadow", "demon", "impulse", "proof", "revenge"]
            if focus not in valid_types:
                typer.echo(f"Error: focus must be one of {valid_types}", err=True)
                raise typer.Exit(code=2)

            # Map singular to plural key
            key_map = {
                "shadow": "shadows",
                "demon": "demons",
                "impulse": "impulses",
                "proof": "proofs",
                "revenge": "revenges",
            }
            key = key_map[focus]
            result = {
                "input_metadata": ctx.to_metadata_dict_minimal(),
                focus: psych[key],
            }
        else:
            result = {
                "input_metadata": ctx.to_metadata_dict_minimal(),
                "psychological": psych,
            }

        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
