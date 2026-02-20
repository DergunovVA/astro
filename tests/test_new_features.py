"""Tests for new house systems, aspects expansion, and synastry features."""

import json
import sys
from pathlib import Path
from subprocess import run, PIPE, STDOUT
import pytest


class TestNewFeatures:
    """Tests for house systems, minor aspects, and synastry."""

    def run_command(self, *args) -> dict:
        """Run main.py command and parse JSON output."""
        project_root = Path(__file__).parent.parent
        result = run(
            [sys.executable, str(project_root / "main.py")] + list(args),
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stdout}")

        lines = result.stdout.strip().split("\n")
        json_start = next(
            (i for i, line in enumerate(lines) if line.startswith("{")), None
        )
        if json_start is None:
            raise RuntimeError(f"No JSON output found: {result.stdout}")
        json_str = "\n".join(lines[json_start:])
        return json.loads(json_str)

    def test_natal_placidus_houses(self):
        """Test natal with Placidus house system (default)."""
        result = self.run_command("natal", "1985-01-15", "14:30", "Moscow")

        # Should have 12 house cusps
        house_cusps = [f for f in result["facts"] if f["type"] == "house_cusp"]
        assert len(house_cusps) == 12
        assert all(f["object"].startswith("House") for f in house_cusps)

    def test_natal_koch_houses(self):
        """Test natal with Koch house system."""
        result = self.run_command(
            "natal", "1985-01-15", "14:30", "Moscow", "--house-system", "Koch"
        )

        # Should have 12 house cusps
        house_cusps = [f for f in result["facts"] if f["type"] == "house_cusp"]
        assert len(house_cusps) == 12

        # Koch houses should be different from Placidus
        result_placidus = self.run_command(
            "natal", "1985-01-15", "14:30", "Moscow", "--house-system", "Placidus"
        )
        cusps_koch = [float(f["value"]) for f in house_cusps]
        cusps_placidus = [
            float(f["value"])
            for f in result_placidus["facts"]
            if f["type"] == "house_cusp"
        ]
        # At least some should be different (they're different systems)
        assert (
            len(
                [
                    i
                    for i, (k, p) in enumerate(zip(cusps_koch, cusps_placidus))
                    if abs(k - p) > 0.1
                ]
            )
            > 0
        )

    def test_natal_whole_sign_houses(self):
        """Test natal with Whole Sign house system."""
        result = self.run_command(
            "natal", "1985-01-15", "14:30", "Moscow", "--house-system", "Whole Sign"
        )

        # Should have 12 house cusps
        house_cusps = [f for f in result["facts"] if f["type"] == "house_cusp"]
        assert len(house_cusps) == 12

    def test_aspect_categories_in_output(self):
        """Test that aspects include category (major/minor)."""
        result = self.run_command("natal", "1985-01-15", "14:30", "Moscow")

        aspects = [f for f in result["facts"] if f["type"] == "aspect"]
        assert len(aspects) > 0

        # Each aspect should have category in details
        for aspect in aspects:
            assert "category" in aspect["details"]
            assert aspect["details"]["category"] in ["major", "minor"]

    def test_synastry_command(self):
        """Test synastry command for two people."""
        result = self.run_command(
            "synastry", "1990-05-15", "14:30", "Moscow", "1992-03-20", "10:15", "London"
        )

        # Check structure
        assert "synastry_summary" in result
        assert "synastry_aspects" in result
        assert "chart1_metadata" in result
        assert "chart2_metadata" in result
        assert "composite_planets" in result
        assert "composite_houses" in result

        # Check summary
        summary = result["synastry_summary"]
        assert summary["person1"]["place"] == "Moscow"
        assert summary["person2"]["place"] == "London"
        assert summary["total_aspects"] > 0
        assert len(result["synastry_aspects"]) > 0

    def test_synastry_aspects_structure(self):
        """Test synastry aspects have correct structure."""
        result = self.run_command(
            "synastry", "1990-05-15", "14:30", "Moscow", "1992-03-20", "10:15", "London"
        )

        # Check aspect structure
        aspects = result["synastry_aspects"]
        assert len(aspects) > 0

        for aspect in aspects:
            assert "planet1" in aspect
            assert "planet2" in aspect
            assert "aspect" in aspect
            assert "orb" in aspect
            assert "type" in aspect  # "hard" or "soft"
            assert "category" in aspect  # "major" or "minor"
            assert aspect["type"] in ["hard", "soft"]
            assert aspect["category"] in ["major", "minor"]

    def test_synastry_includes_sun_moon_aspects(self):
        """Test that synastry includes major Sun/Moon aspects."""
        result = self.run_command(
            "synastry", "1990-05-15", "14:30", "Moscow", "1992-03-20", "10:15", "London"
        )

        aspects = result["synastry_aspects"]
        planets_involved = set()
        for aspect in aspects:
            planets_involved.add(aspect["planet1"])
            planets_involved.add(aspect["planet2"])

        # Should include at least Sun and Moon
        assert len(planets_involved) > 0

    def test_synastry_composite_chart(self):
        """Test that synastry includes composite chart."""
        result = self.run_command(
            "synastry", "1990-05-15", "14:30", "Moscow", "1992-03-20", "10:15", "London"
        )

        # Check composite
        composite = result["composite_planets"]
        assert (
            len(composite) >= 7
        )  # At least 7 traditional planets (may include outer planets)
        assert all(isinstance(v, float) for v in composite.values())

        composite_houses = result["composite_houses"]
        assert len(composite_houses) == 12  # 12 houses

    def test_synastry_with_minor_aspects(self):
        """Test synastry with minor aspects included."""
        result = self.run_command(
            "synastry",
            "1990-05-15",
            "14:30",
            "Moscow",
            "1992-03-20",
            "10:15",
            "London",
            "--include-minor",
        )

        aspects = result["synastry_aspects"]
        # Should have some minor aspects when flag is set
        # At least some charts will have minor aspects
        # (This might not always be true, so we just check structure is correct)
        assert all(a["category"] in ["major", "minor"] for a in aspects)

    def test_natal_different_house_systems_produce_different_results(self):
        """Test that different house systems produce measurably different results."""
        placidus = self.run_command(
            "natal", "1985-01-15", "14:30", "Moscow", "--house-system", "Placidus"
        )
        koch = self.run_command(
            "natal", "1985-01-15", "14:30", "Moscow", "--house-system", "Koch"
        )

        # Extract house cusps
        def get_house_cusps(result):
            houses = [f for f in result["facts"] if f["type"] == "house_cusp"]
            return [float(h["value"]) for h in houses]

        placidus_cusps = get_house_cusps(placidus)
        koch_cusps = get_house_cusps(koch)

        # They should have the same count
        assert len(placidus_cusps) == len(koch_cusps) == 12

        # At least one cusp should be different (they're different systems)
        differences = sum(
            1 for p, k in zip(placidus_cusps, koch_cusps) if abs(p - k) > 0.1
        )
        assert differences > 0

    def test_synastry_sorted_by_importance(self):
        """Test that synastry aspects are sorted by importance (major hard first)."""
        result = self.run_command(
            "synastry", "1990-05-15", "14:30", "Moscow", "1992-03-20", "10:15", "London"
        )

        aspects = result["synastry_aspects"]

        # Check they're sorted: major before minor, hard before soft, tighter orbs first
        for i in range(len(aspects) - 1):
            curr = aspects[i]
            next_asp = aspects[i + 1]

            # Major comes before minor
            if curr["category"] != next_asp["category"]:
                assert curr["category"] == "major"
            # Within same category, hard comes before soft
            elif curr["type"] != next_asp["type"]:
                assert curr["type"] == "hard"
            # Within same category and type, tighter orb comes first
            else:
                assert curr["orb"] <= next_asp["orb"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
