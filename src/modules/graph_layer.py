# Interaction Graph Layer
import networkx as nx
from facts_models import Fact
from typing import List

class InteractionGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_facts(self, facts: List[Fact]):
        for fact in facts:
            self.graph.add_node(fact.id, type=fact.type, object=fact.object, value=fact.value)
            # Пример: добавить рёбра по рецепциям, диспозиторам и аспектам
            # TODO: реализовать логику связей

    def get_graph(self):
        return self.graph

    def export(self):
        # Экспорт в простой формат для анализа
        return nx.node_link_data(self.graph)
