# Interaction Graph Layer
import networkx as nx
from facts_models import Fact
from typing import List


class InteractionGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_facts(self, facts: List[Fact]):
        """Add facts as nodes to the graph.

        ⚠️ WIP: Edge logic (receptions, dispositors, aspects) not yet implemented

        📋 PLANNED (v0.2 - Horary & Dignities):
        - Add edges for mutual receptions
        - Add edges for dispositor chains
        - Add edges for aspect relationships
        - Add edge weights based on strength

        Status: Base structure ready, edge logic pending v0.2 release
        """
        for fact in facts:
            self.graph.add_node(
                fact.id, type=fact.type, object=fact.object, value=fact.value
            )
            # 📋 v0.2: реализовать логику связей
            # - Mutual receptions: planet1 in planet2's sign AND vice versa
            # - Dispositor chain: planet -> ruler of its sign
            # - Aspects: planet1 <-> planet2 with aspect type as edge label

    def get_graph(self):
        return self.graph

    def export(self):
        # Экспорт в простой формат для анализа
        return nx.node_link_data(self.graph)
