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
    # DISPOSITOR CHAINS
    # ============================================================

    def build_dispositor_chain(self, planet: str) -> List[str]:
        """
        Build dispositor chain for planet.

        Dispositor: ruler of the sign a planet is in
        Chain: planet → its dispositor → dispositor's dispositor → ...

        Example:
            Moon in Gemini → Mercury (rules Gemini)
            Mercury in Pisces → Jupiter (traditional ruler)
            Jupiter in Sagittarius → Jupiter (rules its own sign)
            Chain: Moon → Mercury → Jupiter → Jupiter (final dispositor)

        Args:
            planet: Planet name to build chain for

        Returns:
            List of planets in dispositor chain
            Last element may have "(loop)" suffix if mutual reception detected
        """
        planets = self.chart.get("planets", {})

        if planet not in planets:
            return [planet]

        chain = [planet]
        current = planet
        visited = set([planet])

        while True:
            # Get sign where current planet is located
            planet_data = planets.get(current)
            if not planet_data:
                break

            sign = planet_data.get("Sign")
            if not sign:
                break

            # Get ruler of that sign
            dispositor = self._get_sign_ruler(sign)
            if not dispositor:
                break

            # Check if planet is in its own sign (final dispositor)
            if dispositor == current:
                break

            # Check for mutual reception loop
            if dispositor in visited:
                chain.append(f"{dispositor} (loop)")
                break

            # Add to chain and continue
            chain.append(dispositor)
            visited.add(dispositor)
            current = dispositor

            # Safety: max 12 iterations (should never happen naturally)
            if len(chain) > 12:
                break

        return chain

    def find_final_dispositor(self, planet: str) -> str:
        """
        Find final dispositor in chain.

        The final dispositor is either:
        - A planet in its own sign (dignified)
        - A planet involved in a mutual reception loop

        Args:
            planet: Planet name

        Returns:
            Final dispositor planet name (without "(loop)" suffix)
        """
        chain = self.build_dispositor_chain(planet)
        if not chain:
            return planet

        final = chain[-1]
        return final.replace(" (loop)", "")

    def analyze_dispositor_tree(self) -> Dict:
        """
        Analyze complete dispositor tree for chart.

        Also adds dispositor edges to graph for visualization.

        Returns:
            Dictionary with:
            - 'final_dispositors': List of planets that are final dispositors
            - 'chains': Dict mapping each planet to its dispositor chain
            - 'loops': List of planet pairs in mutual reception loops

        Example:
            >>> analysis = graph.analyze_dispositor_tree()
            >>> print(analysis['final_dispositors'])
            ['Jupiter', 'Venus']
            >>> print(analysis['chains']['Moon'])
            ['Moon', 'Mercury', 'Jupiter']
            >>> print(analysis['loops'])
            [('Mars', 'Venus')]
        """
        analysis = {
            "final_dispositors": set(),
            "chains": {},
            "loops": [],
        }

        planets = self.chart.get("planets", {})

        for planet in planets.keys():
            chain = self.build_dispositor_chain(planet)
            analysis["chains"][planet] = chain

            if not chain:
                continue

            # Add dispositor edges to graph
            for i in range(len(chain) - 1):
                current = chain[i]
                next_planet = chain[i + 1]

                # Remove "(loop)" suffix if present
                next_planet_clean = next_planet.replace(" (loop)", "")

                # Add edge (unless it's a loop back to self or edge already exists)
                if current != next_planet_clean:
                    # Only add if no edge exists (don't overwrite mutual_reception, etc.)
                    if not self.graph.has_edge(current, next_planet_clean):
                        self.graph.add_edge(
                            current,
                            next_planet_clean,
                            relation="dispositor",
                        )

            final = chain[-1]
            if "(loop)" in final:
                # Extract loop planets
                loop_planet = final.replace(" (loop)", "")
                # Find the planet before the loop marker
                if len(chain) >= 2:
                    prev_planet = chain[-2]
                    loop_pair = tuple(sorted([prev_planet, loop_planet]))
                    if loop_pair not in analysis["loops"]:
                        analysis["loops"].append(loop_pair)
            else:
                # Final dispositor (planet in own sign)
                analysis["final_dispositors"].add(final)

        analysis["final_dispositors"] = list(analysis["final_dispositors"])
        return analysis

    # ============================================================
    # ASPECT RELATIONSHIPS
    # ============================================================

    def add_aspect_edges(self):
        """
        Add aspect relationships as graph edges.

        Reads aspects from chart data and adds them as edges with:
        - relation='aspect'
        - aspect_type (Conjunction, Trine, Square, etc.)
        - orb (exact orb in degrees)
        - strength (very_strong, strong, moderate, weak based on orb)
        - harmonious (True for Trine/Sextile/Conjunction, False for Square/Opposition)

        Example:
            >>> graph = ChartGraph(chart_data)
            >>> graph.add_aspect_edges()
            >>> # Sun Trine Moon added as harmonious aspect
        """
        # Get aspects from chart data
        # Supports two formats:
        # 1. List of Fact objects with type="aspect"
        # 2. Direct calculate_aspects() call if planets available

        aspects = []

        # Format 1: Pre-calculated aspects in chart_data
        if "aspects" in self.chart:
            aspects_data = self.chart["aspects"]

            # Check if it's Fact objects or dict format
            for aspect in aspects_data:
                if hasattr(aspect, "type"):  # Fact object
                    if aspect.type == "aspect":
                        # Parse object "planet1-planet2"
                        planets_str = aspect.object
                        if "-" in planets_str:
                            planet1, planet2 = planets_str.split("-")
                            aspects.append(
                                {
                                    "planet1": planet1,
                                    "planet2": planet2,
                                    "type": aspect.value,
                                    "orb": aspect.details.get("orb", 0),
                                    "category": aspect.details.get("category", "major"),
                                }
                            )
                elif isinstance(aspect, dict):  # Dict format
                    aspects.append(aspect)

        # Format 2: Calculate aspects from planets if not provided
        elif "planets" in self.chart:
            from src.core.core_geometry import calculate_aspects

            # Aspect configuration (major aspects)
            ASPECTS_CONFIG = {
                "conjunction": 0,
                "opposition": 180,
                "trine": 120,
                "square": 90,
                "sextile": 60,
            }

            planets = self.chart["planets"]
            aspects_tuples = calculate_aspects(planets, ASPECTS_CONFIG)

            for p1, p2, asp_name, orb, category, motion in aspects_tuples:
                aspects.append(
                    {
                        "planet1": p1,
                        "planet2": p2,
                        "type": asp_name,
                        "orb": orb,
                        "category": category,
                    }
                )

        # Add aspect edges to graph
        for aspect in aspects:
            planet1 = aspect["planet1"]
            planet2 = aspect["planet2"]
            aspect_type = aspect["type"]
            orb = aspect["orb"]

            # Determine aspect strength based on orb
            if orb < 1.0:
                strength = "very_strong"
            elif orb < 3.0:
                strength = "strong"
            elif orb < 5.0:
                strength = "moderate"
            else:
                strength = "weak"

            # Harmonious vs challenging aspects
            harmonious_aspects = [
                "trine",
                "sextile",
                "conjunction",
            ]
            challenging_aspects = ["square", "opposition"]

            harmonious = aspect_type.lower() in harmonious_aspects

            # Add undirected edge (aspect goes both ways)
            self.graph.add_edge(
                planet1,
                planet2,
                relation="aspect",
                aspect_type=aspect_type,
                orb=orb,
                strength=strength,
                harmonious=harmonious,
                category=aspect.get("category", "major"),
            )

    def get_all_aspects(self) -> List[Dict]:
        """
        Get all aspect relationships from graph.

        Returns:
            List of aspect dictionaries with planet names, type, orb, strength
        """
        aspects = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == "aspect":
                aspects.append(
                    {
                        "planet1": u,
                        "planet2": v,
                        "type": data.get("aspect_type"),
                        "orb": data.get("orb"),
                        "strength": data.get("strength"),
                        "harmonious": data.get("harmonious"),
                        "category": data.get("category", "major"),
                    }
                )
        return aspects

    def get_planet_aspects(self, planet: str) -> List[Dict]:
        """
        Get all aspects for a specific planet.

        Args:
            planet: Planet name

        Returns:
            List of aspects involving this planet
        """
        aspects = []
        if planet not in self.graph:
            return aspects

        # Check outgoing edges
        for neighbor in self.graph.successors(planet):
            edge_data = self.graph.get_edge_data(planet, neighbor)
            if edge_data and edge_data.get("relation") == "aspect":
                aspects.append(
                    {
                        "planet": neighbor,
                        "type": edge_data.get("aspect_type"),
                        "orb": edge_data.get("orb"),
                        "strength": edge_data.get("strength"),
                        "harmonious": edge_data.get("harmonious"),
                    }
                )

        # Check incoming edges (since aspects are bidirectional conceptually)
        for neighbor in self.graph.predecessors(planet):
            edge_data = self.graph.get_edge_data(neighbor, planet)
            if edge_data and edge_data.get("relation") == "aspect":
                aspects.append(
                    {
                        "planet": neighbor,
                        "type": edge_data.get("aspect_type"),
                        "orb": edge_data.get("orb"),
                        "strength": edge_data.get("strength"),
                        "harmonious": edge_data.get("harmonious"),
                    }
                )

        return aspects

    def count_aspects_by_type(self, planet: str) -> Dict[str, int]:
        """
        Count aspects by type for a planet.

        Args:
            planet: Planet name

        Returns:
            Dict mapping aspect type to count
            Example: {'harmonious': 3, 'challenging': 2}
        """
        aspects = self.get_planet_aspects(planet)

        counts = {"harmonious": 0, "challenging": 0, "total": len(aspects)}

        for aspect in aspects:
            if aspect["harmonious"]:
                counts["harmonious"] += 1
            else:
                counts["challenging"] += 1

        return counts

    # ============================================================
    # VISUALIZATION
    # ============================================================

    def _get_planet_color(self, planet: str) -> str:
        """
        Get traditional astrological color for planet.

        Args:
            planet: Planet name

        Returns:
            Hex color code
        """
        # Traditional astrological colors
        PLANET_COLORS = {
            "Sun": "#FFD700",  # Gold
            "Moon": "#C0C0C0",  # Silver
            "Mercury": "#87CEEB",  # Sky Blue
            "Venus": "#98FB98",  # Pale Green
            "Mars": "#FF6347",  # Tomato Red
            "Jupiter": "#9370DB",  # Medium Purple
            "Saturn": "#696969",  # Dim Gray
            "Uranus": "#00CED1",  # Dark Turquoise
            "Neptune": "#4682B4",  # Steel Blue
            "Pluto": "#8B0000",  # Dark Red
        }
        return PLANET_COLORS.get(planet, "#FFFFFF")  # White as default

    def export_graphviz(self, filename: str):
        """
        Export graph to Graphviz DOT format.

        Creates a visualization file that can be rendered with Graphviz tools.
        Nodes are colored by planet, edges by relationship type.

        Args:
            filename: Output filename (e.g., 'chart.dot')

        Example:
            >>> graph.export_graphviz('natal_chart.dot')
            >>> # Render with: dot -Tpng natal_chart.dot -o natal_chart.png

        Visual attributes:
            - Nodes: Circle shape, filled with planet colors
            - Green bold edges: Mutual receptions
            - Blue edges: Harmonious aspects
            - Red edges: Challenging aspects
            - Gray edges: Dispositor chains
        """
        try:
            from networkx.drawing.nx_agraph import write_dot
        except ImportError:
            raise ImportError(
                "pygraphviz required for Graphviz export. "
                "Install with: pip install pygraphviz"
            )

        # Create a copy to avoid modifying original graph
        viz_graph = self.graph.copy()

        # Add visual attributes to nodes
        for node in viz_graph.nodes():
            viz_graph.nodes[node]["shape"] = "circle"
            viz_graph.nodes[node]["style"] = "filled"
            viz_graph.nodes[node]["fillcolor"] = self._get_planet_color(node)
            viz_graph.nodes[node]["fontcolor"] = "black"
            viz_graph.nodes[node]["fontname"] = "Arial"

        # Add visual attributes to edges
        for u, v, data in viz_graph.edges(data=True):
            relation = data.get("relation", "")

            if relation == "mutual_reception":
                data["color"] = "green"
                data["style"] = "bold"
                data["label"] = "mutual"
                data["penwidth"] = "2.0"

            elif relation == "aspect":
                # Color by harmonious/challenging
                is_harmonious = data.get("harmonious", True)
                data["color"] = "blue" if is_harmonious else "red"
                data["label"] = data.get("aspect_type", "aspect")
                data["penwidth"] = "1.5"

                # Style by strength
                strength = data.get("strength", "moderate")
                if strength == "very_strong":
                    data["style"] = "bold"
                elif strength == "weak":
                    data["style"] = "dashed"

            elif relation == "dispositor":
                data["color"] = "gray"
                data["label"] = "dispositor"
                data["style"] = "solid"

        # Write to DOT file
        write_dot(viz_graph, filename)

    def export_json(self) -> Dict:
        """
        Export graph as JSON for web visualization.

        Returns node-link format compatible with D3.js, Cytoscape.js, etc.

        Returns:
            Dict with 'nodes' and 'links' keys

        Example:
            >>> data = graph.export_json()
            >>> import json
            >>> with open('chart.json', 'w') as f:
            ...     json.dump(data, f)

        Format:
            {
                "nodes": [
                    {"id": "Sun", "color": "#FFD700"},
                    {"id": "Moon", "color": "#C0C0C0"},...
                ],
                "links": [
                    {
                        "source": "Sun",
                        "target": "Moon",
                        "relation": "aspect",
                        "aspect_type": "trine",
                        "harmonious": true,
                        ...
                    }
                ]
            }
        """
        from networkx.readwrite import json_graph

        # Convert to node-link format
        data = json_graph.node_link_data(self.graph)

        # Add colors to nodes
        for node in data["nodes"]:
            node["color"] = self._get_planet_color(node["id"])

        # NetworkX uses "edges" key, rename to "links" for D3.js compatibility
        if "edges" in data:
            data["links"] = data.pop("edges")
        else:
            data["links"] = []

        # Add visual hints to links
        for link in data["links"]:
            relation = link.get("relation", "")

            if relation == "mutual_reception":
                link["color"] = "green"
                link["width"] = 3

            elif relation == "aspect":
                is_harmonious = link.get("harmonious", True)
                link["color"] = "blue" if is_harmonious else "red"
                link["width"] = 2

            elif relation == "dispositor":
                link["color"] = "gray"
                link["width"] = 1

        return data

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
