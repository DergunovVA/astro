"""
Dataset Validation Tests

Validates the chart dataset structure, schema, and DSL compatibility.
Task 2.4: Create Real Chart Dataset
"""

import json
import pytest
from pathlib import Path

# DSL imports
from src.dsl.evaluator import evaluate


# Constants
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

PLANETS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]

DIGNITIES = ["Rulership", "Exaltation", "Detriment", "Fall", "Neutral"]

ASPECT_TYPES = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]


@pytest.fixture(scope="module")
def dataset():
    """Load chart dataset"""
    dataset_path = Path("tests/fixtures/chart_dataset.json")
    assert dataset_path.exists(), f"Dataset not found at {dataset_path}"

    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def charts(dataset):
    """Extract charts from dataset"""
    return dataset.get("charts", [])


class TestDatasetStructure:
    """Test dataset structure and metadata"""

    def test_dataset_has_info(self, dataset):
        """Dataset should have dataset_info section"""
        assert "dataset_info" in dataset
        assert "version" in dataset["dataset_info"]
        assert "total_charts" in dataset["dataset_info"]

    def test_dataset_has_charts(self, dataset):
        """Dataset should have charts array"""
        assert "charts" in dataset
        assert isinstance(dataset["charts"], list)

    def test_dataset_size(self, charts):
        """Dataset should contain at least 100 charts"""
        assert len(charts) >= 100, f"Expected >=100 charts, got {len(charts)}"

    def test_edge_cases_present(self, dataset):
        """Dataset should include edge cases"""
        assert "edge_cases" in dataset["dataset_info"]
        assert dataset["dataset_info"]["edge_cases"] >= 5


class TestChartSchema:
    """Test individual chart schema compliance"""

    def test_all_charts_have_id(self, charts):
        """All charts should have unique IDs"""
        chart_ids = [chart.get("id") for chart in charts]
        assert len(chart_ids) == len(set(chart_ids)), "Duplicate chart IDs found"
        assert all(chart_ids), "Some charts missing ID"

    def test_all_charts_have_metadata(self, charts):
        """All charts should have metadata section"""
        for chart in charts:
            assert "metadata" in chart, f"Chart {chart.get('id')} missing metadata"
            metadata = chart["metadata"]
            assert "name" in metadata
            assert "date" in metadata
            assert "time" in metadata
            assert "place" in metadata

    def test_all_charts_have_planets(self, charts):
        """All charts should have planets section"""
        for chart in charts:
            assert "planets" in chart, f"Chart {chart.get('id')} missing planets"
            planets = chart["planets"]

            # Should have at least Sun, Moon
            assert "Sun" in planets, f"Chart {chart['id']} missing Sun"
            assert "Moon" in planets, f"Chart {chart['id']} missing Moon"

    def test_all_charts_have_houses(self, charts):
        """All charts should have houses section"""
        for chart in charts:
            assert "houses" in chart, f"Chart {chart.get('id')} missing houses"
            houses = chart["houses"]

            # Should have at least house 1
            assert 1 in houses or "1" in houses, f"Chart {chart['id']} missing house 1"

    def test_all_charts_have_aspects(self, charts):
        """All charts should have aspects section"""
        for chart in charts:
            assert "aspects" in chart, f"Chart {chart.get('id')} missing aspects"
            assert isinstance(chart["aspects"], list)


class TestPlanetSchema:
    """Test planet data structure"""

    def test_planet_has_required_fields(self, charts):
        """All planets should have required fields"""
        for chart in charts[:20]:  # Sample 20 charts
            for planet_name, planet_data in chart["planets"].items():
                assert "Sign" in planet_data, f"Planet {planet_name} missing Sign"
                assert "House" in planet_data, f"Planet {planet_name} missing House"
                assert "Dignity" in planet_data, f"Planet {planet_name} missing Dignity"
                assert "Retrograde" in planet_data, (
                    f"Planet {planet_name} missing Retrograde"
                )
                assert "Degree" in planet_data, f"Planet {planet_name} missing Degree"

    def test_planet_sign_valid(self, charts):
        """Planet signs should be valid zodiac signs"""
        for chart in charts[:20]:
            for planet_name, planet_data in chart["planets"].items():
                sign = planet_data["Sign"]
                assert sign in ZODIAC_SIGNS, f"Invalid sign: {sign}"

    def test_planet_house_valid(self, charts):
        """Planet houses should be 1-12"""
        for chart in charts[:20]:
            for planet_name, planet_data in chart["planets"].items():
                house = planet_data["House"]
                assert 1 <= house <= 12, f"Invalid house: {house}"

    def test_planet_dignity_valid(self, charts):
        """Planet dignities should be valid"""
        for chart in charts[:20]:
            for planet_name, planet_data in chart["planets"].items():
                dignity = planet_data["Dignity"]
                assert dignity in DIGNITIES, f"Invalid dignity: {dignity}"

    def test_planet_degree_valid(self, charts):
        """Planet degrees should be 0-29.99"""
        for chart in charts[:20]:
            for planet_name, planet_data in chart["planets"].items():
                degree = planet_data["Degree"]
                assert 0.0 <= degree < 30.0, f"Invalid degree: {degree}"

    def test_planet_retrograde_boolean(self, charts):
        """Retrograde should be boolean"""
        for chart in charts[:20]:
            for planet_name, planet_data in chart["planets"].items():
                retrograde = planet_data["Retrograde"]
                assert isinstance(retrograde, bool), (
                    f"Retrograde not boolean: {retrograde}"
                )


class TestHouseSchema:
    """Test house data structure"""

    def test_house_has_sign(self, charts):
        """All houses should have Sign field"""
        for chart in charts[:20]:
            for house_num, house_data in chart["houses"].items():
                assert "Sign" in house_data, f"House {house_num} missing Sign"
                assert house_data["Sign"] in ZODIAC_SIGNS

    def test_house_has_ruler(self, charts):
        """All houses should have Ruler field"""
        for chart in charts[:20]:
            for house_num, house_data in chart["houses"].items():
                assert "Ruler" in house_data, f"House {house_num} missing Ruler"
                # Ruler should be a planet
                assert house_data["Ruler"] in PLANETS or house_data["Ruler"] in [
                    "Sun",
                    "Moon",
                    "Mercury",
                    "Venus",
                    "Mars",
                    "Jupiter",
                    "Saturn",
                ]


class TestAspectSchema:
    """Test aspect data structure"""

    def test_aspect_has_required_fields(self, charts):
        """All aspects should have required fields"""
        for chart in charts[:20]:
            for aspect in chart["aspects"]:
                assert "Planet1" in aspect, "Aspect missing Planet1"
                assert "Planet2" in aspect, "Aspect missing Planet2"
                assert "Type" in aspect, "Aspect missing Type"
                assert "Orb" in aspect, "Aspect missing Orb"

    def test_aspect_type_valid(self, charts):
        """Aspect types should be valid"""
        for chart in charts[:20]:
            for aspect in chart["aspects"]:
                aspect_type = aspect["Type"]
                assert aspect_type in ASPECT_TYPES, (
                    f"Invalid aspect type: {aspect_type}"
                )

    def test_aspect_orb_valid(self, charts):
        """Aspect orbs should be positive"""
        for chart in charts[:20]:
            for aspect in chart["aspects"]:
                orb = aspect["Orb"]
                assert orb >= 0, f"Invalid orb: {orb}"
                assert orb <= 10, f"Orb too large: {orb}"  # Typical max orb


class TestDatasetCoverage:
    """Test that dataset covers all important cases"""

    def test_all_sun_signs_covered(self, charts):
        """Dataset should cover all 12 sun signs"""
        sun_signs = set()
        for chart in charts:
            sun_sign = chart["planets"]["Sun"]["Sign"]
            sun_signs.add(sun_sign)

        assert len(sun_signs) == 12, f"Only {len(sun_signs)} sun signs covered"
        for sign in ZODIAC_SIGNS:
            assert sign in sun_signs, f"Sun sign {sign} not covered"

    def test_retrograde_coverage(self, charts):
        """Dataset should include retrograde planets"""
        retrograde_count = 0
        for chart in charts:
            for planet_data in chart["planets"].values():
                if planet_data["Retrograde"]:
                    retrograde_count += 1

        assert retrograde_count >= 50, (
            f"Only {retrograde_count} retrograde planets (expected >=50)"
        )

    def test_dignity_coverage(self, charts):
        """Dataset should cover all dignity types"""
        dignities_found = set()
        for chart in charts:
            for planet_data in chart["planets"].values():
                dignities_found.add(planet_data["Dignity"])

        for dignity in DIGNITIES:
            assert dignity in dignities_found, f"Dignity {dignity} not covered"

    def test_aspect_coverage(self, charts):
        """Dataset should cover all aspect types"""
        aspects_found = set()
        for chart in charts:
            for aspect in chart["aspects"]:
                aspects_found.add(aspect["Type"])

        for aspect_type in ASPECT_TYPES:
            assert aspect_type in aspects_found, f"Aspect {aspect_type} not covered"


class TestEdgeCases:
    """Test specific edge cases in dataset"""

    def test_degree_zero_exists(self, charts):
        """Dataset should include planet at 0° degree"""
        found_zero = False
        for chart in charts:
            for planet_data in chart["planets"].values():
                if planet_data["Degree"] < 0.1:  # Close to 0
                    found_zero = True
                    break
            if found_zero:
                break

        assert found_zero, "No planet at 0° degree found"

    def test_degree_29_exists(self, charts):
        """Dataset should include planet at 29° degree"""
        found_29 = False
        for chart in charts:
            for planet_data in chart["planets"].values():
                if planet_data["Degree"] > 29.9:
                    found_29 = True
                    break
            if found_29:
                break

        assert found_29, "No planet at 29° degree found"

    def test_stellium_exists(self, charts):
        """Dataset should include chart with stellium (3+ planets in same sign)"""
        found_stellium = False
        for chart in charts:
            sign_counts = {}
            for planet_data in chart["planets"].values():
                sign = planet_data["Sign"]
                sign_counts[sign] = sign_counts.get(sign, 0) + 1

            if max(sign_counts.values()) >= 3:
                found_stellium = True
                break

        assert found_stellium, "No stellium chart found"


class TestDSLCompatibility:
    """Test that charts work with DSL evaluator"""

    def test_simple_formula_sun_sign(self, charts):
        """DSL should evaluate Sun.Sign formula"""
        chart = charts[0]
        sun_sign = chart["planets"]["Sun"]["Sign"]
        formula = f"Sun.Sign == {sun_sign}"

        result = evaluate(formula, chart)
        assert result is True, f"Formula '{formula}' failed on chart {chart['id']}"

    def test_simple_formula_moon_house(self, charts):
        """DSL should evaluate Moon.House formula"""
        chart = charts[0]
        moon_house = chart["planets"]["Moon"]["House"]
        formula = f"Moon.House == {moon_house}"

        result = evaluate(formula, chart)
        assert result is True, f"Formula '{formula}' failed"

    def test_complex_formula_and(self, charts):
        """DSL should evaluate complex AND formula"""
        chart = charts[0]
        sun_sign = chart["planets"]["Sun"]["Sign"]
        moon_sign = chart["planets"]["Moon"]["Sign"]
        formula = f"Sun.Sign == {sun_sign} AND Moon.Sign == {moon_sign}"

        result = evaluate(formula, chart)
        assert result is True, f"Formula '{formula}' failed"

    def test_retrograde_formula(self, charts):
        """DSL should evaluate Retrograde formula"""
        # Find chart with retrograde planet
        for chart in charts:
            for planet_name, planet_data in chart["planets"].items():
                if planet_data["Retrograde"]:
                    formula = f"{planet_name}.Retrograde == True"
                    result = evaluate(formula, chart)
                    assert result is True, (
                        f"Retrograde formula failed for {planet_name}"
                    )
                    return

        pytest.skip("No retrograde planets in first 10 charts")

    def test_dignity_formula(self, charts):
        """DSL should evaluate Dignity formula"""
        chart = charts[0]
        for planet_name, planet_data in chart["planets"].items():
            dignity = planet_data["Dignity"]
            formula = f"{planet_name}.Dignity == {dignity}"
            result = evaluate(formula, chart)
            assert result is True, f"Dignity formula failed for {planet_name}"
            break  # Test one planet

    def test_degree_comparison(self, charts):
        """DSL should evaluate Degree comparison"""
        chart = charts[0]
        sun_degree = chart["planets"]["Sun"]["Degree"]
        formula = f"Sun.Degree > {sun_degree - 1}"

        result = evaluate(formula, chart)
        assert result is True, "Degree comparison failed"

    def test_house_in_list(self, charts):
        """DSL should evaluate House IN [...] formula"""
        chart = charts[0]
        moon_house = chart["planets"]["Moon"]["House"]
        formula = f"Moon.House IN [{moon_house}, {(moon_house % 12) + 1}]"

        result = evaluate(formula, chart)
        assert result is True, "House IN formula failed"

    def test_batch_evaluation(self, charts):
        """DSL should handle batch evaluation on multiple charts"""
        formulas = [
            "Sun.Sign == Leo",
            "Moon.House IN [1,2,3,4]",
            "Mars.Retrograde == True OR Mars.Retrograde == False",  # Always true
        ]

        for i, chart in enumerate(charts[:10]):
            for formula in formulas:
                try:
                    result = evaluate(formula, chart)
                    assert isinstance(result, bool), (
                        f"Non-boolean result for '{formula}'"
                    )
                except Exception as e:
                    pytest.fail(f"Evaluation failed on chart {i}: {formula} - {e}")


class TestDatasetStatistics:
    """Generate statistics about the dataset"""

    def test_print_sun_sign_distribution(self, charts):
        """Print sun sign distribution for documentation"""
        sun_signs = {}
        for chart in charts:
            sign = chart["planets"]["Sun"]["Sign"]
            sun_signs[sign] = sun_signs.get(sign, 0) + 1

        print("\n=== Sun Sign Distribution ===")
        for sign in ZODIAC_SIGNS:
            count = sun_signs.get(sign, 0)
            print(f"{sign:12s}: {count:3d}")

        assert True  # Always pass, just for printing

    def test_print_retrograde_statistics(self, charts):
        """Print retrograde statistics"""
        retrograde_counts = {planet: 0 for planet in PLANETS}
        total_planets = {planet: 0 for planet in PLANETS}

        for chart in charts:
            for planet_name, planet_data in chart["planets"].items():
                if planet_name in retrograde_counts:
                    total_planets[planet_name] += 1
                    if planet_data["Retrograde"]:
                        retrograde_counts[planet_name] += 1

        print("\n=== Retrograde Statistics ===")
        for planet in PLANETS:
            if total_planets[planet] > 0:
                percent = (retrograde_counts[planet] / total_planets[planet]) * 100
                print(
                    f"{planet:10s}: {retrograde_counts[planet]:3d}/{total_planets[planet]:3d} ({percent:5.1f}%)"
                )

        assert True

    def test_print_dignity_statistics(self, charts):
        """Print dignity statistics"""
        dignity_counts = {d: 0 for d in DIGNITIES}

        for chart in charts:
            for planet_data in chart["planets"].values():
                dignity = planet_data["Dignity"]
                dignity_counts[dignity] = dignity_counts.get(dignity, 0) + 1

        total = sum(dignity_counts.values())

        print("\n=== Dignity Distribution ===")
        for dignity in DIGNITIES:
            count = dignity_counts[dignity]
            percent = (count / total) * 100
            print(f"{dignity:12s}: {count:4d} ({percent:5.1f}%)")

        assert True
