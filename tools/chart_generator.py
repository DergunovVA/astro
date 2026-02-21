"""
Chart Dataset Generator

Generates synthetic natal charts for comprehensive DSL testing.
Covers all zodiac signs, houses, aspects, and edge cases.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any


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

ASPECT_TYPES = [
    "Conjunction",  # 0°
    "Sextile",  # 60°
    "Square",  # 90°
    "Trine",  # 120°
    "Opposition",  # 180°
]

DIGNITIES = ["Rulership", "Exaltation", "Detriment", "Fall", "Neutral"]

# Rulership table (classical)
RULERSHIPS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Exaltations (classical)
EXALTATIONS = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mercury": "Virgo",
    "Venus": "Pisces",
    "Mars": "Capricorn",
    "Jupiter": "Cancer",
    "Saturn": "Libra",
}

# Cities for geographical diversity
CITIES = [
    {
        "name": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
    },
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "timezone": "Europe/London"},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "timezone": "Asia/Tokyo"},
    {
        "name": "Sydney",
        "lat": -33.8688,
        "lon": 151.2093,
        "timezone": "Australia/Sydney",
    },
    {"name": "Moscow", "lat": 55.7558, "lon": 37.6173, "timezone": "Europe/Moscow"},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "timezone": "Asia/Kolkata"},
    {
        "name": "São Paulo",
        "lat": -23.5505,
        "lon": -46.6333,
        "timezone": "America/Sao_Paulo",
    },
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357, "timezone": "Africa/Cairo"},
    {
        "name": "Reykjavik",
        "lat": 64.1466,
        "lon": -21.9426,
        "timezone": "Atlantic/Reykjavik",
    },  # Polar edge case
    {
        "name": "Anchorage",
        "lat": 61.2181,
        "lon": -149.9003,
        "timezone": "America/Anchorage",
    },  # High latitude
]


class ChartGenerator:
    """Generates synthetic natal charts for testing"""

    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility"""
        random.seed(seed)
        self.chart_counter = 0

    def calculate_dignity(self, planet: str, sign: str) -> str:
        """Calculate dignity of planet in sign"""
        # Rulership
        if RULERSHIPS.get(sign) == planet:
            return "Rulership"

        # Exaltation
        if EXALTATIONS.get(planet) == sign:
            return "Exaltation"

        # Detriment (opposite of rulership)
        opposite_sign_idx = (ZODIAC_SIGNS.index(sign) + 6) % 12
        opposite_sign = ZODIAC_SIGNS[opposite_sign_idx]
        if RULERSHIPS.get(opposite_sign) == planet:
            return "Detriment"

        # Fall (opposite of exaltation)
        if planet in EXALTATIONS:
            exalt_sign = EXALTATIONS[planet]
            fall_sign_idx = (ZODIAC_SIGNS.index(exalt_sign) + 6) % 12
            if ZODIAC_SIGNS[fall_sign_idx] == sign:
                return "Fall"

        return "Neutral"

    def generate_planet_positions(self, sun_sign: str = None) -> Dict[str, Any]:
        """Generate positions for all planets"""
        positions = {}

        # Sun sign (fixed or random)
        if sun_sign:
            sun_sign_actual = sun_sign
        else:
            sun_sign_actual = random.choice(ZODIAC_SIGNS)

        # Generate each planet
        for i, planet in enumerate(PLANETS):
            if planet == "Sun":
                sign = sun_sign_actual
                degree = random.uniform(5.0, 25.0)  # Middle of sign usually
            elif planet == "Moon":
                # Moon moves fast, any sign
                sign = random.choice(ZODIAC_SIGNS)
                degree = random.uniform(0.0, 29.99)
            elif planet in ["Mercury", "Venus"]:
                # Mercury/Venus stay near Sun
                if random.random() < 0.7:
                    # Same or adjacent sign
                    sun_idx = ZODIAC_SIGNS.index(sun_sign_actual)
                    offset = random.choice([-1, 0, 1])
                    sign = ZODIAC_SIGNS[(sun_idx + offset) % 12]
                else:
                    sign = random.choice(ZODIAC_SIGNS)
                degree = random.uniform(0.0, 29.99)
            else:
                # Outer planets can be anywhere
                sign = random.choice(ZODIAC_SIGNS)
                degree = random.uniform(0.0, 29.99)

            # Calculate dignity
            dignity = self.calculate_dignity(planet, sign)

            # Retrograde chance (higher for outer planets)
            if planet in ["Mercury", "Venus", "Mars"]:
                retrograde_chance = 0.15
            elif planet in ["Jupiter", "Saturn"]:
                retrograde_chance = 0.3
            else:  # Uranus, Neptune, Pluto
                retrograde_chance = 0.4

            retrograde = random.random() < retrograde_chance

            # House (1-12)
            house = random.randint(1, 12)

            positions[planet] = {
                "Sign": sign,
                "House": house,
                "Dignity": dignity,
                "Retrograde": retrograde,
                "Degree": round(degree, 2),
            }

        return positions

    def generate_houses(self, asc_sign: str = None) -> Dict[int, Dict[str, str]]:
        """Generate house cusps"""
        houses = {}

        # Ascendant sign (1st house cusp)
        if asc_sign:
            first_sign = asc_sign
        else:
            first_sign = random.choice(ZODIAC_SIGNS)

        first_idx = ZODIAC_SIGNS.index(first_sign)

        # Simple equal house system: each house is 30°
        for house_num in range(1, 13):
            sign_idx = (first_idx + house_num - 1) % 12
            sign = ZODIAC_SIGNS[sign_idx]
            ruler = RULERSHIPS[sign]

            houses[house_num] = {"Sign": sign, "Ruler": ruler}

        return houses

    def generate_aspects(self, planets: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate realistic aspects between planets"""
        aspects = []
        planet_names = list(planets.keys())

        # Generate 3-7 aspects per chart
        num_aspects = random.randint(3, 7)

        for _ in range(num_aspects):
            planet1 = random.choice(planet_names)
            planet2 = random.choice([p for p in planet_names if p != planet1])

            aspect_type = random.choice(ASPECT_TYPES)

            # Orb depends on aspect type
            if aspect_type == "Conjunction":
                max_orb = 8.0
            elif aspect_type in ["Trine", "Opposition"]:
                max_orb = 6.0
            elif aspect_type == "Square":
                max_orb = 6.0
            else:  # Sextile
                max_orb = 4.0

            orb = round(random.uniform(0.1, max_orb), 1)

            # Avoid duplicates
            aspect_sig = tuple(sorted([planet1, planet2, aspect_type]))
            if not any(
                tuple(sorted([a["Planet1"], a["Planet2"], a["Type"]])) == aspect_sig
                for a in aspects
            ):
                aspects.append(
                    {
                        "Planet1": planet1,
                        "Planet2": planet2,
                        "Type": aspect_type,
                        "Orb": orb,
                    }
                )

        return aspects

    def generate_metadata(
        self, base_date: datetime, city: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate chart metadata"""
        # Add random time offset (0-23 hours, 0-59 minutes)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        chart_date = base_date + timedelta(hours=hours, minutes=minutes)

        return {
            "name": f"Chart_{self.chart_counter:03d}",
            "date": chart_date.strftime("%Y-%m-%d"),
            "time": chart_date.strftime("%H:%M:%S"),
            "place": city["name"],
            "lat": city["lat"],
            "lon": city["lon"],
            "timezone": city["timezone"],
        }

    def generate_chart(
        self,
        sun_sign: str = None,
        asc_sign: str = None,
        date: datetime = None,
        city: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate a complete natal chart"""
        self.chart_counter += 1

        # Default date if not specified
        if date is None:
            # Random date between 1950-2020
            base_year = random.randint(1950, 2020)
            base_month = random.randint(1, 12)
            base_day = random.randint(1, 28)  # Safe for all months
            date = datetime(base_year, base_month, base_day)

        # Default city if not specified
        if city is None:
            city = random.choice(CITIES)

        # Generate components
        planets = self.generate_planet_positions(sun_sign)
        houses = self.generate_houses(asc_sign)
        aspects = self.generate_aspects(planets)
        metadata = self.generate_metadata(date, city)

        return {
            "id": f"chart_{self.chart_counter:03d}",
            "metadata": metadata,
            "planets": planets,
            "houses": houses,
            "aspects": aspects,
        }

    def generate_dataset(self, total_charts: int = 120) -> Dict[str, Any]:
        """Generate complete dataset of charts"""
        charts = []

        # Strategy: Ensure good coverage
        # 1. All 12 zodiac signs for Sun (10 charts each = 120)
        charts_per_sign = total_charts // 12

        for sign in ZODIAC_SIGNS:
            for i in range(charts_per_sign):
                chart = self.generate_chart(sun_sign=sign)
                charts.append(chart)

        return {
            "dataset_info": {
                "version": "1.0",
                "generated": datetime.now().isoformat(),
                "total_charts": len(charts),
                "purpose": "Comprehensive DSL testing and validation",
                "coverage": {
                    "sun_signs": "All 12 zodiac signs",
                    "retrograde_planets": "Mercury, Venus, Mars, outer planets",
                    "dignities": "Rulership, Exaltation, Detriment, Fall, Neutral",
                    "aspects": "Conjunction, Sextile, Square, Trine, Opposition",
                    "geographical": "10 cities across continents and latitudes",
                },
            },
            "charts": charts,
        }


def generate_edge_cases() -> List[Dict[str, Any]]:
    """Generate specific edge case charts"""
    gen = ChartGenerator(seed=999)
    edge_cases = []

    # Edge Case 1: Planet at 0°00'
    chart = gen.generate_chart()
    chart["planets"]["Mars"]["Degree"] = 0.0
    chart["id"] = "edge_case_001_degree_zero"
    chart["metadata"]["name"] = "Edge_0_Degree"
    edge_cases.append(chart)

    # Edge Case 2: Planet at 29°59'
    chart = gen.generate_chart()
    chart["planets"]["Venus"]["Degree"] = 29.99
    chart["id"] = "edge_case_002_degree_29"
    chart["metadata"]["name"] = "Edge_29_Degree"
    edge_cases.append(chart)

    # Edge Case 3: All planets retrograde
    chart = gen.generate_chart()
    for planet in chart["planets"]:
        if planet != "Sun":  # Sun can't be retrograde
            chart["planets"][planet]["Retrograde"] = True
    chart["id"] = "edge_case_003_all_retrograde"
    chart["metadata"]["name"] = "Edge_All_Retrograde"
    edge_cases.append(chart)

    # Edge Case 4: Multiple planets in same sign
    chart = gen.generate_chart()
    for planet in ["Mercury", "Venus", "Mars"]:
        chart["planets"][planet]["Sign"] = chart["planets"]["Sun"]["Sign"]
    chart["id"] = "edge_case_004_stellium"
    chart["metadata"]["name"] = "Edge_Stellium"
    edge_cases.append(chart)

    # Edge Case 5: All planets in dignity
    chart = gen.generate_chart(sun_sign="Leo")  # Sun in rulership
    chart["planets"]["Moon"]["Sign"] = "Cancer"
    chart["planets"]["Moon"]["Dignity"] = "Rulership"
    chart["planets"]["Mars"]["Sign"] = "Aries"
    chart["planets"]["Mars"]["Dignity"] = "Rulership"
    chart["planets"]["Venus"]["Sign"] = "Taurus"
    chart["planets"]["Venus"]["Dignity"] = "Rulership"
    chart["id"] = "edge_case_005_all_dignified"
    chart["metadata"]["name"] = "Edge_All_Dignified"
    edge_cases.append(chart)

    # Edge Case 6: All planets in detriment/fall
    chart = gen.generate_chart(sun_sign="Aquarius")  # Sun in detriment
    chart["planets"]["Sun"]["Dignity"] = "Detriment"
    chart["planets"]["Moon"]["Sign"] = "Capricorn"
    chart["planets"]["Moon"]["Dignity"] = "Detriment"
    chart["planets"]["Mars"]["Sign"] = "Libra"
    chart["planets"]["Mars"]["Dignity"] = "Detriment"
    chart["id"] = "edge_case_006_all_debilitated"
    chart["metadata"]["name"] = "Edge_All_Debilitated"
    edge_cases.append(chart)

    # Edge Case 7: Polar latitude (affects house calculations)
    chart = gen.generate_chart(
        city={
            "name": "Reykjavik",
            "lat": 64.1466,
            "lon": -21.9426,
            "timezone": "Atlantic/Reykjavik",
        }
    )
    chart["id"] = "edge_case_007_polar"
    chart["metadata"]["name"] = "Edge_Polar_Latitude"
    edge_cases.append(chart)

    # Edge Case 8: Date line crossing
    chart = gen.generate_chart(
        city={
            "name": "Fiji",
            "lat": -18.1248,
            "lon": 178.4501,
            "timezone": "Pacific/Fiji",
        }
    )
    chart["id"] = "edge_case_008_dateline"
    chart["metadata"]["name"] = "Edge_Date_Line"
    edge_cases.append(chart)

    return edge_cases


def main():
    """Generate and save chart dataset"""
    print("Generating Chart Dataset...")

    # Generate main dataset (120 charts)
    gen = ChartGenerator(seed=42)
    dataset = gen.generate_dataset(total_charts=120)

    # Add edge cases (8 charts)
    edge_cases = generate_edge_cases()
    dataset["charts"].extend(edge_cases)
    dataset["dataset_info"]["total_charts"] = len(dataset["charts"])
    dataset["dataset_info"]["edge_cases"] = len(edge_cases)

    # Save to file
    output_path = "tests/fixtures/chart_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated {len(dataset['charts'])} charts")
    print("     - Main dataset: 120 charts (10 per zodiac sign)")
    print(f"     - Edge cases: {len(edge_cases)} charts")
    print(f"     - Saved to: {output_path}")

    # Print statistics
    print("\nDataset Statistics:")
    sun_signs = {}
    retrograde_count = 0
    dignities = {
        "Rulership": 0,
        "Exaltation": 0,
        "Detriment": 0,
        "Fall": 0,
        "Neutral": 0,
    }

    for chart in dataset["charts"]:
        # Count sun signs
        sun_sign = chart["planets"]["Sun"]["Sign"]
        sun_signs[sun_sign] = sun_signs.get(sun_sign, 0) + 1

        # Count retrogrades
        for planet, data in chart["planets"].items():
            if data["Retrograde"]:
                retrograde_count += 1
            dignities[data["Dignity"]] += 1

    print("\nSun Sign Distribution:")
    for sign in ZODIAC_SIGNS:
        count = sun_signs.get(sign, 0)
        print(f"  {sign:12s}: {count:3d} charts")

    print(f"\nRetrograde Planets: {retrograde_count}")
    print("\nDignity Distribution:")
    for dignity, count in dignities.items():
        print(f"  {dignity:12s}: {count:4d}")


if __name__ == "__main__":
    main()
