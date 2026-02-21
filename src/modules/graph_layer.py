# Graph Layer - Relationship graphs for astrological analysis

"""
Graph-based analysis of astrological relationships.

Features:
- Mutual receptions (planets in each other's signs)
- Dispositor chains (rulership chains)
- Aspect relationships as graph edges
- Visualization export (Graphviz, JSON)

Example:
    >>> from src.modules import ChartGraph
    >>> graph = ChartGraph(chart_data)
    >>> receptions = graph.find_all_receptions()
    >>> print(receptions)
    [('Venus', 'Mars'), ('Mercury', 'Jupiter')]
"""

from typing import Dict, List, Tuple, Optional
import networkx as nx


class ChartGraph:
    """
    Graph representation of astrological chart relationships.

    Uses NetworkX for graph operations and analysis.
    """

    def __init__(self, chart_data: Dict, mode: str = "modern"):
        """
        Initialize chart graph.

        Args:
            chart_data: Chart data with planets, houses, aspects
            mode: 'traditional' (7 planets) or 'modern' (10 planets)
        """
        self.chart = chart_data
        self.mode = mode
        self.graph = nx.DiGraph()  # Directed graph for dispositors

        # Initialize nodes for all planets
        planets = chart_data.get("planets", {})
        for planet_name in planets.keys():
            self.graph.add_node(planet_name)

    # ============================================================
    # MUTUAL RECEPTIONS
    # ============================================================

    def _get_sign_ruler(self, sign: str) -> Optional[str]:
        """
        Get ruler of a sign.

        Args:
            sign: Zodiac sign name

        Returns:
            Planet name or None
        """
        # Rulership table (modern)
        RULERS_MODERN = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Pluto",  # Modern ruler (traditional: Mars)
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Uranus",  # Modern ruler (traditional: Saturn)
            "Pisces": "Neptune",  # Modern ruler (traditional: Jupiter)
        }

        # Traditional rulership
        RULERS_TRADITIONAL = {
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

        rulers = RULERS_TRADITIONAL if self.mode == "traditional" else RULERS_MODERN
        return rulers.get(sign)

    def _is_mutual_reception(self, planet1: str, planet2: str) -> bool:
        """
        Check if two planets are in mutual reception.

        Mutual reception: planet1 in planet2's sign AND planet2 in planet1's sign

        Example:
            Venus in Aries (Mars rules Aries)
            Mars in Taurus (Venus rules Taurus)
            → Mutual reception between Venus and Mars

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            True if mutual reception exists
        """
        planets = self.chart.get("planets", {})

        if planet1 not in planets or planet2 not in planets:
            return False

        # Get signs where planets are located
        p1_sign = planets[planet1].get("Sign")
        p2_sign = planets[planet2].get("Sign")

        if not p1_sign or not p2_sign:
            return False

        # Get rulers of those signs
        p1_sign_ruler = self._get_sign_ruler(p1_sign)
        p2_sign_ruler = self._get_sign_ruler(p2_sign)

        # Check mutual reception
        return p1_sign_ruler == planet2 and p2_sign_ruler == planet1

    def add_mutual_reception(self, planet1: str, planet2: str) -> bool:
        """
        Add mutual reception edge between two planets.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            True if mutual reception was added
        """
        if not self._is_mutual_reception(planet1, planet2):
            return False

        # Add bidirectional edges for mutual reception
        self.graph.add_edge(
            planet1,
            planet2,
            relation="mutual_reception",
            strength="strong",
            type="harmonious",
        )

        self.graph.add_edge(
            planet2,
            planet1,
            relation="mutual_reception",
            strength="strong",
            type="harmonious",
        )

        return True

    def find_all_receptions(self) -> List[Tuple[str, str]]:
        """
        Find all mutual receptions in chart.

        Returns:
            List of planet pairs in mutual reception

        Example:
            >>> graph = ChartGraph(chart_data)
            >>> receptions = graph.find_all_receptions()
            >>> print(receptions)
            [('Venus', 'Mars'), ('Mercury', 'Jupiter')]
        """
        planets = list(self.chart.get("planets", {}).keys())
        receptions = []

        # Check all planet pairs
        for i, p1 in enumerate(planets):
            for p2 in planets[i + 1 :]:
                if self._is_mutual_reception(p1, p2):
                    receptions.append((p1, p2))
                    self.add_mutual_reception(p1, p2)

        return receptions

    def get_reception_strength(self, planet1: str, planet2: str) -> Optional[str]:
        """
        Get mutual reception strength.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            'strong' if mutual reception exists, None otherwise
        """
        if self.graph.has_edge(planet1, planet2):
            edge_data = self.graph.get_edge_data(planet1, planet2)
            if edge_data and edge_data.get("relation") == "mutual_reception":
                return edge_data.get("strength", "strong")
        return None

    # ============================================================
    # DISPOSITOR CHAINS (To be implemented in Task 4.1.2)
    # ============================================================

    def build_dispositor_chain(self, planet: str) -> List[str]:
        """Build dispositor chain for planet (TODO: Task 4.1.2)"""
        raise NotImplementedError("Task 4.1.2: Dispositor chains")

    def find_final_dispositor(self, planet: str) -> str:
        """Find final dispositor in chain (TODO: Task 4.1.2)"""
        raise NotImplementedError("Task 4.1.2: Dispositor chains")

    # ============================================================
    # ASPECT RELATIONSHIPS (To be implemented in Task 4.1.3)
    # ============================================================

    def add_aspect_edges(self):
        """Add aspect relationships as graph edges (TODO: Task 4.1.3)"""
        raise NotImplementedError("Task 4.1.3: Aspect relationships")

    # ============================================================
    # VISUALIZATION (To be implemented in Task 4.1.4)
    # ============================================================

    def export_graphviz(self, filename: str):
        """Export graph to Graphviz DOT format (TODO: Task 4.1.4)"""
        raise NotImplementedError("Task 4.1.4: Graph visualization")

    def export_json(self) -> Dict:
        """Export graph as JSON for web visualization (TODO: Task 4.1.4)"""
        raise NotImplementedError("Task 4.1.4: Graph visualization")

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def get_all_receptions(self) -> List[Tuple[str, str]]:
        """
        Get all mutual receptions (including already added).

        Returns:
            List of planet pairs in mutual reception
        """
        receptions = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == "mutual_reception":
                # Only include unique pairs (avoid duplicates from bidirectional edges)
                if (v, u) not in receptions:
                    receptions.append((u, v))
        return receptions

    def has_mutual_reception(self, planet1: str, planet2: str) -> bool:
        """
        Check if two planets have mutual reception relationship.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            True if mutual reception exists
        """
        return (
            self.graph.has_edge(planet1, planet2)
            and self.graph.get_edge_data(planet1, planet2).get("relation")
            == "mutual_reception"
        )

    def clear_graph(self):
        """Clear all edges (keep nodes)"""
        self.graph.clear_edges()

    def __repr__(self):
        return f"ChartGraph(nodes={self.graph.number_of_nodes()}, edges={self.graph.number_of_edges()})"
