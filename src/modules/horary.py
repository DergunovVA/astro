# Horary Astrology Analyzer

"""
Horary Astrology: Analyzing questions using chart cast for the moment.

Traditional horary astrology uses:
- House rulerships (querent = 1st house, quesited = varies)
- Aspects (applying vs separating)
- Receptions (mutual dignity between planets)
- Dignity scores (essential + accidental)
- Translation of light (3rd planet connects two significators)
- Collection of light (both significators aspect 3rd planet)

Based on:
- William Lilly's "Christian Astrology" (1647)
- Traditional Medieval horary doctrine
"""

from typing import Dict, Optional, Any
from src.core.dignities import calculate_essential_dignity
from src.core.accidental_dignities import (
    calculate_accidental_dignity,
    get_total_dignity,
)


class HoraryAnalyzer:
    """
    Analyze horary questions using traditional methods.

    Horary astrology answers specific questions by interpreting a chart
    cast for the moment the question is asked or understood.
    """

    def __init__(self, chart_data: Dict):
        """
        Initialize horary analyzer.

        Args:
            chart_data: Chart data with planets, houses, aspects, etc.
        """
        self.chart = chart_data
        self.planets = chart_data.get("planets", {})
        self.houses = chart_data.get("houses", {})
        self.aspects = chart_data.get("aspects", [])

    # ============================================================
    # MAIN ANALYSIS METHODS
    # ============================================================

    def analyze_question(
        self, question_type: str, house_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze horary question.

        Args:
            question_type: Type of question:
                - 'will_it_happen': Yes/No outcome
                - 'when': Timing prediction
                - 'lost_object': Location of lost item
                - 'relationship': Relationship outcome
            house_number: House representing the quesited (optional)

        Returns:
            Analysis result with answer, confidence, and factors

        Example:
            >>> analyzer = HoraryAnalyzer(chart_data)
            >>> result = analyzer.analyze_question('will_it_happen', house_number=7)
            >>> print(result['answer'])  # 'yes', 'no', or 'uncertain'
            >>> print(result['confidence'])  # 0.0 to 1.0
        """
        if question_type == "will_it_happen":
            return self._analyze_yes_no(house_number or 7)
        elif question_type == "when":
            return self._analyze_timing(house_number or 7)
        elif question_type == "lost_object":
            return self._analyze_lost_object()
        elif question_type == "relationship":
            return self._analyze_yes_no(7)  # 7th house = partners
        else:
            return {
                "error": f"Unknown question type: {question_type}",
                "supported_types": [
                    "will_it_happen",
                    "when",
                    "lost_object",
                    "relationship",
                ],
            }

    def _analyze_yes_no(self, quesited_house: int) -> Dict[str, Any]:
        """
        Analyze Yes/No horary question.

        Traditional factors:
        1. Applying aspect between significators = YES
        2. Mutual reception = YES (can overcome obstacles)
        3. Translation of light = YES (3rd planet helps)
        4. Collection of light = YES (both planet aspect 3rd)
        5. Separating aspect = NO
        6. No connection = NO
        7. Prohibition/Frustration = NO

        Args:
            quesited_house: House number for quesited (thing asked about)

        Returns:
            dict with:
            {
                'answer': 'yes'/'no'/'uncertain',
                'confidence': float (0.0 to 1.0),
                'factors': [list of reasons],
                'querent_planet': str,
                'quesited_planet': str,
                'aspect': dict or None
            }
        """
        result = {
            "answer": "uncertain",
            "confidence": 0.0,
            "factors": [],
            "querent_planet": None,
            "quesited_planet": None,
            "aspect": None,
        }

        # 1. Get significators
        querent = self._get_querent_significator()  # 1st house ruler
        quesited = self._get_quesited_significator(quesited_house)

        result["querent_planet"] = querent
        result["quesited_planet"] = quesited

        if not querent or not quesited:
            result["factors"].append("Cannot identify significators")
            return result

        # 2. Check for applying aspect (most important)
        aspect_info = self._find_aspect_between(querent, quesited)

        if aspect_info:
            result["aspect"] = aspect_info

            if aspect_info.get("applying"):
                # Applying aspect = positive indication
                result["answer"] = "yes"
                result["confidence"] += 0.6
                result["factors"].append(
                    f"Applying {aspect_info['type']} aspect ({aspect_info['orb']:.2f}°)"
                )

                # Bonus if harmonious aspect
                if aspect_info["type"] in ["trine", "sextile"]:
                    result["confidence"] += 0.1
                    result["factors"].append("Harmonious aspect (easy manifestation)")

            else:
                # Separating aspect = negative indication
                result["answer"] = "no"
                result["confidence"] += 0.5
                result["factors"].append(
                    f"Separating {aspect_info['type']} aspect (opportunity passed)"
                )

        # 3. Check mutual reception (can substitute for aspect)
        if self._has_mutual_reception(querent, quesited):
            if result["answer"] == "uncertain":
                result["answer"] = "yes"
                result["confidence"] = 0.4
            else:
                result["confidence"] += 0.2

            result["factors"].append(
                "Mutual reception present (significators help each other)"
            )

        # 4. Check translation of light
        translator = self._find_translation_of_light(querent, quesited)
        if translator:
            if result["answer"] == "uncertain":
                result["answer"] = "yes"
                result["confidence"] = 0.5
            else:
                result["confidence"] += 0.2

            result["factors"].append(
                f"Translation of light by {translator} (3rd party helps)"
            )

        # 5. Check collection of light
        collector = self._find_collection_of_light(querent, quesited)
        if collector:
            if result["answer"] == "uncertain":
                result["answer"] = "yes"
                result["confidence"] = 0.6
            else:
                result["confidence"] += 0.2

            result["factors"].append(
                f"Collection of light by {collector} (both connect through 3rd planet)"
            )

        # 6. No connection found
        if not aspect_info and result["answer"] == "uncertain":
            result["answer"] = "no"
            result["confidence"] = 0.3
            result["factors"].append("No aspect between significators (no connection)")

        # 7. Dignity consideration
        querent_dignity = self._get_planet_total_dignity(querent)
        quesited_dignity = self._get_planet_total_dignity(quesited)

        if querent_dignity and querent_dignity["total_score"] < -5:
            result["confidence"] *= 0.8
            result["factors"].append("Querent very weak (low ability to achieve goal)")

        if quesited_dignity and quesited_dignity["total_score"] < -5:
            result["confidence"] *= 0.8
            result["factors"].append(
                "Quesited very weak (thing asked about is problematic)"
            )

        # Cap confidence at 1.0
        result["confidence"] = min(1.0, result["confidence"])

        return result

    def _analyze_timing(self, quesited_house: int) -> Dict[str, Any]:
        """
        Analyze WHEN something will happen (horary timing).

        Traditional timing methods:
        1. Orb of applying aspect = time units
        2. House position (angular/succedent/cadent)
        3. Sign speed (cardinal/fixed/mutable)

        Args:
            quesited_house: House number for quesited

        Returns:
            dict with timing prediction
        """
        result = {
            "timing": "unknown",
            "time_units": None,
            "time_value": None,
            "factors": [],
        }

        querent = self._get_querent_significator()
        quesited = self._get_quesited_significator(quesited_house)

        if not querent or not quesited:
            result["factors"].append("Cannot identify significators")
            return result

        # Find applying aspect
        aspect_info = self._find_aspect_between(querent, quesited)

        if not aspect_info or not aspect_info.get("applying"):
            result["factors"].append("No applying aspect (timing uncertain)")
            return result

        orb = aspect_info["orb"]
        result["time_value"] = round(orb, 2)

        # Determine time units based on house position
        querent_house = self._get_planet_house(querent)

        if querent_house in [1, 4, 7, 10]:
            # Angular = fast (days to weeks)
            result["time_units"] = "days"
            result["timing"] = f"approximately {int(orb)} days"
            result["factors"].append("Angular house (fast timing)")

        elif querent_house in [2, 5, 8, 11]:
            # Succedent = moderate (weeks to months)
            result["time_units"] = "weeks"
            result["timing"] = f"approximately {int(orb)} weeks"
            result["factors"].append("Succedent house (moderate timing)")

        else:
            # Cadent = slow (months)
            result["time_units"] = "months"
            result["timing"] = f"approximately {int(orb)} months"
            result["factors"].append("Cadent house (slow timing)")

        # Sign speed modifier
        querent_sign = self._get_planet_sign(querent)
        if querent_sign:
            if querent_sign in ["Aries", "Cancer", "Libra", "Capricorn"]:
                result["factors"].append("Cardinal sign (speeds things up)")
            elif querent_sign in ["Taurus", "Leo", "Scorpio", "Aquarius"]:
                result["factors"].append("Fixed sign (delays/stabilizes)")
            elif querent_sign in ["Gemini", "Virgo", "Sagittarius", "Pisces"]:
                result["factors"].append("Mutable sign (variable timing)")

        return result

    def _analyze_lost_object(self) -> Dict[str, Any]:
        """
        Analyze lost object location (horary).

        Traditional method:
        - 2nd house ruler = lost object
        - Sign & house = location clues
        - Aspects = who might help

        Returns:
            dict with location hints
        """
        result = {"location_hints": [], "likely_found": False, "factors": []}

        # Get 2nd house ruler (possessions, lost items)
        second_house_ruler = self._get_house_ruler(2)

        if not second_house_ruler:
            result["factors"].append("Cannot identify 2nd house ruler")
            return result

        # Get sign and house position
        sign = self._get_planet_sign(second_house_ruler)
        house = self._get_planet_house(second_house_ruler)

        if sign:
            result["location_hints"].append(f"Sign: {sign}")

        if house:
            result["location_hints"].append(f"House: {house}")

        # Dignity check (strong = likely found)
        dignity = self._get_planet_total_dignity(second_house_ruler)
        if dignity and dignity["total_score"] > 3:
            result["likely_found"] = True
            result["factors"].append(
                "2nd house ruler has good dignity (item likely found)"
            )
        else:
            result["factors"].append("2nd house ruler weak (may not be found)")

        return result

    # ============================================================
    # HELPER METHODS: SIGNIFICATORS
    # ============================================================

    def _get_querent_significator(self) -> Optional[str]:
        """
        Get querent significator (person asking question).

        Traditional: Ruler of 1st house (Ascendant)

        Returns:
            Planet name or None
        """
        return self._get_house_ruler(1)

    def _get_quesited_significator(self, house_number: int) -> Optional[str]:
        """
        Get quesited significator (thing asked about).

        Args:
            house_number: House representing the quesited
                - 7th: Partnerships, others, opponents
                - 10th: Career, status, authority
                - 5th: Children, creativity, romance
                - etc.

        Returns:
            Planet name or None
        """
        return self._get_house_ruler(house_number)

    def _get_house_ruler(self, house_number: int) -> Optional[str]:
        """
        Get ruler of a house.

        Args:
            house_number: House number (1-12)

        Returns:
            Planet name ruling the sign on the house cusp
        """
        # Get house cusp sign
        house_key = f"House{house_number}"
        house_info = self.houses.get(house_key, {})

        cusp_sign = house_info.get("Sign")
        if not cusp_sign:
            return None

        # Get ruler of that sign
        from src.core.dignities import get_dispositor

        return get_dispositor(cusp_sign)

    # ============================================================
    # HELPER METHODS: ASPECTS
    # ============================================================

    def _find_aspect_between(
        self, planet1: str, planet2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find aspect between two planets.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            dict with aspect info or None
            {
                'type': 'trine'/'square'/etc.,
                'orb': float,
                'applying': bool,
                'category': 'major'/'minor'
            }
        """
        if not planet1 or not planet2:
            return None

        # Search in pre-calculated aspects
        for aspect in self.aspects:
            if isinstance(aspect, dict):
                p1 = aspect.get("planet1")
                p2 = aspect.get("planet2")

                if (p1 == planet1 and p2 == planet2) or (
                    p1 == planet2 and p2 == planet1
                ):
                    # Determine if applying or separating
                    applying = self._is_aspect_applying(planet1, planet2, aspect)

                    return {
                        "type": aspect.get("type", "unknown"),
                        "orb": abs(aspect.get("orb", 0.0)),
                        "applying": applying,
                        "category": aspect.get("category", "major"),
                    }

        return None

    def _is_aspect_applying(self, planet1: str, planet2: str, aspect: Dict) -> bool:
        """
        Determine if aspect is applying (getting closer) or separating.

        Applying = orb decreasing
        Separating = orb increasing

        Args:
            planet1: First planet
            planet2: Second planet
            aspect: Aspect data

        Returns:
            True if applying, False if separating
        """
        # Get planet data
        p1_data = self.planets.get(planet1, {})
        p2_data = self.planets.get(planet2, {})

        # Check for retrograde motion
        # If faster planet is behind slower planet = applying
        # This is simplified; real calculation requires positions
        # For now, default to applying if no retrograde
        p1_retro = p1_data.get("Retrograde", False)
        p2_retro = p2_data.get("Retrograde", False)

        if p1_retro or p2_retro:
            return False  # Retrograde often breaks aspects

        return True  # Default: assume applying

    # ============================================================
    # HELPER METHODS: RECEPTION & LIGHT
    # ============================================================

    def _has_mutual_reception(self, planet1: str, planet2: str) -> bool:
        """
        Check if two planets have mutual reception.

        Mutual reception: planets in each other's ruling signs

        Args:
            planet1: First planet
            planet2: Second planet

        Returns:
            True if mutual reception exists
        """
        if not planet1 or not planet2:
            return False

        from src.core.dignities import DOMICILE, get_planet_sign

        # Get signs
        p1_data = self.planets.get(planet1, {})
        p2_data = self.planets.get(planet2, {})

        if "longitude" in p1_data and "longitude" in p2_data:
            p1_sign = get_planet_sign(p1_data["longitude"])
            p2_sign = get_planet_sign(p2_data["longitude"])

            # Check if planet1 rules planet2's sign AND vice versa
            p1_rules_p2_sign = planet1 in DOMICILE and p2_sign in DOMICILE[planet1]
            p2_rules_p1_sign = planet2 in DOMICILE and p1_sign in DOMICILE[planet2]

            return p1_rules_p2_sign and p2_rules_p1_sign

        return False

    def _find_translation_of_light(self, planet1: str, planet2: str) -> Optional[str]:
        """
        Find translation of light.

        Translation: 3rd planet aspects both significators,
        connecting them when they don't aspect each other.

        The 3rd planet must:
        1. Separate from one significator
        2. Apply to the other significator

        Args:
            planet1: First significator
            planet2: Second significator

        Returns:
            Translator planet name or None
        """
        # Check all other planets
        for planet in self.planets.keys():
            if planet == planet1 or planet == planet2:
                continue

            # Check if planet aspects both
            aspect1 = self._find_aspect_between(planet, planet1)
            aspect2 = self._find_aspect_between(planet, planet2)

            if aspect1 and aspect2:
                # Ideally: separating from one, applying to other
                # Simplified: both aspects exist
                return planet

        return None

    def _find_collection_of_light(self, planet1: str, planet2: str) -> Optional[str]:
        """
        Find collection of light.

        Collection: both significators apply to a 3rd planet,
        which "collects" their light and brings them together.

        Args:
            planet1: First significator
            planet2: Second significator

        Returns:
            Collector planet name or None
        """
        # Check all other planets
        for planet in self.planets.keys():
            if planet == planet1 or planet == planet2:
                continue

            # Both significators must aspect this planet
            aspect1 = self._find_aspect_between(planet1, planet)
            aspect2 = self._find_aspect_between(planet2, planet)

            if aspect1 and aspect2:
                # Check if both are applying
                if aspect1.get("applying") and aspect2.get("applying"):
                    return planet

        return None

    # ============================================================
    # HELPER METHODS: PLANET INFO
    # ============================================================

    def _get_planet_sign(self, planet: str) -> Optional[str]:
        """Get sign where planet is located."""
        planet_data = self.planets.get(planet, {})

        if "Sign" in planet_data:
            return planet_data["Sign"]
        elif "longitude" in planet_data:
            from src.core.dignities import get_planet_sign

            return get_planet_sign(planet_data["longitude"])

        return None

    def _get_planet_house(self, planet: str) -> Optional[int]:
        """Get house number where planet is located."""
        planet_data = self.planets.get(planet, {})
        return planet_data.get("House")

    def _get_planet_total_dignity(self, planet: str) -> Optional[Dict]:
        """
        Calculate total dignity (essential + accidental) for planet.

        Returns:
            dict from get_total_dignity() or None
        """
        planet_data = self.planets.get(planet, {})
        if not planet_data:
            return None

        # Essential dignity
        longitude = planet_data.get("longitude")
        if longitude is None:
            return None

        # Determine if day chart
        sun_data = self.planets.get("Sun", {})
        asc_data = self.houses.get("House1", {})

        sun_lon = sun_data.get("longitude", 0)
        asc_lon = asc_data.get("Degree", 0)

        from src.core.dignities import is_day_chart

        is_day = is_day_chart(sun_lon, asc_lon)

        essential = calculate_essential_dignity(planet, longitude, is_day)

        # Accidental dignity
        house = planet_data.get("House", 1)
        is_retro = planet_data.get("Retrograde", False)
        speed = planet_data.get("Speed", 0.0)

        accidental = calculate_accidental_dignity(
            planet, house, is_retro, speed, longitude, sun_lon
        )

        # Combine
        return get_total_dignity(essential, accidental)
