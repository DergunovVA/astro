import sys
import os
import io
import typer
import json
from typing import Optional, List
from astro_adapter import natal_calculation
from interpretation_layer import facts_from_calculation, signals_from_facts, decisions_from_signals
from input_pipeline import normalize_input, InputContext
from comparative_charts import comparative_charts, load_cities_from_file

# Force UTF-8 encoding for all I/O (fixes Windows cp1252 encoding issues)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.environ['PYTHONIOENCODING'] = 'utf-8'

app = typer.Typer()

@app.command()
def natal(date: str, time: str, place: str, tz: str | None = None, lat: float | None = None, lon: float | None = None, locale: str | None = None, strict: bool = False, explain: bool = False, devils: bool = False):
    try:
        # Step 1: Normalize input
        ni = normalize_input(date, time, place, tz_override=tz, lat_override=lat, lon_override=lon, locale=locale, strict=strict)
        ctx = InputContext.from_normalized(ni)
        
        # Step 2: Calculate using normalized data directly
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        
        # Step 3: Interpret
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        
        # Step 4: CLI output
        result = {
            "input_metadata": ctx.to_metadata_dict(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions]
        }
        if explain:
            result["explain"] = [{"signal": s.id, "reason": "Demo reason"} for s in signals]
            result["fix"] = [{"signal": s.id, "advice": "Demo advice"} for s in signals]
        if devils:
            result["devils"] = {"raw": True, "calc": calc_result}
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
def transit(date: str, time: str, place: str, tz: str | None = None, lat: float | None = None, lon: float | None = None, locale: str | None = None, strict: bool = False):
    try:
        ni = normalize_input(date, time, place, tz_override=tz, lat_override=lat, lon_override=lon, locale=locale, strict=strict)
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions]
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
def solar(year: int, natal_date: str, natal_time: str, place: str, tz: str | None = None, lat: float | None = None, lon: float | None = None, locale: str | None = None, strict: bool = False):
    try:
        ni = normalize_input(natal_date, natal_time, place, tz_override=tz, lat_override=lat, lon_override=lon, locale=locale, strict=strict)
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        signals = signals_from_facts(facts)
        decisions = decisions_from_signals(signals)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "facts": [f.model_dump() for f in facts],
            "signals": [s.model_dump() for s in signals],
            "decisions": [d.model_dump() for d in decisions]
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
        "coords": {
            "lat": rp.lat,
            "lon": rp.lon
        },
        "timezone": rp.tz_name,
        "source": rp.source,
        "confidence": rp.confidence
    }
    if rp.warnings:
        result["warnings"] = [{"code": w.code, "message": w.message} for w in rp.warnings]
    
    typer.echo(json.dumps(result, indent=2, ensure_ascii=False))

@app.command()
def rectify(date: str, time: str, place: str, tz: str | None = None, lat: float | None = None, lon: float | None = None, locale: str | None = None, strict: bool = False):
    try:
        ni = normalize_input(date, time, place, tz_override=tz, lat_override=lat, lon_override=lon, locale=locale, strict=strict)
        ctx = InputContext.from_normalized(ni)
        calc_result = natal_calculation(ctx.utc_dt, ctx.lat, ctx.lon)
        facts = facts_from_calculation(calc_result)
        result = {
            "input_metadata": ctx.to_metadata_dict_minimal(),
            "candidates": [],
            "facts_count": len(facts)
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
def devils(date: str, time: str, place: str, tz: str | None = None, lat: float | None = None, lon: float | None = None, locale: str | None = None, strict: bool = False):
    try:
        ni = normalize_input(date, time, place, tz_override=tz, lat_override=lat, lon_override=lon, locale=locale, strict=strict)
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
                "weights": [s.weight for s in signals] if any(s.weight for s in signals) else []
            }
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
    chart_type: str = typer.Option("natal", help="Chart type: natal, transit, solar, relocation"),
    cities_file: Optional[str] = typer.Option(None, help="File with city names (one per line)"),
    cities: Optional[List[str]] = typer.Argument(None, help="City names (if not using cities_file)"),
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
            typer.echo("Error: provide either --cities-file or city names as arguments", err=True)
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

if __name__ == "__main__":
    app()
