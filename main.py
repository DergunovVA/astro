import io
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
    calculate_house_positions,
    calculate_essential_dignity,
    calculate_accidental_dignity,
    is_day_chart,
)
from modules.psychological_layer import get_psychological_analysis  # noqa: E402
from core.core_geometry import planet_in_sign  # noqa: E402
from core.dignities import ZODIAC_SIGNS  # noqa: E402
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
    format: str = "json",  # Output format: json, summary, table, markdown, compact, line
    no_color: bool = False,  # Disable ANSI colors in output
    validate: bool = False,  # Professional: validate formulas and calculations
    find_events: str = "",  # Professional: find events/patterns (e.g., "mars saturn", "grand trine", "stellium")
    check: str = "",  # DSL: check formula on chart (e.g., "Sun.Sign == Capricorn AND Moon.House IN [1,4,7,10]")
    verbose: bool = False,  # Verbose output with detailed explanations
    quiet: bool = False,  # Quiet mode: minimal output (only results and errors)
):
    try:
        # Configure CLI output based on verbosity flags
        from src.cli import configure_output

        out = configure_output(verbose=verbose, quiet=quiet)
        # Step 1: Normalize input
        out.verbose("Step 1: Normalizing input...")
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
        out.verbose(f"  UTC: {ctx.utc_dt}")
        out.verbose(f"  Location: {ctx.lat:.4f}, {ctx.lon:.4f}")

        # Step 2: Calculate using normalized data directly
        # Use extended=True to include retrograde indicators and full planet data
        out.verbose("Step 2: Calculating planetary positions...")
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method=house_system, extended=extended
        )
        if isinstance(calc_result, dict):
            out.verbose(f"  Planets calculated: {len(calc_result.get('planets', {}))}")
        else:
            out.verbose("  Calculation complete")

        # Step 3: Interpret
        out.verbose("Step 3: Interpreting chart...")
        facts = facts_from_calculation(calc_result)
        out.verbose(f"  Facts extracted: {len(facts)}")
        signals = signals_from_facts(facts)
        out.verbose(f"  Signals generated: {len(signals)}")
        decisions = decisions_from_signals(signals)
        out.verbose(f"  Decisions made: {len(decisions)}")

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
            )
            from src.dsl.lexer import LexerError
            from src.dsl.parser import ParserError
            from src.dsl.evaluator import EvaluatorError

            try:
                # Конвертируем данные карты в формат для Evaluator
                out.verbose("Converting chart data for DSL evaluator...")
                chart_data = convert_chart_for_evaluator(calc_result)

                # Выполняем DSL формулу
                out.verbose(f"Evaluating formula: {check}")
                dsl_result = evaluate(check, chart_data)

                # Форматируем результат используя CLIOutput
                formatted = out.format_dsl_result(
                    formula=check,
                    result=dsl_result,
                    chart_data=chart_data,
                )

                # Если check используется, выводим только результат DSL
                out.quiet(formatted)
                return  # Завершаем выполнение, не выводим JSON

            except LexerError as e:
                out.error(f"❌ Lexer Error: {e}")
                raise typer.Exit(code=2)
            except ParserError as e:
                out.error(f"❌ Parser Error: {e}")
                raise typer.Exit(code=2)
            except EvaluatorError as e:
                out.error(f"❌ Evaluator Error: {e}")
                raise typer.Exit(code=2)
            except Exception as e:
                out.error(f"❌ Unexpected DSL Error: {e}")
                if verbose:
                    import traceback

                    traceback.print_exc()
                raise typer.Exit(code=1)

        # Output formatting based on format parameter
        out.verbose(f"Step 4: Formatting output (format={format})...")
        if format == "json":
            out.json_result(result)
        elif format == "summary":
            from src.modules.output_formatter import format_summary

            out.quiet(format_summary(result))
        elif format == "table":
            from src.modules.output_formatter import format_table

            out.quiet(format_table(result, use_colors=not no_color))
        elif format == "markdown":
            from src.modules.output_formatter import format_markdown

            out.quiet(format_markdown(result))
        elif format == "compact":
            from src.modules.output_formatter import format_compact

            out.quiet(format_compact(result))
        elif format == "line":
            from src.modules.output_formatter import format_summary_line

            out.quiet(format_summary_line(result))
        else:
            out.error(
                f"Unknown format: {format}. Use: json, summary, table, markdown, compact, line"
            )
            raise typer.Exit(code=2)
    except ValueError as e:
        # Configure output for error handling (in case not configured yet)
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Error: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Unexpected error: {e}")
        if "verbose" in locals() and verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def aspects(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    house_system: str = "Placidus",
    aspect_type: str = "all",  # Filter: all, major, minor
    max_orb: float = 10.0,  # Maximum orb to display
    planets: str = typer.Option(
        None,
        help="Filter by specific planets (comma-separated, e.g., 'Moon,Saturn,Jupiter')",
    ),
    no_color: bool = False,  # Disable colors
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Display aspects for a natal chart.

    Filters:
    - aspect_type: all (default), major (conjunction/opposition/square/trine/sextile), minor
    - max_orb: maximum orb in degrees (default: 10.0)
    - planets: filter by specific planets (e.g., --planets "Moon,Saturn,Jupiter")

    Examples:
        python main.py aspects 1982-01-08 09:40 Saratov
        python main.py aspects 1982-01-08 09:40 Saratov --aspect-type major
        python main.py aspects 1982-01-08 09:40 Saratov --max-orb 5
        python main.py aspects 2026-02-28 00:16 "Rehovot, Israel" --planets "Moon,Saturn,Jupiter"
    """
    try:
        from src.cli import configure_output

        out = configure_output(verbose=verbose, quiet=quiet)

        # Step 1: Normalize input
        out.verbose("Step 1: Normalizing input...")
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

        # Step 2: Calculate chart
        out.verbose("Step 2: Calculating planetary positions...")
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method=house_system, extended=True
        )

        # Step 3: Get facts
        out.verbose("Step 3: Extracting aspects...")
        facts = facts_from_calculation(calc_result)

        # Build result
        result = {
            "input_metadata": ctx.to_metadata_dict(),
            "facts": [f.model_dump() for f in facts],
        }

        # Parse planet filter
        planet_filter = None
        if planets:
            planet_filter = [p.strip() for p in planets.split(",")]

        # Format and display
        from src.modules.output_formatter import format_aspects

        out.quiet(
            format_aspects(
                result,
                aspect_type=aspect_type,
                max_orb=max_orb,
                planet_filter=planet_filter,
                use_colors=not no_color,
            )
        )

    except ValueError as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Error: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Unexpected error: {e}")
        if "verbose" in locals() and verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def dignities(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    house_system: str = "Placidus",
    no_color: bool = False,  # Disable colors
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Display planetary dignities (essential + accidental).

    Shows:
    - Essential dignities: domicile, exaltation, detriment, fall
    - Accidental dignities: house position, motion/speed
    - Total dignity score and strength level

    Examples:
        python main.py dignities 1982-01-08 09:40 Saratov
    """
    try:
        from src.cli import configure_output

        out = configure_output(verbose=verbose, quiet=quiet)

        # Step 1: Normalize input
        out.verbose("Step 1: Normalizing input...")
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

        # Step 2: Calculate chart
        out.verbose("Step 2: Calculating planetary positions...")
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method=house_system, extended=True
        )

        # Step 3: Get facts
        out.verbose("Step 3: Calculating dignities...")
        facts = facts_from_calculation(calc_result)

        # Build result
        result = {
            "input_metadata": ctx.to_metadata_dict(),
            "facts": [f.model_dump() for f in facts],
        }

        # Format and display
        from src.modules.output_formatter import format_dignities

        out.quiet(format_dignities(result, use_colors=not no_color))

    except ValueError as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Error: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Unexpected error: {e}")
        if "verbose" in locals() and verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def transit(
    natal_date: str,
    natal_time: str,
    natal_place: str,
    transit_date: str = typer.Option(None, help="Transit date (default: now)"),
    transit_time: str = typer.Option(None, help="Transit time (default: now)"),
    max_orb: float = typer.Option(3.0, help="Maximum orb for aspects"),
    no_color: bool = typer.Option(False, help="Disable color output"),
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Display current transits to natal chart.

    Examples:
        python main.py transit 1982-01-08 09:40 Saratov
        python main.py transit 1982-01-08 09:40 Saratov --max-orb 5
        python main.py transit 1982-01-08 09:40 Saratov --transit-date 2026-03-01 --transit-time 12:00
    """
    from src.cli import configure_output

    out = configure_output(verbose=verbose, quiet=quiet)

    try:
        from datetime import datetime
        from src.modules.output_formatter import format_transits

        # Normalize natal input
        out.info(
            f"Calculating natal chart for {natal_date} {natal_time} {natal_place}..."
        )
        natal_ni = normalize_input(
            natal_date,
            natal_time,
            natal_place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        natal_ctx = InputContext.from_normalized(natal_ni)

        # Calculate natal chart
        natal_calc = natal_calculation(
            natal_ctx.utc_dt,
            natal_ctx.lat,
            natal_ctx.lon,
            extended=False,  # Just need longitudes for synastry
        )
        natal_planets = natal_calc.get("planets", {})

        # Normalize transit input (default to now)
        if transit_date is None:
            transit_date = datetime.now().strftime("%Y-%m-%d")
        if transit_time is None:
            transit_time = datetime.now().strftime("%H:%M")

        out.info(f"Calculating transits for {transit_date} {transit_time}...")
        transit_ni = normalize_input(
            transit_date,
            transit_time,
            natal_place,  # Use natal place for transits
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
            locale=locale,
            strict=strict,
        )
        transit_ctx = InputContext.from_normalized(transit_ni)

        # Calculate transit chart
        transit_calc = natal_calculation(
            transit_ctx.utc_dt,
            transit_ctx.lat,
            transit_ctx.lon,
            extended=False,  # Just need longitudes for synastry
        )
        transit_planets = transit_calc.get("planets", {})

        # Calculate transit-to-natal aspects
        out.info("Calculating transit aspects...")
        transit_aspects = calculate_synastry_aspects(
            transit_planets, natal_planets, include_minor=True, min_orb=0.0
        )

        # Prepare data for formatting (need full calc for metadata)
        natal_data = {**natal_calc, "input_metadata": natal_ctx.to_metadata_dict()}

        transit_data = {
            **transit_calc,
            "input_metadata": transit_ctx.to_metadata_dict(),
        }

        # Format and display
        formatted = format_transits(
            natal_data,
            transit_data,
            transit_aspects,
            lang="ru",
            max_orb=max_orb,
            use_colors=not no_color,
        )
        out.quiet(formatted)

    except ValueError as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Error: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        from src.cli import configure_output

        out = configure_output(
            verbose=verbose if "verbose" in locals() else False,
            quiet=quiet if "quiet" in locals() else False,
        )
        out.error(f"Unexpected error: {e}")
        if "verbose" in locals() and verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def horary(
    date: str,
    time: str,
    place: str,
    question_type: str = typer.Option(
        "lost-item",
        help="Type of question: lost-item, will-it-happen, timing, relationship",
    ),
    quesited_house: int = typer.Option(
        None, help="House number for quesited (default: auto from question type)"
    ),
    no_color: bool = typer.Option(False, help="Disable color output"),
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str | None = None,
    strict: bool = False,
    verbose: bool = False,
    quiet: bool = False,
):
    """
    Horary astrology analysis for specific questions.

    Question Types:
    - lost-item: Analyze lost object location and recovery (uses 2nd house)
    - will-it-happen: Yes/No outcome prediction
    - timing: When will event happen
    - relationship: Relationship outcome (uses 7th house)

    Examples:
        python main.py horary 2026-02-28 00:16 "Rehovot, Israel" --question-type lost-item
        python main.py horary 2026-02-28 00:16 "Rehovot, Israel" --question-type will-it-happen --quesited-house 7
        python main.py horary 2026-02-28 00:16 "Rehovot, Israel" --question-type timing --quesited-house 10
    """
    from src.cli import configure_output

    out = configure_output(verbose=verbose, quiet=quiet)

    try:
        from src.modules.horary import (
            time_to_perfection,
            is_void_of_course,
            check_radicality,
            find_mutual_receptions,
        )
        from src.core.dignities import get_planet_sign, get_dispositor
        from src.core.aspects_math import calc_aspects
        from colorama import Fore, Style

        # Normalize input
        out.info(f"Casting horary chart for {date} {time} {place}...")
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

        # Calculate chart with extended data
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method="Placidus", extended=True
        )

        planets = calc_result.get("planets", {})
        houses = calc_result.get("houses", [])  # List of 12 house cusps

        # Determine quesited house based on question type
        if quesited_house is None:
            quesited_map = {
                "lost-item": 2,
                "will-it-happen": 7,
                "timing": 7,
                "relationship": 7,
            }
            quesited_house = quesited_map.get(question_type, 7)

        # Get chart metadata
        metadata = ctx.to_metadata_dict()

        # === EXTRACT PLANET DATA ===
        # Normalize planet longitudes and speeds
        planet_longs = {
            name: data.get("longitude", 0) for name, data in planets.items()
        }

        # Calculate house positions for all planets
        planet_houses = calculate_house_positions(houses, planet_longs)

        # Determine if day/night chart for dignity calculations
        sun_lon = planet_longs.get("Sun", 0)
        asc_lon = houses[0] if houses else 0
        is_day = is_day_chart(sun_lon, asc_lon)

        # === CHART RADICALITY CHECK ===
        saturn_house = planet_houses.get("Saturn", 0)
        radicality = check_radicality(asc_lon, saturn_house)

        # === VOID OF COURSE MOON ===
        moon_data = planets.get("Moon", {})
        moon_lon = moon_data.get("longitude", 0)
        moon_speed = moon_data.get("speed", 13.0)  # lowercase "speed"

        voc_result = is_void_of_course(moon_lon, moon_speed, planet_longs)

        # === SIGNIFICATORS ===
        # Querent: 1st house ruler (use traditional rulers for horary)
        house1_sign = get_planet_sign(asc_lon)
        querent_ruler = get_dispositor(house1_sign, traditional=True)

        # Quesited: specified house ruler (use traditional rulers for horary)
        quesited_cusp = (
            houses[quesited_house - 1] if quesited_house <= len(houses) else 0
        )
        quesited_sign = get_planet_sign(quesited_cusp)
        quesited_ruler = get_dispositor(quesited_sign, traditional=True)

        # Calculate detailed data for significators
        def get_planet_details(planet_name):
            """Get Sign, House, and Dignity for a planet"""
            if planet_name not in planet_longs:
                return {"sign": "N/A", "house": "N/A", "dignity": "N/A"}

            lon = planet_longs[planet_name]
            sign_idx = planet_in_sign(lon)
            sign_name = ZODIAC_SIGNS[sign_idx]
            house = planet_houses.get(planet_name, 0)

            # Calculate essential dignity
            essential = calculate_essential_dignity(planet_name, lon, is_day)

            # Calculate accidental dignity
            planet_data = planets.get(planet_name, {})
            speed = planet_data.get("speed", 0.0)
            is_retro = planet_data.get("retrograde", False)

            accidental = calculate_accidental_dignity(
                planet=planet_name,
                house=house,
                is_retrograde=is_retro,
                speed=speed,
                longitude=lon,
                sun_longitude=sun_lon,
            )

            # Combine for total dignity
            total_score = essential["score"] + accidental["score"]
            if total_score >= 5:
                dignity_level = "Very Strong"
            elif total_score >= 2:
                dignity_level = "Strong"
            elif total_score >= -2:
                dignity_level = "Moderate"
            elif total_score >= -5:
                dignity_level = "Weak"
            else:
                dignity_level = "Very Weak"

            return {
                "sign": sign_name,
                "house": house,
                "dignity": dignity_level,
                "dignity_score": total_score,
            }

        querent_data = get_planet_details(querent_ruler)
        quesited_data = get_planet_details(quesited_ruler)

        # === MUTUAL RECEPTIONS ===
        mutual_receptions = find_mutual_receptions(planets)

        # === KEY ASPECTS ===
        # Moon to quesited ruler (most important for lost items)
        moon_lon = planet_longs.get("Moon", 0)
        quesited_lon = planet_longs.get(quesited_ruler, 0)

        # Calculate all aspects
        all_aspects = calc_aspects(planet_longs, include_minor=True, min_orb=0.1)

        # Find Moon-Quesited aspect
        moon_quesited_aspect = None
        for p1, p2, asp_type, orb, category in all_aspects:
            if (p1 == "Moon" and p2 == quesited_ruler) or (
                p1 == quesited_ruler and p2 == "Moon"
            ):
                moon_quesited_aspect = {
                    "type": asp_type,
                    "orb": orb,
                    "category": category,
                }
                break

        # === TIME TO PERFECTION ===
        perfection_time = None
        if moon_quesited_aspect:
            from src.core.aspects_math import ASPECTS

            aspect_angle = ASPECTS[moon_quesited_aspect["type"]]["angle"]

            moon_speed = planets.get("Moon", {}).get("speed", 13.0)
            quesited_speed = planets.get(quesited_ruler, {}).get("speed", 0.0)

            perfection_time = time_to_perfection(
                moon_lon, moon_speed, quesited_lon, quesited_speed, aspect_angle
            )

        # === FORMAT OUTPUT ===
        use_colors = not no_color

        def color(text, color_code):
            return f"{color_code}{text}{Style.RESET_ALL}" if use_colors else text

        output = []
        output.append("\n" + "═" * 80)
        output.append(color("ХОРАРНЫЙ АНАЛИЗ", Fore.CYAN))
        output.append("═" * 80)

        # Question info
        output.append(f"\n{color('Вопрос:', Fore.YELLOW)} {question_type}")
        output.append(f"{color('Время:', Fore.YELLOW)} {metadata['local_datetime']}")
        output.append(
            f"{color('Место:', Fore.YELLOW)} {metadata['place']['name']}, {metadata['place']['country']}"
        )
        output.append(
            f"{color('Координаты:', Fore.YELLOW)} {metadata['coordinates']['lat']:.2f}°N, {metadata['coordinates']['lon']:.2f}°E"
        )

        # Radicality check
        output.append(f"\n{color('═══ РАДИКАЛЬНОСТЬ КАРТЫ ═══', Fore.CYAN)}")
        if radicality["is_radical"]:
            output.append(
                color("✓ Карта радикальна (валидна для суждения)", Fore.GREEN)
            )
        else:
            output.append(color("✗ Карта НЕ радикальна - будьте осторожны!", Fore.RED))
        output.append(f"ASC: {radicality['asc_degree_in_sign']:.1f}° в знаке")
        for warning in radicality["warnings"]:
            output.append(color(f"  ⚠ {warning}", Fore.YELLOW))

        # VOC Moon
        output.append(f"\n{color('═══ ЛУНА БЕЗ КУРСА ═══', Fore.CYAN)}")
        if voc_result["is_void"]:
            output.append(
                color("✗ Луна БЕЗ КУРСА (не рекомендуется для суждения)", Fore.RED)
            )
        else:
            output.append(
                color("✓ Луна делает аспекты (хорошо для хорара)", Fore.GREEN)
            )
        output.append(f"Текущий знак: {voc_result['current_sign']}")
        output.append(f"До смены знака: {voc_result['next_sign_in_hours']:.1f} часов")

        # Significators
        output.append(f"\n{color('═══ СИГНИФИКАТОРЫ ═══', Fore.CYAN)}")
        output.append(f"{color('Кверент (1 дом):', Fore.YELLOW)} {querent_ruler}")
        output.append(f"  Знак: {querent_data['sign']}")
        output.append(f"  Дом: {querent_data['house']}")
        output.append(
            f"  Достоинство: {querent_data['dignity']} ({querent_data['dignity_score']:+.0f})"
        )

        output.append(
            f"\n{color('Потерянная вещь (' + str(quesited_house) + ' дом):', Fore.YELLOW)} {quesited_ruler}"
        )
        output.append(f"  Знак: {quesited_data['sign']}")
        output.append(f"  Дом: {quesited_data['house']}")
        output.append(
            f"  Достоинство: {quesited_data['dignity']} ({quesited_data['dignity_score']:+.0f})"
        )

        # Key aspect
        output.append(f"\n{color('═══ КЛЮЧЕВОЙ АСПЕКТ ═══', Fore.CYAN)}")
        if moon_quesited_aspect:
            aspect_symbol = {
                "conjunction": "☌",
                "opposition": "☍",
                "trine": "△",
                "square": "□",
                "sextile": "✶",
            }.get(moon_quesited_aspect["type"], moon_quesited_aspect["type"])

            output.append(f"☽ Луна {aspect_symbol} {quesited_ruler}")
            output.append(
                f"  Тип: {moon_quesited_aspect['type']} ({moon_quesited_aspect['category']})"
            )
            output.append(f"  Орб: {moon_quesited_aspect['orb']:.2f}°")

            if perfection_time and perfection_time["is_applying"]:
                output.append(color("  Движение: APPLYING (сходящийся) ✓", Fore.GREEN))
                output.append(
                    f"  До точного аспекта: {perfection_time['days']:.2f} дней ({perfection_time['hours']:.1f} часов)"
                )
            else:
                output.append(color("  Движение: SEPARATING (расходящийся)", Fore.RED))
        else:
            output.append(color("✗ Нет аспекта между Луной и сигнификатором", Fore.RED))

        # Mutual receptions
        if mutual_receptions:
            output.append(f"\n{color('═══ ВЗАИМНЫЕ РЕЦЕПЦИИ ═══', Fore.CYAN)}")
            for mr in mutual_receptions:
                output.append(color(f"✓ {mr['planet1']} ↔ {mr['planet2']}", Fore.GREEN))
                output.append(
                    f"  {mr['planet1']} в {mr['planet1_sign']} (знак {mr['planet2']})"
                )
                output.append(
                    f"  {mr['planet2']} в {mr['planet2_sign']} (знак {mr['planet1']})"
                )
                output.append(f"  Тип: {mr['type']}")

        # Judgment
        output.append(f"\n{color('═══ СУЖДЕНИЕ ═══', Fore.CYAN)}")
        if question_type == "lost-item":
            if (
                moon_quesited_aspect
                and perfection_time
                and perfection_time["is_applying"]
            ):
                output.append(color("✓ ПРОГНОЗ: Вещь БУДЕТ НАЙДЕНА", Fore.GREEN))
                output.append(
                    f"  Ожидаемое время находки: ~{perfection_time['days']:.1f} дней"
                )
                output.append(
                    "  Гармоничный аспект указывает на легкую находку"
                    if moon_quesited_aspect["type"] in ["trine", "sextile"]
                    else "  Напряженный аспект - потребуются усилия"
                )
            else:
                output.append(
                    color("✗ ПРОГНОЗ: Находка маловероятна или затруднена", Fore.RED)
                )
                if not moon_quesited_aspect:
                    output.append("  Причина: Нет связи между сигнификаторами")
                else:
                    output.append(
                        "  Причина: Аспект расходящийся (возможность упущена)"
                    )

        output.append("\n" + "═" * 80 + "\n")

        out.quiet("\n".join(output))

    except ValueError as e:
        out.error(f"Error: {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        out.error(f"Unexpected error: {e}")
        if verbose:
            import traceback

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


@app.command()
def houses(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    house_system: str = "Placidus",
    format: str = "table",  # table, json, degrees
):
    """
    Вывести координаты всех 12 куспидов домов.

    Форматы вывода:
    - table: Таблица с домами и знаками
    - json: JSON формат
    - degrees: Только градусы (для копирования)

    Примеры:
    python main.py houses "8 Jan 1982" "10:30" "Rehovot, Israel"
    python main.py houses "8 Jan 1982" "10:30" "Rehovot" --format degrees
    python main.py houses "8 Jan 1982" "10:30" "31.8914" "34.8103" --lat 31.8914 --lon 34.8103
    """
    try:
        from src.core.dignities import get_planet_sign, get_planet_degree_in_sign

        # Normalize input
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
        )
        ctx = InputContext.from_normalized(ni)

        # Calculate houses
        calc_result = natal_calculation(
            ctx.utc_dt, ctx.lat, ctx.lon, house_method=house_system
        )

        houses_data = calc_result.get("houses", [])

        if format == "json":
            result = {
                "input": ctx.to_metadata_dict_minimal(),
                "house_system": house_system,
                "houses": [
                    {
                        "house": i + 1,
                        "longitude": houses_data[i],
                        "sign": get_planet_sign(houses_data[i]),
                        "degree": get_planet_degree_in_sign(houses_data[i]),
                    }
                    for i in range(12)
                ],
            }
            typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

        elif format == "degrees":
            typer.echo(f"\n{house_system} Houses:")
            for i in range(12):
                sign = get_planet_sign(houses_data[i])
                deg = get_planet_degree_in_sign(houses_data[i])
                typer.echo(f"House {i + 1:2d}: {deg:6.2f}° {sign}")

        else:  # table
            typer.echo(f"\n━━━ {house_system} Houses ━━━")
            typer.echo(f"Date: {ctx.utc_dt.date()} {ctx.utc_dt.time()} UTC")
            typer.echo(f"Location: {ctx.lat:.4f}, {ctx.lon:.4f}\n")
            typer.echo("House │ Sign        │ Degree   │ Longitude")
            typer.echo("──────┼─────────────┼──────────┼──────────")
            for i in range(12):
                sign = get_planet_sign(houses_data[i])
                deg = get_planet_degree_in_sign(houses_data[i])
                typer.echo(
                    f"  {i + 1:2d}  │ {sign:11s} │ {deg:6.2f}°  │ {houses_data[i]:7.2f}°"
                )
            typer.echo()

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:
        import traceback

        typer.echo(f"Unexpected error: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def arabic_parts(
    date: str,
    time: str,
    place: str,
    tz: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    format: str = "table",  # table, json
):
    """
    Вывести арабские точки (жребии): Part of Fortune, Part of Spirit и др.

    Формулы:
    - Part of Fortune (день): ASC + Moon - Sun
    - Part of Fortune (ночь): ASC + Sun - Moon
    - Part of Spirit: обратная формула

    Примеры:
    python main.py arabic-parts "8 Jan 1982" "10:30" "Rehovot, Israel"
    python main.py arabic-parts "8 Jan 1982" "10:30" "Rehovot" --format json
    """
    try:
        from src.core.dignities import get_planet_sign, get_planet_degree_in_sign

        # Normalize input
        ni = normalize_input(
            date,
            time,
            place,
            tz_override=tz,
            lat_override=lat,
            lon_override=lon,
        )
        ctx = InputContext.from_normalized(ni)

        # Calculate with extended mode
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon, extended=True)

        special_points = calc_result.get("special_points", {})

        if format == "json":
            result = {
                "input": ctx.to_metadata_dict_minimal(),
                "arabic_parts": {
                    name: {
                        "longitude": lon,
                        "sign": get_planet_sign(lon),
                        "degree": get_planet_degree_in_sign(lon),
                    }
                    for name, lon in special_points.items()
                },
            }
            typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

        else:  # table
            typer.echo("\n━━━ Arabic Parts (Жребии) ━━━")
            typer.echo(f"Date: {ctx.utc_dt.date()} {ctx.utc_dt.time()} UTC")
            typer.echo(f"Location: {ctx.lat:.4f}, {ctx.lon:.4f}\n")

            if not special_points:
                typer.echo("No arabic parts calculated.")
            else:
                typer.echo("Point             │ Sign        │ Degree   │ Longitude")
                typer.echo("──────────────────┼─────────────┼──────────┼──────────")
                for name, lon in special_points.items():
                    sign = get_planet_sign(lon)
                    deg = get_planet_degree_in_sign(lon)
                    typer.echo(f"{name:17s} │ {sign:11s} │ {deg:6.2f}°  │ {lon:7.2f}°")
            typer.echo()

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
