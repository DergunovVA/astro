from typer.testing import CliRunner
import main

runner = CliRunner()


def test_natal_basic():
    result = runner.invoke(main.app, ["natal", "1990-01-01", "12:00", "Moscow"])
    assert result.exit_code == 0
    assert "facts" in result.output


def test_transit_basic():
    result = runner.invoke(main.app, ["transit", "2026-01-15", "12:00", "Moscow"])
    assert result.exit_code == 0
    assert "facts" in result.output


def test_solar_basic():
    result = runner.invoke(main.app, ["solar", "2026", "1990-01-01", "12:00", "Moscow"])
    assert result.exit_code == 0
    assert "facts" in result.output


def test_relocate_basic():
    result = runner.invoke(main.app, ["relocate", "Moscow"])
    assert result.exit_code == 0
    assert "coords" in result.output


def test_devils_basic():
    result = runner.invoke(main.app, ["devils", "1990-01-01", "12:00", "Moscow"])
    assert result.exit_code == 0
    assert "devils" in result.output


def test_rectify_basic():
    result = runner.invoke(main.app, ["rectify", "1990-01-01", "12:00", "Moscow"])
    assert result.exit_code == 0
    assert "candidates" in result.output
